#!/usr/bin/env python3
import requests
import json
import zipfile
import xml.etree.ElementTree as ET

# 1. 读取 DOCX
file_path = r'C:\Users\Administrator\.openclaw\media\outbound\20d52bb6-4b37-4ca3-aa7a-6b95971cd839.docx'
print("=" * 70)
print("DS_zhutu_Branch2 技能测试")
print("=" * 70)
print("\n读取文件...")

with zipfile.ZipFile(file_path, 'r') as z:
    with z.open('word/document.xml') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        texts = [elem.text.strip() for elem in root.iter() if elem.text and elem.text.strip()]
        product_info = '\n'.join(texts)

print(f"提取文本：{len(product_info)} 字符")

# 2. 调用 API
url = 'https://api.coze.cn/v1/workflow/run'
headers = {
    'Authorization': 'Bearer sat_XgBcLmKsynqKGraHmrSwW4BbGNQRqrPOlzqv6wKBLMjhyRGQtsRWiVYwBJCA93FC',
    'Content-Type': 'application/json'
}
payload = {
    'workflow_id': '7619646208533250090',
    'parameters': {
        'Product_Information': product_info,
        'Product_name': '测试产品'
    }
}

print("调用扣子工作流 API...")
response = requests.post(url, headers=headers, json=payload, timeout=120)
result = response.json()

print(f"响应状态：{response.status_code}")

# 3. 解析结果
inner = json.loads(result['data'])
sellpoints = json.loads(inner['sellpoints'])

# 获取内容（可能是字符串或字典）
content_raw = sellpoints.get('修正后的最终内容', '')

print("\n" + "=" * 70)
print("测试结果")
print("=" * 70)

# 检查内容类型
if isinstance(content_raw, str):
    # 字符串格式，需要进一步解析
    content = json.loads(content_raw)
    if isinstance(content, dict):
        print(f"\n✅ 产品名称：{content.get('产品全称', 'N/A')}")
        print(f"✅ 审查状态：{sellpoints.get('是否通过审查', 'N/A')}")
        if '问题清单' in sellpoints and sellpoints['问题清单']:
            print(f"⚠️  问题：{sellpoints['问题清单']}")
    else:
        print(f"\n内容预览：{content_raw[:200]}...")
elif isinstance(content_raw, dict):
    print(f"\n✅ 产品名称：{content_raw.get('产品全称', 'N/A')}")
    print(f"✅ 审查状态：{sellpoints.get('是否通过审查', 'N/A')}")
    if '问题清单' in sellpoints and sellpoints['问题清单']:
        print(f"⚠️  问题：{sellpoints['问题清单']}")

print(f"\n📊 执行 ID: {result.get('execute_id')}")
print(f"📊 Token 消耗：{result.get('usage', {}).get('token_count')}")
print(f"🔗 调试：{inner.get('debug_url')}")
print("\n" + "=" * 70)
print("✅ 技能执行成功！")
print("=" * 70)
