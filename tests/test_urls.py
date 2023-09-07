import pytest
from urlShortener.db import get_db


def test_index(client, auth):
    response = client.get("/")
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get("/")
    assert b"Log Out" in response.data
    assert b"test url" in response.data
    assert b"testing" in response.data


@pytest.mark.parametrize("path", ("/create", "/1/delete"))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"


def test_creator_required(app, client, auth):
    with app.app_context():
        db = get_db()
        db.execute("UPDATE urls SET creator_id = 2 WHERE id = 1")
        db.commit()

    auth.login()
    assert client.post("/1/delete").status_code == 403


@pytest.mark.parametrize("path", ("/4/update", "/4/delete"))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get("/create").status_code == 200
    client.post(
        "/create",
        data={
            "url_name": "test",
            "extension": "test",
            "url": "https://example.com",
        },
    )
    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM urls").fetchone()[0]
        assert count == 4


def test_create_long_url_required(client, auth, app):
    auth.login()
    assert client.get("/create").status_code == 200
    response = client.post(
        "/create",
        data={
            "url_name": "test",
            "extension": "",
            "url": "",
        },
    )
    assert b"URL is required" in response.data
    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM urls").fetchone()[0]
        assert count == 3


def test_handle_empty_suffix(client, auth, app):
    auth.login()
    response = client.post(
        "/create",
        data={
            "url_name": "test",
            "extension": "",
            "url": "https://example.com",
        },
    )
    assert response.status_code == 302
    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM urls").fetchone()[0]
        assert count == 4


def test_update(client, auth, app):
    pass


def test_delete(client, auth, app):
    auth.login()
    response = client.post("/1/delete")
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        url = db.execute("SELECT * FROM urls WHERE id = 1").fetchone()
        assert url is None


def test_require_unique_suffix(client, auth, app):
    auth.login()
    response = client.post(
        "/create",
        data={
            "url_name": "test",
            "extension": "testing",
            "url": "https://example.com",
        },
    )
    assert response.status_code == 200
    assert b"not available" in response.data
    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM urls").fetchone()[0]
        assert count == 3
