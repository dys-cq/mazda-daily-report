# Mazda Daily Report - 马自达 KPI 每日全维度分析报告生成技能

## 📋 概述

本技能用于自动生成马自达售后 KPI 每日全维度分析报告，从多个数据源聚合数据，输出完整的 Markdown 和 HTML 格式日报。

### 核心功能

- ✅ **经营数据分析**：服务总收入、零件总收入、工时总收入、进店台次、达成率、机油/事故单车、零附件目标/达成等
- ✅ **保险平台数据**：新保/续保出单、续保率、参考续保率、季度累计等
- ✅ **客诉/线索统计**：总数、未关闭、已关闭、超时时长
- ✅ **车质网投诉**：未撤诉投诉统计（按经销商）
- ✅ **CSI 自主调研**：评价客户数、参与率、满意率、不满意客户明细
- ✅ **可视化输出**：Markdown + HTML（含 Chart.js 图表）

---

## 📁 数据源说明

### 默认数据目录
```
E:\每日分析数据源\
```

### 必需文件

| 文件类型 | 匹配关键字 | 格式 | 说明 |
|---------|-----------|------|------|
| **售后日报** | `售后` or `日报` or `综合` | .xlsx/.xls | 经营数据主表 |
| **CSI 自主调研** | `CSI` or `自主` | .xlsx | CSI 统计数据 |
| **保险平台** | `保险` or `平台` | .xlsx | 续保/新保数据 |
| **客诉/线索** | `线索工单` | .xls/.xlsx/.html | 客诉线索统计 |
| **车质网投诉** | `投诉` | .xls/.xlsx | 车质网未撤诉投诉 |

### 文件命名建议
```
售后日报 20260312.xlsx
CSI 自主调研数据明细 0301-0308.xlsx
保险平台数据 0101-0310.xlsx
线索工单 2026314184.xls
车质网投诉列表 - 20260313.xls
```

---

## 🔧 技术架构

### 目录结构
```
~/.openclaw/skills/mazda-daily-report/
├── SKILL.md              # 技能定义文件
├── README.md             # 本文档
├── scripts/
│   ├── generate_report.py    # 主报告生成脚本
│   ├── run_report.bat        # Windows 批处理启动器
│   └── run_report.ps1        # PowerShell 启动器
└── README.md             # 使用说明
```

### 核心模块

```
┌─────────────────────────────────────────────────────────┐
│                    generate_report.py                    │
├─────────────────────────────────────────────────────────┤
│  find_latest_file()     → 文件查找（hex 字节匹配）        │
│  load_biz()             → 加载经营数据                   │
│  load_platform()        → 加载保险平台数据               │
│  load_csi()             → 加载 CSI 数据                   │
│  parse_chezhinet()      → 解析车质网投诉                 │
│  parse_csi()            → 解析 CSI 统计（openpyxl 表头）   │
│  parse_biz()            → 解析经营指标                   │
│  parse_platform()       → 解析平台指标                   │
│  build_markdown()       → 生成 Markdown 报告              │
│  build_html()           → 生成 HTML 报告（含图表）         │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ 开发逻辑详解

### 1. 文件查找逻辑（解决 Windows 编码问题）

**问题**：Windows 控制台中文路径/文件名显示为乱码

**解决方案**：使用 UTF-8 hex 字节匹配
```python
def find_latest_file(daily, keywords, exts=None):
    for f in files:
        fb_hex = f.encode('utf-8').hex()
        # 售后日报：e594aee5908e = "售后", e697a5e68aa5 = "日报"
        if 'e594aee5908e' in fb_hex or 'e697a5e68aa5' in fb_hex:
            candidates.append(os.path.join(root, f))
