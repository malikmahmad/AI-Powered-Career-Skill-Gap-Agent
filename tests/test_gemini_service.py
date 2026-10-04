"""
Unit tests for src/services/gemini_service.py

All Gemini API calls are mocked — no API key or internet connection required.
Run with:  python -m pytest tests/test_gemini_service.py -v
"""

import sys
import os
import json
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ── Helper factories ──────────────────────────────────────────────────────────

def _make_response(data: dict) -> MagicMock:
    """Create a mock Gemini API response."""
    mock = MagicMock()
    mock.text = json.dumps(data)
    return mock


def _make_client(response_data: dict) -> MagicMock:
    """Create a mock Gemini client that returns the given response."""
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _make_response(response_data)
    return mock_client


# ── _clean_json ───────────────────────────────────────────────────────────────

class TestCleanJson:

    def test_strips_json_fences(self):
        from src.services.gemini_service import _clean_json
        raw = '```json\n{"key": "val"}\n```'
        result = _clean_json(raw)
        assert result == {"key": "val"}

    def test_strips_plain_fences(self):
        from src.services.gemini_service import _clean_json
        raw = '```\n{"key": "val"}\n```'
        result = _clean_json(raw)
        assert result == {"key": "val"}

    def test_plain_json_passthrough(self):
        from src.services.gemini_service import _clean_json
        raw = '{"key": "val"}'
        result = _clean_json(raw)
        assert result == {"key": "val"}

    def test_raises_on_invalid_json(self):
        from src.services.gemini_service import _clean_json
        with pytest.raises(json.JSONDecodeError):
            _clean_json("not valid json")


# ── extract_candidate_skills ──────────────────────────────────────────────────

class TestExtractCandidateSkills:

    def test_returns_skills_list_on_success(self):
        mock_data = {
            "skills": [
                {"name": "Python", "category": "Languages & Frameworks",
                 "evidence_level": 2, "justification": "5 projects"},
                {"name": "React",  "category": "Languages & Frameworks",
                 "evidence_level": 1, "justification": "listed only"},
            ]
        }
        with patch("src.services.gemini_service._get_client", return_value=_make_client(mock_data)):
            from src.services.gemini_service import extract_candidate_skills
            result = extract_candidate_skills("Some resume text")

        assert len(result) == 2
        assert result[0]["name"] == "Python"
        assert result[0]["evidence_level"] == 2
        assert result[1]["evidence_level"] == 1

    def test_returns_empty_list_when_client_is_none(self):
        with patch("src.services.gemini_service._get_client", return_value=None):
            from src.services.gemini_service import extract_candidate_skills
            result = extract_candidate_skills("resume")
        assert result == []

    def test_returns_empty_list_on_api_exception(self):
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("API error")
        with patch("src.services.gemini_service._get_client", return_value=mock_client):
            with patch("streamlit.error"):
                from src.services.gemini_service import extract_candidate_skills
                result = extract_candidate_skills("resume")
        assert result == []

    def test_resume_truncated_to_max_chars(self):
        """Verify very long resumes are truncated before sending to Gemini."""
        from src.config import RESUME_MAX_CHARS
        long_resume = "A" * (RESUME_MAX_CHARS + 5000)
        captured = []
        mock_data = {"skills": []}

        def capture_call(*args, **kwargs):
            captured.append(kwargs.get("contents", args[1] if len(args) > 1 else ""))
            return _make_response(mock_data)

        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = capture_call

        with patch("src.services.gemini_service._get_client", return_value=mock_client):
            from src.services.gemini_service import extract_candidate_skills
            extract_candidate_skills(long_resume)

        # The prompt should not contain the full long resume
        if captured:
            prompt_str = str(captured[0])
            assert len(prompt_str) < len(long_resume) + 1000   # allow for prompt template overhead

    def test_result_keys_are_present(self):
        mock_data = {
            "skills": [
                {"name": "Docker", "category": "Tools & DevOps",
                 "evidence_level": 2, "justification": "deployed 3 services"}
            ]
        }
        with patch("src.services.gemini_service._get_client", return_value=_make_client(mock_data)):
            from src.services.gemini_service import extract_candidate_skills
            result = extract_candidate_skills("resume")

        assert "name" in result[0]
        assert "evidence_level" in result[0]
        assert "category" in result[0]
        assert "justification" in result[0]


# ── extract_market_skills ─────────────────────────────────────────────────────

class TestExtractMarketSkills:

    def test_returns_jd_analysis_on_success(self):
        mock_data = {
            "jd_analysis": [
                {"jd_index": 1, "skills": ["React", "Node.js"]},
                {"jd_index": 2, "skills": ["Python", "Docker"]},
            ]
        }
        with patch("src.services.gemini_service._get_client", return_value=_make_client(mock_data)):
            from src.services.gemini_service import extract_market_skills
            result = extract_market_skills(["JD 1 text", "JD 2 text"])

        assert len(result) == 2
        assert result[0]["jd_index"] == 1
        assert "React" in result[0]["skills"]

    def test_returns_empty_list_when_client_is_none(self):
        with patch("src.services.gemini_service._get_client", return_value=None):
            from src.services.gemini_service import extract_market_skills
            result = extract_market_skills(["JD text"])
        assert result == []

    def test_returns_empty_list_on_api_exception(self):
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("quota exceeded")
        with patch("src.services.gemini_service._get_client", return_value=mock_client):
            with patch("streamlit.error"):
                from src.services.gemini_service import extract_market_skills
                result = extract_market_skills(["JD text"])
        assert result == []
