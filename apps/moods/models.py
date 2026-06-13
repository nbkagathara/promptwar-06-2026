from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class MoodLog(models.Model):
    MOOD_CHOICES = [
        (1, "Very Low / Depressed"),
        (2, "Low / Anxious"),
        (3, "Neutral / Okay"),
        (4, "Good / Happy"),
        (5, "Excellent / Energetic"),
    ]
    STRESS_CHOICES = [
        (1, "No Stress / Calm"),
        (2, "Low Stress"),
        (3, "Moderate / Manageable"),
        (4, "High Stress / Heavy"),
        (5, "Extreme Stress / Overwhelmed"),
    ]
    ENERGY_CHOICES = [
        (1, "Exhausted / Low"),
        (2, "Tired / Sluggish"),
        (3, "Normal / Steady"),
        (4, "High Energy"),
        (5, "Peaked / Very Active"),
    ]
    SLEEP_CHOICES = [
        (1, "Terrible / Restless"),
        (2, "Poor Sleep"),
        (3, "Average / Sufficient"),
        (4, "Good Rest"),
        (5, "Deep / Restorative"),
    ]
    STUDY_CHOICES = [
        (1, "Highly Unsatisfied"),
        (2, "Disappointed"),
        (3, "Acceptable / Progressing"),
        (4, "Satisfied / Productive"),
        (5, "Highly Satisfied / Peak Study Day"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mood_logs")
    mood_score = models.IntegerField(choices=MOOD_CHOICES, help_text="Mood score from 1 (very low) to 5 (excellent)")
    stress_score = models.IntegerField(choices=STRESS_CHOICES, help_text="Stress score from 1 (no stress) to 5 (extreme stress)")
    energy_level = models.IntegerField(choices=ENERGY_CHOICES, help_text="Energy level from 1 (very low) to 5 (very high)")
    sleep_quality = models.IntegerField(choices=SLEEP_CHOICES, help_text="Sleep quality from 1 (terrible) to 5 (excellent)")
    study_satisfaction = models.IntegerField(choices=STUDY_CHOICES, help_text="Study satisfaction from 1 (unsatisfied) to 5 (highly satisfied)")
    logged_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-logged_date"]
        unique_together = ("user", "logged_date")

    def __str__(self):
        return f"{self.user.username}'s mood on {self.logged_date}"
