import pytest
from django.core.exceptions import ValidationError
from habits.models import Habit


@pytest.mark.django_db
def test_duration_must_be_le_120(user):
    h = Habit(
        user=user, place="дом", time="10:00", action="медитация", duration_seconds=121
    )
    with pytest.raises(ValidationError):
        h.full_clean()


@pytest.mark.django_db
def test_periodicity_between_1_and_7(user):
    h = Habit(user=user, place="дом", time="10:00", action="чай", periodicity_days=0)
    with pytest.raises(ValidationError):
        h.full_clean()
    h.periodicity_days = 8
    with pytest.raises(ValidationError):
        h.full_clean()


@pytest.mark.django_db
def test_reward_and_linked_mutually_exclusive(user):
    pleasant = Habit.objects.create(
        user=user, place="дом", time="20:00", action="ванна", is_pleasant=True
    )
    main = Habit(
        user=user,
        place="улица",
        time="21:00",
        action="прогулка",
        reward="десерт",
        linked_habit=pleasant,
    )
    with pytest.raises(ValidationError):
        main.full_clean()


@pytest.mark.django_db
def test_linked_must_be_pleasant(user):
    not_pleasant = Habit.objects.create(
        user=user, place="дом", time="19:00", action="зарядка", is_pleasant=False
    )
    main = Habit(
        user=user,
        place="дом",
        time="20:00",
        action="медитация",
        linked_habit=not_pleasant,
    )
    with pytest.raises(ValidationError):
        main.full_clean()


@pytest.mark.django_db
def test_pleasant_cannot_have_reward_or_linked(user):
    pleasant = Habit(
        user=user,
        place="дом",
        time="20:00",
        action="чай",
        is_pleasant=True,
        reward="печенька",
    )
    with pytest.raises(ValidationError):
        pleasant.full_clean()
