from django.urls import path
from apps.dashboard.views import LandingView, MainDashboardView, CrisisSupportView

urlpatterns = [
    path("", LandingView.as_view(), name="landing"),
    path("dashboard/", MainDashboardView.as_view(), name="dashboard"),
    path("crisis-support/", CrisisSupportView.as_view(), name="crisis_support"),
]
