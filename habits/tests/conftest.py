import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.fixture
def user(db):
    return User.objects.create_user(username="alice", password="pass", email="a@a.a")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="bob", password="pass", email="b@b.b")


@pytest.fixture
def auth_client(user):
    client = APIClient()
    # Получаем JWT access
    resp = client.post(
        "/api/token/obtain/", {"username": "alice", "password": "pass"}, format="json"
    )
    assert resp.status_code == 200, resp.data
    token = resp.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def anon_client():
    return APIClient()
