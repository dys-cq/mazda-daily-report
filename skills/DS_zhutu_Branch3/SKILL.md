---
name: DS_zhutu_Branch3
description: 调用指定的扣子 Coze workflow/stream_run 处理产品资料文档。支持读取 DOCX、PDF、TXT 文件，将提取的正文传给 Product_Information；将 DS_zhutu_Branch2 的输出传给 sellpoints；从文件名识别 Product_name，识别失败时默认使用“酷洛菲黑松露润浸洁面乳”。当需要基于本地产品文档 + 卖点结果调用 Coze 工作流时使用。
---

# DS_zhutu_Branch3

用这个技能把本地产品资料文档转换成 Coze workflow 所需参数并调用工作流。

## 适用场景

当用户需要：
- 读取本地 `docx` / `pdf` / `txt` 产品资料
- 把正文内容传给工作流参数 `Product_Information`
- 把 `DS_zhutu_Branch2` 的执行结果传给 `sellpoints`
- 从文件名识别 `Product_name`，失败时回退为 `酷洛菲黑松露润浸洁面乳`
- 调用指定 Coze workflow 并保存原始返回结果

## 快速用法

```bash
uv run python scripts/run_workflow.py \
  --file "C:\\path\\to\\product.docx" \
  --sellpoints-file "C:\\path\\to\\sellpoints.json" \
  --output "C:\\path\\to\\result.json"
```

如果 `sellpoints` 已经是纯文本，也可以直接传：

```bash
uv run python scripts/run_workflow.py \
  --file "C:\\path\\to\\product.pdf" \
  --sellpoints "这里放 DS_zhutu_Branch2 的输出文本"
```

## 参数规则

- `Product_Information`：从输入文件提取出的正文文本
- `sellpoints`：优先来自 `--sellpoints` 或 `--sellpoints-file`
- `Product_name`：优先从输入文件名抽取中文产品名；抽取失败时使用 `酷洛菲黑松露润浸洁面乳`

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
- 默认产品名：`酷洛菲黑松露润浸洁面乳`
- 输出保留原始返回文本，方便后续排查与调试

## 运行建议

- 文档较长时，先检查提取文本是否正常
- `sellpoints` 若是 JSON，脚本会尽量保留原始结构并转为字符串传入
- 若工作流返回流式内容，脚本会自动聚合并输出 `events`、`raw_text`、`parsed_json`（若可解析）
