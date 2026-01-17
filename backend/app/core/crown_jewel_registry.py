from app.models.crown_jewel import CrownJewel

CROWN_JEWELS = [
    CrownJewel(
        jewel_id="CJ-001",
        name="Customer Database",
        asset_type="internal_service",
        impact_score=90,
        data_types=["pii", "financial"]
    ),
    CrownJewel(
        jewel_id="CJ-002",
        name="AI Model Weights",
        asset_type="ai_model",
        impact_score=85,
        data_types=["ip"]
    )
]
