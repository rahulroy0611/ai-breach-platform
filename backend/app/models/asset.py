from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Asset(BaseModel):
    asset_id: str
    asset_type: str  # domain, ip, api, ai_endpoint
    identifier: str
    source: str
    risk_tags: List[str] = []
    risk_score: Optional[int] = None
    discovered_at: datetime = datetime.utcnow()
