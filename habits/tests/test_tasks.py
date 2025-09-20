import pytest
from datetime import datetime, date, time, timedelta
from django.utils import timezone
from model_bakery import baker
from habits.models import Habit


@pytest.mark.django_db
def test_send_due_habit_reminders(monkeypatch, settings, user):
    # подменяем chat_id через настройку по умолчанию
    settings.DEFAULT_TELEGRAM_CHAT_ID = "123"
    # время "сейчас" принудительно
    now = timezone.now().astimezone(timezone.get_current_timezone())
    current_minute = now.time().replace(second=0, microsecond=0)

    # создаём привычку на текущее время
    habit = baker.make(
        Habit,
        user=user,
        time=current_minute,
        place="дом",
        action="вода",
        periodicity_days=1,
        last_notified_date=None,
    )

    sent = {"called": 0, "payloads": []}

    def fake_send_message(chat_id, text):
        sent["called"] += 1
        sent["payloads"].append((chat_id, text))

    monkeypatch.setattr("telegram_bot.tasks.send_message", fake_send_message)

    from telegram_bot.tasks import send_due_habit_reminders

    send_due_habit_reminders()

    habit.refresh_from_db()
    assert sent["called"] == 1
    assert habit.last_notified_date == date.today()

    # повторный запуск в ту же дату — не должно слать снова
    send_due_habit_reminders()
    assert sent["called"] == 1
