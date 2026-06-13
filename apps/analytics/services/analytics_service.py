from datetime import timedelta
from django.contrib.auth.models import User
from django.db.models import Avg
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

    @staticmethod
    def get_health_trends(user: User, days: int = 7) -> dict:
        """
        Retrieves health parameters (steps, heart rate, sleep hours, active minutes) for the past N days.
        """
        from apps.moods.models import HealthDataLog
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days - 1)

        logs = (
            HealthDataLog.objects.filter(user=user, logged_date__range=[start_date, end_date])
            .order_by("logged_date")
        )

        dates = []
        steps = []
        sleep_hours = []
        sleep_quality = []
        heart_rate = []
        active_minutes = []

        log_map = {log.logged_date: log for log in logs}

        for i in range(days):
            current_date = start_date + timedelta(days=i)
            dates.append(current_date.strftime("%b %d"))

            log = log_map.get(current_date)
            if log:
                steps.append(log.steps)
                sleep_hours.append(log.sleep_hours)
                sleep_quality.append(log.sleep_quality_score)
                heart_rate.append(log.resting_heart_rate)
                active_minutes.append(log.active_minutes)
            else:
                steps.append(None)
                sleep_hours.append(None)
                sleep_quality.append(None)
                heart_rate.append(None)
                active_minutes.append(None)

        return {
            "dates": dates,
            "steps": steps,
            "sleep_hours": sleep_hours,
            "sleep_quality": sleep_quality,
            "heart_rate": heart_rate,
            "active_minutes": active_minutes,
        }

    @classmethod
    def get_wellness_summary(cls, user: User) -> dict:
        """
        Retrieves a summary of wellness trends, detects warnings, and calculates an overall wellness score.
        """
        from apps.moods.models import HealthDataLog
        from apps.moods.services.health_service import HealthService

        today = timezone.now().date()
        past_7_days = today - timedelta(days=7)

        logs_7 = HealthDataLog.objects.filter(user=user, logged_date__range=[past_7_days, today])
        count = logs_7.count()

        avg_steps = logs_7.aggregate(avg=Avg("steps"))["avg"] or 0
        avg_sleep = logs_7.aggregate(avg=Avg("sleep_hours"))["avg"] or 0.0
        avg_hr = logs_7.aggregate(avg=Avg("resting_heart_rate"))["avg"] or 70
        avg_active = logs_7.aggregate(avg=Avg("active_minutes"))["avg"] or 0

        # Calculate recent wellness score from the latest log
        latest_log = HealthDataLog.objects.filter(user=user).order_by("-logged_date").first()
        wellness_score = HealthService.calculate_wellness_score(latest_log) if latest_log else 0

        # Warnings detection
        warnings = []
        if count > 0:
            if avg_sleep < 6.0:
                warnings.append({
                    "title": "Sleep Deprivation Risk",
                    "text": "Your average sleep over the last week is under 6 hours. Consider resting more to maintain memory retention.",
                    "level": "danger"
                })
            if avg_steps < 4000:
                warnings.append({
                    "title": "Highly Sedentary Pattern",
                    "text": "Average steps are below 4,000. Take short 10-minute active walking breaks during study sessions.",
                    "level": "warning"
                })
            if avg_hr > 82:
                warnings.append({
                    "title": "Elevated Resting Heart Rate",
                    "text": "Your resting heart rate is higher than average, potentially indicating stress. Try breathing exercises.",
                    "level": "warning"
                })
        else:
            warnings.append({
                "title": "No Data Synced",
                "text": "Connect your wearable or trigger a sync to generate wellness insights.",
                "level": "info"
            })

        return {
            "wellness_score": wellness_score,
            "avg_steps": round(avg_steps),
            "avg_sleep": round(avg_sleep, 1),
            "avg_hr": round(avg_hr),
            "avg_active": round(avg_active),
            "warnings": warnings,
        }

    @classmethod
    def get_cohort_analytics(cls) -> dict:
        """
        Computes aggregate and anonymized wellness metrics for all students.
        """
        from apps.moods.models import HealthDataLog
        from apps.moods.services.health_service import HealthService

        today = timezone.now().date()
        past_30_days = today - timedelta(days=30)

        logs = HealthDataLog.objects.filter(logged_date__range=[past_30_days, today])

        total_students_tracked = User.objects.filter(health_logs__isnull=False).distinct().count()
        avg_steps = logs.aggregate(avg=Avg("steps"))["avg"] or 0
        avg_sleep = logs.aggregate(avg=Avg("sleep_hours"))["avg"] or 0.0
        avg_hr = logs.aggregate(avg=Avg("resting_heart_rate"))["avg"] or 70

        # Compute cohort wellness score average
        all_latest_logs = []
        users_with_logs = User.objects.filter(health_logs__isnull=False).distinct()
        for u in users_with_logs:
            latest_log = HealthDataLog.objects.filter(user=u).order_by("-logged_date").first()
            if latest_log:
                all_latest_logs.append(HealthService.calculate_wellness_score(latest_log))

        cohort_wellness_score = int(sum(all_latest_logs) / len(all_latest_logs)) if all_latest_logs else 0

        # Simple participation tracking
        total_users = User.objects.count()
        participation_rate = int((total_students_tracked / total_users) * 100) if total_users else 0

        # Build distribution
        distribution = {
            "excellent": sum(1 for s in all_latest_logs if s >= 80),
            "good": sum(1 for s in all_latest_logs if 60 <= s < 80),
            "fair": sum(1 for s in all_latest_logs if 40 <= s < 60),
            "risk": sum(1 for s in all_latest_logs if s < 40),
        }

        return {
            "total_students_tracked": total_students_tracked,
            "avg_steps": round(avg_steps),
            "avg_sleep": round(avg_sleep, 1),
            "avg_hr": round(avg_hr),
            "cohort_wellness_score": cohort_wellness_score,
            "participation_rate": participation_rate,
            "distribution": distribution,
        }

    @classmethod
    def get_detailed_health_metrics(cls, user: User) -> dict:
        """
        Retrieves the latest health metrics values and connection status of platforms.
        """
        from apps.moods.models import HealthDataLog, HealthIntegration

        latest_log = HealthDataLog.objects.filter(user=user).order_by("-logged_date").first()

        # Get connection status for platforms
        platforms = ["google_fit", "apple_health", "fitbit", "smart_band"]
        integrations = {
            p: HealthIntegration.objects.filter(user=user, platform=p, is_connected=True).exists()
            for p in platforms
        }

        return {
            "latest_log": latest_log,
            "integrations": integrations,
            "any_connected": any(integrations.values())
        }
