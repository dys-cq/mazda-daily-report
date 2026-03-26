#!/usr/bin/env python3
"""
Parse and display ingredients from Coze workflow JSON output.

Usage:
  uv run python show_ingredients.py result.json
"""

import json
import sys
import re

def parse_json_file(file_path: str):
    """Parse JSON file from Coze workflow output."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract nested JSON from 'data' field
    inner_data = json.loads(data['data'])
    sellpoints = json.loads(inner_data['sellpoints'])
    
    # Get content (try different keys)
    content = sellpoints.get('修正后的最终内容', 
              sellpoints.get('检查结果分析', 
              sellpoints.get('content', '')))
    
    return content, data

def extract_ingredients(content: str) -> dict:
    """Extract ingredients from content."""
    ingredients = {
        'core': [],
        'full': [],
        'trace': []
    }
    
    # Extract core ingredients
    core_match = re.search(r'\*\*核心功效成分\*\*: (.+?)(?:\\n|\*\*)', content)
    if core_match:
        ingredients['core'] = [i.strip() for i in core_match.group(1).split('、') if i.strip()]
    
    # Extract full ingredients list
    full_match = re.search(r'\*\*全成分列表\*\*:\\n(.+?)(?:\\n 其他微量成分|\\n\\n|$)', content, re.DOTALL)
    if full_match:
        ingredients['full'] = [i.strip() for i in full_match.group(1).split('、') if i.strip()]
    
    # Extract trace ingredients
    trace_match = re.search(r'其他微量成分：(.+?)(?:\\n|$)', content, re.DOTALL)
    if trace_match:
        ingredients['trace'] = [i.strip() for i in trace_match.group(1).split('、') if i.strip()]
    
    return ingredients

def display_ingredients(ingredients: dict, execute_id: str):
    """Display ingredients in a readable format."""
    print("=" * 70)
    print("产品成分信息")
    print("=" * 70)
    print()
    
    print(f"【核心功效成分】 ({len(ingredients['core'])} 个)")
    print("-" * 70)
    for i, ing in enumerate(ingredients['core'], 1):
        print(f"  {i}. {ing}")
    print()
    
    print(f"【全成分列表】 ({len(ingredients['full'])} 个)")
    print("-" * 70)
    for i, ing in enumerate(ingredients['full'], 1):
        print(f"  {i:2d}. {ing}")
    print()
    
    print(f"【微量成分】 ({len(ingredients['trace'])} 个)")
    print("-" * 70)
    for ing in ingredients['trace']:
        print(f"  • {ing}")
    print()
    
    print("=" * 70)
    print(f"执行 ID: {execute_id}")
    print(f"总计：{len(ingredients['core']) + len(ingredients['full']) + len(ingredients['trace'])} 种成分")
    print("=" * 70)

def main():
    if len(sys.argv) < 2:
        print("Usage: uv run python show_ingredients.py <result.json>")
        print("Example: uv run python show_ingredients.py 产品分析报告.json")
        return 1
    
    file_path = sys.argv[1]
    
    try:
        content, raw_data = parse_json_file(file_path)
        ingredients = extract_ingredients(content)
        execute_id = raw_data.get('execute_id', 'N/A')
        
        display_ingredients(ingredients, execute_id)
        
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
