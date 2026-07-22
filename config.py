import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "").replace(" ", "").strip()
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

if not API_KEY:
    raise ValueError("❌ 未检测到 OPENAI_API_KEY，请确保在 .env 文件中正确配置！")
