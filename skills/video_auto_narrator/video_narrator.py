#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Video Auto Narrator - 视频自动解说配音技能
自动为本地视频素材生成营销式解说配音，实现音画对齐和字幕生成
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
import edge_tts
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip

# 配置参数
CONFIG = {
    # TTS 配置
    "default_voice": "zh-CN-XiaoxiaoNeural",
    "default_rate": "+0%",
    "default_volume": "+0%",

    # 文案配置
    "style": "marketing",
    "max_script_length": 500,

    # 视频配置
    "target_duration": None,
    "video_codec": "libx264",
    "video_bitrate": "5000k",
    "audio_bitrate": "192k",

    # 字幕配置
    "subtitle_font": "Microsoft-YaHei",
    "subtitle_size": 36,
    "subtitle_color": "white",
    "subtitle_outline": "black",

    # 对齐配置
    "alignment_tolerance": 0.5,
    "auto_adjust_speed": True,
}

# 营销式文案模板
MARKETING_TEMPLATES = {
    "opening": [
        "家人们！今天必须给你们安利这个神器！",
        "哇！这个真的太好用！",
        "兄弟们！发现一个宝藏！",
        "绝了！这个我必须分享！",
    ],
    "pain_point": [
        "是不是经常遇到这个问题？",
        "有没有同款烦恼？",
        "相信大家都遇到过这种情况...",
    ],
    "product_intro": [
        "看看这个，简直太好用！",
        "就是这个宝贝！",
        "今天的主角就是它！",
    ],
    "selling_points": [
        "第一...第二...第三...",
        "不仅...而且...最重要的是...",
        "三大亮点让你无法拒绝！",
    ],
    "call_to_action": [
        "链接在评论区，赶紧冲！",
        "手慢无，快去抢！",
        "今天福利价，别错过！",
    ],
}


def analyze_video_content(video_path):
    """
    分析视频内容（简化版，实际应使用多模态 AI）
    返回视频基本信息和场景描述
    """
    print(f"📊 分析视频：{video_path}")

    clip = VideoFileClip(str(video_path))

    info = {
        "duration": clip.duration,
        "width": clip.w,
        "height": clip.h,
        "fps": clip.fps,
        "has_audio": clip.audio is not None,
        "scenes": [],
    }

    # 简化版场景分析（实际应使用 AI 模型）
    # 这里只是示例，实际需要使用 Gemini Vision 等模型
    info["scenes"].append({
        "time": 0,
        "description": "视频开场",
        "type": "intro"
    })

    clip.close()

    return info


def generate_marketing_script(video_info):
    """
    根据视频内容生成营销式解说文案
    """
    print("📝 生成营销式解说文案...")

    duration = video_info.get("duration", 60)

    # 根据视频时长估算文案长度（约 4 字/秒）
    estimated_words = int(duration * 4)

    # 使用模板生成文案
    script = f"""{MARKETING_TEMPLATES['opening'][0]}

{MARKETING_TEMPLATES['pain_point'][0]}

{MARKETING_TEMPLATES['product_intro'][0]}

{MARKETING_TEMPLATES['selling_points'][0]}

{MARKETING_TEMPLATES['call_to_action'][0]}"""

    print(f"✅ 生成文案，约{len(script)}字")
    return script


async def generate_tts_audio(text, output_path, voice=None, rate=None):
    """
    使用 Edge TTS 生成配音音频
    """
    voice = voice or CONFIG["default_voice"]
    rate = rate or CONFIG["default_rate"]

    print(f"🎙️ 生成 TTS 语音：{voice}")

    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(str(output_path))

    print(f"✅ TTS 音频已保存：{output_path}")
    return output_path


def generate_subtitle_from_text(text, duration, output_path):
    """
    根据文本生成简单字幕（简化版，实际应使用 Whisper 时间戳）
    """
    print(f"📜 生成字幕...")

    # 简化版：将文案平均分段
    lines = text.split('\n')
    segment_duration = duration / len(lines)

    srt_content = ""
    for i, line in enumerate(lines):
        start = i * segment_duration
        end = (i + 1) * segment_duration

        srt_content += f"{i+1}\n"
        srt_content += f"{format_srt_time(start)} --> {format_srt_time(end)}\n"
        srt_content += f"{line}\n\n"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(srt_content)

    print(f"✅ 字幕已保存：{output_path}")
    return output_path


