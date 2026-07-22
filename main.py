import asyncio
import logging
# 把原来的 from agent import run_crawler_agent 改为：
from my_agent import run_crawler_agent

# 初始化控制台日志显示格式
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

if __name__ == "__main__":
    # 你可以在这里随意修改你的任务
    user_prompt = """
    请访问 https://movie.douban.com/review/best/
    提取前 5 条影评，
    将数据保存到本地 'output/talking.json' 中，
    并发送一封标题为 'talking 热点推送' 的邮件通知我。
    """

    # 启动任务
    asyncio.run(run_crawler_agent(user_prompt))