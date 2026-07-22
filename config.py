import os
from dotenv import load_dotenv

load_dotenv()

# 1. API 配置（优先读取 DEEPSEEK_API_KEY，若无则读取 OPENAI_API_KEY）
API_KEY = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL") or os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")

if not API_KEY:
    raise ValueError("❌ 未检测到 API Key！请确保在 .env 文件中配置了 DEEPSEEK_API_KEY 或 OPENAI_API_KEY。")

# 2. 邮件 SMTP 配置
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")

# 端口安全转换（避免空字符串引发 ValueError）
port_val = os.getenv("SMTP_PORT")
SMTP_PORT = int(port_val) if port_val and port_val.isdigit() else 465

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
# 去除 App Password 中常见的空格（比如 Google 生成授权码时带的空格）
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "").replace(" ", "").strip()
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")