# Deployment Guide: AuraWell

AuraWell can be deployed to Vercel, Railway, or Render.

## 1. Vercel (Recommended Primary Target)

Vercel hosts the application as a serverless Python function.

### Config Files
* `vercel.json`: Handles routing and wsgi target.
* `requirements.txt`: Python package installations.

### Steps to Deploy
1. Install Vercel CLI: `npm install -g vercel`
2. Run `vercel` in the project root.
3. Configure environment variables in Vercel project settings:
   * `SECRET_KEY`: Long random string.
   * `DATABASE_URL`: Production PostgreSQL URL.
   * `AI_PROVIDER`: `openai` | `gemini` | `azure`.
   * `OPENAI_API_KEY`: OpenAI secret key.
   * `DEBUG`: `False`.

---

## 2. Railway (Secondary Target)

Railway is excellent for running permanent stateful web projects.

### Config Files
* `Procfile`:
  ```text
  web: gunicorn config.wsgi --log-file -
  ```

### Steps to Deploy
1. Create a new project on Railway.
2. Link your GitHub repository.
3. Add a PostgreSQL database service.
4. Railway automatically injects the `DATABASE_URL` variable.

---

## 3. Render (Third Target)

### Steps to Deploy
1. Click **New Web Service** in Render.
2. Link your GitHub repository.
3. Select **Python** runtime environment.
4. Set Build Command:
   ```bash
   pip install -r requirements.txt && python manage.py collectstatic --noinput
   ```
5. Set Start Command:
   ```bash
   gunicorn config.wsgi
   ```
