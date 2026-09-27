from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)