from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class Evidence(BaseModel):
    evidence_id: str
    asset_id: str
    type: str

    category: str          # discovery | application | exposure | identity
    type: str              # admin_panel_detected, port_open, login_page_detected, etc.
    source: str            # dns_lookup, http_fingerprint, port_scan
    confidence: str        # high | medium | low
    strength: str          # weak | moderate | strong

    observed_value: Optional[Any] = None
    raw_proof: Optional[Any] = None

    first_seen: datetime
    last_seen: datetime
    is_active: bool = True
