import json

with open('新产品_JSON 结果.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

inner = json.loads(data['data'])
sellpoints = json.loads(inner['sellpoints'])
content = sellpoints['修正后的最终内容']

print("=" * 70)
print("✅ 扣子工作流 - 产品分析结果")
print("=" * 70)
print()

# 审查结果
status = "✅ 通过" if sellpoints['是否通过审查'] == '是' else "❌ 未通过"
print(f"审查状态：{status}")
if '问题清单' in sellpoints and sellpoints['问题清单']:
    print(f"问题：{sellpoints['问题清单']}")
print()

# 显示内容
print(content)
print()

print("=" * 70)
print(f"执行 ID: {inner['execute_id']}")
print(f"Token: {data['usage']['token_count']}")
print("=" * 70)
