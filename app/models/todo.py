from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(
        primary_key = True,
        index = True
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable = False
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable = False
        
    )
    completed: Mapped[bool] = mapped_column(
        Boolean,
        default = False,
        nullable = False
    )
    