import pytest


@pytest.mark.django_db
def test_register_and_login(client):
    payload = {
        "username": "new",
        "password": "StrongPass123!",
        "email": "new@example.com",  # <-- валидный email
    }
    resp = client.post("/api/register/", payload, format="json")
    assert resp.status_code == 201, resp.content

    resp = client.post(
        "/api/token/obtain/",
        {"username": "new", "password": "StrongPass123!"},
        format="json",
    )
    assert resp.status_code == 200
    assert "access" in resp.data and "refresh" in resp.data
