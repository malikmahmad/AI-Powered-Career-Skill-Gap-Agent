import os
import json
import logging
import streamlit as st
from supabase import create_client, Client

logger = logging.getLogger(__name__)


@st.cache_resource
def get_supabase_client():
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")

    if not url or not key or url == "your-supabase-project-url":
        return None

    try:
        supabase: Client = create_client(url, key)
        return supabase
    except Exception as e:
        logger.error(f"Supabase connection error: {e}")
        return None


def save_analysis(user_id: str, user_email: str, profile_data: dict, gap_matrix: list) -> bool:
    """
    Persists the analysis result to Supabase.
    Gracefully returns False if Supabase is not configured.

    Expected Profiles table schema:
        user_id     text
        user_email  text
        resume_text text
        target_role text
        gap_matrix  jsonb
        readiness_score int  (optional, derived from gap_matrix)
        created_at  timestamptz default now()
    """
    client = get_supabase_client()
    if not client:
        return False

    try:
        client.table("Profiles").insert({
            "user_id":     user_id,
            "user_email":  user_email,
            "resume_text": profile_data.get("resume", ""),
            "target_role": profile_data.get("target_role", "unknown"),
            "gap_matrix":  json.dumps(gap_matrix),
        }).execute()
        return True
    except Exception as e:
        logger.warning(f"save_analysis failed: {e}")
        return False