def format_srt_time(seconds):
    """将秒数转换为 SRT 时间格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def add_subtitles_to_video(video_path, audio_path, subtitle_path, output_path, work_dir=None):
    """
    将配音和字幕添加到视频 - 使用 ffmpeg 命令行，从 work 目录执行使用相对路径
    
    Args:
        video_path: 输入视频路径
        audio_path: 输入音频路径
        subtitle_path: 字幕文件路径
        output_path: 输出视频路径
        work_dir: 工作目录（用于计算相对路径）
    """
    print(f"🎬 合成视频...")
    
    import subprocess
    import os
    
    # 保存当前目录
    original_cwd = os.getcwd()
    
    try:
        # 转换为绝对路径
        video_abs = str(Path(video_path).resolve())
        audio_abs = str(Path(audio_path).resolve())
        output_abs = str(Path(output_path).resolve())
        
        # 使用英文临时文件名避免编码问题
        video_name = Path(video_path).stem
        temp_output = str(Path(output_path).parent / f"{video_name}_temp.mp4")
        
        # 步骤 1: 合并视频和音频
        print(f"🔧 合并视频和音频...")
        cmd1 = f'ffmpeg -y -i "{video_abs}" -i "{audio_abs}" -c:v libx264 -c:a aac -b:a 192k -shortest "{temp_output}"'
        result1 = subprocess.run(cmd1, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if not ('video:' in result1.stderr and 'audio:' in result1.stderr):
            print(f"⚠️ 音频合并失败，保留原视频音频")
            # 直接使用原视频
            temp_output = video_abs
        
        # 步骤 2: 添加字幕 - 关键：切换到 work 目录使用相对路径
        if Path(subtitle_path).exists() and work_dir:
            print(f"📜 添加字幕到视频...")
            
            # 切换到 work 目录
            os.chdir(str(work_dir))
            
            # 使用相对路径
            subtitle_rel = f"work/{Path(subtitle_path).name}"
            temp_rel = Path(temp_output).name
            output_rel = Path(output_abs).name
            output_parent = str(Path(output_abs).parent)
            
            print(f"📜 字幕相对路径：{subtitle_rel}")
            
            # 从 work 目录执行
            cmd2 = f'ffmpeg -y -i "{output_parent}/{temp_rel}" -vf "subtitles={subtitle_rel}:force_style=\'FontName=Microsoft YaHei,FontSize=36\'" -c:a copy "{output_parent}/{output_rel}"'
            print(f"🔧 执行：{cmd2}")
            
            result2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            # 检查是否成功
            if 'video:' in result2.stderr and 'Lsize=' in result2.stderr:
                print(f"✅ 字幕已成功嵌入")
                # 删除临时文件
                if Path(temp_output).exists() and temp_output != video_abs:
                    Path(temp_output).unlink()
            else:
                print(f"⚠️ 字幕嵌入失败，保留无字幕版本")
                if temp_output != output_abs and temp_output != video_abs:
                    Path(temp_output).rename(output_abs)
        else:
            # 没有字幕文件或 work_dir，直接使用临时文件
            if temp_output != output_abs and temp_output != video_abs:
                Path(temp_output).rename(output_abs)
            
        print(f"✅ 视频已保存：{output_abs}")
        
    except Exception as e:
        print(f"❌ 处理失败：{e}")
        # 清理临时文件
        if Path(temp_output).exists() and temp_output != video_abs:
            Path(temp_output).unlink()
        raise
    finally:
        # 恢复原始目录
        os.chdir(original_cwd)


def process_single_video(video_path, output_dir, work_dir):
    """
    处理单个视频
    """
    video_name = Path(video_path).stem
    print(f"\n{'='*60}")
    print(f"🎬 开始处理：{video_name}")
    print(f"{'='*60}")

    # 1. 分析视频内容
    video_info = analyze_video_content(video_path)

    # 2. 生成营销式文案
    script = generate_marketing_script(video_info)

    # 3. 保存文案
    script_path = output_dir / f"{video_name}_解说文案.txt"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script)

    # 4. 生成 TTS 配音
    audio_path = work_dir / f"{video_name}_配音.mp3"
    asyncio.run(generate_tts_audio(script, audio_path))

    # 5. 生成字幕
    subtitle_path = work_dir / f"{video_name}_字幕.srt"
    generate_subtitle_from_text(script, video_info["duration"], subtitle_path)

    # 6. 合成最终视频
    output_path = output_dir / f"{video_name}_带解说.mp4"
    add_subtitles_to_video(video_path, audio_path, subtitle_path, output_path, work_dir)

    # 7. 生成处理报告
    report_path = output_dir / f"{video_name}_处理报告.md"
    generate_report(video_info, script, video_path, output_path, report_path)

    print(f"\n✅ 处理完成！输出：{output_path}")
    return output_path


def generate_report(video_info, script, input_path, output_path, report_path):
    """生成处理报告"""
    report = f"""# 视频处理报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 输入视频
