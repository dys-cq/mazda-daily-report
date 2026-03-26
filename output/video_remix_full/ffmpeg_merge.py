#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用 ffmpeg 重新合成视频
"""

import subprocess
from pathlib import Path

output_dir = Path(r"C:\Users\Administrator\.openclaw\workspace\output\video_remix_full")
work_dir = output_dir / "work"
audio_path = output_dir / "配音.mp3"

# 素材文件
assets = [
    work_dir / "asset_开头钩子.mp4",
    work_dir / "asset_痛点引入.mp4",
    work_dir / "asset_产品介绍.mp4",
    work_dir / "asset_卖点展示.mp4",
    work_dir / "asset_行动号召.mp4",
]

# 创建 concat 文件（ffmpeg 格式）
concat_file = output_dir / "concat.txt"
with open(concat_file, 'w', encoding='utf-8') as f:
    for asset in assets:
        # 使用正斜杠并转义单引号
        path_str = str(asset).replace("'", "'\\''").replace("\\", "/")
        f.write(f"file '{path_str}'\n")

print(f"Created: {concat_file}")

# 步骤 1: 先拼接视频（不含音频）
temp_video = output_dir / "temp_video_only.mp4"
print(f"\nStep 1: 拼接视频...")

cmd1 = [
    "ffmpeg", "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", str(concat_file),
    "-c", "copy",
    "-an",  # 不含音频
    str(temp_video)
]

result1 = subprocess.run(cmd1, capture_output=True, text=True)
if result1.returncode != 0:
    print(f"Error: {result1.stderr}")
else:
    print(f"OK: {temp_video.name}")

# 步骤 2: 添加音频
final_output = output_dir / "复刻版_最终.mp4"
print(f"\nStep 2: 添加音频...")

cmd2 = [
    "ffmpeg", "-y",
    "-i", str(temp_video),
    "-i", str(audio_path),
    "-c:v", "copy",
    "-c:a", "aac",
    "-b:a", "192k",
    "-shortest",
    str(final_output)
]

result2 = subprocess.run(cmd2, capture_output=True, text=True)
if result2.returncode != 0:
    print(f"Error: {result2.stderr}")
else:
    print(f"OK: {final_output.name}")

# 清理临时文件
print(f"\nStep 3: 清理临时文件...")
try:
    concat_file.unlink()
    temp_video.unlink()
    print("Cleaned temp files")
except:
    pass

print(f"\n[OK] 完成！最终视频：{final_output}")
