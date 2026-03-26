import requests, base64, json

# 测试图片路径
test_image_path = r"C:\Users\Administrator\.openclaw\media\outbound\01e73df1-9b20-49e4-9f2c-2d634e7b0098.jpg"

# KieAI API 配置
KIEAI_API_KEY = '6d1930c46776db2e8224c9580a925378'
KIEAI_BASE_URL = 'https://kieai.redpandaai.co'

# 读取图片
with open(test_image_path, 'rb') as f:
    file_bytes = f.read()
    base64_data = base64.b64encode(file_bytes).decode('utf-8')
    base64_full = f'data:image/jpeg;base64,{base64_data}'

# 上传到 KieAI
url = f'{KIEAI_BASE_URL}/api/file-base64-upload'
headers = {
    'Authorization': f'Bearer {KIEAI_API_KEY}',
    'Content-Type': 'application/json'
}

payload = {
    'base64Data': base64_full,
    'uploadPath': 'images/product',
    'fileName': 'test_product.jpg'
}

print("正在上传到 KieAI...")
response = requests.post(url, json=payload, headers=headers, timeout=30)
result = response.json()

print("\nKieAI 完整返回结果:")
print(json.dumps(result, ensure_ascii=False, indent=2))

# 检查返回的字段
if result.get('success'):
    data = result.get('data', {})
    print("\n可用字段:")
    for key in data.keys():
        print(f"  - {key}: {data[key]}")
