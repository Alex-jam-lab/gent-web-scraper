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
    请调用 download_media_file 工具，
将测试视频 'https://www.w3schools.com/html/mov_bbb.mp4' 
下载并保存为本地的 'output/test_video.mp4'。
    
    """

    # 启动任务
    asyncio.run(run_crawler_agent(user_prompt))