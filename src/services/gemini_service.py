import json
import os
import streamlit as st
from google import genai
from google.genai import types
from src.config import (
    GEMINI_MODEL,
    GEMINI_TEMPERATURE_EXTRACTION,
    RESUME_MAX_CHARS,
)


def _get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("Gemini API Key missing — add GEMINI_API_KEY to your .env file.")
        return None
    return genai.Client(api_key=api_key)


def _clean_json(text: str):
    """Strip markdown fences from Gemini responses before json.loads."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return json.loads(text.strip())


_MODEL = GEMINI_MODEL


def extract_candidate_skills(resume_text: str) -> list:
    """
    Uses Gemini to extract and normalise all technical skills from a resume.
    Assigns an evidence level: 2 = Demonstrated, 1 = Theoretical.
    Returns a list of skill dicts.
    """
    client = _get_client()
    if not client:
        return []

    truncated = resume_text[:RESUME_MAX_CHARS]

    prompt = f"""You are an expert technical recruiter and skill gap analyst.
Analyse the following resume and extract all technical skills.
Normalise skill names (e.g. Postgres -> PostgreSQL, React.js -> React).
Categorise each skill into one of: 'Core Foundations', 'Languages & Frameworks', 'Tools & DevOps'.
Assign an evidence level:
  - 2 (Demonstrated): Backed by project descriptions, metrics, or work experience.
  - 1 (Theoretical): Listed only in a skills section with no supporting proof.

Return ONLY valid JSON in this exact format — no markdown, no explanation:
{{
  "skills": [
    {{
      "name": "Skill Name",
      "category": "Category",
      "evidence_level": 1,
      "justification": "Short reason"
    }}
  ]
}}

Resume:
{truncated}"""

    try:
        response = client.models.generate_content(
            model=_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=GEMINI_TEMPERATURE_EXTRACTION,
            ),
        )
        result = _clean_json(response.text)
        return result.get("skills", [])
    except Exception as e:
        st.error(f"Skill extraction failed: {e}")
        return []


def extract_market_skills(jd_texts: list) -> list:
    """
    Uses Gemini to extract required/preferred skills from a list of job descriptions.
    Returns per-JD skill lists so frequency can be calculated.
    """
    client = _get_client()
    if not client:
        return []

    combined = "\n\n--- NEXT JD ---\n\n".join(jd_texts)

    prompt = f"""You are an expert technical recruiter and talent market analyst.
Analyse the following job descriptions and extract all REQUIRED and PREFERRED technical skills.
Normalise skill names to standard forms (e.g. Postgres -> PostgreSQL, React.js -> React).
Keep skills mapped per job description so frequency can be calculated.

Return ONLY valid JSON in this exact format — no markdown, no explanation:
{{
  "jd_analysis": [
    {{
      "jd_index": 1,
      "skills": ["React", "Node.js", "PostgreSQL"]
    }}
  ]
}}

Job Descriptions:
{combined}"""

    try:
        response = client.models.generate_content(
            model=_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=GEMINI_TEMPERATURE_EXTRACTION,
            ),
        )
        result = _clean_json(response.text)
        return result.get("jd_analysis", [])
    except Exception as e:
        st.error(f"Market skill extraction failed: {e}")
        return []
