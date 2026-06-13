from django.urls import path
from apps.moods.views import LogMoodView, MoodHistoryView

urlpatterns = [
    path("log/", LogMoodView.as_view(), name="log_mood"),
    path("history/", MoodHistoryView.as_view(), name="mood_history"),
]
