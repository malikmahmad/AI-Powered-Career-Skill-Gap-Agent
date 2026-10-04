"""
Unit tests for src/services/export_service.py

Run with:  python -m pytest tests/test_export_service.py -v
"""

import sys
import os
import csv
import io
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.export_service import gap_matrix_to_csv


SAMPLE_MATRIX = [
    {
        "skill": "Python", "frequency": 100.0, "evidence_level": 2,
        "is_high_priority": False, "category": "Languages & Frameworks",
        "justification": "Used in 5 projects"
    },
    {
        "skill": "Docker", "frequency": 66.7, "evidence_level": 0,
        "is_high_priority": True, "category": "Tools & DevOps",
        "justification": "Missing from profile"
    },
    {
        "skill": "React", "frequency": 66.7, "evidence_level": 1,
        "is_high_priority": True, "category": "Languages & Frameworks",
        "justification": "Listed only"
    },
]


class TestGapMatrixToCsv:

    def test_returns_string(self):
        result = gap_matrix_to_csv(SAMPLE_MATRIX)
        assert isinstance(result, str)

    def test_csv_has_header_row(self):
        result = gap_matrix_to_csv(SAMPLE_MATRIX)
        reader = csv.DictReader(io.StringIO(result))
        assert reader.fieldnames is not None
        assert "Skill" in reader.fieldnames
        assert "Status" in reader.fieldnames
        assert "Market %" in reader.fieldnames

    def test_csv_has_correct_row_count(self):
        result = gap_matrix_to_csv(SAMPLE_MATRIX)
        reader = csv.DictReader(io.StringIO(result))
        rows = list(reader)
        assert len(rows) == len(SAMPLE_MATRIX)

    def test_status_mapped_correctly(self):
        result = gap_matrix_to_csv(SAMPLE_MATRIX)
        reader = csv.DictReader(io.StringIO(result))
        rows = {r["Skill"]: r for r in reader}
        assert rows["Python"]["Status"] == "Demonstrated"
        assert rows["Docker"]["Status"] == "Missing"
        assert rows["React"]["Status"]  == "Theoretical"

    def test_market_percent_formatted(self):
        result = gap_matrix_to_csv(SAMPLE_MATRIX)
        reader = csv.DictReader(io.StringIO(result))
        rows = {r["Skill"]: r for r in reader}
        assert rows["Python"]["Market %"] == "100.0%"
        assert rows["Docker"]["Market %"] == "66.7%"

    def test_priority_flag_formatted(self):
        result = gap_matrix_to_csv(SAMPLE_MATRIX)
        reader = csv.DictReader(io.StringIO(result))
        rows = {r["Skill"]: r for r in reader}
        assert rows["Python"]["Priority"] == "No"
        assert rows["Docker"]["Priority"] == "Yes"

    def test_empty_matrix_returns_header_only(self):
        result = gap_matrix_to_csv([])
        reader = csv.DictReader(io.StringIO(result))
        rows = list(reader)
        assert len(rows) == 0
        assert reader.fieldnames is not None

    def test_csv_is_valid_and_parseable(self):
        result = gap_matrix_to_csv(SAMPLE_MATRIX)
        try:
            reader = csv.DictReader(io.StringIO(result))
            list(reader)   # consume all rows without error
        except Exception as e:
            pytest.fail(f"CSV parsing failed: {e}")
