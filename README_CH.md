# Mazda Daily Report - 马自达 KPI 每日全维度分析报告生成技能

[![GitHub](https://img.shields.io/github/license/dys-cq/mazda-daily-report)](https://github.com/dys-cq/mazda-daily-report)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-green.svg)](https://openclaw.ai)

📊 **自动生成马自达售后 KPI 每日全维度分析报告** —— 从多个数据源聚合数据，输出完整的 Markdown 和 HTML 格式日报，支持 5 家门店数据对比分析。

---

## 📋 目录

- [功能特性](#-功能特性)
- [安装方法](#-安装方法)
- [使用方法](#-使用方法)
- [数据源要求](#-数据源要求)
- [输出说明](#-输出说明)
- [配置选项](#-配置选项)
- [常见问题](#-常见问题)
- [技术架构](#-技术架构)

---

## ✨ 功能特性

### 核心功能

| 功能模块 | 支持指标 |
|---------|---------|
| **📈 经营数据分析** | 服务总收入、零件总收入、工时总收入、进店台次、达成率、机油/事故单车、零附件目标/达成、保养台次 |
| **🛡️ 保险平台数据** | 新保出单、续保出单、续保录单、续保率、参考续保率、季度累计、忠诚用户 |
| **📞 客诉/线索统计** | 总数、未关闭、已关闭、超时时长（处理） |
| **⚠️ 车质网投诉** | 未撤诉投诉统计（按经销商） |
| **📋 CSI 自主调研** | 评价客户数、参与率、满意率、不满意客户明细、维修合同数、评价工单结算范围、直评日期 |

### 输出格式

- ✅ **Markdown 报告** - 完整明细，便于存档和分享
- ✅ **HTML 报告** - 响应式布局，含 Chart.js 可视化图表
- ✅ **中间数据 CSV** - 便于审计和二次分析

---

## 🚀 安装方法

### 前置条件

1. **OpenClaw / ClawX** - 本技能需要 OpenClaw 环境
   - 文档：https://openclaw.ai
   - 安装指南：https://docs.openclaw.ai

2. **Python 3.10+** - 已包含在 OpenClaw 环境中

3. **依赖库** - 已预装：
   ```bash
   pandas
   openpyxl
   xlrd  # 用于读取.xls 文件
   ```

### 安装步骤

#### 方式 1：通过 OpenClaw Skills 安装（推荐）

```bash
# 克隆技能到 OpenClaw skills 目录
cd ~/.openclaw/skills
git clone https://github.com/dys-cq/mazda-daily-report.git
```

#### 方式 2：手动下载

1. 下载本仓库 ZIP 文件
2. 解压到 `~/.openclaw/skills/mazda-daily-report/`

#### 方式 3：使用 git 克隆

```bash
git clone https://github.com/dys-cq/mazda-daily-report.git ~/.openclaw/skills/mazda-daily-report
```

### 验证安装

```bash
cd ~/.openclaw/skills/mazda-daily-report
ls -la
# 应该看到：SKILL.md, README.md, scripts/, run_report.bat, run_report.ps1
```

---

## 📖 使用方法

### 方式 1：双击运行（推荐）

**Windows 用户**：
```
双击运行：run_report.bat
```

或在 PowerShell 中：
```powershell
.\run_report.ps1
```

### 方式 2：命令行运行

```bash
# 默认数据目录
uv run python scripts/generate_report.py

# 指定数据目录
uv run python scripts/generate_report.py \
  --daily-dir "E:\每日分析数据源" \
  --workspace "C:/Users/Administrator/.openclaw/workspace"
```

### 方式 3：在 OpenClaw 中调用

在 OpenClaw 聊天中输入：
```
/mazda-daily-report 请生成今天的马自达售后日报
```

### 创建桌面快捷方式

1. 右键 `run_report.bat` → 发送到 → 桌面快捷方式
2. 双击桌面快捷方式即可运行

---

## 📁 数据源要求

### 默认数据目录

```
E:\每日分析数据源\
```

可通过 `--daily-dir` 参数自定义。

### 必需文件

| 文件类型 | 匹配关键字 | 格式 | 说明 |
|---------|-----------|------|------|
| **售后日报** | `售后` 或 `日报` 或 `综合` | .xlsx/.xls | 经营数据主表 |
| **CSI 自主调研** | `CSI` 或 `自主` | .xlsx | CSI 统计数据 |
| **保险平台** | `保险` 或 `平台` | .xlsx | 续保/新保数据 |
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

### 支持的五家门店

默认配置（可在 `generate_report.py` 中修改）：

```python
STORES = [
    '重庆金团',    # M18003
    '重庆瀚达',    # M23002
    '重庆银马',    # A28856
    '重庆万事新',  # M18571
    '西藏鼎恒'     # M18912
]
```

---

## 📊 输出说明

### 任务目录输出

在数据源目录下创建 `YYYY-MM-DD-统计` 文件夹：

```
E:\每日分析数据源\2026-03-16-统计\
├── KPI 日报_20260315_full.md    # Markdown 报告
├── KPI 日报_20260315_full.html  # HTML 报告（含图表）
├── lead_utf8_header.csv         # 客诉原始数据
├── csi_stat.csv                 # CSI 统计数据
├── csi_bad.csv                  # CSI 不满意客户
└── platform_*.csv               # 保险平台各月数据
```

### 工作区镜像

同时复制一份到 OpenClaw 工作区：

```
C:\Users\Administrator\.openclaw\workspace\
├── KPI 日报_20260315_full.md
└── KPI 日报_20260315_full.html
```

### 报告结构示例

```markdown
# KPI 每日全维度分析报告

**报告日期**: 2026-03-15  
**生成时间**: 2026-03-16 10:31  

## 重庆金团

### 经营（日常）
| 指标 | 数值 |
|---|---|
| 服务总收入 | 595123 |
| 零件总收入 | 410575 |
| 进店台次 | 110 |
| 台次达成率 | 110.00% |
| ... | ... |

### 保险平台数据
| 指标 | 数值 |
|---|---|
| 1 月 - 续保率 | 44.01% |
| 2 月 - 续保率 | 29.46% |
| 参考续保率 | 27.45% |
| ... | ... |

### 客诉/线索
- 客诉/线索总数：3
- 未关闭：0
- 已关闭：3
- 超时时长（处理）>0: 0

### CSI 自主调研
| 指标 | 数值 |
|---|---|
| 经销商名称 | 重庆金团... |
| 评价客户数 | 6 |
| 参与率 | 4.29% |
| 满意率 | 100.00% |

#### 不满意客户
（本店无不满意客户）
```

---

## ⚙️ 配置选项

### 修改数据目录

编辑 `run_report.bat`：
```batch
set DAILY_DIR=E:\每日分析数据源
```

或编辑 `run_report.ps1`：
```powershell
$DAILY_DIR = "E:\每日分析数据源"
```

### 修改工作区目录

```batch
set WORKSPACE=C:\Users\Administrator\.openclaw\workspace
```

### 修改门店配置

编辑 `scripts/generate_report.py`：

```python
STORES = ['重庆金团','重庆瀚达','重庆银马','重庆万事新','西藏鼎恒']

STORE_CODES = {
    '重庆金团': 'M18003',
    '重庆瀚达': 'M23002',
    '重庆银马': 'A28856',
    '重庆万事新': 'M18571',
    '西藏鼎恒': 'M18912'
}
```

### 命令行参数

```bash
uv run python scripts/generate_report.py \
  --daily-dir "E:\每日分析数据源" \
  --workspace "C:/Users/Administrator/.openclaw/workspace"
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--daily-dir` | 数据源目录 | `E:\每日分析数据源` |
| `--workspace` | OpenClaw 工作区目录 | `C:/Users/Administrator/.openclaw/workspace` |

---

## 🐛 常见问题

### Q1: 找不到数据文件

**检查**：
1. 数据目录是否正确（默认 `E:\每日分析数据源`）
2. 文件是否包含匹配关键字（售后、CSI、保险、线索、投诉）
3. 文件是否以 `~$` 开头（临时文件会被跳过）
4. 文件扩展名是否正确（.xlsx/.xls）

**解决**：
```bash
# 使用 --daily-dir 指定正确目录
uv run python scripts/generate_report.py --daily-dir "你的数据目录"
```

### Q2: 中文乱码

**说明**：脚本已内置 UTF-8 编码处理，通常不会出现乱码。

**检查**：
1. 脚本开头已设置 `# -*- coding: utf-8 -*-`
2. 批处理已设置 `chcp 65001`
3. 文件读写使用 `encoding='utf-8'`

### Q3: CSI 表头为空

**原因**：CSI 文件第一个 sheet 应为统计表，第一行包含合并单元格的表头信息。

**检查**：
1. CSI 文件第一个 sheet 是否为统计表（非明细表）
2. 第一行是否包含：本月维修合同、评价工单结算范围、直评日期等
3. openpyxl 是否正确安装

### Q4: 车质网投诉统计为 0

**说明**：如果"未撤诉"sheet 中没有五家店的数据，则显示"（无车质网未关闭客诉）"，这是正常情况。

### Q5: HTML 报告图表不显示

**检查**：
1. 确保网络连接正常（Chart.js 从 CDN 加载）
2. 使用现代浏览器打开（Chrome/Edge/Firefox）
3. 不要直接在文件管理器双击，右键 → 打开方式 → 浏览器

---

## 🏗️ 技术架构

### 目录结构

```
mazda-daily-report/
├── SKILL.md                  # OpenClaw 技能定义文件
├── README.md                 # 英文说明文档
├── README_CH.md              # 中文说明文档（本文件）
├── SPECIFICATION.md          # 技术规格说明
├── run_report.bat            # Windows 批处理启动器
├── run_report.ps1            # PowerShell 启动器
├── .gitignore                # Git 忽略规则
└── scripts/
    └── generate_report.py    # 主报告生成脚本（核心）
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

### 关键技术点

1. **UTF-8 hex 字节匹配** - 解决 Windows 中文文件名乱码问题
2. **openpyxl 表头解析** - 正确读取 CSI 合并单元格表头
3. **Chart.js 可视化** - 生成客诉状态柱状图、CSI 参与率折线图
4. **响应式 HTML** - 支持桌面端和移动端浏览

---

## 📄 许可证

本技能采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📞 联系方式

- **作者**: dys-cq
- **项目主页**: https://github.com/dys-cq/mazda-daily-report
- **OpenClaw 文档**: https://openclaw.ai
- **问题反馈**: https://github.com/dys-cq/mazda-daily-report/issues

---

## 📝 更新日志

### v1.0.0 (2026-03-16)
- ✨ 初始版本发布
- ✅ 支持 5 家门店经营数据分析
- ✅ 支持保险平台数据聚合
- ✅ 支持客诉/线索统计
- ✅ 支持车质网投诉统计
- ✅ 支持 CSI 自主调研分析
- ✅ 输出 Markdown + HTML 双格式
- ✅ 内置 Chart.js 可视化

---

*最后更新：2026-03-16*
