# 早晨自动验收脚本需求清单（建议 08:05 执行）

> 用途：自动检查昨晚（00:00–08:00）任务是否完整交付，快速发现漏项。

## 1) 输入与范围
- [ ] 默认检查日期：当天 `YYYY-MM-DD`（可用参数覆盖）
- [ ] 检查目录：`daily-results/YYYY-MM-DD/`
- [ ] 支持命令参数：
  - [ ] `--date 2026-03-12`
  - [ ] `--base-dir daily-results`
  - [ ] `--strict`（严格模式）

## 2) 目录完整性检查
- [ ] 根目录存在
- [ ] 子目录存在：`original/ rewrite/ skills/ reports/ logs/`
- [ ] 缺失目录要输出明确错误

## 3) 文件数量与配对检查
- [ ] 统计 `original/*.md` 数量
- [ ] 统计 `rewrite/*.md` 数量
- [ ] 校验同名配对：`<slug>-original.md` ↔ `<slug>-wechat.md`
- [ ] 输出未配对清单（仅原文/仅改写）

## 4) 最小交付阈值检查（可配置）
- [ ] 原文数量 >= 3
- [ ] 改写数量 >= 3
- [ ] Skill 草案数量 >= 1（`skills/*.md`）
- [ ] 日报存在（`reports/daily-summary.md`）

## 5) 质量基础检查（轻量）
- [ ] 检查空文件（size=0）
- [ ] 检查超短文件（例如 < 300 字）并标记“可能无效”
- [ ] 改写稿需包含关键段落关键词（如“行动清单/步骤/注意事项”）

## 6) 日志连续性检查
- [ ] `logs/run-start.log` 存在
- [ ] `logs/run-end.log` 存在
- [ ] 结束时间晚于开始时间
- [ ] 异常条目（error/fail）汇总

## 7) 输出格式
- [ ] 控制台摘要：PASS / WARN / FAIL
- [ ] 生成验收报告：`daily-results/YYYY-MM-DD/reports/acceptance-report.md`
- [ ] 报告包含：
  - [ ] 总体状态
  - [ ] 各项检查结果
  - [ ] 缺失项与修复建议
  - [ ] 下一晚优先修复列表

## 8) 退出码规范
- [ ] `0`：全部通过
- [ ] `1`：有警告（可用但需修复）
- [ ] `2`：关键失败（交付不完整）

## 9) 建议实现方式
- [ ] Python 脚本：`automation/check_nightly_outputs.py`
- [ ] 调用方式：`uv run python automation/check_nightly_outputs.py --date <YYYY-MM-DD> --strict`
- [ ] 可选：将结果追加到 `logs/morning-check.log`

## 10) 后续增强（可选）
- [ ] 自动生成“缺失项修复任务单”
- [ ] 自动对未配对文章重试改写
- [ ] 连续 3 天失败触发高优先级告警
