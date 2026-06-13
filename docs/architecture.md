# Architecture Design: AuraWell

AuraWell is built using a clean separation of concerns leveraging Django's Model-View-Template (MVT) pattern combined with a mandatory Service Layer.

## Component Overview

```text
               +-----------------------+
               |   Django Templates    | <--- Rendered on Server
               +-----------------------+
                           |
                           v
               +-----------------------+
               |     Django Views      | <--- Class-Based Views (CBVs)
               +-----------------------+
                           |
                           v
               +-----------------------+
               |     Service Layer     | <--- Business Logic (<app>/services/)
               +-----------------------+
                /         |           \
               /          |            \
              v           v             v
      +------------+  +-----------+  +---------------+
      | Data Model |  | AI Engine |  | Safety Engine |
      +------------+  +-----------+  +---------------+
```

## Modular Structure

Each custom feature is encapsulated in a dedicated Django app:
* **`apps/accounts`**: Custom registration and target exam configurations.
* **`apps/moods`**: Daily mood parameters logging (energy, sleep, satisfaction).
* **`apps/journals`**: Secure student reflections storage and emotional triggers.
* **`apps/ai_coach`**: Empathic coach guidelines retrieval.
* **`apps/analytics`**: Trend aggregations and burnout warning logic.
* **`apps/notifications`**: Email/database reminder generation.
* **`apps/safety`**: Crisis database logging and security logs.

## AI Service Abstraction Layer

All AI calls go through `services/ai_service.py` which abstracts the third-party providers (OpenAI, Gemini, Azure OpenAI). If API keys are missing, the system gracefully falls back to a deterministic Mock provider to prevent crashes and facilitate offline testing.

## Safety Engine

The safety engine `services/safety_engine.py` runs standard regex keyword searches. If a student shows crisis markers, the AI analysis pipeline is bypassed, generating a `SafetyAlert` and redirecting the user to emergency crisis numbers.
