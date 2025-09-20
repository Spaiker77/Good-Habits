from celery import shared_task
from django.utils import timezone
from datetime import date, datetime, timedelta
from django.conf import settings
from habits.models import Habit
from .bot import send_message


@shared_task
def send_due_habit_reminders():
    now = timezone.localtime()
    current_time = now.time().replace(second=0, microsecond=0)

    queryset = Habit.objects.filter(time=current_time)

    for habit in queryset.select_related("linked_habit", "user"):
        # вычисляем «сегодня ли день напоминания»
        already = habit.last_notified_date == now.date()
        if already:
            continue

        if habit.last_notified_date:
            delta = (now.date() - habit.last_notified_date).days
            if delta < habit.periodicity_days:
                continue

        reward_text = f" Награда: {habit.reward}." if habit.reward else ""
        pleasant = (
            f" Приятная: {habit.linked_habit.action}." if habit.linked_habit else ""
        )
        msg = f"Пора выполнить привычку: {habit.action} в {habit.place}.{reward_text}{pleasant}"

        chat_id = settings.DEFAULT_TELEGRAM_CHAT_ID or getattr(
            habit.user, "telegram_chat_id", None
        )
        if chat_id:
            send_message(chat_id, msg)

        habit.last_notified_date = now.date()
        habit.save(update_fields=["last_notified_date"])
