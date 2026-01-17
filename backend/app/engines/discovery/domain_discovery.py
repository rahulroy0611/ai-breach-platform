import socket
from uuid import uuid4
from typing import List
from datetime import datetime
from app.core.evidence_store import add_evidence
from app.models.evidence import Evidence
from app.models.asset import Asset
from app.engines.discovery.subdomain_discovery import discover_subdomains
from app.core.evidence_factory import create_evidence


def resolve_ip(hostname: str) -> List[Asset]:
    """
    Resolve IP address for a hostname.
    """
    assets = []
    try:
        ip = socket.gethostbyname(hostname)
        assets.append(
            Asset(
                asset_id=str(uuid4()),
                asset_type="ip",
                identifier=ip,
                source="dns_lookup",
                risk_tags=["internet_exposed"],
            )
        )
    except Exception:
        pass

    return assets


def discover_domain(domain: str) -> List[Asset]:
    assets: List[Asset] = []

    # 1️⃣ Root domain asset
    assets.append(
        Asset(
            asset_id=str(uuid4()),
            asset_type="domain",
            identifier=domain,
            source="manual",
            risk_tags=["internet_exposed"],
        )
    )

    # 2️⃣ Resolve IP for root domain
    assets.extend(resolve_ip(domain))

    # 3️⃣ Discover subdomains (PASSIVE)
    try:
        subdomains = discover_subdomains(domain)
    except Exception as e:
        # Log but don't fail entire scan if subdomain discovery fails
        print(f"Subdomain discovery failed for {domain}: {e}")
        subdomains = []

    for sub in subdomains:
        assets.append(sub)

        try:
            add_evidence(create_evidence(
                asset_id=sub.asset_id,
                category="discovery",
                type="subdomain_found",
                source="cert_transparency",
                confidence="high",
                strength="moderate",
                observed_value=sub.identifier,
                raw_proof=None
            ))
        except Exception as e:
            print(f"Failed to record evidence for {sub.identifier}: {e}")

        # 4️⃣ Resolve IPs for subdomains
        assets.extend(resolve_ip(sub.identifier))

    return assets
