#!/usr/bin/env python3
"""
Extract and display ingredients from Coze workflow result.
Enhanced version with better parsing.
"""

import json
import re
import sys

# API 返回的完整结果
api_response = {
  "code": 0,
  "data": "{\"sellpoints\":\"{\\\"修正后的最终内容\\\":\\\"### 1. 产品全称\\\\n酷洛菲黑松露润浸洁面乳（Black Truffle Moisturizing Facial Cleanser）\\\\n\\\\n### 2. 产品成分信息\\\\n* **核心功效成分**: 黑孢块菌（黑松露）提取物、透明质酸钠、积雪草叶提取物、甘油、尿囊素\\\\n* **全成分列表**:\\\\n水、月桂醇磺基琥珀酸酯二钠、月桂醇聚醚硫酸酯钠、氯化钠、椰油酰胺丙基甜菜碱、甘油、乙二醇二硬脂酸酯、精氨酸、PEG-120 甲基葡糖二油酸酯、PEG-150 二硬脂酸酯、苯氧乙醇、氯苯甘醚、尿囊素、氢氧化钾\\\\n其他微量成分：（日用）香精、黄原胶、EDTA 二钠、亚硫酸钠、乙基己基甘油、黑孢块菌（TUBER MELANOSPORUM）提取物、苯甲酸钠、山梨酸钾、丁二醇、硝酸镁、透明质酸钠、甲基氯异噻唑啉酮、积雪草（CENTELLA ASIATICA）叶提取物、氯化镁、甲基异噻唑啉酮、甘氨酸、丝氨酸、谷氨酸、天冬氨酸、亮氨酸、丙氨酸、赖氨酸、酪氨酸、苯丙氨酸、脯氨酸、苏氨酸、缬氨酸、异亮氨酸、组氨酸\\\\n\\\"}\"}",
  "execute_id": "7620409746637520959"
}

# 解析嵌套 JSON
data = json.loads(api_response['data'])
result = json.loads(data['sellpoints'])
content = result['修正后的最终内容']

# 清理转义字符
content = content.replace('\\\\n', '\n').replace('\\\\', '\\')

print("=" * 70)
print("产品成分信息 - 完整提取")
print("=" * 70)
print()

# 按行解析
lines = content.split('\n')
in_core = False
in_full = False
in_trace = False

core_ingredients = []
full_ingredients = []
trace_ingredients = []

for line in lines:
    line = line.strip()
    
    # 检查核心功效成分
    if '**核心功效成分**' in line:
        in_core = True
        in_full = False
        in_trace = False
        # 提取冒号后的内容
        if ':' in line or '：' in line:
            parts = line.split(':' if ':' in line else '：', 1)
            if len(parts) > 1:
                ingredients_text = parts[1].strip()
                core_ingredients = [ing.strip() for ing in ingredients_text.split('、') if ing.strip()]
        continue
    
    # 检查全成分列表
    if '**全成分列表**' in line:
        in_core = False
        in_full = True
        in_trace = False
        continue
    
    # 检查微量成分
    if '其他微量成分' in line or '微量成分' in line:
        in_core = False
        in_full = False
        in_trace = True
        # 提取冒号后的内容
        if ':' in line or '：' in line:
            parts = line.split(':' if ':' in line else '：', 1)
            if len(parts) > 1:
                ingredients_text = parts[1].strip()
                trace_ingredients = [ing.strip() for ing in ingredients_text.split('、') if ing.strip()]
        continue
    
    # 提取成分
    if in_full and line and not line.startswith('*') and not line.startswith('#'):
        ingredients = [ing.strip() for ing in line.split('、') if ing.strip()]
        full_ingredients.extend(ingredients)
        in_full = False  # 只处理一行
    
    if in_trace and line and not line.startswith('*') and not line.startswith('#'):
        ingredients = [ing.strip() for ing in line.split('、') if ing.strip()]
        trace_ingredients.extend(ingredients)
        in_trace = False  # 只处理一行

# 输出结果
print("【核心功效成分】")
for ing in core_ingredients:
    print(f"  ✓ {ing}")
print()

print("【全成分列表】")
for i, ing in enumerate(full_ingredients, 1):
    print(f"  {i:2d}. {ing}")
print()

print("【微量成分】")
for ing in trace_ingredients:
    print(f"  • {ing}")
print()

print("=" * 70)
print(f"执行 ID: {api_response['execute_id']}")
print(f"核心成分：{len(core_ingredients)} 个")
print(f"全成分：{len(full_ingredients)} 个")
print(f"微量成分：{len(trace_ingredients)} 个")
print("=" * 70)
