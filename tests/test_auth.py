import pytest
from flask import g, session

from urlShortener.db import get_db


def test_register(client, app):
    assert client.get("/auth/register").status_code == 200
    response = client.post(
        "/auth/register", data={"username": "user", "password": "123"}
    )
    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        assert (
            get_db()
            .execute(
                "SELECT * FROM user WHERE username = 'user'",
            )
            .fetchone()
        ) is not None


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (("test", "test", b"already registered"),),
)
def test_register_validate_input(client, username, password, message):
    response = client.post(
        "/auth/register", data={"username": username, "password": password}
    )
    assert message in response.data


def test_login(client, auth):
    assert client.get("/auth/login").status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        client.get("/")
        assert session["user_id"] == 1
        assert g.user["username"] == "test"


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("user", "test", b"Incorrect username"),
        ("test", "123", b"Incorrect password"),
    ),
)
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session
