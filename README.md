# 🤖 Agent Web Scraper

一个基于 **DeepSeek** 与 **Playwright** 构建的智能网页爬虫 Agent，能够根据自然语言指令自动完成网页交互与数据提取。

---

## ✨ 项目特性

* 🧠 **智能决策**：利用大语言模型（DeepSeek）进行步骤推理与任务拆解。
* 🌐 **动态交互**：基于 Playwright 支持复杂页面（JS 渲染、点击、滚动等）的自动化操作。
* 🔒 **安全配置**：使用 `.env` 管理 API Key 等敏感信息，防止密钥泄露。

---

## 🛠️ 环境要求

* Python 3.9+
* Playwright

---

## 🚀 快速开始

### 1. 克隆仓库与安装依赖

```bash
git clone [https://github.com/Alex-jam-lab/gent-web-scraper.git](https://github.com/Alex-jam-lab/gent-web-scraper.git)
cd gent-web-scraper

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器内核
playwright install
```

### 2. 配置环境变量

复制配置文件模板：

```bash
cp .env.example .env
```

在 `.env` 文件中填入你的 API Key：

```env
DEEPSEEK_API_KEY=your_actual_api_key_here
```

### 3. 运行项目

```bash
python main.py
```

---

## 📂 项目结构

```text
gent-web-scraper/
├── .env.example       # 环境变量配置模板
├── config.py          # 基础配置文件
├── main.py            # 项目入口文件
├── my_agent.py        # Agent 核心逻辑
├── tools.py           # 工具函数库
└── requirements.txt   # 项目依赖列表
```
