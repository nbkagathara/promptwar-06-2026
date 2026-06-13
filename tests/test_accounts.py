import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from apps.accounts.models import ExamType, Profile
from apps.accounts.services.account_service import AccountService
from apps.safety.models import AuditLog


@pytest.mark.django_db
def test_account_registration_service():
    user = User.objects.create_user(username="newstudent", email="new@test.com", password="SecurePassword123")
    exam = ExamType.objects.create(name="TEST_NEET", description="Medical entrance")
    
    profile = AccountService.create_user_profile(user, exam.id)
    assert profile.user == user
    assert profile.exam_type == exam
    
    # Audit log check
    assert AuditLog.objects.filter(user=user, action__icontains="profile").exists()


@pytest.mark.django_db
def test_update_profile_service():
    user = User.objects.create_user(username="newstudent2", email="new2@test.com", password="SecurePassword123")
    exam1 = ExamType.objects.create(name="TEST_JEE_2", description="Engineering")
    exam2 = ExamType.objects.create(name="TEST_UPSC", description="Civil services")
    
    profile = AccountService.create_user_profile(user, exam1.id)
    assert profile.exam_type == exam1

    updated_profile = AccountService.update_profile(user, exam2.id)
    assert updated_profile.exam_type == exam2


@pytest.mark.django_db
def test_login_view(client):
    user = User.objects.create_user(username="testuser", email="test@test.com", password="SecurePassword123")
    url = reverse("login")
    response = client.post(url, {"username": "testuser", "password": "SecurePassword123"})
    assert response.status_code == 302
    assert response.url == reverse("dashboard")
