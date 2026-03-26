# Video Auto Narrator - 视频自动解说配音技能

## 快速开始

### 1. 准备视频素材

将需要添加解说的视频放入一个文件夹，例如：
```
C:\Users\Administrator\.openclaw\workspace\videos\product_demos\
├── video1.mp4
├── video2.mp4
└── video3.mp4
```

### 2. 运行技能

```bash
cd C:\Users\Administrator\.openclaw\workspace\skills\video_auto_narrator
uv run python video_narrator.py ../../videos/product_demos ../../output
```

### 3. 查看输出

```
../../output/
├── video1_带解说.mp4      # 最终视频
├── video1_解说文案.txt    # 解说词
├── video1_字幕.srt        # 字幕文件
├── video1_配音.mp3        # 配音音频
└── video1_处理报告.md     # 处理报告
```

## 功能特性

✅ **自动内容理解** - 分析视频场景和内容  
✅ **营销式文案生成** - 带货口播风格  
✅ **Edge TTS 配音** - 多种语音可选  
✅ **音画自动对齐** - 智能匹配节奏  
✅ **字幕生成** - 自动嵌入字幕  
✅ **批量处理** - 支持文件夹批量处理  

## 常用命令

### 基础用法
```bash
uv run python video_narrator.py ./videos ./output
```

### 指定 TTS 语音
```bash
# 磁性男声
uv run python video_narrator.py ./videos ./output --voice zh-CN-YunxiNeural

# 激情男声
uv run python video_narrator.py ./videos ./output --voice zh-CN-YunjianNeural

# 活泼女声
uv run python video_narrator.py ./videos ./output --voice zh-CN-XiaoyiNeural
```

### 调整语速
```bash
# 加快 20%
uv run python video_narrator.py ./videos ./output --rate +20%

# 放慢 10%
uv run python video_narrator.py ./videos ./output --rate -10%
```

### 更换解说风格
```bash
# 营销式（默认）
uv run python video_narrator.py ./videos ./output --style marketing

# 教程式
uv run python video_narrator.py ./videos ./output --style tutorial

# 纪录片式
uv run python video_narrator.py ./videos ./output --style documentary
```

## TTS 语音列表

### 女声
- `zh-CN-XiaoxiaoNeural` - 温柔女声（推荐）
- `zh-CN-XiaoyiNeural` - 活泼女声
- `zh-CN-XiaochenNeural` - 知性女声

### 男声
- `zh-CN-YunxiNeural` - 磁性男声（推荐）
- `zh-CN-YunjianNeural` - 激情男声
- `zh-CN-YunyangNeural` - 新闻男声

## 配置说明

编辑 `video_narrator.py` 顶部的 `CONFIG` 字典：

```python
CONFIG = {
    "default_voice": "zh-CN-XiaoxiaoNeural",  # 默认语音
    "default_rate": "0%",                      # 默认语速
    "style": "marketing",                      # 默认风格
    "subtitle_size": 36,                       # 字幕大小
    # ... 更多配置
}
```

## 与其他技能配合

### 配合 video_auto_cut
```bash
# 1. 先粗剪
uv run python video_editor_auto_v4.6.py ./raw_videos ./trimmed

# 2. 再加配音
uv run python video_narrator.py ./trimmed ./output
```

## 常见问题

### Q: 没有声音？
A: 检查是否正确安装 edge-tts：
```bash
uv pip install edge-tts
```

### Q: 字幕显示乱码？
A: 修改配置中的字体为系统已有的中文字体：
```python
"subtitle_font": "Microsoft-YaHei"
```

### Q: 视频处理失败？
A: 确保安装了 FFmpeg 并添加到系统 PATH。

## 技术栈

- **Edge TTS** - 微软免费 TTS 服务
- **MoviePy** - Python 视频编辑库
- **FFmpeg** - 音视频处理工具
- **Whisper** - 语音识别（可选，用于精确时间戳）

## 许可证

MIT License

## 版本历史

- v1.0.0 (2026-03-23) - 初始版本
  - 营销式文案生成
  - Edge TTS 配音
  - 自动字幕生成
  - 批量处理支持
