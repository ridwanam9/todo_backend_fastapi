
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
import jwt
from jwt import InvalidTokenError

from app.core.database import get_db
from app.models.user import User
from app.repositories import user as user_repository
from app.security.token import SECRET_KEY, ALGORITHM


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized

    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        subject = payload.get("sub")

        if not isinstance(subject, str) or not subject.isdecimal():
            raise unauthorized

        user_id = int(subject)

        if user_id <= 0:
            raise unauthorized

    except (InvalidTokenError, ValueError):
        raise unauthorized

    user = user_repository.get_by_id(db=db, user_id=user_id)

    if user is None:
        raise unauthorized

    return user
