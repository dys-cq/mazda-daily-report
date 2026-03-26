import requests, base64, json, re

# 测试图片路径
test_image_path = r"C:\Users\Administrator\.openclaw\media\outbound\01e73df1-9b20-49e4-9f2c-2d634e7b0098.jpg"

# KieAI API 配置
KIEAI_API_KEY = '6d1930c46776db2e8224c9580a925378'
KIEAI_BASE_URL = 'https://kieai.redpandaai.co'

print("=" * 60)
print("DS_zhutu_yansetiqu 技能 - 颜色提取测试")
print("=" * 60)

# Step 1: 读取并上传图片
print("\n[1] 读取图片并上传到 KieAI...")
with open(test_image_path, 'rb') as f:
    file_bytes = f.read()
    base64_data = base64.b64encode(file_bytes).decode('utf-8')
    base64_full = f'data:image/jpeg;base64,{base64_data}'

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

response = requests.post(url, json=payload, headers=headers, timeout=30)
upload_result = response.json()

if upload_result.get('success'):
    download_url = upload_result['data']['downloadUrl']
    print("    [OK] 上传成功")
    print(f"    下载 URL: {download_url}")
else:
    print(f"    [FAIL] 上传失败：{upload_result}")
    exit(1)

# Step 2: 调用扣子工作流
print("\n[2] 调用扣子工作流提取颜色...")
coze_headers = {
    'Authorization': 'Bearer sat_XgBcLmKsynqKGraHmrSwW4BbGNQRqrPOlzqv6wKBLMjhyRGQtsRWiVYwBJCA93FC',
    'Content-Type': 'application/json'
}

coze_body = {
    'workflow_id': '7619645484659343402',
    'parameters': {
        'Product_photo_zhu': download_url
    }
}

coze_response = requests.post(
    'https://api.coze.cn/v1/workflow/stream_run',
    headers=coze_headers,
    json=coze_body,
    timeout=60
)

print(f"    状态码：{coze_response.status_code}")

# Step 3: 解析并显示颜色
print("\n[3] 解析颜色数据...")
coze_result_text = coze_response.text

try:
    json_match = re.search(r'"content":"({.*?})"', coze_result_text)
    if json_match:
        colour_data = json.loads(json_match.group(1).replace('\\"', '"'))
        colours = colour_data.get('colour', '')
        
        print("\n" + "=" * 60)
        print("颜色提取结果")
        print("=" * 60)
        
        if colours:
            color_lines = colours.split('\n')
            for line in color_lines:
                if line.strip():
                    print(f"    {line}")
        else:
            print("    未找到颜色数据")
            
        print("\n" + "=" * 60)
        print("[OK] 测试完成 - 技能输出应为上述颜色数据")
        print("=" * 60)
    else:
        print("    无法解析扣子返回的 JSON")
        print(f"    原始响应：{coze_result_text[:500]}")
except Exception as e:
    print(f"    解析错误：{e}")
    print(f"    原始响应：{coze_result_text[:500]}")
