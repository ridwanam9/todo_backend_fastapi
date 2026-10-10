from app.security.password import(
    hash_password,
    verify_password,
)


def test_hash_password():
    password = "secret123"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)

def test_verify_wrong_password():
    password = "secret123"

    hashed = hash_password(password)

    assert not verify_password(
        "wrongpassword",
        hashed
    )
