# Deployment Guide

Three options: Streamlit Community Cloud (easiest), Railway, or Docker.

---

## Option 1: Streamlit Community Cloud (Recommended — Free)

**Best for:** Quick deploys, no infrastructure needed.

### Steps

1. **Fork the repo** on GitHub.

2. **Go to** [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.

3. **Click "New app"** and select your forked repo.
   - Main file path: `app.py`
   - Branch: `main`

4. **Set secrets** under "Advanced settings → Secrets":
   ```toml
   GEMINI_API_KEY = "your-gemini-api-key"
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_KEY = "your-supabase-anon-key"
   ADMIN_SECRET_KEY = "your-admin-secret"
   ```

5. **Click Deploy.** Done — your app is live at `https://your-app-name.streamlit.app`.

### Notes
- Streamlit Cloud reads secrets from `.streamlit/secrets.toml` at runtime, so don't commit that file (it's in `.gitignore`).
- Free tier: 1 GB RAM, sleeps after 7 days of inactivity.

---

## Option 2: Railway

**Best for:** Always-on deployment with more control.

### Steps

1. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. Init a new project:
   ```bash
   railway init
   ```

3. Add a `Procfile` at the repo root:
   ```
   web: python -m streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```

4. Set environment variables in the Railway dashboard under your service → Variables:
   ```
   GEMINI_API_KEY = your-key
   SUPABASE_URL   = your-url
   SUPABASE_KEY   = your-key
   ADMIN_SECRET_KEY = your-secret
   ```

5. Deploy:
   ```bash
   railway up
   ```

Railway auto-detects Python and installs from `requirements.txt`.

---

## Option 3: Docker

**Best for:** Self-hosting, consistent environments.

### Dockerfile

Create `Dockerfile` at the repo root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
```

### Build and Run

```bash
# Build
docker build -t skillgap-ai .

# Run (pass env vars)
docker run -p 8501:8501 \
  -e GEMINI_API_KEY="your-key" \
  -e SUPABASE_URL="your-url" \
  -e SUPABASE_KEY="your-key" \
  skillgap-ai
```

App is available at `http://localhost:8501`.

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ Yes | Google AI Studio API key — get one free at [aistudio.google.com](https://aistudio.google.com) |
| `SUPABASE_URL` | ❌ Optional | Supabase project URL |
| `SUPABASE_KEY` | ❌ Optional | Supabase anon/public key |
| `ADMIN_SECRET_KEY` | ❌ Optional | Secret key for admin sidebar access |

The app runs in **demo mode** without Supabase — all analysis, roadmap, and export features work fully offline.

---

## Database Setup (Supabase)

If using Supabase, run the schema before first deployment:

1. Go to your Supabase project → SQL Editor → New Query.
2. Paste the contents of `scripts/setup_supabase.sql`.
3. Click Run.

This creates the `Profiles` table, indexes, RLS policies, and the `analysis_summary` view.

---

## Health Check

After deployment, verify the app is working:

1. Open the app URL.
2. Select **Full-Stack Developer** from the role dropdown.
3. Paste the contents of `src/data/sample_resume.txt` into the text field.
4. Click **Run Analysis**.
5. You should see a readiness score and a populated gap matrix within ~30 seconds.
6. Use the **⬇️ Download Report (CSV)** button in the Results tab to verify the export works.
