from typing import List
from app.models.asset import Asset
from app.core.bas_simulator import simulate_attack
from app.core.bas_dsl_loader import load_attack_chain
from app.core.crown_jewel_evaluator import evaluate_crown_jewel_impact
from app.core.attack_path_scorer import score_attack_path

def run_bas_simulation(chain_path: str, assets: list):
    chain = load_attack_chain(chain_path)
    attack_steps = simulate_attack(chain, assets)

    jewel_impacts = evaluate_crown_jewel_impact(attack_steps)
    scoring = score_attack_path(attack_steps, jewel_impacts)

    return {
        "chain_id": chain.chain_id,
        "chain_name": chain.name,
        "attack_path": [
            {
                "step_id": s.step_id,
                "technique": s.technique.name,
                "stage": s.technique.stage,
                "success": s.success,
                "outcome": s.outcome,
                "failed_conditions": s.failed_conditions
            }
            for s in attack_steps
        ],
        "crown_jewels_reached": jewel_impacts,
        "attack_path_score": scoring
    }