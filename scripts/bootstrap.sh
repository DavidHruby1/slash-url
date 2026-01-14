#!/bin/bash

set -e

echo "🚀 Bootstrapping Slash URL for local development..."
echo ""

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose plugin is not installed."
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

if [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo "⚠️  Please review and update ADMIN_KEY and POSTGRES_PASSWORD in .env"
    echo ""
else
    echo "✅ .env file already exists"
    echo ""
fi

if [ ! -f compose.override.yaml ]; then
    if [ -f compose.override.yaml.example ]; then
        echo "🛠️  Setting up Dev environment (copying override config)..."
        cp compose.override.yaml.example compose.override.yaml
        echo "✅ Created compose.override.yaml"
    else
        echo "⚠️  Warning: compose.override.yaml.example not found."
        echo "   You might be running in 'Production Mode' locally (no hot-reload)."
    fi
    echo ""
else
    echo "✅ compose.override.yaml already exists"
    echo ""
fi

echo "🐳 Building and starting services..."
echo "   - Frontend dev server: http://localhost:5173"
echo "   - Backend API: http://localhost:8000"
echo "   - API docs: http://localhost:8000/docs"
echo ""

docker compose up -d --build

echo ""
echo "✅ Slash URL is running!"
echo ""
echo "📊 Services:"
docker compose ps
echo ""
echo "📝 To view logs:"
echo "   docker compose logs -f"
echo ""
echo "🛑 To stop:"
echo "   docker compose down"
