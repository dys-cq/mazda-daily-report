import requests, base64, json

# 读取图片并转为 Base64
img_path = r"C:\Users\Administrator\.openclaw\media\outbound\01e73df1-9b20-49e4-9f2c-2d634e7b0098.jpg"
with open(img_path, 'rb') as f:
    image_bytes = f.read()
    base64_data = base64.b64encode(image_bytes).decode()
    product_photo = f'data:image/jpeg;base64,{base64_data}'

product_name = "product_test"

print(f"正在上传图片... (Base64 长度：{len(product_photo)})")

# Step 1: 上传图片到图床 (使用 JSON 格式，直接传 Base64)
upload_url = 'https://kieai.redpandaai.co/api/file-url-upload'
upload_headers = {
    'Authorization': 'Bearer 6d1930c46776db2e8224c9580a925378',
    'Content-Type': 'application/json'
}

# 尝试直接传 Base64 数据
upload_body = {
    'fileUrl': product_photo,
    'uploadPath': 'images/downloaded',
    'fileName': f'{product_name}1.jpg'
}

print("正在上传 Base64 数据到图床...")
upload_response = requests.post(upload_url, headers=upload_headers, json=upload_body, timeout=30)

upload_result = upload_response.json()
print(f"图床返回：{json.dumps(upload_result, ensure_ascii=False, indent=2)}")

if not upload_result.get('success'):
    print(json.dumps({'error': '图床上传失败', 'details': upload_result}))
    print("尝试使用外部图片 URL...")
    # 如果 Base64 失败，使用一个测试图片 URL
    upload_body = {
        'fileUrl': 'https://picsum.photos/seed/test123/800/600.jpg',
        'uploadPath': 'images/downloaded',
        'fileName': f'{product_name}1.jpg'
    }
    upload_response = requests.post(upload_url, headers=upload_headers, json=upload_body, timeout=30)
    upload_result = upload_response.json()
    print(f"图床返回（测试 URL）: {json.dumps(upload_result, ensure_ascii=False, indent=2)}")
    
    if not upload_result.get('success'):
        print(json.dumps({'error': '图床上传失败', 'details': upload_result}))
        exit(1)

# Step 2: 构建完整图片 URL
file_path = upload_result.get('data', {}).get('filePath', '')
image_url = f'https://kieai.redpandaai.co/{file_path}'
print(f"图片 URL: {image_url}")

# Step 3: 调用扣子工作流
print("正在调用扣子工作流...")
coze_headers = {
    'Authorization': 'Bearer sat_XgBcLmKsynqKGraHmrSwW4BbGNQRqrPOlzqv6wKBLMjhyRGQtsRWiVYwBJCA93FC',
    'Content-Type': 'application/json'
}

coze_body = {
    'workflow_id': '7619645484659343402',
    'parameters': {
        'Product_photo_zhu': image_url
    }
}

coze_response = requests.post(
    'https://api.coze.cn/v1/workflow/stream_run',
    headers=coze_headers,
    json=coze_body,
    timeout=60
)

# 输出结果
result = {
    'success': True,
    'uploaded_image_url': image_url,
    'coze_status_code': coze_response.status_code,
    'coze_response': coze_response.text
}

print("\n=== 最终结果 ===")
print(json.dumps(result, ensure_ascii=False, indent=2))
