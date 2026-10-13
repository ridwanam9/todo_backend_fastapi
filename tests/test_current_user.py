
import jwt
from uuid import uuid4
from datetime import datetime, timedelta, timezone

from app.security.token import SECRET_KEY, ALGORITHM

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




def test_current_user_with_expired_token(client):
    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": "1",
            "iat": now - timedelta(minutes=10),
            "exp": now - timedelta(minutes=5),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_current_user_with_wrong_signature(client):
    token = jwt.encode(
        {
            "sub": "1",
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=5),
        },
        "wrong-secret-key-that-is-not-the-real-secret",
        algorithm=ALGORITHM,
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_current_user_without_subject(client):
    token = jwt.encode(
        {
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=5),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_current_user_with_non_integer_subject(client):
    token = jwt.encode(
        {
            "sub": "not-an-integer",
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=5),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
