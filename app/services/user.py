
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories import user as user_repository
from app.schemas.user import UserCreate
from app.security.password import hash_password


def register_user(db: Session, user_data: UserCreate):
    email = str(user_data.email).lower()

    existing_user = user_repository.get_by_email(
        db=db,
        email=email,
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    hashed_password = hash_password(user_data.password)

    try:
        return user_repository.create(
            db=db,
            email=email,
            password_hash=hashed_password,
        )

    except IntegrityError:
        # Menangani kemungkinan dua request mendaftarkan
        # email yang sama secara bersamaan.
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )
