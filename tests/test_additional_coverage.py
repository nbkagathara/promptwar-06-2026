import datetime
import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import ExamType, Profile
from apps.accounts.services.account_service import AccountService
from apps.ai_coach.models import AIRecommendation
from apps.ai_coach.services.coach_service import CoachService
from apps.analytics.services.analytics_service import AnalyticsService
from apps.journals.models import JournalEntry, AIAnalysis
from apps.journals.services.journal_service import JournalService
from apps.moods.models import MoodLog, HealthDataLog, HealthIntegration
from apps.moods.services.health_service import HealthService
from apps.notifications.models import Notification
from apps.safety.models import SafetyAlert, AuditLog
from apps.safety.services.safety_service import SafetyService
from services.ai_service import AIService


@pytest.mark.django_db
def test_models_str_methods(create_test_user):
    user = create_test_user()
    
    exam = ExamType.objects.create(name="TEST_EXAM", description="Description")
    assert str(exam) == "TEST_EXAM"
    
    profile = Profile.objects.get(user=user)
    assert str(profile) == f"{user.username}'s Profile"
    
    mood_log = MoodLog.objects.create(
        user=user,
        mood_score=4,
        stress_score=2,
        energy_level=3,
        sleep_quality=3,
        study_satisfaction=4,
        logged_date=datetime.date.today(),
    )
    assert str(mood_log) == f"{user.username}'s mood on {datetime.date.today()}"
    
    health_log = HealthDataLog.objects.create(
        user=user,
        logged_date=datetime.date.today(),
        source="Apple Health",
    )
    assert str(health_log) == f"{user.username}'s health logs on {datetime.date.today()} (Apple Health)"
    
    integration = HealthIntegration.objects.create(
        user=user,
        platform="google_fit",
    )
    assert str(integration) == f"{user.username}'s google_fit Integration"
    
    rec = AIRecommendation.objects.create(
        user=user,
        rec_type="MINDFULNESS",
        content="Test recommendation content",
    )
    assert str(rec) == "Mindfulness Exercise for student"
    
    notification = Notification.objects.create(
        user=user,
        message="Test message",
        send_at=timezone.now(),
        is_sent=True,
    )
    assert str(notification) == f"Notification for {user.username} - Sent: True"
    
    journal = JournalEntry.objects.create(user=user, content="Test content")
    
    alert = SafetyAlert.objects.create(
        user=user,
        journal_entry=journal,
        safety_level="CRITICAL",
        detected_terms="suicide",
    )
    assert "CRITICAL Alert for student" in str(alert)
    
    audit = AuditLog.objects.create(
        user=user,
        action="Logged in",
    )
    assert f"Logged in by {user.username}" in str(audit)


@pytest.mark.django_db
def test_account_service_exceptions():
    user = User.objects.create_user(username="noprofile", email="no@profile.com", password="Password123")
    
    # 1. Invalid exam type in create_user_profile should fall back
    profile = AccountService.create_user_profile(user, exam_type_id=99999)
    assert profile.exam_type is None
    
    # 2. Invalid exam type in update_profile should raise ValueError
    with pytest.raises(ValueError, match="Invalid Exam Type"):
        AccountService.update_profile(user, exam_type_id=99999)



@pytest.mark.django_db
def test_safety_service_exceptions(create_test_user):
    user = create_test_user()
    with pytest.raises(ValueError, match="Alert not found"):
        SafetyService.resolve_alert(user, alert_id=99999)


@pytest.mark.django_db
def test_analytics_service_edge_cases(create_test_user):
    user = create_test_user()
    
    # 1. Test trends with missing logs (should return list of None values)
    trends = AnalyticsService.get_mood_trends(user, days=7)
    assert len(trends["dates"]) == 7
    assert all(x is None for x in trends["moods"])
    
    # 2. Test summary metrics burnout calculation: Stress is high, Energy/Sleep is low
    today = timezone.now().date()
    for i in range(5):
        MoodLog.objects.create(
            user=user,
            mood_score=2,
            stress_score=4,  # high stress
            energy_level=2,  # low energy
            sleep_quality=2,  # low sleep
            study_satisfaction=2,
            logged_date=today - datetime.timedelta(days=i),
        )
    
    metrics = AnalyticsService.get_summary_metrics(user)
    assert metrics["burnout_risk"] == "HIGH"
    
    # Clean up logs
    MoodLog.objects.all().delete()
    
    # 3. Stress moderate triggers MEDIUM risk
    for i in range(5):
        MoodLog.objects.create(
            user=user,
            mood_score=3,
            stress_score=3,  # moderate
            energy_level=3,
            sleep_quality=3,
            study_satisfaction=3,
            logged_date=today - datetime.timedelta(days=i),
        )
    metrics = AnalyticsService.get_summary_metrics(user)
    assert metrics["burnout_risk"] == "MEDIUM"
    
    # Clean up logs
    MoodLog.objects.all().delete()
    
    # 4. Fallback if no logs: check recent AI analyses from journal entries
    journal = JournalEntry.objects.create(user=user, content="Sad thoughts")
    AIAnalysis.objects.create(
        journal_entry=journal,
        primary_emotion="Anxiety",
        stress_indicators=["exams"],
        burnout_risk="HIGH",
        motivation_trends=["low"],
        summary="summary"
    )
    metrics = AnalyticsService.get_summary_metrics(user)
    assert metrics["burnout_risk"] == "HIGH"
    
    # Change risk to MEDIUM
    AIAnalysis.objects.all().update(burnout_risk="MEDIUM")
    metrics = AnalyticsService.get_summary_metrics(user)
    assert metrics["burnout_risk"] == "MEDIUM"