```

**hex 对照表**：
| 中文 | UTF-8 Hex |
|------|-----------|
| 售后 | `e594aee5908e` |
| 日报 | `e697a5e68aa5` |
| 综合 | `e7bbbce59088` |
| CSI | `435349` |
| 自主 | `e887aa` |
| 保险 | `e4bf9de999a9` |
| 平台 | `e5b9b3e58fb0` |
| 线索 | `e7babe7b79a` |
| 工单 | `e5b7a5e58d95` |
| 投诉 | `e68a95e8af89` |

### 2. CSI 表头时间范围解析

**问题**：CSI 统计表第一行是合并单元格的表头信息，pandas 无法正确读取

**解决方案**：使用 openpyxl 读取原始单元格
```python
from openpyxl import load_workbook
wb = load_workbook(csi_file, data_only=True)
ws = wb.worksheets[0]
for col in range(1, ws.max_column + 1):
    cell = ws.cell(row=1, column=col)
    # 解析："评价工单结算范围：2 月 1 日 -3 月 8 日"
    m = re.match(r'^(.*?)[：:]\s*(.*)$', cell.value)
```

**提取字段**：
- 本月维修合同：3 月 1 日 -3 月 8 日
- 评价工单结算范围：2 月 1 日 -3 月 8 日
- 直评日期：3 月 1 日 -3 月 10 日

### 3. 车质网投诉统计

**数据源**：车质网投诉文件的"未撤诉"sheet（索引 2）

**经销商列**：第 32 列（索引 31）

**逻辑**：
```python
def parse_chezhinet(chezhinet_df, stores):
    for st in stores:
        sub = df[df.iloc[:, 31].astype(str).str.contains(st, na=False)]
        stats[st] = {'total': len(sub), 'unclosed': len(sub)}
    return stats
```

**输出**：
- 有投诉：显示"投诉总数：X | 未关闭：X"
- 无投诉：显示"（无车质网未关闭客诉）"

### 4. 报告日期提取

从售后日报文件名自动提取：
```python
def extract_report_date(aftermarket_file):
    fname = os.path.basename(aftermarket_file)
    m = re.search(r'(\d{4})(\d{2})(\d{2})', fname)
    # "售后日报 20260312.xlsx" → "2026-03-12"
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
```

### 5. 百分比格式化

统一百分比显示格式：
```python
def format_percent(v):
    if v <= 1:
        return f"{v*100:.2f}%"  # 小数转百分比
    return f"{v:.2f}%"          # 已是百分比
```

**应用字段**：台次达成率、零件达成率、续保率、CSI 参与率、CSI 满意率

---

## 📊 输出格式

### Markdown 结构
```markdown
# KPI 每日全维度分析报告

**报告日期**: 2026-03-12  
**生成时间**: 2026-03-14 01:44  
**数据目录**: `E:\每日分析数据源\2026-03-14-统计`

## 重庆金团

### 经营（日常）
| 指标 | 数值 |
|---|---|
| 服务总收入 | 562547 |
| 零件总收入 | 392539 |
| ... | ... |

### 保险平台数据
| 指标 | 数值 |
|---|---|
| 1 月 - 续保率 | 44.01% |
| ... | ... |

### 客诉/线索
- 客诉/线索总数：2
- 未关闭：0
- 已关闭：2
- 超时时长（处理）>0: 0

### 车质网投诉
（无车质网未关闭客诉）

### CSI 自主调研
| 指标 | 数值 |
|---|---|
| 经销商名称 | 重庆金团... |
| 本月维修合同数 | 本月维修合同数（3 月 1 日 -3 月 8 日）：140 |
| 评价工单结算范围 | 2 月 1 日 -3 月 8 日 |
| 直评日期范围 | 3 月 1 日 -3 月 10 日 |
| 评价客户数 | 6 |
| 参与率 | 4.29% |
| 满意客户数 | 6 |
| 满意率 | 100.00% |

#### 不满意客户
（本店无不满意客户）
```

### HTML 特性
- 响应式布局（卡片 + 双栏网格）
- Chart.js 可视化图表（客诉状态柱状图、CSI 参与率折线图）
- 结构化表格渲染
- 移动端适配

---

## 🚀 使用方法

### 方式 1：双击运行（推荐）
```
双击：C:\Users\Administrator\.openclaw\skills\mazda-daily-report\run_report.bat
```

### 方式 2：命令行运行
```bash
# 默认目录
uv run python "C:\Users\Administrator\.openclaw\skills\mazda-daily-report\scripts\generate_report.py"

