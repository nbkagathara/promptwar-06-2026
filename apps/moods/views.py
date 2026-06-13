from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
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
