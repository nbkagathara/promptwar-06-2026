from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.dashboard.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("journals/", include("apps.journals.urls")),
    path("moods/", include("apps.moods.urls")),
    path("coach/", include("apps.ai_coach.urls")),
    path("analytics/", include("apps.analytics.urls")),
]
