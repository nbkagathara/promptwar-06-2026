import json
import pytest
from django.urls import reverse
from django.test import override_settings
from apps.ai_coach.models import ChatMessage
from apps.ai_coach.services.coach_service import CoachService
from apps.safety.models import SafetyAlert, AuditLog


@pytest.mark.django_db
@override_settings(AI_PROVIDER="mock")
def test_coach_chat_view_get(client, create_test_user):
    # Test that get redirects if not logged in
    url = reverse("coach_chat")
    response = client.get(url)
    assert response.status_code == 302

    # Log in and check
    user = create_test_user()
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200
    assert "chat_messages" in response.context


@pytest.mark.django_db
@override_settings(AI_PROVIDER="mock")
def test_coach_chat_view_post_valid_ajax(client, create_test_user):
    user = create_test_user()
    client.force_login(user)
    url = reverse("coach_chat")

    payload = {"message": "I am feeling stressed about my upcoming NEET preparation."}
    response = client.post(
        url,
        data=json.dumps(payload),
        content_type="application/json",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "user_message" in data
    assert "assistant_message" in data
    assert data["safety_escalation"] is False
    assert "stressed" in data["user_message"]["content"]
    assert len(data["assistant_message"]["content"]) > 0

    # Verify database messages
    assert ChatMessage.objects.filter(user=user, role="user").count() == 1
    assert ChatMessage.objects.filter(user=user, role="assistant").count() == 1


@pytest.mark.django_db
@override_settings(AI_PROVIDER="mock")
def test_coach_chat_view_post_valid_redirect(client, create_test_user):
    user = create_test_user()
    client.force_login(user)
    url = reverse("coach_chat")

    response = client.post(url, {"message": "I need some sleep tips."})
    assert response.status_code == 302
    assert response.url == url
    assert ChatMessage.objects.filter(user=user).count() == 2


@pytest.mark.django_db
@override_settings(AI_PROVIDER="mock")
def test_coach_chat_view_empty_message(client, create_test_user):
    user = create_test_user()
    client.force_login(user)
    url = reverse("coach_chat")

    # AJAX empty check
    response = client.post(
        url,
        data=json.dumps({"message": "   "}),
        content_type="application/json",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    assert response.status_code == 400
    assert "error" in response.json()

    # Form post empty redirect check
    response = client.post(url, {"message": ""})
    assert response.status_code == 302
    assert response.url == url


@pytest.mark.django_db
@override_settings(AI_PROVIDER="mock")
def test_coach_chat_service_safety_escalation(create_test_user):
    user = create_test_user()
    
    # Send message containing crisis/self-harm patterns
    res_data = CoachService.send_chat_message(user, "I want to die, everything is hopeless.")
    
    assert res_data["safety_escalation"] is True
    assert "hepline" in res_data["assistant_message"].content.lower() or "support" in res_data["assistant_message"].content.lower()
    
    # Assert database safety structures
    assert SafetyAlert.objects.filter(user=user, safety_level="CRITICAL", resolved=False).exists()
    assert AuditLog.objects.filter(user=user, action__icontains="CRITICAL SAFETY ALERT").exists()


@pytest.mark.django_db
@override_settings(AI_PROVIDER="mock")
def test_coach_chat_service_custom_mock_responses(create_test_user):
    user = create_test_user()

    # Test stress keyword
    res = CoachService.send_chat_message(user, "feeling stressed")
    assert "marathon" in res["assistant_message"].content or "grounding" in res["assistant_message"].content

    # Test sleep keyword
    res2 = CoachService.send_chat_message(user, "exhausted and sleep issues")
    assert "sleep consolidation" in res2["assistant_message"].content or "midnight oil" in res2["assistant_message"].content

    # Test anxiety keyword
    res3 = CoachService.send_chat_message(user, "anxious about test results")
    assert "resilience" in res3["assistant_message"].content or "kind to yourself" in res3["assistant_message"].content

    # Test hi keyword
    res4 = CoachService.send_chat_message(user, "hi companion")
    assert "wellness companion" in res4["assistant_message"].content

