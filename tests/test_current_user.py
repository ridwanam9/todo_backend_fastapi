
from uuid import uuid4


def test_current_user_with_valid_token(client):
    email = f"{uuid4().hex}@example.com"
    password = "secret123"

    client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )

    login_response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == email
    assert "password_hash" not in response.json()


def test_current_user_without_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_current_user_with_invalid_token(client):
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
