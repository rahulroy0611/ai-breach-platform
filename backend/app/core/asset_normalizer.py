import re
from typing import List
from app.models.asset import Asset

DOMAIN_REGEX = re.compile(r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$")


def normalize_assets(assets: List[Asset], root_domain: str | None = None) -> List[Asset]:
    """
    Remove invalid / noisy assets produced by discovery engines.
    """
    normalized: List[Asset] = []

    for asset in assets:
        # --- DOMAIN VALIDATION ---
        if asset.asset_type == "domain":
            name = asset.identifier.lower()

            # Remove emails
            if "@" in name:
                continue

            # Remove cert metadata junk
            if " " in name:
                continue

            # Regex validation
            if not DOMAIN_REGEX.match(name):
                continue

            # Ensure subdomains belong to root domain (if known)
            if root_domain and not name.endswith(root_domain):
                continue

            asset.identifier = name
            normalized.append(asset)

        # --- IP VALIDATION ---
        elif asset.asset_type == "ip":
            normalized.append(asset)

        # --- OTHER TYPES (future) ---
        else:
            normalized.append(asset)

    return normalized
