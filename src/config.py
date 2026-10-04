"""
Central configuration for SkillGap AI.
All constants, thresholds, and model settings live here.
Import from this module instead of scattering magic numbers across the codebase.
"""

# ── AI Model ──────────────────────────────────────────────────────────────────
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_TEMPERATURE_EXTRACTION = 0.1   # low temp → deterministic JSON output
GEMINI_TEMPERATURE_ROADMAP    = 0.4   # slightly creative for roadmap prose
GEMINI_TEMPERATURE_CHAT       = 0.5   # conversational but grounded

# Max characters sent to Gemini (avoid context-limit errors on large resumes)
RESUME_MAX_CHARS = 15_000

# ── Gap Engine ────────────────────────────────────────────────────────────────
# A skill is flagged HIGH PRIORITY if market frequency >= this AND evidence < 2
HIGH_PRIORITY_THRESHOLD = 50.0    # percent

# Evidence levels
EVIDENCE_DEMONSTRATED = 2
EVIDENCE_THEORETICAL  = 1
EVIDENCE_MISSING      = 0

EVIDENCE_LABELS = {
    EVIDENCE_DEMONSTRATED: "Demonstrated",
    EVIDENCE_THEORETICAL:  "Theoretical",
    EVIDENCE_MISSING:      "Missing",
}

# Readiness score colour bands
SCORE_STRONG   = 75   # >= this → green
SCORE_MODERATE = 50   # >= this → yellow
SCORE_WEAK     = 25   # >= this → orange
                      # < SCORE_WEAK → red

# ── Chat ──────────────────────────────────────────────────────────────────────
CHAT_HISTORY_WINDOW = 10   # keep last N messages in prompt context

# ── Roadmap ───────────────────────────────────────────────────────────────────
ROADMAP_MIN_STEPS = 2
ROADMAP_MAX_STEPS = 5

# ── Skill Categories ──────────────────────────────────────────────────────────
SKILL_CATEGORIES = [
    "Core Foundations",
    "Languages & Frameworks",
    "Tools & DevOps",
]

# ── Export ────────────────────────────────────────────────────────────────────
CSV_COLUMNS = ["Skill", "Status", "Market %", "Category", "Evidence", "Priority"]
