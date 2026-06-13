import logging
from django.contrib.auth.models import User
from apps.journals.models import JournalEntry, AIAnalysis
from apps.safety.models import SafetyAlert, AuditLog
from services.safety_engine import SafetyEngine
from services.ai_service import AIService
from apps.ai_coach.models import AIRecommendation

logger = logging.getLogger("app")


class JournalService:
    @staticmethod
    def create_and_analyze_journal(user: User, content: str) -> tuple:
        """
        Creates a journal entry, performs safety checks, and handles AI analysis if safe.
        Returns a tuple: (journal_entry, safety_level, alert_obj)
        """
        # 1. Create journal entry
        entry = JournalEntry.objects.create(user=user, content=content)

        # 2. Run safety engine
        safety_res = SafetyEngine.analyze_safety(content)
        safety_level = safety_res["safety_level"]
        detected_terms = ", ".join(safety_res["detected_terms"])

        alert = None

        if safety_level == "CRITICAL":
            # Crisis detected: create a critical alert and bypass AI generation
            alert = SafetyAlert.objects.create(
                user=user,
                journal_entry=entry,
                safety_level="CRITICAL",
                detected_terms=detected_terms,
                resolved=False,
            )
            AuditLog.objects.create(
                user=user,
                action=f"CRITICAL SAFETY ALERT TRIGGERED: Detected terms '{detected_terms}' in journal entry {entry.id}",
            )
            logger.warning(f"Critical safety escalation for user {user.username} (Entry ID: {entry.id})")

            # Immediately add an emergency local notification/recommendation to check safety resources
            AIRecommendation.objects.create(
                user=user,
                rec_type="MOTIVATION",
                content=(
                    "It seems you are going through a very tough time. Please remember that you are not alone, "
                    "and there are people who want to support you. We strongly encourage you to reach out to "
                    "professional support resources listed on your dashboard."
                ),
            )
            return entry, safety_level, alert

        elif safety_level == "WARNING":
            # Moderate distress detected
            alert = SafetyAlert.objects.create(
                user=user,
                journal_entry=entry,
                safety_level="WARNING",
                detected_terms=detected_terms,
                resolved=False,
            )
            AuditLog.objects.create(
                user=user,
                action=f"Warning safety alert triggered: Detected terms '{detected_terms}' in journal entry {entry.id}",
            )

        # 3. Request AI Analysis for SAFE/WARNING entries
        try:
            analysis_data = AIService.analyze_journal(content)
            AIAnalysis.objects.create(
                journal_entry=entry,
                primary_emotion=analysis_data.get("primary_emotion", "Neutral"),
                stress_indicators=analysis_data.get("stress_indicators", []),
                burnout_risk=analysis_data.get("burnout_risk", "LOW"),
                motivation_trends=analysis_data.get("motivation_trends", []),
                summary=analysis_data.get("summary", ""),
            )

            # Generate fresh personalized recommendations based on new entry
            cls_coach = CoachServiceHelper
            cls_coach.generate_personalized_recommendations(user)
        except Exception as e:
            logger.error(f"Failed to analyze journal entry {entry.id} via AI: {str(e)}")

        AuditLog.objects.create(
            user=user, action=f"Journal entry {entry.id} saved and analyzed successfully."
        )
        return entry, safety_level, alert


class CoachServiceHelper:
    """Helper to avoid circular dependencies when triggering coach recommendations from journals"""
    @staticmethod
    def generate_personalized_recommendations(user: User):
        from apps.ai_coach.services.coach_service import CoachService
        try:
            CoachService.generate_user_coach_guidance(user)
        except Exception as e:
            logger.error(f"Could not generate personalized coach suggestions: {str(e)}")
