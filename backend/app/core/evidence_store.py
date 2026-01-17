from typing import Dict, List
from app.models.evidence import Evidence
from datetime import datetime, timedelta

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


# ========== ENHANCEMENT: Deduplication helpers ==========

def get_evidence_by_key(asset_id: str, evidence_type: str, observed_value) -> List[Evidence]:
    """
    Get evidence matching (asset_id, type, observed_value) key.
    Useful for deduplication across different sources.
    """
    return [
        e for e in EVIDENCE_STORE.get(asset_id, [])
        if e.type == evidence_type and e.observed_value == observed_value and e.is_active
    ]


# ========== ENHANCEMENT: Evidence expiration ==========

def expire_old_evidence(asset_id: str, days: int = 30) -> int:
    """
    Mark evidence older than N days as inactive.
    Returns count of expired evidence.
    Note: Does not delete, only marks is_active=False.
    """
    evs = EVIDENCE_STORE.get(asset_id, [])
    if not evs:
        return 0
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    expired_count = 0
    
    for e in evs:
        if e.is_active and e.first_seen < cutoff:
            e.is_active = False
            expired_count += 1
    
    return expired_count


def expire_all_old_evidence(days: int = 30) -> int:
    """
    Mark evidence older than N days as inactive across all assets.
    Returns total count of expired evidence.
    """
    total_expired = 0
    for asset_id in EVIDENCE_STORE.keys():
        total_expired += expire_old_evidence(asset_id, days)
    return total_expired


# ========== ENHANCEMENT: Evidence summary ==========

def summarize_evidence_store(asset_id: str = None) -> Dict:
    """
    Return summary of evidence grouped by type and confidence.
    
    If asset_id provided: Summary for that asset.
    If asset_id None: Summary across all assets.
    
    Returns:
    {
        "total_active": int,
        "total_inactive": int,
        "by_type": {
            "http_service_detected": {"active": 2, "inactive": 0},
            ...
        },
        "by_confidence": {
            "high": {"active": 3, "inactive": 1},
            ...
        }
    }
    """
    summary = {
        "total_active": 0,
        "total_inactive": 0,
        "by_type": {},
        "by_confidence": {}
    }
    
    # Collect evidence
    if asset_id:
        evidences = EVIDENCE_STORE.get(asset_id, [])
    else:
        evidences = []
        for evs in EVIDENCE_STORE.values():
            evidences.extend(evs)
    
    # Count by status
    for e in evidences:
        if e.is_active:
            summary["total_active"] += 1
        else:
            summary["total_inactive"] += 1
        
        # Group by type
        if e.type not in summary["by_type"]:
            summary["by_type"][e.type] = {"active": 0, "inactive": 0}
        
        if e.is_active:
            summary["by_type"][e.type]["active"] += 1
        else:
            summary["by_type"][e.type]["inactive"] += 1
        
        # Group by confidence
        if e.confidence not in summary["by_confidence"]:
            summary["by_confidence"][e.confidence] = {"active": 0, "inactive": 0}
        
        if e.is_active:
            summary["by_confidence"][e.confidence]["active"] += 1
        else:
            summary["by_confidence"][e.confidence]["inactive"] += 1
    
    return summary
