# 夜间产出验收报告

- 检查目录：`daily-results/2026-03-12`
- 生成时间：`2026-03-12 08:56:09`
- 总体状态：**WARN**

## 指标统计

```json
{
  "date": "2026-03-12",
  "original_count": 9,
  "rewrite_count": 9,
  "skills_count": 2,
  "unpaired_original": [],
  "unpaired_rewrite": [],
  "empty_files": [],
  "short_files": [
    "daily-results/2026-03-12/reports/daily-summary.md"
  ],
  "missing_keyword_files": [
    "daily-results/2026-03-12/rewrite/2026-03-12-notion-database-automation-wechat.md",
    "daily-results/2026-03-12/rewrite/2026-03-12-zapier-5-systems-wechat.md",
    "daily-results/2026-03-12/rewrite/article-20260312-011308-01-wechat.md",
    "daily-results/2026-03-12/rewrite/article-20260312-011308-02-wechat.md",
    "daily-results/2026-03-12/rewrite/article-20260312-011308-03-wechat.md"
  ]
}
```

## 通过项
- ✅ 目录存在：original/
- ✅ 目录存在：rewrite/
- ✅ 目录存在：skills/
- ✅ 目录存在：reports/
- ✅ 目录存在：logs/
- ✅ 原文与改写文件配对完整
- ✅ 原文数量达标：9
- ✅ 改写数量达标：9
- ✅ Skill 草案数量达标：2
- ✅ 日报存在：reports/daily-summary.md
- ✅ 日志存在：run-start.log / run-end.log

## 警告项
- ⚠️ 存在疑似过短文件：1 个
- ⚠️ 部分改写稿缺少关键段关键词：5 个

## 失败项
- （无）

## 修复建议

- 先补齐目录与双文件配对（original/rewrite）。
- 再补最小交付阈值（3 原文/3 改写/1 skill/1 日报）。
- 最后处理质量项（空文件、超短文件、改写关键段缺失）。
