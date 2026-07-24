import asyncio
import json
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import requests
from pathlib import Path
import config
import yt_dlp
import json
import logging
import re
from pathlib import Path
import requests




# 确保 output 目录存在
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


# 1. 浏览器单例控制器
class BrowserController:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    async def start(self, headless: bool = False):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({"width": 1280, "height": 800})

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


browser_ctrl = BrowserController()


# 2. 交互工具定义
async def navigate_to(url: str) -> str:
    """访问指定 URL"""
    try:
        logging.info(f"🌐 [Tool] 正在导航至: {url}")
        response = await browser_ctrl.page.goto(url, timeout=30000, wait_until="domcontentloaded")
        await asyncio.sleep(1)
        title = await browser_ctrl.page.title()
        status = response.status if response else 200
        return f"成功访问网址: {url} | HTTP 状态码: {status} | 页面标题: '{title}'"
    except Exception as e:
        return f"❌ 访问失败: {str(e)}"


async def scroll_down(pixels: int = 800) -> str:
    """向下滚动页面"""
    try:
        logging.info(f"📜 [Tool] 向下滚动 {pixels} 像素...")
        await browser_ctrl.page.mouse.wheel(0, pixels)
        await asyncio.sleep(1.5)
        return f"已向下滚动 {pixels} 像素。"
    except Exception as e:
        return f"❌ 滚动失败: {str(e)}"


async def extract_clean_text() -> str:
    """提取页面纯文本（省 Token）"""
    try:
        logging.info("🧹 [Tool] 正在清洗页面 DOM 并提取文本...")
        html = await browser_ctrl.page.content()
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "iframe", "svg"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        return f"清洗后的网页主要文本（前 3000 字）：\n{text[:3000]}"
    except Exception as e:
        return f"❌ 页面清洗提取失败: {str(e)}"


