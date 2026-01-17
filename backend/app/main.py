from fastapi import FastAPI
from app.engines.discovery.domain_discovery import discover_domain
from app.agents.asset_risk_agent import classify_asset
from fastapi import BackgroundTasks
from uuid import uuid4
from app.models.scan_job import ScanJob
from app.core.scan_store import SCAN_JOBS, SCAN_RESULTS
from app.core.scan_orchestrator import run_domain_scan , run_scan
from app.models.scan_type import ScanType
from app.core.bas_service import run_bas_simulation
from app.core.scheduler import schedule_scan
from app.core.scan_store import create_scan_job
from app.core.evidence_store import EVIDENCE_STORE


app = FastAPI(
    title="AI External Breach & Attack Simulation Platform",
    version="0.1"
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/scan/domain")
def scan_domain(domain: str):
    assets = discover_domain(domain)
    enriched = []

    for asset in assets:
        ai_result = classify_asset(asset.dict())
        asset.risk_score = ai_result.get("risk_score")
        asset.risk_tags += ai_result.get("risk_tags", [])
        enriched.append(asset)

    return enriched

@app.post("/scan/start")
def start_scan(
    target: str,
    background_tasks: BackgroundTasks
):
    # Create job via centralized factory
    job = create_scan_job(target)

    # Run scan in background using SAME job_id
    background_tasks.add_task(
        run_scan,
        job.job_id,
        target
    )

    return {
        "job_id": job.job_id,
        "status": job.status,
        "target": target
    }

@app.get("/scan/{job_id}")
def get_scan_status(job_id: str):
    job = SCAN_JOBS.get(job_id)
    if not job:
        return {"error": "Job not found"}

    return job

@app.get("/scan/{job_id}/results")
def get_scan_results(job_id: str):
    if job_id not in SCAN_RESULTS:
        return {"status": "Results not ready"}

    return SCAN_RESULTS[job_id]

@app.get("/bas/simulate/{job_id}")
def simulate_bas(job_id: str):
    if job_id not in SCAN_RESULTS:
        return {"error": "Scan results not found"}

    assets = SCAN_RESULTS[job_id]

    result = run_bas_simulation(
        chain_name="external_to_internal.yaml",
        assets=assets
    )

    return result

@app.post("/easm/continuous/start")
def start_continuous_easm(target: str, interval_minutes: int = 60):
    schedule_scan(target, interval_minutes * 60)
    return {
        "target": target,
        "status": "continuous_monitoring_enabled",
        "interval_minutes": interval_minutes
    }

@app.get("/debug/evidence")
def debug_evidence():
    return EVIDENCE_STORE