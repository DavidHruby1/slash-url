from fastapi import Depends, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from backend.app.auth import AdminAuthDep
from backend.app.config import settings
from backend.app.db import get_db, init_db
from backend.app.models import Click, Link
from backend.app.schemas import (
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


def add_cors_middleware(app_instance: FastAPI) -> None:
    pass


def mount_admin_ui(app_instance: FastAPI) -> None:
    pass


def is_reserved_slug(slug: str) -> bool:
    pass


def generate_slug() -> str:
    pass


def parse_user_agent(user_agent: str | None) -> dict[str, str | None]:
    pass


def normalize_referer(referer: str | None) -> str | None:
    pass


@app.on_event("startup")
def on_startup() -> None:
    pass


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    pass


@app.post("/auth/login", response_model=LoginResponse)
def login(request: LoginRequest, response: Response) -> LoginResponse:
    pass


@app.get("/auth/me", response_model=AuthMeResponse)
def auth_me(admin_session: str | None = None) -> AuthMeResponse:
    pass


@app.post("/auth/logout", response_model=LoginResponse)
def logout(response: Response) -> LoginResponse:
    pass


@app.post("/api/links", response_model=LinkResponse)
def create_link(
    request: LinkCreateRequest,
    db: Session = Depends(get_db),
    _: AdminAuthDep = None,
) -> LinkResponse:
    pass


@app.get("/api/links", response_model=LinkListResponse)
def list_links(
    limit: int = 50,
    db: Session = Depends(get_db),
    _: AdminAuthDep = None,
) -> LinkListResponse:
    pass


@app.patch("/api/links/{slug}", response_model=LinkResponse)
def update_link(
    slug: str,
    request: LinkUpdateRequest,
    db: Session = Depends(get_db),
    _: AdminAuthDep = None,
) -> LinkResponse:
    pass


@app.get("/api/links/{slug}/stats", response_model=LinkStatsResponse)
def link_stats(
    slug: str,
    filters: LinkStatsFilters = Depends(),
    db: Session = Depends(get_db),
    _: AdminAuthDep = None,
) -> LinkStatsResponse:
    pass


@app.get("/{slug}")
def redirect_slug(slug: str, db: Session = Depends(get_db)) -> RedirectResponse:
    pass
