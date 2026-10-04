# System Architecture

## Overview

SkillGap AI is a single-page Streamlit application with a clean four-layer architecture:

```
┌─────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                   │
│   app.py (entry point, CSS, sidebar)                     │
│   src/ui/dashboard.py (4-tab interface)                  │
│   src/ui/charts.py (Plotly visualisations)               │
├─────────────────────────────────────────────────────────┤
│                      SERVICE LAYER                        │
│   src/services/gemini_service.py   (AI extraction)       │
│   src/services/gap_engine.py       (math core)           │
│   src/services/roadmap_service.py  (roadmap + chat)      │
│   src/services/export_service.py   (CSV export)          │
├─────────────────────────────────────────────────────────┤
│                  CONFIGURATION LAYER                      │
│   src/config.py (constants, thresholds, model settings)  │
├─────────────────────────────────────────────────────────┤
│                    DATA / PERSISTENCE                     │
│   src/db/supabase_client.py (Supabase connection)        │
│   src/data/presets.json     (role JD presets)            │
└─────────────────────────────────────────────────────────┘
```

---

## Data Flow

```
User Input
  ├── Resume (PDF / Text)
  └── Target Role (preset or custom JD)
          │
          ▼
  gemini_service.extract_candidate_skills(resume_text)
          │                returns: List[SkillDict]
          │
  gemini_service.extract_market_skills(jd_texts)
          │                returns: List[JDAnalysisDict]
          │
          ▼
  gap_engine.calculate_market_frequencies(jd_analyses)
          │                returns: Dict[skill_name, frequency_%]
          │
  gap_engine.analyze_gaps(candidate_skills, market_frequencies)
          │                returns: {readiness_score, gap_matrix}
          │
          ▼
  Stored in st.session_state:
    gap_matrix, readiness_score, market_frequencies
          │
  ┌───────┴──────────────────┐
  ▼                          ▼
Charts (Plotly)         roadmap_service.generate_roadmap()
  ├── Gauge                    │   returns: Markdown string
  ├── Radar chart              │
  └── Gap matrix table    roadmap_service.get_chat_response()
                                   (contextual AI coach)
```

---

## Key Design Decisions

### 1. Stateless Services
All service functions (`gap_engine`, `gemini_service`, etc.) are pure functions or stateless modules. They receive inputs, return outputs, and have no side effects. This makes them independently testable and reusable.

### 2. Streamlit Session State as Application State
`st.session_state` is the single source of truth for the current analysis. All pipeline outputs are stored here after `process_analysis()` runs. This means:
- Tabs 2–4 can render independently without re-running the analysis.
- A "New Analysis" button simply clears all relevant keys.

### 3. Graceful Supabase Degradation
`get_supabase_client()` returns `None` if credentials are not configured. Every call site checks for `None` before proceeding. The app is **fully functional without Supabase** — making it zero-friction to run locally.

### 4. Gemini Strict JSON Mode
Both extraction functions (`extract_candidate_skills`, `extract_market_skills`) use `response_mime_type="application/json"`. This forces Gemini to return structurally valid JSON, eliminating fragile regex-based parsing. A `_clean_json()` fallback strips markdown fences in case the mime type hint is ignored.

### 5. REST-only AI (No gRPC)
The `google-genai` package (v1.16+) uses pure HTTP/REST instead of gRPC. This avoids DLL dependency issues on managed/restricted Windows environments and simplifies deployment.

### 6. Lazy Roadmap Generation
The roadmap is generated only when the user first visits Tab 4, then cached in `session_state["roadmap"]`. Switching tabs does not re-trigger the API call.

---

## State Machine

The application has two high-level states:

```
[IDLE]
  │  User selects role + uploads resume
  ▼
[READY]  (jds_ready AND resume_ready)
  │  User clicks "Run Analysis"
  ▼
[ANALYSING]  (progress bar shown, UI blocked)
  │  process_analysis() completes
  ▼
[COMPLETE]  (analysis_complete = True)
  │  Score banner visible, Tabs 2/3/4 unlocked
  │  User clicks "New Analysis"
  └─────────────────────────────────────► [IDLE]
```

---

## Skill Scoring Model

Each skill in the gap matrix has an evidence level:

| Level | Name | Meaning |
|-------|------|---------|
| 2 | Demonstrated | Backed by project, metrics, or work experience |
| 1 | Theoretical | Listed in skills section only — no proof |
| 0 | Missing | Not present in the candidate's profile |

### Readiness Score Formula

```
Readiness = round( Σ(freq_i × evidence_i) / Σ(freq_i × 2) × 100 )
```

Where `freq_i` is the market demand frequency (0–100%) of skill `i`.

This formula weights high-demand skills more heavily — a missing skill that appears in 90% of JDs hurts the score more than a missing skill at 20%.

### High-Priority Flag

A skill is flagged `is_high_priority = True` if:
```
market_frequency >= HIGH_PRIORITY_THRESHOLD (50%)
AND evidence_level < EVIDENCE_DEMONSTRATED (2)
```

---

## File Reference

| File | Responsibility |
|------|---------------|
| `app.py` | Entry point, global CSS, sidebar, routing |
| `src/config.py` | All constants, thresholds, model settings |
| `src/ui/dashboard.py` | 4-tab dashboard, pipeline orchestration |
| `src/ui/charts.py` | Plotly gauge, radar chart, gap matrix table |
| `src/services/gemini_service.py` | Gemini API calls, JSON extraction |
| `src/services/gap_engine.py` | Market frequency calculation, readiness score |
| `src/services/roadmap_service.py` | Roadmap generation, AI chat |
| `src/services/export_service.py` | CSV export |
| `src/db/supabase_client.py` | DB connection, `save_analysis()` |
| `src/data/presets.json` | 6 industry role presets (3 JDs each) |
| `src/data/sample_resume.txt` | Demo resume for testing |
| `scripts/setup_supabase.sql` | DB schema — run once in Supabase SQL editor |
| `tests/` | Unit test suite (no API key needed) |
