from django.urls import path
from apps.moods.views import (
    LogMoodView,
    MoodHistoryView,
    SyncHealthDataView,
    HealthIntegrationSettingsView,
    OAuthCallbackView,
    DeleteHealthDataView,
)

urlpatterns = [
    path("log/", LogMoodView.as_view(), name="log_mood"),
    path("history/", MoodHistoryView.as_view(), name="mood_history"),
    path("sync-health/", SyncHealthDataView.as_view(), name="sync_health"),
    path("integrations/", HealthIntegrationSettingsView.as_view(), name="health_integrations"),
    path("oauth/callback/", OAuthCallbackView.as_view(), name="health_oauth_callback"),
    path("delete-data/", DeleteHealthDataView.as_view(), name="delete_health_data"),
]

