import json
import logging
import asyncio  # 👈 导入 asyncio 用于兼容同步/异步工具
from openai import OpenAI
import config
from tools import browser_ctrl, TOOLS_MAP, tools_schema

client = OpenAI(api_key=config.API_KEY, base_url=config.BASE_URL)


async def run_crawler_agent(user_prompt: str, max_steps: int = 20):
    """驱动 Agent 思考与工具调用的核心调度逻辑"""
    logging.info("🚀 正在启动自动化浏览器...")
    await browser_ctrl.start(headless=False)

    system_instruction = (
        "你是一个具备自我纠错能力的自动化爬虫 Agent。\n"
        "任务流程：\n"
        "1. 访问网页，抓取目标数据。若选择器未知可优先使用 `extract_clean_text`。\n"
        "2. 对于动态加载（如下拉刷新、AJAX）的网页，请调用滚动或等待类工具。\n"  # 👈 加上这句提示
        "3. 报错时自动更换思路或选择器，不要轻易放弃。\n"
        "4. 数据提取成功后，先调用 `save_data_to_file` 存为本地文件。\n"
        "5. 最后必须调用 `send_email_notification` 将结果推送至用户邮箱。\n"
    )

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_prompt}
    ]

    logging.info(f"📋 [任务目标]: {user_prompt}\n" + "=" * 60)

    try:
        step = 0
        while step < max_steps:
            step += 1

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                tools=tools_schema,
                tool_choice="auto"
            )

            response_message = response.choices[0].message
            messages.append(response_message)

            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments)

                    logging.info(f"🧠 [Step {step}] AI 决定调用 `{fn_name}` | 参数: {fn_args}")

                    tool_func = TOOLS_MAP.get(fn_name)
                    if tool_func:
                        # -------------------------------------------------------------
                        # 🔒 兼容性增强：判断工具函数是异步 (async) 还是同步 (sync)
                        # -------------------------------------------------------------
                        if asyncio.iscoroutinefunction(tool_func):
                            tool_result = await tool_func(**fn_args)
                        else:
                            tool_result = tool_func(**fn_args)

                        logging.info(f"📥 [Tool Output]: {str(tool_result)[:120]}...\n")

                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(tool_result)  # 确保转为 string 传给 LLM
                        })
                    else:
                        logging.error(f"❌ 未定义的工具名称: {fn_name}")
            else:
                print("=" * 60)
                logging.info("🎯 [Agent 总结汇报]:\n")
                print(response_message.content)
                break

    except Exception as e:
        logging.error(f"❌ 运行发生异常: {e}")

    finally:
        await browser_ctrl.close()
        logging.info("✅ 浏览器资源已释放，程序正常退出。")