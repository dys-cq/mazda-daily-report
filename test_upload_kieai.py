import requests, base64, json

# 读取图片并转为 Base64
img_path = r"C:\Users\Administrator\.openclaw\media\outbound\01e73df1-9b20-49e4-9f2c-2d634e7b0098.jpg"
with open(img_path, 'rb') as f:
    image_bytes = f.read()
    base64_data = base64.b64encode(image_bytes).decode()

print(f"图片读取成功，大小：{len(image_bytes)} 字节")

# 图床 API 配置
upload_url = 'https://kieai.redpandaai.co/api/file-url-upload'
upload_headers = {
    'Authorization': 'Bearer 6d1930c46776db2e8224c9580a925378',
    'Content-Type': 'application/json'
}

# 方案 1：尝试直接传 Base64（可能不支持）
print("\n=== 测试 1：直接传 Base64 数据 ===")
upload_body = {
    'fileUrl': f'data:image/jpeg;base64,{base64_data}',
    'uploadPath': 'images/downloaded',
    'fileName': 'test_product.jpg'
}

try:
    upload_response = requests.post(upload_url, headers=upload_headers, json=upload_body, timeout=30)
    upload_result = upload_response.json()
    print(f"图床返回：{json.dumps(upload_result, ensure_ascii=False, indent=2)}")
    
    if upload_result.get('success'):
        print("[OK] Base64 上传成功！")
        file_path = upload_result.get('data', {}).get('filePath', '')
        image_url = f'https://kieai.redpandaai.co/{file_path}'
        print(f"图片 URL: {image_url}")
    else:
        print(f"[FAIL] Base64 上传失败：{upload_result.get('msg', 'Unknown error')}")
except Exception as e:
    print(f"[FAIL] 请求失败：{e}")

# 方案 2：使用外部图片 URL 测试
print("\n=== 测试 2：使用外部图片 URL ===")
upload_body = {
    'fileUrl': 'https://picsum.photos/seed/test123/800/600.jpg',
    'uploadPath': 'images/downloaded',
    'fileName': 'test_external.jpg'
}

try:
    upload_response = requests.post(upload_url, headers=upload_headers, json=upload_body, timeout=30)
    upload_result = upload_response.json()
    print(f"图床返回：{json.dumps(upload_result, ensure_ascii=False, indent=2)}")
    
    if upload_result.get('success'):
        print("[OK] 外部 URL 上传成功！")
        file_path = upload_result.get('data', {}).get('filePath', '')
        download_url = upload_result.get('data', {}).get('downloadUrl', '')
        print(f"文件路径：{file_path}")
        print(f"下载 URL: {download_url}")
    else:
        print(f"[FAIL] 外部 URL 上传失败：{upload_result.get('msg', 'Unknown error')}")
except Exception as e:
    print(f"[FAIL] 请求失败：{e}")

print("\n=== 结论 ===")
print("图床 API 只支持 HTTP/HTTPS URL，不支持 Base64 数据。")
print("如果需要上传本地图片，需要先将图片托管到可公开访问的 URL。")
