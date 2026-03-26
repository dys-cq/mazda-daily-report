# Video Auto Narrator 技能测试

## 测试步骤

### 1. 准备测试视频

创建一个简单的测试视频（或使用现有视频）：
```bash
# 如果有测试视频，放在这里
C:\Users\Administrator\.openclaw\workspace\skills\video_auto_narrator\test_videos\
```

### 2. 运行测试

```bash
cd C:\Users\Administrator\.openclaw\workspace\skills\video_auto_narrator

# 测试单个视频
uv run python video_narrator.py ./test_videos ./test_output

# 测试指定语音
uv run python video_narrator.py ./test_videos ./test_output --voice zh-CN-YunxiNeural

# 测试指定风格
uv run python video_narrator.py ./test_videos ./test_output --style tutorial
```

### 3. 检查输出

应该生成以下文件：
```
test_output/
├── xxx_带解说.mp4      # 最终视频
├── xxx_解说文案.txt    # 解说词
├── xxx_字幕.srt        # 字幕文件
├── xxx_配音.mp3        # 配音音频
└── xxx_处理报告.md     # 处理报告
```

### 4. 验证功能

- [ ] 视频能正常播放
- [ ] 配音音频清晰
- [ ] 字幕显示正常
- [ ] 解说文案通顺
- [ ] 音画基本对齐

## 已知限制

1. **内容理解** - 当前版本使用简化版分析，实际应集成多模态 AI（如 Gemini Vision）
2. **音画对齐** - 当前版本使用简化对齐，实际应使用 Whisper 时间戳
3. **文案生成** - 当前版本使用模板，实际应调用 LLM API

## 下一步优化

1. 集成 Gemini Vision 进行视频内容理解
2. 使用 Whisper 生成精确时间戳
3. 调用 LLM API 生成更智能的文案
4. 改进音画对齐算法

## 测试命令

```bash
# 检查依赖
uv pip list | Select-String "edge-tts|moviepy"

# 测试 TTS
uv run python -c "import edge_tts; print('Edge TTS OK')"

# 测试 MoviePy
uv run python -c "from moviepy import VideoFileClip; print('MoviePy OK')"

# 测试 FFmpeg
ffmpeg -version
```
