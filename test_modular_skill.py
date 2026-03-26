import requests, base64, json, sys, os, re
from pathlib import Path

# 获取技能根目录
skill_root = Path(__file__).parent / 'skills' / 'DS_zhutu_yansetiqu'
scripts_dir = skill_root / 'scripts'

# 添加 scripts 目录到 Python 路径
sys.path.insert(0, str(scripts_dir))

# 导入 KieAI 上传模块
from kieai_uploader import upload_to_kieai_base64, get_file_url

# 测试图片路径（新图片）
test_image_path = r"C:\Users\Administrator\.openclaw\media\outbound\fc28b1fa-ff5d-4bb8-839d-adb243ab4067.jpg"
product_name = "test_product"

print("=" * 60)
print("DS_zhutu_yansetiqu 技能测试 - 模块化版本")
print("=" * 60)

# Step 1: 检测输入类型并上传图片
print("\n[1] 检测输入类型...")
print(f"    图片路径：{test_image_path}")
print(f"    文件存在：{os.path.isfile(test_image_path)}")

if os.path.isfile(test_image_path):
    print("\n[2] 检测到本地文件，转为 Base64 上传...")
    with open(test_image_path, 'rb') as f:
        file_bytes = f.read()
        base64_data = base64.b64encode(file_bytes).decode('utf-8')
        base64_full = f'data:image/jpeg;base64,{base64_data}'
    
    print(f"    文件大小：{len(file_bytes)} 字节")
    
    file_name = f'{product_name}.jpg'
    print("\n[3] 调用 kieai_uploader 模块上传...")
    upload_result = upload_to_kieai_base64(base64_full, file_name)
    
    print(f"\n    KieAI 返回结果:")
    print(f"    Success: {upload_result.get('success')}")
    
    # 检查上传结果
    if not upload_result.get('success'):
        print(f"\n[FAIL] 图床上传失败！")
        print(f"    错误：{upload_result}")
        sys.exit(1)
    
    # Step 2: 获取文件 URL
    file_url = get_file_url(upload_result)
    if not file_url:
        print(f"\n[FAIL] 无法获取文件 URL！")
        sys.exit(1)
    
    print(f"\n[OK] 上传成功！")
    print(f"    文件 URL: {file_url}")
    
    # Step 3: 调用扣子工作流
    print("\n[4] 调用扣子工作流提取颜色...")
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

    # Step 4: 解析颜色结果
    print("\n[5] 解析颜色数据...")
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
                
            # 输出最终结果
            result = {
                'success': True,
                'input_type': 'local_file',
                'uploaded_image_url': file_url,
                'colours': colours,
                'note': '文件将在 3 天后自动删除，请及时保存颜色数据'
            }
            
            print("\n" + "=" * 60)
            print("技能输出（JSON 格式）")
            print("=" * 60)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            print("\n[OK] 测试完成！")
        else:
            print("    无法解析扣子返回的 JSON")
            print(f"    原始响应：{coze_result_text[:500]}")
    except Exception as e:
        print(f"    解析错误：{e}")
        print(f"    原始响应：{coze_result_text[:500]}")
        
else:
    print(f"\n[ERROR] 文件不存在：{test_image_path}")
    sys.exit(1)
