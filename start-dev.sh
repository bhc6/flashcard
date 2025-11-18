#!/bin/bash
# 项目启动脚本 - 用于本地开发环境

echo "🚀 启动 AI 闪卡生成器开发环境..."

# 检查是否安装了必需的工具
command -v python3 >/dev/null 2>&1 || { echo "❌ 需要安装 Python 3"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ 需要安装 Node.js"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ 需要安装 Docker"; exit 1; }

# 启动 Redis
echo "📦 启动 Redis 容器..."
docker ps | grep my-redis > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Redis 已经在运行"
else
    docker start my-redis > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "🔄 创建新的 Redis 容器..."
        docker run --name my-redis -d -p 6379:6379 redis:7
    fi
    echo "✅ Redis 已启动"
fi

echo ""
echo "📝 下一步："
echo "1. 打开终端 1，运行后端 Celery Worker:"
echo "   cd backend && source .venv/bin/activate && celery -A app.celery_app worker --loglevel=info"
echo ""
echo "2. 打开终端 2，运行后端 Flask API:"
echo "   cd backend && source .venv/bin/activate && python app.py"
echo ""
echo "3. 打开终端 3，运行前端开发服务器:"
echo "   cd frontend && npm run dev"
echo ""
echo "✨ 完成后，访问 http://localhost:3000"
