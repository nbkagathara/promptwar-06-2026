import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from apps.accounts.models import ExamType, Profile
from apps.ai_coach.models import AIRecommendation
from apps.safety.models import SafetyAlert, AuditLog
from apps.safety.services.safety_service import SafetyService


@pytest.mark.django_db
def test_register_view(client):
    exam = ExamType.objects.create(name="TEST_GATE", description="GATE Exam")
    url = reverse("register")
    
    # 1. Test get registration page
    response = client.get(url)
    assert response.status_code == 200

    # 2. Submit valid registration
    response = client.post(
        url,
        {
            "username": "regstudent",
            "email": "reg@test.com",
            "exam_type": exam.id,
            "password": "SecurePassword123",
            "password_confirm": "SecurePassword123",
        },
    )
    assert response.status_code == 302
    assert response.url == reverse("dashboard")
    assert User.objects.filter(username="regstudent").exists()
    assert Profile.objects.filter(user__username="regstudent", exam_type=exam).exists()


@pytest.mark.django_db
def test_profile_view_update(client, create_test_user):
    user = create_test_user()
    client.force_login(user)
    exam = ExamType.objects.create(name="TEST_SSC", description="SSC Exam")

    url = reverse("profile")
    
    # Get profile settings page
    response = client.get(url)
    assert response.status_code == 200

    # Post update
    response = client.post(url, {"exam_type": exam.id})
    assert response.status_code == 302
    user.profile.refresh_from_db()
    assert user.profile.exam_type == exam


@pytest.mark.django_db
def test_dashboard_view_content(client, create_test_user):
    user = create_test_user()
    client.force_login(user)

    url = reverse("dashboard")
    response = client.get(url)
    assert response.status_code == 200
    assert "analytics" in response.context
    assert "recommendations" in response.context


@pytest.mark.django_db
def test_coach_guidance_regenerate(client, create_test_user):
    user = create_test_user()
    client.force_login(user)

    url = reverse("coach_guidance")
    
    # 1. Get recommendations page
    response = client.get(url)
    assert response.status_code == 200

    # 2. Post to trigger regeneration
    response = client.post(url)
    assert response.status_code == 302
    assert AIRecommendation.objects.filter(user=user).count() == 4


@pytest.mark.django_db
def test_analytics_dashboard_view(client, create_test_user):
    user = create_test_user()
    client.force_login(user)

    url = reverse("analytics_dashboard")
    response = client.get(url + "?days=14")
    assert response.status_code == 200
    assert response.context["days"] == 14
    assert "trends_json" in response.context


@pytest.mark.django_db
def test_safety_service_resolution(create_test_user):
    user = create_test_user()
    alert = SafetyAlert.objects.create(
        user=user,
        safety_level="CRITICAL",
        detected_terms="suicide",
        resolved=False,
    )

    resolved_alert = SafetyService.resolve_alert(user, alert.id)
    assert resolved_alert.resolved is True
    
    # Audit log check
    assert AuditLog.objects.filter(user=user, action__icontains="Resolved safety alert").exists()
