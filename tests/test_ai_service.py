import pytest
from unittest.mock import patch, MagicMock
from django.test import override_settings
from services.ai_service import AIService


@override_settings(AI_PROVIDER="openai", OPENAI_API_KEY="dummy-key")
@patch("openai.OpenAI")
def test_openai_provider_journal(mock_openai_class):
    # Mocking OpenAI response format
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    
    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = '{"primary_emotion": "Excited", "stress_indicators": [], "burnout_risk": "LOW", "motivation_trends": [], "summary": "Excited Student"}'
    mock_completion.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_completion

    res = AIService.analyze_journal("Test content")
    assert res["primary_emotion"] == "Excited"


@override_settings(AI_PROVIDER="gemini", GEMINI_API_KEY="dummy-key")
@patch("google.generativeai.GenerativeModel")
def test_gemini_provider_journal(mock_gemini_model):
    mock_model = MagicMock()
    mock_gemini_model.return_value = mock_model
    
    mock_response = MagicMock()
    mock_response.text = '{"primary_emotion": "Focused", "stress_indicators": [], "burnout_risk": "LOW", "motivation_trends": [], "summary": "Focused Student"}'
    mock_model.generate_content.return_value = mock_response

    res = AIService.analyze_journal("Test content")
    assert res["primary_emotion"] == "Focused"


@override_settings(AI_PROVIDER="azure", AZURE_OPENAI_API_KEY="dummy-key", AZURE_OPENAI_ENDPOINT="https://dummy.openai.azure.com")
@patch("requests.post")
def test_azure_provider_journal(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": '{"primary_emotion": "Calm", "stress_indicators": [], "burnout_risk": "LOW", "motivation_trends": [], "summary": "Calm Student"}'
                }
            }
        ]
    }
    mock_post.return_value = mock_response

    res = AIService.analyze_journal("Test content")
    assert res["primary_emotion"] == "Calm"


@override_settings(AI_PROVIDER="openai", OPENAI_API_KEY="dummy-key")
@patch("openai.OpenAI")
def test_openai_provider_coach(mock_openai_class):
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    
    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = '{"recommendations": [{"type": "MINDFULNESS", "content": "Breathe deep"}]}'
    mock_completion.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_completion

    res = AIService.generate_coach_guidance({}, [], [])
    assert len(res["recommendations"]) == 1
    assert res["recommendations"][0]["content"] == "Breathe deep"
