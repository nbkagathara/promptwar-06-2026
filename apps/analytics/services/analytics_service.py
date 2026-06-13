from datetime import timedelta
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from django.utils import timezone
from apps.moods.models import MoodLog
from apps.journals.models import JournalEntry, AIAnalysis


class AnalyticsService:
    @staticmethod
    def get_mood_trends(user: User, days: int = 7) -> dict:
        """
        Retrieves mood score, stress score, energy level, and other parameters for the past N days.
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days - 1)

        logs = (
            MoodLog.objects.filter(user=user, logged_date__range=[start_date, end_date])
            .order_by("logged_date")
        )

        dates = []
        moods = []
        stress = []
        energy = []
        sleep = []
        satisfaction = []

        # Build complete map of date -> logs to handle missing dates cleanly
        log_map = {log.logged_date: log for log in logs}

        for i in range(days):
            current_date = start_date + timedelta(days=i)
            dates.append(current_date.strftime("%b %d"))

            log = log_map.get(current_date)
            if log:
                moods.append(log.mood_score)
                stress.append(log.stress_score)
                energy.append(log.energy_level)
                sleep.append(log.sleep_quality)
                satisfaction.append(log.study_satisfaction)
            else:
                # Nulls or zeros for missing days
                moods.append(None)
                stress.append(None)
                energy.append(None)
                sleep.append(None)
                satisfaction.append(None)

        return {
            "dates": dates,
            "moods": moods,
            "stress": stress,
            "energy": energy,
            "sleep": sleep,
            "satisfaction": satisfaction,
        }

    @classmethod
    def get_summary_metrics(cls, user: User) -> dict:
        """
        Calculates consistency, average scores, and evaluates current burnout risk.
        """
        today = timezone.now().date()
        past_30_days = today - timedelta(days=30)

        # Get logs of last 30 days
        logs_30 = MoodLog.objects.filter(user=user, logged_date__range=[past_30_days, today])
        total_logs = logs_30.count()

        # Consistency: percentage of days logged out of 30 days
        consistency_pct = int((total_logs / 30.0) * 100)

        # Averages
        avg_scores = logs_30.aggregate(
            avg_mood=Avg("mood_score"),
            avg_stress=Avg("stress_score"),
            avg_energy=Avg("energy_level"),
            avg_sleep=Avg("sleep_quality"),
            avg_satisfaction=Avg("study_satisfaction"),
        )

        # Clean averages
        mood_val = avg_scores["avg_mood"] or 0.0
        stress_val = avg_scores["avg_stress"] or 0.0
        energy_val = avg_scores["avg_energy"] or 0.0
        sleep_val = avg_scores["avg_sleep"] or 0.0
        satisfaction_val = avg_scores["avg_satisfaction"] or 0.0

        # Burnout risk rules:
        # High: stress is high (>3.5) and energy is low (<2.5) or sleep is low (<2.5)
        # Medium: stress is moderate (2.5 to 3.5)
        # Low: stress is low (<2.5)
        burnout_risk = "LOW"
        if total_logs > 0:
            if stress_val >= 3.8 and (energy_val <= 2.2 or sleep_val <= 2.2):
                burnout_risk = "HIGH"
            elif stress_val >= 2.8:
                burnout_risk = "MEDIUM"
        else:
            # Fallback if no logs: check recent AI analyses from journal entries
            recent_journals = JournalEntry.objects.filter(user=user).order_by("-created_at")[:3]
            analyses = AIAnalysis.objects.filter(journal_entry__in=recent_journals)
            high_count = sum(1 for a in analyses if a.burnout_risk == "HIGH")
            med_count = sum(1 for a in analyses if a.burnout_risk == "MEDIUM")
            if high_count >= 1:
                burnout_risk = "HIGH"
            elif med_count >= 1:
                burnout_risk = "MEDIUM"

        return {
            "consistency_percentage": consistency_pct,
            "avg_mood": round(mood_val, 1),
            "avg_stress": round(stress_val, 1),
            "avg_energy": round(energy_val, 1),
            "avg_sleep": round(sleep_val, 1),
            "avg_satisfaction": round(satisfaction_val, 1),
            "burnout_risk": burnout_risk,
        }
