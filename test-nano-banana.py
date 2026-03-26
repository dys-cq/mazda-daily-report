#!/usr/bin/env python3
import os
import sys
import requests
import base64
import json
from pathlib import Path

# API Key
api_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyA0V5TfSijQoWaWMT-p5Rb1kL5rWoHOknM')

# 提示词 - 使用英文效果更好
prompt = '''Flat vector illustration, panoramic banner 16:9 aspect ratio, 2.5D isometric view. 
Cream beige background, black uniform monoline outline, geometric simplification style. 
Decorative elements: pill-shaped clouds, radiating sun rays, small dots and stars. 
Color palette: coral red, mint green, mustard yellow, burnt orange, rock blue. 
Toy model cute aesthetic, coloring book line art style, no gradients, no 3D rendering. 
Central blank area reserved for text overlay.
Professional infographic background, clean and minimal.'''

url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent?key={api_key}'

headers = {'Content-Type': 'application/json'}

data = {
    'contents': [{'role': 'user', 'parts': [{'text': prompt}]}],
    'generationConfig': {
        'responseModalities': ['IMAGE'],
        'imageConfig': {
            'aspectRatio': '16:9',
            'imageSize': '2K'
        }
    }
}

print('[INFO] 正在生成图片...')
print(f'[INFO] 提示词：{prompt[:80]}...')
print('[INFO] 比例：16:9')
print('[INFO] 质量：2K')
print()

try:
    response = requests.post(url, json=data, headers=headers, timeout=120)
    print(f'[INFO] 状态码：{response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        
        # 解析响应
        candidates = result.get('candidates', [])
        if candidates:
            parts = candidates[0].get('content', {}).get('parts', [])
            for part in parts:
                inline_data = part.get('inlineData')
                if inline_data:
                    image_b64 = inline_data.get('data')
                    if image_b64:
                        # 保存图片
                        output_path = Path('C:/Users/Administrator/.openclaw/workspace/swot-nano-banana.png')
                        image_bytes = base64.b64decode(image_b64)
                        with open(output_path, 'wb') as f:
                            f.write(image_bytes)
                        print(f'[SUCCESS] 图片已保存：{output_path}')
                        print(f'[INFO] 文件大小：{len(image_bytes) / 1024:.1f} KB')
                        sys.exit(0)
        
        print('[ERROR] 未找到图片数据')
        print(f'响应内容：{json.dumps(result, indent=2)[:1000]}')
        sys.exit(1)
    else:
        print(f'[ERROR] 请求失败：{response.text[:500]}')
        sys.exit(1)
        
except Exception as e:
    print(f'[ERROR] 错误：{str(e)}')
    sys.exit(1)
