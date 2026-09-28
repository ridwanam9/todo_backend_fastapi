from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.main import app
from app.repositories import todo as todo_repository


# client = TestClient(app)

# cek health
def test_health_check(client):

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status" : "ok"
    }

# create todos
def test_create_todo(client):
    response = client.post(
        "/todos", 
        json = {

            "title": "Test todo",
            "description": "Testing FastAPI"
        }
    )

    assert response.status_code == 201
    data = response.json()

    assert data["title"] == "Test todo"
    assert data["description"] == "Testing FastAPI"
    assert data["completed"] is False
    assert "id" in data

# get todos
def test_get_todos(client):
    response = client.get("/todos")

    assert response.status_code == 200

    assert isinstance(response.json(), list)


# get todo by id
def test_get_todo(client):
    create_response = client.post(
        "/todos", 
        json = {

            "title": "Todo untuk GET",
            "description": "Testing GET by ID"
        }
    )

    todo_id = create_response.json()["id"]

    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == todo_id
    assert data["title"] == "Todo untuk GET"


# test get todo not found
def test_get_todo_not_found(client):
    response = client.get("/todos/999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail" : "Todo not found"
    }


# test patch todo
def test_update_todo(client):
    create_response = client.post(
        "/todos", 
        json = {

            "title": "Test lama",
            "description": "Description lama"
        }
    )

    todo_id = create_response.json()["id"]
    
    response = client.patch(
        f"/todos/{todo_id}", 
        json = {

            "completed": True,
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == todo_id
    assert data["title"] == "Test lama"
    assert data["description"] == "Description lama"
    assert data["completed"] is True


# test delete todo
def test_delete_todo(client):
    create_response = client.post(
        "/todos", 
        json = {
            "title": "Todo untuk delete",
            "description": "Akan dihapus"
        }
    )

    todo_id = create_response.json()["id"]
    
    response = client.delete(
        f"/todos/{todo_id}"
    )
    assert response.status_code == 204

    get_response = client.get(
        f"/todos/{todo_id}"
    )
    assert get_response.status_code == 404
    

# test update todo not found
def test_update_todo_not_found(client):
    response = client.patch(
        "/todos/999999",
        json={
            "completed": True
        }
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail" : "Todo not found"
    }

# test delete todo not found
def test_delete_todo_not_found(client):
    response = client.delete(
        "/todos/999999"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail" : "Todo not found"
    }

# create todo without title
def test_create_todo_missing_title(client):
    response = client.post(
        "/todos",
        json={
            "description":"Todo tanpa title"
        }
    )

    assert response.status_code == 422

# create todo without description
def test_create_todo_missing_title(client):
    response = client.post(
        "/todos",
        json={
            "title":"Todo tanpa description"
        }
    )

    assert response.status_code == 422


# test patch todo empty body
def test_update_todo_empty_body(client):
    create_response = client.post(
        "/todos", 
        json = {

            "title": "Todo test",
            "description": "Testing empty patch"
        }
    )

    todo_id = create_response.json()["id"]
    
    response = client.patch(
        f"/todos/{todo_id}", 
        json = {}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["title"] == "Todo test"
    assert data["description"] == "Testing empty patch"
    assert data["completed"] is False


# test patch todo wrong data type
def test_update_todo_invalid_completed_type(client):
    create_response = client.post(
        "/todos", 
        json = {

            "title": "Todo test",
            "description": "Testing validation"
        }
    )

    todo_id = create_response.json()["id"]
    
    response = client.patch(
        f"/todos/{todo_id}", 
        json = {
            "completed":"not-a-boolean"
        }
    )

    assert response.status_code == 422

# test create todo rollback
def test_create_todo_rollback(db_session, monkeypatch):
    def fake_commit():
        raise SQLAlchemyError("Simulated database error")

    monkeypatch.setattr(
        db_session,
        "commit",
        fake_commit
    )

    try:
        todo_repository.create(
            db=db_session,
            title = "Rollback Test",
            description="Testing Rollback"
        )
    except SQLAlchemyError:
        pass

    todos = todo_repository.get_all(
        db_session
    )

    assert todos == []

# test update todo rollback
def test_update_todo_rollback(db_session, monkeypatch):
    todo = todo_repository.create(
        db=db_session,
        title="Todo sebelum update",
        description="Original"
    )

    def fake_commit():
        raise SQLAlchemyError("Simulated database error")

    monkeypatch.setattr(
        db_session,
        "commit",
        fake_commit
    )

    try:
        todo_repository.update(
            db=db_session,
            todo=todo,
            update_data={
                "title": "Title baru"
            }
        )
    except SQLAlchemyError:
        pass

    db_session.rollback()

    todo_from_db = todo_repository.get_by_id(
        db=db_session,
        todo_id=todo.id
    )

    assert todo_from_db.title == "Todo sebelum update"

# test delete todo rollback
def test_delete_todo_rollback(db_session, monkeypatch):
    todo = todo_repository.create(
        db=db_session,
        title="Todo yang tidak boleh terhapus",
        description="Testing rollback"
    )

    def fake_commit():
        raise SQLAlchemyError("Simulated database error")

    monkeypatch.setattr(
        db_session,
        "commit",
        fake_commit
    )

    try:
        todo_repository.delete(
            db=db_session,
            todo=todo
        )
    except SQLAlchemyError:
        pass

    db_session.rollback()

    todo_from_db = todo_repository.get_by_id(
        db=db_session,
        todo_id=todo.id
    )

    assert todo_from_db is not None
    assert todo_from_db.title == "Todo yang tidak boleh terhapus"

