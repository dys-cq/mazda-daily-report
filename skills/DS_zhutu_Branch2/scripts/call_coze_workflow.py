#!/usr/bin/env python3
"""
Call Coze Workflow API to process product information.

Enhanced version with:
- Markdown output format (default)
- Complete ingredient extraction
- Structured product information
"""

import os
import sys
import json
import requests
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False


def extract_text_from_docx_xml(file_path: str) -> str:
    """Extract text from DOCX by parsing internal XML directly."""
    try:
        with zipfile.ZipFile(file_path, 'r') as z:
            with z.open('word/document.xml') as f:
                tree = ET.parse(f)
                root = tree.getroot()
                texts = []
                for elem in root.iter():
                    if elem.text and elem.text.strip():
                        texts.append(elem.text.strip())
                    if elem.tail and elem.tail.strip():
                        texts.append(elem.tail.strip())
                return '\n'.join(texts)
    except Exception as e:
        print(f"XML extraction failed: {e}", file=sys.stderr)
        return None


def extract_text_from_file(file_path: str) -> str:
    """Extract text content from various file formats."""
    file_path = Path(file_path)
    extension = file_path.suffix.lower()
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if extension == '.txt':
        for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        raise ValueError("Unable to decode file")
    
    elif extension == '.docx':
        text = extract_text_from_docx_xml(file_path)
        if text:
            return text
        if not HAS_DOCX:
            raise ImportError("python-docx not installed")
        doc = docx.Document(file_path)
        return '\n'.join([p.text for p in doc.paragraphs if p.text and p.text.strip()])
    
    elif extension == '.pdf':
        if not HAS_PDFPLUMBER:
            raise ImportError("pdfplumber not installed")
        text_content = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
        return '\n'.join(text_content)
    
    else:
        raise ValueError(f"Unsupported format: {extension}")


def extract_product_name_from_filename(file_path: str) -> str:
    """Extract product name from filename."""
    file_name = Path(file_path).stem
    chinese_chars = re.findall(r'[\u4e00-\u9fa5]+', file_name)
    if chinese_chars:
        return ''.join(chinese_chars)
    return "酷洛菲黑松露润浸洁面乳"


def call_coze_workflow(product_info: str, product_name: str, workflow_id: str, api_token: str) -> dict:
    """Call Coze workflow API."""
    url = 'https://api.coze.cn/v1/workflow/run'
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "workflow_id": workflow_id,
        "parameters": {
            "Product_Information": product_info,
            "Product_name": product_name
        }
    }
    
    print(f"Calling Coze API...", file=sys.stderr)
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    print(f"Response status: {response.status_code}", file=sys.stderr)
    return response.json()


def parse_workflow_result(api_response: dict) -> dict:
    """Parse workflow result and extract structured data."""
    data = json.loads(api_response['data'])
    result = json.loads(data['sellpoints'])
    
    # Get content from either key
    content = result.get('修正后的最终内容', result.get('检查结果分析', ''))
    
    # Get review status and issues
    review_status = result.get('是否通过审查', result.get('是否通过审核', ''))
    issues = result.get('问题清单', result.get('问题列表', []))
    
    # Handle both string and dict content
    if isinstance(content, dict):
        # Content is already structured
        content['是否通过审查'] = review_status
        content['问题清单'] = issues
        return {
            'content': content,
            'sections': content,
            'review_status': review_status,
            'issues': issues,
            'execute_id': api_response.get('execute_id', ''),
            'usage': api_response.get('usage', {}),
            'debug_url': api_response.get('debug_url', '')
        }
    
    # Parse sections from string content
    sections = {}
    current_section = None
    current_content = []
    
    for line in content.split('\n'):
        if line.startswith('###'):
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = line.replace('###', '').strip()
            current_content = []
        elif current_section:
            current_content.append(line)
    
    if current_section:
        sections[current_section] = '\n'.join(current_content)
    
    return {
        'content': content,
        'sections': sections,
        'review_status': review_status,
        'issues': issues,
        'execute_id': api_response.get('execute_id', ''),
        'usage': api_response.get('usage', {}),
        'debug_url': api_response.get('debug_url', '')
    }


def generate_markdown_report(parsed_data: dict, output_path: str = None):
    """Generate Markdown format report."""
    sections = parsed_data['sections']
    
    md_content = f"""# 产品信息分析报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**执行 ID**: {parsed_data['execute_id']}

---

"""
    
    # Product Name
    if '产品全称' in sections:
        md_content += f"## 1. 产品全称\n\n{sections['产品全称']}\n\n"
    
    # Ingredients
    if '产品成分信息' in sections:
        md_content += f"## 2. 产品成分信息\n\n{sections['产品成分信息']}\n\n"
    
    # Selling Points
    if '产品卖点信息' in sections:
        md_content += f"## 3. 产品卖点信息\n\n{sections['产品卖点信息']}\n\n"
    
    # Specifications
    if '产品规格信息' in sections:
        md_content += f"## 4. 产品规格信息\n\n{sections['产品规格信息']}\n\n"
    
    # Regulatory Info
    if '产品备案信息' in sections:
        md_content += f"## 5. 产品备案信息\n\n{sections['产品备案信息']}\n\n"
    
    # Usage Instructions
    if '使用说明' in sections:
        md_content += f"## 6. 使用说明\n\n{sections['使用说明']}\n\n"
    
    # Execution Info
    md_content += f"""---

## 执行信息

| 项目 | 数值 |
|------|------|
| Token 消耗 | {parsed_data['usage'].get('token_count', 0)} |
| 输入 Token | {parsed_data['usage'].get('input_count', 0)} |
| 输出 Token | {parsed_data['usage'].get('output_count', 0)} |

**调试链接**: {parsed_data['debug_url']}

---

*本报告由 coze-workflow-runner 自动生成*
"""
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"Markdown 报告已保存：{output_path}", file=sys.stderr)
    else:
        print(md_content)
    
    return md_content


