import pytest
from model_bakery import baker
from habits.models import Habit


@pytest.mark.django_db
def test_create_habit(auth_client):
    payload = {
        "place": "дом",
        "time": "08:00",
        "action": "зарядка",
        "is_pleasant": False,
        "periodicity_days": 1,
        "duration_seconds": 90,
        "is_public": False,
    }
    resp = auth_client.post("/api/habits/", payload, format="json")
    assert resp.status_code == 201
    assert resp.data["action"] == "зарядка"


@pytest.mark.django_db
def test_update_and_delete_only_own(auth_client, user, other_user):
    mine = baker.make(Habit, user=user, place="дом", time="09:00", action="чай")
    foreign = baker.make(
        Habit, user=other_user, place="офис", time="10:00", action="кофе"
    )

    # PATCH свой
    resp = auth_client.patch(
        f"/api/habits/{mine.id}/", {"action": "зелёный чай"}, format="json"
    )
    assert resp.status_code == 200
    assert resp.data["action"] == "зелёный чай"

    # PATCH чужой — 404 (из-за queryset только свои)
    resp = auth_client.patch(
        f"/api/habits/{foreign.id}/", {"action": "латте"}, format="json"
    )
    assert resp.status_code == 404

    # DELETE свой
    resp = auth_client.delete(f"/api/habits/{mine.id}/")
    assert resp.status_code == 204


@pytest.mark.django_db
def test_public_list_is_open(anon_client, user):
    # создаём публичные/непубличные
    baker.make(Habit, user=user, is_public=True, _quantity=3)
    baker.make(Habit, user=user, is_public=False, _quantity=2)

    resp = anon_client.get("/api/public-habits/")
    assert resp.status_code == 200
    # без пагинации — возвращается простой list
    assert isinstance(resp.data, list)
    assert len(resp.data) == 3


@pytest.mark.django_db
def test_list_only_own_and_pagination(auth_client, user, other_user):
    baker.make(Habit, user=user, _quantity=7)  # мои 7
    baker.make(Habit, user=other_user, _quantity=4)  # чужие
    # страница 1
    r1 = auth_client.get("/api/habits/?page=1")
    assert r1.status_code == 200
    assert r1.data["count"] == 7
    assert len(r1.data["results"]) == 5
    # страница 2
    r2 = auth_client.get("/api/habits/?page=2")
    assert r2.status_code == 200
    assert len(r2.data["results"]) == 2


@pytest.mark.django_db
def test_serializer_validation_on_create(auth_client, user):
    # linked и reward вместе — 400
    pleasant = Habit.objects.create(
        user=user, place="дом", time="20:00", action="ванна", is_pleasant=True
    )
    payload = {
        "place": "улица",
        "time": "21:00",
        "action": "прогулка",
        "linked_habit": pleasant.id,
        "reward": "десерт",
        "duration_seconds": 60,
        "periodicity_days": 1,
    }
    resp = auth_client.post("/api/habits/", payload, format="json")
    assert resp.status_code == 400
    assert "Нельзя одновременно указать" in str(resp.data)

    # duration > 120 — 400
    payload = {
        "place": "дом",
        "time": "07:00",
        "action": "медитация",
        "duration_seconds": 121,
        "periodicity_days": 1,
    }
    resp = auth_client.post("/api/habits/", payload, format="json")
    assert resp.status_code == 400

    # periodicity 8 — 400
    payload["duration_seconds"] = 60
    payload["periodicity_days"] = 8
    resp = auth_client.post("/api/habits/", payload, format="json")
    assert resp.status_code == 400
