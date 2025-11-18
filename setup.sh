#!/bin/bash
# 项目初始化脚本

set -e

echo "🎓 AI 闪卡生成器 - 初始化脚本"
echo "================================"
echo ""

# 检查 Python
echo "✓ 检查 Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python 3。请先安装 Python 3.12+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "  Python 版本: $PYTHON_VERSION"

# 检查 Node.js
echo "✓ 检查 Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ 未找到 Node.js。请先安装 Node.js 18+"
    exit 1
fi
NODE_VERSION=$(node --version)
echo "  Node.js 版本: $NODE_VERSION"

# 检查 Docker
echo "✓ 检查 Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ 未找到 Docker。请先安装 Docker"
    exit 1
fi
echo "  Docker 已安装"

echo ""
echo "📦 设置后端..."
cd backend

# 创建虚拟环境
if [ ! -d ".venv" ]; then
    echo "  创建 Python 虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境并安装依赖
echo "  安装 Python 依赖..."
source .venv/bin/activate
pip install --upgrade pip > /dev/null
pip install -r requirements.txt

# 创建 .env 文件
if [ ! -f ".env" ]; then
    echo "  创建环境变量文件..."
    cp .env.example .env
    echo ""
    echo "⚠️  重要: 请编辑 backend/.env 文件并设置你的 OPENAI_API_KEY"
    echo ""
fi

cd ..

echo ""
echo "📦 设置前端..."
cd frontend

# 安装 Node 依赖
echo "  安装 Node.js 依赖..."
npm install

cd ..

echo ""
echo "🐳 设置 Docker..."
# 检查 Redis 容器
if docker ps -a | grep -q my-redis; then
    echo "  Redis 容器已存在"
else
    echo "  创建 Redis 容器..."
    docker run --name my-redis -d -p 6379:6379 redis:7
fi

echo ""
echo "✅ 初始化完成！"
echo ""
echo "📝 下一步："
echo "1. 编辑 backend/.env 文件，设置 OPENAI_API_KEY"
echo "2. 运行 ./start-dev.sh 启动开发服务器"
echo ""
echo "或者查看 README.md 了解更多信息"
