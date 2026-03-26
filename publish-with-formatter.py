# -*- coding: utf-8 -*-
"""
直接使用 wechat-article-formatter 转换并发布到微信公众号
"""
import sys
import os
sys.path.insert(0, r'C:\Users\Administrator\.claude\skills\wechat-article-formatter\scripts')

from markdown_to_html import WeChatHTMLConverter
import requests
import json
import re

# 配置
MD_FILE = r'C:\Users\Administrator\.openclaw\workspace\mazda-skyactiv-article.md'
OUTPUT_FILE = r'C:\Users\Administrator\.openclaw\workspace\mazda-wechat-final.html'
APP_ID = 'wx28846bfb1ba4ab2c'
APP_SECRET = '812120a5fe5fcd89a6103a535e79a02d'

# 1. 获取 access_token
print("Getting access_token...")
token_url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}'
token_resp = requests.get(token_url)
token_data = token_resp.json()
access_token = token_data.get('access_token')
if not access_token:
    print(f"Failed to get token: {token_data}")
    sys.exit(1)
print(f"OK Token: {access_token[:20]}...")

# 2. 转换 Markdown 为 HTML
print("\nConverting Markdown...")
converter = WeChatHTMLConverter(theme='tech')
with open(MD_FILE, 'r', encoding='utf-8') as f:
    markdown_content = f.read()

html_content = converter.convert(markdown_content)

# 移除 H1 标题和注释
html_content = re.sub(r'<h1[^>]*>.*?</h1>', '', html_content)
html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)

# 提取 body 内容
body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL)
if body_match:
    content = body_match.group(1).strip()
else:
    content = html_content

# 保存 HTML 用于预览
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"OK HTML saved: {OUTPUT_FILE}")
print(f"Content length: {len(content)} chars")

# 3. 获取封面图 media_id
print("\nGetting cover image...")
material_url = f'https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={access_token}'
material_resp = requests.post(material_url, json={'type': 'image', 'offset': 0, 'count': 1})
material_data = material_resp.json()
thumb_media_id = ''
if material_data.get('item'):
    thumb_media_id = material_data['item'][0]['media_id']
    print(f"OK Using media_id: {thumb_media_id}")

# 4. 发布到草稿箱
print("\nPublishing to draft...")
draft_url = f'https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}'

# 短标题
short_title = "Mazda Skyactiv"

# 直接使用字典，让 requests 处理 JSON 编码（确保 UTF-8）
payload = {
    "articles": [
        {
            "title": short_title,
            "author": "Nice 哥",
            "digest": "马自达创驰蓝天技术深度解析",
            "content": content,  # 直接使用字符串，不要手动 JSON 编码
            "thumb_media_id": thumb_media_id,
            "need_open_comment": 1,
            "only_fans_can_comment": 0
        }
    ]
}

# 使用 json.dumps 确保正确的 UTF-8 编码
json_payload = json.dumps(payload, ensure_ascii=False).encode('utf-8')

headers = {
    'Content-Type': 'application/json; charset=utf-8'
}

draft_resp = requests.post(draft_url, data=json_payload, headers=headers)
draft_data = draft_resp.json()

if draft_data.get('media_id'):
    print(f"\nOK Published successfully!")
    print(f"Media ID: {draft_data['media_id']}")
    print(f"\nView at: https://mp.weixin.qq.com/cgi-bin/appmsgpublish?sub=draft")
else:
    print(f"\nFailed: {draft_data}")
