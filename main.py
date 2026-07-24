import asyncio
import logging
from my_agent import run_crawler_agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

SYSTEM_INSTRUCTION = """
【Agent 行为准则】：
1. 精确提取用户指令中的所有参数。
2. 本环境具备完整本地文件读写权限。如果指定了盘符路径（如“存到E盘”），在调用工具时必须传入 output_dir。
3. 爬取影评详情时，务必提取正文元素的完整文本（如选择器 `#link-report` 或 `.review-content`），不要只截取摘要。
"""

if __name__ == "__main__":
  user_prompt = """
    请帮我爬取视频：https://www.bilibili.com/video/BV1qD4y1U7fs/?spm_id_from=333.337.search-card.all.click&vd_source=288c9d9663183d48fd9c910c0b0e4367
    存在e盘
    不要发邮件
    """

  full_prompt = f"{SYSTEM_INSTRUCTION}\n\n[用户任务]:\n{user_prompt}"
  asyncio.run(run_crawler_agent(full_prompt))