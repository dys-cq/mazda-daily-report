#!/usr/bin/env python3
import os
import sys
import requests
import base64
import json
import time
from pathlib import Path

# API Key - 阿里云 DashScope
api_key = os.environ.get('DASHSCOPE_API_KEY', '')

if not api_key:
    print('[ERROR] 请设置环境变量 DASHSCOPE_API_KEY')
    sys.exit(1)

# 提示词
prompt = '''扁平化矢量插画，全景横幅 16:9 比例，2.5D 等轴测视角。
米色奶油色背景，黑色统一轮廓线，几何化简风格。
装饰元素：药丸形云朵、放射状阳光、小圆点和星星。
配色：珊瑚红、薄荷绿、芥末黄、赭石色、岩石蓝。
玩具模型可爱风格，填色书线稿风格，无渐变无 3D 渲染。
中央留白区域用于文字叠加。
专业信息图背景，简洁 minimal。'''

url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}',
    'X-DashScope-WorkSpace': 'generation'
}

# 通义万相 API
data = {
    'model': 'wanx-v1',
    'input': {
        'prompt': prompt
    },
    'parameters': {
        'size': '1280x720',
        'n': 1,
        'style': '<cartoon>'
    }
}

print('[INFO] 正在使用阿里云通义万相生成图片...')
print(f'[INFO] 提示词：{prompt[:50]}...')
print('[INFO] 尺寸：1280x720 (16:9)')
print()

try:
    # 第一步：提交任务
    response = requests.post(url, json=data, headers=headers, timeout=60)
    print(f'[INFO] 提交状态码：{response.status_code}')
    
    if response.status_code != 200:
        print(f'[ERROR] 提交失败：{response.text[:500]}')
        sys.exit(1)
    
    result = response.json()
    task_id = result.get('output', {}).get('task_id')
    
    if not task_id:
        print(f'[ERROR] 未获取到 task_id: {result}')
        sys.exit(1)
    
    print(f'[INFO] Task ID: {task_id}')
    
    # 第二步：轮询任务状态
    task_url = f'https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}'
    
    max_attempts = 30
    for i in range(max_attempts):
        time.sleep(2)
        
        task_response = requests.get(task_url, headers=headers, timeout=30)
        task_result = task_response.json()
        
        status = task_result.get('output', {}).get('task_status', 'UNKNOWN')
        print(f'[INFO] 轮询 {i+1}/{max_attempts}: 状态={status}')
        
        if status == 'SUCCEEDED':
            # 获取图片 URL
            img_url = task_result.get('output', {}).get('results', [{}])[0].get('url')
            if img_url:
                print(f'[INFO] 图片 URL: {img_url}')
                
                # 下载图片
                img_response = requests.get(img_url, timeout=30)
                if img_response.status_code == 200:
                    output_path = Path('C:/Users/Administrator/.openclaw/workspace/swot-dashscope.png')
                    with open(output_path, 'wb') as f:
                        f.write(img_response.content)
                    print(f'[SUCCESS] 图片已保存：{output_path}')
                    print(f'[INFO] 文件大小：{len(img_response.content) / 1024:.1f} KB')
                    sys.exit(0)
            break
        elif status in ['FAILED', 'CANCELED']:
            print(f'[ERROR] 任务失败：{task_result}')
            sys.exit(1)
    
    print('[ERROR] 任务超时')
    sys.exit(1)
    
except Exception as e:
    print(f'[ERROR] 错误：{str(e)}')
    sys.exit(1)
