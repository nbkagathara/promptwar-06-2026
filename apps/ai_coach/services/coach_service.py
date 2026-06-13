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

    @staticmethod
    def get_chat_history(user: User, limit: int = 30) -> list:
        """
        Retrieves the latest chat message history for the user.
        """
        from apps.ai_coach.models import ChatMessage
        return ChatMessage.objects.filter(user=user).order_by("created_at")[:limit]

    @classmethod
    def send_chat_message(cls, user: User, content: str) -> dict:
        """
        Processes a user's chat message, checks safety limits, constructs contexts,
        queries AI service, and returns both user and assistant message records.
        """
        from apps.ai_coach.models import ChatMessage
        from services.safety_engine import SafetyEngine
        from apps.safety.models import SafetyAlert, AuditLog

        # 1. Save user chat message
        user_msg = ChatMessage.objects.create(
            user=user,
            role="user",
            content=content
        )

        # 2. Run safety engine
        safety_res = SafetyEngine.analyze_safety(content)
        safety_level = safety_res["safety_level"]
        detected_terms = ", ".join(safety_res["detected_terms"])

        if safety_level == "CRITICAL":
            # Crisis safety limit triggered: bypass AI call and immediately respond with helpline info
            alert = SafetyAlert.objects.create(
                user=user,
                safety_level="CRITICAL",
                detected_terms=detected_terms,
                resolved=False
            )
            AuditLog.objects.create(
                user=user,
                action=f"CRITICAL SAFETY ALERT IN CHAT COMPANION: Detected terms '{detected_terms}'"
            )
            logger.warning(f"Critical safety escalation in companion chat for user {user.username}")

            crisis_content = (
                "I am concernced about your well-being. Please remember that you are not alone, and there is support available. "
                "Because your safety is important, I want to encourage you to connect with professionals who can help you right now. "
                "Please call or text a helpline: Vandrevala Foundation at +91 9999 666 555, or AASRA at +91-9820466726. "
                "These services are free, confidential, and available 24/7. Please reach out to them."
            )
            assistant_msg = ChatMessage.objects.create(
                user=user,
                role="assistant",
                content=crisis_content
            )
            return {
                "user_message": user_msg,
                "assistant_message": assistant_msg,
                "safety_escalation": True
            }

        elif safety_level == "WARNING":
            # Record warning alert but allow conversational AI response
            SafetyAlert.objects.create(
                user=user,
                safety_level="WARNING",
                detected_terms=detected_terms,
                resolved=False
            )
            AuditLog.objects.create(
                user=user,
                action=f"Warning safety alert in chat: Detected terms '{detected_terms}'"
            )

        # 3. Gather Exam & Telemetry context for personalized support
        exam_name = "High-Stakes"
        if hasattr(user, "profile") and user.profile.exam_type:
            exam_name = user.profile.exam_type.name

        mood_logs = MoodLog.objects.filter(user=user).order_by("-logged_date")[:5]
        mood_history = [
            {"date": log.logged_date.isoformat(), "mood": log.mood_score, "stress": log.stress_score}
            for log in mood_logs
        ]

        journals = JournalEntry.objects.filter(user=user).order_by("-created_at")[:2]
        recent_journals = [j.content[:150] for j in journals]

        from apps.moods.models import HealthDataLog
        health_logs = HealthDataLog.objects.filter(user=user).order_by("-logged_date")[:2]
        health_history = [
            {"date": log.logged_date.isoformat(), "steps": log.steps, "sleep_hours": log.sleep_hours, "heart_rate": log.resting_heart_rate}
            for log in health_logs
        ]

        # 4. Construct System Instruction Prompt
        system_prompt = (
            f"You are AuraWell's Empathetic AI Wellness Coach and Digital Companion for students.\n"
            f"You are helping a student preparing for the '{exam_name}' competitive exam.\n"
            f"Here is the context of their recent wellbeing metrics to personalize your responses:\n"
            f"- Recent mood logs (1=Very low, 5=Excellent): {mood_history}\n"
            f"- Recent journal entries: {recent_journals}\n"
            f"- Recent health/wearable logs (sleep/steps/heart rate): {health_history}\n\n"
            f"Your Role Rules:\n"
            f"1. Always communicate with deep empathy, warmth, and supportive encouragement.\n"
            f"2. Suggest contextual wellness strategies: real-time coping strategies (e.g. quick desk breaks, sleep hygiene, or study load prioritization) "
            f"and adaptive mindfulness/breathing exercises.\n"
            f"3. Maintain boundaries: Do NOT answer exam prep curriculum questions or write code/math equations. If the user asks standard test prep questions (e.g. 'Solve this math problem'), "
            f"politely redirect them to taking a break, study planning, or checking their wellness.\n"
            f"4. Keep responses conversational, short (2-3 paragraphs max), and clear."
        )

        # 5. Extract Chat history (last 10 messages)
        history_msgs = ChatMessage.objects.filter(user=user).exclude(id=user_msg.id).order_by("-created_at")[:10]
        history_list = []
        # Reverse to get chronological order
        for h in reversed(history_msgs):
            history_list.append({"role": h.role, "content": h.content})

        # Append new user message to the conversation list
        history_list.append({"role": "user", "content": content})

        # 6. Generate AI response
        ai_reply = AIService.generate_chat_response(system_prompt, history_list)

        # 7. Save and return response
        assistant_msg = ChatMessage.objects.create(
            user=user,
            role="assistant",
            content=ai_reply
        )

        return {
            "user_message": user_msg,
            "assistant_message": assistant_msg,
            "safety_escalation": False
        }

