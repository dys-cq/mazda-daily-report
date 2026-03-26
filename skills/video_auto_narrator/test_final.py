#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""最终测试 - 从 skill 目录执行，使用相对路径"""

import subprocess
from pathlib import Path
import os

# 切换到技能目录
skill_dir = r"C:\Users\Administrator\.openclaw\workspace\skills\video_auto_narrator"
os.chdir(skill_dir)

print(f"当前目录：{os.getcwd()}")
print(f"work 目录存在：{Path('work').exists()}\n")

# 测试文件（相对路径）
video = "E:/vedio_test/test1.mp4"
audio = "work/test1_配音.mp3"
subtitle = "work/test1_字幕.srt"
output_dir = "E:/vedio_test/output_final_v3"
temp_output = f"{output_dir}/test1_temp.mp4"
final_output = f"{output_dir}/test1_final.mp4"

# 确保输出目录存在
Path(output_dir).mkdir(exist_ok=True)

print("=" * 60)
print("步骤 1: 合并视频和音频")
print("=" * 60)

cmd1 = f'ffmpeg -y -i "{video}" -i "{audio}" -c:v libx264 -c:a aac -b:a 192k -shortest "{temp_output}"'
print(f"命令：{cmd1}\n")

result1 = subprocess.run(cmd1, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')

if 'video:' in result1.stderr and 'audio:' in result1.stderr:
    print("✅ 合并成功")
    print(f"临时文件：{temp_output}")
    print(f"文件大小：{Path(temp_output).stat().st_size:,} 字节\n")
else:
    print("❌ 合并失败")
    print(result1.stderr[-500:])
    exit(1)

print("=" * 60)
print("步骤 2: 添加字幕（使用相对路径）")
print("=" * 60)

# 关键：使用相对于当前目录的路径
cmd2 = f'ffmpeg -y -i "{temp_output}" -vf "subtitles={subtitle}:force_style=\'FontName=Microsoft YaHei,FontSize=36\'" -c:a copy "{final_output}"'
print(f"命令：{cmd2}\n")

result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')

print("FFmpeg 输出（最后 15 行）:")
lines = result2.stderr.split('\n')
for line in lines[-15:]:
    print(line)

if Path(final_output).exists():
    size = Path(final_output).stat().st_size
    print(f"\n✅ 成功！最终文件：{final_output}")
    print(f"文件大小：{size:,} 字节")
    
    # 删除临时文件
    Path(temp_output).unlink()
    print(f"已清理临时文件")
else:
    print(f"\n❌ 失败！输出文件不存在")
    print(f"错误：{result2.stderr[-300:]}")
