from uuid import uuid4
from datetime import datetime
from app.models.evidence import Evidence

CONFIDENCE = {"low", "medium", "high"}
STRENGTH = {"weak", "moderate", "strong"}

def create_evidence(
    *,
    asset_id: str,
    category: str,
    type: str,
    source: str,
    confidence: str,
    strength: str,
    observed_value=None,
    raw_proof=None,
) -> Evidence:

    if confidence not in CONFIDENCE:
        raise ValueError(f"Invalid confidence: {confidence}")

    if strength not in STRENGTH:
        raise ValueError(f"Invalid strength: {strength}")

    now = datetime.utcnow()

    return Evidence(
        evidence_id=str(uuid4()),
        asset_id=asset_id,
        category=category,
        type=type,
        source=source,
        confidence=confidence,
        strength=strength,
        observed_value=observed_value,
        raw_proof=raw_proof,
        first_seen=now,
        last_seen=now,
    )
