
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.todo import Todo


def get_all(db: Session, user_id: int):
    statement = select(Todo).where(Todo.user_id == user_id)
    return db.scalars(statement).all()


def get_by_id(db: Session, todo_id: int, user_id: int):
    statement = select(Todo).where(
        Todo.id == todo_id,
        Todo.user_id == user_id,
    )
    return db.scalars(statement).first()


def create(
    db: Session,
    title: str,
    description: str,
    user_id: int,
):
    todo = Todo(
        title=title,
        description=description,
        user_id=user_id,
    )

    try:
        db.add(todo)
        db.commit()
        db.refresh(todo)
        return todo
    except SQLAlchemyError:
        db.rollback()
        raise


def update(db: Session, todo: Todo, update_data: dict):
    try:
        for field, value in update_data.items():
            setattr(todo, field, value)

        db.commit()
        db.refresh(todo)
        return todo
    except SQLAlchemyError:
        db.rollback()
        raise


def delete(db: Session, todo: Todo):
    try:
        db.delete(todo)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
