from enum import Enum

class AttackStage(str, Enum):
    RECON = "reconnaissance"
    INITIAL_ACCESS = "initial_access"
    EXECUTION = "execution"
    LATERAL_MOVEMENT = "lateral_movement"
    PRIV_ESC = "privilege_escalation"
    EXFILTRATION = "data_exfiltration"
