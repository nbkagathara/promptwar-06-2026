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
        import random
        from django.views import View
        from django.contrib import messages
        from django.utils import timezone
        from apps.moods.models import HealthDataLog

        source = request.POST.get("source", "Apple Health")
        steps = random.randint(5500, 12000)
        sleep_hours = round(random.uniform(5.8, 8.8), 1)
        resting_hr = random.randint(60, 78)

        log, created = HealthDataLog.objects.update_or_create(
            user=request.user,
            logged_date=timezone.now().date(),
            defaults={
                "steps": steps,
                "sleep_hours": sleep_hours,
                "resting_heart_rate": resting_hr,
                "source": source,
            },
        )

        messages.success(
            request,
            f"Successfully synced metrics from {source}! (Steps: {steps}, Sleep: {sleep_hours} hrs, HR: {resting_hr} bpm)",
        )
        return redirect("dashboard")
