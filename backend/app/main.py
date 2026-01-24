from fastapi import Depends, FastAPI, Response, Cookie, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Annotated
import secrets
import hashlib

from backend.app.auth import AdminAuthDep
from backend.app.config import settings
from backend.app.db import get_db, init_db
from backend.app.models import Click, Link
from backend.app.schemas import (
    LoginResponse,
    AuthMeResponse,
    HealthResponse,
    LinkCreateRequest,
    LinkListResponse,
    LinkResponse,
    LinkStatsResponse,
    LinkUpdateRequest,
    LoginRequest,
)


app = FastAPI()
origins = [
    settings.cors_origins
]


# Won't be needed actually, but keep it for now
def add_cors_middleware(app_instance: FastAPI) -> None:
    app_instance.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
        allow_headers=["Content-Type"]
    )


def mount_admin_ui(app_instance: FastAPI) -> None:
    # Ignore for now
    pass


def slug_hash(url: str) -> str:
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    digest = hashlib.sha256(url.encode('utf-8')).digest()
    return "".join(alphabet[b % 62] for b in digest[:8])


def check_unique_slug(slug: str, db: Session) -> bool:
    stmt = select(Link).where(Link.slug == slug)
    result = db.execute(stmt).scalar_one_or_none()
    return result is None


def add_salt(url: str) -> str:
    salt = secrets.token_hex(4)
    new_url = url + salt
    return hash_slug(new_url)


def generate_slug(url: str) -> str:
    slug = slug_hash(url)
    
    if check_unique_slug:
        return slug
    
    return add_salt(slug)


def generate_title() -> str:
    # Look at the database and look if there is anything starting with "Title"
    # Then look for the highest number and once acquired, add +1 to it
    # Create new title: "Title_{number}" and return
    pass


def parse_user_agent(user_agent: str | None) -> dict[str, str | None]:
    pass


def normalize_referer(referer: str | None) -> str | None:
    pass


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    add_cors_middleware() # Maybe ignored idk yet


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(ok=True)


@app.post("/auth/login", response_model=LoginResponse)
def login(request: LoginRequest, response: Response) -> LoginResponse:
    if not secrets.compare_digest(request.admin_key, settings.admin_key):
        raise HTTPException(status_code=401, detail="Invalid admin key")
    
    max_age = 100 * 365 * 24 * 60 * 60 if request.remember_me else None

    response.set_cookie(
        key="admin_session",
        value=request.admin_key,
        httponly=True,
        samesite="lax", # strict for production
        secure=False, # True for production
        max_age=max_age,
        path="/"
    )

    return LoginResponse(
        success=True,
        message="Logged in"
    )


@app.get("/auth/me", response_model=AuthMeResponse)
def auth_me(admin_session: Annotated[str | None, Cookie()] = None) -> AuthMeResponse:
    if admin_session is not None and secrets.compare_digest(admin_session, settings.admin_key):
        authenticated = True
    else:
        authenticated = False

    return AuthMeResponse(authenticated=authenticated)


@app.post("/auth/logout", response_model=LoginResponse)
def logout(response: Response) -> LoginResponse:
    response.delete_cookie(
        key="admin_session",
        path="/",
        samesite="lax", # strict for production
        secure=False, # True for production
    )

    return LoginResponse(
        success=True,
        message="Logged out"
    )


@app.post("/api/links", response_model=LinkResponse)
def create_link(
    request: LinkCreateRequest,
    db: Session = Depends(get_db),
    _: AdminAuthDep,
) -> LinkResponse:
    url = request.original_url
    title = request.title or generate_title()
    slug = request.slug or generate_slug(url)

    data = {
        "original_url": url,
        "slug": slug,
        "title": title,
    }

    if request.is_active is not None:
        data["is_active"] = request.is_active
    if request.expires_at is not None:
        data["expires_at"] = request.expires_at
    if request.max_clicks is not None:
        data["max_clicks"] = request.max_clicks

    link = Link(**data)

    try:
        db.add(link)
        db.commit()
        db.refresh(link)

        return LinkResponse(
            id=link.id,
            original_url=link.original_url,
            slug=link.slug,
            title=link.title,
            clicks=link.clicks,
            created_at=link.created_at,
            is_active=link.is_active,
            expires_at=link.expires_at,
            max_clicks=link.max_clicks
        )
    except Exception as e:
        db.rollback()
        raise e

    
@app.get("/api/links", response_model=LinkListResponse)
def list_links(
    limit: int = 50,
    db: Session = Depends(get_db),
    _: AdminAuthDep,
) -> LinkListResponse:
    pass


@app.patch("/api/links/{slug}", response_model=LinkResponse)
def update_link(
    slug: str,
    request: LinkUpdateRequest,
    db: Session = Depends(get_db),
    _: AdminAuthDep,
) -> LinkResponse:
    pass


@app.get("/api/links/{slug}/stats", response_model=LinkStatsResponse)
def link_stats(
    slug: str,
    filters: LinkStatsFilters = Depends(),
    db: Session = Depends(get_db),
    _: AdminAuthDep,
) -> LinkStatsResponse:
    pass


@app.get("/{slug}")
def redirect_slug(slug: str, db: Session = Depends(get_db)) -> RedirectResponse:
    pass
