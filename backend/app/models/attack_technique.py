from typing import List
from pydantic import BaseModel
from app.models.attack_stage import AttackStage

class AttackTechnique(BaseModel):
    technique_id: str
    name: str
    stage: AttackStage
    description: str
    required_conditions: List[str]
    success_effects: List[str]
