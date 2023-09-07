import pytest

from urlShortener.db import get_db
from urlShortener.api import check_safe_string


@pytest.mark.parametrize("test_string", ("aBcDeF", "QWERTY", "adgjl"))
def test_check_safe_string(test_string):
    assert check_safe_string(test_string)


@pytest.mark.parametrize("test_string", ("aC54hs7", "abcd.", "#@46fetD"))
def test_check_unsafe_string(test_string):
    assert not check_safe_string(test_string)


@pytest.mark.parametrize("method", ("GET", "POST"))
def test_urls_require_auth(client, method):
    response = client.open(path="/api/v0.1.0/urls", method=method)
    assert response.status_code == 401


@pytest.mark.parametrize("method", ("GET", "PATCH", "DELETE"))
def test_url_by_id_require_auth(client, method):
    response = client.open(path="/api/v0.1.0/urls/1", method=method)
    assert response.status_code == 401


def test_get_urls(client):
    response = client.get(
        "/api/v0.1.0/urls",
        headers=[
            (
                "Authorization",
                "647b370dc5a980fb07a87aa6370d371de2c0b40226236fd708c9b03c2b5f14fd",
            )
        ],
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert len(response.json["urls"]) == 3
    for url in response.json["urls"]:
        assert url["shortener_string"] in (
            "testing",
            "exampleOne",
            "exampleTwo",
        )


def test_only_get_owned_urls(client):
    response = client.get(
        "/api/v0.1.0/urls",
        headers=[
            (
                "Authorization",
                "53117e6dee7463659a73c29ba125b8be86481ec586269f7cca3045375c6bfc5b",
            )
        ],
    )
    assert response.status_code == 404
    assert b"No URLs found" in response.data


def test_get_not_exists(client):
    response = client.get(
        "/api/v0.1.0/urls/24",
        headers=[
            (
                "Authorization",
                "647b370dc5a980fb07a87aa6370d371de2c0b40226236fd708c9b03c2b5f14fd",
            )
        ],
    )
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "application/json"
    assert b"this ID was not found" in response.data


def test_get_url_by_id(client):
    response = client.get(
        "/api/v0.1.0/urls/1",
        headers=[
            (
                "Authorization",
                "647b370dc5a980fb07a87aa6370d371de2c0b40226236fd708c9b03c2b5f14fd",
            )
        ],
    )
    assert response.status_code == 200
    assert b"testing" in response.data


def test_only_get_owned_url_by_id(client):
    response = client.get(
        "/api/v0.1.0/urls/1",
        headers=[
            (
                "Authorization",
                "53117e6dee7463659a73c29ba125b8be86481ec586269f7cca3045375c6bfc5b",
            )
        ],
    )
    assert response.status_code == 404
    assert b"this ID was not found" in response.data


def test_create_new_url(client, app):
    response = client.post(
        "/api/v0.1.0/urls",
        headers=[
            (
                "Authorization",
                "647b370dc5a980fb07a87aa6370d371de2c0b40226236fd708c9b03c2b5f14fd",
            )
        ],
        json={
            "url_name": "Created Example",
            "original_url": "https://example.com",
            "shortener_string": "testcreate",
        },
    )
    assert response.status_code == 201
    assert b"Created Example" in response.data
    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM urls").fetchone()[0]
        assert count == 4


def test_generate_random_suffix(client, app):
    response = client.post(
        "/api/v0.1.0/urls",
        headers=[
            (
                "Authorization",
                "647b370dc5a980fb07a87aa6370d371de2c0b40226236fd708c9b03c2b5f14fd",
            )
        ],
        json={
            "url_name": "Test Suffix",
            "original_url": "https://example.com",
            "shortener_string": "",
        },
    )
    assert response.status_code == 201
    assert b"Test Suffix" in response.data
    assert bool(response.json["shortener_string"])
    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM urls").fetchone()[0]
        assert count == 4


def test_shortener_string_required(client):
    response = client.post(
        "/api/v0.1.0/urls",
        headers=[
            (
                "Authorization",
                "647b370dc5a980fb07a87aa6370d371de2c0b40226236fd708c9b03c2b5f14fd",
            )
        ],
        json={
            "url_name": "Test Shortener String Required",
            "original_url": "https://example.com",
        },
    )
    assert response.status_code == 400


def test_safe_suffix_string_required(client):
    response = client.post(
        "/api/v0.1.0/urls",
        headers=[
            (
                "Authorization",
                "647b370dc5a980fb07a87aa6370d371de2c0b40226236fd708c9b03c2b5f14fd",
            )
        ],
        json={
            "url_name": "Test Shortener String Required",
            "original_url": "https://example.com",
            "shortener_string": "abc123!@£",
        },
    )
    assert response.status_code == 400


def test_create_bad_request(client):
    response = client.post(
        "/api/v0.1.0/urls",
        headers=[
            (
                "Authorization",
                "647b370dc5a980fb07a87aa6370d371de2c0b40226236fd708c9b03c2b5f14fd",
            )
        ],
        # Spelling mistake in url_name
        json={
            "urlname": "Created Example",
            "original_url": "https://example.com",
            "shortener_string": "testcreate",
        },
    )
    assert response.status_code == 400
    assert b"checking the spelling" in response.data


def test_create_duplicate_name_conflict(client, app):
    response = client.post(
        "/api/v0.1.0/urls",
        headers=[
            (
                "Authorization",
                "647b370dc5a980fb07a87aa6370d371de2c0b40226236fd708c9b03c2b5f14fd",
            )
        ],
        json={
            "url_name": "Conflict Example",
            "original_url": "https://example.com",
            "shortener_string": "testing",
        },
    )
    assert response.status_code == 409
    assert b"already exists" in response.data
    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM urls").fetchone()[0]
        assert count == 3


def test_update_url(client):
    response = client.patch(
        "/api/v0.1.0/urls/1",
        headers=[
            (
                "Authorization",
                "647b370dc5a980fb07a87aa6370d371de2c0b40226236fd708c9b03c2b5f14fd",
            )
        ],
        json={
            "url_name": "Update Example",
            "original_url": "https://example.com",
        },
    )
    assert response.status_code == 200


def test_update_not_exists(client):
    response = client.patch(
        "/api/v0.1.0/urls/24",
        headers=[
            (
                "Authorization",
                "647b370dc5a980fb07a87aa6370d371de2c0b40226236fd708c9b03c2b5f14fd",
            )
        ],
        json={
            "url_name": "Update Example",
            "original_url": "https://example.com",
        },
    )
    assert response.status_code == 404
    assert b"Not Found" in response.data


def test_update_bad_request(client):
    response = client.patch(
        "/api/v0.1.0/urls/1",
        headers=[
            (
                "Authorization",
                "647b370dc5a980fb07a87aa6370d371de2c0b40226236fd708c9b03c2b5f14fd",
            )
        ],
        # Spelling mistake in url_name
        json={
            "urlname": "Created Example",
            "original_url": "https://example.com",
        },
    )
    assert response.status_code == 400
    assert b"checking the spelling" in response.data


def test_update_bad_content_type(client):
    response = client.patch(
        "/api/v0.1.0/urls/1",
        headers=[
            (
                "Authorization",
                "647b370dc5a980fb07a87aa6370d371de2c0b40226236fd708c9b03c2b5f14fd",
            )
        ],
        content_type="text/plain",
        data={
            "url_name": "Created Example",
            "original_url": "https://example.com",
            "shortener_string": "testing",
        },
    )
    assert response.status_code == 415
    assert b"attempt to load JSON" in response.data


def test_delete_url(client, app):
    response = client.delete(
        "/api/v0.1.0/urls/1",
        headers=[
            (
                "Authorization",
                "647b370dc5a980fb07a87aa6370d371de2c0b40226236fd708c9b03c2b5f14fd",
            )
        ],
    )
    assert response.status_code == 204
    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM urls").fetchone()[0]
        assert count == 2


def test_delete_only_owned_url(client, app):
    response = client.delete(
        "/api/v0.1.0/urls/1",
        headers=[
            (
                "Authorization",
                "53117e6dee7463659a73c29ba125b8be86481ec586269f7cca3045375c6bfc5b",
            )
        ],
    )
    assert response.status_code == 204
    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM urls").fetchone()[0]
        assert count == 1
