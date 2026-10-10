
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories import user as user_repository
from app.schemas.user import UserCreate, LoginRequest
from app.security.password import hash_password, verify_password
from app.security.token import create_access_token


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



def login_user(db: Session, login_data: LoginRequest) -> dict:
    email = str(login_data.email).lower()

    user = user_repository.get_by_email(db=db, email=email)

    if user is None or not verify_password(
        login_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
