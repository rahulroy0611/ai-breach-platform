import requests
from typing import List
from app.models.asset import Asset
from uuid import uuid4
import re

CRT_SH_URL = "https://crt.sh/?q=%25.{domain}&output=json"

DOMAIN_REGEX = re.compile(
    r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"
)


def is_valid_domain(name: str, root_domain: str) -> bool:
    if "@" in name:
        return False
    if not name.endswith(root_domain):
        return False
    if not DOMAIN_REGEX.match(name):
        return False
    return True


def discover_subdomains(domain: str) -> List[Asset]:
    """
    Passive subdomain discovery using Certificate Transparency logs.
    Safe, non-intrusive, enterprise-friendly.
    """
    discovered = set()
    assets = []

    try:
        url = CRT_SH_URL.format(domain=domain)
        # Increase timeout, add retries
        response = requests.get(url, timeout=30, allow_redirects=True)

        if response.status_code != 200:
            return []

        data = response.json()

        for entry in data:
            name = entry.get("name_value")
            if not name:
                continue

            for sub in name.split("\n"):
                sub = sub.strip().lower()

                if is_valid_domain(sub, domain):
                    discovered.add(sub)

    except requests.Timeout:
        print(f"Timeout querying crt.sh for {domain}")
        return []
    except requests.ConnectionError as e:
        print(f"Connection error querying crt.sh for {domain}: {e}")
        return []
    except Exception as e:
        print(f"Error discovering subdomains for {domain}: {e}")
        return []

    for subdomain in discovered:
        assets.append(
            Asset(
                asset_id=str(uuid4()),
                asset_type="domain",
                identifier=subdomain,
                source="cert_transparency",
                risk_tags=["internet_exposed"]
            )
        )

    return assets
