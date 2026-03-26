# baoyu-skills 完整使用手册

> 宝玉分享的 Claude Code 效率技能包，共 17 个技能，帮你自动生成图片、发布信息、处理内容。
> 
> 项目地址：https://github.com/jimliu/baoyu-skills  
> 最后更新：2026-03-09

---

## 📦 一、安装方法

### 方法 1：一键安装全部技能（推荐新手）
```bash
npx skills add jimliu/baoyu-skills
```

### 方法 2：注册为插件市场
```bash
/plugin marketplace add jimliu/baoyu-skills
```
然后通过界面浏览选择要安装的技能。

### 方法 3：直接告诉 Claude
```
请帮我安装 github.com/JimLiu/baoyu-skills 里的技能
```

---

## 🗂️ 二、技能包结构

baoyu-skills 的技能是**分层打包**的：

```
baoyu-skills (总仓库)
├── content-skills (内容生成包) ← 9 个技能
│   ├── baoyu-xhs-images        # 小红书配图
│   ├── baoyu-infographic       # 信息图
│   ├── baoyu-cover-image       # 文章封面
│   ├── baoyu-slide-deck        # PPT 幻灯片
│   ├── baoyu-comic             # 漫画
│   ├── baoyu-article-illustrator # 文章插图
│   ├── baoyu-post-to-x         # 发布到 X
│   ├── baoyu-post-to-wechat    # 发布到微信
│   ├── baoyu-post-to-weibo     # 发布到微博
│   ├── baoyu-infographic        # 信息图生成
│
├── ai-generation-skills (AI 生成包) ← 2 个技能
│   ├── baoyu-image-gen         # 图片生成后端
│   └── baoyu-danger-gemini-web # Gemini 网页版
│
└── utility-skills (工具包) ← 6 个技能
    ├── baoyu-url-to-markdown   # 网页转 Markdown
    ├── baoyu-danger-x-to-markdown # X 转 Markdown
    ├── baoyu-compress-image    # 图片压缩
    ├── baoyu-format-markdown   # Markdown 格式化
    ├── baoyu-markdown-to-html  # Markdown 转 HTML
    └── baoyu-translate         # 翻译
```

---

## 🔧 三、安装命令速查

### 安装整个技能包
```bash
# 内容生成包（9 个技能）
/plugin install content-skills@baoyu-skills

# AI 生成包（2 个技能）
/plugin install ai-generation-skills@baoyu-skills

# 工具包（6 个技能）
/plugin install utility-skills@baoyu-skills
```

### 安装单个技能
```bash
# 只装小红书技能
/plugin install baoyu-xhs-images@baoyu-skills

# 只装信息图技能
/plugin install baoyu-infographic@baoyu-skills

# 只装封面技能
/plugin install baoyu-cover-image@baoyu-skills
```

### ⚠️ 命令格式注意
```bash
# ❌ 错误：少了 install 关键字
/plugin baoyu-xhs-images@baoyu-skills

# ✅ 正确
/plugin install baoyu-xhs-images@baoyu-skills
```

---

## 📱 四、技能详细用法

### 1️⃣ baoyu-xhs-images — 小红书配图生成器

**功能：** 把文章自动变成 1-10 张卡通风格的小红书图文

**基本用法：**
```bash
# 最简单：直接给文章
/baoyu-xhs-images posts/article.md

# 直接输入文字内容
/baoyu-xhs-images 今日星座运势
```

**风格选项（9 种）：**
```bash
/baoyu-xhs-images article.md --style cute       # 可爱风（默认）
/baoyu-xhs-images article.md --style fresh      # 清新风
/baoyu-xhs-images article.md --style warm       # 温暖风
/baoyu-xhs-images article.md --style bold       # 大胆风
/baoyu-xhs-images article.md --style minimal    # 极简风
/baoyu-xhs-images article.md --style retro      # 复古风
/baoyu-xhs-images article.md --style pop        # 流行风
/baoyu-xhs-images article.md --style notion     # Notion 风
/baoyu-xhs-images article.md --style chalkboard # 黑板风
```

