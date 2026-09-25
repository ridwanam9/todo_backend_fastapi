from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Membuat model
class Todo(BaseModel):
    title: str
    description: str
    completed: bool = False

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
@app.post("/todos")
def create_todo(todo: Todo):
    global next_id

    new_todo = {
        "id": next_id,
        "title": todo.title,
        "description": todo.description,
        "completed": todo.completed
    }

    todos.append(new_todo)
    next_id += 1

    return new_todo


# get todos
@app.get("/todos")
def get_todos():
    return todos


# get todo by id
@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    for todo in todos:
        if todo["id"] == todo_id:
            return todo

    return {"Message: Todo not found"}

# update todo
@app.put("/todos/{todo_id}")
def update_todo(todo_id : int, todo: Todo):
    for index, existing_todo in enumerate(todos):
        if existing_todo["id"] == todo_id:

            updated_todo = {
                "id": todo_id,
                "title": todo.title,
                "description": todo.description,
                "completed": todo.completed
            }

            todos[index] = updated_todo
            return updated_todo

    return {"Message: Todo not found"}

# delete todo
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    for index, todo in enumerate(todos):
        if todo["id"] == todo_id:
            deleted_todo = todos.pop(index)
            return deleted_todo

    return {"Message: Todo not found"}