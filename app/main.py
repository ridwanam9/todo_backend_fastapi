
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.routers.todos import router as todos_router
from app.routers.auth import router as auth_router


logger = logging.getLogger(__name__)

app = FastAPI()


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(
    request: Request,
    exc: SQLAlchemyError,
):
    logger.error(
        "Database error on %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
        },
    )


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
        "version": "1.0.0",
    }


app.include_router(todos_router)
app.include_router(auth_router)
