"""
Export service — converts analysis results to downloadable formats.
Currently supports CSV. Extend here for PDF or Excel in future.
"""

import csv
import io
from src.config import EVIDENCE_LABELS, CSV_COLUMNS


def gap_matrix_to_csv(gap_matrix: list) -> str:
    """
    Converts a gap matrix to a UTF-8 CSV string suitable for st.download_button.

    Args:
        gap_matrix: List of gap dicts from analyze_gaps()["gap_matrix"].

    Returns:
        CSV string with columns: Skill, Status, Market %, Category, Evidence, Priority
    """
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_COLUMNS)
    writer.writeheader()

    for row in gap_matrix:
        writer.writerow({
            "Skill":    row.get("skill", ""),
            "Status":   EVIDENCE_LABELS.get(row.get("evidence_level", 0), "Unknown"),
            "Market %": f"{row.get('frequency', 0)}%",
            "Category": row.get("category", ""),
            "Evidence": row.get("justification", ""),
            "Priority": "Yes" if row.get("is_high_priority") else "No",
        })

    return output.getvalue()
