from django.urls import path
from apps.moods.views import LogMoodView, MoodHistoryView, SyncHealthDataView

urlpatterns = [
    path("log/", LogMoodView.as_view(), name="log_mood"),
    path("history/", MoodHistoryView.as_view(), name="mood_history"),
    path("sync-health/", SyncHealthDataView.as_view(), name="sync_health"),
]
