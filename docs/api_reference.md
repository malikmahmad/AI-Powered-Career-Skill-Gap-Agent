# API Reference

Function-level reference for all service modules.

---

## `src/services/gemini_service.py`

### `extract_candidate_skills(resume_text: str) -> list`

Extracts and normalises technical skills from a resume using Gemini.

**Parameters:**
- `resume_text` — Full resume text (PDF-extracted or pasted). Truncated to `RESUME_MAX_CHARS` (15,000) before sending to the model.

**Returns:** List of skill dicts:
```python
[
  {
    "name": "React",
    "category": "Languages & Frameworks",
    "evidence_level": 2,
    "justification": "Used in 3 production projects with metrics"
  }
]
```

**Evidence levels:** `2` = Demonstrated, `1` = Theoretical, `0` = Missing (never returned here — only assigned by `analyze_gaps` for market skills not found in the resume).

**Errors:** Returns `[]` and shows `st.error()` if the API call fails.

---

### `extract_market_skills(jd_texts: list[str]) -> list`

Extracts required and preferred skills from a list of job descriptions.

**Parameters:**
- `jd_texts` — List of raw job description strings.

**Returns:** Per-JD skill lists:
```python
[
  {"jd_index": 1, "skills": ["React", "Node.js", "PostgreSQL"]},
  {"jd_index": 2, "skills": ["Python", "Docker", "AWS"]}
]
```

**Errors:** Returns `[]` and shows `st.error()` if the API call fails.

---

## `src/services/gap_engine.py`

### `calculate_market_frequencies(jd_analyses: list) -> dict`

Calculates how frequently each skill appears across all job descriptions.

**Parameters:**
- `jd_analyses` — Output of `extract_market_skills()`.

**Returns:** Dict mapping skill name → frequency percentage:
```python
{"React": 100.0, "Docker": 66.7, "AWS": 33.3}
```

**Notes:**
- Uses `set()` deduplication per JD to prevent a skill mentioned twice in one JD from inflating its count.
- Frequencies are rounded to 1 decimal place.

---

### `analyze_gaps(candidate_skills: list, market_frequencies: dict) -> dict`

Cross-references candidate skills with market demand to produce a gap matrix and readiness score.

**Parameters:**
- `candidate_skills` — Output of `extract_candidate_skills()`.
- `market_frequencies` — Output of `calculate_market_frequencies()`.

**Returns:**
```python
{
  "readiness_score": 67,   # 0-100 integer
  "gap_matrix": [
    {
      "skill": "Docker",
      "frequency": 66.7,
      "evidence_level": 0,
      "is_high_priority": True,
      "category": "Tools & DevOps",
      "justification": "Missing from profile"
    }
  ]
}
```

**Gap matrix is sorted by `frequency` descending.**

**Readiness formula:**
```
round( Σ(freq × evidence_level) / Σ(freq × 2) × 100 )
```

---

## `src/services/roadmap_service.py`

### `generate_roadmap(gap_matrix: list) -> str`

Generates a project-first learning roadmap targeting high-priority gaps.

**Parameters:**
- `gap_matrix` — Output of `analyze_gaps()["gap_matrix"]`.

**Returns:** Markdown string (rendered via `st.markdown()`).

**Notes:**
- Filters to `is_high_priority` and `evidence_level == 1` skills before building the prompt.
- Number of steps = `min(max(len(high_priority), 2), 5)`.
- Returns a success message string if no gaps are found.

---

### `get_chat_response(messages: list, gap_matrix: list) -> str`

Answers user questions grounded in the candidate's gap analysis.

**Parameters:**
- `messages` — Chat history as `[{"role": "user"|"assistant", "content": str}]`.
- `gap_matrix` — The current gap matrix for context injection.

**Returns:** Plain text response string.

**Notes:**
- Only the last `CHAT_HISTORY_WINDOW` (10) messages are sent to keep prompt size bounded.
- The full gap matrix is injected as a system context block before the conversation.

---

## `src/services/export_service.py`

### `gap_matrix_to_csv(gap_matrix: list) -> str`

Converts a gap matrix to a CSV string for download.

**Parameters:**
- `gap_matrix` — Output of `analyze_gaps()["gap_matrix"]`.

**Returns:** UTF-8 CSV string with columns: `Skill, Status, Market %, Category, Evidence, Priority`.

---

## `src/db/supabase_client.py`

### `get_supabase_client() -> Client | None`

Returns a cached Supabase client, or `None` if credentials are not configured.

Decorated with `@st.cache_resource` — created once per session.

---

### `save_analysis(user_id, user_email, profile_data, gap_matrix) -> bool`

Persists an analysis result to Supabase.

**Parameters:**
- `user_id` — UUID string (auto-generated if user is anonymous).
- `user_email` — Email string (defaults to `"anonymous"`).
- `profile_data` — Dict with `resume` (str, truncated) and `target_role` (str).
- `gap_matrix` — Full gap matrix list (saved as JSONB).

**Returns:** `True` on success, `False` on failure or if Supabase is not configured.

**DB Table:** `public."Profiles"` — see `scripts/setup_supabase.sql` for full schema.

---

## `src/config.py`

All application-level constants. Import directly:

```python
from src.config import GEMINI_MODEL, HIGH_PRIORITY_THRESHOLD, SCORE_STRONG
```

| Constant | Value | Purpose |
|----------|-------|---------|
| `GEMINI_MODEL` | `"gemini-2.0-flash"` | Model used for all AI calls |
| `GEMINI_TEMPERATURE_EXTRACTION` | `0.1` | Low temp for deterministic JSON |
| `GEMINI_TEMPERATURE_ROADMAP` | `0.4` | Slightly creative for roadmap prose |
| `GEMINI_TEMPERATURE_CHAT` | `0.5` | Conversational chat responses |
| `RESUME_MAX_CHARS` | `15000` | Truncation limit before Gemini |
| `HIGH_PRIORITY_THRESHOLD` | `50.0` | Min frequency for high-priority flag |
| `EVIDENCE_DEMONSTRATED` | `2` | Max evidence level |
| `EVIDENCE_THEORETICAL` | `1` | Partial evidence level |
| `EVIDENCE_MISSING` | `0` | Not present |
| `CHAT_HISTORY_WINDOW` | `10` | Max messages in chat prompt |
| `ROADMAP_MAX_STEPS` | `5` | Max roadmap steps generated |
| `SCORE_STRONG` | `75` | Green threshold |
| `SCORE_MODERATE` | `50` | Yellow threshold |
