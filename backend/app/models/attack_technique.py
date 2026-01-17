from typing import List, Dict, Optional
from pydantic import BaseModel

class AttackTechnique(BaseModel):
    technique_id: str
    name: str
    stage: str

    # Human explanation (used later for narratives)
    description: str

    # Evidence-driven conditions
    required_conditions: List[Dict]

    # Tags applied on success
    success_effects: List[str] = []

    # Optional metadata (future-proofing)
    mitre_technique: Optional[str] = None
