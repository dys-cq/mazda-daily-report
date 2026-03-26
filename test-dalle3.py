#!/usr/bin/env python3
import os
import sys
import requests
import base64
import json
from pathlib import Path

# API Key
api_key = os.environ.get('OPENAI_API_KEY', 'sk-proj-xxx')

# 提示词
prompt = '''Flat vector illustration, panoramic banner 16:9 aspect ratio, 2.5D isometric view. 
Cream beige background, black uniform monoline outline, geometric simplification style. 
Decorative elements: pill-shaped clouds, radiating sun rays, small dots and stars. 
Color palette: coral red, mint green, mustard yellow, burnt orange, rock blue. 
Toy model cute aesthetic, coloring book line art style, no gradients, no 3D rendering. 
Central blank area reserved for text overlay.
Professional infographic background, clean and minimal.'''

url = 'https://api.openai.com/v1/images/generations'

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

data = {
    'model': 'dall-e-3',
    'prompt': prompt,
    'n': 1,
    'size': '1792x1024',
    'quality': 'standard',
    'response_format': 'b64_json'
}

print('[INFO] 正在使用 DALL-E 3 生成图片...')
print(f'[INFO] 提示词：{prompt[:80]}...')
print('[INFO] 尺寸：1792x1024 (16:9)')
print()

try:
    response = requests.post(url, json=data, headers=headers, timeout=120)
    print(f'[INFO] 状态码：{response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        
        if 'data' in result and len(result['data']) > 0:
            image_b64 = result['data'][0].get('b64_json')
            if image_b64:
                output_path = Path('C:/Users/Administrator/.openclaw/workspace/swot-dalle3.png')
                image_bytes = base64.b64decode(image_b64)
                with open(output_path, 'wb') as f:
                    f.write(image_bytes)
                print(f'[SUCCESS] 图片已保存：{output_path}')
                print(f'[INFO] 文件大小：{len(image_bytes) / 1024:.1f} KB')
                sys.exit(0)
        
        print(f'[ERROR] 未找到图片数据：{result}')
        sys.exit(1)
    else:
        print(f'[ERROR] 请求失败：{response.text[:500]}')
        sys.exit(1)
        
except Exception as e:
    print(f'[ERROR] 错误：{str(e)}')
    sys.exit(1)
