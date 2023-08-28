def test_redirect_url(client):
    response = client.get("/url/testing")
    assert response.status_code == 302
    assert b"https://example.com" in response.data


def test_not_exists(client):
    response = client.get("/url/testnotfound")
    assert response.status_code == 404
