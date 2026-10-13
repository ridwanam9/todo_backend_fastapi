import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
except ValueError as exc:
    raise RuntimeError(
        "ACCESS_TOKEN_EXPIRE_MINUTES must be an integer"
    ) from exc

if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not configured")

if len(SECRET_KEY.encode("utf-8")) < 32:
    raise RuntimeError(
        "JWT_SECRET_KEY must be at least 32 bytes long"
    )

if ACCESS_TOKEN_EXPIRE_MINUTES <= 0:
    raise RuntimeError(
        "ACCESS_TOKEN_EXPIRE_MINUTES must be positive"
    )

configured_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
if configured_algorithm != ALGORITHM:
    raise RuntimeError("JWT_ALGORITHM must be HS256")


def create_access_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
) -> str:
    lifetime = (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    if lifetime.total_seconds() <= 0:
        raise ValueError("Token lifetime must be positive")

    now = datetime.now(timezone.utc)
    expires_at = now + lifetime

    payload = {
        "sub": str(subject),
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