**排版选项（6 种）：**
```bash
/baoyu-xhs-images article.md --layout sparse      # 稀疏（1-2 个点，适合封面）
/baoyu-xhs-images article.md --layout balanced    # 平衡（3-4 个点，常规内容）
/baoyu-xhs-images article.md --layout dense       # 密集（5-8 个点，知识卡片）
/baoyu-xhs-images article.md --layout list        # 列表（4-7 项，清单排名）
/baoyu-xhs-images article.md --layout comparison  # 对比（正反对比）
/baoyu-xhs-images article.md --layout flow        # 流程（3-6 步，时间线）
```

**组合使用：**
```bash
/baoyu-xhs-images article.md --style tech --layout list
```

---

### 2️⃣ baoyu-infographic — 信息图生成器

**功能：** 把复杂内容变成一张专业的信息图

**基本用法：**
```bash
# 自动推荐最佳组合
/baoyu-infographic content.md
```

**布局选项（20 种）：**
```bash
/baoyu-infographic content.md --layout pyramid            # 金字塔（层级结构）
/baoyu-infographic content.md --layout funnel             # 漏斗（转化流程）
/baoyu-infographic content.md --layout timeline-horizontal # 时间线
/baoyu-infographic content.md --layout mind-map           # 思维导图
/baoyu-infographic content.md --layout comparison-table   # 对比表格
/baoyu-infographic content.md --layout venn               # 维恩图
/baoyu-infographic content.md --layout fishbone           # 鱼骨图（因果分析）
/baoyu-infographic content.md --layout bridge             # 桥梁（问题 - 方案）
/baoyu-infographic content.md --layout circular-flow      # 循环流程
/baoyu-infographic content.md --layout do-dont            # 对错对比
/baoyu-infographic content.md --layout equation           # 公式拆解
/baoyu-infographic content.md --layout feature-list       # 特性列表
/baoyu-infographic content.md --layout grid-cards         # 网格卡片
/baoyu-infographic content.md --layout iceberg            # 冰山图
/baoyu-infographic content.md --layout journey-path       # 旅程路径
/baoyu-infographic content.md --layout layers-stack       # 层级堆叠
/baoyu-infographic content.md --layout nested-circles     # 嵌套圆圈
/baoyu-infographic content.md --layout priority-quadrants # 优先四象限
/baoyu-infographic content.md --layout scale-balance      # 天平对比
/baoyu-infographic content.md --layout tree-hierarchy     # 树状层级
```

**风格选项（17 种）：**
```bash
/baoyu-infographic content.md --style craft-handmade      # 手绘风（默认）
/baoyu-infographic content.md --style claymation          # 粘土动画
/baoyu-infographic content.md --style kawaii              # 日式可爱
/baoyu-infographic content.md --style storybook-watercolor # 童话水彩
/baoyu-infographic content.md --style chalkboard          # 黑板风
/baoyu-infographic content.md --style cyberpunk-neon      # 赛博朋克
/baoyu-infographic content.md --style bold-graphic        # 大胆图形
/baoyu-infographic content.md --style aged-academia       # 复古学术
/baoyu-infographic content.md --style corporate-memphis   # 商务扁平
/baoyu-infographic content.md --style technical-schematic # 技术蓝图
/baoyu-infographic content.md --style origami             # 折纸风
/baoyu-infographic content.md --style pixel-art           # 像素风
/baoyu-infographic content.md --style ui-wireframe        # 线框图
/baoyu-infographic content.md --style subway-map          # 地铁图
/baoyu-infographic content.md --style ikea-manual         # 宜家说明书
/baoyu-infographic content.md --style knolling            # 平铺整理
/baoyu-infographic content.md --style lego-brick          # 乐高积木
```

**其他选项：**
```bash
# 指定比例
/baoyu-infographic content.md --aspect landscape  # 16:9 横版
/baoyu-infographic content.md --aspect portrait   # 9:16 竖版
/baoyu-infographic content.md --aspect square     # 1:1 方版

# 指定语言
/baoyu-infographic content.md --lang zh  # 中文
/baoyu-infographic content.md --lang en  # 英文
```

---

### 3️⃣ baoyu-cover-image — 文章封面生成器

