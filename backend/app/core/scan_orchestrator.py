from uuid import uuid4
from datetime import datetime
from app.models.scan_job import ScanJob
from app.core.scan_store import SCAN_JOBS, SCAN_RESULTS
from app.engines.discovery.domain_discovery import discover_domain
from app.agents.asset_risk_agent import classify_asset
from app.models.scan_type import ScanType
from app.engines.discovery.domain_discovery import discover_domain
from app.engines.discovery.ip_discovery import discover_ip
from app.core.target_classifier import detect_scan_type
from app.models.scan_type import ScanType
from app.core.snapshot_store import ASSET_SNAPSHOTS
from app.models.asset_snapshot import AssetSnapshot
from app.core.asset_diff import diff_assets
from app.core.bas_service import run_bas_simulation
from app.core.snapshot_store import ASSET_SNAPSHOTS
from app.core.logger import logger
from app.core.asset_normalizer import normalize_assets
from app.core.asset_deduplicator import deduplicate_assets
from app.engines.discovery.service_discovery import discover_services
from app.engines.discovery.http_fingerprinting import fingerprint_http_service
from app.core.evidence_store import add_evidence
from app.models.evidence import Evidence
from app.engines.discovery.http_fingerprinting import fingerprint_http_service
from app.core.evidence_factory import create_evidence




def run_domain_scan(job_id: str, domain: str):
    job = SCAN_JOBS.get(job_id)
    if not job:
        logger.error(f"Scan job {job_id} missing — skipping scan")
        # raise RuntimeError(f"Scan job {job_id} not initialized")
        return
    job.status = "RUNNING"
    logger.info(
        f"Scan started | job_id={job.job_id} target={domain}"
    )
    

    try:
        assets = discover_domain(domain)
        enriched = []

        for asset in assets:
            ai_result = classify_asset(asset.dict())
            asset.risk_score = ai_result.get("risk_score")
            asset.risk_tags += ai_result.get("risk_tags", [])
            enriched.append(asset)

        SCAN_RESULTS[job_id] = enriched
        job.status = "COMPLETED"
        job.completed_at = datetime.utcnow()
        logger.info(
            f"Scan completed | job_id={job.job_id} assets_discovered={len(enriched)}"
        )


    except Exception as e:
        job.status = "FAILED"
        job.error = str(e)

def run_scan(job_id: str, target: str):
    job = SCAN_JOBS.get(job_id)
    if not job:
        logger.error(f"Scan job {job_id} missing — skipping scan")
        return

    job.status = "RUNNING"

    logger.info(
        f"Scan started | job_id={job.job_id} target={target}"
    )

    try:
        scan_type = detect_scan_type(target)

        if scan_type == ScanType.DOMAIN:
            assets = discover_domain(target)
        elif scan_type == ScanType.IP:
            assets = discover_ip(target)
        else:
            raise ValueError("Scan type not supported yet")

        enriched = []
        for asset in assets:
            ai_result = classify_asset(asset.dict())
            asset.risk_score = ai_result.get("risk_score")
            asset.risk_tags += ai_result.get("risk_tags", [])
            enriched.append(asset)

            # 🔹 NEW: Service discovery for IPs
            if asset.asset_type == "ip":
                services = discover_services(asset.identifier)
                enriched.extend(services)

                # 🔹 HTTP fingerprinting for web services
                for svc in services:
                    if "http" in svc.risk_tags or "https" in svc.risk_tags:
                        url = f"http://{svc.identifier}"

                        fp = fingerprint_http_service(url)

                        now = datetime.utcnow()

                        if fp.get("is_http"):
                            add_evidence(create_evidence(
                                asset_id=svc.asset_id,
                                category="application",
                                type="http_service_detected",
                                source="http_fingerprint",
                                confidence="high",
                                strength="strong",
                                observed_value=url,
                                raw_proof=fp.get("tech_headers")
                            ))

                        if fp.get("has_login"):
                            add_evidence(create_evidence(
                                asset_id=svc.asset_id,
                                category="application",
                                type="login_page_detected",
                                source="http_fingerprint",
                                confidence="high",
                                strength="strong",
                                observed_value=url,
                                raw_proof=fp.get("html_snippet")
                            ))

                        if fp.get("has_admin"):
                            add_evidence(create_evidence(
                                asset_id=svc.asset_id,
                                category="application",
                                type="admin_panel_detected",
                                source="http_fingerprint",
                                confidence="high",
                                strength="strong",
                                observed_value=url,
                                raw_proof=fp.get("html_snippet")
                            ))

                        for k, v in fp.get("tech_headers", {}).items():
                            svc.risk_tags.append(f"tech:{k}")


        # 🔹 Normalize & deduplicate assets
        normalized = normalize_assets(enriched, root_domain=target if scan_type == ScanType.DOMAIN else None)
        final_assets = deduplicate_assets(normalized)

        SCAN_RESULTS[job_id] = final_assets
        job.status = "COMPLETED"
        job.completed_at = datetime.utcnow()

        logger.info(
            f"Scan completed | job_id={job.job_id} assets_discovered={len(enriched)}"
        )

        snapshot = AssetSnapshot(
            snapshot_id=str(uuid4()),
            target=target,
            assets=enriched
        )

        ASSET_SNAPSHOTS.setdefault(target, []).append(snapshot)

        logger.info(
            f"Snapshot saved | target={target} total_snapshots={len(ASSET_SNAPSHOTS[target])}"
        )

        snapshots = ASSET_SNAPSHOTS[target]
        if len(snapshots) >= 2:
            prev = snapshots[-2].assets
            curr = snapshots[-1].assets

            diff = diff_assets(prev, curr)

            logger.info(
                f"EASM diff | target={target} "
                f"added={len(diff['added'])} "
                f"removed={len(diff['removed'])}"
            )

            if diff["added"]:
                logger.info("New attack surface detected — triggering BAS")
                run_bas_simulation(
                    chain_path="attack_chains/external_to_internal.yaml",
                    assets=curr
                )

    except Exception as e:
        job.status = "FAILED"
        job.error = str(e)
        logger.error(
            f"Scan failed | job_id={job.job_id} error={e}"
        )
