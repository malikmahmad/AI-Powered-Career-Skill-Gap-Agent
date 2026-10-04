"""
Unit tests for src/services/gap_engine.py

Run with:  python -m pytest tests/test_gap_engine.py -v
No API key required — pure Python math, no external dependencies.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.gap_engine import calculate_market_frequencies, analyze_gaps


# ── calculate_market_frequencies ─────────────────────────────────────────────

class TestCalculateMarketFrequencies:

    def test_basic_frequency_calculation(self):
        jd_analyses = [
            {"jd_index": 1, "skills": ["Python", "React", "Docker"]},
            {"jd_index": 2, "skills": ["Python", "Docker", "AWS"]},
            {"jd_index": 3, "skills": ["Python", "React", "TypeScript"]},
        ]
        freq = calculate_market_frequencies(jd_analyses)
        assert freq["Python"] == 100.0
        assert abs(freq["React"]  - round(2/3*100, 1)) < 0.01
        assert abs(freq["Docker"] - round(2/3*100, 1)) < 0.01
        assert abs(freq["AWS"]    - round(1/3*100, 1)) < 0.01

    def test_empty_input_returns_empty_dict(self):
        assert calculate_market_frequencies([]) == {}

    def test_single_jd_all_100_percent(self):
        jd_analyses = [{"jd_index": 1, "skills": ["Python", "Git"]}]
        freq = calculate_market_frequencies(jd_analyses)
        assert freq["Python"] == 100.0
        assert freq["Git"]    == 100.0

    def test_deduplication_within_single_jd(self):
        """A skill listed twice in one JD should only count once."""
        jd_analyses = [
            {"jd_index": 1, "skills": ["Python", "Python", "React"]},
            {"jd_index": 2, "skills": ["React"]},
        ]
        freq = calculate_market_frequencies(jd_analyses)
        assert freq["Python"] == 50.0   # 1/2 JDs, not 2/2
        assert freq["React"]  == 100.0  # 2/2 JDs

    def test_missing_skills_key_handled_gracefully(self):
        jd_analyses = [{"jd_index": 1}, {"jd_index": 2, "skills": ["Python"]}]
        freq = calculate_market_frequencies(jd_analyses)
        assert "Python" in freq

    def test_frequency_rounded_to_one_decimal(self):
        jd_analyses = [{"jd_index": i, "skills": ["X"]} for i in range(3)]
        jd_analyses.append({"jd_index": 4, "skills": []})
        freq = calculate_market_frequencies(jd_analyses)
        val = freq.get("X", 0)
        assert val == round(val, 1)


# ── analyze_gaps ─────────────────────────────────────────────────────────────

class TestAnalyzeGaps:

    def _sample_candidate(self):
        return [
            {"name": "Python",     "evidence_level": 2, "category": "Languages", "justification": "5 projects"},
            {"name": "React",      "evidence_level": 1, "category": "Frameworks", "justification": "listed only"},
            {"name": "Git",        "evidence_level": 2, "category": "Tools",      "justification": "all projects"},
        ]

    def _sample_freq(self):
        return {"Python": 100.0, "React": 66.7, "Docker": 66.7, "Git": 66.7, "AWS": 33.3}

    def test_result_has_required_keys(self):
        result = analyze_gaps(self._sample_candidate(), self._sample_freq())
        assert "readiness_score" in result
        assert "gap_matrix" in result

    def test_readiness_score_in_valid_range(self):
        result = analyze_gaps(self._sample_candidate(), self._sample_freq())
        assert 0 <= result["readiness_score"] <= 100

    def test_gap_matrix_rows_have_required_keys(self):
        result = analyze_gaps(self._sample_candidate(), self._sample_freq())
        required = {"skill", "frequency", "evidence_level", "is_high_priority", "category", "justification"}
        for row in result["gap_matrix"]:
            assert required.issubset(set(row.keys())), f"Missing keys in row: {row}"

    def test_matrix_sorted_by_frequency_descending(self):
        result = analyze_gaps(self._sample_candidate(), self._sample_freq())
        freqs = [r["frequency"] for r in result["gap_matrix"]]
        assert freqs == sorted(freqs, reverse=True)

    def test_missing_skill_has_evidence_level_zero(self):
        result = analyze_gaps(self._sample_candidate(), self._sample_freq())
        docker = next(r for r in result["gap_matrix"] if r["skill"] == "Docker")
        assert docker["evidence_level"] == 0

    def test_high_priority_logic_correct(self):
        result = analyze_gaps(self._sample_candidate(), self._sample_freq())
        for row in result["gap_matrix"]:
            expected = row["frequency"] >= 50.0 and row["evidence_level"] < 2
            assert row["is_high_priority"] == expected, f"Wrong HP flag for {row['skill']}"

    def test_readiness_score_formula(self):
        result = analyze_gaps(self._sample_candidate(), self._sample_freq())
        matrix = result["gap_matrix"]
        total  = sum(r["frequency"] * 2 for r in matrix)
        earned = sum(r["frequency"] * r["evidence_level"] for r in matrix)
        expected = round(earned / total * 100) if total > 0 else 0
        assert result["readiness_score"] == expected

    def test_empty_candidate_all_missing(self):
        result = analyze_gaps([], {"Python": 100.0, "Docker": 80.0})
        assert result["readiness_score"] == 0
        for row in result["gap_matrix"]:
            assert row["evidence_level"] == 0

    def test_empty_market_returns_zero_score(self):
        result = analyze_gaps(self._sample_candidate(), {})
        assert result["readiness_score"] == 0
        assert result["gap_matrix"] == []

    def test_case_insensitive_matching(self):
        """Gemini may return 'postgresql' vs 'PostgreSQL' — should still match."""
        candidate = [{"name": "PostgreSQL", "evidence_level": 2, "category": "DB", "justification": "used"}]
        market    = {"postgresql": 100.0}
        result    = analyze_gaps(candidate, market)
        assert result["gap_matrix"][0]["evidence_level"] == 2

    def test_perfect_score_when_all_demonstrated(self):
        candidate = [
            {"name": "Python", "evidence_level": 2, "category": "L", "justification": "x"},
            {"name": "Docker", "evidence_level": 2, "category": "T", "justification": "x"},
        ]
        market = {"Python": 100.0, "Docker": 100.0}
        result = analyze_gaps(candidate, market)
        assert result["readiness_score"] == 100

    def test_score_uses_round_not_int(self):
        """round(73.9) == 74, int(73.9) == 73 — we want 74."""
        # 1 skill at 100% market demand, evidence_level=1 → earned=100, total=200 → 50.0 exactly
        # Use a case that would differ: earned=149, total=200 → 74.5 → round=75, int=74
        candidate = [
            {"name": "Python", "evidence_level": 2, "category": "L", "justification": "x"},
            {"name": "React",  "evidence_level": 1, "category": "F", "justification": "x"},
        ]
        market = {"Python": 100.0, "React": 49.0}
        result = analyze_gaps(candidate, market)
        # Verify it equals round(), not int()
        matrix = result["gap_matrix"]
        total  = sum(r["frequency"] * 2 for r in matrix)
        earned = sum(r["frequency"] * r["evidence_level"] for r in matrix)
        assert result["readiness_score"] == round(earned / total * 100)
