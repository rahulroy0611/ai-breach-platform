from pydantic import BaseModel
from typing import List

class CrownJewel(BaseModel):
    jewel_id: str
    name: str
    asset_type: str          # db, internal_service, ai_model, payment_system
    impact_score: int        # 1–100 (business impact)
    data_types: List[str]    # pii, financial, ip, credentials
