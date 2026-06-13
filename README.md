# AuraWell: AI-Powered Student Wellness Companion

AuraWell is a production-grade Django web application designed to help students track mood levels, maintain daily journals, analyze emotional burnout markers, and receive personalized generative AI wellness coaching while preparing for high-stakes examinations (such as UPSC, JEE, NEET, and CAT).

---

## 🌟 Key Features

1. **Daily Mood Logging**: Records daily mood, stress, energy levels, sleep quality, and study satisfaction scores.
2. **Secure Reflective Journaling**: Daily journals to register study stress or preparation anxieties.
3. **AI Journal Analysis**: Analyzes student journals for emotional patterns, stress triggers, and burnout risks.
4. **Empathetic AI Coaching**: Generates actionable, context-personalized mindfulness, study break, and time management suggestions.
5. **Safety Regex Engine**: Monitors entries for crisis/self-harm keywords. When detected, the AI is bypassed to immediately escalate and display crisis helplines.
6. **Analytics Dashboard**: Renders interactive trend line charts of stress and mood dynamics using Chart.js.
7. **Daily Reminders**: Command line helper tool for scheduling cron alerts.

---

## 🏗️ Folder Structure

```text
/Users/inception/promptwar/
├── config/                  # Global django settings and routing
├── apps/                    # Encapsulated application modules
│   ├── accounts/            # Users, profile, exam models
│   ├── moods/               # Mood logs
│   ├── journals/            # Journal entries and AI analysis
│   ├── ai_coach/            # AI recommendation targets
│   ├── analytics/           # Trend reports and metrics
│   ├── notifications/       # User reminders
│   └── safety/              # Safety escalation, crisis alerts, and audits
├── services/                # Mandatory service layer (AI, Safety, Logging)
├── static/                  # Shared style sheets and JS charts
├── templates/               # Global templates (sidebar layouts and forms)
├── tests/                   # Pytest automated test suites
├── docs/                    # Architectural and developer guides
└── manage.py                # Django manager script
```

---

## ⚙️ Local Installation & Setup

### 1. Initialize Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory:
```env
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
AI_PROVIDER=mock
SECRET_KEY=your-custom-django-secret-key
```

### 3. Apply Migrations & Seed Exams
```bash
python manage.py migrate
```
*Note: AuraWell automatically seeds standard high-stakes exams (UPSC, JEE, NEET, CAT, SSC, Banking) into the database on migration.*

### 4. Run Development Server
```bash
python manage.py runserver
```
Visit the landing page at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

## 🧪 Running Automated Tests
The test suite implements 91% coverage across services, views, forms, and models.
```bash
.venv/bin/pytest
```

---

## 🚀 Deployment

Please review our [Deployment Guide](file:///Users/inception/promptwar/docs/deployment.md) for details on setting up WhiteNoise, PostgreSQL databases, and environment configs for **Vercel**, **Railway**, and **Render**.
