# Mazda Daily Report - 完整技术规格说明书

> 本文档包含技能的完整实现细节，可用于 AI 工具复刻整个技能系统。

---

## 📑 目录

1. [系统概述](#1-系统概述)
2. [环境要求](#2-环境要求)
3. [目录结构](#3-目录结构)
4. [数据源规格](#4-数据源规格)
5. [核心算法详解](#5-核心算法详解)
6. [完整代码实现](#6-完整代码实现)
7. [输出规格](#7-输出规格)
8. [测试用例](#8-测试用例)
9. [故障排除](#9-故障排除)

---

## 1. 系统概述

### 1.1 功能目标
自动从多个 Excel 数据源聚合马自达 4S 店售后 KPI 数据，生成包含以下维度的日报：
- 经营数据（收入、台次、达成率）
- 保险平台数据（新保/续保）
- 客诉/线索统计
- 车质网投诉统计
- CSI 自主调研数据

### 1.2 输入输出
```
输入：E:\每日分析数据源\*.xlsx, *.xls
输出：KPI 日报_YYYYMMDD_full.md
      KPI 日报_YYYYMMDD_full.html
```

### 1.3 处理门店
固定 5 家门店：
| 门店名称 | 经销商代码 |
|---------|-----------|
| 重庆金团 | M18003 |
| 重庆瀚达 | M23002 |
| 重庆银马 | A28856 |
| 重庆万事新 | M18571 |
| 西藏鼎恒 | M18912 |

---

## 2. 环境要求

### 2.1 Python 环境
```
Python >= 3.9
```

### 2.2 依赖库
```requirements.txt
pandas>=2.0.0
openpyxl>=3.0.0
xlrd>=2.0.0  # 用于读取.xls 文件
```

### 2.3 安装命令
```bash
uv pip install pandas openpyxl xlrd
```

---

## 3. 目录结构

### 3.1 完整文件树
```
~/.openclaw/skills/mazda-daily-report/
├── SKILL.md                    # 技能定义（YAML front matter）
├── README.md                   # 用户使用说明
├── SPECIFICATION.md            # 本文档（技术规格）
├── scripts/
│   ├── generate_report.py      # 主程序（约 800 行）
│   ├── run_report.bat          # Windows 批处理启动器
│   └── run_report.ps1          # PowerShell 启动器
└── references/
    └── (可选) 示例数据文件
```

### 3.2 SKILL.md 格式
```yaml
---
name: mazda-daily-report
description: 生成马自达售后日报（经营 + 客诉/线索+CSI）并输出 Markdown/HTML
---
```

---

## 4. 数据源规格

### 4.1 售后日报（必需）

**文件匹配**：文件名包含"售后"或"日报"或"综合"
**格式**：.xlsx 或 .xls

#### Sheet 结构：综合经营数据
| 列索引 | 列名 | 数据类型 | 说明 |
|-------|------|---------|------|
| 0 | 经销商代码 | string | 如 M18003 |
| 1 | 经销商名称 | string | 如重庆金团... |
| 2 | 区域 | string | 如西区 |
| 3 | 服务顾问 | string | - |
| 4 | 服务总收入 | number | 元 |
| 5 | 零件总收入 | number | 元 |
| 6 | 工时总收入 | number | 元 |
| 7 | 进店台次 | number | 台 |
| 8 | 台次目标 | number | 台 |
| ... | ... | ... | ... |

#### Sheet 结构：零附件明细（第 3 个 sheet，索引 2）
| 列索引 | 列名 | 数据类型 |
|-------|------|---------|
| 0 | 经销商代码 | string |
| 1 | 经销商名称 | string |
| 2 | 区域 | string |
| ... | ... | ... |
| 9 | 当月零附件目标 | number |
| 10 | 当月零附件达成 | number |
| 11 | 当月达成率 | number |
| 12 | 当季度零附件目标 | number |
| 13 | 当季度零附件达成 | number |
| 14 | 当季度达成率 | number |
| 16 | 当月保养台次 | number |
| 17 | 机油单车 | number |
| 20 | 事故单车 | number |

### 4.2 CSI 自主调研（必需）

**文件匹配**：文件名包含"CSI"或"自主"
**格式**：.xlsx

#### Sheet 1: 统计表
**特殊结构**：第 1 行是合并单元格的表头信息，第 2 行是列名，第 3 行起是数据

**第 1 行（表头信息）**：
| 列 | 内容示例 |
|---|---------|
| A | 统计日期： |
| B | 本月维修合同：3 月 1 日 -3 月 8 日 |
| C | 评价工单结算范围：2 月 1 日 -3 月 8 日 |
| F | 直评日期：3 月 1 日 -3 月 10 日 |

**第 2 行（列名）**：
| 列索引 | 列名 |
|-------|------|
| 0 | 经销商代码 |
| 1 | 经销商名称 |
| 2 | 区域 |
| 3 | 服务顾问 |
| 4 | 本月维修合同 |
| 5 | 评价客户数 |
| 6 | 参与率 |
| 7 | 满意客户数 |
| 8 | 满意率 |

**第 3 行起（数据行）**：
```
M18003, 重庆金团..., 西区, ..., 140, 6, 0.0429, 6, 1.0
```

#### Sheet 4: 不满意客户名单
| 列索引 | 列名 |
|-------|------|
| 0 | 维修合同号 |
| ... | ... |
| 6 | 客诉所属经销商 |
| 9 | 直评时间 |
| 13 | 不满意点概述 |

### 4.3 保险平台数据（可选）

**文件匹配**：文件名包含"保险"或"平台"
**格式**：.xlsx

#### Sheet 结构：多月份 sheet
每个 sheet 名为月份（如"1 月"、"2 月"、"3 月 10 日"）

| 列索引 | 列名 | 数据类型 |
|-------|------|---------|
| 0 | 序号 | number |
| 1 | 经销商代码 | string |
| 2 | 经销商名称 | string |
| 3 | 区域 | string |
| 4 | 经理 | string |
| 5 | 新保出单 | number |
| 6 | 续保出单 | number |
| 7 | 续保录单 | number |
| 8 | 续保汇总 | number |
| 9 | 忠诚用户 | number |
| 10 | 续保率 | number |

### 4.4 客诉/线索工单（可选）

**文件匹配**：文件名包含"线索工单"
**格式**：.xls/.xlsx/.html

**结构**：HTML 伪装的 XLS，用 `pd.read_html()` 读取

| 列索引 | 列名 |
|-------|------|
| ... | ... |
| 8 | 状态（关闭/未关闭） |
| 15 | 经销商名称 |
| ... | ... |
| -1 | 超时时长（处理） |

### 4.5 车质网投诉（可选）

**文件匹配**：文件名包含"投诉"
**格式**：.xls

#### Sheet: 未撤诉（索引 2）
| 列索引 | 列名 | 数据类型 |
|-------|------|---------|
| 0 | 投诉编号 | string |
| 1 | 投诉时间 | datetime |
| ... | ... | ... |
| 24 | 投诉状态 | string |
| 31 | 经销商名称 | string |
| 32 | 投诉内容 | string |

---

## 5. 核心算法详解

### 5.1 文件查找算法（解决 Windows 编码问题）

**问题**：Windows 控制台中文显示为乱码，无法用字符串直接匹配

**解决方案**：UTF-8 hex 字节匹配

```python
def find_latest_file(daily, keywords, exts=None):
    """
    在目录中递归查找最新文件
    
    参数:
        daily: 根目录路径
        keywords: 关键字列表（中文）
        exts: 允许的文件扩展名列表
    
    返回:
        最新匹配文件的完整路径，或 None
    """
    candidates = []
    for root, _, files in os.walk(daily):
        for f in files:
            if f.startswith('~$'):  # 跳过临时文件
                continue
            if exts and not f.lower().endswith(tuple(exts)):
                continue
            
            try:
                fb_hex = f.encode('utf-8').hex()
                
                # 售后日报匹配
                if ('售后日报' in keywords or '售后' in keywords or 
                    '日报' in keywords or '综合' in keywords):
                    if ('e594aee5908e' in fb_hex or   # 售后
                        'e697a5e68aa5' in fb_hex or   # 日报
                        'e7bbbce59088' in fb_hex):    # 综合
                        candidates.append(os.path.join(root, f))
                        continue
                
                # CSI 匹配
                if ('CSI' in keywords or '自主调研' in keywords or '自主' in keywords):
                    if ('435349' in fb_hex or         # CSI
                        'e887aa' in fb_hex):           # 自主
                        candidates.append(os.path.join(root, f))
                        continue
                
                # 保险平台匹配
                if ('保险平台' in keywords or '保险' in keywords or '平台' in keywords):
                    if ('e4bf9de999a9' in fb_hex or  # 保险
                        'e5b9b3e58fb0' in fb_hex):    # 平台
                        candidates.append(os.path.join(root, f))
                        continue
                
                # 线索工单匹配
                if ('线索工单' in keywords):
                    if ('e7babe7b79a' in fb_hex or  # 线索
                        'e5b7a5e58d95' in fb_hex):   # 工单
                        candidates.append(os.path.join(root, f))
                        continue
                
                # 车质网投诉匹配
                if ('投诉' in keywords):
                    if ('e68a95e8af89' in fb_hex):   # 投诉
                        candidates.append(os.path.join(root, f))
                        continue
                        
            except Exception:
                pass
    
    if not candidates:
        return None
    return max(candidates, key=lambda p: os.path.getmtime(p))
```

### 5.2 UTF-8 Hex 对照表（完整）

| 中文 | UTF-8 Hex | 说明 |
|------|-----------|------|
| 售后 | `e594aee5908e` | |
| 日报 | `e697a5e68aa5` | |
| 综合 | `e7bbbce59088` | |
| CSI | `435349` | ASCII |
| 自主 | `e887aa` | |
| 调研 | `e8b083e7a094` | |
| 保险 | `e4bf9de999a9` | |
| 平台 | `e5b9b3e58fb0` | |
| 线索 | `e7babe7b79a` | |
| 工单 | `e5b7a5e58d95` | |
| 投诉 | `e68a95e8af89` | |
| 车质 | `e8bda6e8b4a8` | |
| 重庆 | `e9878de5ba86` | |
| 西藏 | `e8a5bfe8978f` | |

### 5.3 CSI 表头解析算法

**问题**：第 1 行是合并单元格，pandas 读取为 NaN

**解决方案**：使用 openpyxl 读取原始单元格

```python
def parse_csi_header(csi_file):
    """
    解析 CSI 统计表第 1 行的表头信息
    
    返回:
        dict = {
            '本月维修合同': '3 月 1 日 -3 月 8 日',
            '评价工单结算范围': '2 月 1 日 -3 月 8 日',
            '直评日期': '3 月 1 日 -3 月 10 日'
        }
    """
    from openpyxl import load_workbook
    import re
    
    csi_header_map = {}
    wb = load_workbook(csi_file, data_only=True)
    ws = wb.worksheets[0]  # 第一个 sheet
    
    for col in range(1, ws.max_column + 1):
        cell = ws.cell(row=1, column=col)
        if cell.value and isinstance(cell.value, str):
            if '：' in cell.value or ':' in cell.value:
                m = re.match(r'^(.*?)[：:]\s*(.*)$', cell.value)
                if m:
                    key = m.group(1).strip()
                    value = m.group(2).strip()
                    csi_header_map[key] = value
    
    return csi_header_map
```

### 5.4 车质网投诉统计

```python
def parse_chezhinet(chezhinet_df, stores):
    """
    统计车质网未撤诉投诉
    
    参数:
        chezhinet_df: 未撤诉 sheet 的 DataFrame
        stores: 门店列表
    
    返回:
        stats = {
            '重庆金团': {'total': 0, 'unclosed': 0},
            ...
        }
    """
    stats = {s: {'total': 0, 'unclosed': 0} for s in stores}
    
    if chezhinet_df is None or chezhinet_df.empty:
        return stats
    
    # 第 32 列（索引 31）是经销商名称
    dealer_col = 31
    if len(chezhinet_df.columns) <= dealer_col:
        return stats
    
    # 第 25 列（索引 24）是投诉状态
    status_col = 24
    
    for st in stores:
        # 筛选包含店名的行
        sub = chezhinet_df[
            chezhinet_df.iloc[:, dealer_col]
            .astype(str)
            .str.contains(st, na=False)
        ]
        
        total = len(sub)
        
        # 统计未关闭（状态包含"未关闭"或"未处理"）
        if len(chezhinet_df.columns) > status_col:
            unclosed = sub[
                sub.iloc[:, status_col]
                .astype(str)
                .str.contains('未关闭 | 未处理', na=False)
            ].shape[0]
        else:
            unclosed = total
        
        stats[st] = {'total': int(total), 'unclosed': int(unclosed)}
    
    return stats
```

### 5.5 百分比格式化

```python
def format_percent(v):
    """
    统一百分比格式为 XX.XX%
    
    处理逻辑:
    - 如果值 <= 1，认为是小数，乘以 100
    - 如果值 > 1，认为是百分比数值，直接格式化
    - 保留 2 位小数
    """
    if v is None:
        return None
    s = str(v).strip()
    if s == '' or s.lower() == 'nan':
        return None
    
    had_percent = '%' in s
    s_num = s.replace('%', '').replace(',', '').strip()
    
    try:
        n = float(s_num)
    except Exception:
        return s
    
    if (not had_percent) and n <= 1:
        n = n * 100
    
    return f"{n:.2f}%"
```

### 5.6 报告日期提取

```python
def extract_report_date(aftermarket_file):
    """
    从售后日报文件名提取日期
    
    示例:
        "售后日报 20260312.xlsx" → "2026-03-12"
    """
    if not aftermarket_file:
        return datetime.now().strftime('%Y-%m-%d')
    
    fname = os.path.basename(aftermarket_file)
    m = re.search(r'(\d{4})(\d{2})(\d{2})', fname)
    
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    
    return datetime.now().strftime('%Y-%m-%d')
```

---

## 6. 完整代码实现

### 6.1 主程序结构

```python
# -*- coding: utf-8 -*-
"""
Mazda Daily Report - 马自达 KPI 每日全维度分析报告生成器

功能:
- 读取多源 Excel 数据
- 聚合 5 家门店 KPI 指标
- 生成 Markdown 和 HTML 报告
"""

import os
import re
import json
import html
import shutil
import argparse
from datetime import datetime
import pandas as pd
from openpyxl import load_workbook

# ============ 常量定义 ============
STORES = ['重庆金团','重庆瀚达','重庆银马','重庆万事新','西藏鼎恒']
STORE_CODES = {
    '重庆金团':'M18003',
    '重庆瀚达':'M23002',
    '重庆银马':'A28856',
    '重庆万事新':'M18571',
    '西藏鼎恒':'M18912'
}

BIZ_DISPLAY_ORDER = [
    '服务总收入', '零件总收入', '工时总收入', '进店台次', '台次达成率',
    '机油单车', '事故单车', '当月保养台次', '当季度保养台次累计',
    '当月零附件目标', '当月零附件达成', '当月零件达成率',
    '当季度零附件目标', '当季度零附件达成', '当季度达成率',
]

# ============ 工具函数 ============

def format_percent(v):
    # ... 见 5.5 节 ...

def format_int(v):
    if v is None:
        return None
    s = str(v).strip()
    if s == '' or s.lower() == 'nan':
        return None
    try:
        n = float(str(v).replace(',', ''))
        return int(round(n))
    except Exception:
        return v

# ============ 文件查找 ============

def find_latest_file(daily, keywords, exts=None):
    # ... 见 5.1 节 ...

# ============ 数据加载 ============

def load_lead(lead_file):
    """加载客诉/线索数据"""
    if not lead_file:
        return None
    try:
        tables = pd.read_html(lead_file, encoding='utf-8')
    except Exception:
        tables = pd.read_html(lead_file)
    df = max(tables, key=lambda t: t.shape[1])
    df.columns = df.iloc[0]
    df = df.iloc[1:]
    return df

def load_csi(csi_file):
    """加载 CSI 数据"""
    if not csi_file:
        return None, None
    xl = pd.ExcelFile(csi_file)
    stat = pd.read_excel(csi_file, sheet_name=0)
    bad = pd.read_excel(csi_file, sheet_name=xl.sheet_names[-1])
    return stat, bad

def load_platform(platform_file):
    """加载保险平台数据"""
    if not platform_file:
        return None
    xls = pd.ExcelFile(platform_file)
    out = []
    for sn in xls.sheet_names:
        try:
            df = pd.read_excel(platform_file, sheet_name=sn)
            if df is not None and not df.empty and df.shape[1] >= 11:
                out.append((sn, df))
        except Exception:
            continue
    return out

def load_biz(aftermarket_file):
    """加载经营数据"""
    if not aftermarket_file or not os.path.exists(aftermarket_file):
        return None
    try:
        xl = pd.ExcelFile(aftermarket_file)
        target_sheet = None
        for sn in xl.sheet_names:
            if 'mazda' in str(sn).lower() or '月' in str(sn):
                target_sheet = sn
                break
        if target_sheet is None:
            target_sheet = xl.sheet_names[0]
        return pd.read_excel(aftermarket_file, sheet_name=target_sheet)
    except Exception:
        return None

def load_biz_detail(aftermarket_file, daily_dir):
    """加载零附件明细数据"""
    xlsx_files = []
    if aftermarket_file and os.path.exists(aftermarket_file):
        xlsx_files.append(aftermarket_file)
    xlsx_files += [
        os.path.join(daily_dir, f)
        for f in os.listdir(daily_dir)
        if f.lower().endswith('.xlsx') and (not f.startswith('~$'))
    ]
    
    for wb in xlsx_files:
        try:
            xl = pd.ExcelFile(wb)
            if len(xl.sheet_names) >= 3:
                df = pd.read_excel(wb, sheet_name=2)
                if df is not None and not df.empty and df.shape[1] >= 21:
                    return df
        except Exception:
            continue
    return None

# ============ 数据解析 ============

def parse_lead_stats(lead_df):
    """解析客诉/线索统计"""
    stats = {s: {'total':0,'closed':0,'unclosed':0,'timeout':0} for s in STORES}
    if lead_df is None or lead_df.empty:
        return stats
    
    cols = list(lead_df.columns)
    name_col = cols[15] if len(cols) > 15 else cols[-1]
    status_col = cols[8] if len(cols) > 8 else cols[0]
    timeout_col = cols[-1]
    
    for st in STORES:
        sub = lead_df[lead_df[name_col].astype(str).str.contains(st, na=False)]
        total = len(sub)
        closed = sub[sub[status_col].astype(str).str.contains('关闭 | 已 | 闭', na=False)].shape[0]
        unclosed = max(total - closed, 0)
        timeout = (
            pd.to_numeric(
                sub[timeout_col].astype(str).str.extract(r'(\d+\.?\d*)', expand=False),
                errors='coerce'
            ).fillna(0) > 0
        ).sum()
        stats[st] = {
            'total': int(total),
            'closed': int(closed),
            'unclosed': int(unclosed),
            'timeout': int(timeout)
        }
    return stats

def parse_csi(stat_df, bad_df, csi_file=None):
    """解析 CSI 数据"""
    csi_stats = {}
    bad_lists = {}
    
    # 解析表头
    csi_header_map = {}
    if csi_file and os.path.exists(csi_file):
        try:
            wb = load_workbook(csi_file, data_only=True)
            ws = wb.worksheets[0]
            for col in range(1, ws.max_column + 1):
                cell = ws.cell(row=1, column=col)
                if cell.value and isinstance(cell.value, str) and ('：' in cell.value or ':' in cell.value):
                    m = re.match(r'^(.*?)[：:]\s*(.*)$', cell.value)
                    if m:
                        csi_header_map[m.group(1).strip()] = m.group(2).strip()
        except Exception as e:
            print(f'  Error parsing CSI header: {e}')
    
    # 解析统计数据
    for st in STORES:
        code = STORE_CODES[st]
        data = {
            '经销商名称':'',
            '评价工单结算范围':'',
            '本月维修合同数_label':'本月维修合同数',
            '本月维修合同数':0,
            '直评日期范围':'',
            '评价客户数':0,
            '参与率':'0.00%',
            '满意客户数':0,
            '满意率':'0.00%'
        }
        
        if stat_df is not None and not stat_df.empty and len(stat_df) > 2:
            for idx in range(2, len(stat_df)):
                row = stat_df.iloc[idx]
                row_code = str(row.iloc[0]) if len(row) > 0 else ''
                if code == row_code or code in row_code:
                    data['经销商名称'] = str(row.iloc[1]) if len(row) > 1 else ''
                    data['评价工单结算范围'] = csi_header_map.get('评价工单结算范围', '')
                    contract_cnt = float(row.iloc[4]) if len(row)>4 and pd.notna(row.iloc[4]) else 0
                    contract_range = csi_header_map.get('本月维修合同', '')
                    data['本月维修合同数'] = format_int(contract_cnt)
                    data['本月维修合同数_label'] = f"本月维修合同数（{contract_range}）" if contract_range else '本月维修合同数'
                    data['直评日期范围'] = csi_header_map.get('直评日期', '')
                    eval_cnt = float(row.iloc[5]) if len(row)>5 and pd.notna(row.iloc[5]) else 0
                    part = float(row.iloc[6]) if len(row)>6 and pd.notna(row.iloc[6]) else 0
                    sat_cnt = float(row.iloc[7]) if len(row)>7 and pd.notna(row.iloc[7]) else 0
                    sat_rate = float(row.iloc[8]) if len(row)>8 and pd.notna(row.iloc[8]) else 0
                    data['评价客户数'] = format_int(eval_cnt)
                    data['参与率'] = f"{part*100:.2f}%" if part <= 1 else f"{part:.2f}%"
                    data['满意客户数'] = format_int(sat_cnt)
                    data['满意率'] = f"{sat_rate*100:.2f}%" if sat_rate <= 1 else f"{sat_rate:.2f}%"
                    break
        csi_stats[st] = data
        
        # 解析不满意客户
        rows = []
        if bad_df is not None and not bad_df.empty and bad_df.shape[1] >= 4:
            sub = bad_df[bad_df.iloc[:,3].astype(str) == code]
            for _, r in sub.iterrows():
                rows.append({
                    '客诉所属经销商': str(r.iloc[6]) if len(r)>6 else '',
                    '直评时间': str(r.iloc[9]) if len(r)>9 else '',
                    '维修合同号': str(r.iloc[0]) if len(r)>0 else '',
                    '不满意点概述': str(r.iloc[13]) if len(r)>13 else ''
                })
        bad_lists[st] = rows
    
    return csi_stats, bad_lists

def parse_platform(monthly_sheets):
    """解析保险平台数据"""
    stats = {s:{} for s in STORES}
    if not monthly_sheets:
        return stats
    
    month_name_pattern = re.compile(r'^\s*\d{1,2}\s*月 (\s*\d{1,2}\s*日)?\s*$', re.IGNORECASE)
    month_sheets = [(sn, df) for sn, df in monthly_sheets if month_name_pattern.match(str(sn))]
    if not month_sheets:
        month_sheets = [(sn, df) for sn, df in monthly_sheets if any(ch.isdigit() for ch in str(sn))]
    if not month_sheets:
        month_sheets = monthly_sheets
    
    for st in STORES:
        vals = {}
        quarter_renew_sum = 0
        monthly_renew_rates = []
        
        for idx_m, (sn, df) in enumerate(month_sheets):
            name_col = df.columns[2] if len(df.columns) > 2 else df.columns[0]
            row = df[df[name_col].astype(str).str.contains(st, na=False)]
            if row.empty:
                continue
            r = row.iloc[0]
            
            month_prefix = f"{sn}-"
            field_map = [
                (5, '新保出单'), (6, '续保出单'), (7, '续保录单'),
                (8, '续保汇总'), (9, '忠诚用户'), (10, '续保率'),
            ]
            for fidx, label in field_map:
                if len(df.columns) > fidx:
                    raw = r.iloc[fidx]
                    val = format_percent(raw) if label == '续保率' else format_int(raw)
                    vals[month_prefix + label] = val
                    
                    if label == '续保汇总':
                        try:
                            quarter_renew_sum += int(format_int(raw) or 0)
                        except Exception:
                            pass
                    if label == '续保率':
                        rp = format_percent(raw)
                        if rp and rp != '-':
                            try:
                                monthly_renew_rates.append(float(str(rp).replace('%', '').strip()))
                            except Exception:
                                pass
        
        if monthly_renew_rates:
            vals['参考续保率'] = format_percent(sum(monthly_renew_rates) / len(monthly_renew_rates) / 100)
        else:
            vals['参考续保率'] = '-'
        vals['当季度续保汇总累加'] = format_int(quarter_renew_sum)
        stats[st] = vals
    
    return stats

def parse_biz(biz_df, biz_detail_df=None):
    """解析经营数据"""
    out = {}
    if biz_df is None or biz_df.empty:
        return {s:{} for s in STORES}
    
    detail_by_store = {}
    if biz_detail_df is not None and not biz_detail_df.empty:
        cols = list(biz_detail_df.columns)
        name_col = cols[2] if len(cols) > 2 else cols[0]
        for st in STORES:
            rr = biz_detail_df[biz_detail_df[name_col].astype(str).str.contains(st, na=False)]
            if not rr.empty:
                detail_by_store[st] = rr.iloc[0]
    
    for st in STORES:
        code = STORE_CODES[st]
        row = biz_df[biz_df.iloc[:,0].astype(str)==code]
        if row.empty:
            out[st] = {}
            continue
        
        r = row.iloc[0]
        cols = r.index
        
        def find_any(keys):
            for c in cols:
                if any(k in str(c) for k in keys):
                    return r[c]
            return None
        
        d = detail_by_store.get(st)
        def dget(idx):
            if d is None:
                return None
            try:
                return d.iloc[idx]
            except Exception:
                return None
        
        month_target = dget(9)
        month_achieve = dget(10)
        month_rate = dget(11)
        quarter_target = dget(12)
        quarter_achieve = dget(13)
        quarter_rate = dget(14)
        month_maint_count = dget(16)
        oil_per_car = dget(17)
        accident_per_car = dget(20)
        
        out[st] = {
            '服务总收入': format_int(find_any(['服务总'])),
            '零件总收入': format_int(find_any(['零件总'])),
            '工时总收入': format_int(find_any(['工时总'])),
            '进店台次': format_int(find_any(['进店','台'])),
            '台次达成率': format_percent(find_any(['台次','达成'])),
            '机油单车': format_int(oil_per_car if oil_per_car is not None else find_any(['机油','单车'])),
            '事故单车': format_int(accident_per_car if accident_per_car is not None else find_any(['事故','单车'])),
            '当月保养台次': format_int(month_maint_count),
            '当季度保养台次累计': format_int(month_maint_count),
            '当月零附件目标': format_int(month_target),
            '当月零附件达成': format_int(month_achieve),
            '当月零件达成率': format_percent(month_rate),
            '当季度零附件目标': format_int(quarter_target),
            '当季度零附件达成': format_int(quarter_achieve),
            '当季度达成率': format_percent(quarter_rate),
        }
    return out

def parse_chezhinet(chezhinet_df, stores):
    """解析车质网投诉"""
    # ... 见 5.4 节 ...

# ============ 报告生成 ============

def build_markdown(run_folder, report_date, biz_metrics, platform_stats, lead_stats, csi_stats, bad_lists, chezhinet_stats=None):
    """生成 Markdown 报告"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    md = [
        '# KPI 每日全维度分析报告',
        '',
        f'**报告日期**: {report_date}  ',
        f'**生成时间**: {now}  ',
        f'**数据目录**: `{run_folder}`',
        ''
    ]
    
    for st in STORES:
        md.append(f'## {st}')
        md.append('')
        md.append('### 经营（日常）')
        bm = biz_metrics.get(st, {})
        if bm:
            md.append('| 指标 | 数值 |')
            md.append('|---|---|')
            for k in BIZ_DISPLAY_ORDER:
                v = bm.get(k)
                if v is None or str(v) == 'nan':
                    v = '-'
                md.append(f'| {k} | {v} |')
        else:
            md.append('（无经营数据）')
        
        md.append('')
        md.append('### 保险平台数据')
        ps = platform_stats.get(st, {})
        if ps:
            md.append('| 指标 | 数值 |')
            md.append('|---|---|')
            for k,v in ps.items():
                md.append(f'| {k} | {v} |')
        else:
            md.append('（无保险平台数据）')
        
        ls = lead_stats.get(st, {'total':0,'closed':0,'unclosed':0,'timeout':0})
        md.append('')
        md.append('### 客诉/线索')
        md.append(f"- 客诉/线索总数：{ls['total']}")
        md.append(f"- 未关闭：{ls['unclosed']}")
        md.append(f"- 已关闭：{ls['closed']}")
        md.append(f"- 超时时长（处理）>0: {ls['timeout']}")
        
        md.append('')
        md.append('### 车质网投诉')
        cz = chezhinet_stats.get(st, {}) if chezhinet_stats else {}
        if cz and cz.get('total', 0) > 0:
            md.append(f"- 投诉总数：**{cz.get('total', 0)}**")
            md.append(f"- 未关闭：**{cz.get('unclosed', 0)}**")
        else:
            md.append('（无车质网未关闭客诉）')
        
        cs = csi_stats.get(st, {})
        md.append('')
        md.append('### CSI 自主调研')
        md.append('| 指标 | 数值 |')
        md.append('|---|---|')
        md.append(f"| 经销商名称 | {cs.get('经销商名称','')} |")
        md.append(f"| 本月维修合同数 | {cs.get('本月维修合同数_label', '本月维修合同数')}：{cs.get('本月维修合同数',0)} |")
        md.append(f"| 评价工单结算范围 | {cs.get('评价工单结算范围','')} |")
        md.append(f"| 直评日期范围 | {cs.get('直评日期范围','')} |")
        md.append(f"| 评价客户数 | {cs.get('评价客户数',0)} |")
        md.append(f"| 参与率 | {cs.get('参与率','0.00%')} |")
        md.append(f"| 满意客户数 | {cs.get('满意客户数',0)} |")
        md.append(f"| 满意率 | {cs.get('满意率','0.00%')} |")
        
        md.append('')
        md.append('#### 不满意客户')
        bad = bad_lists.get(st, [])
        if not bad:
            md.append('（本店无不满意客户）')
        else:
            md.append('| 客诉所属经销商 | 直评时间 | 维修合同号 | 不满意点概述 |')
            md.append('|---|---|---|---|')
            for b in bad:
                md.append(f"| {b['客诉所属经销商']} | {b['直评时间']} | {b['维修合同号']} | {b['不满意点概述']} |")
        md.append('')
        md.append('---')
        md.append('')
    
    return '\n'.join(md)

def build_html(report_date, now, cards_html, labels, closed, unclosed, timeout, part):
    """生成 HTML 报告"""
    return f"""<!doctype html>
<html><head><meta charset='utf-8'><title>KPI 每日全维度分析报告</title>
<script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
<style>
body{{font-family:'Microsoft YaHei',Arial;background:#f7f8fb;padding:20px;color:#222}}
.wrap{{max-width:1200px;margin:0 auto}}
.card{{background:#fff;border-radius:12px;padding:16px;margin:14px 0;box-shadow:0 2px 10px rgba(0,0,0,.08)}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
@media (max-width:900px){{.grid{{grid-template-columns:1fr}}}}
table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{border:1px solid #e5e7eb;padding:8px;vertical-align:top}}th{{background:#f3f4f6;text-align:left}}
canvas{{max-height:320px}}
</style></head><body><div class='wrap'>
<h1>KPI 每日全维度分析报告</h1>
<p>报告日期：{report_date} ｜ 生成时间：{now}</p>
<section class='card'><h3>总览图表</h3><canvas id='leadChart'></canvas><br/><canvas id='csiChart'></canvas></section>
{cards_html}
</div>
<script>
new Chart(document.getElementById('leadChart'),{{type:'bar',data:{{labels:{json.dumps(labels)},datasets:[{{label:'已关闭',data:{json.dumps(closed)}}},{{label:'未关闭',data:{json.dumps(unclosed)}}},{{label:'超时>0',data:{json.dumps(timeout)}}}]}}}});
new Chart(document.getElementById('csiChart'),{{type:'line',data:{{labels:{json.dumps(labels)},datasets:[{{label:'CSI 参与率 (%)',data:{json.dumps(part)}}}]}}}});
</script></body></html>"""

# ============ 主函数 ============

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--daily-dir', default=None, help='每日分析目录')
    ap.add_argument('--workspace', default='C:/Users/Administrator/.openclaw/workspace')
    args = ap.parse_args()
    
    daily = args.daily_dir or 'E:/每日分析数据源'
    today = datetime.now().strftime('%Y-%m-%d')
    run_folder = os.path.join(daily, f'{today}-统计')
    os.makedirs(run_folder, exist_ok=True)
    
    # 查找文件
    aftermarket_file = find_latest_file(daily, ['售后日报'], ['.xlsx', '.xls'])
    csi_file = find_latest_file(daily, ['CSI', '自主调研'], ['.xlsx', '.xls'])
    platform_file = find_latest_file(daily, ['保险平台'], ['.xlsx', '.xls'])
    lead_file = find_latest_file(daily, ['线索工单'], ['.xls', '.xlsx', '.html', '.htm'])
    
    # 查找车质网（排除线索工单）
    chezhinet_file = None
    for f in os.listdir(daily):
        if f.startswith('~$'): continue
        fb = f.encode('utf-8').hex()
        if ('e68a95e8af89' in fb) and f not in [os.path.basename(lead_file) if lead_file else '']:
            chezhinet_file = os.path.join(daily, f)
            break
    
    # 加载和解析数据
    lead_df = load_lead(lead_file)
    lead_stats = parse_lead_stats(lead_df)
    
    csi_stat, csi_bad = load_csi(csi_file)
    csi_stats, bad_lists = parse_csi(csi_stat, csi_bad, csi_file)
    
    platform_sheets = load_platform(platform_file)
    platform_stats = parse_platform(platform_sheets)
    
    biz_df = load_biz(aftermarket_file)
    biz_detail_df = load_biz_detail(aftermarket_file, daily)
    biz_metrics = parse_biz(biz_df, biz_detail_df)
    
    # 车质网
    chezhinet_df = None
    if chezhinet_file and chezhinet_file != lead_file:
        try:
            if chezhinet_file.endswith('.xls'):
                chezhinet_df = pd.read_excel(chezhinet_file, sheet_name=2, engine='xlrd')
            else:
                chezhinet_df = pd.read_excel(chezhinet_file, sheet_name=2)
        except Exception as e:
            print(f'Error loading chezhinet: {e}')
    chezhinet_stats = parse_chezhinet(chezhinet_df, STORES)
    
    # 生成报告
    report_date = extract_report_date(aftermarket_file)
    md_text = build_markdown(run_folder, report_date, biz_metrics, platform_stats, lead_stats, csi_stats, bad_lists, chezhinet_stats)
    date_slug = report_date.replace('-', '')
    md_out = os.path.join(run_folder, f'KPI 日报_{date_slug}_full.md')
    with open(md_out, 'w', encoding='utf-8') as f:
        f.write(md_text)
    
    # 生成 HTML
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    # ... HTML 生成逻辑 ...
    
    # 复制到工作区
    ws = args.workspace
    shutil.copyfile(md_out, os.path.join(ws, f'KPI 日报_{date_slug}_full.md'))
    shutil.copyfile(html_out, os.path.join(ws, f'KPI 日报_{date_slug}_full.html'))
    
    print(f'OK: {html_out}')

if __name__ == '__main__':
    main()
```

---

## 7. 输出规格

### 7.1 Markdown 输出模板

```markdown
# KPI 每日全维度分析报告

**报告日期**: YYYY-MM-DD  
**生成时间**: YYYY-MM-DD HH:MM  
**数据目录**: `{run_folder}`

## {店名}

### 经营（日常）
| 指标 | 数值 |
|---|---|
| 服务总收入 | {value} |
| ... | ... |

### 保险平台数据
| 指标 | 数值 |
|---|---|
| {month}-{metric} | {value} |
| ... | ... |

### 客诉/线索
- 客诉/线索总数：{total}
- 未关闭：{unclosed}
- 已关闭：{closed}
- 超时时长（处理）>0: {timeout}

### 车质网投诉
（无车质网未关闭客诉）
或
- 投诉总数：**{total}**
- 未关闭：**{unclosed}**

### CSI 自主调研
| 指标 | 数值 |
|---|---|
| 经销商名称 | {name} |
| 本月维修合同数 | {label}: {count} |
| 评价工单结算范围 | {range} |
| 直评日期范围 | {range} |
| 评价客户数 | {count} |
| 参与率 | {rate}% |
| 满意客户数 | {count} |
| 满意率 | {rate}% |

#### 不满意客户
（本店无不满意客户）
或
| 客诉所属经销商 | 直评时间 | 维修合同号 | 不满意点概述 |
|---|---|---|---|
| {dealer} | {time} | {contract} | {desc} |

---
```

### 7.2 HTML 输出规格

- 响应式布局（桌面双栏，移动单栏）
- Chart.js 4.x 兼容
- 内联 CSS（无外部样式表依赖）
- 字符编码：UTF-8

---

## 8. 测试用例

### 8.1 单元测试

```python
def test_format_percent():
    assert format_percent(0.865) == "86.50%"
    assert format_percent(86.5) == "86.50%"
    assert format_percent("86.5%") == "86.50%"
    assert format_percent(None) is None

def test_extract_report_date():
    assert extract_report_date("售后日报 20260312.xlsx") == "2026-03-12"
    assert extract_report_date(None) == datetime.now().strftime('%Y-%m-%d')

def test_find_latest_file():
    # 测试 hex 匹配
    result = find_latest_file('E:/每日分析数据源', ['售后日报'], ['.xlsx'])
    assert result is not None
    assert result.endswith('.xlsx')
```

### 8.2 集成测试

1. 准备完整数据集（5 个文件）
2. 运行主程序
3. 验证输出文件存在
4. 验证 Markdown 包含所有必需章节
5. 验证 HTML 可被浏览器正常渲染

---

## 9. 故障排除

### 9.1 错误代码对照表

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| FileNotFoundError | 数据目录不存在 | 检查 `--daily-dir` 参数 |
| Excel file format cannot be determined | .xls 文件需要 xlrd | `pip install xlrd` |
| Worksheet named 'xxx' not found | sheet 名称不匹配 | 检查 Excel 文件结构 |
| 中文乱码 | 编码问题 | 确保文件 UTF-8 编码 |

### 9.2 调试技巧

```python
# 1. 打印找到的文件
print(f'Aftermarket: {aftermarket_file}')
print(f'CSI: {csi_file}')

# 2. 打印 CSI 表头
print(f'CSI Header: {csi_header_map}')

# 3. 打印车质网统计
print(f'Chezhinet stats: {chezhinet_stats}')

# 4. 检查 DataFrame 结构
print(f'biz_df columns: {biz_df.columns}')
print(f'biz_df shape: {biz_df.shape}')
```

---

*文档版本：1.0*
*最后更新：2026-03-14*
*作者：Mazda Daily Report Skill*
