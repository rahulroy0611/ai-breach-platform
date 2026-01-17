import socket
from uuid import uuid4
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.models.asset import Asset
from app.core.config_loader import load_easm_config
from app.core.evidence_store import add_evidence
from app.core.evidence_factory import create_evidence
from app.engines.discovery.http_fingerprinting import fingerprint_http_service


# -------------------------------------------------
# Common externally exposed ports (safe list)
# -------------------------------------------------
COMMON_PORTS = {
    21: "ftp",
    22: "ssh",
    25: "smtp",
    53: "dns",
    80: "http",
    110: "pop3",
    143: "imap",
    443: "https",
    465: "smtps",
    587: "smtp",
    993: "imaps",
    995: "pop3s",
    3306: "mysql",
    3389: "rdp",
    5432: "postgres",
    6379: "redis",
    9200: "elasticsearch",
}


# -------------------------------------------------
# Socket-level port check
# -------------------------------------------------
def check_port(ip: str, port: int, service_name: str, timeout: float):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    try:
        if sock.connect_ex((ip, port)) == 0:
            return port, service_name
    except Exception:
        pass
    finally:
        sock.close()

    return None


# -------------------------------------------------
# Port selection logic (policy-driven)
# -------------------------------------------------
def get_ports_to_scan() -> dict:
    config = load_easm_config()
    port_cfg = config.get("port_scan", {})
    mode = port_cfg.get("mode", "curated")

    if mode == "curated":
        curated = port_cfg.get("curated_ports", {})
        if isinstance(curated, list):
            return {int(p): "unknown" for p in curated}
        if isinstance(curated, dict):
            return {int(p): str(v) for p, v in curated.items()}
        raise RuntimeError("Invalid curated_ports format")

    if mode == "extended":
        range_str = port_cfg.get("extended_ports", {}).get("range", "1-1024")
        start, end = range_str.split("-")
        return {p: "unknown" for p in range(int(start), int(end) + 1)}

    if mode == "full":
        if not port_cfg.get("full_scan", {}).get("enabled", False):
            raise RuntimeError("Full port scan disabled by policy")
        return {p: "unknown" for p in range(1, 65536)}

    raise RuntimeError(f"Invalid port scan mode: {mode}")


# -------------------------------------------------
# Service discovery + evidence emission
# -------------------------------------------------
def discover_services(ip: str, timeout: float = 0.5) -> List[Asset]:
    services: List[Asset] = []
    ports = get_ports_to_scan()
    scan_mode = load_easm_config()["port_scan"]["mode"]

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [
            executor.submit(check_port, ip, port, service_name, timeout)
            for port, service_name in ports.items()
        ]

        for future in as_completed(futures):
            result = future.result()
            if not result:
                continue

            port, service_name = result

            # -------------------------------
            # Create Service Asset
            # -------------------------------
            service_asset = Asset(
                asset_id=str(uuid4()),
                asset_type="service",
                identifier=f"{ip}:{port}",
                source="port_scan",
                risk_tags=[
                    "public_service",
                    service_name,
                    f"scan_mode:{scan_mode}"
                ],
            )

            services.append(service_asset)

            # -------------------------------
            # Evidence: Port Open
            # -------------------------------
            add_evidence(create_evidence(
                asset_id=service_asset.asset_id,
                type="port_open",            # ✅ correct
                category="exposure",
                source="port_scan",
                confidence="high",
                strength="moderate",
                observed_value=service_asset.identifier,
                raw_proof=service_asset.identifier
            ))

            # -------------------------------
            # HTTP Fingerprinting (CRITICAL)
            # -------------------------------
            if port in {80, 443, 8080, 8443}:
                scheme = "https" if port in {443, 8443} else "http"
                url = f"{scheme}://{ip}:{port}"

                fingerprint_http_service(
                    asset_id=service_asset.asset_id,
                    url=url
                )

    return services
