import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker

from app.models.user import User

from app.core.database import Base, get_db
from app.main import app
from app.models.todo import Todo

TEST_DATABASE_URL = (
    "postgresql+psycopg://"
    "todo_user:todo_password@localhost:5433/todo_test_db"
)


test_engine = create_engine(
    TEST_DATABASE_URL
)


TestingSessionLocal = sessionmaker(
    bind = test_engine,
    autoflush = False,
    autocommit = False,
)


@pytest.fixture(scope="session", autouse = True)
def setup_database():
    Base.metadata.create_all(bind = test_engine)
    yield
    Base.metadata.drop_all(bind = test_engine)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.execute(delete(Todo))
        db.execute(delete(User))
        db.commit()
        db.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    email = f"{uuid4().hex}@example.com"
    password = "secret123"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }