
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.user import User


def get_by_email(db: Session, email: str):
    statement = select(User).where(User.email == email)
    return db.scalars(statement).first()


def get_by_id(db: Session, user_id: int):
    return db.get(User, user_id)


def create(
    db: Session,
    email: str,
    password_hash: str,
):
    user = User(
        email=email,
        password_hash=password_hash,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    except SQLAlchemyError:
        db.rollback()
        raise
