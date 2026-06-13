# Security Architecture: AuraWell

AuraWell integrates security across the data, logic, and networking layers.

## 1. OWASP Top 10 Protection

* **SQL Injection**: Prevented by using the Django Object-Relational Mapper (ORM), which uses parameterized queries. Raw SQL is strictly forbidden.
* **Cross-Site Scripting (XSS)**: Django Templates autoescape HTML characters by default. Rich inputs (like journal text) are rendered without raw HTML styling unless explicitly sanitized.
* **Cross-Site Request Forgery (CSRF)**: CSRF tokens are injected and verified on all POST forms.
* **Clickjacking**: Protected via `django.middleware.clickjacking.XFrameOptionsMiddleware` which sets `X-Frame-Options: DENY`.

## 2. Session Security (Production Settings)

In production Settings:
* `SESSION_COOKIE_SECURE = True`
* `CSRF_COOKIE_SECURE = True`
* `SESSION_COOKIE_HTTPONLY = True`

## 3. Safety Scanning (Crisis Protections)

* **Keyword Filtering**: Regex keyword list checks for self-harm and crisis indicators.
* **AI Bypass**: Whenever critical indicators match, AI analysis is skipped, rendering local safe resources instead to prevent dangerous AI hallucinations.
* **Audit Trails**: Security audits are stored in `AuditLog` for sign-ins, logouts, profile target updates, and safety alerts.
