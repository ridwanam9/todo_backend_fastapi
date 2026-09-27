from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

# cek health
def test_health_check():

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status" : "ok"
    }

# create todos
def test_create_todo():
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
def test_get_todos():
    response = client.get("/todos")

    assert response.status_code == 200

    assert isinstance(response.json(), list)


# get todo by id
def test_get_todo():
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
def test_get_todo_not_found():
    response = client.get("/todos/999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail" : "Todo not found"
    }


# test patch todo
def test_update_todo():
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
def test_delete_todo():
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
def test_update_todo_not_found():
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
def test_delete_todo_not_found():
    response = client.delete(
        "/todos/999999"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail" : "Todo not found"
    }


    