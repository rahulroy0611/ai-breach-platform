from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class AttackTechnique(BaseModel):
    technique_id: str
    name: str
    description: Optional[str] = ""
    stage: str
    required_conditions: List[Dict]
    success_effects: List[str] = []
    crown_jewels: List[Dict] = []


class AttackStep(BaseModel):
    step_id: str
    technique: AttackTechnique
    success: bool = False
    outcome: Optional[str] = None
    failed_conditions: List[str] = Field(default_factory=list)

    # 🔥 FIX: declare mutation-safe runtime fields
    evidence_used: List[str] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True


class AttackChain(BaseModel):
    chain_id: str
    name: str
    steps: List[AttackStep]
