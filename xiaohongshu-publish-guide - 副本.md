# 小红书图文笔记发布指南

使用 `xiaohongshu-skills` 技能在 ClawX 中自动化发布小红书图文笔记的完整流程。

---

## 📋 前置条件

### 1. 环境要求

| 项目 | 要求 |
|------|------|
| Python | ≥ 3.11 |
| uv | 已安装（ClawX 自带） |
| Google Chrome | 已安装 |
| 小红书账号 | 已注册 |

### 2. 技能位置

```
C:\Users\Administrator\.openclaw\workspace\skills\xiaohongshu-skills
```

---

## 📦 技能安装

### 方法一：Git Clone（推荐）

```bash
# 1. 进入 ClawX 技能目录
cd C:\Users\Administrator\.openclaw\workspace\skills

# 2. 克隆技能仓库
git clone https://github.com/autoclaw-cc/xiaohongshu-skills.git

# 3. 进入技能目录
cd xiaohongshu-skills

# 4. 安装 Python 依赖
uv sync
```

### 方法二：下载 ZIP 安装

1. 访问 https://github.com/autoclaw-cc/xiaohongshu-skills
2. 点击 **Code → Download ZIP** 下载
3. 解压到 `C:\Users\Administrator\.openclaw\workspace\skills\xiaohongshu-skills`
4. 打开终端，进入技能目录
5. 运行 `uv sync` 安装依赖

### 验证安装

```bash
cd "C:\Users\Administrator\.openclaw\workspace\skills\xiaohongshu-skills"
uv run python scripts/cli.py --help
```

成功输出命令帮助信息即表示安装完成。

### 安装后的目录结构

```
xiaohongshu-skills/
├── scripts/                        # Python 自动化引擎
│   ├── xhs/                        # 核心自动化包
│   ├── cli.py                      # CLI 入口
│   └── chrome_launcher.py          # Chrome 启动器
├── skills/                         # 子技能定义
│   ├── xhs-auth/
│   ├── xhs-publish/
│   ├── xhs-explore/
│   ├── xhs-interact/
│   └── xhs-content-ops/
├── SKILL.md                        # 技能主入口
├── README.md                       # 项目说明
├── pyproject.toml                  # Python 依赖配置
└── uv.lock                         # 依赖锁定文件
```

---

## 🚀 完整发布流程

### 步骤 1：启动 Chrome 浏览器

```bash
cd "C:\Users\Administrator\.openclaw\workspace\skills\xiaohongshu-skills"
uv run python scripts/chrome_launcher.py
```

**说明：**
- 启动带调试端口的 Chrome（默认端口 9222）
- 保持 Chrome 窗口打开，不要关闭

---

### 步骤 2：登录小红书

```bash
uv run python scripts/cli.py check-login
```
或者让OpenClaw自动发布小红书文章。
**如果未登录，会返回二维码：**
```json
{
  "logged_in": false,
  "qrcode_path": "C:\\Users\\Administrator\\AppData\\Local\\Temp\\xhs\\login_qrcode.png",
  "login_method": "qrcode"
}
```

**扫码登录：**
1. 打开小红书 APP
2. 扫描生成的二维码
3. 在手机上确认登录
4. 再次运行 `check-login` 确认登录成功

**登录成功返回：**
```json
{
  "logged_in": true
}
```

---

### 步骤 3：准备发布内容

#### 3.1 创建内容目录

```bash
mkdir C:\Users\Administrator\.openclaw\workspace\xhs-images\ez60-10reasons
```

#### 3.2 准备标题文件

创建 `title.txt`：
```
选择 EZ-60 的十大理由
```

#### 3.3 准备正文文件

创建 `content.txt`：
```
选择 EZ-60 的十大理由

1. 颜值出众，设计时尚
2. 智能科技，便捷驾驶
3. 空间宽敞，舒适乘坐
4. 动力强劲，操控流畅
5. 安全可靠，全方位保护
6. 节能环保，经济实用
7. 配置丰富，性价比高
8. 品牌信赖，品质保证
9. 售后完善，服务周到
10. 口碑优秀，用户好评

#EZ60 #汽车推荐 #购车指南 #智能汽车 #高颜值汽车
```

