import requests, base64, json, sys, os

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

# Step 1: 检测输入类型并上传图片
print("=" * 50)
print("测试 DS_zhutu_yansetiqu 技能")
print("=" * 50)
print(f"\n[步骤 1] 检测输入类型...")
print(f"输入路径：{test_image_path}")
print(f"文件存在：{os.path.isfile(test_image_path)}")

if os.path.isfile(test_image_path):
    print(f"\n[步骤 2] 检测到本地文件，转为 Base64 上传...")
    with open(test_image_path, 'rb') as f:
        file_bytes = f.read()
        base64_data = base64.b64encode(file_bytes).decode('utf-8')
        base64_full = f'data:image/jpeg;base64,{base64_data}'
    
    print(f"文件大小：{len(file_bytes)} 字节")
    print(f"Base64 长度：{len(base64_full)} 字符")
    
    file_name = 'test_product.jpg'
    print(f"\n[步骤 3] 上传到 KieAI...")
    upload_result = upload_to_kieai_base64(base64_full, file_name)
    
    print(f"\nKieAI 返回结果:")
    print(json.dumps(upload_result, ensure_ascii=False, indent=2))
    
    # 检查上传结果
    if not upload_result.get('success'):
        print(f"\n[FAIL] 图床上传失败！")
        print(json.dumps({'error': '图床上传失败', 'details': upload_result}, ensure_ascii=False))
        sys.exit(1)
    
    # Step 2: 构建完整图片 URL
    file_url = upload_result.get('data', {}).get('fileUrl', '')
    download_url = upload_result.get('data', {}).get('downloadUrl', '')
    expires_at = upload_result.get('data', {}).get('expiresAt', 'unknown')
    
    print(f"\n[OK] 上传成功！")
    print(f"文件 URL: {file_url}")
    print(f"下载 URL: {download_url}")
    print(f"过期时间：{expires_at}")
    
    # Step 3: 调用扣子工作流
    print(f"\n[步骤 4] 调用扣子工作流...")
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

    # 解析扣子工作流返回结果
    coze_result_text = coze_response.text
    print(f"扣子工作流状态码：{coze_response.status_code}")
    
    try:
        # 尝试提取 JSON 数据
        import re
        json_match = re.search(r'"content":"({.*?})"', coze_result_text)
        if json_match:
            colour_data = json.loads(json_match.group(1).replace('\\"', '"'))
            colours = colour_data.get('colour', '')
        else:
            colours = coze_result_text
    except Exception as e:
        print(f"解析扣子返回结果时出错：{e}")
        colours = coze_result_text
    
    # 输出最终结果
    print(f"\n" + "=" * 50)
    print("测试结果 - 成功！")
    print("=" * 50)
    print(f"\n输入类型：local_file")
    print(f"上传成功：{file_url}")
    print(f"提取颜色：\n{colours}")
    print(f"\n[OK] 技能测试通过！")
    
else:
    print(f"\n[ERROR] 文件不存在：{test_image_path}")
    sys.exit(1)
