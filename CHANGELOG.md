# Changelog

All notable changes to SkillGap AI are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [2.0.0] — 2026-10-04

### Breaking Changes
- Replaced `google-generativeai` (gRPC) with `google-genai` (REST-only). No gRPC dependency.
- Upgraded AI model to `gemini-2.0-flash` for faster, more accurate extraction.
- Removed mandatory authentication — app opens directly to dashboard.

### Added
- 6 industry role presets: Full-Stack Developer, Data Scientist, ML Engineer, DevOps Engineer, UI/UX Designer, Product Manager (up from 2).
- Export feature: download gap matrix as CSV directly from the Skill Gaps tab.
- `src/config.py` — centralised constants (model name, thresholds, limits).
- `src/services/export_service.py` — CSV export logic.
- `tests/` — full unit test suite for gap engine and service layer.
- `docs/` — architecture, API reference, and deployment guides.
- `scripts/setup_supabase.sql` — complete DB schema for one-command setup.
- `src/data/sample_resume.txt` — demo resume for testing without a real CV.
- `.env.example` — safe template for environment configuration.
- `CONTRIBUTING.md`, `CHANGELOG.md`, `LICENSE`.
- Sidebar "How it works" step guide and post-analysis summary card.

### Fixed
- **PDF upload bug**: resume text now persisted to `session_state` immediately on upload, survives reruns.
- **Readiness score truncation**: `int()` replaced with `round()` — scores like 73.9% now correctly show as 74%.
- **Roadmap rendering bug**: Gemini Markdown was being injected into raw HTML, breaking all formatting. Now rendered via `st.markdown()`.
- **Chat history unbounded growth**: rolling window of last 10 messages prevents prompt bloat.
- **`save_analysis` silent data loss**: gap_matrix now actually persisted to Supabase as JSONB.
- `load_presets()` cached with `@st.cache_data` — eliminated 3× redundant disk reads per render.

### Removed
- Mandatory login / signup / admin authentication screen.
- Admin panel (telemetry + dataset editor) — removed from routing.
- Dead code: `admin_dashboard.py`, `github_service.py`, `extractor.py`, `gap_engine.py` (root), `roadmap.py`, `schemas.py`.
- GitHub URL input and LinkedIn paste fields — simplicity over feature creep.

---

## [1.0.0] — 2026-09-15

### Added
- Initial release with Supabase auth, 2 presets, Gemini skill extraction, gap matrix, roadmap, and AI career coach chatbot.
