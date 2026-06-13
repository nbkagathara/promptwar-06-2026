from django.contrib.auth.models import User
from django.db import models


class AIRecommendation(models.Model):
    REC_TYPES = [
        ("MINDFULNESS", "Mindfulness Exercise"),
        ("STUDY_BREAK", "Study-Life Balance / Break"),
        ("MOTIVATION", "Motivational Encouragement"),
        ("TIME_MGMT", "Time Management Suggestion"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recommendations")
    rec_type = models.CharField(max_length=20, choices=REC_TYPES)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_rec_type_display()} for {self.user.username}"


class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_messages")
    role = models.CharField(max_length=10, choices=[("user", "User"), ("assistant", "Assistant")])
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.role}: {self.content[:30]}"

