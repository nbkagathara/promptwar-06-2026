# Service Interfaces: AuraWell

AuraWell uses standard clean services in `/services/` and `<app>/services/`.

## 1. `AIService` (`services/ai_service.py`)

### `analyze_journal(content: str) -> dict`
* **Input**: User journal string.
* **Output**:
  ```json
  {
    "primary_emotion": "Anxiety",
    "stress_indicators": ["Test anxiety", "Fatigue"],
    "burnout_risk": "MEDIUM",
    "motivation_trends": ["Steady"],
    "summary": "The student feels overwhelmed by chemistry mock tests."
  }
  ```

### `generate_coach_guidance(profile: dict, mood: list, journals: list) -> dict`
* **Output**:
  ```json
  {
    "recommendations": [
      { "type": "MINDFULNESS", "content": "4-7-8 Breathing Technique..." },
      { "type": "STUDY_BREAK", "content": "50/10 active rest breaks..." },
      { "type": "MOTIVATION", "content": "Keep going!..." },
      { "type": "TIME_MGMT", "content": "Eisenhower Matrix priority..." }
    ]
  }
  ```

---

## 2. `SafetyEngine` (`services/safety_engine.py`)

### `analyze_safety(text: str) -> dict`
* **Output**:
  ```json
  {
    "safety_level": "CRITICAL" | "WARNING" | "SAFE",
    "detected_terms": ["suicide"]
  }
  ```
