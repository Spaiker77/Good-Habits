import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from habits.models import Habit


@pytest.mark.django_db
def test_pleasant_cannot_have_reward_or_linked():
    u = User.objects.create_user("u")
    pleasant = Habit(
        user=u,
        place="дом",
        time="20:00",
        action="чай",
        is_pleasant=True,
        reward="печенька",
    )
    with pytest.raises(ValidationError):
        pleasant.full_clean()


@pytest.mark.django_db
def test_linked_must_be_pleasant():
    u = User.objects.create_user("u")
    good = Habit.objects.create(user=u, place="дом", time="21:00", action="прогулка")
    main = Habit(user=u, place="дом", time="22:00", action="зарядка", linked_habit=good)
    with pytest.raises(ValidationError):
        main.full_clean()
