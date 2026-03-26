import requests, base64, json, sys, os, re
from pathlib import Path
from dotenv import load_dotenv

# 获取技能根目录
skill_root = Path(__file__).parent / 'skills' / 'DS_zhutu_yansetiqu'

# 加载.env 文件
env_path = skill_root / '.env'
load_dotenv(dotenv_path=env_path)

# 从环境变量读取配置
KIEAI_API_KEY = os.getenv('KIEAI_API_KEY')
COZE_API_KEY = os.getenv('COZE_API_KEY')
COZE_WORKFLOW_ID = os.getenv('COZE_WORKFLOW_ID')

# 测试图片路径
test_image_path = r"C:\Users\Administrator\.openclaw\media\outbound\fc28b1fa-ff5d-4bb8-839d-adb243ab4067.jpg"
product_name = "test_product"

print("=" * 60)
print("DS_zhutu_yansetiqu 技能测试 - 环境变量版本")
print("=" * 60)

# 验证配置
print("\n[配置检查]")
print(f"    KIEAI_API_KEY: {'[OK] 已配置' if KIEAI_API_KEY else '[FAIL] 未配置'}")
print(f"    COZE_API_KEY: {'[OK] 已配置' if COZE_API_KEY else '[FAIL] 未配置'}")
print(f"    COZE_WORKFLOW_ID: {'[OK] 已配置' if COZE_WORKFLOW_ID else '[FAIL] 未配置'}")

if not KIEAI_API_KEY or not COZE_API_KEY or not COZE_WORKFLOW_ID:
    print("\n[ERROR] 配置不完整，请检查.env 文件")
    sys.exit(1)

# 添加 scripts 目录到 Python 路径
scripts_dir = skill_root / 'scripts'
sys.path.insert(0, str(scripts_dir))

# 导入 KieAI 上传模块
from kieai_uploader import upload_to_kieai_base64, get_file_url

# Step 1: 上传图片
print(f"\n[1] 读取图片并上传...")
with open(test_image_path, 'rb') as f:
    file_bytes = f.read()
    base64_data = base64.b64encode(file_bytes).decode('utf-8')
    base64_full = f'data:image/jpeg;base64,{base64_data}'

file_name = f'{product_name}.jpg'
upload_result = upload_to_kieai_base64(base64_full, file_name)

if not upload_result.get('success'):
    print(f"    [FAIL] 上传失败：{upload_result}")
    sys.exit(1)

file_url = get_file_url(upload_result)
print(f"    [OK] 上传成功")
print(f"    文件 URL: {file_url}")

# Step 2: 调用扣子工作流
print(f"\n[2] 调用扣子工作流 (ID: {COZE_WORKFLOW_ID})...")
coze_headers = {
    'Authorization': f'Bearer {COZE_API_KEY}',
    'Content-Type': 'application/json'
}

coze_body = {
    'workflow_id': COZE_WORKFLOW_ID,
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
except Exception as e:
    print(f"    解析错误：{e}")
