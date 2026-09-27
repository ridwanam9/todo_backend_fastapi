from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.todo import Todo


def get_all(db: Session):
    statement = select(Todo)

    return db.scalars(statement).all()

def get_by_id(db: Session, todo_id: int):

    return db.get(Todo, todo_id)

def create(db: Session, title: str, description: str):
    todo = Todo(
        title = title,
        description = description
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)

    return todo

def update(db: Session, todo: Todo, update_data: dict):
    for field, value in update_data.items():
        setattr(todo, field, value)
    
    db.commit()
    db.refresh(todo)

    return todo

def delete(db: Session, todo: Todo):
    
    db.delete(todo)
    db.commit()



