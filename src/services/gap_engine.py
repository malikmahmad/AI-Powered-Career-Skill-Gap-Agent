def calculate_market_frequencies(jd_analyses):
    """
    Given a list of jd analysis dicts, calculate the appearance frequency of each skill.
    """
    total_jds = len(jd_analyses)
    if total_jds == 0:
         return {}
         
    skill_counts = {}
    for jd in jd_analyses:
        for skill in set(jd.get("skills", [])):  # Use set to avoid double counting per JD if there are duplicates
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
            
    frequencies = {s: round((count / total_jds) * 100, 1) for s, count in skill_counts.items()}
    return frequencies

def analyze_gaps(candidate_skills, market_frequencies):
    """
    Compares candidate skills with market frequencies to create a gap matrix.
    candidate_skills: list of dicts [{"name": "React", "evidence_level": 2, "category": "...", "justification": "..."}]
    market_frequencies: dict {"React": 100.0, "Docker": 60.0}
    """
    # Create a lower-case map for fuzzy matching
    cand_skill_map = {s["name"].lower(): s for s in candidate_skills}
    
    matrix = []
    total_market_points = 0
    earned_points = 0
    
    for market_skill, freq in market_frequencies.items():
        market_skill_lower = market_skill.lower()
        cand_skill = cand_skill_map.get(market_skill_lower)
        
        evidence_level = cand_skill["evidence_level"] if cand_skill else 0
        
        # Priority logic: High if frequency >= 50% and evidence < 2
        is_high_priority = (freq >= 50.0) and (evidence_level < 2)
        
        # Readiness Calculation Logic
        total_market_points += freq * 2  # Max evidence level is 2
        earned_points += freq * evidence_level
        
        matrix.append({
            "skill": market_skill,
            "frequency": freq,
            "evidence_level": evidence_level,
            "is_high_priority": is_high_priority,
            "category": cand_skill.get("category", "Uncategorized") if cand_skill else "Uncategorized",
            "justification": cand_skill.get("justification", "Missing from profile") if cand_skill else "Missing from profile"
        })
        
    readiness_score = round((earned_points / total_market_points * 100)) if total_market_points > 0 else 0
    
    # Sort matrix by frequency descending
    matrix = sorted(matrix, key=lambda x: x["frequency"], reverse=True)
    
    return {
        "readiness_score": readiness_score,
        "gap_matrix": matrix
    }
