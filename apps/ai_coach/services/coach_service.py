import logging
from django.contrib.auth.models import User
from apps.ai_coach.models import AIRecommendation
from apps.moods.models import MoodLog
from apps.journals.models import JournalEntry
from services.ai_service import AIService

logger = logging.getLogger("app")


class CoachService:
    @staticmethod
    def get_latest_recommendations(user: User, limit: int = 4) -> list:
        """
        Retrieves the latest recommendations for a user.
        """
        return AIRecommendation.objects.filter(user=user)[:limit]

    @classmethod
    def generate_user_coach_guidance(cls, user: User) -> list:
        """
        Gathers profile, mood, and journal context, and requests new AI recommendations.
        """
        # 1. Profile information
        exam_name = "High-Stakes"
        if hasattr(user, "profile") and user.profile.exam_type:
            exam_name = user.profile.exam_type.name

        profile_info = {"exam_name": exam_name}

        # 2. Get last 7 mood logs
        mood_logs = MoodLog.objects.filter(user=user).order_by("-logged_date")[:7]
        mood_history = [
            {
                "date": log.logged_date.isoformat(),
                "mood": log.mood_score,
                "stress": log.stress_score,
            }
            for log in mood_logs
        ]

        # 3. Get last 3 journal entries
        journals = JournalEntry.objects.filter(user=user).order_by("-created_at")[:3]
        recent_journals = [j.content[:200] for j in journals]

        # 3.5. Get last 3 wearable health logs
        from apps.moods.models import HealthDataLog
        health_logs = HealthDataLog.objects.filter(user=user).order_by("-logged_date")[:3]
        health_history = [
            {
                "date": log.logged_date.isoformat(),
                "steps": log.steps,
                "sleep_hours": log.sleep_hours,
                "heart_rate": log.resting_heart_rate,
                "source": log.source
            }
            for log in health_logs
        ]

        # 4. Generate recommendations
        guidance_data = AIService.generate_coach_guidance(
            profile_info, mood_history, recent_journals, health_history
        )

        recs = []
        recommendations_list = guidance_data.get("recommendations", [])

        # Create recommendations in database
        for rec in recommendations_list:
            rec_type = rec.get("type", "MOTIVATION")
            content = rec.get("content", "")
            if content:
                # We can choose to overwrite or just insert new ones
                rec_obj = AIRecommendation.objects.create(
                    user=user,
                    rec_type=rec_type,
                    content=content,
                )
                recs.append(rec_obj)

        return recs
