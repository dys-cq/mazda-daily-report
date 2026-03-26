# OpenClaw 机器人外呼客户实现方案

> **文档版本**: v1.0  
> **生成时间**: 2026-03-18 23:40 CST  
> **适用场景**: 企业客户通知、预约提醒、任务反馈、客服外呼

---

## 📋 目录

1. [方案概述](#1-方案概述)
2. [技术架构](#2-技术架构)
3. [环境依赖与要求](#3-环境依赖与要求)
4. [服务商选择对比](#4-服务商选择对比)
5. [详细实现步骤](#5-详细实现步骤)
6. [代码实现示例](#6-代码实现示例)
7. [配置说明](#7-配置说明)
8. [测试与验证](#8-测试与验证)
9. [生产部署建议](#9-生产部署建议)
10. [成本估算](#10-成本估算)
11. [常见问题 FAQ](#11-常见问题-faq)

---

## 1. 方案概述

### 1.1 目标

使用 OpenClaw 框架实现 AI 机器人自动外呼客户，支持：
- ✅ 批量外呼通知
- ✅ 智能语音对话
- ✅ 通话记录查询
- ✅ 实时通话监听
- ✅ 通话结果分析

### 1.2 核心能力

| 功能 | 描述 |
|------|------|
| 自动外呼 | 根据预设名单自动拨打电话 |
| 语音对话 | AI 与客户进行自然语言交流 |
| 意图识别 | 识别客户回复意图并做出响应 |
| 通话记录 | 保存通话录音和文字转录 |
| 状态追踪 | 实时追踪通话状态（接通/未接/忙音等） |

---

## 2. 技术架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        OpenClaw Gateway                          │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐ │
│  │  Voice Call │  │   AI Agent   │  │    Session Manager      │ │
│  │   Plugin    │  │  (LLM+TTS)   │  │                         │ │
│  └──────┬──────┘  └──────┬───────┘  └─────────────────────────┘ │
│         │                │                                       │
│         └────────┬───────┘                                       │
│                  │                                               │
│         ┌────────▼────────┐                                      │
│         │  Media Stream   │                                      │
│         │   (WebSocket)   │                                      │
│         └────────┬────────┘                                      │
└──────────────────┼────────────────────────────────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
   ┌────────┐ ┌────────┐ ┌────────┐
   │ Twilio │ │ Telnyx │ │ Stepone│
   │        │ │        │ │  (CN)  │
   └────────┘ └────────┘ └────────┘
        │          │          │
        └──────────┼──────────┘
                   ▼
            ┌─────────────┐
            │   PSTN      │
            │  公共电话网  │
            └─────────────┘
                   │
                   ▼
            ┌─────────────┐
            │   客户手机   │
            └─────────────┘
```

### 2.2 组件说明

| 组件 | 职责 |
|------|------|
| OpenClaw Gateway | 核心网关，管理会话和路由 |
| Voice Call Plugin | 电话呼叫插件，处理 SIP/WebRTC 信令 |
| AI Agent | LLM 驱动的智能对话引擎 |
| TTS/STT | 语音合成/语音识别服务 |
| 电话服务商 | 提供电话线路和媒体流 (Twilio/Telnyx/Stepone) |

---

## 3. 环境依赖与要求

### 3.1 硬件要求

| 配置项 | 最低要求 | 推荐配置 |
|--------|----------|----------|
| CPU | 2 核 | 4 核+ |
| 内存 | 4GB | 8GB+ |
| 存储 | 20GB | 50GB+ (录音存储) |
| 网络 | 10Mbps | 100Mbps+ |

### 3.2 软件环境

```yaml
操作系统:
  - Windows 10/11
  - macOS 12+
  - Linux (Ubuntu 20.04+, CentOS 7+)

Node.js:
  版本：v24.13.1+ (推荐) 或 v22.16+ LTS

包管理器:
  - npm 10+
  - 或 pnpm 9+
  - 或 bun 1.0+

OpenClaw:
  版本：latest (通过 npm install -g openclaw@latest)
```

### 3.3 必需账号

| 服务 | 用途 | 获取方式 |
|------|------|----------|
| OpenClaw | 核心框架 | `npm install -g openclaw` |
| 电话服务商 | 外呼线路 | Twilio/Telnyx/Stepone 注册 |
| LLM Provider | AI 对话 | OpenAI/Anthropic/自定义 |
| TTS 服务 | 语音合成 | ElevenLabs/阿里云/Azure |

### 3.4 网络要求

```yaml
出站端口:
  - 443/tcp (HTTPS API)
  - 5060/5061/udp (SIP, 如使用)
  - 10000-20000/udp (RTP 媒体流)

入站端口:
  - 3334/tcp (Webhook 回调，可自定义)
  - 或使用 Tailscale Funnel/Ngrok 暴露

公网 IP:
  - 电话服务商 Webhook 需要公网可达
  - 本地开发可用 Ngrok/Tailscale 隧道
```

---

## 4. 服务商选择对比

### 4.1 国际服务商

| 服务商 | 优势 | 劣势 | 适合场景 |
|--------|------|------|----------|
| **Twilio** | 全球覆盖、文档完善、功能丰富 | 价格较高、国内号码有限 | 国际业务、企业级 |
| **Telnyx** | 价格较低、自有网络、延迟低 | 文档稍弱、国内覆盖一般 | 成本敏感、欧美业务 |
| **Plivo** | 性价比高、API 简单 | 功能相对基础 | 简单通知场景 |

### 4.2 中国服务商

| 服务商 | 优势 | 劣势 | 适合场景 |
|--------|------|------|----------|
| **Stepone AI** | 中文优化、OpenClaw 集成、新用户送 10 元 | 仅支持中国号码 | 中国大陆业务 |
| **阿里云通信** | 稳定可靠、合规 | 需企业资质、审核严格 | 企业正式生产 |
| **腾讯云通信** | 生态整合好 | 价格较高 | 腾讯生态用户 |

### 4.3 推荐选择

```yaml
中国大陆客户:
  首选：Stepone AI (开发测试)
  生产：阿里云通信/腾讯云通信

国际客户:
  首选：Twilio (功能最全)
  备选：Telnyx (成本更低)

开发测试:
  使用 Mock 模式或 Stepone 免费额度
```

---

## 5. 详细实现步骤

### 5.1 步骤总览

```
Step 1: 安装 OpenClaw
    ↓
Step 2: 安装 Voice Call 插件
    ↓
Step 3: 配置电话服务商
    ↓
Step 4: 配置 TTS/STT 服务
    ↓
Step 5: 配置 AI Agent
    ↓
Step 6: 编写外呼脚本
    ↓
Step 7: 测试通话
    ↓
Step 8: 生产部署
```

### 5.2 Step 1: 安装 OpenClaw

```bash
# 安装 OpenClaw CLI
npm install -g openclaw@latest

# 验证安装
openclaw --version

# 初始化配置
openclaw onboard

# 安装为系统服务 (可选)
openclaw gateway install-daemon
```

### 5.3 Step 2: 安装 Voice Call 插件

```bash
# 安装官方 voice-call 插件
openclaw plugins install @openclaw/voice-call

# 或安装 Stepone AI 技能 (中国大陆推荐)
npx clawhub@latest install ustczz/ai-calls-china-phone

# 查看已安装插件
openclaw plugins list
```

### 5.4 Step 3: 配置电话服务商

#### 3.4.1 Twilio 配置

```json5
// ~/.clawd/config.json
{
  "plugins": {
    "entries": {
      "voice-call": {
        "enabled": true,
        "config": {
          "provider": "twilio",
          "fromNumber": "+1234567890",  // Twilio 购买的号码
          "twilio": {
            "accountSid": "ACxxxxxxxxxxxxxxxx",
            "authToken": "your_auth_token"
          },
          "serve": {
            "port": 3334,
            "path": "/voice/webhook"
          },
          "publicUrl": "https://your-domain.com/voice/webhook"
        }
      }
    }
  }
}
```

#### 3.4.2 Stepone AI 配置

```bash
# 设置环境变量
export STEPONEAI_API_KEY="sk_xxxxxxxxxxxxx"

# 或写入 secrets 文件
echo '{ "steponeai_api_key": "sk_xxxxxxxxxxxxx" }' > ~/.clawd/secrets.json
```

### 5.5 Step 4: 配置 TTS/STT 服务

```json5
// ~/.clawd/config.json
{
  "messages": {
    "tts": {
      "provider": "elevenlabs",
      "elevenlabs": {
        "voiceId": "pMsXgVXv3BLzUgSXRplE",
        "modelId": "eleven_multilingual_v2"
      }
    }
  },
  "plugins": {
    "entries": {
      "voice-call": {
        "config": {
          "tts": {
            "provider": "elevenlabs",
            "elevenlabs": {
              "voiceId": "pMsXgVXv3BLzUgSXRplE"
            }
          }
        }
      }
    }
  }
}
```

### 5.6 Step 5: 配置 AI Agent

```json5
// ~/.clawd/config.json
{
  "agents": {
    "defaults": {
      "model": "openai/gpt-4o",
      "thinking": "on"
    }
  },
  "plugins": {
    "entries": {
      "voice-call": {
        "config": {
          "agent": {
            "systemPrompt": "你是一个专业的客服助手，负责通知客户会议安排。语气友好、专业、简洁。",
            "maxTurns": 10,
            "maxDurationSeconds": 300
          }
        }
      }
    }
  }
}
```

### 5.7 Step 6: 重启 Gateway

```bash
# 重启 Gateway 使配置生效
openclaw gateway restart

# 查看状态
openclaw gateway status
```

---

## 6. 代码实现示例

### 6.1 基础外呼脚本 (Node.js)

```javascript
// callout.js
const fetch = require('node-fetch');

const STEPONE_API_KEY = process.env.STEPONEAI_API_KEY;
const BASE_URL = 'https://open-skill-api.steponeai.com/api/v1';

/**
 * 发起外呼
 * @param {string} phoneNumber - 电话号码
 * @param {string} requirement - 外呼需求描述
 * @returns {Promise<{call_id: string, status: string}>}
 */
async function initiateCall(phoneNumber, requirement) {
  const response = await fetch(`${BASE_URL}/callinfo/initiate_call`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': STEPONE_API_KEY,
      'X-Skill-Version': '1.0.0'
    },
    body: JSON.stringify({
      phones: phoneNumber,
      user_requirement: requirement
    })
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
}

/**
 * 查询通话记录
 * @param {string} callId - 通话 ID
 * @returns {Promise<Object>}
 */
async function getCallInfo(callId) {
  const response = await fetch(`${BASE_URL}/callinfo/search_callinfo`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': STEPONE_API_KEY,
      'X-Skill-Version': '1.0.0'
    },
    body: JSON.stringify({ call_id: callId })
  });

  return await response.json();
}

// 使用示例
async function main() {
  try {
    // 发起外呼
    const result = await initiateCall(
      '13800138000',
      '通知客户明天上午 9 点开会，确认是否参加'
    );
    console.log('Call initiated:', result);

    // 等待通话完成
    await new Promise(resolve => setTimeout(resolve, 30000));

    // 查询通话记录
    const info = await getCallInfo(result.call_id);
    console.log('Call info:', info);

  } catch (error) {
    console.error('Error:', error);
  }
}

main();
```

### 6.2 OpenClaw Voice Call CLI 使用

```bash
# 通知模式外呼 (播放预录消息)
openclaw voicecall call \
  --to "+8613800138000" \
  --message "您好，这里是 XX 公司，提醒您明天上午 9 点参加会议" \
  --mode notify

# 对话模式外呼 (AI 交互)
openclaw voicecall call \
  --to "+8613800138000" \
  --message "确认客户是否参加明天的会议" \
  --mode conversation

# 查询通话状态
openclaw voicecall status --call-id "call_xxxxx"

# 结束通话
openclaw voicecall end --call-id "call_xxxxx"
```

### 6.3 批量外呼脚本

```javascript
// batch-callout.js
const fs = require('fs');
const { initiateCall, getCallInfo } = require('./callout');

/**
 * 批量外呼
 * @param {Array<{phone: string, name: string, message: string}>} customers
 * @param {number} concurrency - 并发数
 */
async function batchCallout(customers, concurrency = 3) {
  const results = [];
  const queue = [...customers];
  const active = new Set();

  return new Promise((resolve) => {
    function processNext() {
      while (active.size < concurrency && queue.length > 0) {
        const customer = queue.shift();
        const promise = initiateCall(customer.phone, customer.message)
          .then(result => {
            results.push({ ...customer, ...result, status: 'initiated' });
            active.delete(promise);
            processNext();
          })
          .catch(err => {
            results.push({ ...customer, error: err.message, status: 'failed' });
            active.delete(promise);
            processNext();
          });
        active.add(promise);
      }

      if (active.size === 0 && queue.length === 0) {
        resolve(results);
      }
    }

    processNext();
  });
}

// 从 CSV 读取客户列表
function loadCustomers(csvPath) {
  const content = fs.readFileSync(csvPath, 'utf-8');
  const lines = content.trim().split('\n');
  const headers = lines[0].split(',');

  return lines.slice(1).map(line => {
    const values = line.split(',');
    const customer = {};
    headers.forEach((h, i) => customer[h.trim()] = values[i]?.trim());
    return customer;
  });
}

// 使用示例
async function main() {
  const customers = loadCustomers('customers.csv');
  console.log(`Loaded ${customers.length} customers`);

  const results = await batchCallout(customers, 3);
  console.log('Batch callout completed:', results);

  // 保存结果
  fs.writeFileSync('results.json', JSON.stringify(results, null, 2));
}

main();
```

### 6.4 实时通话监听 (SSE)

```javascript
// stream-listen.js
const fetch = require('node-fetch');
const { EventSource } = require('eventsource');

const STEPONE_API_KEY = process.env.STEPONEAI_API_KEY;
const BASE_URL = 'https://open-skill-api.steponeai.com/api/v1';

/**
 * 实时监听通话对话
 * @param {string} callId - 通话 ID
 */
function streamConversation(callId) {
  const url = `${BASE_URL}/callinfo/stream_chat_history`;

  const eventSource = new EventSource(url, {
    headers: {
      'X-API-Key': STEPONE_API_KEY,
      'X-Skill-Version': '1.0.0',
      'Content-Type': 'application/json'
    },
    initialRequest: {
      method: 'POST',
      body: JSON.stringify({ call_id: callId })
    }
  });

  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const emoji = data.role === 'assistant' ? '🤖' : data.role === 'user' ? '👤' : '📞';
    console.log(`${emoji} ${data.role}: ${data.content}`);

    if (data.content === '[DONE]' || data.content === '[TIMEOUT]') {
      eventSource.close();
      console.log('Call ended');
    }
  };

  eventSource.onerror = (err) => {
    console.error('Stream error:', err);
    eventSource.close();
  };

  return eventSource;
}

// 使用示例
async function main() {
  const callId = process.argv[2];
  if (!callId) {
    console.log('Usage: node stream-listen.js <call_id>');
    process.exit(1);
  }

  console.log(`🎙️ Streaming conversation for call: ${callId}`);
  streamConversation(callId);
}

main();
```

---

## 7. 配置说明

### 7.1 完整配置文件示例

```json5
// ~/.clawd/config.json
{
  "agents": {
    "defaults": {
      "model": "openai/gpt-4o",
      "thinking": "on",
      "workspace": "~/.clawd/workspace"
    }
  },

  "messages": {
    "tts": {
      "provider": "elevenlabs",
      "elevenlabs": {
        "voiceId": "pMsXgVXv3BLzUgSXRplE",
        "modelId": "eleven_multilingual_v2",
        "stability": 0.5,
        "similarityBoost": 0.75
      }
    }
  },

  "plugins": {
    "entries": {
      "voice-call": {
        "enabled": true,
        "config": {
          "provider": "twilio",
          "fromNumber": "+1234567890",

          "twilio": {
            "accountSid": "ACxxxxxxxx",
            "authToken": "${TWILIO_AUTH_TOKEN}"
          },

          "serve": {
            "port": 3334,
            "path": "/voice/webhook",
            "bind": "0.0.0.0"
          },

          "publicUrl": "https://voice.your-domain.com/voice/webhook",

          "webhookSecurity": {
            "allowedHosts": ["voice.your-domain.com"],
            "trustedProxyIPs": ["100.64.0.1"]
          },

          "outbound": {
            "defaultMode": "conversation"
          },

          "streaming": {
            "enabled": true,
            "streamPath": "/voice/stream",
            "maxConnections": 128
          },

          "maxDurationSeconds": 300,
          "staleCallReaperSeconds": 360,

          "agent": {
            "systemPrompt": "你是 XX 公司的智能客服助手。你的任务是：\n1. 礼貌问候客户\n2. 说明来电目的\n3. 回答客户疑问\n4. 确认客户意向\n5. 礼貌结束通话\n\n语气要求：友好、专业、简洁、耐心",
            "maxTurns": 10,
            "greeting": "您好，请问是{customer_name}吗？",
            "fallbackResponses": [
              "抱歉，我没听清楚，您能再说一遍吗？",
              "信号可能不太好，我重复一下..."
            ]
          }
        }
      }
    }
  },

  "secrets": {
    "files": ["~/.clawd/secrets.json"]
  }
}
```

### 7.2 环境变量配置

```bash
# ~/.clawd/.env
# 电话服务商
TWILIO_ACCOUNT_SID=ACxxxxxxxx
TWILIO_AUTH_TOKEN=your_token
TWILIO_FROM_NUMBER=+1234567890

# 或 Stepone AI
STEPONEAI_API_KEY=sk_xxxxxxxxxxxxx

# TTS 服务
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID=pMsXgVXv3BLzUgSXRplE

# LLM 服务
OPENAI_API_KEY=sk-xxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxx
```

---

## 8. 测试与验证

### 8.1 测试清单

```yaml
功能测试:
  - [ ] 单呼测试：拨打测试号码
  - [ ] 通话质量：语音清晰度、延迟
  - [ ] AI 对话：多轮交互正常
  - [ ] 意图识别：正确理解客户回复
  - [ ] 通话记录：录音和转录保存
  - [ ] Webhook 回调：状态更新及时

性能测试:
  - [ ] 并发外呼：同时拨打 N 路电话
  - [ ] 长时间运行：连续运行 24 小时
  - [ ] 资源占用：CPU/内存/网络

异常测试:
  - [ ] 无人接听处理
  - [ ] 忙音处理
  - [ ] 网络中断恢复
  - [ ] API 限流处理
```

### 8.2 测试脚本

```javascript
// test-call.js
const { initiateCall, getCallInfo } = require('./callout');

async function runTests() {
  const testPhone = '13800138000';  // 测试号码

  console.log('🧪 Starting tests...\n');

  // Test 1: Initiate call
  console.log('Test 1: Initiate call');
  const callResult = await initiateCall(testPhone, '测试通话，请接听');
  console.log('✓ Call initiated:', callResult.call_id);

  // Test 2: Wait and check status
  console.log('\nTest 2: Check call status (waiting 30s)');
  await new Promise(r => setTimeout(r, 30000));

  const callInfo = await getCallInfo(callResult.call_id);
  console.log('✓ Call info:', callInfo);

  // Test 3: Validate transcript
  console.log('\nTest 3: Validate transcript');
  if (callInfo.transcript && callInfo.transcript.length > 0) {
    console.log('✓ Transcript available');
  } else {
    console.log('⚠ No transcript yet');
  }

  console.log('\n✅ All tests completed');
}

runTests().catch(console.error);
```

---

## 9. 生产部署建议

### 9.1 部署架构

```
                    ┌─────────────────┐
                    │   Load Balancer │
                    │   (Nginx/ALB)   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
        ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
        │ Gateway 1 │  │ Gateway 2 │  │ Gateway 3 │
        │  (Active) │  │  (Active) │  │  (Standby)│
        └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
              │              │              │
              └──────────────┼──────────────┘
                             │
                    ┌────────▼────────┐
                    │  Shared Storage │
                    │  (录音/日志)     │
                    └─────────────────┘
```

### 9.2 高可用配置

```json5
{
  "gateway": {
    "cluster": {
      "enabled": true,
      "nodeId": "node-1",
      "peers": ["node-2", "node-3"]
    },
    "healthCheck": {
      "enabled": true,
      "interval": 30000
    }
  }
}
```

### 9.3 监控告警

```yaml
监控指标:
  - 通话成功率
  - 平均通话时长
  - API 响应时间
  - 并发通话数
  - 错误率

告警规则:
  - 通话成功率 < 90% → 发送告警
  - 并发通话数 > 阈值 → 发送告警
  - API 错误率 > 5% → 发送告警

告警渠道:
  - 邮件
  - 短信
  - 钉钉/企业微信
  - OpenClaw 消息通知
```

### 9.4 安全建议

```yaml
网络安全:
  - 使用 HTTPS 加密所有 API 通信
  - Webhook 启用签名验证
  - 限制 Webhook 来源 IP

数据安全:
  - 录音文件加密存储
  - 敏感信息脱敏
  - 定期清理过期数据

访问控制:
  - API Key 定期轮换
  - 最小权限原则
  - 操作日志审计
```

---

## 10. 成本估算

### 10.1 Stepone AI (中国大陆)

| 项目 | 价格 | 备注 |
|------|------|------|
| 开户 | 免费 | 新用户送 10 元 |
| 通话费 | ~0.12 元/分钟 | 按实际通话时长 |
| API 调用 | 免费 | 包含在通话费中 |

**月成本估算** (1000 通/月，平均 2 分钟/通):
```
1000 通 × 2 分钟 × 0.12 元 = 240 元/月
```

### 10.2 Twilio (国际)

| 项目 | 价格 | 备注 |
|------|------|------|
| 号码月租 | $1-2/月/号码 | 依国家而定 |
| 通话费 | $0.013-0.05/分钟 | 依目的地而定 |
| 语音识别 | $0.024/分钟 | 可选 |

**月成本估算** (1000 通/月，平均 2 分钟/通，美国号码):
```
号码月租：$1.50
通话费：1000 × 2 × $0.013 = $26
总计：~$27.50/月 ≈ 200 元/月
```

### 10.3 TTS 服务

| 服务 | 免费额度 | 超出价格 |
|------|----------|----------|
| ElevenLabs | 1 万字符/月 | $5-330/月 |
| 阿里云 | 50 万字符/月 | 按量计费 |
| Azure | 50 万字符/月 | 按量计费 |

---

## 11. 常见问题 FAQ

### Q1: 通话质量差/延迟高怎么办？

**A:** 检查以下几点：
1. 网络带宽是否足够 (推荐 100Mbps+)
2. 选择离客户最近的电话服务商节点
3. 启用媒体流优化配置
4. 考虑使用专线或 SD-WAN

### Q2: 如何避免被标记为骚扰电话？

**A:** 
1. 使用正规企业号码
2. 控制外呼频率 (同一号码每天不超过 3 次)
3. 在合适时间外呼 (9:00-18:00)
4. 提供退订选项
5. 遵守当地法律法规

### Q3: 通话录音如何存储和管理？

**A:**
```json5
{
  "recording": {
    "enabled": true,
    "storage": {
      "type": "s3",  // 或 local
      "bucket": "call-recordings",
      "retention": 90  // 保留 90 天
    },
    "encryption": true,
    "transcription": true
  }
}
```

### Q4: 如何处理客户投诉？

**A:**
1. 建立投诉处理流程
2. 保存完整通话记录
3. 设置投诉关键词自动标记
4. 定期回访不满意客户

### Q5: 外呼被限制/封禁怎么办？

**A:**
1. 检查是否违反服务商政策
2. 降低外呼频率
3. 申请企业白名单
4. 考虑多号码轮换

---

## 附录

### A. 相关文档链接

- [OpenClaw 官方文档](https://docs.openclaw.ai)
- [Voice Call 插件文档](https://docs.openclaw.ai/plugins/voice-call)
- [Twilio API 文档](https://www.twilio.com/docs/voice/api)
- [Stepone AI 文档](https://open-skill.steponeai.com)
- [ClawHub 技能市场](https://clawhub.ai)

### B. 示例代码仓库

```bash
# 官方示例
git clone https://github.com/openclaw/openclaw.git
cd openclaw/extensions/voice-call

# Stepone AI 技能
git clone https://github.com/ustczz/openclaw-ai-calls-china-phone.git
```

### C. 技术支持

- OpenClaw Discord 社区：https://discord.gg/clawd
- GitHub Issues: https://github.com/openclaw/openclaw/issues
- 邮件支持：support@openclaw.ai

---

**文档结束**

> 如有问题，请在 OpenClaw 社区或 GitHub 提 Issue。
