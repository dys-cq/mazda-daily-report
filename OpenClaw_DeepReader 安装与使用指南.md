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
10. [资源链接](#十资源链接)
11. [NotebookLM 集成详解](#十一 notebooklm-集成详解)
12. [性能优化](#十二性能优化)
13. [安全与隐私](#十三安全与隐私)

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
| 🎙️ NotebookLM 集成| 支持将内容上传到 Google NotebookLM 并生成多种格式

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
| **Google NotebookLM** | https://notebooklm.google.com |
| **FxTwitter API** | https://github.com/FxEmbed/FxEmbed |
| **Trafilatura 文档** | https://trafilatura.readthedocs.io |

---

## 十一、NotebookLM 集成详解

### 11.1 认证流程（图文步骤）

#### 步骤 1：检查认证状态

```bash
# 查看当前认证状态
notebooklm status
```

**预期输出**:
```
✓ 已认证：your-email@gmail.com
  令牌有效期：2026-04-09
  笔记本数量：5
```

或

```
✗ 未认证
  请运行：notebooklm login
```

#### 步骤 2：执行认证

```bash
# 启动认证流程
notebooklm login
```

**认证过程**:

```
🔐 NotebookLM Authentication

1. 打开浏览器访问：
   https://notebooklm.google.com/auth/device-code

2. 输入认证码：ABCD-1234

3. 使用 Google 账号登录并授权

4. 认证成功后返回终端...

✓ 认证成功！
  账号：your-email@gmail.com
  令牌已保存到：~/.notebooklm/credentials.json
```

#### 步骤 3：验证认证

```bash
# 测试连接
notebooklm list
```

**预期输出**:
```
📓 你的 NotebookLM 笔记本:

  1. 默认笔记本 (2026-03-01)
  2. AI 学习资料 (2026-03-05)
  3. 研究论文 (2026-03-08)
  
共 3 个笔记本
```

### 11.2 凭证管理

#### 凭证文件位置

| 系统 | 路径 |
|------|------|
| **Windows** | `C:\Users\<用户名>\.notebooklm\credentials.json` |
| **macOS** | `~/.notebooklm/credentials.json` |
| **Linux** | `~/.notebooklm/credentials.json` |

#### 凭证文件内容示例

```json
{
  "email": "your-email@gmail.com",
  "access_token": "ya29.a0AfH6SMBxxx...",
  "refresh_token": "1//0Gxxx...",
  "token_type": "Bearer",
  "expiry": "2026-04-09T14:00:00Z"
}
```

⚠️ **安全提醒**: 不要将此文件上传到 Git 或分享给他人！

#### 管理命令

```bash
# 退出登录（删除凭证）
notebooklm logout

# 切换账号
notebooklm logout
notebooklm login

# 刷新令牌
notebooklm refresh

# 查看凭证详情
notebooklm auth info
```

### 11.3 高级配置

#### 自定义笔记本名称

```python
from deepreader_skill import run

# 指定笔记本名称
result = run(
    "https://example.com/article",
    notebooklm=True,
    notebook_name="AI 技术学习笔记"
)
```

#### 批量内容合并到一个笔记本

```python
from deepreader_skill import run

# 定义学习主题
topic = "AI Agent 架构"
notebook_name = f"{topic} 专题研究"

# 相关文章列表
articles = [
    "https://example.com/agent-architecture-101",
    "https://example.com/agent-memory-systems",
    "https://example.com/agent-planning-strategies",
    "https://x.com/expert/status/agent-best-practices"
]

print(f"📚 创建专题笔记本：{notebook_name}\n")

# 逐个上传
for i, url in enumerate(articles, 1):
    print(f"[{i}/{len(articles)}] 处理：{url}")
    result = run(
        url,
        notebooklm=True,
        notebook_name=notebook_name,
        merge=True  # 合并到同一笔记本
    )
    print(f"  ✓ 已添加：{result['title']}")

print(f"\n✅ 专题笔记本创建完成！")
print(f"📓 笔记本名称：{notebook_name}")
print(f"📄 包含文档：{len(articles)} 篇")
```

#### 自定义生成参数

```python
from deepreader_skill import run

result = run(
    "https://example.com/advanced-ai-concepts",
    notebooklm=True,
    
    # 音频配置
    audio=True,
    audio_config={
        "duration": "medium",      # short(5 分钟) / medium(15 分钟) / long(30 分钟)
        "voice": "conversational", # conversational / formal / enthusiastic
        "language": "zh-CN",       # 输出语言
        "speakers": 2              # 播客主持人数量 (1-4)
    },
    
    # 抽认卡配置
    flashcards=True,
    flashcard_config={
        "count": 30,               # 卡片数量 (10-100)
        "difficulty": "medium",    # easy / medium / hard
        "type": "cloze",           # basic(问答) / cloze(填空) / both
        "include_examples": True   # 是否包含示例
    },
    
    # 测验配置
    quiz=True,
    quiz_config={
        "count": 20,               # 题目数量 (5-50)
        "difficulty": "medium",    # easy / medium / hard
        "question_types": ["multiple_choice", "true_false"],
        "include_explanations": True  # 包含答案解析
    },
    
    # 思维导图配置
    mindmap=True,
    mindmap_config={
        "depth": 3,                # 层级深度 (1-5)
        "format": "png",           # png / svg / pdf
        "layout": "hierarchical",  # hierarchical / radial / organic
        "include_icons": True      # 包含图标
    }
)

# 查看生成的文件
print("\n📂 生成的文件:")
for key, path in result.items():
    if key.endswith('_path'):
        print(f"  {key}: {path}")
```

### 11.4 输出格式详解

#### 🎙️ Audio Overview（音频概述）

**文件格式**: MP3  
**典型大小**: 5-30 MB  
**适用场景**: 通勤、运动、做家务时学习

```python
result = run("https://example.com/article", notebooklm=True, audio=True)

# 输出信息
print(f"音频时长：{result['audio_duration_minutes']} 分钟")
print(f"文件大小：{result['audio_size_mb']} MB")
print(f"保存位置：{result['audio_path']}")
```

**音频内容结构**:
- 开场介绍 (30 秒)
- 核心概念讲解 (40%)
- 关键要点总结 (30%)
- 实际应用案例 (20%)
- 结束语 (30 秒)

#### 🧠 Mind Map（思维导图）

**文件格式**: PNG / SVG / PDF  
**典型大小**: 500 KB - 5 MB  
**适用场景**: 知识梳理、复习、演讲准备

```python
result = run("https://example.com/article", notebooklm=True, mindmap=True)

# 思维导图包含:
# - 中心主题
# - 主要分支 (3-8 个)
# - 子分支 (每分支 2-5 个)
# - 关键词标注
# - 颜色编码
```

**思维导图结构**:
```
中心主题
├── 核心概念 1
│   ├── 子概念 1.1
│   └── 子概念 1.2
├── 核心概念 2
│   ├── 子概念 2.1
│   └── 子概念 2.2
└── 核心概念 3
    ├── 子概念 3.1
    └── 子概念 3.2
```

#### 📇 Flashcards（抽认卡）

**文件格式**: JSON / Anki (.apkg)  
**典型大小**: 10-100 KB  
**适用场景**: 记忆复习、考试准备

```python
result = run("https://example.com/article", notebooklm=True, flashcards=True)

# 抽认卡数据结构
{
    "deck_name": "AI Agent 架构",
    "cards": [
        {
            "front": "什么是 AI Agent 的核心组成部分？",
            "back": "感知模块、决策模块、执行模块、记忆模块",
            "difficulty": "medium",
            "tags": ["基础概念", "架构"]
        },
        {
            "front": "ReAct 框架的全称是什么？",
            "back": "Reasoning + Acting",
            "difficulty": "easy",
            "tags": ["框架", "方法论"]
        }
    ]
}
```

**导入 Anki**:
```python
# 导出为 Anki 格式
result = run(
    "https://example.com/article",
    notebooklm=True,
    flashcards=True,
    export_format="anki"  # 或 "json"
)

# 生成的 .apkg 文件可直接导入 Anki
print(f"Anki 包：{result['anki_package_path']}")
```

#### ❓ Quiz（测验题）

**文件格式**: JSON / HTML / PDF  
**典型大小**: 50-500 KB  
**适用场景**: 自我测试、培训考核

```python
result = run("https://example.com/article", notebooklm=True, quiz=True)

# 测验题数据结构
{
    "quiz_name": "AI Agent 架构测试",
    "total_questions": 20,
    "passing_score": 70,
    "time_limit_minutes": 30,
    "questions": [
        {
            "id": 1,
            "type": "multiple_choice",
            "question": "以下哪项不是 AI Agent 的核心组件？",
            "options": [
                "A. 感知模块",
                "B. 决策模块", 
                "C. 数据库模块",
                "D. 执行模块"
            ],
            "correct_answer": "C",
            "explanation": "数据库模块不是核心组件，而是可选的辅助组件。",
            "difficulty": "medium",
            "points": 5
        }
    ]
}
```

**在线测试生成**:
```python
# 生成可交互的 HTML 测试
result = run(
    "https://example.com/article",
    notebooklm=True,
    quiz=True,
    export_format="html"
)

# 用浏览器打开即可进行测试
import webbrowser
webbrowser.open(result['quiz_html_path'])
```

### 11.5 故障排除

#### 问题 1: 认证失败

**错误信息**:
```
Error: Authentication failed
Please check your Google account credentials
```

**解决方案**:
```bash
# 1. 清除旧凭证
notebooklm logout
rm -rf ~/.notebooklm/credentials.json  # Linux/macOS
del C:\Users\<用户名>\.notebooklm\credentials.json  # Windows

# 2. 重新认证
notebooklm login

# 3. 检查网络连接
ping notebooklm.google.com

# 4. 如使用代理，确保配置正确
export HTTP_PROXY="http://127.0.0.1:10808"
export HTTPS_PROXY="http://127.0.0.1:10808"
```

#### 问题 2: 上传超时

**错误信息**:
```
Error: Upload timeout after 30 seconds
```

**解决方案**:
```python
# 增加超时时间
result = run(
    "https://example.com/long-article",
    notebooklm=True,
    timeout=120  # 增加到 120 秒
)

# 或分批上传
urls = [url1, url2, url3]
for url in urls:
    run(url, notebooklm=True)
```

#### 问题 3: 生成格式失败

**错误信息**:
```
Error: Failed to generate audio overview
```

**解决方案**:
```python
# 检查内容长度
# 过短的内容可能无法生成某些格式

# 查看日志
export DEEPREEDER_LOG_LEVEL="DEBUG"
run("https://example.com", notebooklm=True, audio=True)

# 尝试其他格式
run("https://example.com", notebooklm=True, flashcards=True)  # 通常更稳定
```

#### 问题 4: 笔记本数量超限

**错误信息**:
```
Error: Notebook limit reached (50 notebooks)
```

**解决方案**:
```bash
# 查看现有笔记本
notebooklm list

# 删除不需要的笔记本
notebooklm delete "旧笔记本名称"

# 或合并内容到新笔记本
```

---

## 十二、性能优化

### 12.1 批量处理优化

```python
from deepreader_skill import run
import asyncio
from concurrent.futures import ThreadPoolExecutor

# 方法 1: 使用线程池并发处理
def batch_process_urls(urls, max_workers=5):
    """批量处理 URL，限制并发数"""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(run, urls))
    return results

# 方法 2: 使用 asyncio 异步处理
async def batch_process_async(urls):
    """异步批量处理"""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        tasks = [loop.run_in_executor(executor, run, url) for url in urls]
        results = await asyncio.gather(*tasks)
    return results

# 使用示例
urls = ["https://example.com/1", "https://example.com/2", ...]  # 100 个 URL
results = batch_process_urls(urls, max_workers=5)  # 同时处理 5 个
```

### 12.2 内存优化

```python
# 处理大量 URL 时，定期清理缓存
import gc

def process_large_batch(urls, batch_size=20):
    """分批处理大量 URL，避免内存溢出"""
    all_results = []
    
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i + batch_size]
        print(f"处理批次 {i//batch_size + 1}/{(len(urls)-1)//batch_size + 1}")
        
        batch_results = [run(url) for url in batch]
        all_results.extend(batch_results)
        
        # 清理内存
        gc.collect()
    
    return all_results
```

### 12.3 缓存策略

```python
import hashlib
import json
from pathlib import Path

class DeepReaderCache:
    """简单的缓存实现"""
    
    def __init__(self, cache_dir="~/.deepreader/cache"):
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_key(self, url):
        """生成缓存键"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def get(self, url):
        """从缓存获取"""
        cache_key = self._get_cache_key(url)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            with open(cache_file) as f:
                return json.load(f)
        return None
    
    def set(self, url, result):
        """保存到缓存"""
        cache_key = self._get_cache_key(url)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        with open(cache_file, 'w') as f:
            json.dump(result, f)

# 使用缓存
cache = DeepReaderCache()

def run_with_cache(url):
    """带缓存的 run 函数"""
    # 尝试从缓存获取
    cached = cache.get(url)
    if cached:
        print(f"✓ 从缓存加载：{url}")
        return cached
    
    # 执行实际抓取
    result = run(url)
    
    # 保存到缓存
    cache.set(url, result)
    print(f"✓ 已抓取并缓存：{url}")
    
    return result
```

---

## 十三、安全与隐私

### 13.1 数据安全

⚠️ **重要提醒**:

1. **不要上传敏感信息**: 避免处理包含个人隐私、商业机密的 URL
2. **凭证保护**: `credentials.json` 文件不要上传到 Git
3. **定期清理**: 定期清理记忆库中的敏感内容

### 13.2 .gitignore 配置

```bash
# 添加到项目 .gitignore

# NotebookLM 凭证
.notebooklm/credentials.json

# DeepReader 缓存
.deepreader/cache/

# 记忆库（可选，根据需求）
memory/inbox/*.md
memory/inbox/*.mp3

# 环境变量
.env
```

### 13.3 访问控制

```python
# 限制可处理的域名
ALLOWED_DOMAINS = [
    "example.com",
    "x.com",
    "twitter.com",
    "reddit.com",
    "youtube.com"
]

from tldextract import extract

def is_allowed_domain(url):
    """检查域名是否在白名单中"""
    extracted = extract(url)
    domain = f"{extracted.domain}.{extracted.suffix}"
    return domain in ALLOWED_DOMAINS

# 使用
if is_allowed_domain(url):
    result = run(url)
else:
    print(f"⚠️ 域名 {url} 不在白名单中")
```

---

## 📝 更新日志

| 日期 | 版本 | 内容 |
|------|------|------|
| 2026-03-09 | 1.1.0 | 完善安装指南，添加代理配置说明、7 个实战案例、NotebookLM 详细教程 |
| 2026-03-06 | 1.0.0 | 添加 NotebookLM 集成（支持 9 种输出格式） |
| 2026-02-16 | 0.1.0 | 初始版本发布 |

---

## 📎 附录：快速参考卡片

### 基础快速参考

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

### NotebookLM 快速参考

```
┌─────────────────────────────────────────────────────────┐
│         NotebookLM 集成快速参考                          │
├─────────────────────────────────────────────────────────┤
│  认证：notebooklm login                                 │
│  状态：notebooklm status                                │
│  登出：notebooklm logout                                │
│                                                         │
│  播客：run(url, notebooklm=True, audio=True)            │
│  脑图：run(url, notebooklm=True, mindmap=True)          │
│  卡片：run(url, notebooklm=True, flashcards=True)       │
│  测验：run(url, notebooklm=True, quiz=True)             │
│                                                         │
│  输出：memory/inbox/*.mp3 / *.png / *.json              │
│                                                         │
│  凭证：~/.notebooklm/credentials.json                   │
└─────────────────────────────────────────────────────────┘
```

### 命令速查表

| 任务 | 命令 |
|------|------|
| **安装** | `npx clawhub@latest install deepreader` |
| **测试** | `run('https://www.baidu.com')` |
| **认证 NotebookLM** | `notebooklm login` |
| **生成播客** | `run(url, notebooklm=True, audio=True)` |
| **生成抽认卡** | `run(url, notebooklm=True, flashcards=True)` |
| **查看日志** | `export DEEPREEDER_LOG_LEVEL="DEBUG"` |
| **配置代理** | `export HTTP_PROXY="http://127.0.0.1:10808"` |
| **清理缓存** | `rm -rf ~/.deepreader/cache/*` |

---

> **提示**: 本指南基于实际安装和使用经验编写，如遇问题可参考 GitHub Issues 或联系社区。
> 
> **作者**: OpenClaw Community  
> **许可**: MIT License  
> **生成时间**: 2026-03-09 14:04 GMT+8
