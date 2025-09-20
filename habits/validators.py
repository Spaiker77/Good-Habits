from django.core.exceptions import ValidationError


def validate_duration_seconds_le_120(duration_seconds: int):
    if duration_seconds is None:
        return
    if duration_seconds > 120:
        raise ValidationError("Время выполнения не должно превышать 120 секунд.")


def validate_periodicity_days(value: int):
    # не реже 1 раза в 7 дней
    if value is None:
        return
    if value > 7 or value < 1:
        raise ValidationError("Периодичность должна быть в диапазоне 1..7 дней.")


def validate_reward_and_linked(reward: str | None, linked_is_set: bool):
    if reward and linked_is_set:
        raise ValidationError(
            "Нельзя одновременно указать 'вознаграждение' и 'связанную привычку'."
        )


def validate_pleasant_constraints(
    is_pleasant: bool, reward: str | None, linked_is_set: bool
):
    if is_pleasant and (reward or linked_is_set):
        raise ValidationError(
            "У приятной привычки не может быть вознаграждения или связанной привычки."
        )
