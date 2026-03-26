import json

# 读取 JSON 文件
with open('新产品测试结果.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 解析嵌套 JSON
inner = json.loads(data['data'])
sellpoints = json.loads(inner['sellpoints'])

# 获取内容
content = sellpoints.get('修正后的最终内容', sellpoints.get('检查结果分析', ''))

print('=' * 70)
print('扣子工作流 - 产品分析结果')
print('=' * 70)
print()
print(content)
print()
print('=' * 70)
print(f"执行 ID: {inner['execute_id']}")
print(f"Token 消耗：{data['usage']['token_count']}")
print('=' * 70)
