from django.urls import path
from apps.ai_coach.views import CoachGuidanceView, CoachChatView

urlpatterns = [
    path("guidance/", CoachGuidanceView.as_view(), name="coach_guidance"),
    path("companion/", CoachChatView.as_view(), name="coach_chat"),
]

