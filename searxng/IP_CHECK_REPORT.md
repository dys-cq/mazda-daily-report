# 公网 IP 检查报告

**检查时间**: 2026-03-23 01:59 GMT+8

---

## 🌐 公网 IP 信息

| 项目 | 值 |
|------|-----|
| **公网 IP** | `183.226.119.220` |
| **城市** | Shanghai（上海） |
| **省份** | Shanghai（上海） |
| **国家** | CN（中国） |
| **运营商** | China Mobile（中国移动） |
| **ASN** | AS9808 |
| **时区** | Asia/Shanghai |

---

## 🐳 Docker 容器网络信息

| 项目 | 值 |
|------|-----|
| **容器名称** | searxng |
| **容器 IP** | `172.17.0.2` |
| **网络模式** | bridge |
| **映射端口** | 8888:8080 |

---

## ⚠️ 微信公众号 IP 白名单配置

### 需要添加到白名单的 IP

根据之前的发布错误，微信公众号 API 检测到的 IP 是 `172.18.96.1`，这可能是：
- Docker 容器的网络地址
- 或者是系统使用的其他网络接口

**建议操作**：

1. **登录微信公众平台**
   - https://mp.weixin.qq.com

2. **进入基本配置**
   - 设置与开发 → 基本配置

3. **添加 IP 白名单**
   - 点击"修改"
   - 添加以下 IP：
     ```
     183.226.119.220    # 公网 IP（主要）
     172.18.96.1        # 之前报错的 IP（备用）
     172.17.0.1         # Docker 网桥 IP（备用）
     ```
   - 保存配置

4. **等待生效**
   - IP 白名单配置后通常需要 5-10 分钟生效

---

## 🔍 网络拓扑

```
互联网
  ↓
公网 IP: 183.226.119.220 (中国移动)
  ↓
本地网络
  ↓
Docker 网桥：172.17.0.0/16
  ↓
SearXNG 容器：172.17.0.2
```

---

## 📋 验证方法

### 验证 IP 白名单是否生效

配置 IP 白名单后，运行以下命令测试：

```bash
cd C:\Users\Administrator\.openclaw\skills\wechat-draft-publisher
uv run python publisher.py --title "测试" --content "C:\Users\Administrator\.openclaw\workspace\searxng-article-wechat.html" --cover cover.png
```

如果显示 `SUCCESS: 草稿创建成功`，说明 IP 白名单已生效。

---

## 💡 注意事项

1. **动态 IP 风险**
   - 中国移动家庭宽带通常使用动态 IP
   - IP 可能会变化（重启光猫、租约到期等）
   - 如果 IP 变化，需要重新配置白名单

2. **多 IP 情况**
   - 系统可能有多个网络接口（WiFi、有线、虚拟机等）
   - 微信 API 可能检测到不同的出口 IP
   - 建议添加多个可能的 IP 到白名单

3. **Docker 网络**
   - Docker 容器通过 NAT 访问外网
   - 出口 IP 是宿主机的公网 IP
   - 容器内部 IP（172.17.x.x）不会暴露给外部

---

## 🔗 相关文档

- 微信公众号 IP 白名单配置：https://developers.weixin.qq.com/doc/offiaccount/Basic_Information/Access_Overview.html
- SearXNG 部署文档：`C:\Users\Administrator\.openclaw\workspace\searxng\TEST_REPORT.md`
- 发布指南：`C:\Users\Administrator\.openclaw\workspace\searxng\WECHAT_PUBLISH_GUIDE.md`

---

**报告生成时间**: 2026-03-23 01:59 GMT+8
