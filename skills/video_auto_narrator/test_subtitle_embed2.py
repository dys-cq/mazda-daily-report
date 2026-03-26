#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试字幕嵌入 - 使用相对路径"""

import subprocess
from pathlib import Path
import os

# 切换到 work 目录
os.chdir(r"C:\Users\Administrator\.openclaw\workspace\skills\video_auto_narrator")

# 测试文件（使用相对路径）
video = "../../E:/vedio_test/test1.mp4"
video_abs = "E:/vedio_test/test1.mp4"
subtitle = "work/test1_字幕.srt"
output = "E:/vedio_test/output_final/test1_测试字幕版.mp4"

# 方案 1: 使用相对路径
cmd = f'''ffmpeg -y -i "{video_abs}" -vf "subtitles={subtitle}:force_style='FontName=Microsoft YaHei,FontSize=36'" -c:a copy "{output}"'''

print(f"当前目录：{os.getcwd()}")
print(f"执行命令：{cmd}\n")
print(f"字幕文件存在：{Path(subtitle).exists()}")
print(f"视频文件存在：{Path(video_abs).exists()}\n")

result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')

print("STDERR (最后 30 行):")
lines = result.stderr.split('\n')
for line in lines[-30:]:
    print(line)

print(f"\n返回码：{result.returncode}")

# 检查输出文件
if Path(output).exists():
    print(f"\n✅ 成功！输出文件：{output}")
    print(f"文件大小：{Path(output).stat().st_size:,} 字节")
else:
    print(f"\n❌ 失败！输出文件不存在")
