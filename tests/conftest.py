import os
import pytest
from django.contrib.auth.models import User
from apps.accounts.models import ExamType, Profile

# Set up django settings module for tests
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


def pytest_configure():
    from django.conf import settings
    # Use standard storage in tests to avoid needing run collectstatic
    settings.STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"



@pytest.fixture
def db_setup(db):
    """Ensure database access for tests."""
    return db


@pytest.fixture
def create_test_user(db):
    def make_user(username="student", email="student@test.com", password="SecurePassword123"):
        user = User.objects.create_user(username=username, email=email, password=password)
        exam_type, _ = ExamType.objects.get_or_create(name="TEST_JEE", defaults={"description": "JEE exam"})
        Profile.objects.create(user=user, exam_type=exam_type)
        return user

    return make_user
