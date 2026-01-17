"""
BAS Run Store

In-memory storage for BAS run metadata and versioning.
Enables deterministic replay, evidence traceability, and audit trails.

Storage Structure:
- BAS_RUNS: Dict[run_id -> BasRunResult]
- BAS_RUN_SEQUENCES: Dict[job_id -> int] (run counter per job)
- BAS_RUN_INDEX: Dict[job_id -> List[run_id]] (runs per job)
"""

from typing import Dict, List, Optional
from app.models.bas_run import BasRunResult, BasRunSummary

# In-memory storage (storage-agnostic, could be migrated to DB/Redis)
BAS_RUNS: Dict[str, BasRunResult] = {}
BAS_RUN_SEQUENCES: Dict[str, int] = {}  # job_id -> next_sequence_number
BAS_RUN_INDEX: Dict[str, List[str]] = {}  # job_id -> [run_id1, run_id2, ...]


def create_bas_run_sequence(job_id: str) -> int:
    """
    Get next sequence number for a BAS run within a job.
    Ensures deterministic, ordered run tracking.
    """
    if job_id not in BAS_RUN_SEQUENCES:
        BAS_RUN_SEQUENCES[job_id] = 1
    else:
        BAS_RUN_SEQUENCES[job_id] += 1
    
    return BAS_RUN_SEQUENCES[job_id]


def store_bas_run(run: BasRunResult):
    """Store a BAS run result and update indices"""
    BAS_RUNS[run.run_id] = run
    
    if run.job_id not in BAS_RUN_INDEX:
        BAS_RUN_INDEX[run.job_id] = []
    
    BAS_RUN_INDEX[run.job_id].append(run.run_id)


def get_bas_run(run_id: str) -> Optional[BasRunResult]:
    """Retrieve a specific BAS run by ID"""
    return BAS_RUNS.get(run_id)


def get_bas_runs_by_job(job_id: str) -> List[BasRunResult]:
    """Retrieve all BAS runs for a specific scan job"""
    run_ids = BAS_RUN_INDEX.get(job_id, [])
    return [BAS_RUNS[run_id] for run_id in run_ids if run_id in BAS_RUNS]


def get_bas_run_summary(job_id: str) -> BasRunSummary:
    """Generate summary of all BAS runs for a job"""
    runs = get_bas_runs_by_job(job_id)
    
    if not runs:
        return BasRunSummary(job_id=job_id, total_runs=0, runs=[])
    
    summary = BasRunSummary(
        job_id=job_id,
        total_runs=len(runs),
        runs=runs,
        last_run_id=runs[-1].run_id if runs else None,
        earliest_run_at=runs[0].started_at if runs else None,
        latest_run_at=runs[-1].completed_at if runs else None,
    )
    
    return summary


def get_last_bas_run(job_id: str) -> Optional[BasRunResult]:
    """Get the most recent BAS run for a job"""
    run_ids = BAS_RUN_INDEX.get(job_id, [])
    if not run_ids:
        return None
    
    return BAS_RUNS.get(run_ids[-1])


def clear_bas_runs(job_id: Optional[str] = None):
    """Clear BAS runs (for testing/reset)"""
    if job_id:
        # Clear specific job
        run_ids = BAS_RUN_INDEX.pop(job_id, [])
        for run_id in run_ids:
            BAS_RUNS.pop(run_id, None)
        BAS_RUN_SEQUENCES.pop(job_id, None)
    else:
        # Clear all
        BAS_RUNS.clear()
        BAS_RUN_SEQUENCES.clear()
        BAS_RUN_INDEX.clear()