@pytest.mark.django_db
def test_analytics_service_wellness_warnings(create_test_user):
    user = create_test_user()
    
    # 1. sleep warning (<6.0)
    HealthDataLog.objects.create(
        user=user,
        logged_date=timezone.now().date(),
        sleep_hours=5.0,
        steps=5000,
        resting_heart_rate=70,
    )
    summary = AnalyticsService.get_wellness_summary(user)
    assert any("Sleep Deprivation" in w["title"] for w in summary["warnings"])
    
    HealthDataLog.objects.all().delete()
    
    # 2. sedentary warning (<4000)
    HealthDataLog.objects.create(
        user=user,
        logged_date=timezone.now().date(),
        sleep_hours=8.0,
        steps=3000,
        resting_heart_rate=70,
    )
    summary = AnalyticsService.get_wellness_summary(user)
    assert any("Highly Sedentary" in w["title"] for w in summary["warnings"])
    
    HealthDataLog.objects.all().delete()
    
    # 3. heart rate warning (>82)
    HealthDataLog.objects.create(
        user=user,
        logged_date=timezone.now().date(),
        sleep_hours=8.0,
        steps=8000,
        resting_heart_rate=85,
    )
    summary = AnalyticsService.get_wellness_summary(user)
    assert any("Elevated Resting Heart Rate" in w["title"] for w in summary["warnings"])


@pytest.mark.django_db
def test_send_reminders_command(create_test_user):
    user = create_test_user()
    
    # Both missing
    call_command("send_reminders")
    assert Notification.objects.filter(user=user, message__icontains="haven't logged your mood or journal").exists()
    
    Notification.objects.all().delete()
    
    # Mood logged but no journal
    MoodLog.objects.create(
        user=user,
        mood_score=4,
        stress_score=2,
        energy_level=3,
        sleep_quality=3,
        study_satisfaction=4,
        logged_date=timezone.now().date(),
    )
    call_command("send_reminders")
    assert Notification.objects.filter(user=user, message__icontains="logged your mood but haven't written").exists()
    
    Notification.objects.all().delete()
    MoodLog.objects.all().delete()
    
    # Journal logged but no mood
    JournalEntry.objects.create(user=user, content="Confident study day")
    call_command("send_reminders")
    assert Notification.objects.filter(user=user, message__icontains="Remember to record your daily mood").exists()


@pytest.mark.django_db
def test_views_additional(client, create_test_user):
    user = create_test_user()
    client.force_login(user)
    
    # 1. Logout View
    response = client.post(reverse("logout"))
    assert response.status_code == 302
    
    client.force_login(user)
    
    # 2. OAuth callback simulator view
    response = client.get(reverse("health_oauth_callback") + "?platform=apple_health")
    assert response.status_code == 302
    assert HealthIntegration.objects.filter(user=user, platform="apple_health", is_connected=True).exists()
    
    # 3. Delete health data view post
    response = client.post(reverse("delete_health_data"))
    assert response.status_code == 302
    assert HealthDataLog.objects.filter(user=user).count() == 0
    assert HealthIntegration.objects.get(user=user, platform="apple_health").is_connected is False
    
    # 4. Sync health data view under different sandbox profiles
    response = client.post(reverse("sync_health"), {"source": "Apple Health", "profile_type": "stress_burnout"})
    assert response.status_code == 302
    
    response = client.post(reverse("sync_health"), {"source": "Apple Health", "profile_type": "sedentary_restless"})
    assert response.status_code == 302


@pytest.mark.django_db
def test_cohort_analytics_calculation(create_test_user):
    user1 = create_test_user(username="u1", email="u1@test.com")
    user2 = create_test_user(username="u2", email="u2@test.com")
    
    HealthDataLog.objects.create(
        user=user1,
        logged_date=timezone.now().date(),
        steps=8000,
        sleep_hours=7.5,
        resting_heart_rate=65,
    )
    HealthDataLog.objects.create(
        user=user2,
        logged_date=timezone.now().date(),
        steps=4000,
        sleep_hours=6.0,
        resting_heart_rate=75,
    )
    
    cohort = AnalyticsService.get_cohort_analytics()
    assert cohort["total_students_tracked"] == 2
    assert cohort["avg_steps"] == 6000
    assert cohort["avg_sleep"] == 6.8