# 指定目录
uv run python "C:\Users\Administrator\.openclaw\skills\mazda-daily-report\scripts\generate_report.py" ^
  --daily-dir "E:\每日分析数据源" ^
  --workspace "C:/Users/Administrator/.openclaw/workspace"
```

### 方式 3：创建桌面快捷方式
1. 右键 `run_report.bat` → 发送到 → 桌面快捷方式
2. 双击桌面快捷方式运行

---

## 📝 配置说明

### 修改数据目录
编辑 `run_report.bat` 或 `run_report.ps1`：
```batch
set DAILY_DIR=E:\每日分析数据源
```

### 修改工作区目录
```batch
set WORKSPACE=C:\Users\Administrator\.openclaw\workspace
```

### 修改五家店配置
编辑 `generate_report.py`：
```python
STORES = ['重庆金团','重庆瀚达','重庆银马','重庆万事新','西藏鼎恒']
STORE_CODES = {
    '重庆金团':'M18003',
    '重庆瀚达':'M23002',
    '重庆银马':'A28856',
    '重庆万事新':'M18571',
    '西藏鼎恒':'M18912'
}
```

---

## ✅ 验证清单

运行后检查以下项目：

- [ ] CSI 表格是否显示"评价工单结算范围"（如：2 月 1 日 -3 月 8 日）
- [ ] CSI 表格是否显示"直评日期范围"（如：3 月 1 日 -3 月 10 日）
- [ ] CSI 表格是否显示"本月维修合同数"及时间范围
- [ ] 车质网投诉是否显示"（无车质网未关闭客诉）"或具体数量
- [ ] 百分比字段是否显示为 XX.XX% 格式
- [ ] HTML 报告是否正常渲染（非`<pre>`包裹）
- [ ] 五家店数据是否完整（重庆金团、重庆瀚达、重庆银马、重庆万事新、西藏鼎恒）

---

## 🐛 常见问题

### Q1: 找不到数据文件
**检查**：
1. 数据目录是否正确（`E:\每日分析数据源`）
2. 文件是否包含匹配关键字（售后、CSI、保险、线索、投诉）
3. 文件是否以 `~$` 开头（临时文件会被跳过）

### Q2: 中文乱码
**解决**：
1. 脚本已设置 `# -*- coding: utf-8 -*-`
2. 批处理已设置 `chcp 65001`
3. 文件读写使用 `encoding='utf-8'`

### Q3: CSI 表头为空
**检查**：
1. CSI 文件第一个 sheet 是否为统计表
2. 第一行是否包含合并单元格的表头信息
3. openpyxl 是否正确安装

### Q4: 车质网投诉统计为 0
**说明**：如果"未撤诉"sheet 中没有五家店的数据，则显示"（无车质网未关闭客诉）"，这是正常情况。

---

## 📦 依赖项

```bash
pandas
openpyxl
xlrd  # 用于读取.xls 文件
```

所有依赖已包含在 OpenClaw 环境中，无需单独安装。

---

## 📄 输出文件

### 任务目录输出
```
E:\每日分析数据源\2026-03-14-统计\
├── KPI 日报_20260312_full.md    # Markdown 报告
├── KPI 日报_20260312_full.html  # HTML 报告（含图表）
├── lead_utf8_header.csv         # 客诉原始数据
├── csi_stat.csv                 # CSI 统计数据
├── csi_bad.csv                  # CSI 不满意客户
└── platform_*.csv               # 保险平台各月数据
```

### 工作区镜像
```
C:\Users\Administrator\.openclaw\workspace\
├── KPI 日报_20260312_full.md
└── KPI 日报_20260312_full.html
```

---

## 📞 维护与更新

- **技能位置**：`~/.openclaw/skills/mazda-daily-report/`
- **主脚本**：`scripts/generate_report.py`
- **启动器**：`run_report.bat` / `run_report.ps1`

如需更新技能逻辑，修改 `generate_report.py` 后重新运行即可。

---

*最后更新：2026-03-14*
