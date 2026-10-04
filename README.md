<div align="center">

# ⚡ SkillGap AI

### AI-Powered Career Skill Gap Analyzer

**Know exactly where you stand. Close the gaps. Land the role.**

SkillGap AI compares your resume against real job market demands using Google Gemini 2.0, computes a mathematical readiness score, generates a personalised project-based roadmap, and lets you chat with an AI career coach — all in under a minute, no account required.

<br/>

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.36-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Google_Gemini-3.5_Flash_Lite-4285F4?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev)
[![Supabase](https://img.shields.io/badge/Supabase-DB-3FCF8E?style=flat-square&logo=supabase&logoColor=white)](https://supabase.com)
[![Plotly](https://img.shields.io/badge/Plotly-Charts-3F4F75?style=flat-square&logo=plotly&logoColor=white)](https://plotly.com)
[![Tests](https://img.shields.io/badge/Tests-38_passing-22c55e?style=flat-square&logo=pytest&logoColor=white)](#testing)
[![License](https://img.shields.io/badge/License-MIT-a78bfa?style=flat-square)](LICENSE)

</div>

---

## What It Does

Most job seekers don't know which specific skills are missing from their profile. SkillGap AI solves this by:

1. **Extracting** and normalising skills from your resume using Gemini's structured JSON output
2. **Analysing** target job descriptions (6 built-in industry presets or your own) to identify market-demanded skills and their frequency
3. **Computing** a mathematical gap matrix scoring each skill as *Demonstrated*, *Theoretical*, or *Missing*, weighted by market demand
4. **Generating** a dynamic project-first learning roadmap targeting your highest-priority gaps
5. **Providing** an interactive AI career coach chatbot grounded in your actual analysis data
6. **Exporting** your full gap matrix as a CSV for offline review or sharing

---

## Features

### 🎯 Precision Skill Extraction
Gemini parses your resume and normalises skills to standard names (`Postgres → PostgreSQL`, `React.js → React`). Each skill is assigned an evidence level:
- **Demonstrated** — backed by project descriptions, metrics, or work experience
- **Theoretical** — listed in a skills section with no supporting proof

### 📊 Market Intelligence Dashboard
- **Readiness Score** — a single percentage quantifying your overall market fit, rendered as a live gauge chart
- **Radar Chart** — visual comparison of your proficiency vs. market demand across the top 10 skills
- **Gap Matrix Table** — every market-demanded skill, your status, and frequency — colour-coded and sortable
- **High-Priority Alerts** — skills with ≥50% market demand that you haven't demonstrated yet

### 🗺️ AI Roadmap Generation
A dynamic (2–5 step) project-based roadmap respecting prerequisite logic. Each step is a specific micro-project that produces a portfolio artefact as proof of the skill.

### 💬 AI Career Coach
A conversational chatbot grounded in your gap matrix data. Ask contextual questions like *"Why is Docker high priority?"* or *"What should I build first?"* — it answers using your actual numbers, not generic advice.

### ⬇️ CSV Export
Download your complete gap matrix as a structured CSV from both the Results and Skill Gaps tabs for offline review, portfolio tracking, or sharing with a mentor.

### 🚀 6 Industry Role Presets
Ready-to-use market baselines, each backed by 3 real-world job descriptions:

| Role | Key Skills Analysed |
|------|---------------------|
| Full-Stack Developer | React, Node.js, PostgreSQL, Docker, TypeScript, AWS |
| Data Scientist | Python, Pandas, Scikit-learn, SQL, PyTorch, Snowflake |
| ML Engineer | PyTorch, MLflow, Kubernetes, LLMs, Hugging Face, FastAPI |
| DevOps Engineer | Docker, Kubernetes, Terraform, AWS, CI/CD, Prometheus |
| UI/UX Designer | Figma, Design Systems, User Research, Prototyping, Framer |
| Product Manager | Roadmapping, SQL, A/B Testing, Agile, OKRs, Stakeholder Comms |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                     │
│   app.py · src/ui/dashboard.py · src/ui/charts.py        │
├─────────────────────────────────────────────────────────┤
│                    SERVICE LAYER                         │
│   gemini_service · gap_engine · roadmap_service          │
│   export_service                                         │
├─────────────────────────────────────────────────────────┤
│                  CONFIGURATION LAYER                     │
│   src/config.py  (all constants & thresholds)            │
├─────────────────────────────────────────────────────────┤
│                   DATA / PERSISTENCE                     │
│   Supabase (optional) · presets.json · session_state     │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
Resume (PDF / Text) + Target Role (preset or custom JD)
        │
        ▼
Gemini → Extract & Normalise Candidate Skills
        │
        ▼
Gemini → Extract & Normalise Market Skills per JD
        │
        ▼
Gap Engine → Frequency Calculation + Gap Comparison
        │
        ├─── Readiness Score (gauge)
        ├─── Gap Matrix Table (colour-coded)
        ├─── Radar Chart (proficiency vs. demand)
        ├─── CSV Export
        ├─── AI Roadmap (lazy, tab 4)
        └─── AI Career Coach (chat, tab 4)
```

---

## Tech Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend | Streamlit | 1.36 | Interactive dashboard, custom CSS design system |
| AI / LLM | Google Gemini 3.5 Flash Lite | via `google-genai` | Skill extraction, roadmap, chatbot |
| Database | Supabase | 2.5 | Optional profile persistence (JSONB gap matrix) |
| Charts | Plotly | 5.22 | Gauge chart, radar chart |
| Data | Pandas | 2.2 | DataFrame manipulation, styled gap table |
| PDF | pypdf | 4.2 | Resume text extraction |
| Config | python-dotenv | 1.0.1 | Environment variable management |
| HTTP | requests | 2.32 | External API calls |

> **Note:** Uses `google-genai` (REST/HTTP) instead of the legacy `google-generativeai` (gRPC). No gRPC dependencies — works on restricted Windows environments.

---

## Project Structure

```
skillgap-ai/
│
├── app.py                        # Entry point — global CSS, sidebar, routing
├── requirements.txt              # Pinned Python dependencies
├── .env                          # API keys & secrets (never committed)
├── .env.example                  # Environment variable template
├── CHANGELOG.md                  # Version history
├── CONTRIBUTING.md               # Development guide
├── LICENSE                       # MIT License
│
├── .streamlit/
│   └── config.toml               # Dark theme + performance config
│
├── docs/
│   ├── architecture.md           # System design, data flow, scoring model
│   ├── api_reference.md          # All public function docs with types
│   └── deployment.md             # Streamlit Cloud, Railway, Docker guides
│
├── scripts/
│   └── setup_supabase.sql        # One-command DB schema setup
│
├── tests/
│   ├── test_gap_engine.py        # 16 unit tests — math core
│   ├── test_gemini_service.py    # 14 unit tests — AI layer (mocked)
│   └── test_export_service.py    # 8 unit tests — CSV export
│
└── src/
    ├── config.py                 # All constants, thresholds, model settings
    ├── data/
    │   ├── presets.json          # 6 industry role presets (3 JDs each)
    │   └── sample_resume.txt     # Demo resume for testing
    ├── db/
    │   └── supabase_client.py    # Supabase connection + save_analysis()
    ├── services/
    │   ├── gemini_service.py     # Gemini API: skill extraction
    │   ├── gap_engine.py         # Mathematical gap analysis + readiness score
    │   ├── roadmap_service.py    # AI roadmap generation + career coach chat
    │   └── export_service.py     # CSV export logic
    └── ui/
        ├── dashboard.py          # Main 4-tab dashboard + pipeline orchestration
        └── charts.py             # Plotly gauge, radar chart, gap matrix table
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- A [Google AI Studio API Key](https://aistudio.google.com/) (required — free tier available)
- A [Supabase](https://supabase.com) project (optional — app works fully without it)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/malikmahmad/AI-Powered-Career-Skill-Gap-Agent.git
cd AI-Powered-Career-Skill-Gap-Agent

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Environment Variables

```env
# Required
GEMINI_API_KEY="your-gemini-api-key"

# Optional — app runs in demo mode without these
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_KEY="your-supabase-anon-key"
ADMIN_SECRET_KEY="your-admin-secret"
```

> `.env` is already in `.gitignore` — your secrets will never be committed.

### Run

```bash
python -m streamlit run app.py
```

App opens at **http://localhost:8501**

---

## How to Use

1. **Choose a target role** — select from 6 presets in the dropdown, or paste a custom JD
2. **Upload your resume** — PDF upload or paste text directly
3. **Run the analysis** — click **Run Analysis** and wait ~15–30 seconds for Gemini to process
4. **Explore your results across 3 tabs:**
   - **📊 Results** — readiness score gauge, radar chart, skill stats, CSV download
   - **🔍 Skill Gaps** — full colour-coded skill matrix sorted by market demand, CSV export
   - **🗺️ Roadmap & Chat** — AI-generated project roadmap + interactive career coach

---

## Testing

**38 tests, 0 failures.** No API key required — all AI calls are mocked.

```bash
python -m pytest tests/ -v
```

| Test File | Coverage |
|-----------|----------|
| `test_gap_engine.py` | Frequency calculation, gap analysis, score formula, edge cases |
| `test_gemini_service.py` | JSON cleaning, skill extraction, error handling, truncation |
| `test_export_service.py` | CSV structure, status mapping, empty input, parseability |

---

## Readiness Score Formula

```
Readiness = round( Σ(skill_frequency × evidence_level) / Σ(skill_frequency × 2) × 100 )
```

Where `evidence_level` is `0` (Missing), `1` (Theoretical), or `2` (Demonstrated).

A skill at 100% market frequency that's only Theoretical contributes 50% of its maximum — incentivising the candidate to back it with a real project.

**High-Priority Flag:** A skill is flagged if its market frequency is ≥50% **and** evidence level is below Demonstrated. These appear as alerts in the UI and are prioritised in the roadmap.

---

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/architecture.md) | System design, data flow, state machine, scoring model |
| [API Reference](docs/api_reference.md) | Every public function with parameters, return types, and examples |
| [Deployment Guide](docs/deployment.md) | Deploy to Streamlit Cloud, Railway, or Docker |
| [Contributing](CONTRIBUTING.md) | Dev setup, code style, how to add presets or features |
| [Changelog](CHANGELOG.md) | Version history and breaking changes |

---

## Database Setup (Optional)

To enable analysis persistence, run the schema in your Supabase SQL Editor:

```bash
# Paste the contents of scripts/setup_supabase.sql into:
# Supabase Dashboard → SQL Editor → New Query → Run
```

This creates the `Profiles` table with JSONB gap matrix storage, indexes, RLS policies, and an `analysis_summary` analytics view.

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built with [Streamlit](https://streamlit.io) · [Google Gemini](https://ai.google.dev) · [Supabase](https://supabase.com) · [Plotly](https://plotly.com)

</div>
