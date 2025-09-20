from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = [
            "id",
            "place",
            "time",
            "action",
            "is_pleasant",
            "linked_habit",
            "periodicity_days",
            "reward",
            "duration_seconds",
            "is_public",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate(self, attrs):
        reward = attrs.get("reward", getattr(self.instance, "reward", None))
        linked = attrs.get("linked_habit", getattr(self.instance, "linked_habit", None))
        is_pleasant = attrs.get(
            "is_pleasant", getattr(self.instance, "is_pleasant", False)
        )

        if reward and linked:
            raise serializers.ValidationError(
                "Нельзя одновременно указать 'вознаграждение' и 'связанную привычку'."
            )

        if linked and not linked.is_pleasant:
            raise serializers.ValidationError(
                "Связанной может быть только приятная привычка."
            )

        if is_pleasant and (reward or linked):
            raise serializers.ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки."
            )

        periodicity = attrs.get(
            "periodicity_days", getattr(self.instance, "periodicity_days", 1)
        )
        if periodicity < 1 or periodicity > 7:
            raise serializers.ValidationError(
                "Периодичность должна быть от 1 до 7 дней."
            )

        duration = attrs.get(
            "duration_seconds", getattr(self.instance, "duration_seconds", 60)
        )
        if duration > 120:
            raise serializers.ValidationError(
                "Время выполнения не должно превышать 120 секунд."
            )

        return attrs

    def create(self, validated_data):
        return Habit.objects.create(user=self.context["request"].user, **validated_data)
