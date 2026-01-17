from typing import List, Tuple
from app.models.asset import Asset


def deduplicate_assets(assets: List[Asset]) -> List[Asset]:
    """
    Deduplicate assets based on (asset_type, identifier).
    Keeps the first occurrence.
    """
    seen: set[Tuple[str, str]] = set()
    deduped: List[Asset] = []

    for asset in assets:
        key = (asset.asset_type, asset.identifier)

        if key in seen:
            continue

        seen.add(key)
        deduped.append(asset)

    return deduped
