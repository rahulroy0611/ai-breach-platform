from pydantic import BaseModel, Field
from typing import List, Optional
from app.models.attack_technique import AttackTechnique

class AttackStep(BaseModel):
    step_id: str
    technique: AttackTechnique
    target_asset_type: str

    # Execution result
    success: bool = False
    outcome: Optional[str] = None

    # Explainability & evidence
    failed_conditions: List = Field(default_factory=list)
    evidence_used: List[str] = Field(default_factory=list)
    confidence: Optional[str] = None


class AttackChain(BaseModel):
    chain_id: str
    name: str
    steps: List[AttackStep]

