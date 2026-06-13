from django.urls import path
from apps.analytics.views import AnalyticsDashboardView

urlpatterns = [
    path("", AnalyticsDashboardView.as_view(), name="analytics_dashboard"),
]
