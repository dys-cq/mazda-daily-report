"""
测试 SKILL.md 格式的技能
"""

import sys
from pathlib import Path

# 添加技能脚本目录到 Python 路径
skill_scripts = Path(__file__).parent / 'skills' / 'DS_zhutu_yansetiqu' / 'scripts'
sys.path.insert(0, str(skill_scripts))

# 导入主模块
from main import extract_colors

# 测试图片路径
test_image = r"C:\Users\Administrator\.openclaw\media\outbound\fc28b1fa-ff5d-4bb8-839d-adb243ab4067.jpg"

print("=" * 60)
print("DS_zhutu_yansetiqu SKILL.md 格式测试")
print("=" * 60)

print("\n[1] 调用技能提取颜色...")
result = extract_colors(test_image, 'test_product')

if result.get('error'):
    print(f"\n[ERROR] {result['error']}")
    if 'details' in result:
        print(f"详情：{result['details']}")
    sys.exit(1)

print("\n[OK] 技能执行成功！")
print("\n" + "=" * 60)
print("颜色提取结果")
print("=" * 60)

if result.get('colours'):
    colours = result['colours']
    color_lines = colours.split('\n')
    for line in color_lines:
        if line.strip():
            print(f"    {line}")

print("\n" + "=" * 60)
print("完整输出（JSON 格式）")
print("=" * 60)
import json
print(json.dumps(result, ensure_ascii=False, indent=2))

print("\n[OK] 测试完成！")
