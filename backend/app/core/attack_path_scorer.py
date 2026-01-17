def score_attack_path(attack_steps, jewel_impacts):
    if not jewel_impacts:
        return {
            "path_score": 0,
            "reason": "No crown jewel reached"
        }

    # Likelihood = % of steps succeeded
    success_steps = len([s for s in attack_steps if s.success])
    total_steps = len(attack_steps)
    likelihood = int((success_steps / total_steps) * 100)

    # Impact = max jewel impact reached
    impact = max(j["impact_score"] for j in jewel_impacts)

    # Final score (simple, explainable)
    path_score = int((likelihood * impact) / 100)

    return {
        "likelihood": likelihood,
        "impact": impact,
        "path_score": path_score
    }
