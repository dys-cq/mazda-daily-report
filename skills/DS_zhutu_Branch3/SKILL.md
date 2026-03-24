---
name: DS_zhutu_Branch3
description: 调用指定的扣子 Coze workflow/stream_run 处理产品资料文档。支持读取 DOCX、PDF、TXT 文件，将提取的正文传给 Product_Information；将 DS_zhutu_Branch2 的输出传给 sellpoints；Product_name 优先从上传文档文件名识别，识别不到再从文档内容识别，仍识别不到则要求用户输入。当需要基于本地产品文档 + 卖点结果调用 Coze 工作流时使用。
---

# DS_zhutu_Branch3

用这个技能把本地产品资料文档转换成 Coze workflow 所需参数并调用工作流。

## 适用场景

当用户需要：
- 读取本地 `docx` / `pdf` / `txt` 产品资料
- 把正文内容传给工作流参数 `Product_Information`
- 把 `DS_zhutu_Branch2` 的执行结果传给 `sellpoints`
- 优先从文件名识别 `Product_name`
- 文件名识别不到时，从文档正文继续识别 `Product_name`
- 仍无法识别时，明确要求用户输入 `Product_name`
- 调用指定 Coze workflow 并保存原始返回结果

## 快速用法

```bash
uv run python scripts/run_workflow.py \
  --file "C:\\path\\to\\product.docx" \
  --original-filename "测试样例-CL0142酷洛菲黑松露润浸洁面乳.docx" \
  --sellpoints-file "C:\\path\\to\\sellpoints.json" \
  --output "C:\\path\\to\\result.json"
```

如果 `sellpoints` 已经是纯文本，也可以直接传：

```bash
uv run python scripts/run_workflow.py \
  --file "C:\\path\\to\\product.pdf" \
  --sellpoints "这里放 DS_zhutu_Branch2 的输出文本"
```

如果前两步都识别不到产品名，显式传入：

```bash
uv run python scripts/run_workflow.py \
  --file "C:\\path\\to\\product.pdf" \
  --sellpoints-file "C:\\path\\to\\sellpoints.json" \
  --product-name "酷洛菲黑松露润浸洁面乳"
```

## 参数规则

- `Product_Information`：从输入文件提取出的正文文本
- `sellpoints`：优先来自 `--sellpoints` 或 `--sellpoints-file`
- `Product_name`：按以下顺序确定
  1. `--product-name` 显式传入
  2. 从输入文件的原始上传文件名 / 显示文件名识别（若提供 `--original-filename`）
  3. 从本地输入文件名识别
  4. 从文档正文识别
  5. 仍失败则报错并要求用户输入
  4. 仍失败则报错并要求用户输入

## 配置

脚本按以下优先级读取配置：

1. 命令行参数
2. 环境变量

建议在 `C:\Users\Administrator\.openclaw\.env` 里配置：

```env
COZE_API_TOKEN=你的_token
COZE_PRODUCT_WORKFLOW_ID=7619646482521538606
```

## 说明

- 默认调用接口：`https://api.coze.cn/v1/workflow/stream_run`
- 默认工作流 ID：`7619646482521538606`
- 输出保留原始返回文本，方便后续排查与调试
- 输出会额外记录 `product_name_source`，便于确认产品名来自文件名、内容还是显式输入

## 运行建议

- 文档较长时，先检查提取文本是否正常
- `sellpoints` 若是 JSON，脚本会尽量保留原始结构并转为字符串传入
- 若工作流返回流式内容，脚本会自动聚合并输出 `events`、`raw_text`、`parsed_json`（若可解析）
