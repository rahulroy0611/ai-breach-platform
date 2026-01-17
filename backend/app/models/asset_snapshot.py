from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from app.models.asset import Asset

class AssetSnapshot(BaseModel):
    snapshot_id: str
    snapshot_version: int = 1  # Increment for each scan of same target
    target: str
    assets: List[Asset]
    created_at: datetime = datetime.utcnow()
    
    # ========================================================
    # Enterprise Hardening Metadata
    # ========================================================
    
    # Immutability & auditability
    is_immutable: bool = True  # Once created, snapshots are immutable
    hash: Optional[str] = None  # Checksum of snapshot contents for integrity
    
    # Versioning for BAS replay
    scan_job_id: Optional[str] = None  # Link to originating scan job
    previous_snapshot_id: Optional[str] = None  # For diff tracking
    
    class Config:
        arbitrary_types_allowed = True