**注意：** 标签放在正文末尾，用 `#` 开头，会自动识别为话题标签。

#### 3.4 准备图片

将图片放在同一目录下：
```
C:\Users\Administrator\.openclaw\workspace\xhs-images\ez60-10reasons\
├── reason-01.png
├── reason-02.png
├── reason-03.png
├── reason-04.png
└── reason-05.png
```

**图片要求：**
- 格式：png、jpg、jpeg、webp（不支持 gif）
- 大小：单张 ≤ 32MB
- 分辨率：推荐 720*960 以上，1280P 更佳
- 比例：3:4 至 2:1 之间最佳

---

### 步骤 4：填写并发布笔记

#### 4.1 执行发布命令

```bash
uv run python scripts/cli.py fill-publish \
  --title-file "C:\Users\Administrator\.openclaw\workspace\xhs-images\ez60-10reasons\title.txt" \
  --content-file "C:\Users\Administrator\.openclaw\workspace\xhs-images\ez60-10reasons\content.txt" \
  --images \
    "C:\Users\Administrator\.openclaw\workspace\xhs-images\ez60-10reasons\reason-01.png" \
    "C:\Users\Administrator\.openclaw\workspace\xhs-images\ez60-10reasons\reason-02.png" \
    "C:\Users\Administrator\.openclaw\workspace\xhs-images\ez60-10reasons\reason-03.png" \
    "C:\Users\Administrator\.openclaw\workspace\xhs-images\ez60-10reasons\reason-04.png" \
    "C:\Users\Administrator\.openclaw\workspace\xhs-images\ez60-10reasons\reason-05.png"
```

**命令参数说明：**
| 参数 | 说明 |
|------|------|
| `--title-file` | 标题文件路径（绝对路径） |
| `--content-file` | 正文文件路径（绝对路径） |
| `--images` | 图片路径，可传多张（1-9 张） |

#### 4.2 等待处理完成

CLI 会自动执行：
1. ✅ 上传图片（逐张）
2. ✅ 填写标题
3. ✅ 填写正文
4. ✅ 识别并添加标签
5. ✅ 设置可见范围（公开）

**成功返回：**
```json
{
  "success": true,
  "title": "选择 EZ-60 的十大理由",
  "images": 5,
  "status": "表单已填写，等待确认发布"
}
```

#### 4.3 确认发布

```bash
uv run python scripts/cli.py click-publish
```

**成功返回：**
```json
{
  "success": true,
  "status": "发布完成"
}
```

---

## 📱 发布后检查

### 1. 查看笔记状态

**方法一：小红书 APP**
- 打开小红书 APP → "我" → "笔记"
- 新笔记会显示在列表中

**方法二：网页端**
- 访问 https://creator.xiaohongshu.com/note/manage
- 查看笔记管理页面

### 2. 审核时间

- ⏳ 通常需要 **5-30 分钟** 审核
- 审核通过后才会公开显示
- APP 上可能比网页端先显示

### 3. 搜索测试

审核通过后可以搜索：
- 搜索笔记标题
- 搜索你的用户名
- 搜索笔记中的标签

---

## 🔧 常用命令参考

| 命令 | 说明 |
|------|------|
| `cli.py check-login` | 检查登录状态 |
| `cli.py login` | 二维码登录 |
| `cli.py delete-cookies` | 清除登录状态（切换账号） |
| `cli.py fill-publish` | 填写图文发布表单 |
| `cli.py click-publish` | 确认发布 |
| `cli.py save-draft` | 保存为草稿 |
| `cli.py publish` | 一步发布（自动填写 + 发布） |
| `cli.py publish-video` | 发布视频笔记 |
| `cli.py long-article` | 发布长文 |
| `cli.py search-feeds` | 搜索笔记 |
| `cli.py like-feed` | 点赞笔记 |
| `cli.py favorite-feed` | 收藏笔记 |
| `cli.py post-comment` | 发表评论 |

---

## ⚠️ 注意事项

