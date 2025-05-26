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

echo "✅ 配置文件检查完成"
echo "🌐 启动服务器..."
echo "📱 访问地址: http://localhost:8888"
echo "🛑 按 Ctrl+C 停止服务"
echo ""

# 启动服务器
python web_server.py