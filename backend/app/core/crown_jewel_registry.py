from app.models.crown_jewel import CrownJewel

CROWN_JEWELS = [
    CrownJewel(
        jewel_id="CJ-001",
        name="Customer Database",
        asset_type="service",
        required_evidence=[
            "auth_missing",
            "http_service_detected"
        ],
        impact_score=90
    )
]