
from uuid import uuid4


def test_login_success(client):
    email = f"{uuid4().hex}@example.com"
    password = "secret123"

    register_response = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201

    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    email = f"{uuid4().hex}@example.com"

    client.post(
        "/auth/register",
        json={"email": email, "password": "secret123"},
    )

    response = client.post(
        "/auth/login",
        json={"email": email, "password": "wrongpassword"},
    )

    assert response.status_code == 401


def test_login_unknown_email(client):
    response = client.post(
        "/auth/login",
        json={
            "email": f"{uuid4().hex}@example.com",
            "password": "secret123",
        },
    )

    assert response.status_code == 401
