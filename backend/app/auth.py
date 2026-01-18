from fastapi import Cookie, HTTPException, Depends
from typing import Annotated
from backend.app.config import settings
import secrets


def verify_admin_cookie(admin_session: Annotated[str | None, Cookie()] = None):
    if admin_session is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if not secrets.compare_digest(admin_session, settings.admin_key):
        raise HTTPException(status_code=401, detail="Invalid admin key")

    return True

AdminAuthDep = Annotated[bool, Depends(verify_admin_cookie)]
