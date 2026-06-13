from django.contrib.auth.models import User
from django.utils import timezone
from apps.moods.models import MoodLog
from apps.safety.models import AuditLog


class MoodService:
    @staticmethod
    def log_daily_mood(
        user: User,
        mood_score: int,
        stress_score: int,
        energy_level: int,
        sleep_quality: int,
        study_satisfaction: int,
        date_logged=None,
    ) -> MoodLog:
        """
        Logs or updates daily mood parameters.
        """
        if not date_logged:
            date_logged = timezone.now().date()

        # Update if exists, otherwise create
        mood_log, created = MoodLog.objects.update_or_create(
            user=user,
            logged_date=date_logged,
            defaults={
                "mood_score": mood_score,
                "stress_score": stress_score,
                "energy_level": energy_level,
                "sleep_quality": sleep_quality,
                "study_satisfaction": study_satisfaction,
            },
        )

        action_msg = "Created daily mood log" if created else "Updated daily mood log"
        AuditLog.objects.create(user=user, action=f"{action_msg} for date: {date_logged}")
        return mood_log
