"""add users and todo user_id

Revision ID: 5e381cfbee5b
Revises: 0e70ddae1964
Create Date: 2026-09-28 18:22:03.715860

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e381cfbee5b'
down_revision: Union[str, Sequence[str], None] = '0e70ddae1964'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_users_email",
        "users",
        ["email"],
        unique=True,
    )

    # Add user_id to the existing todos table.
    # This migration assumes the development database has been reset.
    op.add_column(
        "todos",
        sa.Column("user_id", sa.Integer(), nullable=False),
    )

    op.create_foreign_key(
        "fk_todos_user_id_users",
        "todos",
        "users",
        ["user_id"],
        ["id"],
    )

    op.create_index(
        "ix_todos_user_id",
        "todos",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_todos_user_id", table_name="todos")

    op.drop_constraint(
        "fk_todos_user_id_users",
        "todos",
        type_="foreignkey",
    )

    op.drop_column("todos", "user_id")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
