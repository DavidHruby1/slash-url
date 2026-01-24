from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.config import ConfigDict
from datetime import datetime, timezone
from typing import Optional
import re
from urllib.parse import urlparse
import ipaddress


SLUG_MIN_LEN = 3
SLUG_MAX_LEN = 64
TITLE_MAX_LEN = 64
RESERVED_SLUGS = ("admin", "health", "static", "assets", "api")
SLUG_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
RESERVED_SLUG_PATTERN = re.compile(
    r'^(?:' + "|".join(RESERVED_SLUGS) + r')(?:$|[-_])',
    re.IGNORECASE
)


def _validate_slug_value(slug: Optional[str]) -> Optional[str]:
    """Validate slug and raise ValueError if invalid.

    Used by:
    - LinkCreateRequest.validate_slug() (line 118)
    - LinkUpdateRequest.validate_slug() (line 174)
    """
    if slug is None:
        return slug
    if len(slug) < SLUG_MIN_LEN or len(slug) > SLUG_MAX_LEN:
        raise ValueError(f"length must be between {SLUG_MIN_LEN}-{SLUG_MAX_LEN}")
    if slug.startswith("__"):
        raise ValueError("invalid slug")
    if RESERVED_SLUG_PATTERN.match(slug):
        raise ValueError("forbidden slug name")
    if not SLUG_PATTERN.fullmatch(slug):
        raise ValueError("invalid characters")

    return slug


def _validate_slug_format(slug: Optional[str]) -> Optional[str]:
    """Validate slug characters only.

    Used by:
    - LinkDeleteRequest.validate_slugs() (line 215)
    """
    if slug is None:
        return slug
    if not SLUG_PATTERN.fullmatch(slug):
        raise ValueError("invalid characters")

    return slug


def _validate_title_value(title: Optional[str]) -> Optional[str]:
    """Validate title and raise ValueError if invalid.

    Used by:
    - LinkCreateRequest.validate_title() (line 124)
    - LinkUpdateRequest.validate_title() (line 178)
    """
    if title is None:
        return title

    stripped = title.strip()
    if not stripped:
        raise ValueError("Title cannot be empty")
    if len(stripped) > TITLE_MAX_LEN:
        raise ValueError(f"Title length must be between 1-{TITLE_MAX_LEN}")

    return stripped


def _validate_expires_at_value(expires_at: Optional[datetime]) -> Optional[datetime]:
    """Validate expires_at and raise ValueError if invalid.

    Used by:
    - LinkCreateRequest.validate_expires_at() (line 150)
    - LinkUpdateRequest.validate_expires_at() (line 204)
    """
    if expires_at is None:
        return expires_at
    if expires_at.tzinfo is None or expires_at.utcoffset() is None:
        raise ValueError("Expiration date must include timezone offset")
    if expires_at <= datetime.now(timezone.utc):
        raise ValueError("Expiration date must be in the future")

    return expires_at


def _validate_max_clicks_value(max_clicks: Optional[int]) -> Optional[int]:
    """Validate max_clicks and raise ValueError if invalid.

    Used by:
    - LinkCreateRequest.validate_max_clicks() (line 160)
    - LinkUpdateRequest.validate_max_clicks() (line 214)
    """
    if max_clicks is not None and max_clicks <= 0:
        raise ValueError("max_clicks must be greater than 0")

    return max_clicks


class LoginRequest(BaseModel):
    admin_key: str = Field(..., min_length=16, max_length=128)
    remember_me: bool = False


