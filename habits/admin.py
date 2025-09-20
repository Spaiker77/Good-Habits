from django.contrib import admin
from .models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "action",
        "time",
        "is_pleasant",
        "is_public",
        "periodicity_days",
    )
    list_filter = ("is_pleasant", "is_public", "periodicity_days")
    search_fields = ("action", "place", "user__username")
