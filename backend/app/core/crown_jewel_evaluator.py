from typing import List
from app.models.attack_chain import AttackStep
from app.core.crown_jewel_registry import CROWN_JEWELS

def evaluate_crown_jewel_impact(attack_steps: List[AttackStep]):
    impacts = []

    for step in attack_steps:
        if not step.success:
            break

        for jewel in CROWN_JEWELS:
            if step.target_asset_type == jewel.asset_type:
                impacts.append({
                    "jewel_id": jewel.jewel_id,
                    "jewel_name": jewel.name,
                    "impact_score": jewel.impact_score,
                    "reached_via_step": step.step_id
                })

    return impacts
