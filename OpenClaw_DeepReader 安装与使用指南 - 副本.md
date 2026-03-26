# 🦞 OpenClaw DeepReader 完整安装与使用指南

> **版本**: 1.0.0  
> **最后更新**: 2026-03-09  
> **适用系统**: Windows / macOS / Linux  
> **前置条件**: 已安装 OpenClaw

---

## 📋 目录

1. [DeepReader 是什么](#一deepreader-是什么)
2. [安装前准备](#二安装前准备)
3. [详细安装步骤](#三详细安装步骤)
4. [配置说明](#四配置说明)
5. [使用方法](#五使用方法)
6. [实战案例](#六实战案例)
7. [常见问题](#七常见问题)
8. [高级技巧](#八高级技巧)
9. [最佳实践](#九最佳实践)

---

## 一、DeepReader 是什么

**DeepReader** 是 OpenClaw 的默认网页内容读取器，核心功能：

> **将任意 URL 自动转化为 OpenClaw 智能体的长期记忆**

### ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🚀 **零配置** | 无需 API Key，无需登录 |
| 🌐 **多平台支持** | Twitter/X、Reddit、YouTube、任意网页 |
| 📝 **Markdown 输出** | 自动清洗为干净格式 |
| 💾 **自动保存** | 保存到智能体记忆库 |
| 🔍 **智能路由** | 自动识别 URL 类型并选择解析器 |

### 📊 支持的平台

| 平台 | 支持内容 | 技术实现 |
|------|---------|---------|
| 🐦 **Twitter/X** | 推文、线程、X Articles、个人资料 | FxTwitter API + Nitter |
| 🟠 **Reddit** | 帖子 + 评论线程 | Reddit .json API |
| 🎬 **YouTube** | 视频字幕/转录 | youtube-transcript-api |
| 🌐 **任意网页** | 博客、文章、文档 | Trafilatura + BeautifulSoup |

---

## 二、安装前准备

### 1️⃣ 检查系统要求

```bash
# 检查 Python 版本（需要 3.10+）
python --version

# 检查是否已安装 OpenClaw
openclaw status
```

### 2️⃣ 配置网络代理（中国大陆用户必读）

由于 GitHub 和部分外网服务可能被限制，需要配置代理：

#### 方法 A：临时设置（当前终端会话）

```powershell
# Windows PowerShell
$env:HTTP_PROXY="http://127.0.0.1:10808"
$env:HTTPS_PROXY="http://127.0.0.1:10808"
```

```bash
# macOS / Linux
export HTTP_PROXY="http://127.0.0.1:10808"
export HTTPS_PROXY="http://127.0.0.1:10808"
```

#### 方法 B：永久设置（推荐）

**Windows**:

1. `Win + R` → 输入 `sysdm.cpl` → 回车
2. 点击"高级" → "环境变量"
3. 在"用户变量"中新建：
   - 变量名：`HTTP_PROXY`，变量值：`http://127.0.0.1:10808`
   - 变量名：`HTTPS_PROXY`，变量值：`http://127.0.0.1:10808`
4. 重启终端生效

**macOS / Linux**:

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
echo 'export HTTP_PROXY="http://127.0.0.1:10808"' >> ~/.bashrc
echo 'export HTTPS_PROXY="http://127.0.0.1:10808"' >> ~/.bashrc
source ~/.bashrc
```

#### 方法 C：配置 Git 代理

```bash
git config --global http.proxy http://127.0.0.1:10808
git config --global https.proxy http://127.0.0.1:10808
```

### 3️⃣ 验证网络连接

```bash
# 测试 GitHub 连接
curl -s -o nul -w "HTTP Status: %{http_code}\n" https://github.com/

# 预期输出：HTTP Status: 200
```

---

## 三、详细安装步骤

### 方法一：使用 ClawHub（推荐）

```bash
# 一键安装
npx clawhub@latest install deepreader
```

### 方法二：手动安装（完整版）

#### 步骤 1：克隆仓库

```bash
# 进入 OpenClaw skills 目录
cd C:\Users\Administrator\.openclaw\skills

# 克隆 DeepReader 仓库
git clone --depth 1 https://github.com/astonysh/OpenClaw-DeepReeder.git
```

#### 步骤 2：安装依赖

```bash
# 进入项目目录
cd OpenClaw-DeepReeder

# 使用 uv 安装依赖（推荐）
uv pip install -e .

# 或使用 pip
pip install -e .
```

#### 步骤 3：验证安装

```bash
# 测试抓取网页
uv run python -c "from deepreader_skill import run; run('https://www.baidu.com')"

# 检查输出目录是否生成文件
ls memory/inbox/
```

### 方法三：手动安装（精简版）

如果无法访问 GitHub，可以创建基础版本：

```bash
# 创建目录
mkdir -p C:\Users\Administrator\.openclaw\skills\deepreader
cd C:\Users\Administrator\.openclaw\skills\deepreader

# 创建 requirements.txt
cat > requirements.txt << EOF
requests>=2.31.0
beautifulsoup4>=4.12.0
trafilatura>=1.6.0
youtube-transcript-api>=0.6.0
EOF

# 安装依赖
uv pip install -r requirements.txt
```

---

## 四、配置说明

### 1️⃣ 目录结构

```
OpenClaw-DeepReeder/
├── deepreader_skill/
│   ├── __init__.py         # 入口文件
│   ├── manifest.json       # 技能配置
│   ├── SKILL.md            # 使用文档
│   ├── requirements.txt    # 依赖列表
│   ├── core/
│   │   ├── router.py       # URL 路由逻辑
│   │   ├── storage.py      # 文件保存管理
│   │   └── utils.py        # 工具函数
│   └── parsers/
│       ├── base.py         # 基础解析器类
│       ├── generic.py      # 通用网页解析
│       ├── twitter.py      # Twitter/X 解析
│       ├── reddit.py       # Reddit 解析
│       └── youtube.py      # YouTube 解析
├── pyproject.toml          # Python 项目配置
└── README.md               # 项目说明
```

### 2️⃣ 环境变量配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `DEEPREEDER_MEMORY_PATH` | `../../memory/inbox/` | Markdown 文件保存路径 |
| `DEEPREEDER_LOG_LEVEL` | `INFO` | 日志级别（DEBUG/INFO/WARNING/ERROR） |
| `HTTP_PROXY` | - | HTTP 代理地址 |
| `HTTPS_PROXY` | - | HTTPS 代理地址 |

### 3️⃣ 输出文件格式

每个 URL 会被保存为 Markdown 文件，包含：

```markdown
---
uuid: 27e9db2b-e8ef-49b6-a8d0-1d09b17f00f8
source: "https://x.com/user/status/123"
date: 2026-03-09T05:19:01.314773+00:00
type: external_resource
tags:
  - "imported"
  - "x_com"
  - "twitter"
title: "文章标题"
author: "@username"
content_hash: d5df3427e011bd6a3472386beb3d9cc114c65b87...
---

# 文章标题

**作者** · 发布时间

📊 ❤️ 点赞 🔁 转发 🔖 收藏 👁️ 浏览

---

正文内容...
```

---

## 五、使用方法

### 1️⃣ 在 OpenClaw 中自动触发（最常用）

**直接在对话中发送包含 URL 的消息**，DeepReader 会自动处理：

```
帮我读一下这篇文章：https://example.com/blog/ai-agents
```

```
看看这个推文说了什么：https://x.com/elonmusk/status/123456
```

```
我想了解这个视频的内容：https://youtube.com/watch?v=xxx
```

### 2️⃣ Python API 调用

```python
from deepreader_skill import run

# 处理单个 URL
result = run("https://example.com/article")

# 处理多个 URL
result = run("""
请阅读以下内容：
https://x.com/user/status/123
https://reddit.com/r/python/comments/abc
https://youtube.com/watch?v=xyz
""")

# 查看结果
for r in result:
    print(f"URL: {r['url']}")
    print(f"文件：{r['filepath']}")
```

### 3️⃣ 命令行调用

```bash
# 设置代理（如需要）
export HTTP_PROXY="http://127.0.0.1:10808"
export HTTPS_PROXY="http://127.0.0.1:10808"

# 运行
cd OpenClaw-DeepReeder
uv run python -c "from deepreader_skill import run; run('https://www.baidu.com')"
```

### 4️⃣ 批量处理

```python
from deepreader_skill import run

urls = """
https://x.com/user1/status/111
https://x.com/user2/status/222
https://reddit.com/r/ai/comments/abc
https://youtube.com/watch?v=111
https://youtube.com/watch?v=222
https://example.com/article1
https://example.com/article2
"""

results = run(urls)
print(f"成功处理 {len(results)} 个 URL")
```

---

## 六、实战案例

### 案例 1：读取 Twitter/X 长文

**场景**: 需要分析一篇 X Article

```
用户：请帮我总结这篇 X 文章的核心观点
https://x.com/berryxia/status/2029950589313101902
```

**DeepReader 输出**:

```
📄 已读取：五步用 Telegram 创建 OpenClaw 多角色群聊！

📊 互动数据:
- ❤️ 507 点赞
- 🔁 124 转发
- 👁️ 151,457 浏览

📝 核心内容摘要:
1. 一个 Gateway + 一个 Bot + 多个群组 = 多角色 AI 团队
2. 五步配置流程...
3. 两种架构选择...

📂 完整内容已保存到：memory/inbox/2026-03-09_telegram-openclaw.md
```

### 案例 2：分析 Reddit 技术讨论

**场景**: 了解某个技术话题的社区讨论

```
用户：我想了解 Python 社区对 AI Agent 框架的看法
https://reddit.com/r/Python/comments/abc123/best_ai_agent_framework
```

**DeepReader 输出**:

```
📄 已读取：[r/Python] Best AI Agent Framework for 2026?

📊 帖子数据:
- ⬆️ 847 点赞 (96% 好评)
- 💬 234 条评论

💬 热门评论摘要:
1. u/expert_dev (⬆️ 342): "推荐 OpenClaw，因为..."
2. u/pythonista (⬆️ 215): "LangChain 更成熟，但是..."
3. u/ai_researcher (⬆️ 189): "从研究角度看..."

📂 完整讨论已保存到：memory/inbox/2026-03-09_reddit_python.md
```

### 案例 3：提取 YouTube 视频字幕

**场景**: 需要搜索视频内容或做文字分析

```
用户：帮我提取这个教程的字幕，我想搜索关键内容
https://youtube.com/watch?v=dQw4w9WgXcQ
```

**DeepReader 输出**:

```
📄 已读取：YouTube 视频字幕

🎬 视频信息:
- 标题：AI Agent 开发教程
- 时长：15:32
- 字幕语言：中文

📝 字幕已提取（约 3000 字）
关键时间点:
- 02:15 - 环境配置
- 05:30 - 核心架构
- 10:45 - 实战演示

📂 完整字幕已保存到：memory/inbox/2026-03-09_youtube.md
```

### 案例 4：批量读取行业资讯

**场景**: 每日收集 AI 行业资讯

```python
from deepreader_skill import run

# 每日必读链接列表
daily_links = """
https://x.com/OpenClaw/status/daily1
https://x.com/ai_news/status/daily2
https://reddit.com/r/MachineLearning/comments/daily3
https://example.com/ai-digest-2026-03-09
"""

print("📰 开始处理每日资讯...")
results = run(daily_links)
print(f"✅ 成功处理 {len(results)} 篇")

# 生成摘要
for r in results:
    print(f"\n📌 {r['title']}")
    print(f"   来源：{r['url']}")
```

### 案例 5：竞品分析

**场景**: 收集竞品动态进行分析

```python
from deepreader_skill import run
import os

# 竞品列表
competitors = [
    "https://x.com/competitor1",
    "https://x.com/competitor2",
    "https://competitor1.com/blog",
    "https://competitor2.com/updates"
]

# 创建竞品分析目录
os.makedirs("memory/competitor_analysis", exist_ok=True)

print("🔍 开始竞品分析数据收集...")
for url in competitors:
    result = run(url)
    print(f"✓ 已读取：{result[0]['title']}")

print("\n✅ 数据收集完成，可在 memory/inbox/ 查看")
```

### 案例 6：用 NotebookLM 生成学习资料（高级）

**场景**: 将技术文章转换为多种学习格式

```python
from deepreader_skill import run

# 目标文章
article = "https://example.com/ai-agent-architecture"

print("📚 开始生成学习资料包...\n")

# 1. 上传到 NotebookLM
print("📤 上传到 NotebookLM...")
result = run(article, notebooklm=True)
print(f"✓ 笔记本已创建：{result['notebook_name']}")

# 2. 生成播客（通勤学习）
print("\n🎙️ 生成播客...")
result = run(article, notebooklm=True, audio=True)
print(f"✓ 播客已保存：{result['audio_path']}")
print(f"  时长：{result['audio_duration']} 分钟")

# 3. 生成思维导图（知识梳理）
print("\n🧠 生成思维导图...")
result = run(article, notebooklm=True, mindmap=True)
print(f"✓ 思维导图已保存：{result['mindmap_path']}")

# 4. 生成抽认卡（记忆复习）
print("\n📇 生成抽认卡...")
result = run(article, notebooklm=True, flashcards=True)
print(f"✓ 生成 {result['flashcard_count']} 张抽认卡")
print(f"  保存位置：{result['flashcards_path']}")

# 5. 生成测验题（自我测试）
print("\n❓ 生成测验题...")
result = run(article, notebooklm=True, quiz=True)
print(f"✓ 生成 {result['quiz_count']} 道测验题")
print(f"  难度：{result['quiz_difficulty']}")

print("\n✅ 学习资料包生成完成！")
print("\n📂 文件清单:")
print(f"  📄 原文：{result['markdown_path']}")
print(f"  🎙️ 播客：{result['audio_path']}")
print(f"  🧠 思维导图：{result['mindmap_path']}")
print(f"  📇 抽认卡：{result['flashcards_path']}")
print(f"  ❓ 测验题：{result['quiz_path']}")
```

**输出示例**:

```
📚 开始生成学习资料包...

📤 上传到 NotebookLM...
✓ 笔记本已创建：AI Agent Architecture Study

🎙️ 生成播客...
✓ 播客已保存：memory/inbox/2026-03-09_ai_agent_audio.mp3
  时长：12 分钟

🧠 生成思维导图...
✓ 思维导图已保存：memory/inbox/2026-03-09_ai_agent_mindmap.png

📇 生成抽认卡...
✓ 生成 20 张抽认卡
  保存位置：memory/inbox/2026-03-09_ai_agent_flashcards.json

❓ 生成测验题...
✓ 生成 10 道测验题
  难度：medium

✅ 学习资料包生成完成！

📂 文件清单:
  📄 原文：memory/inbox/2026-03-09_ai_agent.md
  🎙️ 播客：memory/inbox/2026-03-09_ai_agent_audio.mp3
  🧠 思维导图：memory/inbox/2026-03-09_ai_agent_mindmap.png
  📇 抽认卡：memory/inbox/2026-03-09_ai_agent_flashcards.json
  ❓ 测验题：memory/inbox/2026-03-09_ai_agent_quiz.json
```

### 案例 7：YouTube 视频学习套装

**场景**: 将 YouTube 教程转换为完整学习资料

```python
from deepreader_skill import run

# YouTube 视频 URL
video_url = "https://youtube.com/watch?v=ai-tutorial-2026"

print("🎬 开始处理 YouTube 视频...\n")

# 1. 提取字幕
print("📝 提取字幕...")
result = run(video_url)
print(f"✓ 字幕已提取：{result['word_count']} 字")

# 2. 上传到 NotebookLM 并生成播客（音频版教程）
print("\n🎙️ 生成音频教程...")
result = run(video_url, notebooklm=True, audio=True)
print(f"✓ 音频教程已生成：{result['audio_path']}")

# 3. 生成抽认卡（关键概念记忆）
print("\n📇 生成概念抽认卡...")
result = run(video_url, notebooklm=True, flashcards=True)
print(f"✓ 生成 {result['flashcard_count']} 张概念卡")

# 4. 生成测验（学习成果检验）
print("\n❓ 生成学习测验...")
result = run(video_url, notebooklm=True, quiz=True)
print(f"✓ 生成 {result['quiz_count']} 道测验题")

print("\n✅ YouTube 视频学习套装已生成！")
print("\n💡 学习建议:")
print("  1️⃣ 先听音频教程了解概览")
print("  2️⃣ 用抽认卡记忆关键概念")
print("  3️⃣ 做测验检验学习成果")
print("  4️⃣ 查看思维导图建立知识框架")
```

---

## 七、常见问题

### Q1: 安装时遇到 "Rate limit exceeded"

**原因**: GitHub API 调用频率限制

**解决方案**:

```bash
# 等待几分钟后重试
# 或使用手动安装方法
git clone --depth 1 https://github.com/astonysh/OpenClaw-DeepReeder.git
```

### Q2: 无法连接 GitHub

**原因**: 网络限制

**解决方案**:

```bash
# 配置代理
export HTTP_PROXY="http://127.0.0.1:10808"
export HTTPS_PROXY="http://127.0.0.1:10808"

# 测试连接
curl -I https://github.com
```

### Q3: 抓取 Twitter/X 失败

**原因**: Twitter 反爬虫或 API 限制

**解决方案**:

1. 检查代理是否生效
2. DeepReader 会自动使用 FxTwitter API + Nitter 备用
3. 如仍失败，使用通用解析器 fallback

### Q4: YouTube 字幕无法获取

**原因**: 视频无字幕或字幕被禁用

**解决方案**:

```python
# 检查视频是否有字幕
from youtube_transcript_api import YouTubeTranscriptApi

video_id = "dQw4w9WgXcQ"
try:
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    print("✓ 有字幕")
except:
    print("✗ 无字幕")
```

### Q5: 中文输出乱码

**原因**: Windows 控制台编码问题

**解决方案**:

```powershell
# 设置控制台编码
chcp 65001

# 或在 Python 脚本开头添加
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
```

### Q6: 文件保存位置找不到

**解决方案**:

```bash
# 查看默认保存路径
# Windows
dir C:\Users\Administrator\.openclaw\skills\memory\inbox\

# macOS / Linux
ls ~/memory/inbox/

# 或自定义路径
export DEEPREEDER_MEMORY_PATH="/your/custom/path"
```

### Q7: 依赖安装失败

**解决方案**:

```bash
# 升级 pip
pip install --upgrade pip

# 使用 uv（推荐）
uv pip install -r requirements.txt

# 或逐个安装
pip install trafilatura
pip install youtube-transcript-api
pip install requests
pip install beautifulsoup4
```

---

## 八、高级技巧

### 1️⃣ 自定义解析器

```python
# 在 parsers/ 目录添加自定义解析器
class CustomParser(BaseParser):
    def parse(self, url: str) -> ParseResult:
        # 自定义解析逻辑
        pass
```

### 2️⃣ 集成 Google NotebookLM（高级功能）

DeepReader 支持将抓取的内容上传到 **Google NotebookLM**，并自动生成多种格式的学习资料。

#### 📋 前置要求

1. **Google 账号**: 需要有 Google 账号
2. **认证 NotebookLM**: 首次使用前需要认证

```bash
# 登录 NotebookLM
notebooklm login
```

认证后会保存凭证到 `~/.notebooklm/credentials.json`

#### 🎯 支持的输出格式

| 格式 | 说明 | 使用场景 |
|------|------|---------|
| 🎙️ **Audio Overview** | AI 生成的播客对话 | 通勤学习、听觉学习 |
| 🎥 **Video Overview** | 视频概述 | 演示、分享 |
| 🧠 **Mind Map** | 思维导图 | 知识梳理、结构化学习 |
| 📄 **Reports** | 详细报告 | 深度研究、文档归档 |
| 📇 **Flashcards** | 抽认卡 | 记忆复习、考试准备 |
| ❓ **Quiz** | 测验题 | 自我测试、知识检验 |
| 📊 **Infographic** | 信息图 | 可视化展示、分享传播 |
| 🖥️ **Slide Deck** | 幻灯片 | 演讲、培训 |
| 📈 **Data Table** | 数据表格 | 数据分析、对比研究 |

#### 💡 使用方法

**方法 1: 命令行标志**

```bash
# 上传并生成播客
result = run("https://example.com/article --notebooklm --audio")

# 上传并生成思维导图
result = run("https://example.com/article --notebooklm --mindmap")

# 上传并生成抽认卡
result = run("https://example.com/article --notebooklm --flashcards")
```

**方法 2: Python API**

```python
from deepreader_skill import run

# 单个 URL + 播客
result = run("https://youtube.com/watch?v=xxx", notebooklm=True, audio=True)

# 单个 URL + 多种格式
result = run(
    "https://example.com/article",
    notebooklm=True,
    formats=["audio", "mindmap", "flashcards"]
)

# 批量 URL + NotebookLM
urls = """
https://x.com/user/status/111
https://reddit.com/r/ai/comments/abc
https://example.com/research-paper
"""
result = run(urls, notebooklm=True, audio=True)
```

**方法 3: 在 OpenClaw 对话中**

```
用户：请帮我把这篇文章上传到 NotebookLM 并生成播客
https://example.com/article --notebooklm --audio

用户：我想基于这个 YouTube 视频生成抽认卡复习
https://youtube.com/watch?v=xxx --notebooklm --flashcards
```

#### 📁 输出文件位置

生成的文件会保存到记忆库目录：

```
memory/inbox/
├── 2026-03-09_article.md           # 原始 Markdown
├── 2026-03-09_article_audio.mp3    # 播客音频
├── 2026-03-09_article_mindmap.png  # 思维导图
├── 2026-03-09_article_flashcards.json  # 抽认卡数据
└── ...
```

#### 🎬 完整示例

```python
from deepreader_skill import run
import os

# 技术文章学习
article_url = "https://example.com/ai-agent-architecture"

print("📚 开始处理学习资料...")

# 1. 上传到 NotebookLM 并生成播客
print("🎙️ 生成播客...")
result = run(article_url, notebooklm=True, audio=True)
print(f"✓ 播客已保存：{result['audio_path']}")

# 2. 生成思维导图
print("🧠 生成思维导图...")
result = run(article_url, notebooklm=True, mindmap=True)
print(f"✓ 思维导图已保存：{result['mindmap_path']}")

# 3. 生成抽认卡
print("📇 生成抽认卡...")
result = run(article_url, notebooklm=True, flashcards=True)
print(f"✓ 抽认卡已保存：{result['flashcards_path']}")

# 4. 生成测验题
print("❓ 生成测验题...")
result = run(article_url, notebooklm=True, quiz=True)
print(f"✓ 测验题已保存：{result['quiz_path']}")

print("\n✅ 学习资料生成完成！")
print(f"\n📂 所有文件位置：{os.path.dirname(result['markdown_path'])}")
```

#### ⚙️ 配置选项

```python
# 自定义 NotebookLM 设置
result = run(
    "https://example.com/article",
    notebooklm=True,
    audio=True,
    notebooklm_config={
        "notebook_name": "AI 学习资料",  # 自定义笔记本名称
        "audio_duration": "medium",      # 音频时长：short/medium/long
        "flashcard_count": 20,           # 抽认卡数量
        "quiz_difficulty": "medium",     # 测验难度：easy/medium/hard
        "language": "zh-CN"              # 输出语言
    }
)
```

#### 🔧 故障排除

**问题 1: 认证失败**

```bash
# 重新认证
notebooklm logout
notebooklm login
```

**问题 2: 上传失败**

```bash
# 检查网络连接
# 确保能访问 Google 服务
curl -I https://notebooklm.google.com
```

**问题 3: 生成格式不支持**

```python
# 查看支持的格式
from deepreader_skill.integrations import notebooklm
print(notebooklm.SUPPORTED_FORMATS)
```

### 3️⃣ 设置记忆库路径

```bash
# 环境变量
export DEEPREEDER_MEMORY_PATH="/path/to/your/memory"

# 或在代码中
from deepreader_skill import run
run("https://example.com", memory_path="/custom/path")
```

### 4️⃣ 日志调试

```bash
# 开启详细日志
export DEEPREEDER_LOG_LEVEL="DEBUG"

# 查看实时日志
tail -f memory/inbox/*.md
```

---

## 九、最佳实践

### ✅ 推荐做法

1. **定期清理记忆库**: 避免文件过多影响性能
2. **使用有意义的 URL**: 便于后续检索
3. **批量处理时控制数量**: 建议每次不超过 20 个 URL
4. **保存重要内容备份**: 记忆库文件可能更新

### ❌ 避免做法

1. **不要抓取付费墙内容**: 可能违反服务条款
2. **不要高频抓取同一网站**: 可能被封 IP
3. **不要依赖单一数据源**: 重要信息多源验证
4. **不要忽略版权**: 商业用途注意授权

---

## 十、资源链接

| 资源 | 链接 |
|------|------|
| **GitHub 仓库** | https://github.com/astonysh/OpenClaw-DeepReeder |
| **OpenClaw 文档** | https://docs.openclaw.ai |
| **ClawHub** | https://clawhub.ai |
| **问题反馈** | https://github.com/astonysh/OpenClaw-DeepReeder/issues |
| **社区 Discord** | https://discord.com/invite/clawd |

---

## 📝 更新日志

| 日期 | 版本 | 内容 |
|------|------|------|
| 2026-03-09 | 1.1.0 | 完善安装指南，添加代理配置说明、7 个实战案例、NotebookLM 详细教程 |
| 2026-03-06 | 1.0.0 | 添加 NotebookLM 集成（支持 9 种输出格式） |
| 2026-02-16 | 0.1.0 | 初始版本发布 |

---

## 📎 附录：快速参考卡片

```
┌─────────────────────────────────────────────────────────┐
│           OpenClaw DeepReader 快速参考                   │
├─────────────────────────────────────────────────────────┤
│  安装：npx clawhub@latest install deepreader            │
│  测试：uv run python -c "from deepreader_skill import    │
│        run; run('https://www.baidu.com')"               │
│                                                         │
│  使用：直接在 OpenClaw 对话中发送 URL                    │
│                                                         │
│  支持：Twitter/X · Reddit · YouTube · 任意网页          │
│                                                         │
│  输出：memory/inbox/*.md                                │
│                                                         │
│  代理：export HTTP_PROXY="http://127.0.0.1:10808"       │
│                                                         │
│  日志：export DEEPREEDER_LOG_LEVEL="DEBUG"              │
└─────────────────────────────────────────────────────────┘
```

---

> **提示**: 本指南基于实际安装和使用经验编写，如遇问题可参考 GitHub Issues 或联系社区。
> 
> **作者**: OpenClaw Community  
> **许可**: MIT License  
> **生成时间**: 2026-03-09 14:04 GMT+8
