from app.models.attack_stage import AttackStage

ALLOWED_ASSET_TYPES = {
    "ip", "domain", "api", "internal_service", "ai_model", "service"
}

def validate_attack_chain(data: dict):
    if "steps" not in data:
        raise ValueError("Attack chain must define steps")

    for step in data["steps"]:
        if "step_id" not in step:
            raise ValueError("Each step must have step_id")

        if "technique" not in step:
            raise ValueError(f"Step {step.get('step_id')} missing technique")

        tech = step["technique"]

        required_fields = [
            "technique_id",
            "name",
            "stage",
            "required_conditions",
            "success_effects",
        ]

        for field in required_fields:
            if field not in tech:
                raise ValueError(
                    f"Technique {tech.get('name')} missing field: {field}"
                )
