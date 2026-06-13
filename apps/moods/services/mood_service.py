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
            date_logged = timezone.localdate()


        # Create new mood log record (allowing multiple logs per day)
        mood_log = MoodLog.objects.create(
            user=user,
            logged_date=date_logged,
            mood_score=mood_score,
            stress_score=stress_score,
            energy_level=energy_level,
            sleep_quality=sleep_quality,
            study_satisfaction=study_satisfaction,
        )

        AuditLog.objects.create(user=user, action=f"Created mood log for date: {date_logged}")
        return mood_log

