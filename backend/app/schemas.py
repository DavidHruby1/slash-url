from pydantic import BaseModel, Field, field_validator
from pydantic.config import ConfigDict
from datetime import datetime
from typing import Optional


class LoginRequest(BaseModel):
    admin_key: str = Field(..., min_length=16, max_length=128)
