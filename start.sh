#!/bin/bash
# 股票分析系统启动脚本

echo "🚀 启动股票分析系统..."

# 激活虚拟环境
source stock_env/bin/activate

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "❌ 未找到 .env 配置文件，请先配置API密钥"
    echo "请编辑 .env 文件，设置以下必要参数："
    echo "  API_KEY=你的API密钥"
    echo "  API_URL=你的API地址"
    echo "  API_MODEL=你的模型名称"
    exit 1
fi

echo "📋 检查环境变量配置..."

# 读取并验证关键配置
source .env

# 检查API_URL
if [ -z "$API_URL" ]; then
    echo "❌ API_URL 未设置"
    exit 1
else
    echo "✅ API_URL: $API_URL"
fi

# 检查API_KEY
if [ -z "$API_KEY" ] || [ "$API_KEY" = "your_openrouter_api_key_here" ]; then
    echo "❌ API_KEY 未设置或使用默认值，请设置真实的API密钥"
    exit 1
else
    # 隐藏API密钥，只显示前8位和后4位
    masked_key="${API_KEY:0:8}...${API_KEY: -4}"
    echo "✅ API_KEY: $masked_key"
fi

# 检查API_MODEL
if [ -z "$API_MODEL" ]; then
    echo "⚠️  API_MODEL 未设置，将使用默认值"
else
    echo "✅ API_MODEL: $API_MODEL"
fi

# 检查API_TIMEOUT
if [ -z "$API_TIMEOUT" ]; then
    echo "⚠️  API_TIMEOUT 未设置，将使用默认值"
else
    echo "✅ API_TIMEOUT: ${API_TIMEOUT}秒"
fi

echo "✅ 配置文件检查完成"
echo "🌐 启动服务器..."
echo "📱 访问地址: http://localhost:8888"
echo "🛑 按 Ctrl+C 停止服务"
echo ""

# 启动服务器
python web_server.py