def generate_ingredients_report(parsed_data: dict, output_path: str = None):
    """Generate dedicated ingredients report in Markdown."""
    sections = parsed_data['sections']
    content = parsed_data['content']
    
    # Extract ingredients using regex
    core_match = re.search(r'\*\*核心功效成分\*\*: (.+?)(?:\\\\n|$)', content)
    full_match = re.search(r'\*\*全成分列表\*\*:\\\\n(.+?)(?:\\\\n 其他微量成分|$)', content, re.DOTALL)
    trace_match = re.search(r'其他微量成分：(.+?)(?:\\\\n|$)', content, re.DOTALL)
    
    core_ingredients = []
    full_ingredients = []
    trace_ingredients = []
    
    if core_match:
        core_ingredients = [i.strip() for i in core_match.group(1).split('、') if i.strip()]
    
    if full_match:
        full_ingredients = [i.strip() for i in full_match.group(1).split('、') if i.strip()]
    
    if trace_match:
        trace_ingredients = [i.strip() for i in trace_match.group(1).split('、') if i.strip()]
    
    md_content = f"""# 产品成分信息

**产品名称**: 酷洛菲黑松露润浸洁面乳  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**执行 ID**: {parsed_data['execute_id']}

---

## 核心功效成分（{len(core_ingredients)} 个）

"""
    for i, ing in enumerate(core_ingredients, 1):
        md_content += f"{i}. ✓ {ing}\n"
    
    md_content += f"\n## 全成分列表（{len(full_ingredients)} 个）\n\n"
    for i, ing in enumerate(full_ingredients, 1):
        md_content += f"{i:2d}. {ing}\n"
    
    md_content += f"\n## 微量成分（{len(trace_ingredients)} 个）\n\n"
    for ing in trace_ingredients:
        md_content += f"• {ing}\n"
    
    md_content += f"\n---\n\n**成分统计**:\n- 核心成分：{len(core_ingredients)} 个\n- 全成分：{len(full_ingredients)} 个\n- 微量成分：{len(trace_ingredients)} 个\n- **总计**: {len(core_ingredients) + len(full_ingredients) + len(trace_ingredients)} 种\n"
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"成分报告已保存：{output_path}", file=sys.stderr)
    else:
        print(md_content)
    
    return md_content


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Call Coze workflow with product information')
    parser.add_argument('file_path', help='Path to input file (DOCX, PDF, or TXT)')
    parser.add_argument('--workflow-id', default='7619646208533250090', help='Coze workflow ID')
    parser.add_argument('--api-token', default=os.environ.get('COZE_API_TOKEN', ''), help='Coze API token')
    parser.add_argument('--output', '-o', help='Output Markdown file path')
    parser.add_argument('--ingredients', '-i', action='store_true', help='Generate ingredients-only report')
    parser.add_argument('--json', action='store_true', help='Output in JSON format instead of Markdown')
    
    args = parser.parse_args()
    
    try:
        # Extract text
        print(f"Reading file: {args.file_path}", file=sys.stderr)
        product_info = extract_text_from_file(args.file_path)
        product_name = extract_product_name_from_filename(args.file_path)
        
        # Call API
        result = call_coze_workflow(product_info, product_name, args.workflow_id, args.api_token)
        
        # Parse result
        parsed = parse_workflow_result(result)
        
        # Check review status
        review_status = parsed.get('review_status', '')
        issues = parsed.get('issues', [])
        
        # Display review status prominently
        if review_status != '是' and review_status != '通过':
            print("\n" + "=" * 70, file=sys.stderr)
            print("❌ 卖点审查未通过", file=sys.stderr)
            print("=" * 70, file=sys.stderr)
            
            if issues:
                print("\n未通过原因:", file=sys.stderr)
                if isinstance(issues, list):
                    for i, issue in enumerate(issues, 1):
                        if isinstance(issue, dict):
                            print(f"\n问题 {i}:", file=sys.stderr)
                            print(f"  位置：{issue.get('位置', issue.get('问题位置', 'N/A'))}", file=sys.stderr)
                            print(f"  类型：{issue.get('问题类型', 'N/A')}", file=sys.stderr)
                            print(f"  描述：{issue.get('问题描述', 'N/A')}", file=sys.stderr)
                        else:
                            print(f"\n问题 {i}: {issue}", file=sys.stderr)
                else:
                    print(f"  {issues}", file=sys.stderr)
            else:
                print("\n未找到具体问题清单，请检查原始文档内容。", file=sys.stderr)
            
            print("\n💡 建议：请根据上述问题修改产品文案后，重新运行该技能。", file=sys.stderr)
            print("=" * 70 + "\n", file=sys.stderr)
        
        # Generate output
        if args.json:
            # JSON output
            print(json.dumps(parsed, ensure_ascii=False, indent=2))
        elif args.ingredients:
            # Ingredients report
            generate_ingredients_report(parsed, args.output)
        else:
            # Full Markdown report
            generate_markdown_report(parsed, args.output)
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
