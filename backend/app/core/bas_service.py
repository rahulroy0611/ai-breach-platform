from pathlib import Path
from datetime import datetime
from uuid import uuid4
from app.core.bas_simulator import simulate_attack, get_evidence_ids_for_conditions
from app.core.bas_dsl_loader import load_attack_chain
from app.core.crown_jewel_evaluator import evaluate_crown_jewel_impact
from app.core.crown_jewel_registry import CROWN_JEWELS
from app.core.attack_path_scorer import score_attack_path
from app.models.bas_run import BasRunMetadata, BasRunResult
from app.core.bas_run_store import create_bas_run_sequence, store_bas_run
from app.core.evidence_store import EVIDENCE_STORE


BASE_DIR = Path(__file__).resolve().parent.parent
ATTACK_CHAIN_DIR = BASE_DIR / "attack_chains"


def run_bas_simulation(chain_name: str, assets: list, job_id: str = "", snapshot_id: str = ""):
    """
    Run BAS simulation with enterprise hardening features.
    
    Args:
        chain_name: Attack chain filename
        assets: List of Asset objects
        job_id: Scan job ID for traceability
        snapshot_id: Asset snapshot version ID
    
    Returns:
        Dictionary with attack results, BAS run tracking, and evidence traceability
    """
    chain_file = ATTACK_CHAIN_DIR / chain_name

    if not chain_file.exists():
        raise FileNotFoundError(
            f"Attack chain not found: {chain_file}. "
            f"Available: {[p.name for p in ATTACK_CHAIN_DIR.glob('*.yaml')]}"
        )

    chain = load_attack_chain(str(chain_file))
    
    # ====================================================
    # Enterprise Hardening: BAS Run Versioning
    # ====================================================
    
    start_time = datetime.utcnow()
    run_id = str(uuid4())
    
    # Create deterministic seed from inputs for replay consistency
    deterministic_seed = f"{chain.chain_id}:{snapshot_id}:{len(assets)}"
    
    # Get sequence number for this run
    if not job_id:
        job_id = f"local-{run_id[:8]}"
    
    run_sequence = create_bas_run_sequence(job_id)

    attack_steps = simulate_attack(chain, assets)
    jewel_impacts = evaluate_crown_jewel_impact(attack_steps, CROWN_JEWELS)
    scoring = score_attack_path(attack_steps, jewel_impacts)
    
    # ====================================================
    # Evidence Traceability: Link evidence to BAS run
    # ====================================================
    
    evidence_used = []
    for step in attack_steps:
        if step.success and step.technique.required_conditions:
            # Collect evidence IDs that contributed to this step
            for asset in assets:
                cond_evidence = get_evidence_ids_for_conditions(asset, step.technique.required_conditions)
                evidence_used.extend(cond_evidence)
                
                # Update evidence records to track this BAS run
                for cond in step.technique.required_conditions:
                    if isinstance(cond, dict) and cond.get("requires_evidence"):
                        evidence_type = cond["requires_evidence"]
                        if asset.asset_id in EVIDENCE_STORE:
                            for evidence in EVIDENCE_STORE[asset.asset_id]:
                                if evidence.type == evidence_type:
                                    if run_id not in evidence.bas_run_ids:
                                        evidence.bas_run_ids.append(run_id)
    
    # ====================================================
    # Create immutable BAS run record
    # ====================================================
    
    end_time = datetime.utcnow()
    steps_executed = len(attack_steps)
    steps_succeeded = len([s for s in attack_steps if s.success])
    
    run_metadata = BasRunMetadata(
        chain_id=chain.chain_id,
        snapshot_id=snapshot_id,
        assets_count=len(assets),
        evidence_store_version="1.0",
        parameters={
            "chain_name": chain_name,
            "assets_count": len(assets),
        }
    )
    
    bas_run = BasRunResult(
        run_id=run_id,
        run_sequence=run_sequence,
        job_id=job_id,
        chain_id=chain.chain_id,
        started_at=start_time,
        completed_at=end_time,
        success_rate=scoring.get("likelihood", 0),
        impact_score=scoring.get("impact", 0),
        path_score=scoring.get("path_score", 0),
        steps_executed=steps_executed,
        steps_succeeded=steps_succeeded,
        crown_jewels_reached=jewel_impacts,
        evidence_used_ids=list(set(evidence_used)),  # Deduplicate
        deterministic_seed=deterministic_seed,
        metadata=run_metadata,
    )
    
    # Store immutable run record
    store_bas_run(bas_run)

    return {
        # Original fields (backward compatible)
        "chain_id": chain.chain_id,
        "chain_name": chain.name,
        "attack_path": [
            {
                "step_id": s.step_id,
                "technique": s.technique.name,
                "stage": s.technique.stage,
                "success": s.success,
                "outcome": s.outcome,
                "failed_conditions": s.failed_conditions,
                "confidence": s.confidence,  # Include confidence scoring
            }
            for s in attack_steps
        ],
        "crown_jewels_reached": jewel_impacts,
        "attack_path_score": scoring,
        
        # ========================================================
        # Enterprise Hardening: Run Versioning & Traceability
        # ========================================================
        "bas_run": {
            "run_id": run_id,
            "run_sequence": run_sequence,
            "job_id": job_id,
            "deterministic_seed": deterministic_seed,
            "evidence_used_count": len(evidence_used),
            "evidence_used_ids": list(set(evidence_used)),
        }
    }
