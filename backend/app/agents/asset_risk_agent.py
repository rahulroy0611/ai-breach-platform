from app.core.ai_client import call_llm

def classify_asset(asset: dict) -> dict:
    prompt = f"""
You are a cybersecurity risk engine.

Evaluate the exposure risk of this asset:
{asset}

Return JSON only:
- risk_score (0-100)
- risk_tags
"""
    return call_llm(prompt)
