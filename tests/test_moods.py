import datetime
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from apps.moods.models import MoodLog
from apps.moods.services.mood_service import MoodService


@pytest.mark.django_db
def test_log_mood_service(create_test_user):
    user = create_test_user()
    
    # Log today's parameters
    log = MoodService.log_daily_mood(
        user=user,
        mood_score=4,
        stress_score=2,
        energy_level=3,
        sleep_quality=4,
        study_satisfaction=5,
    )

    assert log.mood_score == 4
    assert log.stress_score == 2
    assert log.logged_date == datetime.date.today()

    # Update parameters for the same day
    updated_log = MoodService.log_daily_mood(
        user=user,
        mood_score=5,
        stress_score=1,
        energy_level=4,
        sleep_quality=5,
        study_satisfaction=5,
    )
    
    assert updated_log.id == log.id
    assert updated_log.mood_score == 5
    assert updated_log.stress_score == 1


@pytest.mark.django_db
def test_log_mood_view(client, create_test_user):
    user = create_test_user()
    client.force_login(user)

    url = reverse("log_mood")
    response = client.post(
        url,
        {
            "mood_score": 4,
            "stress_score": 2,
            "energy_level": 3,
            "sleep_quality": 4,
            "study_satisfaction": 4,
        },
    )
    assert response.status_code == 302
    assert MoodLog.objects.filter(user=user, mood_score=4).exists()
