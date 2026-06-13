import json
import logging
from django.conf import settings

logger = logging.getLogger("app")


class AIService:
    @classmethod
    def get_provider(cls):
        return getattr(settings, "AI_PROVIDER", "mock").lower()

    @classmethod
    def analyze_journal(cls, content: str) -> dict:
        """
        Analyzes a journal entry using the configured AI provider.
        Returns a dictionary:
        {
            'primary_emotion': str,
            'stress_indicators': list,
            'burnout_risk': 'LOW' | 'MEDIUM' | 'HIGH',
            'motivation_trends': list,
            'summary': str
        }
        """
        provider = cls.get_provider()
        prompt = (
            "Analyze the following student exam preparation journal entry.\n"
            f"Journal Entry: \"{content}\"\n"
            "Respond ONLY with a valid JSON object matching this schema:\n"
            "{\n"
            '  "primary_emotion": "string describing primary emotion",\n'
            '  "stress_indicators": ["indicator1", "indicator2"],\n'
            '  "burnout_risk": "LOW" or "MEDIUM" or "HIGH",\n'
            '  "motivation_trends": ["trend1", "trend2"],\n'
            '  "summary": "a short empathetic summary of the user\'s feelings"\n'
            "}"
        )

        try:
            if provider == "openai" and getattr(settings, "OPENAI_API_KEY", ""):
                return cls._call_openai(prompt)
            elif provider == "gemini" and getattr(settings, "GEMINI_API_KEY", ""):
                return cls._call_gemini(prompt)
            elif provider == "azure" and getattr(settings, "AZURE_OPENAI_API_KEY", ""):
                return cls._call_azure(prompt)
        except Exception as e:
            logger.error(f"Error calling AI provider {provider}: {str(e)}")

        # Fallback to mock behavior
        return cls._mock_journal_analysis(content)

    @classmethod
    def generate_coach_guidance(cls, profile_info: dict, mood_history: list, recent_journals: list) -> dict:
        """
        Generates personalized guidance from a digital wellness coach.
        Returns a dictionary:
        {
            'recommendations': [
                {'type': 'MINDFULNESS' | 'STUDY_BREAK' | 'MOTIVATION' | 'TIME_MGMT', 'content': '...'}
            ]
        }
        """
        provider = cls.get_provider()
        prompt = (
            f"Based on a student preparing for the {profile_info.get('exam_name', 'High-Stakes')} exam.\n"
            f"Recent Mood Scores (out of 5): {mood_history}\n"
            f"Recent Journals: {recent_journals}\n"
            "Provide 4 highly specific, empathetic, and actionable recommendations (one for each type: MINDFULNESS, STUDY_BREAK, MOTIVATION, TIME_MGMT).\n"
            "Respond ONLY with a valid JSON object matching this schema:\n"
            "{\n"
            '  "recommendations": [\n'
            '    {"type": "MINDFULNESS", "content": "detailed exercise instructions"},\n'
            '    {"type": "STUDY_BREAK", "content": "detailed study break suggestions"},\n'
            '    {"type": "MOTIVATION", "content": "encouraging motivational message"},\n'
            '    {"type": "TIME_MGMT", "content": "actionable time management suggestion"}\n'
            "  ]\n"
            "}"
        )

        try:
            if provider == "openai" and getattr(settings, "OPENAI_API_KEY", ""):
                return cls._call_openai_guidance(prompt)
            elif provider == "gemini" and getattr(settings, "GEMINI_API_KEY", ""):
                return cls._call_gemini_guidance(prompt)
            elif provider == "azure" and getattr(settings, "AZURE_OPENAI_API_KEY", ""):
                return cls._call_azure_guidance(prompt)
        except Exception as e:
            logger.error(f"Error generating coach guidance with provider {provider}: {str(e)}")

        # Fallback to mock guidance
        return cls._mock_coach_guidance(profile_info)

    # Internal API calling methods
    @classmethod
    def _call_openai(cls, prompt: str) -> dict:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return json.loads(response.choices[0].message.content.strip())

    @classmethod
    def _call_openai_guidance(cls, prompt: str) -> dict:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return json.loads(response.choices[0].message.content.strip())

    @classmethod
    def _call_gemini(cls, prompt: str) -> dict:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model_name = getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        # Handle simple markdown cleanup if returned
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
        return json.loads(text.strip())

    @classmethod
    def _call_gemini_guidance(cls, prompt: str) -> dict:
        return cls._call_gemini(prompt)

    @classmethod
    def _call_azure(cls, prompt: str) -> dict:
        import requests
        headers = {
            "Content-Type": "application/json",
            "api-key": settings.AZURE_OPENAI_API_KEY,
        }
        data = {
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        url = f"{settings.AZURE_OPENAI_ENDPOINT}/openai/deployments/gpt-35-turbo/chat/completions?api-version=2023-05-15"
        res = requests.post(url, headers=headers, json=data, timeout=10)
        res.raise_for_status()
        res_json = res.json()
        return json.loads(res_json["choices"][0]["message"]["content"].strip())

    @classmethod
    def _call_azure_guidance(cls, prompt: str) -> dict:
        return cls._call_azure(prompt)

    # Mock Data Fallbacks
    @classmethod
    def _mock_journal_analysis(cls, content: str) -> dict:
        content_lower = content.lower()
        if "stress" in content_lower or "pressure" in content_lower or "scared" in content_lower:
            return {
                "primary_emotion": "Anxiety / Exam Pressure",
                "stress_indicators": ["Fear of failing standard tests", "Time constraints"],
                "burnout_risk": "MEDIUM",
                "motivation_trends": ["Driven by fear of exam date", "Needs regular breaks"],
                "summary": "The entry reflects standard high-stress symptoms due to test preparations.",
            }
        elif "tired" in content_lower or "exhausted" in content_lower or "give up" in content_lower:
            return {
                "primary_emotion": "Exhaustion / Burnout Risk",
                "stress_indicators": ["Lack of sleep", "Continuous study without recreation"],
                "burnout_risk": "HIGH",
                "motivation_trends": ["Experiencing motivational dip", "Struggling to stay positive"],
                "summary": "The entry suggests high vulnerability to academic burnout; urgent rest is recommended.",
            }
        else:
            return {
                "primary_emotion": "Calm / Optimistic",
                "stress_indicators": ["Mild anticipation stress"],
                "burnout_risk": "LOW",
                "motivation_trends": ["Goal-oriented and steady"],
                "summary": "The entry shows healthy progress and positive framing of study targets.",
            }

    @classmethod
    def _mock_coach_guidance(cls, profile_info: dict) -> dict:
        exam_name = profile_info.get("exam_name", "your upcoming exam")
        return {
            "recommendations": [
                {
                    "type": "MINDFULNESS",
                    "content": f"4-7-8 Breathing Technique: Sit comfortably. Inhale for 4 seconds, hold for 7 seconds, exhale for 8 seconds. Repeat 4 times to calm your nervous system before starting your {exam_name} revision.",
                },
                {
                    "type": "STUDY_BREAK",
                    "content": "Apply the 50/10 Rule: Study for 50 minutes, then take a 10-minute active break. Walk, stretch, or drink water. Do not look at screens during the break.",
                },
                {
                    "type": "MOTIVATION",
                    "content": f"Preparing for {exam_name} is a marathon, not a sprint. Your value is not defined by a single mock test score. Celebrate your efforts today!",
                },
                {
                    "type": "TIME_MGMT",
                    "content": "Prioritize with the Eisenhower Matrix: Focus first on High Importance + High Urgency topics. Delegate or postpone minor revisions to avoid evening study fatigue.",
                },
            ]
        }
