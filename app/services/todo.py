
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import todo as todo_repository
from app.schemas.todo import TodoCreate, TodoUpdate


def get_todos(db: Session, user_id: int):
    return todo_repository.get_all(db=db, user_id=user_id)


def get_todo(db: Session, todo_id: int, user_id: int):
    todo = todo_repository.get_by_id(
        db=db,
        todo_id=todo_id,
        user_id=user_id,
    )

    if todo is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found",
        )

    return todo


def create_todo(db: Session, todo: TodoCreate, user_id: int):
    return todo_repository.create(
        db=db,
        title=todo.title,
        description=todo.description,
        user_id=user_id,
    )


def update_todo(
    db: Session,
    todo_id: int,
    todo_data: TodoUpdate,
    user_id: int,
):
    todo = get_todo(
        db=db,
        todo_id=todo_id,
        user_id=user_id,
    )

    update_data = todo_data.model_dump(exclude_unset=True)

    if not update_data:
        return todo

    return todo_repository.update(
        db=db,
        todo=todo,
        update_data=update_data,
    )


def delete_todo(db: Session, todo_id: int, user_id: int):
    todo = get_todo(
        db=db,
        todo_id=todo_id,
        user_id=user_id,
    )

    todo_repository.delete(db=db, todo=todo)
