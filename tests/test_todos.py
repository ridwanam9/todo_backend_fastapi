from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.main import app
from app.repositories import todo as todo_repository
from uuid import uuid4

from app.repositories import user as user_repository
from app.security.password import hash_password

# client = TestClient(app)

# cek health
def test_health_check(client):

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status" : "ok"
    }

# create todos
def test_create_todo(client, auth_headers):
    response = client.post(
        "/todos", 
        json = {

            "title": "Test todo",
            "description": "Testing FastAPI"
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()

    assert data["title"] == "Test todo"
    assert data["description"] == "Testing FastAPI"
    assert data["completed"] is False
    assert "id" in data

# get todos
def test_get_todos(client, auth_headers):
    response = client.get("/todos", headers=auth_headers,)

    assert response.status_code == 200

    assert isinstance(response.json(), list)


# get todo by id
def test_get_todo(client, auth_headers):
    create_response = client.post(
        "/todos", 
        json = {

            "title": "Todo untuk GET",
            "description": "Testing GET by ID"
        },
        headers=auth_headers,
    )

    todo_id = create_response.json()["id"]

    response = client.get(f"/todos/{todo_id}", headers=auth_headers,)
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == todo_id
    assert data["title"] == "Todo untuk GET"


# test get todo not found
def test_get_todo_not_found(client, auth_headers):
    response = client.get("/todos/999999", headers=auth_headers,)

    assert response.status_code == 404
    assert response.json() == {
        "detail" : "Todo not found"
    }


# test patch todo
def test_update_todo(client, auth_headers):
    create_response = client.post(
        "/todos", 
        json = {

            "title": "Test lama",
            "description": "Description lama"
        },
        headers=auth_headers,
    )

    todo_id = create_response.json()["id"]
    
    response = client.patch(
        f"/todos/{todo_id}", 
        json = {

            "completed": True,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == todo_id
    assert data["title"] == "Test lama"
    assert data["description"] == "Description lama"
    assert data["completed"] is True


# test delete todo
def test_delete_todo(client, auth_headers):
    create_response = client.post(
        "/todos", 
        json = {
            "title": "Todo untuk delete",
            "description": "Akan dihapus"
        },
        headers=auth_headers,
    )

    todo_id = create_response.json()["id"]
    
    response = client.delete(
        f"/todos/{todo_id}"
    , headers=auth_headers,)
    assert response.status_code == 204

    get_response = client.get(
        f"/todos/{todo_id}"
    , headers=auth_headers,)
    assert get_response.status_code == 404
    

# test update todo not found
def test_update_todo_not_found(client, auth_headers):
    response = client.patch(
        "/todos/999999",
        json={
            "completed": True
        },
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail" : "Todo not found"
    }

# test delete todo not found
def test_delete_todo_not_found(client, auth_headers):
    response = client.delete(
        "/todos/999999"
    , headers=auth_headers,)

    assert response.status_code == 404
    assert response.json() == {
        "detail" : "Todo not found"
    }

# create todo without title
def test_create_todo_missing_title(client, auth_headers):
    response = client.post(
        "/todos",
        json={
            "description":"Todo tanpa title"
        },
        headers=auth_headers,
    )

    assert response.status_code == 422

# create todo without description
def test_create_todo_missing_description(client, auth_headers):
    response = client.post(
        "/todos",
        json={
            "title":"Todo tanpa description"
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


# test patch todo empty body
def test_update_todo_empty_body(client, auth_headers):
    create_response = client.post(
        "/todos", 
        json = {

            "title": "Todo test",
            "description": "Testing empty patch"
        },
        headers=auth_headers,
    )

    todo_id = create_response.json()["id"]
    
    response = client.patch(
        f"/todos/{todo_id}", 
        json = {}, headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["title"] == "Todo test"
    assert data["description"] == "Testing empty patch"
    assert data["completed"] is False


# test patch todo wrong data type
def test_update_todo_invalid_completed_type(client, auth_headers):
    create_response = client.post(
        "/todos", 
        json = {

            "title": "Todo test",
            "description": "Testing validation"
        },
        headers=auth_headers,
    )

    todo_id = create_response.json()["id"]
    
    response = client.patch(
        f"/todos/{todo_id}", 
        json = {
            "completed":"not-a-boolean"
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


def _create_test_user(db_session):
    return user_repository.create(
        db=db_session,
        email=f"{uuid4().hex}@example.com",
        password_hash=hash_password("secret123"),
    )





# test create todo rollback
def test_create_todo_rollback(db_session, monkeypatch):
    user = _create_test_user(db_session)

    def fake_commit():
        raise SQLAlchemyError("Simulated database error")

    monkeypatch.setattr(db_session, "commit", fake_commit)

    try:
        todo_repository.create(
            db=db_session,
            title="Rollback Test",
            description="Testing Rollback",
            user_id=user.id,
        )
    except SQLAlchemyError:
        pass

    todos = todo_repository.get_all(
        db=db_session,
        user_id=user.id,
    )

    assert todos == []

# test update todo rollback
def test_update_todo_rollback(db_session, monkeypatch):
    user = _create_test_user(db_session)

    todo = todo_repository.create(
        db=db_session,
        title="Todo sebelum update",
        description="Original",
        user_id=user.id,
    )
    todo_id = todo.id

    def fake_commit():
        raise SQLAlchemyError("Simulated database error")

    monkeypatch.setattr(db_session, "commit", fake_commit)

    try:
        todo_repository.update(
            db=db_session,
            todo=todo,
            update_data={"title": "Title baru"},
        )
    except SQLAlchemyError:
        pass

    db_session.rollback()

    todo_from_db = todo_repository.get_by_id(
        db=db_session,
        todo_id=todo_id,
        user_id=user.id,
    )

    assert todo_from_db is not None
    assert todo_from_db.title == "Todo sebelum update"

# test delete todo rollback
def test_delete_todo_rollback(db_session, monkeypatch):
    user = _create_test_user(db_session)

    todo = todo_repository.create(
        db=db_session,
        title="Todo yang tidak boleh terhapus",
        description="Testing rollback",
        user_id=user.id,
    )
    todo_id = todo.id

    def fake_commit():
        raise SQLAlchemyError("Simulated database error")

    monkeypatch.setattr(db_session, "commit", fake_commit)

    try:
        todo_repository.delete(
            db=db_session,
            todo=todo,
        )
    except SQLAlchemyError:
        pass

    db_session.rollback()

    todo_from_db = todo_repository.get_by_id(
        db=db_session,
        todo_id=todo_id,
        user_id=user.id,
    )

    assert todo_from_db is not None
    assert todo_from_db.title == "Todo yang tidak boleh terhapus"



def test_user_cannot_see_other_users_todos(client, auth_headers):
    # User A membuat Todo
    response_a = client.post(
        "/todos",
        json={
            "title": "Todo User A",
            "description": "Data milik User A",
        },
        headers=auth_headers,
    )
    assert response_a.status_code == 201

    # Buat User B
    from uuid import uuid4

    email_b = f"{uuid4().hex}@example.com"
    password_b = "secret123"

    register_response = client.post(
        "/auth/register",
        json={"email": email_b, "password": password_b},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={"email": email_b, "password": password_b},
    )
    assert login_response.status_code == 200

    token_b = login_response.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B membuat Todo miliknya
    response_b = client.post(
        "/todos",
        json={
            "title": "Todo User B",
            "description": "Data milik User B",
        },
        headers=headers_b,
    )
    assert response_b.status_code == 201

    # User A hanya boleh melihat Todo miliknya
    todos_response_a = client.get(
        "/todos",
        headers=auth_headers,
    )
    assert todos_response_a.status_code == 200

    todos_a = todos_response_a.json()
    titles_a = [todo["title"] for todo in todos_a]

    assert "Todo User A" in titles_a
    assert "Todo User B" not in titles_a



def test_user_cannot_access_other_users_todo(client, auth_headers):
    from uuid import uuid4

    # Buat User B
    email_b = f"{uuid4().hex}@example.com"
    password_b = "secret123"

    client.post(
        "/auth/register",
        json={"email": email_b, "password": password_b},
    )
    login_response = client.post(
        "/auth/login",
        json={"email": email_b, "password": password_b},
    )
    token_b = login_response.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B membuat Todo
    create_response = client.post(
        "/todos",
        json={
            "title": "Todo Rahasia B",
            "description": "Tidak boleh diakses User A",
        },
        headers=headers_b,
    )
    assert create_response.status_code == 201
    todo_id = create_response.json()["id"]

    # User A mencoba membaca Todo milik B
    response = client.get(
        f"/todos/{todo_id}",
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_user_cannot_update_other_users_todo(client, auth_headers):
    from uuid import uuid4

    email_b = f"{uuid4().hex}@example.com"
    password_b = "secret123"

    client.post(
        "/auth/register",
        json={"email": email_b, "password": password_b},
    )
    login_response = client.post(
        "/auth/login",
        json={"email": email_b, "password": password_b},
    )
    headers_b = {
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    }

    create_response = client.post(
        "/todos",
        json={
            "title": "Todo Asli B",
            "description": "Deskripsi asli",
        },
        headers=headers_b,
    )
    assert create_response.status_code == 201
    todo_id = create_response.json()["id"]

    # User A mencoba mengubah Todo milik B
    response = client.patch(
        f"/todos/{todo_id}",
        json={
            "title": "Diubah oleh A",
            "description": "Perubahan tidak sah",
        },
        headers=auth_headers,
    )
    assert response.status_code == 404

    # Pastikan data B tetap tidak berubah
    verify_response = client.get(
        f"/todos/{todo_id}",
        headers=headers_b,
    )
    assert verify_response.status_code == 200
    assert verify_response.json()["title"] == "Todo Asli B"


def test_user_cannot_delete_other_users_todo(client, auth_headers):
    from uuid import uuid4

    email_b = f"{uuid4().hex}@example.com"
    password_b = "secret123"

    client.post(
        "/auth/register",
        json={"email": email_b, "password": password_b},
    )
    login_response = client.post(
        "/auth/login",
        json={"email": email_b, "password": password_b},
    )
    headers_b = {
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    }

    create_response = client.post(
        "/todos",
        json={
            "title": "Todo Milik B",
            "description": "Harus tetap ada",
        },
        headers=headers_b,
    )
    assert create_response.status_code == 201
    todo_id = create_response.json()["id"]

    # User A mencoba menghapus Todo milik B
    response = client.delete(
        f"/todos/{todo_id}",
        headers=auth_headers,
    )
    assert response.status_code == 404

    # Pastikan Todo B masih ada
    verify_response = client.get(
        f"/todos/{todo_id}",
        headers=headers_b,
    )
    assert verify_response.status_code == 200
    assert verify_response.json()["title"] == "Todo Milik B"


def test_get_todos_without_toker(client):
    response = client.get("/todos")
    assert response.status_code == 401


def test_create_todo_without_token(client):
    response = client.post(
        "/todos",
        json={
            "title": "Todo tanpa autentikasi",
            "description": "Seharusnya ditolak",
        },
    )
    assert response.status_code == 401


def test_get_todo_without_token(client):
    response = client.get("/todos/1")
    assert response.status_code == 401


def test_update_todo_without_token(client):
    response = client.patch(
        "/todos/1",
        json={"title": "Perubahan tanpa token"},
    )
    assert response.status_code == 401


def test_delete_todo_without_token(client):
    response = client.delete("/todos/1")
    assert response.status_code == 401