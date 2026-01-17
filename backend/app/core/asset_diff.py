from typing import List, Dict
from app.models.asset import Asset

def diff_assets(old: List[Asset], new: List[Asset]) -> Dict:
    old_map = {a.identifier: a for a in old}
    new_map = {a.identifier: a for a in new}

    added = [a for k, a in new_map.items() if k not in old_map]
    removed = [a for k, a in old_map.items() if k not in new_map]
    unchanged = [a for k, a in new_map.items() if k in old_map]

    return {
        "added": added,
        "removed": removed,
        "unchanged": unchanged
    }
