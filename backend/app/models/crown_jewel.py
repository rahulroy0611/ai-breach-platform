from pydantic import BaseModel

class CrownJewel(BaseModel):
    jewel_id: str
    name: str
    asset_type: str
    required_evidence: list[str]
    impact_score: int
