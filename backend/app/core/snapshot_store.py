from typing import Dict, List, Optional
from app.models.asset_snapshot import AssetSnapshot
import hashlib
import json

ASSET_SNAPSHOTS: Dict[str, List[AssetSnapshot]] = {}
SNAPSHOT_HASHES: Dict[str, str] = {}  # snapshot_id -> hash (integrity tracking)


def compute_snapshot_hash(snapshot: AssetSnapshot) -> str:
    """
    Compute deterministic hash of snapshot for integrity verification.
    Used for immutability validation and replay consistency.
    """
    # Create deterministic JSON representation
    snapshot_dict = {
        "target": snapshot.target,
        "assets_count": len(snapshot.assets),
        "created_at": snapshot.created_at.isoformat(),
        "snapshot_version": snapshot.snapshot_version,
    }
    snapshot_json = json.dumps(snapshot_dict, sort_keys=True)
    return hashlib.sha256(snapshot_json.encode()).hexdigest()


def store_asset_snapshot(snapshot: AssetSnapshot, job_id: Optional[str] = None):
    """
    Store an immutable snapshot with versioning.
    Each scan of same target gets a new version number.
    """
    # Set immutability flag
    snapshot.is_immutable = True
    
    # Link to originating job
    if job_id:
        snapshot.scan_job_id = job_id
    
    # Get or initialize snapshots for this target
    if snapshot.target not in ASSET_SNAPSHOTS:
        ASSET_SNAPSHOTS[snapshot.target] = []
    
    existing_snapshots = ASSET_SNAPSHOTS[snapshot.target]
    
    # Auto-increment version number
    snapshot.snapshot_version = len(existing_snapshots) + 1
    
    # Link to previous snapshot for diffs
    if existing_snapshots:
        snapshot.previous_snapshot_id = existing_snapshots[-1].snapshot_id
    
    # Compute and store hash
    snapshot_hash = compute_snapshot_hash(snapshot)
    snapshot.hash = snapshot_hash
    SNAPSHOT_HASHES[snapshot.snapshot_id] = snapshot_hash
    
    # Store immutable snapshot
    existing_snapshots.append(snapshot)


def get_asset_snapshots(target: str) -> List[AssetSnapshot]:
    """Get all snapshots for a target in version order"""
    return ASSET_SNAPSHOTS.get(target, [])


def get_latest_snapshot(target: str) -> Optional[AssetSnapshot]:
    """Get most recent snapshot for a target"""
    snapshots = get_asset_snapshots(target)
    return snapshots[-1] if snapshots else None


def get_snapshot_by_version(target: str, version: int) -> Optional[AssetSnapshot]:
    """Get specific version of snapshot"""
    snapshots = get_asset_snapshots(target)
    if version <= 0 or version > len(snapshots):
        return None
    return snapshots[version - 1]


def verify_snapshot_integrity(snapshot_id: str, expected_hash: Optional[str] = None) -> bool:
    """
    Verify snapshot hasn't been modified.
    Used for audit trail validation.
    """
    stored_hash = SNAPSHOT_HASHES.get(snapshot_id)
    if not stored_hash:
        return False
    
    if expected_hash:
        return stored_hash == expected_hash
    
    return True


def list_all_targets_with_snapshots() -> List[str]:
    """List all targets that have been scanned"""
    return list(ASSET_SNAPSHOTS.keys())


def clear_snapshots(target: Optional[str] = None):
    """Clear snapshots (for testing/reset)"""
    if target:
        ASSET_SNAPSHOTS.pop(target, None)
        # Also clear hashes for this target's snapshots
        hashes_to_remove = [sid for sid, _ in SNAPSHOT_HASHES.items() 
                           if any(snap.snapshot_id == sid for snaps in [ASSET_SNAPSHOTS.get(target, [])])]
        for hash_id in hashes_to_remove:
            SNAPSHOT_HASHES.pop(hash_id, None)
    else:
        ASSET_SNAPSHOTS.clear()
        SNAPSHOT_HASHES.clear()
