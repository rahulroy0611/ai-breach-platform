from typing import List
from app.models.asset import Asset
from app.models.attack_chain import AttackChain
from app.core.evidence_store import (
    get_evidence_by_type_and_confidence,
    summarize_evidence_strength
)

print("🔥 EVIDENCE-DRIVEN BAS SIMULATOR LOADED")


def simulate_attack(chain: AttackChain, assets: List[Asset]):
    """
    Evidence-driven BAS simulation.
    A step succeeds ONLY if required evidence exists.
    """
    results = []

    for step in chain.steps:
        step.success = False
        step.evidence_used = []
        step.failed_conditions = []
        step.confidence = None

        # 1️⃣ Find matching assets by target_asset_type
        matching_assets = [
            a for a in assets if a.asset_type == step.target_asset_type
        ]

        if not matching_assets:
            step.outcome = f"No asset of type '{step.target_asset_type}' found"
            results.append(step)
            break

        # Deterministic selection (first match)
        asset = matching_assets[0]

        evidence_used = []
        failed_conditions = []

        # 2️⃣ Evaluate REQUIRED CONDITIONS via evidence
        for cond in step.technique.required_conditions:
            evidence_type = cond["evidence_type"]
            min_confidence = cond.get("min_confidence", "low")

            evs = get_evidence_by_type_and_confidence(
                asset.asset_id,
                evidence_type,
                min_confidence
            )

            if not evs:
                failed_conditions.append(
                    f"{evidence_type} (min_confidence={min_confidence})"
                )
            else:
                evidence_used.extend([e.evidence_id for e in evs])

        # 3️⃣ Fail step if any evidence missing
        if failed_conditions:
            step.success = False
            step.failed_conditions = failed_conditions
            step.outcome = (
                "Attack step blocked due to missing evidence: "
                + ", ".join(failed_conditions)
            )
            results.append(step)
            break

        # 4️⃣ Success path
        step.success = True
        step.evidence_used = list(set(evidence_used))

        step.confidence = summarize_evidence_strength(
            get_evidence_by_type_and_confidence(
                asset.asset_id,
                step.technique.required_conditions[0]["evidence_type"],
                "low"
            )
        )

        step.outcome = (
            "Attack step succeeded based on evidence: "
            + ", ".join(step.evidence_used)
        )

        results.append(step)

    return results
