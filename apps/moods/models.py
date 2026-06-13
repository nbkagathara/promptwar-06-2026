from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class MoodLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mood_logs")
    mood_score = models.IntegerField(help_text="Mood score from 1 (very low) to 5 (excellent)")
    stress_score = models.IntegerField(help_text="Stress score from 1 (no stress) to 5 (extreme stress)")
    energy_level = models.IntegerField(help_text="Energy level from 1 (very low) to 5 (very high)")
    sleep_quality = models.IntegerField(help_text="Sleep quality from 1 (terrible) to 5 (excellent)")
    study_satisfaction = models.IntegerField(help_text="Study satisfaction from 1 (unsatisfied) to 5 (highly satisfied)")
    logged_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-logged_date"]
        unique_together = ("user", "logged_date")

    def __str__(self):
        return f"{self.user.username}'s mood on {self.logged_date}"
