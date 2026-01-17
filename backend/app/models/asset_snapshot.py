from pydantic import BaseModel
from datetime import datetime
from typing import List
from app.models.asset import Asset

class AssetSnapshot(BaseModel):
    snapshot_id: str
    target: str
    assets: List[Asset]
    created_at: datetime = datetime.utcnow()
