# 🤖 Agent Web Scraper

一个基于 DeepSeek 与 Playwright 构建的智能网页爬虫与自动化 Agent。能够根据自然语言指令，自动完成复杂网页交互、影评/数据清洗提取，并支持结合 BBDown 内核实现高码率 B 站视频与音视频资源的解析合并与跨盘符落盘。
---

## ✨ 项目特性

* 🧠 智能决策：基于 DeepSeek 驱动 Agent 进行多步推理、任务拆解与异常自我修正。

* 🌐 动态网页爬取：集成 Playwright 无头浏览器，轻松应对异步加载（CSR/SSR）、DOM 节点动态渲染与页面交互。

* 📺 B 站视频一键解析下载：

* 集成 BBDown 内核与 FFmpeg，自动完成高画质/高音质 DASH 音视频轨的抓取与无损合并。

* 编码优化：默认采用 H.264 (AVC) 编码优先策略，彻底解决剪辑软件（如 Clipchamp、剪映）及系统播放器导入黑屏的问题。

* 📁 灵活路径控制：支持通过自然语言指定文件保存路径（如保存在 E 盘），工具层自动校验并创建绝对路径落盘。

* 🔒 安全配置：使用 .env 管理 API Key 等敏感凭证，避免密钥泄漏。
---

## 🛠️ 环境要求

* Python 3.9+

* FFmpeg（用于音视频自动合并，建议将 ffmpeg.exe 放至项目根目录或配置系统环境变量）

* BBDown（用于 B 站视频解析，放在项目根目录）

* 依赖库：playwright, requests, openai 等

---

## 🚀 快速开始

### 1. 克隆仓库与安装依赖

```bash
git clone https://github.com/Alex-jam-lab/gent-web-scraper.git
cd gent-web-scraper

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器内核
playwright install

```

### 2. 配置 API Key
复制配置文件模板：
```Bash
cp .env.example .env
```
在 .env 文件中填入你的 API Key 以及相关配置：
```env

DEEPSEEK_API_KEY=your_actual_api_key_here
```

### 3. 运行项目
修改 main.py 中的 user_prompt 任务指令后执行：
```bash
python main.py
```

### 项目结构
```Plaintext
gent-web-scraper/
├── .env.example       # 环境变量配置模板
├── config.py          # 基础配置文件
├── main.py            # 项目入口文件（包含 Prompt 预处理与 Agent 任务启动）
├── my_agent.py        # Agent 核心逻辑（工具调度与决策循环）
├── tools.py           # 工具函数库（包含 Playwright 网页交互、BBDown 视频下载等）
├── requirements.txt   # 项目依赖列表
├── BBDown.exe         # B 站下载内核（需自行准备）
├── ffmpeg.exe         # 音视频合成内核（需自行准备）
└── output/            # 默认自动生成的抓取数据与下载文件目录
```