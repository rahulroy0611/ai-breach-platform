from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ScanJob(BaseModel):
    job_id: str
    target: str
    status: str
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
