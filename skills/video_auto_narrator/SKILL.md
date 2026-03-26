---
name: video_auto_narrator
description: 自动为本地视频生成营销式解说配音，实现音画对齐和字幕生成
homepage: https://github.com/openclaw/openclaw
metadata: { "openclaw": { "emoji": "🎙️", "requires": { "bins": ["ffmpeg", "ffprobe"], "python": true }, "env": [] } }
---

# Video Auto Narrator - 视频自动解说配音技能

自动为本地视频素材生成营销式解说配音，实现音画对齐和字幕生成。

**版本**: v1.0.0  
**作者**: ClawX  
**许可证**: MIT

## 适用场景

### ✅ 最佳适用
- 电商带货视频配音
- 产品展示视频解说
- 营销口播视频制作
- B 站/抖音/视频号内容创作

### ❌ 不适用
- 纪录片式客观解说
- 多对话视频
- 音乐 MV 类视频

## 安装依赖

### 系统依赖
```bash
# Windows (已安装)
ffmpeg -version
```

### Python 依赖
```bash
uv pip install edge-tts moviepy openai-whisper
```

## 使用方法

### 基础用法

```bash
cd C:\Users\Administrator\.openclaw\workspace\skills\video_auto_narrator
uv run python video_narrator.py ./input_videos ./output
```

### 命令行参数

```bash
uv run python video_narrator.py <input_folder> [output_dir] [options]

参数说明:
  <input_folder>   - 输入视频文件夹（必填）
  [output_dir]     - 输出目录（默认：./output）
  --style          - 解说风格：marketing(默认), documentary, tutorial
  --voice          - TTS 语音：zh-CN-XiaoxiaoNeural(默认), zh-CN-YunxiNeural 等
  --duration       - 目标视频时长（秒），默认自动匹配
  --subtitle       - 是否生成字幕：true(默认), false
```

### 示例

**营销式解说（默认）**：
```bash
uv run python video_narrator.py ./product_videos ./output --style marketing
```

**指定 TTS 语音**：
```bash
uv run python video_narrator.py ./videos ./output --voice zh-CN-YunxiNeural
```

**生成 60 秒视频**：
```bash
uv run python video_narrator.py ./videos ./output --duration 60
```

## 输出说明

### 输出文件

| 文件 | 说明 |
|------|------|
| `xxx_带解说.mp4` | 最终输出视频（含配音 + 字幕） |
| `xxx_解说文案.txt` | 生成的解说词文本 |
| `xxx_字幕.srt` | SRT 格式字幕文件 |
| `xxx_配音.mp3` | 单独配音音频 |
| `处理报告.md` | 详细处理报告 |

### 输出示例

```
output/
├── product_demo_带解说.mp4      # 最终视频
├── product_demo_解说文案.txt    # 解说词
├── product_demo_字幕.srt        # 字幕文件
├── product_demo_配音.mp3        # 配音音频
└── 处理报告.md                 # 处理报告
```

## 核心功能

### 1. 视频内容理解

使用多模态 AI 分析视频内容：
- 场景识别（室内/室外/产品特写等）
- 物体检测（产品、人物、道具）
- 动作识别（演示、使用、对比）
- 画面情感分析（积极/消极/中性）

### 2. 营销式文案生成

基于视频内容生成带货口播文案：
- **开头钩子**（3 秒吸引注意力）
- **痛点挖掘**（引发共鸣）
- **产品介绍**（核心卖点）
- **使用场景**（代入感）
- **价格锚点**（价值对比）
- **行动号召**（立即购买）

文案模板示例：
```
【开头】家人们！今天必须给你们安利这个神器！
【痛点】是不是经常遇到 XXX 问题？
【产品】看看这个 XXX，简直太好用！
【卖点】第一...第二...第三...
【场景】你想想，每天早上...
【价格】外面卖 XXX，今天只要...
【行动】链接在评论区，赶紧冲！
```

### 3. Edge TTS 语音合成

支持多种中文语音：
- `zh-CN-XiaoxiaoNeural` - 温柔女声（默认）
- `zh-CN-YunxiNeural` - 磁性男声
- `zh-CN-YunjianNeural` - 激情男声
- `zh-CN-XiaoyiNeural` - 活泼女声
- `zh-CN-YunyangNeural` - 新闻男声

