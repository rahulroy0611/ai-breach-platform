from app.core.bas_simulator import simulate_attack
from app.models.attack_chain import AttackChain, AttackStep
from app.models.attack_technique import AttackTechnique
from app.models.attack_stage import AttackStage
from app.models.asset import Asset

def test_attack_succeeds_when_conditions_met():
    asset = Asset(
        asset_id="1",
        asset_type="ip",
        identifier="8.8.8.8",
        source="test",
        risk_tags=["internet_exposed"]
    )

    technique = AttackTechnique(
        technique_id="T1",
        name="Test",
        stage=AttackStage.INITIAL_ACCESS,
        description="",
        required_conditions=["internet_exposed"],
        success_effects=["initial_access"]
    )

    chain = AttackChain(
        chain_id="test",
        name="test",
        steps=[
            AttackStep(
                step_id="s1",
                technique=technique,
                target_asset_type="ip"
            )
        ]
    )

    results = simulate_attack(chain, [asset])
    assert results[0].success is True
