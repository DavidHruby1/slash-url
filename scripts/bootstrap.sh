#!/bin/bash

set -e

DETACH=true
SKIP_ENV_CHECK=false

usage() {
    echo "Usage: $0 [--no-detach|--foreground] [--skip-env-check]"
    echo ""
    echo "Options:"
    echo "  --no-detach, --foreground  Run docker compose in the foreground"
    echo "  --skip-env-check           Skip validation of CHANGE_ME_* placeholders"
}

for arg in "$@"; do
    case "$arg" in
        --no-detach|--foreground)
            DETACH=false
            ;;
        --skip-env-check)
            SKIP_ENV_CHECK=true
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "❌ Unknown option: $arg"
            usage
            exit 1
            ;;
    esac
done

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
    if [ ! -f .env.example ]; then
        echo "❌ .env.example not found. Cannot create .env."
        exit 1
    fi
    cp .env.example .env
    echo "✅ Created .env file"
    echo "⚠️  Please review and update ADMIN_KEY and POSTGRES_PASSWORD in .env"
    echo ""
else
    echo "✅ .env file already exists"
    echo ""
fi

if [ -f .env ] && [ "$SKIP_ENV_CHECK" = false ]; then
    PLACEHOLDERS=$(grep -E '^[A-Za-z_][A-Za-z0-9_]*=CHANGE_ME_' .env | cut -d= -f1 || true)
    if [ -n "$PLACEHOLDERS" ]; then
        echo "❌ .env contains placeholder values (CHANGE_ME_*)."
        echo "   Please update these keys before continuing:"
        echo "$PLACEHOLDERS" | sed 's/^/   - /'
        echo ""
        echo "Tip: re-run with --skip-env-check to bypass this check."
        exit 1
    fi
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

if [ "$DETACH" = true ]; then
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
else
    echo "🧭 Running in foreground. Press Ctrl+C to stop."
    echo ""
    docker compose up --build
fi
