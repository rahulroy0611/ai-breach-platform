from app.models.attack_stage import AttackStage

ALLOWED_ASSET_TYPES = {
    "ip", "domain", "api", "internal_service", "ai_model", "service"
}

def validate_attack_chain(data: dict):
    if "steps" not in data or not data["steps"]:
        if not step["technique"]["required_conditions"]:
            raise ValueError("Service-level BAS step must require evidence")

    for step in data["steps"]:
        tech = step.get("technique", {})

        if "name" not in tech:
            raise ValueError("Technique must have a name")

        if "stage" not in tech:
            raise ValueError("Technique must have a stage")

        if step["target_asset_type"] not in ALLOWED_ASSET_TYPES:
            raise ValueError(f"Invalid asset type: {step['target_asset_type']}")

        if tech["stage"] not in [s.value for s in AttackStage]:
            raise ValueError(f"Invalid attack stage: {tech['stage']}")

        if not tech.get("required_conditions"):
            raise ValueError("required_conditions cannot be empty")
