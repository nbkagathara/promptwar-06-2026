import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from apps.journals.models import JournalEntry, AIAnalysis
from apps.journals.services.journal_service import JournalService
from apps.safety.models import SafetyAlert, AuditLog


@pytest.mark.django_db
def test_create_and_analyze_journal_safe(create_test_user):
    user = create_test_user()
    
    entry, safety_level, alert = JournalService.create_and_analyze_journal(
        user, "I feel great today. Did some good math revision and feel confident."
    )

    assert entry.user == user
    assert safety_level == "SAFE"
    assert alert is None
    
    # Check that AI Analysis has been populated
    assert AIAnalysis.objects.filter(journal_entry=entry).exists()
    analysis = entry.analysis
    assert analysis.burnout_risk == "LOW"


@pytest.mark.django_db
def test_create_and_analyze_journal_critical(create_test_user):
    user = create_test_user()

    entry, safety_level, alert = JournalService.create_and_analyze_journal(
        user, "I feel hopeless and just want to end my life. Exam is too much."
    )

    assert safety_level == "CRITICAL"
    assert alert is not None
    assert alert.safety_level == "CRITICAL"
    
    # Verify AI analysis was bypassed
    assert not AIAnalysis.objects.filter(journal_entry=entry).exists()

    # Check audit log was created
    assert AuditLog.objects.filter(
        user=user, action__icontains="CRITICAL SAFETY ALERT"
    ).exists()


@pytest.mark.django_db
def test_write_journal_view_crisis_redirect(client, create_test_user):
    user = create_test_user()
    client.force_login(user)

    url = reverse("write_journal")
    # Post containing crisis words
    response = client.post(url, {"content": "I want to commit suicide."})
    
    # Must redirect to the crisis support view
    assert response.status_code == 302
    assert response.url == reverse("crisis_support")
