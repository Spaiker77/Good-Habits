from rest_framework import viewsets, mixins, permissions, filters
from rest_framework.response import Response
from .models import Habit
from .serializers import HabitSerializer
from .permissions import IsOwner


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)


class PublicHabitViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = HabitSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Habit.objects.filter(is_public=True)
    pagination_class = None
