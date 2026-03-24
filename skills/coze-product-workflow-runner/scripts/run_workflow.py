#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

try:
    import pdfplumber  # type: ignore
    HAS_PDF = True
except Exception:
    HAS_PDF = False

try:
    import docx  # type: ignore
    HAS_DOCX = True
except Exception:
    HAS_DOCX = False

DEFAULT_WORKFLOW_ID = "7619646482521538606"
DEFAULT_PRODUCT_NAME = "酷洛菲黑松露润浸洁面乳"
DEFAULT_URL = "https://api.coze.cn/v1/workflow/stream_run"


def load_env_from_openclaw():
    env_path = Path(r"C:\Users\Administrator\.openclaw\.env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def extract_text_from_docx_xml(file_path: Path) -> str:
    with zipfile.ZipFile(file_path, 'r') as zf:
        with zf.open('word/document.xml') as fh:
            tree = ET.parse(fh)
            root = tree.getroot()
            texts = []
            for elem in root.iter():
                if elem.text and elem.text.strip():
                    texts.append(elem.text.strip())
                if elem.tail and elem.tail.strip():
                    texts.append(elem.tail.strip())
            return "\n".join(texts)


def extract_text_from_file(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    ext = path.suffix.lower()
    if ext == ".txt":
        for enc in ("utf-8", "utf-8-sig", "gbk", "gb2312"):
            try:
                return path.read_text(encoding=enc)
            except UnicodeDecodeError:
                continue
        raise ValueError(f"Unable to decode txt file: {path}")

    if ext == ".docx":
        try:
            text = extract_text_from_docx_xml(path)
            if text.strip():
                return text
        except Exception:
            pass
        if not HAS_DOCX:
            raise ImportError("python-docx not installed")
        doc = docx.Document(str(path))
        lines = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
        return "\n".join(lines)

    if ext == ".pdf":
        if not HAS_PDF:
            raise ImportError("pdfplumber not installed")
        chunks = []
        with pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                if text.strip():
                    chunks.append(text)
        return "\n\n".join(chunks)

    raise ValueError(f"Unsupported file format: {ext}. Only .docx .pdf .txt are supported.")


def infer_product_name(file_path: str) -> str:
    stem = Path(file_path).stem
    stem = re.sub(r"[_\-]+", " ", stem)
    chinese_parts = re.findall(r"[\u4e00-\u9fffA-Za-z0-9]+", stem)
    if chinese_parts:
        candidate = "".join(chinese_parts).strip()
        if candidate:
            return candidate
    return DEFAULT_PRODUCT_NAME


def load_sellpoints(raw_text: str | None, raw_file: str | None) -> str:
    if raw_text:
        return raw_text.strip()
    if not raw_file:
        raise ValueError("sellpoints is required: provide --sellpoints or --sellpoints-file")

    path = Path(raw_file)
    if not path.exists():
        raise FileNotFoundError(f"Sellpoints file not found: {path}")

    content = path.read_text(encoding="utf-8", errors="ignore").strip()
    if not content:
        raise ValueError("sellpoints file is empty")

    try:
        parsed = json.loads(content)
        return json.dumps(parsed, ensure_ascii=False)
    except Exception:
        return content


def parse_stream_response(text: str) -> dict:
    events = []
    current_event = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if current_event:
                events.append(current_event)
                current_event = {}
            continue
        if line.startswith("event:"):
            current_event["event"] = line[len("event:"):].strip()
        elif line.startswith("data:"):
            payload = line[len("data:"):].strip()
            try:
                current_event.setdefault("data", []).append(json.loads(payload))
            except Exception:
                current_event.setdefault("data", []).append(payload)

    if current_event:
        events.append(current_event)

    flattened = []
    for ev in events:
        for item in ev.get("data", []):
            flattened.append(item)

    parsed_json = None
    for item in reversed(flattened):
        if isinstance(item, dict):
            parsed_json = item
            break
        if isinstance(item, str):
            try:
                parsed_json = json.loads(item)
                break
            except Exception:
                continue

    return {
        "events": events,
        "parsed_json": parsed_json,
        "raw_text": text,
    }


def call_workflow(url: str, api_token: str, workflow_id: str, product_information: str, sellpoints: str, product_name: str) -> dict:
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "workflow_id": workflow_id,
        "parameters": {
            "Product_Information": product_information,
            "sellpoints": sellpoints,
            "Product_name": product_name,
        },
    }

    response = requests.post(url, headers=headers, json=payload, timeout=180)
    result = {
        "status_code": response.status_code,
        "headers": dict(response.headers),
    }

    content_type = response.headers.get("Content-Type", "")
    body_text = response.text
    result["body_text"] = body_text

    try:
        result["body_json"] = response.json()
    except Exception:
        result["body_json"] = None

    if "text/event-stream" in content_type or body_text.strip().startswith("event:"):
        result["stream"] = parse_stream_response(body_text)

    response.raise_for_status()
    return result


def main():
    load_env_from_openclaw()

    parser = argparse.ArgumentParser(description="Run Coze product workflow with local document + sellpoints")
    parser.add_argument("--file", required=True, help="Path to product information file (.docx/.pdf/.txt)")
    parser.add_argument("--sellpoints", help="Sellpoints text, usually from DS_zhutu_Branch2 result")
    parser.add_argument("--sellpoints-file", help="Path to sellpoints file (txt/json/md)")
    parser.add_argument("--product-name", help="Explicit product name override")
    parser.add_argument("--workflow-id", default=os.environ.get("COZE_PRODUCT_WORKFLOW_ID", DEFAULT_WORKFLOW_ID))
    parser.add_argument("--api-token", default=os.environ.get("COZE_API_TOKEN"))
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("-o", "--output", help="Output JSON path")
    args = parser.parse_args()

    if not args.api_token:
        raise ValueError("Missing API token. Use --api-token or set COZE_API_TOKEN in C:\\Users\\Administrator\\.openclaw\\.env")

    product_information = extract_text_from_file(args.file)
    sellpoints = load_sellpoints(args.sellpoints, args.sellpoints_file)
    product_name = args.product_name or infer_product_name(args.file) or DEFAULT_PRODUCT_NAME

    result = call_workflow(
        url=args.url,
        api_token=args.api_token,
        workflow_id=args.workflow_id,
        product_information=product_information,
        sellpoints=sellpoints,
        product_name=product_name,
    )

    output = {
        "input": {
            "file": str(Path(args.file).resolve()),
            "workflow_id": args.workflow_id,
            "product_name": product_name,
            "product_information_length": len(product_information),
            "sellpoints_length": len(sellpoints),
        },
        "result": result,
    }

    text = json.dumps(output, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(args.output)
    else:
        print(text)


if __name__ == "__main__":
    main()
