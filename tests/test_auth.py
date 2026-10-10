
from uuid import uuid4

from app.repositories import user as user_repository
from app.security.password import verify_password


def test_register_user(client, db_session):
    email = f"{uuid4().hex}@example.com"
    password = "secret123"

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == email
    assert "password" not in response.json()
    assert "password_hash" not in response.json()

    saved_user = user_repository.get_by_email(
        db=db_session,
        email=email,
    )

    assert saved_user is not None
    assert saved_user.password_hash != password
    assert verify_password(password, saved_user.password_hash)


def test_register_duplicate_email(client):
    email = f"{uuid4().hex}@example.com"
    payload = {
        "email": email,
        "password": "secret123",
    }

    first_response = client.post(
        "/auth/register",
        json=payload,
    )
    second_response = client.post(
        "/auth/register",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_register_invalid_email(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "not-an-email",
            "password": "secret123",
        },
    )

    assert response.status_code == 422
