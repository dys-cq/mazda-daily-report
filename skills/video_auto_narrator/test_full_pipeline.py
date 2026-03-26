#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试完整的视频合成流程"""

import subprocess
from pathlib import Path
import os

# 切换到技能目录
os.chdir(r"C:\Users\Administrator\.openclaw\workspace\skills\video_auto_narrator")

# 测试文件
video = "E:/vedio_test/test1.mp4"
audio = "work/test1_配音.mp3"
subtitle = "work/test1_字幕.srt"
output = "E:/vedio_test/output_with_subs/test1_完整版.mp4"
temp_output = "E:/vedio_test/output_with_subs/test1_临时.mp4"

print(f"工作目录：{os.getcwd()}")
print(f"视频存在：{Path(video).exists()}")
print(f"音频存在：{Path(audio).exists()}")
print(f"字幕存在：{Path(subtitle).exists()}\n")

# 步骤 1: 合并视频和音频
print("=" * 60)
print("步骤 1: 合并视频和音频")
print("=" * 60)

cmd1 = f'''ffmpeg -y -i "{video}" -i "{audio}" -c:v libx264 -c:a aac -b:a 192k -shortest "{temp_output}"'''
print(f"命令：{cmd1}\n")

result1 = subprocess.run(cmd1, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')

if 'video:' in result1.stderr:
    print("✅ 音频合并成功")
    print(f"临时文件：{temp_output}")
    print(f"文件大小：{Path(temp_output).stat().st_size:,} 字节\n")
else:
    print("❌ 音频合并失败")
    print(result1.stderr[-500:])
    exit(1)

# 步骤 2: 添加字幕
print("=" * 60)
print("步骤 2: 添加字幕")
print("=" * 60)

cmd2 = f'''ffmpeg -y -i "{temp_output}" -vf "subtitles={subtitle}:force_style='FontName=Microsoft YaHei,FontSize=36'" -c:a copy "{output}"'''
print(f"命令：{cmd2}\n")

result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')

print("FFmpeg 输出（最后 20 行）:")
lines = result2.stderr.split('\n')
for line in lines[-20:]:
    print(line)

if Path(output).exists():
    print(f"\n✅ 成功！最终文件：{output}")
    print(f"文件大小：{Path(output).stat().st_size:,} 字节")
    
    # 删除临时文件
    Path(temp_output).unlink()
    print(f"已删除临时文件")
else:
    print(f"\n❌ 失败！输出文件不存在")
