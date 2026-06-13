from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View
from apps.ai_coach.services.coach_service import CoachService


class CoachGuidanceView(LoginRequiredMixin, View):
    def get(self, request):
        recommendations = CoachService.get_latest_recommendations(request.user, limit=8)
        return render(request, "apps/ai_coach/guidance.html", {"recommendations": recommendations})

    def post(self, request):
        try:
            CoachService.generate_user_coach_guidance(request.user)
            messages.success(request, "AI Coach updated successfully with fresh recommendations!")
        except Exception as e:
            messages.error(request, f"Could not update guidance: {str(e)}")
        
        return redirect("coach_guidance")
