---
name: mazda-daily-report
description: 生成马自达售后日报（经营 + 客诉/线索+CSI）并输出 Markdown/HTML。适用于用户要求读取 `E:\每日分析数据源` 下 Excel 源表，按固定 5 家店（重庆金团、重庆瀚达、重庆银马、重庆万事新、西藏鼎恒）做准确统计、生成可视化日报、并将中间拆解数据落盘到带日期目录。
---

# Mazda Daily Report

## Overview

将"每日分析数据源"目录下多源数据（综合经营、平台线索、CSI、客诉工单）聚合成统一日报，输出：
- `KPI 日报_YYYYMMDD_full.md`
- `KPI 日报_YYYYMMDD_full.html`（Chart.js 可视化）

并在源目录下创建带日期文件夹保存中间数据，方便审计和复盘。

## Workflow

1. **定位数据目录**
   - 默认目录：`E:\每日分析数据源`
   - 或通过 `--daily-dir` 参数指定

2. **创建任务目录（必须）**
   - 在数据源目录下创建：`YYYY-MM-DD-统计`
   - 中间文件和报告写入该目录

3. **解析客诉/线索（重点）**
   - 源文件是 HTML 伪装 XLS 或 Excel，自动识别
   - 按门店统计：
     - 客诉/线索总数
     - 未关闭
     - 已关闭
     - 超时时长（处理）>0

4. **解析 CSI（固定格式）**
   - 统计表：提取
     - 经销商名称
     - 本月维修合同数（带时间范围）
     - 评价工单结算范围（带时间范围）
     - 直评日期范围
     - 评价客户数
     - 参与率
     - 满意客户数
     - 满意率
   - 不满意客户清单：提取
     - 客诉所属经销商
     - 直评时间
     - 维修合同号
     - 不满意点概述
   - 若无不满意客户，输出：`（本店无不满意客户）`

5. **解析经营数据**
   - 从售后日报 Excel 提取：
     - 服务总收入、零件总收入、工时总收入
     - 进店台次、台次达成率
     - 机油单车、事故单车
     - 当月/当季度零附件目标/达成/达成率
     - 保养台次

6. **解析保险平台数据**
   - 支持多月份 sheet（1 月、2 月、3 月等）
   - 统计：
     - 新保出单、续保出单、续保录单、续保汇总
     - 忠诚用户、续保率
     - 参考续保率（季度平均）
     - 当季度续保汇总累加

7. **生成报告（必须完整版）**
   - Markdown：必须输出完整明细，包含每店"经营表 + 保险平台 + 客诉/线索 4 项 + CSI 6 项 + 不满意客户明细/无则提示"，禁止仅输出摘要版。
   - HTML：必须结构化渲染（卡片 + 表格 +Chart.js 图表），禁止将整篇内容包在 `<pre>` 中。
   - 标题统一为：`KPI 每日全维度分析报告`（不要附加"重算版"等后缀）。
   - 报告日期：从售后日报文件名自动提取（如 `售后日报 20260312.xlsx` → `2026-03-12`）

## Run Script

使用脚本：`scripts/generate_report.py`

示例（默认目录）：

```bash
uv run python scripts/generate_report.py
```

可选参数（自定义目录）：

```bash
uv run python scripts/generate_report.py \
  --daily-dir "E:\每日分析数据源" \
  --workspace "C:/Users/Administrator/.openclaw/workspace"
```

## Outputs

- 任务目录（数据源目录下）
  - `KPI 日报_YYYYMMDD_full.md`
  - `KPI 日报_YYYYMMDD_full.html`
  - `lead_utf8_header.csv`（客诉原始数据）
  - `csi_stat.csv`（CSI 统计）
  - `csi_bad.csv`（不满意客户）
  - `platform_*.csv`（保险平台各月数据）
- 工作区镜像
  - `C:/Users/Administrator/.openclaw/workspace/KPI 日报_YYYYMMDD_full.md`
  - `C:/Users/Administrator/.openclaw/workspace/KPI 日报_YYYYMMDD_full.html`

## Validation Checklist

- 西藏鼎恒客诉是否出现"未关闭=1、超时>0=1"（若源表如此）
- 重庆金团客诉是否显示"2 条且均关闭"（若源表如此）
- CSI 表格是否按指定字段输出且参与率/满意率为百分比格式
- HTML 不使用 `<pre>` 承载整篇正文，需结构化渲染
- 报告日期是否从文件名正确提取
- 百分比字段（台次达成率、零件达成率、续保率等）是否显示为百分比格式
