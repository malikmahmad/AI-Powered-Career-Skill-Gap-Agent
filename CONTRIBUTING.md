# Contributing to SkillGap AI

Thanks for your interest in contributing. This document covers everything you need to get started.

---

## Development Setup

```bash
# 1. Fork and clone
git clone https://github.com/malikmahmad/AI-Powered-Career-Skill-Gap-Agent.git
cd AI-Powered-Career-Skill-Gap-Agent

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy env template
cp .env.example .env
# Fill in your GEMINI_API_KEY (required) and optional Supabase keys

# 5. Run the app
python -m streamlit run app.py
```

---

## Project Structure

```
app.py                  Entry point — CSS, sidebar, routing
src/
  config.py             Central constants (model name, thresholds)
  services/
    gemini_service.py   Gemini API calls (skill extraction)
    gap_engine.py       Pure-Python math engine (gap analysis)
    roadmap_service.py  Roadmap generation + chatbot
    export_service.py   CSV export
  ui/
    dashboard.py        Main 4-tab dashboard
    charts.py           Plotly visualisations
  db/
    supabase_client.py  Supabase connection + persistence
  data/
    presets.json        6 industry role presets
    sample_resume.txt   Demo resume for testing
tests/
  test_gap_engine.py    Unit tests — math core
  test_gemini_service.py  Tests — AI service layer (mocked)
docs/
  architecture.md       System design
  api_reference.md      Service function reference
  deployment.md         Deploy to Streamlit Cloud / Railway
scripts/
  setup_supabase.sql    One-command DB schema setup
```

---

## Running Tests

```bash
python -m pytest tests/ -v
```

Tests use `unittest.mock` to avoid real API calls — no API key needed to run them.

---

## Contribution Guidelines

### Code Style
- Follow PEP 8. Use 4-space indentation.
- Keep functions focused — one responsibility each.
- Add docstrings to all public functions.
- Type-hint function signatures where practical.

### Adding a New Role Preset
1. Open `src/data/presets.json`.
2. Add a new entry following the existing structure — `id`, `name`, and exactly 3 `job_descriptions`.
3. Each JD should be formatted with bold section headers and cover a range of experience levels.
4. Test by running the app and selecting your new preset.

### Adding a New Feature
1. Open an issue describing the feature before starting work.
2. Create a branch: `git checkout -b feature/your-feature-name`
3. Write tests in `tests/` for any new logic.
4. Update `docs/api_reference.md` if you add new service functions.
5. Add an entry to `CHANGELOG.md` under `[Unreleased]`.
6. Submit a pull request with a clear description.

### Bug Reports
Open a GitHub issue with:
- Steps to reproduce
- Expected behaviour
- Actual behaviour
- Python version and OS

---

## Commit Message Format

```
type: short description (max 72 chars)

Optional longer explanation.
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

Examples:
```
feat: add cybersecurity analyst preset
fix: handle empty gap matrix in radar chart
docs: update deployment guide for Railway
```
