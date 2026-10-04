<div align="center">

# ⚡ SkillGap AI

### AI-Powered Career Skill Gap Analyzer

**Know exactly where you stand. Close the gaps. Land the role.**

SkillGap AI compares your resume against real job market demands using Google Gemini, computes a mathematical readiness score, and generates a personalised project-based roadmap to close your most critical gaps — all in under a minute, no account required.

<br/>

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.36-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Google_Gemini-3.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev)
[![Supabase](https://img.shields.io/badge/Supabase-Auth_%26_DB-3FCF8E?style=flat-square&logo=supabase&logoColor=white)](https://supabase.com)
[![Plotly](https://img.shields.io/badge/Plotly-Charts-3F4F75?style=flat-square&logo=plotly&logoColor=white)](https://plotly.com)

</div>

---

## What It Does

Most job seekers don't know which skills are actually missing from their profile. SkillGap AI solves this by:

1. **Extracting** and normalising skills from your resume using Gemini's structured JSON output
2. **Analysing** target job descriptions (6 built-in industry presets or your own) to identify market-demanded skills and their frequency
3. **Computing** a mathematical gap matrix scoring each skill as *Demonstrated*, *Theoretical*, or *Missing*, weighted by market demand
4. **Generating** a project-first learning roadmap to close the highest-priority gaps
5. **Providing** an interactive AI career coach chatbot grounded in your actual analysis data

---

## Features

### 🎯 Precision Skill Extraction
Gemini parses your resume and normalises skills to standard names (`Postgres → PostgreSQL`, `React.js → React`). Each skill is assigned an evidence level:
- **Demonstrated** — backed by project descriptions, metrics, or work experience
- **Theoretical** — listed in a skills section with no supporting proof

### 📊 Market Intelligence
- **Readiness Score** — a single percentage quantifying your overall market fit
- **Radar Chart** — visual comparison of your proficiency vs. market demand across the top 10 skills
- **Gap Matrix Table** — every market-demanded skill, your status, and frequency — colour-coded and sortable
- **High-Priority Alerts** — skills with ≥50% market demand that you haven't demonstrated yet

### 🗺️ AI Roadmap Generation
A 3-step project-based roadmap respecting prerequisite logic. Each step is a specific micro-project that produces a portfolio artefact as proof of the skill.

### 💬 AI Career Coach
A conversational chatbot embedded in the roadmap tab. Fully grounded in your gap matrix — ask contextual questions like *"Why is Docker high priority?"* or *"What should I build first?"*

### 🚀 6 Industry Role Presets
Ready-to-use market baselines, each with 3 real-world job descriptions:

| Role | Focus Areas |
|------|-------------|
| Full-Stack Developer | React, Node.js, PostgreSQL, Docker, TypeScript |
| Data Scientist | Python, Pandas, Scikit-learn, SQL, PyTorch |
| ML Engineer | PyTorch, MLflow, Kubernetes, LLMs, Hugging Face |
| DevOps Engineer | Docker, Kubernetes, Terraform, AWS, CI/CD |
| UI/UX Designer | Figma, Design Systems, User Research, Prototyping |
| Product Manager | Roadmapping, SQL, A/B Testing, Agile, Stakeholder Comms |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    STREAMLIT UI                      │
│  ┌──────────────┐  ┌──────────┐  ┌───────────────┐  │
│  │  Setup & Run │  │ Results  │  │ Roadmap & Chat│  │
│  └──────┬───────┘  └────┬─────┘  └──────┬────────┘  │
├─────────┴───────────────┴───────────────┴────────────┤
│                   SERVICE LAYER                      │
│  ┌────────────────┐  ┌───────────┐  ┌─────────────┐  │
│  │ Gemini Service │  │ Gap Engine│  │Roadmap Svc  │  │
│  │ (Extraction)   │  │ (Math)    │  │(AI + Chat)  │  │
│  └───────┬────────┘  └─────┬─────┘  └──────┬──────┘  │
├──────────┴─────────────────┴───────────────┴─────────┤
│                  EXTERNAL SERVICES                   │
│  Google Gemini 3.5 Flash · Supabase · GitHub API     │
└─────────────────────────────────────────────────────┘
```

### Data Flow

```
Resume (PDF / Text)
        │
        ▼
Gemini → Extract & Normalise Candidate Skills
        │
Job Descriptions
        │
        ▼
Gemini → Extract & Normalise Market Skills
        │
        ▼
Gap Engine → Frequency Calculation + Comparison
        │
   ┌────┴────┬──────────────┐
   ▼         ▼              ▼
Readiness  Gap Matrix    AI Roadmap
 Score      Table         + Chat
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Streamlit 1.36 | Interactive dashboard with custom CSS |
| AI / LLM | Google Gemini 3.5 Flash Lite | Skill extraction, roadmap generation, chatbot |
| Auth & DB | Supabase | Authentication & profile persistence |
| Charts | Plotly 5.22 | Radar chart, gauge chart |
| Data | Pandas 2.2 | DataFrame manipulation & styled tables |
| PDF | pypdf 4.2 | Resume text extraction |
| Config | python-dotenv | Environment variable management |

---

## Project Structure

```
skillgap-ai/
│
├── app.py                     # Entry point — global CSS, sidebar, routing
├── requirements.txt           # Pinned Python dependencies
├── .env                       # API keys & secrets (never committed)
│
├── .streamlit/
│   └── config.toml            # Dark theme configuration
│
└── src/
    ├── data/
    │   └── presets.json       # 6 industry role presets (3 JDs each)
    │
    ├── db/
    │   └── supabase_client.py # Supabase connection + profile persistence
    │
    ├── services/
    │   ├── gemini_service.py  # Gemini API: candidate + market skill extraction
    │   ├── gap_engine.py      # Mathematical gap analysis + readiness score
    │   └── roadmap_service.py # AI roadmap generation + career coach chatbot
    │
    └── ui/
        ├── dashboard.py       # Main dashboard (4 tabs)
        └── charts.py          # Plotly gauge, radar, gap matrix table
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- A [Google Gemini API Key](https://aistudio.google.com/) (required)
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
```

### Environment Variables

Create a `.env` file in the project root:

```env
# Required
GEMINI_API_KEY="your-gemini-api-key"

# Optional — app runs in demo mode without these
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_KEY="your-supabase-anon-key"
ADMIN_SECRET_KEY="your-admin-secret"
```

> ⚠️ Never commit your `.env` file. It is already in `.gitignore`.

### Run

```bash
streamlit run app.py
```

App opens at **http://localhost:8501**

---

## How to Use

1. **Choose a target role** — select from 6 presets in the dropdown, or paste a custom JD
2. **Add your resume** — upload a PDF or paste the text
3. **Run the analysis** — click Run Analysis and wait ~15–30 seconds
4. **Explore results**
   - **Results tab** — readiness score gauge + radar chart + summary stats
   - **Skill Gaps tab** — colour-coded skill matrix with high-priority alerts
   - **Roadmap & Chat tab** — AI-generated project roadmap + career coach chatbot

---

## Readiness Score Formula

```
Readiness = Σ(skill_frequency × evidence_level) / Σ(skill_frequency × 2) × 100
```

Where `evidence_level` is `0` (Missing), `1` (Theoretical), or `2` (Demonstrated).

A skill at 100% market frequency that's only Theoretical contributes 50% of its maximum — pushing the candidate to demonstrate it through a real project.

**High-Priority Logic:** A skill is flagged as high priority if its market frequency is ≥50% **and** the candidate's evidence level is below Demonstrated.

---

## License

This project is open-source. See [LICENSE](LICENSE) for details.

---

<div align="center">

Built with [Streamlit](https://streamlit.io) · [Google Gemini](https://ai.google.dev) · [Supabase](https://supabase.com) · [Plotly](https://plotly.com)

</div>
