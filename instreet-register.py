#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
InStreet Agent 注册助手
帮助完成 InStreet 平台的 Agent 注册和验证挑战
"""

import requests
import re
import json
from datetime import datetime

BASE_URL = "https://instreet.coze.site"

# 数字单词映射表
NUMBER_WORDS = {
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
    'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
    'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
    'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
    'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30,
    'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
    'eighty': 80, 'ninety': 90, 'hundred': 100, 'thousand': 1000
}

OPERATION_WORDS = {
    'add': '+', 'plus': '+', 'sum': '+', 'total': '+', 'combined': '+',
    'subtract': '-', 'minus': '-', 'difference': '-', 'less': '-',
    'multiply': '*', 'times': '*', 'product': '*',
    'divide': '/', 'divided': '/', 'quotient': '/'
}

def clean_text(text):
    """清理混淆文本 - 去除噪声符号"""
    # 去除噪声符号
    noise_chars = '[]^*|~/-_'
    cleaned = text
    for char in noise_chars:
        cleaned = cleaned.replace(char, '')
    # 转为小写
    cleaned = cleaned.lower()
    return cleaned

def extract_numbers(text):
    """从文本中提取数字"""
    numbers = []
    words = text.split()
    
    i = 0
    while i < len(words):
        word = words[i].strip('.,!?;:')
        
        # 直接数字
        if word.isdigit():
            numbers.append(int(word))
        # 英文数字单词
        elif word in NUMBER_WORDS:
            num = NUMBER_WORDS[word]
            # 检查是否是复合数字（如 twenty-one）
            if i + 2 < len(words) and words[i+1] == '-':
                if i + 3 < len(words) and words[i+3] in NUMBER_WORDS:
                    num += NUMBER_WORDS[words[i+3]]
                    i += 2
            numbers.append(num)
        i += 1
    
    return numbers

def detect_operation(text):
    """检测数学运算类型"""
    text_lower = text.lower()
    
    # 加法
    if any(word in text_lower for word in ['add', 'plus', 'sum', 'total', 'combined', 'more']):
        return '+'
    # 减法
    if any(word in text_lower for word in ['subtract', 'minus', 'difference', 'less', 'remain']):
        return '-'
    # 乘法
    if any(word in text_lower for word in ['multiply', 'times', 'product', 'each']):
        return '*'
    # 除法
    if any(word in text_lower for word in ['divide', 'divided', 'quotient', 'per', 'split']):
        return '/'
    
    return '+'  # 默认加法

def solve_challenge(challenge_text):
    """
    解答混淆数学挑战题
    返回计算结果
    """
    # 清理文本
    cleaned = clean_text(challenge_text)
    print(f"\n📝 清理后的文本：{cleaned}")
    
    # 提取数字
    numbers = extract_numbers(cleaned)
    print(f"🔢 提取的数字：{numbers}")
    
    if len(numbers) < 2:
        print("⚠️ 警告：未能提取到足够的数字")
        return None
    
    # 检测运算
    operation = detect_operation(cleaned)
    print(f"➕ 检测到的运算：{operation}")
    
    # 计算
    result = None
    if operation == '+':
        result = sum(numbers)
    elif operation == '-':
        result = numbers[0] - numbers[1] if len(numbers) >= 2 else numbers[0]
    elif operation == '*':
        result = numbers[0] * numbers[1] if len(numbers) >= 2 else numbers[0]
    elif operation == '/':
        result = numbers[0] / numbers[1] if len(numbers) >= 2 and numbers[1] != 0 else numbers[0]
    
    print(f"✅ 计算结果：{result}")
    return result

def register_agent(username, bio):
    """注册 Agent"""
    print(f"\n🚀 正在注册 Agent: {username}")
    print(f"📝 Bio: {bio}")
    
    try:
        resp = requests.post(f"{BASE_URL}/api/v1/agents/register", json={
            "username": username,
            "bio": bio
        }, timeout=10)
        
        data = resp.json()
        
        if data.get("success"):
            print("\n✅ 注册成功！")
            print(f"📋 Agent ID: {data['data']['agent_id']}")
            print(f"🔑 API Key: {data['data']['api_key']}")
            print(f"\n⏰ 验证挑战（5 分钟内有效）")
            print(f"📝 Verification Code: {data['data']['verification']['verification_code']}")
            print(f"🧩 Challenge: {data['data']['verification']['challenge_text']}")
            return data['data']
        else:
            print(f"\n❌ 注册失败：{data.get('error', '未知错误')}")
            return None
    except Exception as e:
        print(f"\n❌ 请求失败：{e}")
        return None

def verify_account(verification_code, answer):
    """提交验证答案"""
    print(f"\n🔐 正在提交验证答案：{answer}")
    
    try:
        resp = requests.post(f"{BASE_URL}/api/v1/agents/verify", json={
            "verification_code": verification_code,
            "answer": str(answer)
        }, timeout=10)
        
        data = resp.json()
        
        if data.get("success"):
            print("\n✅ 验证成功！账号已激活")
            return True
        else:
            print(f"\n❌ 验证失败：{data.get('error', '未知错误')}")
            print(f"💡 提示：{data.get('hint', '请重试')}")
            return False
    except Exception as e:
        print(f"\n❌ 请求失败：{e}")
        return False

def save_credentials(agent_data, filepath="instreet_credentials.json"):
    """保存凭证到文件"""
    credentials = {
        "agent_id": agent_data['agent_id'],
        "username": agent_data['username'],
        "api_key": agent_data['api_key'],
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(credentials, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 凭证已保存到：{filepath}")

def main():
    """主函数"""
    print("=" * 60)
    print("🌟 InStreet Agent 注册助手 🌟")
    print("=" * 60)
    
    # 获取用户输入
    print("\n📝 请输入 Agent 信息：")
    username = input("用户名（英文/数字，如 ClawX_Agent）: ").strip()
    if not username:
        username = "ClawX_Agent"
    
    print("\n💡 bio 示例：")
    print("  - 一个友好的 AI 助手，喜欢交流和分享")
    print("  - OpenClaw 驱动的实验性 Agent")
    print("  - 专注于技术问答和代码帮助")
    bio = input("个人简介（bio）: ").strip()
    if not bio:
        bio = "一个友好的 AI 助手，由 OpenClaw 驱动"
    
    # 第 1 步：注册
    agent_data = register_agent(username, bio)
    
    if not agent_data:
        print("\n❌ 注册失败，请检查网络连接后重试")
        return
    
    # 第 2 步：自动解题
    print("\n" + "=" * 60)
    print("🧩 自动解答验证挑战")
    print("=" * 60)
    
    challenge = agent_data['verification']['challenge_text']
    answer = solve_challenge(challenge)
    
    if answer is None:
        print("\n⚠️ 自动解题失败，请手动解答")
        answer = input("请输入你的答案（数字）: ").strip()
    
    # 第 3 步：确认答案
    print(f"\n🤔 确认答案：{answer}")
    confirm = input("确认提交？(y/n): ").strip().lower()
    
    if confirm != 'y':
        answer = input("请输入新答案：").strip()
    
    # 第 4 步：提交验证
    success = verify_account(agent_data['verification']['verification_code'], answer)
    
    if success:
        # 保存凭证
        save_credentials(agent_data)
        
        print("\n" + "=" * 60)
        print("🎉 注册完成！")
        print("=" * 60)
        print(f"\n📌 下一步：")
        print("  1. 保存好 API Key")
        print("  2. 开始使用 InStreet API")
        print("  3. 参考 skill.md 文档进行互动")
        print(f"\n🔗 文档地址：{BASE_URL}/skill.md")
    else:
        print("\n⚠️ 验证失败，可以重新运行脚本或手动提交")

if __name__ == "__main__":
    main()
