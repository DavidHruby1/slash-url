#!/bin/bash

set -e

echo "🚀 Deploying Slash URL to VPS..."
echo ""

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed."
    echo "   Install: https://docs.docker.com/get-docker/"
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
    echo ""
    echo "⚠️  CRITICAL: Before continuing, edit .env and set:"
    echo "   - ADMIN_KEY (use a strong random string)"
    echo "   - POSTGRES_PASSWORD (use a strong random string)"
    echo "   - CADDY_DOMAIN (your domain, e.g., example.com)"
    echo ""
    echo "   Then run this script again."
    exit 1
else
    echo "✅ .env file exists"
fi

source .env

echo ""
echo "🔍 Checking configuration..."
echo ""

if [[ "$CADDY_DOMAIN" == "example.com" ]]; then
    echo "⚠️  Warning: CADDY_DOMAIN is still set to 'example.com'"
    echo "   Make sure your DNS A record points to this VPS:"
    echo "   $CADDY_DOMAIN -> $(curl -s ifconfig.me)"
    echo ""
fi

if [[ "$ADMIN_KEY" == *"change-me"* ]]; then
    echo "⚠️  Warning: ADMIN_KEY seems to be the default."
    echo "   Please update it with a strong random string in .env!"
    echo ""
fi

echo "🐳 Building and starting services with HTTPS (Caddy)..."
echo ""

docker compose --profile proxy up -d --build

echo ""
echo "✅ Slash URL is deployed!"
echo ""
echo "📊 Services:"
docker compose ps
echo ""
echo "🌐 Verify deployment:"
echo "   - Health: https://$CADDY_DOMAIN/health"
echo "   - Admin:  https://$CADDY_DOMAIN/admin"
echo ""
echo "📝 Useful commands:"
echo "   View logs: docker compose logs -f"
echo "   Restart:   docker compose restart"
echo "   Stop:      docker compose down"
echo "   Backup DB: docker compose exec db pg_dump -U \$POSTGRES_USER \$POSTGRES_DB > backup.sql"
echo ""
echo "🔒 Firewall:"
echo "   Ensure ports 80 and 443 are open:"
echo "   ufw allow 80/tcp && ufw allow 443/tcp"
