from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Membuat model
class TodoCreate(BaseModel):
    title: str
    description: str


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool

# penyimpanan sementara menggunakan python sebelum ke database
todos = []

# id todo akan bertambah setiap todo ditambahkan
next_id = 1


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/hello")
def hello():
    return {"message": "Hello, Todo API!"}

@app.get("/about")
def about():
    return {
        "name": "Todo API",
        "version": "1.0.0"
        }


# create todo
@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(todo: TodoCreate):
    global next_id

    new_todo = {
        "id": next_id,
        "title": todo.title,
        "description": todo.description,
        "completed": False
    }

    todos.append(new_todo)
    next_id += 1

    return new_todo

# get todos
@app.get("/todos", response_model=list[TodoResponse])
def get_todos():
    return todos


# get todo by id
@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int):
    for todo in todos:
        if todo["id"] == todo_id:
            return todo

    raise HTTPException(
        status_code=404,
        detail="Todo not found"
    )


# update todo
@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoCreate):
    for existing_todo in todos:
        if existing_todo["id"] == todo_id:
            existing_todo["title"] = todo.title
            existing_todo["description"] = todo.description

            return existing_todo

    raise HTTPException(
        status_code=404,
        detail="Todo not found"
    )

# update todo status (complete)
@app.patch("/todos/{todo_id}", response_model=TodoResponse)
def update_todo_partial(todo_id: int, todo: TodoUpdate):

    for existing_todo in todos:
        if existing_todo["id"] == todo_id:

            update_data = todo.model_dump(exclude_unset=True)

            existing_todo.update(update_data)

            return existing_todo

    raise HTTPException(
        status_code=404,
        detail="Todo not found"
    )


# delete todo
@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    for index, todo in enumerate(todos):
        if todo["id"] == todo_id:
            todos.pop(index)
            return

    raise HTTPException(
        status_code=404,
        detail="Todo not found"
    )