async def extract_by_selector(selector: str, attribute: Optional[str] = None) -> str:
    """用 CSS 选择器精准提取元素"""
    try:
        logging.info(f"🔍 [Tool] 提取选择器 [{selector}]...")
        try:
            await browser_ctrl.page.wait_for_selector(selector, timeout=4000)
        except Exception:
            return f"⚠️ 警告: 页面中未在 4 秒内找到元素 '{selector}'。"

        elements = await browser_ctrl.page.query_selector_all(selector)
        results = []
        for el in elements[:15]:
            if attribute:
                val = await el.get_attribute(attribute)
                if val:
                    results.append(val)
            else:
                text = await el.inner_text()
                if text.strip():
                    results.append(text.strip())

        return f"找到 {len(elements)} 个匹配项：\n" + json.dumps(results, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"❌ 选择器提取错误: {str(e)}"


async def click_element(selector: str) -> str:
    """点击元素"""
    try:
        logging.info(f"👆 [Tool] 点击元素: [{selector}]...")
        await browser_ctrl.page.wait_for_selector(selector, timeout=5000)
        await browser_ctrl.page.click(selector)
        await asyncio.sleep(2)
        return f"成功点击元素: [{selector}]"
    except Exception as e:
        return f"❌ 点击失败: {str(e)}"


async def save_data_to_file(filename: str, content: str) -> str:
    """持久化保存数据到本地 output 目录"""
    try:
        logging.info(f"💾 [Tool] 保存数据到本地: {filename}...")
        filepath = OUTPUT_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ 数据已成功存入本地文件: {filepath}"
    except Exception as e:
        return f"❌ 保存文件失败: {str(e)}"


async def send_email_notification(subject: str, content: str) -> str:
    """通过邮件通道发送通知"""
    if not all([config.SMTP_SERVER, config.SENDER_EMAIL, config.SENDER_PASSWORD, config.RECEIVER_EMAIL]):
        return "❌ 邮箱配置缺失，请先检查 .env 文件！"

    try:
        logging.info(f"📧 [Tool] 正在投递邮件至: {config.RECEIVER_EMAIL}...")

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = config.SENDER_EMAIL
        message["To"] = config.RECEIVER_EMAIL

        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f4f6f9; padding: 20px;">
            <div style="max-width: 650px; margin: 0 auto; background: #ffffff; padding: 24px; border-radius: 8px;">
              <h2 style="color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 8px;">🤖 Agent 自动化数据报告</h2>
              <div style="background-color: #f8f9fa; border-left: 4px solid #1a73e8; padding: 15px; font-family: monospace; white-space: pre-wrap; margin: 15px 0;">
{content}
              </div>
              <p style="font-size: 12px; color: #888;">—— 来自 DeepSeek + Playwright 智能 Agent</p>
            </div>
          </body>
        </html>
        """
        message.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT) as server:
            server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
            server.sendmail(config.SENDER_EMAIL, config.RECEIVER_EMAIL, message.as_string())

        return f"✅ 邮件推送成功！目标邮箱: {config.RECEIVER_EMAIL}"
    except Exception as e:
        return f"❌ 邮件发送失败: {str(e)}"


async def fetch_dynamic_quotes(scroll_times: int = 2) -> str:
    """
    [动态网页工具] 在当前已打开的页面中，连续模拟向下滚动以加载 AJAX / 动态渲染的数据，并返回清洗后的文本内容。
    """
    try:
        page = browser_ctrl.page
        if not page:
            return "❌ 错误: 浏览器尚未启动，请先调用 `navigate_to` 访问网址！"

        logging.info(f"📜 [Tool] 开始执行动态滚动加载，共 {scroll_times} 次...")

        for i in range(scroll_times):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1.5)

        quotes = await page.locator(".quote .text").all_text_contents()

        if quotes:
            return f"✅ 动态加载成功，共抓取到 {len(quotes)} 条文本数据：\n" + json.dumps(quotes, ensure_ascii=False,
                                                                                       indent=2)
        else:
            return await extract_clean_text()

    except Exception as e:
        return f"❌ 动态内容抓取失败: {str(e)}"


import logging
import subprocess
from pathlib import Path

# 默认保存目录
DEFAULT_OUTPUT_DIR = Path("output")
DEFAULT_OUTPUT_DIR.mkdir(exist_ok=True)


def download_bilibili_video(
    url: str,
    output_dir: str = None,
    filename: str = None,
    filename_prefix: str = None,
    encoding: str = "avc",
) -> str:
  """[B站专属下载工具] Calling BBDown 内核下载视频并自动合并音视频。

  ⚠️【大模型必须严格遵守】：
  1. 本工具【完全支持】直接写入本地任意盘符（如 E:\、D:\Videos 等）！
  2. 如果用户 Prompt 中提及了任何保存路径（如 "保存在E盘"、"存到 D:\视频"）：
     你【必须】将提取到的路径传入 output_dir 参数（例如 output_dir="E:\\"）。
     绝对不允许擅自忽略 output_dir 参数，更不允许在未传入参数时向用户宣称“不支持指定E盘”！

  Args:
      url: B站视频链接 (例如 BV号 或完整 URL)
      output_dir: 用户指定的保存路径/文件夹（如 'E:\\' 或 'E:\\Videos'）。若用户未指定路径，则保持为 None。
      filename: [可选] 指定保存的文件名（无需带 .mp4 后缀）。
      filename_prefix: [可选] 兼容参数，效果同 filename。
      encoding: 视频编码格式，默认为 'avc' (H.264，兼容性最高)
  """
  try:
    logging.info(f"📺 [Tool] 正在通过 BBDown 解析下载: {url}")

    # 1. 解析目标保存路径
    if output_dir and str(output_dir).strip():
      target_dir = Path(str(output_dir).strip()).absolute()
    else:
      target_dir = DEFAULT_OUTPUT_DIR.absolute()

    # 确保文件夹存在
    target_dir.mkdir(parents=True, exist_ok=True)

    # 2. 兼容文件名参数
    final_filename = filename or filename_prefix

    # 3. 构建 BBDown 命令
    cmd = [
        "BBDown.exe",
        url,
        "--work-dir",
        str(target_dir),
        "--multi-thread",
        "--encoding-priority",
        encoding,  # H.264 防黑屏
        "--sub-only",
        "false",
    ]

    if final_filename and str(final_filename).strip():
      cmd.extend(["--file-pattern", f"{str(final_filename).strip()}"])

    # 4. 执行下载
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
        errors="ignore",
    )

    log_tail = result.stdout[-300:] if result.stdout else "无日志输出"

    return (
        "✅ B 站视频下载并自动合并成功！\n"
        f"保存绝对路径: {target_dir}\n"
        f"文件名格式: {final_filename + '.mp4' if final_filename else '默认/视频原标题'}\n"
        f"运行日志: {log_tail}"
    )

  except subprocess.CalledProcessError as e:
    err_msg = e.stderr or e.stdout or "未知子进程错误"
    return f"❌ BBDown 下载失败，错误信息:\n{err_msg}"
  except Exception as e:
    return f"❌ 调用 BBDown 工具异常: {str(e)}"

# 3. 工具字典与 Schema 绑定映射
TOOLS_MAP = {
    "navigate_to": navigate_to,
    "scroll_down": scroll_down,
    "extract_clean_text": extract_clean_text,
    "extract_by_selector": extract_by_selector,
    "click_element": click_element,
    "save_data_to_file": save_data_to_file,
    "send_email_notification": send_email_notification,
    "fetch_dynamic_quotes": fetch_dynamic_quotes,
    "download_bilibili_video": download_bilibili_video, # 保留你正在使用的 B 站下载函数
}

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "navigate_to",
            "description": "访问指定的网页 URL",
            "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scroll_down",
            "description": "向下滚动页面",
            "parameters": {"type": "object", "properties": {"pixels": {"type": "integer"}}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_clean_text",
            "description": "获取清洗后的网页纯文本（省 Token）",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_by_selector",
            "description": "用 CSS 选择器精准提取节点",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS 选择器，如 'div.quote'"},
                    "attribute": {"type": "string", "description": "可选属性名"}
                },
                "required": ["selector"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "click_element",
            "description": "点击页面上的按钮或链接",
            "parameters": {"type": "object", "properties": {"selector": {"type": "string"}}, "required": ["selector"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_data_to_file",
            "description": "将数据保存到本地文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "如 'result.json'"},
                    "content": {"type": "string", "description": "文件具体文本/JSON"}
                },
                "required": ["filename", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email_notification",
            "description": "将最终处理完成的数据通过邮件推送给用户",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string", "description": "邮件标题"},
                    "content": {"type": "string", "description": "邮件正文格式化数据"}
                },
                "required": ["subject", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_dynamic_quotes",
            "description": "用于处理动态加载/下拉刷新的网页。在当前页面连续向下滚动并获取渲染后的新内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "scroll_times": {
                        "type": "integer",
                        "description": "向下滚动的次数，默认为 2 次"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "download_media_file",
            "description": "通过音视频文件的直链 URL 下载媒体文件并保存到本地 output 目录",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "媒体文件的直链地址"},
                    "filename": {"type": "string", "description": "保存到本地的文件名，如 video.mp4 或 audio.mp3"}
                },
                "required": ["url", "filename"]
            }
        }
    },

    {
    "type": "function",
    "function": {
        "name": "download_bilibili_video",
        "description": "通过 B 站视频的网页 URL 地址，自动下载并合并为 MP4 视频保存到本地",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "B 站视频的网页链接，如 https://www.bilibili.com/video/BV..."},
                "filename_prefix": {"type": "string", "description": "保存文件的前缀名"}
            },
            "required": ["url"]
        }
    }
    }
]