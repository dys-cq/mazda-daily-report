import requests

# 图片路径
img_path = r"C:\Users\Administrator\.openclaw\media\outbound\01e73df1-9b20-49e4-9f2c-2d634e7b0098.jpg"

print("正在上传到 Catbox 图床...")
print(f"图片路径：{img_path}")

# Catbox API（无需 API Key）
try:
    with open(img_path, 'rb') as f:
        files = {'fileToUpload': f}
        response = requests.post(
            'https://catbox.moe/user/api.php',
            data={'reqtype': 'fileupload'},
            files=files,
            timeout=30
        )
    
    if response.status_code == 200:
        image_url = response.text.strip()
        print(f"\n[OK] 上传成功！")
        print(f"图片 URL: {image_url}")
    else:
        print(f"\n[FAIL] 上传失败：{response.status_code}")
        print(f"返回内容：{response.text}")
except Exception as e:
    print(f"\n[ERROR] 异常：{e}")
