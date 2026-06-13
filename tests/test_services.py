import pytest
from services.safety_engine import SafetyEngine
from services.ai_service import AIService


def test_safety_engine_safe_text():
    res = SafetyEngine.analyze_safety("I studied chemistry today for 4 hours and feel prepared.")
    assert res["safety_level"] == "SAFE"
    assert len(res["detected_terms"]) == 0


def test_safety_engine_warning_text():
    res = SafetyEngine.analyze_safety("I am feeling a lot of burnout preparing for this JEE exam.")
    assert res["safety_level"] == "WARNING"
    assert "burnout" in res["detected_terms"]


def test_safety_engine_critical_text():
    res = SafetyEngine.analyze_safety("I feel completely hopeless and want to end my life.")
    assert res["safety_level"] == "CRITICAL"
    assert "end my life" in res["detected_terms"] or "hopeless" in res["detected_terms"]


def test_ai_service_journal_analysis():
    # Test standard journal content analysis mapping
    res = AIService.analyze_journal("I feel very tired and exhausted today.")
    assert "primary_emotion" in res
    assert "stress_indicators" in res
    assert "burnout_risk" in res
    assert "summary" in res
    assert res["burnout_risk"] in ["LOW", "MEDIUM", "HIGH"]


def test_ai_service_coach_guidance():
    # Test coach recommendations generation
    profile_info = {"exam_name": "NEET"}
    mood_history = [3, 4, 2]
    recent_journals = ["Reviewed biology cells", "Too much work"]

    res = AIService.generate_coach_guidance(profile_info, mood_history, recent_journals)
    assert "recommendations" in res
    assert len(res["recommendations"]) == 4
    for rec in res["recommendations"]:
        assert "type" in rec
        assert "content" in rec
