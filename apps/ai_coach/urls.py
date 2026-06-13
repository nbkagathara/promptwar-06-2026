from django.urls import path
from apps.ai_coach.views import CoachGuidanceView

urlpatterns = [
    path("guidance/", CoachGuidanceView.as_view(), name="coach_guidance"),
]
