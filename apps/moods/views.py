from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import FormView
from apps.moods.forms import MoodLogForm
from apps.moods.models import MoodLog
from apps.moods.services.mood_service import MoodService


class LogMoodView(LoginRequiredMixin, FormView):
    template_name = "apps/moods/log_mood.html"
    form_class = MoodLogForm
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        cleaned = form.cleaned_data
        MoodService.log_daily_mood(
            user=self.request.user,
            mood_score=int(cleaned["mood_score"]),
            stress_score=int(cleaned["stress_score"]),
            energy_level=int(cleaned["energy_level"]),
            sleep_quality=int(cleaned["sleep_quality"]),
            study_satisfaction=int(cleaned["study_satisfaction"]),
        )
        return super().form_valid(form)


class MoodHistoryView(LoginRequiredMixin, ListView):
    model = MoodLog
    template_name = "apps/moods/history.html"
    context_object_name = "mood_logs"
    paginate_by = 10

    def get_queryset(self):
        return MoodLog.objects.filter(user=self.request.user).order_by("-logged_date")


class SyncHealthDataView(LoginRequiredMixin, View):
    def post(self, request):
        from apps.moods.services.health_service import HealthService
        from django.contrib import messages

        platform = request.POST.get("source", "Apple Health")
        profile_type = request.POST.get("profile_type", "active_healthy")

        log = HealthService.sync_device_data(
            user=request.user,
            platform=platform,
            profile_type=profile_type
        )

        score = HealthService.calculate_wellness_score(log)

        messages.success(
            request,
            f"Successfully synced metrics from {platform}! Today's Wellness Score: {score}/100."
        )
        return redirect("dashboard")


class HealthIntegrationSettingsView(LoginRequiredMixin, View):
    def get(self, request):
        from django.shortcuts import render
        from apps.moods.services.health_service import HealthService

        platforms = ["google_fit", "apple_health", "fitbit", "smart_band"]
        integrations = {
            p: HealthService.get_or_create_integration(request.user, p) for p in platforms
        }

        context = {
            "integrations": integrations,
        }
        return render(request, "apps/moods/integrations.html", context)

    def post(self, request):
        from django.contrib import messages
        from apps.moods.services.health_service import HealthService

        platform = request.POST.get("platform")
        if platform:
            consent_data = {
                "allow_steps": request.POST.get("allow_steps") == "on",
                "allow_heart_rate": request.POST.get("allow_heart_rate") == "on",
                "allow_sleep": request.POST.get("allow_sleep") == "on",
                "allow_calories": request.POST.get("allow_calories") == "on",
                "allow_exercise": request.POST.get("allow_exercise") == "on",
                "allow_weight_bmi": request.POST.get("allow_weight_bmi") == "on",
                "allow_stress": request.POST.get("allow_stress") == "on",
            }
            HealthService.save_consent_settings(request.user, platform, consent_data)
            messages.success(request, f"Privacy settings for {platform.replace('_', ' ').title()} updated.")

        return redirect("health_integrations")


class OAuthCallbackView(LoginRequiredMixin, View):
    def get(self, request):
        from django.contrib import messages
        from apps.moods.services.health_service import HealthService

        platform = request.GET.get("platform", "fitbit")
        # Simulating OAuth code flow connection
        integration = HealthService.get_or_create_integration(request.user, platform)
        integration.is_connected = True
        integration.save()

        messages.success(request, f"Successfully authorized integration with {platform.replace('_', ' ').title()}!")
        return redirect("health_integrations")


class DeleteHealthDataView(LoginRequiredMixin, View):
    def post(self, request):
        from django.contrib import messages
        from apps.moods.services.health_service import HealthService

        HealthService.delete_user_health_data(request.user)
        messages.warning(request, "All synchronized health logs deleted and platform integrations reset.")
        return redirect("health_integrations")
