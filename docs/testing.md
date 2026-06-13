# Testing Strategy: AuraWell

AuraWell implements automated pytest validations covering models, views, forms, and services.

## Coverage Report
Our automated test suite maintains **91% code coverage**.

### Run Tests Locally
To execute tests and print the detailed coverage report:
```bash
.venv/bin/pytest
```

## Test Structure (`/tests/`)
* `conftest.py`: Holds database and user mock fixtures.
* `test_services.py`: Validates the Safety engine and fallback mocks.
* `test_accounts.py`: Exercises user registration services and login redirections.
* `test_moods.py`: Asserts daily logging metrics and uniqueness boundaries.
* `test_journals.py`: Asserts crisis detection safety rules and bypass actions.
* `test_views.py`: Exercises CBV render responses, redirect pipelines, and client form postings.
* `test_ai_service.py`: Leverages unit mocks to assert OpenAI, Gemini, and Azure OpenAI API clients.
