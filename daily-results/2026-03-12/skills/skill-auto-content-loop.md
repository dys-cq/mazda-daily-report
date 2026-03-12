# skill-auto-content-loop

## 解决问题
将“信息搜集 -> 原文沉淀 -> 公众号改写 -> 技能提炼”做成每天自动执行闭环。

## 触发条件
- 每天定时触发（建议 00:00）
- 或手动触发（新增高价值文章时）

## 输入
- 文章 URL 列表
- 目标输出目录（按日期）

## 输出
- original/*.md
- rewrite/*.md
- reports/daily-summary.md
- skills/*.md

## 执行步骤
1. 拉取候选文章并抽取正文
2. 保存原文到 original
3. 按固定模板生成公众号改写稿
4. 基于当日案例沉淀 skill 草案
5. 生成每日报告并进入验收

## 边界与注意事项
- 受站点反爬策略影响，部分链接可能抓取失败
- 失败链接需写入日志，次日重试
- 重要来源建议配置白名单与多源备份

## 参考来源
- 5 ways to cut out busywork at work with automation | Zapier