class LinkCreateRequest(BaseModel):
    original_url: str
    slug: Optional[str] = None
    title: Optional[str] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None
    max_clicks: Optional[int] = None

    @model_validator(mode="before")
    @classmethod
    def reject_null_fields(cls, data: object) -> object:
        if isinstance(data, dict):
            for key in ("slug", "title"):
                if key in data:
                    value = data[key]
                    if value is None:
                        data.pop(key)
                    elif isinstance(value, str) and not value.strip():
                        data.pop(key)
            for key in ("is_active", "expires_at", "max_clicks"):
                if key in data and data[key] is None:
                    raise ValueError(f"{key} cannot be null")
        return data

    @field_validator("original_url")
    @classmethod
    def validate_original_url(cls, original_url: str) -> str:
        url = original_url.strip()
        if not url:
            raise ValueError("Invalid URL address")
        if any(char.isspace() for char in url):
            raise ValueError("Invalid URL address")
        if re.match(r'^https?:', url, re.IGNORECASE) and not re.match(
            r'^https?://', url, re.IGNORECASE
        ):
            raise ValueError("Invalid URL address")
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', url):
            url = 'https://' + url

        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("Invalid URL address")

        hostname = parsed.hostname
        if hostname is None:
            raise ValueError("Invalid URL address")
        if hostname.lower() == "localhost":
            raise ValueError("Unsafe URL address")

        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_loopback or ip.is_private or ip.is_link_local:
                raise ValueError("Unsafe URL address")
        except ValueError:
            pass

        return url

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, slug: Optional[str]) -> Optional[str]:
        return _validate_slug_value(slug)

    @field_validator("title")
    @classmethod
    def validate_title(cls, title: Optional[str]) -> Optional[str]:
        return _validate_title_value(title)

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at(cls, expires_at: Optional[datetime]) -> Optional[datetime]:
        return _validate_expires_at_value(expires_at)

    @field_validator("max_clicks")
    @classmethod
    def validate_max_clicks(cls, max_clicks: Optional[int]) -> Optional[int]:
        return _validate_max_clicks_value(max_clicks)


class LinkUpdateRequest(BaseModel):
    slug: Optional[str] = None
    title: Optional[str] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None
    max_clicks: Optional[int] = None

    @model_validator(mode="before")
    @classmethod
    def reject_null_fields(cls, data: object) -> object:
        if isinstance(data, dict):
            for key in ("slug", "title"):
                if key in data:
                    value = data[key]
                    if value is None:
                        data.pop(key)
                    elif isinstance(value, str) and not value.strip():
                        data.pop(key)
            for key in ("is_active", "expires_at", "max_clicks"):
                if key in data and data[key] is None:
                    raise ValueError(f"{key} cannot be null")
        return data

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, slug: Optional[str]) -> Optional[str]:
        return _validate_slug_value(slug)

    @field_validator("title")
    @classmethod
    def validate_title(cls, title: Optional[str]) -> Optional[str]:
        return _validate_title_value(title)

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at(cls, expires_at: Optional[datetime]) -> Optional[datetime]:
        return _validate_expires_at_value(expires_at)

    @field_validator("max_clicks")
    @classmethod
    def validate_max_clicks(cls, max_clicks: Optional[int]) -> Optional[int]:
        return _validate_max_clicks_value(max_clicks)


class LinkDeleteRequest(BaseModel):
    slugs: list[str] = Field(..., min_length=1, max_length=100, strict=True)

    @field_validator("slugs")
    @classmethod
    def validate_slugs(cls, slugs: list[str]) -> list[str]:
        return [_validate_slug_format(slug) for slug in slugs]


class LoginResponse(BaseModel):
    success: bool
    message: str


class AuthMeResponse(BaseModel):
    authenticated: bool


class HealthResponse(BaseModel):
    ok: bool


class LinkResponse(BaseModel):
    id: int
    original_url: str
    slug: str
    title: str
    clicks: int
    created_at: datetime
    is_active: bool
    expires_at: Optional[datetime]
    max_clicks: Optional[int]

    model_config = ConfigDict(from_attributes=True)


class LinkListResponse(BaseModel):
    links: list[LinkResponse]
    total: int


class ClickByDay(BaseModel):
    date: str
    clicks: int


class ReferrerStat(BaseModel):
    referrer: str
    clicks: int


class DeviceStat(BaseModel):
    device: str
    clicks: int


class BrowserStat(BaseModel):
    browser: str
    clicks: int


class OSStat(BaseModel):
    os: str
    clicks: int


class LinkStatsResponse(BaseModel):
    slug: str
    total_clicks: int
    clicks_by_day: list[ClickByDay]
    top_referrers: list[ReferrerStat]
    devices: list[DeviceStat]
    browsers: list[BrowserStat]
    os: list[OSStat]