语速调节：
- 正常：`--rate 0%`
- 快速：`--rate 20%`
- 慢速：`--rate -20%`

### 4. 音画对齐

智能对齐技术：
1. **Whisper 时间戳** - 精确到词级的音频时间戳
2. **画面节奏分析** - 检测场景切换点
3. **智能匹配** - 解说词与对应画面对齐
4. **自动调整** - 调整视频节奏或解说语速

### 5. 自动字幕生成

字幕样式可配置：
- 字体：思源黑体/微软雅黑
- 大小：可调节
- 颜色：白色 + 黑边（默认）
- 位置：底部居中（默认）

## 配置参数

在脚本顶部的 `CONFIG` 字典中：

```python
CONFIG = {
    # TTS 配置
    "default_voice": "zh-CN-XiaoxiaoNeural",
    "default_rate": "0%",
    "default_volume": "+0%",
    
    # 文案配置
    "style": "marketing",  # marketing, documentary, tutorial
    "max_script_length": 500,  # 最大字数
    
    # 视频配置
    "target_duration": None,  # 目标时长（秒），None=自动
    "video_codec": "libx264",
    "video_bitrate": "5000k",
    "audio_bitrate": "192k",
    
    # 字幕配置
    "subtitle_font": "Microsoft-YaHei",
    "subtitle_size": 36,
    "subtitle_color": "white",
    "subtitle_outline": "black",
    
    # 对齐配置
    "alignment_tolerance": 0.5,  # 对齐容差（秒）
    "auto_adjust_speed": True,   # 自动调整语速
}
```

## 处理流程

```
输入视频文件夹
    ↓
1. 视频内容分析（多模态 AI）
    ↓
2. 生成营销式解说文案
    ↓
3. Edge TTS 语音合成
    ↓
4. Whisper 生成时间戳
    ↓
5. 音画对齐分析
    ↓
6. 调整视频节奏/解说语速
    ↓
7. 合成视频 + 配音
    ↓
8. 生成并嵌入字幕
    ↓
输出：带解说的完整视频
```

## 常见问题

### Q: TTS 语音听起来不自然？
**A**: 尝试更换语音：
```bash
uv run python video_narrator.py ./videos ./output --voice zh-CN-YunxiNeural
```

### Q: 解说词与画面对不齐？
**A**: 检查视频是否有清晰的场景切换。如果画面变化太快，可以尝试：
- 增加 `--duration` 参数延长视频
- 使用 `video_auto_cut` 技能先进行粗剪

### Q: 字幕显示不正常？
**A**: 确保系统安装了中文字体。可以修改配置中的 `subtitle_font`。

### Q: 支持哪些视频格式？
**A**: 支持常见格式：`.mp4`, `.mov`, `.avi`, `.mkv`, `.MTS`

### Q: 可以批量处理吗？
**A**: 可以！将多个视频放入同一文件夹，技能会自动批量处理。

## 与其他技能配合

### 配合 video_auto_cut 使用

先用 `video_auto_cut` 进行粗剪，再用本技能添加配音：

```bash
# 步骤 1：粗剪
uv run python video_editor_auto_v4.6.py ./raw_videos ./trimmed

# 步骤 2：添加配音
uv run python video_narrator.py ./trimmed ./output
```

### 配合爆款复刻技能使用

任务 1 的爆款复刻技能生成素材后，用本技能添加配音。

## 技术架构

### 核心模块

| 模块 | 功能 | 技术栈 |
|------|------|--------|
| 内容理解 | 视频场景分析 | 多模态 AI |
| 文案生成 | 营销式解说词 | LLM |
| TTS 合成 | 语音生成 | Edge TTS |
| 时间戳 | 音频对齐 | Whisper |
| 音画对齐 | 节奏匹配 | 自定义算法 |
| 视频合成 | 最终输出 | ffmpeg + moviepy |
| 字幕生成 | SRT+ 嵌入 | ffmpeg |

## 许可证

MIT License

## 相关链接

- **Edge TTS 文档**: https://github.com/rany2/edge-tts
- **MoviePy 文档**: https://zulko.github.io/moviepy/
- **Whisper 文档**: https://github.com/openai/whisper
