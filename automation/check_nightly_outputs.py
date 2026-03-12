from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path

REWRITE_KEYWORDS = ("行动清单", "步骤", "注意事项")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate nightly outputs under daily-results/YYYY-MM-DD")
    p.add_argument("--date", help="Date to check, format YYYY-MM-DD. Default: today")
    p.add_argument("--base-dir", default="daily-results", help="Base output directory")
    p.add_argument("--strict", action="store_true", help="Enable strict checks")
    p.add_argument("--min-original", type=int, default=3)
    p.add_argument("--min-rewrite", type=int, default=3)
    p.add_argument("--min-skills", type=int, default=1)
    return p.parse_args()


def today_str() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def slug_from_name(filename: str, suffix: str) -> str | None:
    if filename.endswith(suffix):
        return filename[: -len(suffix)]
    return None


def add_issue(bucket: list[str], message: str) -> None:
    if message not in bucket:
        bucket.append(message)


def build_report(status: str, checked_dir: Path, pass_items: list[str], warns: list[str], fails: list[str], metrics: dict) -> str:
    lines = [
        "# 夜间产出验收报告",
        "",
        f"- 检查目录：`{checked_dir.as_posix()}`",
        f"- 生成时间：`{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
        f"- 总体状态：**{status}**",
        "",
        "## 指标统计",
        "",
        "```json",
        json.dumps(metrics, ensure_ascii=False, indent=2),
        "```",
        "",
        "## 通过项",
    ]

    if pass_items:
        lines.extend([f"- ✅ {x}" for x in pass_items])
    else:
        lines.append("- （无）")

    lines.extend(["", "## 警告项"])
    if warns:
        lines.extend([f"- ⚠️ {x}" for x in warns])
    else:
        lines.append("- （无）")

    lines.extend(["", "## 失败项"])
    if fails:
        lines.extend([f"- ❌ {x}" for x in fails])
    else:
        lines.append("- （无）")

    lines.extend([
        "",
        "## 修复建议",
        "",
        "- 先补齐目录与双文件配对（original/rewrite）。",
        "- 再补最小交付阈值（3 原文/3 改写/1 skill/1 日报）。",
        "- 最后处理质量项（空文件、超短文件、改写关键段缺失）。",
    ])

    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    check_date = args.date or today_str()
    base_dir = Path(args.base_dir)
    day_dir = base_dir / check_date

    pass_items: list[str] = []
    warns: list[str] = []
    fails: list[str] = []

    required_dirs = ["original", "rewrite", "skills", "reports", "logs"]

    if not day_dir.exists():
        add_issue(fails, f"目录不存在：{day_dir.as_posix()}")
        metrics = {
            "date": check_date,
            "original_count": 0,
            "rewrite_count": 0,
            "skills_count": 0,
            "unpaired_original": [],
            "unpaired_rewrite": [],
            "empty_files": [],
            "short_files": [],
        }
        status = "FAIL"
        print(f"[FAIL] {fails[0]}")
        return 2

    for d in required_dirs:
        if (day_dir / d).exists():
            pass_items.append(f"目录存在：{d}/")
        else:
            add_issue(fails, f"缺失目录：{d}/")

    original_dir = day_dir / "original"
    rewrite_dir = day_dir / "rewrite"
    skills_dir = day_dir / "skills"
    reports_dir = day_dir / "reports"
    logs_dir = day_dir / "logs"

    original_files = sorted(original_dir.glob("*.md")) if original_dir.exists() else []
    rewrite_files = sorted(rewrite_dir.glob("*.md")) if rewrite_dir.exists() else []
    skill_files = sorted(skills_dir.glob("*.md")) if skills_dir.exists() else []

    orig_slugs = {slug_from_name(p.name, "-original.md") for p in original_files}
    rew_slugs = {slug_from_name(p.name, "-wechat.md") for p in rewrite_files}
    orig_slugs.discard(None)
    rew_slugs.discard(None)

    unpaired_original = sorted(s for s in orig_slugs if s not in rew_slugs)
    unpaired_rewrite = sorted(s for s in rew_slugs if s not in orig_slugs)

    if unpaired_original:
        add_issue(fails, f"未配对原文：{', '.join(unpaired_original)}")
    if unpaired_rewrite:
        add_issue(fails, f"未配对改写：{', '.join(unpaired_rewrite)}")
    if not unpaired_original and not unpaired_rewrite:
        pass_items.append("原文与改写文件配对完整")

    if len(original_files) < args.min_original:
        add_issue(fails, f"原文数量不足：{len(original_files)} < {args.min_original}")
    else:
        pass_items.append(f"原文数量达标：{len(original_files)}")

    if len(rewrite_files) < args.min_rewrite:
        add_issue(fails, f"改写数量不足：{len(rewrite_files)} < {args.min_rewrite}")
    else:
        pass_items.append(f"改写数量达标：{len(rewrite_files)}")

    if len(skill_files) < args.min_skills:
        add_issue(fails, f"Skill 草案数量不足：{len(skill_files)} < {args.min_skills}")
    else:
        pass_items.append(f"Skill 草案数量达标：{len(skill_files)}")

    summary_path = reports_dir / "daily-summary.md"
    if summary_path.exists():
        pass_items.append("日报存在：reports/daily-summary.md")
    else:
        add_issue(fails, "缺少日报：reports/daily-summary.md")

    empty_files: list[str] = []
    short_files: list[str] = []

    for f in [*original_files, *rewrite_files, *skill_files, summary_path if summary_path.exists() else None]:
        if f is None:
            continue
        size = f.stat().st_size
        if size == 0:
            empty_files.append(f.as_posix())
        text = read_text(f)
        char_count = len(re.sub(r"\s+", "", text))
        if char_count < 300:
            short_files.append(f.as_posix())

    if empty_files:
        add_issue(fails, f"存在空文件：{len(empty_files)} 个")
    if short_files:
        add_issue(warns, f"存在疑似过短文件：{len(short_files)} 个")

    missing_keyword_files = []
    for f in rewrite_files:
        txt = read_text(f)
        if not any(k in txt for k in REWRITE_KEYWORDS):
            missing_keyword_files.append(f.as_posix())

    if missing_keyword_files:
        add_issue(warns, f"部分改写稿缺少关键段关键词：{len(missing_keyword_files)} 个")
    else:
        if rewrite_files:
            pass_items.append("改写稿关键段关键词检查通过")

    start_log = logs_dir / "run-start.log"
    end_log = logs_dir / "run-end.log"

    if start_log.exists() and end_log.exists():
        pass_items.append("日志存在：run-start.log / run-end.log")
        if end_log.stat().st_mtime < start_log.stat().st_mtime:
            add_issue(fails, "日志时间异常：run-end.log 早于 run-start.log")
    else:
        add_issue(fails, "缺少运行日志（run-start.log 或 run-end.log）")

    metrics = {
        "date": check_date,
        "original_count": len(original_files),
        "rewrite_count": len(rewrite_files),
        "skills_count": len(skill_files),
        "unpaired_original": unpaired_original,
        "unpaired_rewrite": unpaired_rewrite,
        "empty_files": empty_files,
        "short_files": short_files,
        "missing_keyword_files": missing_keyword_files,
    }

    if fails:
        status = "FAIL"
        code = 2
    elif warns:
        status = "WARN"
        code = 1
    else:
        status = "PASS"
        code = 0

    if args.strict and warns and code == 1:
        # strict mode keeps WARN as non-zero (already 1), explicit for readability
        pass

    report_text = build_report(status, day_dir, pass_items, warns, fails, metrics)
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / "acceptance-report.md"
    report_path.write_text(report_text, encoding="utf-8")

    print(f"[{status}] report: {report_path.as_posix()}")
    if fails:
        for x in fails:
            print(f"FAIL - {x}")
    if warns:
        for x in warns:
            print(f"WARN - {x}")

    return code


if __name__ == "__main__":
    raise SystemExit(main())
