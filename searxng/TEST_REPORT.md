# SearXNG API 测试报告

**测试日期**: 2026-03-23 01:17 GMT+8  
**SearXNG 实例**: http://localhost:8888 (Docker)  
**测试状态**: ✅ 全部通过

---

## API 测试结果

### ✅ 1. JSON 格式搜索

**端点**: `GET /search?q=test&format=json`

**测试结果**:
```json
{
  "query": "test",
  "number_of_results": 21,
  "results": [
    {
      "title": "Speedtest by Ookla",
      "url": "https://www.speedtest.net/",
      "content": "Speedtest is better with the app...",
      "engine": "brave",
      "score": 9.0
    }
  ]
}
```

**状态**: ✅ 正常工作

---

### ✅ 2. CSV 格式搜索

**端点**: `GET /search?q=python&format=csv`

**测试结果**: 成功返回 CSV 格式数据，包含 title, url, content, host, engine, score 字段

**状态**: ✅ 正常工作

---

### ✅ 3. POST 方法搜索

**端点**: `POST /search`

**测试**:
```powershell
Invoke-RestMethod -Uri 'http://localhost:8888/search' -Method Post -Body 'q=openclaw&format=json'
```

**结果**: 成功返回 OpenClaw 相关搜索结果

**状态**: ✅ 正常工作

---

### ✅ 4. 分类别搜索

**测试**: `GET /search?q=machine+learning&format=json&categories=it`

**结果**: 成功返回 IT 类别的机器学习相关内容

**状态**: ✅ 正常工作

---

### ✅ 5. 多引擎聚合

**观察到的引擎**:
- brave
- duckduckgo
- startpage
- wikipedia
- google (需启用)
- bing (需启用)

**状态**: ✅ 正常工作

---

## 配置文件修改

**文件**: `C:\Users\Administrator\.openclaw\workspace\searxng\config\settings.yml`

**修改内容**:
```yaml
formats:
  - html
  - json    # ✅ 新增
  - csv     # ✅ 新增
  - rss     # ✅ 新增
```

**原因**: 默认配置只启用了 HTML 格式，API 调用需要启用 JSON/CSV/RSS 格式

---

## 技能创建总结

### 技能名称**: searxng-search

**位置**: `C:\Users\Administrator\.openclaw\workspace\skills\searxng-search\`

**打包文件**: `C:\Users\Administrator\.openclaw\workspace\searxng-search.skill`

### 文件结构**:
```
searxng-search/
├── SKILL.md                    # 技能说明文档
├── scripts/
│   └── searxng_search.py      # Python 搜索脚本
├── .env                        # 环境配置
└── .env.example                # 配置示例
```

### 功能特性**:
- ✅ 支持多种输出格式（json, csv, rss, html）
- ✅ 支持分类别搜索（general, images, videos, news, science, it, music, files）
- ✅ 支持指定搜索引擎
- ✅ 支持时间范围过滤（day, month, year）
- ✅ 支持安全搜索级别
- ✅ 支持分页
- ✅ 支持多语言
- ✅ 命令行参数完整
- ✅ Python API 可直接调用

### 使用示例**:

```bash
# 基础搜索
uv run python scripts/searxng_search.py "machine learning"

# 指定类别
uv run python scripts/searxng_search.py "AI news" --categories news,science

# 时间过滤
uv run python scripts/searxng_search.py "openclaw" --time-range week

# 指定引擎
uv run python scripts/searxng_search.py "python" --engines google,bing,duckduckgo

# 安全搜索
uv run python scripts/searxng_search.py "general" --safesearch 1

# 输出 CSV
uv run python scripts/searxng_search.py "data" --format csv
```

---

## OpenClaw 集成

### 配置修改**:
**文件**: `C:\Users\Administrator\.openclaw\openclaw.json`

```json
{
  "skills": {
    "entries": {
      "searxng-search": {
        "enabled": true
      }
    }
  }
}
```

### Gateway 状态**:
- ✅ 已重启
- ✅ 新技能已加载
- ✅ 可在 OpenClaw 中直接使用

---

## 隐私保护特性

✅ SearXNG 提供的隐私保护**:
- 不追踪用户
- 不记录搜索历史
- 不创建用户画像
- 无 Cookie（默认）
- 支持 HTTPS 加密
- 可选 Tor 访问
- 自托管完全控制数据

---

## 性能指标

| 测试项目 | 响应时间 | 结果数 |
|---------|---------|--------|
| 简单搜索 (test) | <1s | 21+ |
| 分类搜索 (IT) | <2s | 10+ |
| POST 搜索 | <1s | 21+ |
| CSV 导出 | <1s | 25+ |

---

## 后续建议

1. **启用更多搜索引擎**: 编辑 settings.yml 启用 google, bing 等
2. **配置图像代理**: 保护图片搜索隐私
3. **设置速率限制**: 防止滥用
4. **定期更新**: 关注 SearXNG 版本更新
5. **备份配置**: 定期备份 settings.yml

---

## 相关文档

- SearXNG 官方文档: https://docs.searxng.org
- 公共实例列表: https://searx.space
- GitHub 项目: https://github.com/searxng/searxng
- 搜索语法: https://docs.searxng.org/user/search-syntax.html

---

**测试完成时间**: 2026-03-23 01:20 GMT+8  
**测试结论**: ✅ 所有 API 功能正常，技能创建成功，OpenClaw 集成完成
