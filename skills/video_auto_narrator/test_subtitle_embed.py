#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试字幕嵌入"""

import subprocess
from pathlib import Path

# 测试文件
video = "E:/vedio_test/test1.mp4"
subtitle = "C:/Users/Administrator/.openclaw/workspace/skills/video_auto_narrator/work/test1_字幕.srt"
output = "E:/vedio_test/output_final/test1_测试字幕版.mp4"

# FFmpeg 命令
cmd = f'''ffmpeg -y -i "{video}" -vf "subtitles={subtitle}:force_style='FontName=Microsoft YaHei,FontSize=36,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=1,Align=2'" -c:a copy "{output}"'''

print(f"执行命令：{cmd}\n")

result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\n返回码：{result.returncode}")

# 检查输出文件
if Path(output).exists():
    print(f"\n✅ 成功！输出文件：{output}")
    print(f"文件大小：{Path(output).stat().st_size:,} 字节")
else:
    print(f"\n❌ 失败！输出文件不存在")
