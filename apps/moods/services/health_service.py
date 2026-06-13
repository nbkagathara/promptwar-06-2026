import random
from django.contrib.auth.models import User
from django.utils import timezone
from apps.moods.models import HealthDataLog, HealthIntegration
from apps.safety.models import AuditLog


class HealthService:
    @staticmethod
    def get_or_create_integration(user: User, platform: str) -> HealthIntegration:
        integration, created = HealthIntegration.objects.get_or_create(
            user=user,
            platform=platform,
            defaults={"is_connected": False}
        )
        return integration

    @staticmethod
    def save_consent_settings(user: User, platform: str, consent_data: dict) -> HealthIntegration:
        integration = HealthService.get_or_create_integration(user, platform)
        integration.allow_steps = consent_data.get("allow_steps", True)
        integration.allow_heart_rate = consent_data.get("allow_heart_rate", True)
        integration.allow_sleep = consent_data.get("allow_sleep", True)
        integration.allow_calories = consent_data.get("allow_calories", True)
        integration.allow_exercise = consent_data.get("allow_exercise", True)
        integration.allow_weight_bmi = consent_data.get("allow_weight_bmi", True)
        integration.allow_stress = consent_data.get("allow_stress", True)
        integration.save()
        AuditLog.objects.create(user=user, action=f"Updated privacy consent settings for {platform}")
        return integration

    @staticmethod
    def disconnect_platform(user: User, platform: str) -> None:
        HealthIntegration.objects.filter(user=user, platform=platform).update(
            is_connected=False,
            access_token=None,
            refresh_token=None,
            token_expires_at=None
        )
        AuditLog.objects.create(user=user, action=f"Disconnected health platform: {platform}")

    @staticmethod
    def delete_user_health_data(user: User) -> None:
        HealthDataLog.objects.filter(user=user).delete()
        HealthIntegration.objects.filter(user=user).update(
            is_connected=False,
            access_token=None,
            refresh_token=None,
            token_expires_at=None
        )
        AuditLog.objects.create(user=user, action="Deleted all synced health logs and reset integrations")

    @staticmethod
    def calculate_wellness_score(log: HealthDataLog) -> int:
        """
        Calculates a wellness score out of 100 based on health parameters.
        - Steps: 25 points max (target 8,000 steps)
        - Sleep hours & Quality: 25 points max (target 7.5+ hours and 75+ quality score)
        - Resting Heart Rate: 15 points max (target 60-75 bpm)
        - Active Minutes: 15 points max (target 30+ minutes)
        - Stress Level: 20 points max (lower stress = higher points)
        """
        score = 0
        
        # 1. Steps (up to 25 pts)
        step_pts = min(25, int((log.steps / 8000.0) * 25)) if log.steps else 0
        score += step_pts
        
        # 2. Sleep (up to 25 pts)
        sleep_ratio = min(1.0, log.sleep_hours / 7.5) if log.sleep_hours else 0.0
        quality_ratio = min(1.0, log.sleep_quality_score / 100.0) if log.sleep_quality_score else 0.0
        sleep_pts = int((sleep_ratio * 15) + (quality_ratio * 10))
        score += sleep_pts
        
        # 3. Resting HR (up to 15 pts)
        # Ideal: 60 - 75. Over 90 or under 45 is poor.
        hr = log.resting_heart_rate
        if hr:
            if 55 <= hr <= 75:
                score += 15
            elif 45 <= hr < 55 or 75 < hr <= 85:
                score += 10
            elif hr > 85 or hr < 45:
                score += 5
        else:
            score += 10
            
        # 4. Active Minutes (up to 15 pts)
        active_pts = min(15, int((log.active_minutes / 30.0) * 15)) if log.active_minutes else 0
        score += active_pts
        
        # 5. Stress Level (up to 20 pts)
        # Lower stress = higher points
        stress = log.stress_level_score
        if stress:
            stress_pts = max(0, int(((100 - stress) / 100.0) * 20))
            score += stress_pts
        else:
            score += 12
            
        return min(100, max(0, score))

    @staticmethod
    def sync_device_data(user: User, platform: str, profile_type: str = "active_healthy") -> HealthDataLog:
        """
        Simulates syncing from health platform, applying granular privacy filters.
        """
        integration = HealthService.get_or_create_integration(user, platform)
        integration.is_connected = True
        integration.connected_at = timezone.now()
        integration.save()
        
        # Determine values based on profile_type
        if profile_type == "active_healthy":
            steps = random.randint(8500, 14000)
            active_minutes = random.randint(35, 75)
            sleep_hours = round(random.uniform(7.2, 8.5), 1)
            sleep_quality_score = random.randint(80, 95)
            resting_hr = random.randint(58, 68)
            avg_hr = random.randint(70, 85)
            max_hr = random.randint(130, 160)
            calories = random.randint(2200, 2800)
            exercise_count = random.randint(1, 2)
            exercise_duration = random.randint(30, 60)
            weight = 72.5
            bmi = 22.1
            stress_score = random.randint(15, 35)
            mindfulness = random.randint(10, 20)
        elif profile_type == "stress_burnout":
            steps = random.randint(1500, 4500)
            active_minutes = random.randint(0, 10)
            sleep_hours = round(random.uniform(4.0, 5.8), 1)
            sleep_quality_score = random.randint(30, 55)
            resting_hr = random.randint(78, 88)
            avg_hr = random.randint(85, 95)
            max_hr = random.randint(110, 130)
            calories = random.randint(1600, 1900)
            exercise_count = 0
            exercise_duration = 0
            weight = 75.0
            bmi = 22.9
            stress_score = random.randint(75, 95)
            mindfulness = 0
        else:  # sedentary_restless
            steps = random.randint(4000, 7500)
            active_minutes = random.randint(10, 25)
            sleep_hours = round(random.uniform(6.0, 7.1), 1)
            sleep_quality_score = random.randint(55, 75)
            resting_hr = random.randint(68, 77)
            avg_hr = random.randint(75, 85)
            max_hr = random.randint(120, 140)
            calories = random.randint(1900, 2200)
            exercise_count = random.choice([0, 1])
            exercise_duration = 15 if exercise_count else 0
            weight = 73.0
            bmi = 22.3
            stress_score = random.randint(45, 70)
            mindfulness = random.choice([0, 5])

        # Apply user consent privacy filters
        final_steps = steps if integration.allow_steps else 0
        final_active = active_minutes if integration.allow_steps else 0
        final_sleep_hours = sleep_hours if integration.allow_sleep else 0.0
        final_sleep_quality = sleep_quality_score if integration.allow_sleep else 0
        final_resting_hr = resting_hr if integration.allow_heart_rate else 0
        final_avg_hr = avg_hr if integration.allow_heart_rate else 0
        final_max_hr = max_hr if integration.allow_heart_rate else 0
        final_calories = calories if integration.allow_calories else 0
        final_exercise_count = exercise_count if integration.allow_exercise else 0
        final_exercise_dur = exercise_duration if integration.allow_exercise else 0
        final_weight = weight if integration.allow_weight_bmi else 0.0
        final_bmi = bmi if integration.allow_weight_bmi else 0.0
        final_stress = stress_score if integration.allow_stress else 0
        final_mindfulness = mindfulness if integration.allow_stress else 0

        log, created = HealthDataLog.objects.update_or_create(
            user=user,
            logged_date=timezone.now().date(),
            defaults={
                "steps": final_steps,
                "active_minutes": final_active,
                "sleep_hours": final_sleep_hours,
                "sleep_quality_score": final_sleep_quality,
                "resting_heart_rate": final_resting_hr,
                "avg_heart_rate": final_avg_hr,
                "max_heart_rate": final_max_hr,
                "calories_burned": final_calories,
                "exercise_sessions_count": final_exercise_count,
                "exercise_duration_minutes": final_exercise_dur,
                "weight_kg": final_weight,
                "bmi": final_bmi,
                "stress_level_score": final_stress,
                "mindfulness_minutes": final_mindfulness,
                "source": platform,
            }
        )
        
        AuditLog.objects.create(
            user=user,
            action=f"Synced metrics from {platform} with profile '{profile_type}'"
        )
        return log
