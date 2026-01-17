import threading
import time
from app.core.scan_store import create_scan_job
from app.core.scan_orchestrator import run_scan
from app.core.logger import logger


def schedule_scan(target: str, interval_sec: int):
    def loop():
        while True:
            try:
                # ✅ ALWAYS create job via factory
                job = create_scan_job(target)

                logger.info(
                    f"Continuous EASM scan started | "
                    f"job_id={job.job_id} target={target}"
                )

                run_scan(job_id=job.job_id, target=target)

            except Exception as e:
                logger.error(f"Continuous scan failed: {e}")

            time.sleep(interval_sec)

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
