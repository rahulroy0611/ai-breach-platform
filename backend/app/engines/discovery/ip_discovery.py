from uuid import uuid4
from app.models.asset import Asset

def discover_ip(ip: str):
    return [
        Asset(
            asset_id=str(uuid4()),
            asset_type="ip",
            identifier=ip,
            source="direct_input",
            risk_tags=["internet_exposed"]
        )
    ]
