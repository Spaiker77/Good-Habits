from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from .validators import (
    validate_duration_seconds_le_120,
    validate_periodicity_days,
    validate_reward_and_linked,
    validate_pleasant_constraints,
)


class Habit(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="habits"
    )
    place = models.CharField(max_length=255)
    time = models.TimeField(help_text="Время, когда необходимо выполнять привычку")
    action = models.CharField(max_length=255)

    is_pleasant = models.BooleanField(
        default=False, help_text="Признак приятной привычки"
    )
    linked_habit = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"is_pleasant": True},
        related_name="linked_to",
    )
    periodicity_days = models.PositiveSmallIntegerField(
        default=1, validators=[validate_periodicity_days]
    )
    reward = models.CharField(max_length=255, null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(
        default=60, validators=[validate_duration_seconds_le_120]
    )
    is_public = models.BooleanField(default=False)

    # служебные для напоминаний
    last_notified_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ()

    def clean(self):
        # 1) нельзя вознаграждение и связанная одновременно
        validate_reward_and_linked(self.reward, bool(self.linked_habit))

        # 2) связанная может быть только приятной
        if self.linked_habit and not self.linked_habit.is_pleasant:
            raise ValidationError(
                "В связанные привычки могут попадать только приятные привычки."
            )

        # 3) у приятной не может быть вознаграждения
        validate_pleasant_constraints(
            self.is_pleasant, self.reward, bool(self.linked_habit)
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.action} @ {self.time} ({'приятная' if self.is_pleasant else 'полезная'})"
