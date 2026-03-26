import json
import os
import re
import time
from pathlib import Path
import sys

# Paths
workspace = Path(r"C:\Users\Administrator\.openclaw\workspace")
skill_dir = Path(r"C:\Users\Administrator\.openclaw\skills\miaoda-app-builder")
api_script = skill_dir / "scripts" / "miaoda_api.py"
secrets_env = skill_dir / ".env"
prompts_path = workspace / "miaoda_app_prompts.json"
out_path = workspace / "miaoda_app_results.jsonl"

# Load .env
if secrets_env.exists():
    raw_lines = [ln.strip() for ln in secrets_env.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.strip().startswith("#")]
    # Support either KEY=VALUE lines or a single raw key line
    for line in raw_lines:
        if "=" in line:
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k:
                os.environ.setdefault(k, v)
        else:
            # assume this is the key itself
            os.environ.setdefault("MIAODA_API_KEY", line)

if not os.environ.get("MIAODA_API_KEY"):
    raise SystemExit("MIAODA_API_KEY not found in .env or environment")

# Load prompts
items = json.loads(prompts_path.read_text(encoding="utf-8"))

# helper to strip numbering like "1. 标题"
def clean_name(name: str) -> str:
    return re.sub(r"^\s*\d+\.\s*", "", name).strip()

# import miaoda_api for direct call
sys.path.insert(0, str(skill_dir / "scripts"))
import miaoda_api  # type: ignore

results = []

with out_path.open("w", encoding="utf-8") as fout:
    for idx, item in enumerate(items, 1):
        raw_name = item.get("name", "")
        name = clean_name(raw_name)
        prompt = item.get("prompt", "")
        # replace name in prompt if numbered
        if name and raw_name != name:
            prompt = prompt.replace(f"『{raw_name}』", f"『{name}』")
        try:
            chat_result = miaoda_api.chat_no_stream(
                base_url=miaoda_api.DEFAULT_BASE_URL,
                api_key=os.environ["MIAODA_API_KEY"],
                text=prompt,
                context_id="",
                app_id=None,
                query_mode="deep_mode",
                input_field_type="web",
            )
            # extract appId/conversationId
            meta = (
                chat_result
                .get("result", {})
                .get("status", {})
                .get("message", {})
                .get("metadata", {})
            )
            app_id = meta.get("appId")
            conv_id = meta.get("conversationId")
            rec = {
                "index": idx,
                "name": name,
                "appId": app_id,
                "conversationId": conv_id,
            }
            results.append(rec)
            fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fout.flush()
        except Exception as e:
            rec = {
                "index": idx,
                "name": name,
                "error": str(e),
            }
            results.append(rec)
            fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fout.flush()
        time.sleep(2)  # rate limiting

print(f"done: {len(results)}")
print(f"results saved: {out_path}")
