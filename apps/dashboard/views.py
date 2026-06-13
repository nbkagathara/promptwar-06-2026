from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from apps.moods.models import MoodLog
from apps.journals.models import JournalEntry
from apps.ai_coach.services.coach_service import CoachService
from apps.analytics.services.analytics_service import AnalyticsService
from apps.safety.services.safety_service import SafetyService


class LandingView(TemplateView):
    template_name = "landing.html"


class MainDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user

        # 1. Check if user has an unresolved critical safety alert
        active_crisis = SafetyService.get_active_crisis_alert(user)

        # 2. Get latest mood log for today
        today_mood = MoodLog.objects.filter(user=user).order_by("-logged_date").first()

        # 3. Get recent journals
        recent_journals = JournalEntry.objects.filter(user=user).select_related("analysis")[:3]

        # 4. Get recent coach recommendations
        recommendations = CoachService.get_latest_recommendations(user, limit=4)

        # 5. Fetch overall averages and risk scores
        analytics_summary = AnalyticsService.get_summary_metrics(user)

        # 6. Check if profile exists; if not, suggest completing it
        profile = getattr(user, "profile", None)

        # 7. Fetch latest connected wearable health metrics
        from apps.moods.models import HealthDataLog
        from apps.moods.services.health_service import HealthService
        from apps.moods.models import HealthIntegration

        today_health = HealthDataLog.objects.filter(user=user).order_by("-logged_date").first()
        wellness_score = HealthService.calculate_wellness_score(today_health) if today_health else 0
        has_integrations = HealthIntegration.objects.filter(user=user, is_connected=True).exists()

        context = {
            "active_crisis": active_crisis,
            "today_mood": today_mood,
            "recent_journals": recent_journals,
            "recommendations": recommendations,
            "analytics": analytics_summary,
            "profile": profile,
            "today_health": today_health,
            "wellness_score": wellness_score,
            "has_integrations": has_integrations,
        }

        return render(request, "apps/dashboard/dashboard.html", context)


class CrisisSupportView(View):
    """
    Dedicated safe view displaying emergency mental health hotlines and resources.
    """

    def get(self, request):
        return render(request, "apps/dashboard/crisis_support.html")
