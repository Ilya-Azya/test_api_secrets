from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SecretCreate(BaseModel):
    secret: str
    passphrase: Optional[str] = None
    ttl_seconds: Optional[int] = None


class SecretResponse(BaseModel):
    secret_key: str = Field(..., alias="secret_key")


class SecretReadResponse(BaseModel):
    secret: str


class SecretDeleteRequest(BaseModel):
    passphrase: Optional[str] = None


class LogEntry(BaseModel):
    action: str
    timestamp: datetime
    ip_address: Optional[str] = None
