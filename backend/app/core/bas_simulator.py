from typing import List
from app.models.asset import Asset
from app.models.attack_chain import AttackChain
from app.core.evidence_store import get_evidence_by_type


def has_evidence(asset_id: str, evidence_type: str) -> bool:
    return len(get_evidence_by_type(asset_id, evidence_type)) > 0

def get_evidence_ids_for_conditions(asset, conditions: list) -> list:
    """
    Collect evidence IDs that satisfy evidence-based conditions.
    """
    evidence_ids = []
    for cond in conditions:
        if isinstance(cond, dict) and cond.get("requires_evidence"):
            evidence_type = cond["requires_evidence"]
            evidence = get_evidence_by_type(asset.asset_id, evidence_type)
            evidence_ids.extend([e.evidence_id for e in evidence])
    return evidence_ids

def asset_matches_conditions(asset, conditions: list) -> tuple[bool, list]:
    """
    Evaluate DSL required_conditions against an asset.
    Returns (success, failed_conditions)
    """
    failed = []

    for cond in conditions:
        if isinstance(cond, dict):
            if cond.get("asset_type") and asset.asset_type != cond["asset_type"]:
                failed.append(f"asset_type != {cond['asset_type']}")

            if cond.get("requires_evidence") and not has_evidence(asset.asset_id, cond["requires_evidence"]):
                failed.append(f"missing_evidence:{cond['requires_evidence']}")
        else:
            # Simple string tag match
            if cond not in asset.risk_tags:
                failed.append(f"missing_tag:{cond}")

    return len(failed) == 0, failed

def simulate_attack(chain: AttackChain, assets: list[Asset]):
    results = []

    for step in chain.steps:
        step_succeeded = False

        # Try ALL assets, not just first
        for asset in assets:
            success, failed_conditions = asset_matches_conditions(
                asset,
                step.technique.required_conditions
            )

            if success:
                step.success = True
                
                # Collect evidence IDs used to satisfy conditions
                evidence_ids = get_evidence_ids_for_conditions(asset, step.technique.required_conditions)
                
                # Build outcome with evidence IDs if available
                if evidence_ids:
                    step.outcome = "Attack step succeeded based on evidence: " + ", ".join(evidence_ids)
                else:
                    step.outcome = "Technique conditions satisfied"
                
                step.failed_conditions = []
                step_succeeded = True

                # Apply success effects
                for effect in step.technique.success_effects:
                    if effect not in asset.risk_tags:
                        asset.risk_tags.append(effect)

                results.append(step)
                break   # one successful asset is enough

        if not step_succeeded:
            step.success = False
            step.outcome = "No asset satisfied required conditions"
            step.failed_conditions = [
                str(cond) for cond in step.technique.required_conditions
            ]
            results.append(step)

    return results
