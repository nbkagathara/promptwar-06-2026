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


class HealthDataLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="health_logs")
    logged_date = models.DateField(default=timezone.now)
    steps = models.IntegerField(default=0, help_text="Daily steps synced from device")
    active_minutes = models.IntegerField(default=0, help_text="Daily active minutes")
    sleep_hours = models.FloatField(default=0.0, help_text="Daily sleep duration in hours")
    sleep_quality_score = models.IntegerField(default=0, help_text="Sleep quality score from 1 to 100")
    resting_heart_rate = models.IntegerField(default=70, help_text="Average resting heart rate")
    avg_heart_rate = models.IntegerField(default=0, help_text="Average daily heart rate")
    max_heart_rate = models.IntegerField(default=0, help_text="Maximum daily heart rate")
    calories_burned = models.IntegerField(default=0, help_text="Daily calories burned")
    exercise_sessions_count = models.IntegerField(default=0, help_text="Count of exercise/workout sessions")
    exercise_duration_minutes = models.IntegerField(default=0, help_text="Total exercise duration in minutes")
    weight_kg = models.FloatField(default=0.0, help_text="User weight in kg")
    bmi = models.FloatField(default=0.0, help_text="User Body Mass Index")
    stress_level_score = models.IntegerField(default=0, help_text="Stress score from 1 to 100")
    mindfulness_minutes = models.IntegerField(default=0, help_text="Daily mindfulness/meditation minutes")
    source = models.CharField(max_length=50, default="Apple Health")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-logged_date"]
        unique_together = ("user", "logged_date")

    def __str__(self):
        return f"{self.user.username}'s health logs on {self.logged_date} ({self.source})"


class HealthIntegration(models.Model):
    PLATFORM_CHOICES = [
        ("google_fit", "Google Fit"),
        ("apple_health", "Apple Health"),
        ("fitbit", "Fitbit"),
        ("smart_band", "Smartwatch/Fitness Band"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="health_integrations")
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    is_connected = models.BooleanField(default=False)
    connected_at = models.DateTimeField(null=True, blank=True)
    access_token = models.TextField(null=True, blank=True)
    refresh_token = models.TextField(null=True, blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)

    # Granular permissions
    allow_steps = models.BooleanField(default=True)
    allow_heart_rate = models.BooleanField(default=True)
    allow_sleep = models.BooleanField(default=True)
    allow_calories = models.BooleanField(default=True)
    allow_exercise = models.BooleanField(default=True)
    allow_weight_bmi = models.BooleanField(default=True)
    allow_stress = models.BooleanField(default=True)

    class Meta:
        unique_together = ("user", "platform")

    def __str__(self):
        return f"{self.user.username}'s {self.platform} Integration"
