import yaml
from app.models.attack_chain import AttackChain, AttackStep, AttackTechnique


def load_attack_chain(path: str) -> AttackChain:
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    steps = []
    for step in data["steps"]:
        tech = step["technique"]

        technique = AttackTechnique(
            technique_id=tech["technique_id"],
            name=tech["name"],
            description=tech.get("description", ""),
            stage=tech["stage"],
            required_conditions=tech.get("required_conditions", []),
            success_effects=tech.get("success_effects", []),
            crown_jewels=tech.get("crown_jewels", [])
        )

        steps.append(
            AttackStep(
                step_id=step["step_id"],
                target_asset_type=step["target_asset_type"],
                technique=technique
            )
        )

    return AttackChain(
        chain_id=data["chain_id"],
        name=data["name"],
        steps=steps
    )