### 1. 登录状态
- 每次发布前确认登录状态
- Cookies 存储在 `C:\Users\Administrator\.xhs\chrome-profile`
- 多账号切换使用 `delete-cookies` 后重新登录

### 2. 内容规范
- 标题 ≤ 20 字（建议）
- 正文 ≤ 1000 字
- 图片 1-9 张
- 避免敏感词、广告引流

### 3. 发布频率
- 建议间隔 ≥ 30 分钟
- 避免短时间内大量发布
- 保持合理运营节奏

### 4. 图片处理
- 使用绝对路径
- 确保图片文件存在
- 推荐 PNG 格式（无损）

### 5. 审核失败处理
- 检查内容是否违规
- 修改后重新发布
- 避免重复相同内容

### 6. 谨慎使用
- 使用小红书自动化发布流程，极易触发封号风险；
- 仅作为学习交流，真实场景慎用。
---

## 📁 目录结构示例

### 技能目录

```
C:\Users\Administrator\.openclaw\workspace\skills\xiaohongshu-skills\
├── scripts/                        # Python 自动化引擎
│   ├── xhs/                        # 核心自动化包
│   ├── cli.py                      # CLI 入口
│   └── chrome_launcher.py          # Chrome 启动器
├── skills/                         # 子技能定义
├── SKILL.md                        # 技能主入口
├── README.md                       # 项目说明
├── pyproject.toml                  # 依赖配置
└── .venv/                          # Python 虚拟环境（安装后生成）
```

### 内容目录（用户自定义）

```
C:\Users\Administrator\.openclaw\workspace\
├── xhs-images/
│   └── ez60-10reasons/
│       ├── title.txt          # 标题
│       ├── content.txt        # 正文 + 标签
│       ├── reason-01.png      # 图片 1
│       ├── reason-02.png      # 图片 2
│       ├── reason-03.png      # 图片 3
│       ├── reason-04.png      # 图片 4
│       └── reason-05.png      # 图片 5
└── tmp_uploads/               # 临时上传目录（可选）
    └── ...
```

---

## 🎯 快速发布模板

创建批处理脚本 `publish-xhs.bat`：

```batch
@echo off
set XHS_SKILLS=C:\Users\Administrator\.openclaw\workspace\skills\xiaohongshu-skills
set CONTENT_DIR=C:\Users\Administrator\.openclaw\workspace\xhs-images\ez60-10reasons

cd /d %XHS_SKILLS%

echo 检查登录状态...
uv run python scripts/cli.py check-login

echo 发布笔记...
uv run python scripts/cli.py fill-publish ^
  --title-file "%CONTENT_DIR%\title.txt" ^
  --content-file "%CONTENT_DIR%\content.txt" ^
  --images "%CONTENT_DIR%\reason-01.png" "%CONTENT_DIR%\reason-02.png" "%CONTENT_DIR%\reason-03.png" "%CONTENT_DIR%\reason-04.png" "%CONTENT_DIR%\reason-05.png"

echo 确认发布...
uv run python scripts/cli.py click-publish

echo 发布完成！
pause
```

---

## 📞 故障排查

### 问题 1：Chrome 未启动
**解决：** 先运行 `chrome_launcher.py`

### 问题 2：登录失效
**解决：** 运行 `delete-cookies` 后重新扫码登录

### 问题 3：图片上传失败
**解决：** 
- 检查文件路径是否正确
- 确认图片格式和大小符合要求
- 检查网络连接

### 问题 4：发布后看不到笔记
**解决：**
- 等待审核完成（5-30 分钟）
- 在 APP 上查看
- 检查是否违规被驳回

### 问题 5：标签未生效
**解决：**
- 确保标签在正文末尾
- 使用 `#标签` 格式
- 避免使用敏感话题

---

## 📚 相关文档

- 技能源码：https://github.com/autoclaw-cc/xiaohongshu-skills
- 技能位置：`C:\Users\Administrator\.openclaw\workspace\skills\xiaohongshu-skills`
- 小红书创作平台：https://creator.xiaohongshu.com

---


