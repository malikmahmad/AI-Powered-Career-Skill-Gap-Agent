import os
import streamlit as st
from google import genai
from google.genai import types
from src.config import (
    GEMINI_MODEL,
    GEMINI_TEMPERATURE_ROADMAP,
    GEMINI_TEMPERATURE_CHAT,
    CHAT_HISTORY_WINDOW,
    ROADMAP_MIN_STEPS,
    ROADMAP_MAX_STEPS,
)

_MODEL = GEMINI_MODEL
_CHAT_WINDOW = CHAT_HISTORY_WINDOW


def _get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


def generate_roadmap(gap_matrix: list) -> str:
    """
    Generates a project-first learning roadmap targeting high-priority gaps.
    Returns Markdown text.
    """
    client = _get_client()
    if not client:
        return "⚠️ Gemini API key is missing. Add GEMINI_API_KEY to your .env file."

    high_priority = [g for g in gap_matrix if g.get("is_high_priority", False)]
    theoretical   = [g for g in gap_matrix if g.get("evidence_level") == 1]

    if not high_priority and not theoretical:
        return "✅ No critical gaps found — your profile is a strong match for this role!"

    n_steps = min(max(len(high_priority), ROADMAP_MIN_STEPS), ROADMAP_MAX_STEPS)

    gaps_summary  = f"High-Priority Gaps (≥50% market demand, not yet demonstrated): {[g['skill'] for g in high_priority]}\n"
    gaps_summary += f"Theoretical Skills (need project proof): {[g['skill'] for g in theoretical]}"

    prompt = f"""You are an expert career coach and senior software architect.
A candidate has the following skill gaps based on market demand analysis:

{gaps_summary}

Generate a {n_steps}-step project-based learning roadmap to close these gaps.
Rules:
- Each step must be a specific, buildable micro-project that proves the skill (no vague advice).
- Respect prerequisite order (languages before frameworks, foundations before tools).
- Each step should take 1–2 weeks max.
- Format in clean Markdown with step headers, project name, and what it proves.
- Do not include generic career advice or soft skills."""

    try:
        response = client.models.generate_content(
            model=_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=GEMINI_TEMPERATURE_ROADMAP),
        )
        return response.text
    except Exception as e:
        return f"⚠️ Error generating roadmap: {e}"


def get_chat_response(messages: list, gap_matrix: list) -> str:
    """
    AI career coach — answers questions grounded in the candidate's gap matrix.
    Uses a rolling window of the last 10 messages to keep prompts bounded.
    """
    client = _get_client()
    if not client:
        return "⚠️ Gemini API key is missing. Add GEMINI_API_KEY to your .env file."

    # Build gap context
    level_map = {2: "Demonstrated", 1: "Theoretical", 0: "Missing"}
    context_lines = []
    for g in gap_matrix:
        status = level_map.get(g.get("evidence_level"), "Unknown")
        context_lines.append(
            f"- {g['skill']}: {g.get('frequency', 0)}% market demand | Status: {status}"
        )
    context = "\n".join(context_lines)

    system = f"""You are an AI Career Coach embedded in a skill gap analysis platform.
You have access to the candidate's full gap analysis. Use it to give specific, data-driven answers.

Candidate Skill Gap Data:
{context}

Guidelines:
- Be concise (max 3–4 sentences per answer unless a list is needed).
- Be encouraging but honest — don't sugarcoat significant gaps.
- Always reference specific skills from the data, not generic advice.
- If asked about priority, reference the market frequency percentages."""

    # Rolling window — last N messages only
    recent = messages[-_CHAT_WINDOW:]
    history = "\n".join(
        f"{m['role'].capitalize()}: {m['content']}" for m in recent
    )

    full_prompt = f"{system}\n\n--- Conversation ---\n{history}\nAssistant:"

    try:
        response = client.models.generate_content(
            model=_MODEL,
            contents=full_prompt,
            config=types.GenerateContentConfig(temperature=GEMINI_TEMPERATURE_CHAT),
        )
        return response.text
    except Exception as e:
        return f"⚠️ Error generating response: {e}"
