import yaml
from pathlib import Path
from app.models.attack_chain import AttackChain
from app.models.attack_technique import AttackTechnique
from app.models.attack_stage import AttackStage
from app.core.bas_dsl_validator import validate_attack_chain

BASE_DIR = Path(__file__).resolve().parents[1]  # /app

def load_attack_chain(relative_path: str) -> AttackChain:
    full_path = BASE_DIR / relative_path

    if not full_path.exists():
        raise FileNotFoundError(f"Attack chain not found: {full_path}")

    with open(full_path, "r") as f:
        data = yaml.safe_load(f)
        validate_attack_chain(data)

    steps = []
    for step in data["steps"]:
        tech = step["technique"]

        technique = AttackTechnique(
            technique_id=tech.get(
                "technique_id",
                tech["name"].lower().replace(" ", "_")
            ),
            name=tech["name"],
            stage=tech["stage"],
            description=tech.get(
                "description",
                f"Attack technique: {tech['name']}"
            ),
            required_conditions=tech.get("required_conditions", []),
            success_effects=tech.get("success_effects", []),
        )

        steps.append({
            "step_id": step["step_id"],
            "technique": technique,
            "target_asset_type": step["target_asset_type"],
        })

    return AttackChain(
        chain_id=data["chain_id"],
        name=data["name"],
        steps=steps,
    )