**功能：** 给文章自动生成封面图，5 个维度自由组合

**基本用法：**
```bash
# 全自动
/baoyu-cover-image article.md

# 快速模式（不确认直接用）
/baoyu-cover-image article.md --quick
```

**5 个维度选项：**

| 维度 | 选项 |
|------|------|
| **Type** (类型) | `hero`, `conceptual`, `typography`, `metaphor`, `scene`, `minimal` |
| **Palette** (配色) | `warm`, `elegant`, `cool`, `dark`, `earth`, `vivid`, `pastel`, `mono`, `retro` |
| **Rendering** (渲染) | `flat-vector`, `hand-drawn`, `painterly`, `digital`, `pixel`, `chalk` |
| **Text** (文字) | `none`, `title-only`, `title-subtitle`, `text-rich` |
| **Mood** (氛围) | `subtle`, `balanced`, `bold` |

**示例：**
```bash
# 组合使用
/baoyu-cover-image article.md --type conceptual --palette cool --rendering digital --mood bold

# 风格预设（快捷方式）
/baoyu-cover-image article.md --style blueprint

# 指定比例
/baoyu-cover-image article.md --aspect 2.35:1  # 电影宽屏

# 只要图不要字
/baoyu-cover-image article.md --no-title
```

---

### 4️⃣ baoyu-slide-deck — PPT 幻灯片生成器

**功能：** 把文章/演讲稿变成一套专业的幻灯片图片

**用法：**
```bash
# 基本用法
/baoyu-slide-deck presentation.md

# 指定幻灯片数量
/baoyu-slide-deck presentation.md --slides 15

# 指定风格
/baoyu-slide-deck presentation.md --style business    # 商务风
/baoyu-slide-deck presentation.md --style chalkboard  # 黑板风
/baoyu-slide-deck presentation.md --style minimal     # 极简风
```

---

### 5️⃣ baoyu-comic — 漫画生成器

**功能：** 把故事或内容变成多格漫画

**用法：**
```bash
# 基本用法
/baoyu-comic story.md

# 指定格数
/baoyu-comic story.md --panels 4  # 4 格漫画

# 指定风格
/baoyu-comic story.md --style japanese  # 日漫风
/baoyu-comic story.md --style western   # 美漫风
```

---

### 6️⃣ baoyu-article-illustrator — 文章插图生成器

**功能：** 给文章自动配插图

**用法：**
```bash
/baoyu-article-illustrator article.md

# 指定插图数量
/baoyu-article-illustrator article.md --count 5
```

---

### 7️⃣ baoyu-post-to-x — 发布到 X(推特)

**功能：** 一键把内容发布到 X 平台

**用法：**
```bash
/baoyu-post-to-x content.md
```
⚠️ 需要配置 X/Twitter API 密钥

---

### 8️⃣ baoyu-post-to-wechat — 发布到微信公众号

**功能：** 一键发布到微信公众号

**用法：**
```bash
/baoyu-post-to-wechat article.md
```
⚠️ 需要配置微信公众号 API

---

### 9️⃣ baoyu-post-to-weibo — 发布到微博

**功能：** 一键发布到微博

**用法：**
```bash
/baoyu-post-to-weibo content.md
```
⚠️ 需要配置微博 API

---

### 🔟 baoyu-image-gen — 图片生成后端

**功能：** 调用各种 AI 绘图 API 来生成图片

**用法：**
```bash
/baoyu-image-gen "一只可爱的猫咪"

# 指定服务商
/baoyu-image-gen "风景画" --provider google      # Google ImageFX
/baoyu-image-gen "人物肖像" --provider stability # Stability AI
```
⚠️ 需要配置相应 API Key

---

### 1️⃣1️⃣ baoyu-danger-gemini-web — Gemini 网页版接口

**功能：** 使用谷歌 Gemini 的网页版进行生成

**用法：**
```bash
/baoyu-danger-gemini-web "帮我写一首诗"
```
⚠️ **注意：** 带 "danger" 表示可能不稳定（网页版接口容易变）

---

### 1️⃣2️⃣ baoyu-url-to-markdown — 网页转 Markdown

