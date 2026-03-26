#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试从技能目录执行"""

import subprocess
from pathlib import Path
import os

# 切换到技能目录
os.chdir(r"C:\Users\Administrator\.openclaw\workspace\skills\video_auto_narrator")

# 测试命令
temp_file = "E:/vedio_test/output_with_embedded_subs/test1_带解说_temp.mp4"
subtitle = "work/test1_字幕.srt"
output = "E:/vedio_test/output_with_embedded_subs/test1_最终测试.mp4"

cmd = f'ffmpeg -y -i "{temp_file}" -vf "subtitles={subtitle}:force_style=\'FontName=Microsoft YaHei,FontSize=36\'" -c:a copy "{output}"'

print(f"当前目录：{os.getcwd()}")
print(f"命令：{cmd}\n")
print(f"临时文件存在：{Path(temp_file).exists()}")
print(f"字幕文件存在：{Path(subtitle).exists()}\n")

result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')

print("STDERR:")
print(result.stderr)
print(f"\n返回码：{result.returncode}")

if Path(output).exists():
    print(f"\n✅ 成功！文件：{output}")
    print(f"大小：{Path(output).stat().st_size:,} 字节")
else:
    print(f"\n❌ 失败")
