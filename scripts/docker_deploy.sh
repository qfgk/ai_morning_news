#!/bin/bash
# Docker 快速部署脚本

set -e

echo "============================================================"
echo " Morning News System - Docker Deployment"
echo "============================================================"

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Error: Docker Compose is not installed"
    echo "Please install Docker Compose first"
    exit 1
fi

# 检查 .env 文件
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.docker.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file and set:"
    echo "   - ZHIPUAI_API_KEY"
    echo "   - API_KEY"
    echo ""
    read -p "Press Enter after editing .env file..."
fi

# 生成 API 密钥
if grep -q "your-secret-api-key-here" .env 2>/dev/null || grep -q "your-api-key-here" .env 2>/dev/null; then
    echo ""
    echo "Generating API key..."
    python scripts/generate_api_key.py

    # 提示用户更新 .env
    echo ""
    echo "⚠️  Please update API_KEY in .env file with the generated key above"
    read -p "Press Enter after updating .env file..."
fi

# 构建镜像
echo ""
echo "Building Docker images..."
docker-compose build

# 启动服务
echo ""
echo "Starting services..."
docker-compose up -d

# 等待服务启动
echo ""
echo "Waiting for services to be ready..."
sleep 10

# 检查服务状态
echo ""
echo "Checking service status..."
docker-compose ps

# 初始化数据库
echo ""
echo "Initializing database..."
docker-compose exec -T web python scripts/init_db.py

echo ""
echo "============================================================"
echo "✅ Deployment completed!"
echo "============================================================"
echo ""
echo "Services:"
echo "  - Web API:  http://localhost:5000"
echo "  - MySQL:    localhost:3306"
echo "  - Redis:    localhost:6379"
echo ""
echo "Commands:"
echo "  - View logs:     docker-compose logs -f"
echo "  - Stop all:      docker-compose down"
echo "  - Restart:       docker-compose restart"
echo "  - Shell access:  docker-compose exec web bash"
echo ""
echo "API Health Check:"
curl -s http://localhost:5000/health | python -m json.tool || echo "Service not ready yet"
echo ""