**功能：** 把任意网页内容抓取并转成 Markdown 格式

**用法：**
```bash
# 转换网页
/baoyu-url-to-markdown https://example.com/article

# 保存到文件
/baoyu-url-to-markdown https://example.com/article --output saved.md
```

---

### 1️⃣3️⃣ baoyu-danger-x-to-markdown — X(推特) 转 Markdown

**功能：** 把 X 平台的帖子转成 Markdown

**用法：**
```bash
/baoyu-danger-x-to-markdown https://x.com/username/status/123456
```
⚠️ **注意：** 带 "danger" 表示可能不稳定

---

### 1️⃣4️⃣ baoyu-compress-image — 图片压缩

**功能：** 压缩图片大小，节省空间

**用法：**
```bash
# 压缩单张图片
/baoyu-compress-image photo.jpg

# 指定质量
/baoyu-compress-image photo.jpg --quality 80

# 批量压缩
/baoyu-compress-image *.jpg
```

---

### 1️⃣5️⃣ baoyu-format-markdown — Markdown 格式化

**功能：** 自动整理 Markdown 文档格式

**用法：**
```bash
# 格式化文件
/baoyu-format-markdown document.md

# 原地修改
/baoyu-format-markdown document.md --inplace
```

---

### 1️⃣6️⃣ baoyu-markdown-to-html — Markdown 转 HTML

**功能：** 把 Markdown 文档转成网页

**用法：**
```bash
# 转换文件
/baoyu-markdown-to-html article.md

# 指定输出
/baoyu-markdown-to-html article.md --output article.html

# 添加样式
/baoyu-markdown-to-html article.md --style github
```

---

### 1️⃣7️⃣ baoyu-translate — 翻译

**功能：** 多语言翻译工具

**用法：**
```bash
# 翻译文本
/baoyu-translate "Hello World" --to zh

# 翻译文件
/baoyu-translate document.md --to en --output translated.md

# 指定语言对
/baoyu-translate text.txt --from zh --to ja  # 中译日
```

---

## 🔄 五、更新技能

### 手动更新
```bash
/plugin  # 在 Claude Code 里运行
# 切换到 Marketplaces 标签
# 选择 baoyu-skills
# 选择 Update marketplace
```

### 开启自动更新
在 Marketplaces 里选择 **Enable auto-update**

---

## ⚠️ 六、注意事项

1. **环境要求：** 需要 Node.js 环境，能运行 `npx bun` 命令
2. **带 "danger" 的技能** 可能不稳定，慎用
3. **发布类技能** 需要配置相应平台的 API Key
4. **图片生成类技能** 需要配置绘图 API Key

---

## 🎯 七、新手推荐方案

### 方案 A：只做小红书
```bash
/plugin install baoyu-xhs-images@baoyu-skills
```

### 方案 B：内容创作全套
```bash
/plugin install content-skills@baoyu-skills
```
包含：小红书、信息图、封面、PPT、漫画、插图、发布（9 个技能）

### 方案 C：全部技能
```bash
npx skills add jimliu/baoyu-skills
```
17 个技能全部安装

### 方案 D：只要工具类
```bash
/plugin install utility-skills@baoyu-skills
```
包含：网页转换、图片压缩、Markdown 处理、翻译（6 个技能）

---

## 📋 八、快速参考表

| 需求 | 安装命令 |
|------|---------|
| 只做小红书 | `/plugin install baoyu-xhs-images@baoyu-skills` |
| 内容创作全套 | `/plugin install content-skills@baoyu-skills` |
| 全部 17 个技能 | `npx skills add jimliu/baoyu-skills` |
| 只要工具类 | `/plugin install utility-skills@baoyu-skills` |
| AI 绘图后端 | `/plugin install ai-generation-skills@baoyu-skills` |

---

## 🔗 九、相关链接

- 项目仓库：https://github.com/jimliu/baoyu-skills
- 中文文档：https://github.com/jimliu/baoyu-skills/blob/main/README.zh.md
- 更新日志：https://github.com/jimliu/baoyu-skills/blob/main/CHANGELOG.zh.md

---

*文档生成时间：2026-03-09*
