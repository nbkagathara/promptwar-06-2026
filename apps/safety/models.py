from django.contrib.auth.models import User
from django.db import models


class SafetyAlert(models.Model):
    SAFETY_LEVELS = [
        ("WARNING", "Warning"),
        ("CRITICAL", "Critical / Crisis"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="safety_alerts")
    journal_entry = models.ForeignKey(
        "journals.JournalEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="safety_alerts",
    )
    safety_level = models.CharField(max_length=15, choices=SAFETY_LEVELS, default="WARNING")
    detected_terms = models.TextField(help_text="Terms or context that triggered the alert")
    triggered_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-triggered_at"]

    def __str__(self):
        return f"{self.safety_level} Alert for {self.user.username} on {self.triggered_at.strftime('%Y-%m-%d')}"


class AuditLog(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs"
    )
    action = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        user_str = self.user.username if self.user else "Anonymous"
        return f"{self.action} by {user_str} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
