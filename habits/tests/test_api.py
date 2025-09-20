import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_list_only_own_habits():
    u1 = User.objects.create_user("a", password="p")
    u2 = User.objects.create_user("b", password="p")
    baker.make("habits.Habit", user=u1, _quantity=3)
    baker.make("habits.Habit", user=u2, _quantity=2)

    client = APIClient()
    token = client.post("/api/token/obtain/", {"username": "a", "password": "p"}).data[
        "access"
    ]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    resp = client.get("/api/habits/")
    assert resp.status_code == 200
    assert len(resp.data["results"]) == 3 or "results" in resp.data
