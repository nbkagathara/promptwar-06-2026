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
    def generate_coach_guidance(cls, profile_info: dict, mood_history: list, recent_journals: list, health_history: list = None) -> dict:
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
            f"Recent Wearable Health Logs (steps, sleep, heart rate): {health_history}\n"
            "Provide 4 highly specific, empathetic, and actionable recommendations (one for each type: MINDFULNESS, STUDY_BREAK, MOTIVATION, TIME_MGMT).\n"
            "Respond ONLY with a valid JSON object matching this schema:\n"
            "{\n"
            '  "recommendations": [\n'
            '    {"type": "MINDFULNESS", "content": "detailed exercise instructions based on journal/health logs"},\n'
            '    {"type": "STUDY_BREAK", "content": "detailed study break suggestions based on sleep/steps logs"},\n'
            '    {"type": "MOTIVATION", "content": "encouraging motivational message matching journal mood"},\n'
            '    {"type": "TIME_MGMT", "content": "actionable study load organization suggestions"}\n'
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
        return cls._mock_coach_guidance(profile_info, recent_journals, health_history)

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
    def _resolve_gemini_model(cls, model_name: str) -> str:
        import google.generativeai as genai
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            available = [m.name for m in genai.list_models()]
            target = model_name if model_name.startswith("models/") else f"models/{model_name}"
            if target in available:
                return target
            
            alternatives = [
                "models/gemini-3.5-flash",
                "models/gemini-2.5-flash",
                "models/gemini-2.0-flash",
                "models/gemini-flash-latest",
            ]
            for alt in alternatives:
                if alt in available:
                    logger.info(f"Model {target} not available. Mapping to {alt}.")
                    return alt
            
            for m in available:
                if "flash" in m.lower():
                    logger.info(f"Model {target} not available. Mapping to {m}.")
                    return m
            return target
        except Exception as e:
            logger.warning(f"Error listing gemini models: {str(e)}")
            return model_name if model_name.startswith("models/") else f"models/{model_name}"

    @classmethod
    def _call_gemini(cls, prompt: str) -> dict:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model_name = getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")
        model_resolved = cls._resolve_gemini_model(model_name)
        model = genai.GenerativeModel(model_resolved)
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
    def _mock_coach_guidance(cls, profile_info: dict, recent_journals: list = None, health_history: list = None) -> dict:
        exam_name = profile_info.get("exam_name", "your upcoming exam")

        # Analyze recent journals content dynamically for mock output
        journal_text = " ".join(recent_journals or []).lower()

        # Analyze health history dynamically for mock output
        latest_steps = 8000
        latest_sleep = 7.5
        if health_history and len(health_history) > 0:
            latest_steps = health_history[0].get("steps", 8000)
            latest_sleep = health_history[0].get("sleep_hours", 7.5)

        # Dynamic mindfulness response based on journal context
        mindfulness_content = f"4-7-8 Breathing Technique: Sit comfortably. Inhale for 4 seconds, hold for 7 seconds, exhale for 8 seconds. Repeat 4 times to calm your nervous system before starting your {exam_name} revision."
        if "stressed" in journal_text or "anxious" in journal_text or "pressure" in journal_text:
            mindfulness_content = "Vagus Nerve Stimulation: Splash cold water on your face or perform a 5-minute deep belly breathing session. Focus on expanding your diaphragm. This counteracts the physiological response to high exam anxieties."
        elif "tired" in journal_text or "exhausted" in journal_text:
            mindfulness_content = "Progressive Muscle Relaxation: Starting from your toes, tense each muscle group for 5 seconds and release. This helps release the physical tension built up from hours of desk study."

        # Dynamic study break response based on steps
        break_content = "Apply the 50/10 Rule: Study for 50 minutes, then take a 10-minute active break. Walk, stretch, or drink water. Do not look at screens during the break."
        if latest_steps < 6000:
            break_content = f"Since your wearable logged only {latest_steps} steps today, take a brisk 15-minute outdoor walk during your next break. Physical movement improves cognitive function before {exam_name} sessions."

        # Dynamic motivation based on journals
        motivate_content = f"Preparing for {exam_name} is a marathon, not a sprint. Your value is not defined by a single mock test score. Celebrate your efforts today!"
        if "fail" in journal_text or "scared" in journal_text:
            motivate_content = "It's normal to fear failure, but remember that mock tests are tools to learn, not definitions of your final score. You have the resilience to improve!"

        # Dynamic time management based on sleep
        time_content = "Prioritize with the Eisenhower Matrix: Focus first on High Importance + High Urgency topics. Delegate or postpone minor revisions to avoid evening study fatigue."
        if latest_sleep < 6.5:
            time_content = f"Wearables logged only {latest_sleep} hours of sleep. Prioritize getting 7.5+ hours tonight. Rest has a higher impact on memory consolidation than late-night cramming."

        return {
            "recommendations": [
                {
                    "type": "MINDFULNESS",
                    "content": mindfulness_content,
                },
                {
                    "type": "STUDY_BREAK",
                    "content": break_content,
                },
                {
                    "type": "MOTIVATION",
                    "content": motivate_content,
                },
                {
                    "type": "TIME_MGMT",
                    "content": time_content,
                },
            ]
        }

    @classmethod
    def generate_chat_response(cls, system_prompt: str, chat_history: list) -> str:
        """
        Generates an empathetic chat response from the configured AI provider.
        """
        provider = cls.get_provider()
        try:
            if provider == "openai" and getattr(settings, "OPENAI_API_KEY", ""):
                return cls._call_openai_chat(system_prompt, chat_history)
            elif provider == "gemini" and getattr(settings, "GEMINI_API_KEY", ""):
                return cls._call_gemini_chat(system_prompt, chat_history)
            elif provider == "azure" and getattr(settings, "AZURE_OPENAI_API_KEY", ""):
                return cls._call_azure_chat(system_prompt, chat_history)
        except Exception as e:
            logger.error(f"Error calling AI chat provider {provider}: {str(e)}")

        return cls._mock_chat_response(chat_history)

    @classmethod
    def _call_openai_chat(cls, system_prompt: str, chat_history: list) -> str:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        messages = [{"role": "system", "content": system_prompt}] + chat_history
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    @classmethod
    def _call_gemini_chat(cls, system_prompt: str, chat_history: list) -> str:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model_name = getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")
        model_resolved = cls._resolve_gemini_model(model_name)
        model = genai.GenerativeModel(model_resolved)
        
        prompt = f"System Instruction:\n{system_prompt}\n\n"
        for msg in chat_history:
            role = "Student" if msg["role"] == "user" else "Companion"
            prompt += f"{role}: {msg['content']}\n"
        prompt += "Companion:"
        
        response = model.generate_content(prompt)
        return response.text.strip()

    @classmethod
    def _call_azure_chat(cls, system_prompt: str, chat_history: list) -> str:
        import requests
        headers = {
            "Content-Type": "application/json",
            "api-key": settings.AZURE_OPENAI_API_KEY,
        }
        messages = [{"role": "system", "content": system_prompt}] + chat_history
        data = {
            "messages": messages,
            "temperature": 0.7,
        }
        url = f"{settings.AZURE_OPENAI_ENDPOINT}/openai/deployments/gpt-35-turbo/chat/completions?api-version=2023-05-15"
        res = requests.post(url, headers=headers, json=data, timeout=10)
        res.raise_for_status()
        res_json = res.json()
        return res_json["choices"][0]["message"]["content"].strip()

    @classmethod
    def _mock_chat_response(cls, chat_history: list) -> str:
        last_message = chat_history[-1]["content"].lower() if chat_history else ""
        if "stressed" in last_message or "pressure" in last_message or "exam" in last_message or "neet" in last_message or "jee" in last_message or "upsc" in last_message or "gate" in last_message or "cat" in last_message or "study" in last_message:
            return (
                "I completely understand. High-stakes exam preparation can feel like an immense weight. "
                "Remember, it's a marathon, not a sprint. To help manage this pressure right now, let's try a quick grounding exercise: "
                "breathe in deeply for 4 seconds, hold for 4, and release for 4. Focus on this moment. You are doing the best you can."
            )
        elif "tired" in last_message or "sleep" in last_message or "exhausted" in last_message or "burnout" in last_message:
            return (
                "Your physical health is critical for your academic performance. Burning the midnight oil might feel productive, "
                "but sleep consolidation is when your brain actually stores information. "
                "I recommend taking a 15-minute study break right now to walk around or stretch. "
                "Make sure you aim for 7.5+ hours of sleep tonight to perform your best."
            )
        elif "anxious" in last_message or "scared" in last_message or "fail" in last_message or "worry" in last_message:
            return (
                "It's completely normal to feel anxious about the outcome, but try to focus on the process rather than the destination. "
                "A study day that didn't go well is simply feedback, not a definition of your intelligence or final exam score. "
                "You have shown incredible persistence, and you are building resilience. Be kind to yourself today."
            )
        elif "hello" in last_message or "hi" in last_message or "hey" in last_message:
            return (
                "Hello! I am your wellness companion. I'm here to support you through your prep journey. "
                "How are you feeling today, and how is your preparation going?"
            )
        else:
            return (
                "I hear you, and I am here for you. Study stress is very real, and you don't have to carry it alone. "
                "Let's focus on taking small, manageable steps today. What is one area or topic where you're feeling a bit stuck or overwhelmed right now?"
            )

