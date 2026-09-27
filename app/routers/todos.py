from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse
from app.services import todo as todo_service


router = APIRouter(
    prefix="/todos",
    tags=["Todos"]
)


@router.post(
    "",
    response_model=TodoResponse,
    status_code=201
)
def create_todo(
    todo: TodoCreate,
    db: Session = Depends(get_db)
):
    return todo_service.create_todo(
        db=db,
        todo=todo
    )


@router.get(
    "",
    response_model=list[TodoResponse]
)
def get_todos(
    db: Session = Depends(get_db)
):
    return todo_service.get_todos(db)


@router.get(
    "/{todo_id}",
    response_model=TodoResponse
)
def get_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    return todo_service.get_todo(
        db=db,
        todo_id=todo_id
    )


@router.patch(
    "/{todo_id}",
    response_model=TodoResponse
)
def update_todo_partial(
    todo_id: int,
    todo: TodoUpdate,
    db: Session = Depends(get_db)
):
    return todo_service.update_todo(
        db=db,
        todo_id=todo_id,
        todo_data=todo
    )


@router.delete(
    "/{todo_id}",
    status_code=204
)
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    todo_service.delete_todo(
        db=db,
        todo_id=todo_id
    )