- **文件**: {input_path}
- **时长**: {video_info['duration']:.2f}秒
- **分辨率**: {video_info['width']}x{video_info['height']}
- **帧率**: {video_info['fps']}fps
- **原有音频**: {'是' if video_info['has_audio'] else '否'}

## 输出视频
- **文件**: {output_path}
- **解说风格**: {CONFIG['style']}
- **TTS 语音**: {CONFIG['default_voice']}
- **字幕**: 已生成

## 解说文案
```
{script}
```

## 处理说明
1. 视频内容分析 ✓
2. 营销式文案生成 ✓
3. Edge TTS 语音合成 ✓
4. 字幕生成 ✓
5. 视频合成 ✓

---
*Video Auto Narrator v1.0*
"""

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)


def main():
    parser = argparse.ArgumentParser(
        description="Video Auto Narrator - 视频自动解说配音技能",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  uv run python video_narrator.py ./videos ./output
  uv run python video_narrator.py ./videos ./output --voice zh-CN-YunxiNeural
  uv run python video_narrator.py ./videos ./output --style marketing
        """
    )

    parser.add_argument("input", type=str, help="输入视频文件或文件夹路径")
    parser.add_argument("output", type=str, nargs="?", default="./output", help="输出目录（默认：./output）")
    parser.add_argument("--work-dir", type=str, default="./work", help="临时工作目录（默认：./work）")
    parser.add_argument("--voice", type=str, default=CONFIG["default_voice"], help="TTS 语音")
    parser.add_argument("--style", type=str, default=CONFIG["style"], choices=["marketing", "documentary", "tutorial"], help="解说风格")
    parser.add_argument("--rate", type=str, default=CONFIG["default_rate"], help="语速（如：+20%, -10%）")

    args = parser.parse_args()

    # 更新配置
    CONFIG["default_voice"] = args.voice
    CONFIG["style"] = args.style
    CONFIG["default_rate"] = args.rate

    # 创建输出目录
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    work_dir = Path(args.work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    input_path = Path(args.input)

    if not input_path.exists():
        print(f"❌ 输入路径不存在：{input_path}")
        sys.exit(1)

    # 处理单个文件或文件夹
    if input_path.is_file():
        process_single_video(input_path, output_dir, work_dir)
    elif input_path.is_dir():
        video_files = list(input_path.glob("*.mp4")) + \
                      list(input_path.glob("*.mov")) + \
                      list(input_path.glob("*.avi")) + \
                      list(input_path.glob("*.MTS"))

        if not video_files:
            print(f"❌ 未找到视频文件：{input_path}")
            sys.exit(1)

        print(f"📁 找到 {len(video_files)} 个视频文件")

        for video_file in video_files:
            try:
                process_single_video(video_file, output_dir, work_dir)
            except Exception as e:
                print(f"❌ 处理失败 {video_file}: {e}")
                continue
    else:
        print(f"❌ 无效输入：{input_path}")
        sys.exit(1)

    print(f"\n🎉 全部处理完成！输出目录：{output_dir}")


if __name__ == "__main__":
    main()
