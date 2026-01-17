# Slash URL

Self-hosted URL shortener with click analytics. One Docker Compose setup works
for local dev and VPS deployments.

## Requirements

- Docker + Docker Compose plugin

## Quick start (local)

1. Copy env file:

   `cp .env.example .env`

2. Update values in `.env` (at least `ADMIN_KEY` and `POSTGRES_PASSWORD`).
3. Start services:

   `./scripts/bootstrap.sh`

App endpoints:

- Admin UI: `http://localhost:8000/admin`
- API docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

## VPS (HTTPS via Caddy)

1. Set `CADDY_DOMAIN` in `.env` and point DNS to your VPS.
2. Deploy:

   `./scripts/deploy-vps.sh`

## API (MVP)

- `POST /api/links` (admin key required)
- `GET /api/links` (admin key required)
- `GET /api/links/{slug}/stats` (admin key required)
- `GET /{slug}` (public redirect)

## Admin auth

Send `X-Admin-Key: <ADMIN_KEY>` on all `/api/*` requests.
