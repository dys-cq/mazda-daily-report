import requests, base64, json, sys, os, re

# 测试图片路径
test_image_path = r"C:\Users\Administrator\.openclaw\media\outbound\01e73df1-9b20-49e4-9f2c-2d634e7b0098.jpg"

# 模拟技能输入参数
input_data = {
    'Product_photo_zhu': test_image_path,
    'Product_name': 'test_product'
}

# KieAI API 配置
KIEAI_API_KEY = '6d1930c46776db2e8224c9580a925378'
KIEAI_BASE_URL = 'https://kieai.redpandaai.co'

def upload_to_kieai_base64(image_data, file_name):
    """使用 Base64 API 上传图片到 KieAI"""
    url = f'{KIEAI_BASE_URL}/api/file-base64-upload'
    headers = {
        'Authorization': f'Bearer {KIEAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'base64Data': image_data,
        'uploadPath': 'images/product',
        'fileName': file_name
    }
    
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    return response.json()

print("=" * 60)
print("DS_zhutu_yansetiqu 技能测试 - 颜色提取")
print("=" * 60)

# Step 1: 读取并上传图片
print("\n[1] 读取本地文件并转为 Base64...")
with open(test_image_path, 'rb') as f:
    file_bytes = f.read()
    base64_data = base64.b64encode(file_bytes).decode('utf-8')
    base64_full = f'data:image/jpeg;base64,{base64_data}'

print(f"    文件大小：{len(file_bytes)} 字节")

print("\n[2] 上传到 KieAI 图床...")
upload_result = upload_to_kieai_base64(base64_full, 'test_product.jpg')

if upload_result.get('success'):
    file_url = upload_result['data']['fileUrl']
    print(f"    ✓ 上传成功")
    print(f"    文件 URL: {file_url}")
else:
    print(f"    ✗ 上传失败：{upload_result}")
    sys.exit(1)

# Step 2: 调用扣子工作流
print("\n[3] 调用扣子工作流提取颜色...")
coze_headers = {
    'Authorization': 'Bearer sat_XgBcLmKsynqKGraHmrSwW4BbGNQRqrPOlzqv6wKBLMjhyRGQtsRWiVYwBJCA93FC',
    'Content-Type': 'application/json'
}

coze_body = {
    'workflow_id': '7619645484659343402',
    'parameters': {
        'Product_photo_zhu': file_url
    }
}

coze_response = requests.post(
    'https://api.coze.cn/v1/workflow/stream_run',
    headers=coze_headers,
    json=coze_body,
    timeout=60
)

print(f"    状态码：{coze_response.status_code}")

# Step 3: 解析颜色结果
print("\n[4] 解析颜色数据...")
coze_result_text = coze_response.text

try:
    # 提取 JSON 内容
    json_match = re.search(r'"content":"({.*?})"', coze_result_text)
    if json_match:
        colour_data = json.loads(json_match.group(1).replace('\\"', '"'))
        colours = colour_data.get('colour', '')
        
        # 格式化输出
        print("\n" + "=" * 60)
        print("📊 颜色提取结果")
        print("=" * 60)
        
        # 解析并显示颜色
        if colours:
            color_lines = colours.split('\n')
            for line in color_lines:
                if line.strip():
                    print(f"    {line}")
        else:
            print("    未找到颜色数据")
    else:
        print("    无法解析扣子返回的 JSON")
        print(f"    原始响应：{coze_result_text[:500]}")
except Exception as e:
    print(f"    解析错误：{e}")
    print(f"    原始响应：{coze_result_text[:500]}")

print("\n" + "=" * 60)
print("✅ 技能测试完成")
print("=" * 60)
