# 🚀 OpenRouter API 配置指南

## 🌟 为什么选择 OpenRouter？

[OpenRouter](https://openrouter.ai/) 是一个统一的LLM接口平台，具有以下优势：

- 💰 **更优价格**：比官方API更便宜
- 🔄 **更高可用性**：分布式基础设施，自动故障转移
- 🎯 **多模型支持**：300+ 模型，50+ 提供商
- 🔌 **完全兼容**：OpenAI SDK 开箱即用
- 🛡️ **数据保护**：细粒度数据策略控制

## 📋 概述

OpenRouter 是一个统一的AI模型API平台，提供对多种大语言模型的访问，包括 OpenAI、Anthropic、Google、Meta 等厂商的模型。

## 🔧 配置步骤

### 1. 注册 OpenRouter 账户

1. 访问 [OpenRouter官网](https://openrouter.ai/)
2. 点击右上角 "Sign Up" 注册账户
3. 使用邮箱或 GitHub 账户注册

### 2. 获取 API 密钥

1. 登录后，点击右上角头像
2. 选择 "API Keys"
3. 点击 "Create Key" 创建新的API密钥
4. 复制生成的API密钥（格式：`sk-or-v1-...`）

### 3. 账户充值

1. 在控制台中选择 "Credits"
2. 点击 "Add Credits" 充值
3. 支持信用卡和加密货币支付
4. 建议首次充值 $5-10 用于测试

### 4. 配置系统

#### 方法一：修改 .env 文件

```bash
# 编辑配置文件
nano .env
```

更新以下配置：

```env
API_KEY=sk-or-v1-your-actual-api-key-here
API_URL=https://openrouter.ai/api/v1/chat/completions
API_MODEL=anthropic/claude-3.5-sonnet
API_TIMEOUT=60
LOGIN_PASSWORD=admin123
ANNOUNCEMENT_TEXT=欢迎使用股票分析系统！投资有风险，入市需谨慎。
```

**⚠️ 重要提醒：**
- 正确的API端点是：`https://openrouter.ai/api/v1/chat/completions`
- **不是** `https://openrouter.ai/api/v1`
- 必须包含完整的 `/chat/completions` 路径

#### 方法二：在网页界面配置

1. 访问 http://localhost:8888
2. 登录系统（密码：admin123）
3. 在设置页面填入：
   - **API URL**: `https://openrouter.ai/api/v1/chat/completions`
   - **API Key**: 你的OpenRouter API密钥
   - **模型**: 选择合适的模型

## 🎯 推荐模型

### 高性能模型
```bash
# Claude 3.5 Sonnet（推荐）
API_MODEL=anthropic/claude-3.5-sonnet

# GPT-4 Turbo
API_MODEL=openai/gpt-4-turbo

# Claude 3 Opus（最强推理）
API_MODEL=anthropic/claude-3-opus
```

### 性价比模型
```bash
# Claude 3 Haiku（快速便宜）
API_MODEL=anthropic/claude-3-haiku

# GPT-3.5 Turbo
API_MODEL=openai/gpt-3.5-turbo

# Llama 3.1 70B
API_MODEL=meta-llama/llama-3.1-70b-instruct
```

### 开源模型
```bash
# Qwen 2.5 72B
API_MODEL=qwen/qwen-2.5-72b-instruct

# Mixtral 8x7B
API_MODEL=mistralai/mixtral-8x7b-instruct

# DeepSeek V2.5
API_MODEL=deepseek/deepseek-chat
```

## 💰 费用说明

- OpenRouter 按实际使用的token计费
- 不同模型价格不同，详见 [定价页面](https://openrouter.ai/models)
- 支持设置使用限额防止超支
- 可以查看详细的使用统计

## 🚀 重启服务

配置完成后，重启服务以应用新配置：

```bash
# 停止当前服务
pkill -f web_server.py

# 重新启动
./start.sh
```

## 💡 使用技巧

### 1. 模型选择策略
- **股票分析**：推荐 `claude-3.5-sonnet`（分析能力强）
- **快速查询**：使用 `claude-3-haiku`（速度快，成本低）
- **复杂推理**：选择 `claude-3-opus`（最强推理能力）

### 2. 成本控制
```bash
# 查看模型价格
curl https://openrouter.ai/api/v1/models

# 设置合理的超时时间
API_TIMEOUT=30
```

### 3. 错误处理
- OpenRouter 会自动在提供商之间进行故障转移
- 如果某个模型不可用，会自动切换到备用提供商

## 📊 价格对比

| 模型 | OpenRouter 价格 | 官方价格 | 节省 |
|------|----------------|----------|------|
| GPT-4 Turbo | $10/1M tokens | $10/1M tokens | 相同 |
| Claude 3.5 Sonnet | $3/1M tokens | $3/1M tokens | 相同 |
| Claude 3 Haiku | $0.25/1M tokens | $0.25/1M tokens | 相同 |

*注：OpenRouter 的优势在于可用性和统一接口，价格通常与官方相同或更优*

## 🔍 监控和调试

### 查看请求日志
```bash
# 实时查看服务日志
tail -f server.log

# 查看API调用情况
grep "API" server.log
```

### OpenRouter 控制台
- 登录 OpenRouter 查看使用统计
- 监控API调用次数和成本
- 查看错误日志和性能指标

## ⚠️ 注意事项

1. **API密钥安全**：不要将密钥提交到代码仓库
2. **使用限制**：注意OpenRouter的使用条款
3. **成本控制**：定期检查使用量，避免超支
4. **模型可用性**：某些模型可能有地区限制

## 🆘 故障排除

### 常见问题

1. **401 Unauthorized**
   - 检查API密钥是否正确
   - 确认账户有足够余额

2. **模型不可用**
   - 尝试切换到其他模型
   - 检查模型名称是否正确

3. **请求超时**
   - 增加 `API_TIMEOUT` 值
   - 选择响应更快的模型

### 测试连接
```bash
# 测试API连接
curl -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "anthropic/claude-3-haiku",
    "messages": [
      {"role": "user", "content": "Hello"}
    ]
  }'
```

## 📚 更多资源

- [OpenRouter 官方文档](https://openrouter.ai/docs)
- [模型列表和定价](https://openrouter.ai/models)
- [API 参考](https://openrouter.ai/docs/api-reference)
- [社区支持](https://discord.gg/openrouter)

---

**配置完成后，你就可以享受更稳定、更便宜的AI服务了！** 🎉