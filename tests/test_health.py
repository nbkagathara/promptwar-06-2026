import datetime
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from apps.moods.models import HealthDataLog, HealthIntegration
from apps.moods.services.health_service import HealthService


@pytest.mark.django_db
def test_wellness_score_calculation():
    # Setup test logs
    log = HealthDataLog(
        steps=8000,              # 25 pts
        sleep_hours=7.5,         # 15 pts
        sleep_quality_score=80,  # 8 pts
        resting_heart_rate=65,   # 15 pts
        active_minutes=30,       # 15 pts
        stress_level_score=20,   # 16 pts
    )
    score = HealthService.calculate_wellness_score(log)
    assert score >= 80


@pytest.mark.django_db
def test_privacy_granular_filters(create_test_user):
    user = create_test_user()
    
    # Enable only steps and sleep, disable heart rate
    integration = HealthService.get_or_create_integration(user, "Fitbit")
    consent_data = {
        "allow_steps": True,
        "allow_sleep": True,
        "allow_heart_rate": False,
        "allow_calories": False,
        "allow_exercise": False,
        "allow_weight_bmi": False,
        "allow_stress": False,
    }
    HealthService.save_consent_settings(user, "Fitbit", consent_data)
    
    # Sync Fitbit
    log = HealthService.sync_device_data(user, "Fitbit", profile_type="active_healthy")
    
    # Assert allowed data is saved
    assert log.steps > 0
    assert log.sleep_hours > 0
    
    # Assert disabled data is blanked/zeroed
    assert log.resting_heart_rate == 0
    assert log.calories_burned == 0


@pytest.mark.django_db
def test_delete_user_health_data(create_test_user):
    user = create_test_user()
    
    # Sync first
    HealthService.sync_device_data(user, "Apple Health", profile_type="active_healthy")
    assert HealthDataLog.objects.filter(user=user).count() == 1
    
    # Purge
    HealthService.delete_user_health_data(user)
    assert HealthDataLog.objects.filter(user=user).count() == 0


@pytest.mark.django_db
def test_health_integrations_views(client, create_test_user):
    user = create_test_user()
    client.force_login(user)
    
    # GET settings page
    url = reverse("health_integrations")
    response = client.get(url)
    assert response.status_code == 200
    
    # POST update settings
    response = client.post(url, {
        "platform": "google_fit",
        "allow_steps": "on",
        "allow_sleep": "on",
    })
    assert response.status_code == 302
    
    integration = HealthIntegration.objects.get(user=user, platform="google_fit")
    assert integration.allow_steps is True
    assert integration.allow_heart_rate is False  # Omitted on POST, defaults to False
