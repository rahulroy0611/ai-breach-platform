from typing import Dict
from app.models.scan_job import ScanJob
from uuid import uuid4

SCAN_JOBS: Dict[str, ScanJob] = {}
SCAN_RESULTS: Dict[str, list] = {}

def create_scan_job(target: str) -> ScanJob:
    job_id = str(uuid4())
    job = ScanJob(
        job_id=job_id,
        target=target,
        status="PENDING"
    )
    SCAN_JOBS[job_id] = job
    return job
