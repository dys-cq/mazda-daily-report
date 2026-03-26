---
name: DS_zhutu_Branch2
description: 调用扣子 (Coze) 工作流 API 处理产品信息。支持读取 DOCX、PDF、TXT 文件格式，自动提取产品名称并调用工作流。当需要：(1) 调用扣子工作流处理文档内容，(2) 将产品信息发送给 AI 工作流，(3) 批量处理产品文档生成内容时使用此技能。
---

# DS_zhutu_Branch2 - 扣子工作流产品分析

调用扣子 (Coze) 工作流 API，将本地文档内容发送给工作流进行处理。

## 功能特点

- **多格式支持**：自动读取 DOCX、PDF、TXT 文件
- **智能产品名称提取**：从文件名识别产品名称，识别失败时使用默认值
- **灵活的 API 配置**：支持通过参数或环境变量配置 API Token
- **流式响应**：支持扣子工作流的流式调用

## 使用场景

当需要：
1. 将产品文档（Word、PDF、文本）发送给扣子工作流处理
2. 批量处理多个产品文档生成营销内容
3. 自动化产品信息分析和内容生成流程

## 快速开始

### 基本用法

```bash
# 处理单个文档
uv run python scripts/call_coze_workflow.py path/to/product.docx

# 指定输出文件
uv run python scripts/call_coze_workflow.py product.pdf -o result.json

# 使用自定义工作流 ID
uv run python scripts/call_coze_workflow.py product.txt --workflow-id YOUR_WORKFLOW_ID
```

### 配置 API Token

**方式 1：环境变量（推荐）**

在 `C:\Users\Administrator\.openclaw\.env` 文件中添加：

```
COZE_API_TOKEN=sat_your_token_here
```

**方式 2：命令行参数**

```bash
uv run python scripts/call_coze_workflow.py product.docx --api-token sat_xxx
```

## 脚本参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `file_path` | 输入文件路径（必需） | - |
| `--workflow-id` | 扣子工作流 ID | `7619646208533250090` |
| `--api-token` | 扣子 API Token | 环境变量 `COZE_API_TOKEN` |
| `--output`, `-o` | 输出文件路径 | 标准输出 |
| `--product-name` | 手工指定 Product_name，优先级高于文件名识别 | 从文件名自动识别 |

## 工作流参数

脚本会自动向扣子工作流传递以下参数：

- **Product_Information**: 从文档中提取的完整文本内容
- **Product_name**: 从文件名识别的产品名称（或默认值"酷洛菲黑松露润浸洁面乳"）

## 依赖安装

脚本运行前需要安装依赖：

```bash
# 安装基础依赖
uv pip install requests

# 如需处理 DOCX 文件
uv pip install python-docx

# 如需处理 PDF 文件
uv pip install pdfplumber
```

## 示例

### 示例 1：处理 Word 文档

```bash
uv run python scripts/call_coze_workflow.py "C:\Users\Administrator\.openclaw\media\outbound\938d3177-418e-47df-a5db-1da89f49f814.docx"
```

### 示例 2：批量处理多个文件

```bash
# 创建批处理脚本
for file in products/*.docx; do
  uv run python scripts/call_coze_workflow.py "$file" -o "results/$(basename $file .docx).json"
done
```

### 示例 3：在 Python 代码中调用

```python
from scripts.call_coze_workflow import extract_text_from_file, call_coze_workflow

# 提取文档内容
product_info = extract_text_from_file("product.docx")
product_name = "酷洛菲黑松露润浸洁面乳"

# 调用工作流
result = call_coze_workflow(
    product_info=product_info,
    product_name=product_name,
    workflow_id="7619646208533250090",
    api_token="sat_xxx"
)

print(result)
```

## 错误处理

脚本会处理以下常见错误：

- **文件不存在**：`FileNotFoundError`
- **不支持的格式**：`ValueError`（仅支持 .txt, .docx, .pdf）
- **缺少依赖**：`ImportError`（提示安装相应包）
- **API 调用失败**：`requests.exceptions.HTTPError`

## 注意事项

1. **API Token 安全**：不要将 Token 硬编码在代码中，使用环境变量管理
2. **文件大小限制**：扣子 API 对请求大小有限制，大文件可能需要分割处理
3. **网络超时**：处理大文件时可能需要较长时间，注意设置超时
4. **文件名识别**：产品名称优先从文件名提取，确保文件名包含产品信息

## 相关文件

- `scripts/call_coze_workflow.py` - 核心脚本
- `C:\Users\Administrator\.openclaw\.env` - 环境变量配置（包含 API Token）

## 参考资料

- [扣子 API 文档](https://www.coze.cn/docs/developer_guides/workflow_run)
- [Coze Workflow Stream Run](https://www.coze.cn/docs/developer_guides/workflow_stream_run)
