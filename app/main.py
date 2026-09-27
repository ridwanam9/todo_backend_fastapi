from fastapi import FastAPI
from app.routers.todos import router as todos_router

app = FastAPI()




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


app.include_router(todos_router)