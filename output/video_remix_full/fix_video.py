#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速修复视频合成
"""

from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
from pathlib import Path

output_dir = Path(r"C:\Users\Administrator\.openclaw\workspace\output\video_remix_full")
work_dir = output_dir / "work"
audio_path = output_dir / "配音.mp3"

# 素材文件（按顺序）
asset_files = [
    work_dir / "asset_开头钩子.mp4",
    work_dir / "asset_痛点引入.mp4",
    work_dir / "asset_产品介绍.mp4",
    work_dir / "asset_卖点展示.mp4",
    work_dir / "asset_行动号召.mp4",
]

# 目标时长（原视频 58.8 秒，每段约 11.76 秒）
target_duration = 58.8
segment_duration = target_duration / 5

print("加载素材...")
clips = []

for i, asset_path in enumerate(asset_files):
    if asset_path.exists():
        try:
            clip = VideoFileClip(str(asset_path))
            print(f"  [{i+1}/5] {asset_path.name}: {clip.duration:.1f}秒")
            
            # 调整时长
            if clip.duration > segment_duration:
                clip = clip.subclipped(0, segment_duration)
            elif clip.duration < segment_duration:
                clip = clip.loop(duration=segment_duration)
            
            clips.append(clip)
        except Exception as e:
            print(f"  [ERROR] {asset_path.name}: {e}")
    else:
        print(f"  [MISSING] {asset_path.name}")

if not clips:
    print("没有可用素材！")
    exit(1)

print(f"\n合成视频 ({len(clips)} 个片段)...")
final = concatenate_videoclips(clips, method="compose")

# 添加音频
if audio_path.exists():
    print("添加音频...")
    audio = AudioFileClip(str(audio_path))
    
    # 调整音频时长匹配视频
    if audio.duration > final.duration:
        audio = audio.subclipped(0, final.duration)
    # 音频太短就保持原样，视频会自动结束
    
    final = final.with_audio(audio)

# 输出
output_path = output_dir / "复刻版_修复.mp4"
print(f"输出：{output_path.name}")

final.write_videofile(
    str(output_path),
    codec="libx264",
    bitrate="5000k",
    audio_codec="aac",
    audio_bitrate="192k",
    fps=24,
    logger=None,
)

final.close()
for clip in clips:
    clip.close()

print(f"\n[OK] 完成！{output_path}")
