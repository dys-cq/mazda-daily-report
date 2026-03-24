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


def _looks_like_random_or_unusable_name(name: str) -> bool:
    normalized = re.sub(r"[^A-Za-z0-9]", "", name or "")
    if not normalized:
        return True
    if re.fullmatch(r"[A-Fa-f0-9]{24,}", normalized):
        return True
    if re.fullmatch(r"[A-Za-z0-9]{24,}", normalized) and not re.search(r"[\u4e00-\u9fff]", name or ""):
        return True
    return False


def infer_product_name_from_filename(file_path: str, original_filename: str | None = None) -> str | None:
    raw_name = original_filename.strip() if original_filename and original_filename.strip() else Path(file_path).name
    stem = Path(raw_name).stem.strip()

    # Normalize separators first.
    compact = re.sub(r"[_\-\s]+", "", stem)
    compact = re.sub(r"^(测试样例|测试样本|测试文件|测试文档|测试|样例|样本|示例)+", "", compact)
    compact = re.sub(r"^[A-Za-z]{1,8}\d{2,12}", "", compact)
    compact = re.sub(r"^(第?[A-Za-z0-9一二三四五六七八九十]+版)", "", compact)
    compact = compact.strip()

    product_suffixes = r"洁面乳|洁面霜|洗面奶|面膜|精华液|精华水|爽肤水|乳液|面霜|眼霜|防晒霜|洗发水|沐浴露"
    anchored_match = re.search(rf"([\u4e00-\u9fffA-Za-z0-9·（）()]{{2,60}}(?:{product_suffixes}))$", compact)
    if anchored_match:
        normalized = re.sub(r"\s+", "", anchored_match.group(1)).strip()
        normalized = re.sub(r"^(测试样例|测试样本|测试文件|测试文档|测试|样例|样本|示例)+", "", normalized)
        normalized = re.sub(r"^[A-Za-z]{1,8}\d{2,12}", "", normalized)
        normalized = normalized.strip()
        if normalized and not _looks_like_random_or_unusable_name(normalized):
            return normalized

    suffix_match = re.search(rf"([\u4e00-\u9fffA-Za-z0-9·（）()]{{2,80}}(?:{product_suffixes}))", compact)
    if suffix_match:
        normalized = re.sub(r"\s+", "", suffix_match.group(1)).strip()
        normalized = re.sub(r"^(测试样例|测试样本|测试文件|测试文档|测试|样例|样本|示例)+", "", normalized)
        normalized = re.sub(r"^[A-Za-z]{1,8}\d{2,12}", "", normalized)
        normalized = normalized.strip()
        if normalized and not _looks_like_random_or_unusable_name(normalized):
            return normalized

    chinese_chunks = re.findall(r"[\u4e00-\u9fff]+", stem)
    if chinese_chunks:
        candidate = "".join(chinese_chunks).strip()
        candidate = re.sub(r"^(测试样例|测试样本|测试文件|测试文档|测试|样例|样本|示例)+", "", candidate)
        candidate = candidate.strip()
        if candidate and not _looks_like_random_or_unusable_name(candidate):
            return candidate

    cleaned = re.sub(r"[_\-]+", " ", stem).strip()
    if cleaned and not _looks_like_random_or_unusable_name(cleaned) and re.search(r"[\u4e00-\u9fff]", cleaned):
        return cleaned
    return None


def infer_product_name_from_content(content: str) -> str | None:
    lines = [line.strip() for line in content.splitlines() if line.strip()]

    labeled_patterns = [
        r"(?:产品名称|品名|名称)[:：]\s*([\u4e00-\u9fffA-Za-z0-9·（）()\-\s]{2,60})",
        r"^([\u4e00-\u9fffA-Za-z0-9·（）()\-\s]{4,60}(?:洁面乳|洁面霜|洗面奶|面膜|精华液|精华水|爽肤水|乳液|面霜|眼霜|防晒霜|洗发水|沐浴露))$",
    ]
    for line in lines[:80]:
        for pattern in labeled_patterns:
            match = re.search(pattern, line)
            if match:
                candidate = re.sub(r"\s+", "", match.group(1)).strip("：:;；，,. ")
                if candidate and not _looks_like_random_or_unusable_name(candidate):
                    return candidate

    joined = "\n".join(lines[:120])
    generic_pattern = r"([\u4e00-\u9fffA-Za-z0-9·（）()\-]{4,60}(?:洁面乳|洁面霜|洗面奶|面膜|精华液|精华水|爽肤水|乳液|面霜|眼霜|防晒霜|洗发水|沐浴露))"
    match = re.search(generic_pattern, joined)
    if match:
        candidate = re.sub(r"\s+", "", match.group(1)).strip()
        if candidate and not _looks_like_random_or_unusable_name(candidate):
            return candidate
    return None


def resolve_product_name(file_path: str, product_information: str, explicit_product_name: str | None, original_filename: str | None = None) -> tuple[str | None, str]:
    if explicit_product_name and explicit_product_name.strip():
        return explicit_product_name.strip(), "explicit"

    from_filename = infer_product_name_from_filename(file_path, original_filename=original_filename)
    if from_filename:
        return from_filename, "filename"

    from_content = infer_product_name_from_content(product_information)
    if from_content:
        return from_content, "content"

    return None, "missing"


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
    parser.add_argument("--original-filename", help="Original uploaded/display filename, used for Product_name inference when local path was renamed")
    parser.add_argument("--workflow-id", default=os.environ.get("COZE_PRODUCT_WORKFLOW_ID", DEFAULT_WORKFLOW_ID))
    parser.add_argument("--api-token", default=os.environ.get("COZE_API_TOKEN"))
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("-o", "--output", help="Output JSON path")
    args = parser.parse_args()

    if not args.api_token:
        raise ValueError("Missing API token. Use --api-token or set COZE_API_TOKEN in C:\\Users\\Administrator\\.openclaw\\.env")

    product_information = extract_text_from_file(args.file)
    sellpoints = load_sellpoints(args.sellpoints, args.sellpoints_file)
    product_name, product_name_source = resolve_product_name(args.file, product_information, args.product_name, original_filename=args.original_filename)
    if not product_name:
        raise ValueError(
            "Unable to identify Product_name. Tried: original/display filename -> local filename -> document content. "
            "Please provide --product-name explicitly."
        )

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
            "product_name_source": product_name_source,
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
