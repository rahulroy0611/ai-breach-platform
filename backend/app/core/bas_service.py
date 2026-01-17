from pathlib import Path
from app.core.bas_simulator import simulate_attack
from app.core.bas_dsl_loader import load_attack_chain
from app.core.crown_jewel_evaluator import evaluate_crown_jewel_impact
from app.core.crown_jewel_registry import CROWN_JEWELS
from app.core.attack_path_scorer import score_attack_path


BASE_DIR = Path(__file__).resolve().parent.parent
ATTACK_CHAIN_DIR = BASE_DIR / "attack_chains"


def run_bas_simulation(chain_name: str, assets: list):
    chain_file = ATTACK_CHAIN_DIR / chain_name

    if not chain_file.exists():
        raise FileNotFoundError(
            f"Attack chain not found: {chain_file}. "
            f"Available: {[p.name for p in ATTACK_CHAIN_DIR.glob('*.yaml')]}"
        )

    chain = load_attack_chain(str(chain_file))

    attack_steps = simulate_attack(chain, assets)
    jewel_impacts = evaluate_crown_jewel_impact(attack_steps, CROWN_JEWELS)
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
