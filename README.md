# 🔗 Slash URL - (**STILL IN DEVELOPMENT**)

A self-hosted URL shortener with click analytics, built with **FastAPI**, **React**, and **PostgreSQL**. Currently in **foundation phase** – database models, auth layer, and infrastructure are complete.

## 🚀 Quick Start

**Prerequisites:** Docker + Docker Compose plugin

```bash
git clone https://github.com/DavidHruby1/slash-url.git
cd slash-url

# Configure environment
cp .env.example .env
# Edit .env: set ADMIN_KEY (min 16 chars) and POSTGRES_PASSWORD

# Start all services
./scripts/bootstrap.sh
```

## ✨ Current State (Foundation Phase)

### ✅ Complete
- **Database Models:** SQLAlchemy ORM with proper indexing (Link, Click with CASCADE delete)
- **Session Management:** Dependency injection for DB sessions with lifecycle handling
- **Configuration:** Pydantic settings with runtime validation (`ADMIN_KEY` min 16 chars)
- **Auth Dependency:** Cookie-based admin verification with timing-attack protection
- **Infrastructure:** Docker Compose setup for local dev and production

### 🚧 To Be Implemented
- API endpoints (link CRUD, public redirect, statistics)
- Auth endpoints (`/auth/login`, `/auth/me`, `/auth/logout`)
- React admin UI at `/admin`

## 📂 Project Structure

```text
backend/app/
├── config.py          # Pydantic settings with validation
├── db.py              # SQLAlchemy session & engine
├── models.py          # ORM models (Link, Click)
├── auth.py            # Cookie-based auth dependency
├── schemas.py         # Pydantic validation schemas
└── main.py            # FastAPI app (empty - pending implementation)

frontend/src/          # React admin UI (placeholder)

docker/
├── Dockerfile.backend # Python 3.11 runtime
├── Dockerfile.db      # PostgreSQL 16
└── Caddyfile          # HTTPS reverse proxy

scripts/
├── bootstrap.sh       # Local development setup
└── deploy-vps.sh      # Production deployment
```

## 🧠 Engineering Decisions

### 1. Database Models: Composite Indexes for Analytics

The `Click` model uses a composite index on `(link_id, clicked_at)` to optimize queries that fetch click statistics for a specific link ordered by time.

```python
__table_args__ = (
    Index('ix_clicks_link_id_clicked_at', 'link_id', 'clicked_at'),
)
```

### 2. Cookie Auth with Timing-Attack Protection

Admin authentication uses `secrets.compare_digest()` to prevent timing attacks when comparing cookie values. The auth dependency (`verify_admin_cookie`) can be injected into any protected route.

**Why not JWT?** For a single-admin use case, httpOnly cookies are simpler and sufficient. No token expiration logic needed – the cookie is valid until manually cleared via logout.

### 3. Pydantic for Configuration Safety

All environment variables go through Pydantic validation before the app starts. This fails fast if `ADMIN_KEY` is too short or required values are missing.

```python
ADMIN_KEY: str = Field(min_length=16, description="Admin authentication key")
```

## 🐳 Deployment

### Local Development
```bash
./scripts/bootstrap.sh    # Builds and starts all services
```

### Production (VPS with HTTPS)
```bash
# Set CADDY_DOMAIN=your-domain.com in .env
./scripts/deploy-vps.sh   # Deploys with automatic HTTPS via Caddy
```

**Services:** | Backend | Database | Caddy (HTTPS) |
---------------|---------|----------|---------------|
**Port** | 8000 | 5432 | 443/80 |

## 📋 Data Models

### Link
| Field | Type | Description |
|-------|------|-------------|
| `slug` | String(64) | Unique URL slug (indexed) |
| `title` | String(64) | Unique display title |
| `original_url` | String | Target URL |
| `clicks` | Integer | Click counter (default: 0) |
| `is_active` | Boolean | Active status (default: true) |
| `expires_at` | Timestamptz | Optional expiration |
| `max_clicks` | Integer | Optional click limit |

### Click (Analytics)
| Field | Type | Description |
|-------|------|-------------|
| `clicked_at` | Timestamptz | Timestamp of click |
| `user_agent` | String | Browser user agent |
| `referer` | String | HTTP referer |
| `device` | String | Device type |
| `browser` | String | Browser type |
| `os` | String | Operating system |
| `link_id` | Foreign Key | CASCADE delete to Link |

---

[Report Bug](../../issues) | [License](LICENSE)
