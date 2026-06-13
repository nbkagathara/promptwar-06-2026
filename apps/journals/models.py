from django.contrib.auth.models import User
from django.db import models


class JournalEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="journal_entries")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}'s entry on {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class AIAnalysis(models.Model):
    journal_entry = models.OneToOneField(
        JournalEntry, on_delete=models.CASCADE, related_name="analysis"
    )
    primary_emotion = models.CharField(max_length=50)
    stress_indicators = models.JSONField(default=list)
    burnout_risk = models.CharField(
        max_length=10,
        choices=[("LOW", "Low"), ("MEDIUM", "Medium"), ("HIGH", "High")],
        default="LOW",
    )
    motivation_trends = models.JSONField(default=list)
    summary = models.TextField()
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Analysis for entry {self.journal_entry.id}"
