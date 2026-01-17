"""
BAS Run Model & Metadata

Tracks individual Breach & Attack Simulation runs for:
- Version control and replays
- Evidence traceability to specific runs
- Deterministic replay capability
- Enterprise audit trail
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any


class BasRunMetadata(BaseModel):
    """Metadata for deterministic BAS run replay"""
    chain_id: str
    chain_version: str = "1.0"
    snapshot_id: str
    assets_count: int
    evidence_store_version: str  # Version of evidence store at run time
    parameters: Dict[str, Any] = Field(default_factory=dict)  # Input params for replay


class BasRunResult(BaseModel):
    """Result of a single BAS run"""
    run_id: str
    run_sequence: int  # Numeric sequence for ordering (1, 2, 3, ...)
    job_id: str  # Link to scan job
    chain_id: str
    started_at: datetime
    completed_at: datetime
    success_rate: float  # Likelihood percentage
    impact_score: int  # Highest crown jewel impact
    path_score: int  # Combined risk score
    steps_executed: int
    steps_succeeded: int
    crown_jewels_reached: List[Dict] = Field(default_factory=list)
    evidence_used_ids: List[str] = Field(default_factory=list)  # Evidence IDs that contributed
    deterministic_seed: str  # For replay consistency
    metadata: BasRunMetadata
    
    class Config:
        arbitrary_types_allowed = True


class BasRunReplay(BaseModel):
    """Request to replay a specific BAS run"""
    run_id: str
    with_seed: Optional[str] = None  # Override seed for testing


class BasRunSummary(BaseModel):
    """Summary of BAS runs for a job"""
    job_id: str
    total_runs: int
    runs: List[BasRunResult] = Field(default_factory=list)
    last_run_id: Optional[str] = None
    earliest_run_at: Optional[datetime] = None
    latest_run_at: Optional[datetime] = None
