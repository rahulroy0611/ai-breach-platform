from typing import Dict, List
from app.models.evidence import Evidence

EVIDENCE_STORE: Dict[str, List[Evidence]] = {}

def add_evidence(evidence: Evidence):
    evs = EVIDENCE_STORE.setdefault(evidence.asset_id, [])

    for e in evs:
        if (
            e.type == evidence.type
            and e.observed_value == evidence.observed_value
            and e.source == evidence.source
        ):
            # Update existing evidence instead of duplicating
            e.last_seen = evidence.last_seen
            e.is_active = True
            return

    evs.append(evidence)

def get_evidence_for_asset(asset_id: str) -> List[Evidence]:
    return EVIDENCE_STORE.get(asset_id, [])

def get_evidence_by_type(asset_id: str, evidence_type: str) -> List[Evidence]:
    return [
        e for e in EVIDENCE_STORE.get(asset_id, [])
        if e.type == evidence_type and e.is_active
    ]

def get_evidence_by_type_and_confidence(
    asset_id: str,
    evidence_type: str,
    min_confidence: str
) -> List[Evidence]:

    confidence_order = {"low": 1, "medium": 2, "high": 3}

    return [
        e for e in EVIDENCE_STORE.get(asset_id, [])
        if (
            e.type == evidence_type
            and e.is_active
            and confidence_order[e.confidence] >= confidence_order[min_confidence]
        )
    ]

def summarize_evidence_strength(evidences: List[Evidence]) -> str:
    order = {"weak": 1, "moderate": 2, "strong": 3}
    if not evidences:
        return "weak"
    strongest = max(evidences, key=lambda e: order[e.strength])
    return strongest.strength
