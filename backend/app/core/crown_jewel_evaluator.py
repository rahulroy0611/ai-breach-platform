from typing import List
from app.models.attack_chain import AttackStep
from app.models.crown_jewel import CrownJewel


def evaluate_crown_jewel_impact(
    attack_steps: List[AttackStep],
    crown_jewels: List[CrownJewel]
):
    """
    Crown jewels are reached ONLY if attack steps succeed
    AND the technique stage is lateral_movement or exfiltration.
    """
    reached = []

    if not any(step.success for step in attack_steps):
        return []

    for jewel in crown_jewels:
        for step in attack_steps:
            if not step.success:
                continue

            # GATE: Only lateral_movement and exfiltration can reach crown jewels
            if step.technique.stage not in ["lateral_movement", "exfiltration"]:
                continue

            # Minimal v1 logic (safe)
            reached.append({
                "jewel_id": jewel.jewel_id,
                "jewel_name": jewel.name,
                "impact_score": jewel.impact_score,
                "reached_via_step": step.step_id
            })
            break

    return reached
