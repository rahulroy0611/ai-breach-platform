"""
AI-Specific Evidence Discovery Engine

Detects AI-related security indicators without exploitation:
- prompt_injection_detected: Indicators that suggest LLM/AI input handling weaknesses
- model_overexposure: Evidence of exposed model details, API endpoints, or version info
- training_data_leak_risk: Indicators of training data exposure or unredacted artifacts
- unsafe_tool_call: Evidence of dangerous tool integrations or unchecked function calls

AI Misuse & Ethics Risk Detection:
- jailbreak_attempt_detected: Patterns indicating attempts to bypass AI safety guardrails
- harmful_intent_indicator: Signals of intent to use AI for harmful purposes
- context_override_attempt: Evidence of prompt injection or context manipulation
- language_ambiguity_risk: Ambiguous language patterns that could enable misuse

Detection only - no content filtering, no enforcement.
Evidence is generated for audit and investigation purposes.

These evidence types are compatible with future AI-focused attack chains
but do not change existing BAS simulator logic.
"""

import requests
from app.core.evidence_store import add_evidence
from app.core.evidence_factory import create_evidence


# Keywords and patterns that suggest prompt injection vulnerabilities
PROMPT_INJECTION_INDICATORS = [
    "user input",
    "query parameter",
    "dynamically constructed",
    "concatenated prompt",
    "unsafe template",
    "raw user data",
]

# Patterns suggesting model or API overexposure
MODEL_OVEREXPOSURE_INDICATORS = [
    "model:",
    "llm version",
    "api documentation",
    "model-info",
    "llm details",
    "gpt",
    "claude",
    "llama",
    "model capabilities",
]

# Patterns suggesting training data leakage
TRAINING_DATA_LEAK_INDICATORS = [
    "training data",
    "sample data",
    "example prompts",
    "internal documentation",
    "debug output",
    "stack trace",
]

# Patterns suggesting dangerous tool integrations
UNSAFE_TOOL_CALL_INDICATORS = [
    "exec",
    "eval",
    "system call",
    "shell command",
    "subprocess",
    "os.system",
    "dangerous function",
    "code execution",
]

# ========================================================
# AI ETHICS & MISUSE DETECTION INDICATORS
# ========================================================

# Patterns suggesting jailbreak attempts or guardrail bypasses
JAILBREAK_INDICATORS = [
    "ignore instructions",
    "pretend you are",
    "forget everything",
    "disregard safety",
    "override safety",
    "bypass restrictions",
    "disable filters",
    "forget your rules",
    "act as if",
    "roleplay as",
    "assume you have no",
    "you are now",
    "new instructions override",
]

# Patterns suggesting harmful intent
HARMFUL_INTENT_INDICATORS = [
    "create malware",
    "write ransomware",
    "generate exploit",
    "create phishing",
    "bypass security",
    "hack into",
    "unauthorized access",
    "fraud scheme",
    "illegal activity",
    "abuse children",
    "hate speech",
    "discrimination guide",
    "how to harm",
    "instructions for violence",
]

# Patterns indicating context or prompt override attempts
CONTEXT_OVERRIDE_INDICATORS = [
    "---",
    "system override",
    "new context",
    "forget previous",
    "ignore above",
    "override prompt",
    "previous instructions invalid",
    "new directive",
    "[system]",
    "[admin]",
    "[override]",
    "treat as new task",
]

# Patterns indicating language ambiguity that could enable misuse
LANGUAGE_AMBIGUITY_INDICATORS = [
    "theoretically",
    "for research",
    "educational purposes",
    "hypothetical",
    "as an exercise",
    "in fiction",
    "as a test",
    "academic context",
    "for a novel",
    "pretend scenario",
]


def scan_ai_ethics_risk(asset_id: str, url: str, timeout: float = 5.0):
    """
    Scan an HTTP service for AI misuse and ethics risk indicators.
    Detection-only: generates evidence without filtering or enforcement.
    
    Args:
        asset_id: The asset identifier for evidence attribution
        url: The URL to scan
        timeout: HTTP request timeout in seconds
    """
    try:
        resp = requests.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": "AI-Breach-Scanner/1.0"}
        )

        body = resp.text.lower()
        
        # ====================================================
        # CHECK 1: Jailbreak-like Prompt Patterns
        # ====================================================
        for indicator in JAILBREAK_INDICATORS:
            if indicator.lower() in body:
                confidence = "high" if len(indicator) > 5 else "medium"
                add_evidence(create_evidence(
                    asset_id=asset_id,
                    category="ai_ethics",
                    type="jailbreak_attempt_detected",
                    source="ai_ethics_scan",
                    confidence=confidence,
                    strength="strong",
                    observed_value=indicator,
                    raw_proof={
                        "url": url,
                        "indicator_found": indicator,
                        "pattern_type": "guardrail_bypass",
                        "status_code": resp.status_code,
                    }
                ))
                break  # Only record once per service
        
        # ====================================================
        # CHECK 2: Harmful Intent Indicators
        # ====================================================
        for indicator in HARMFUL_INTENT_INDICATORS:
            if indicator.lower() in body:
                add_evidence(create_evidence(
                    asset_id=asset_id,
                    category="ai_ethics",
                    type="harmful_intent_indicator",
                    source="ai_ethics_scan",
                    confidence="high",
                    strength="strong",
                    observed_value=indicator,
                    raw_proof={
                        "url": url,
                        "indicator_found": indicator,
                        "pattern_type": "harmful_use_case",
                        "status_code": resp.status_code,
                    }
                ))
                break  # Only record once per service
        
        # ====================================================
        # CHECK 3: Context Override Attempt Patterns
        # ====================================================
        for indicator in CONTEXT_OVERRIDE_INDICATORS:
            if indicator.lower() in body:
                confidence = "high" if len(indicator) > 10 else "medium"
                add_evidence(create_evidence(
                    asset_id=asset_id,
                    category="ai_ethics",
                    type="context_override_attempt",
                    source="ai_ethics_scan",
                    confidence=confidence,
                    strength="moderate",
                    observed_value=indicator,
                    raw_proof={
                        "url": url,
                        "indicator_found": indicator,
                        "pattern_type": "prompt_manipulation",
                        "status_code": resp.status_code,
                    }
                ))
                break  # Only record once per service
        
        # ====================================================
        # CHECK 4: Language Ambiguity Risks
        # ====================================================
        for indicator in LANGUAGE_AMBIGUITY_INDICATORS:
            if indicator.lower() in body:
                add_evidence(create_evidence(
                    asset_id=asset_id,
                    category="ai_ethics",
                    type="language_ambiguity_risk",
                    source="ai_ethics_scan",
                    confidence="medium",
                    strength="weak",
                    observed_value=indicator,
                    raw_proof={
                        "url": url,
                        "indicator_found": indicator,
                        "pattern_type": "context_framing",
                        "status_code": resp.status_code,
                    }
                ))
                break  # Only record once per service
        
        return {
            "scanned": True,
            "url": url,
            "status_code": resp.status_code,
            "scan_type": "ai_ethics",
        }

    except requests.exceptions.Timeout:
        return {"scanned": False, "error": "Timeout"}
    except requests.exceptions.ConnectionError:
        return {"scanned": False, "error": "Connection refused"}
    except Exception as e:
        return {"scanned": False, "error": str(e)}


def scan_ai_evidence(asset_id: str, url: str, timeout: float = 5.0):
    """
    Scan an HTTP service for AI-specific security indicators.
    Records evidence findings without modifying asset risk tags.
    
    Args:
        asset_id: The asset identifier for evidence attribution
        url: The URL to scan
        timeout: HTTP request timeout in seconds
    """
    try:
        resp = requests.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": "AI-Breach-Scanner/1.0"}
        )

        headers = {k.lower(): v for k, v in resp.headers.items()}
        body = resp.text.lower()
        
        # ====================================================
        # CHECK 1: Prompt Injection Vulnerability Indicators
        # ====================================================
        for indicator in PROMPT_INJECTION_INDICATORS:
            if indicator.lower() in body:
                add_evidence(create_evidence(
                    asset_id=asset_id,
                    category="application",
                    type="prompt_injection_detected",
                    source="ai_evidence_scan",
                    confidence="medium",
                    strength="moderate",
                    observed_value=indicator,
                    raw_proof={
                        "url": url,
                        "indicator_found": indicator,
                        "status_code": resp.status_code,
                    }
                ))
                break  # Only record once per service
        
        # ====================================================
        # CHECK 2: Model Overexposure Indicators
        # ====================================================
        for indicator in MODEL_OVEREXPOSURE_INDICATORS:
            if indicator.lower() in body:
                add_evidence(create_evidence(
                    asset_id=asset_id,
                    category="application",
                    type="model_overexposure",
                    source="ai_evidence_scan",
                    confidence="high",
                    strength="strong",
                    observed_value=indicator,
                    raw_proof={
                        "url": url,
                        "indicator_found": indicator,
                        "headers": dict(headers),
                        "status_code": resp.status_code,
                    }
                ))
                break  # Only record once per service
        
        # ====================================================
        # CHECK 3: Training Data Leak Risk Indicators
        # ====================================================
        for indicator in TRAINING_DATA_LEAK_INDICATORS:
            if indicator.lower() in body:
                add_evidence(create_evidence(
                    asset_id=asset_id,
                    category="exposure",
                    type="training_data_leak_risk",
                    source="ai_evidence_scan",
                    confidence="high",
                    strength="strong",
                    observed_value=indicator,
                    raw_proof={
                        "url": url,
                        "indicator_found": indicator,
                        "status_code": resp.status_code,
                    }
                ))
                break  # Only record once per service
        
        # ====================================================
        # CHECK 4: Unsafe Tool Call Indicators
        # ====================================================
        for indicator in UNSAFE_TOOL_CALL_INDICATORS:
            if indicator.lower() in body:
                add_evidence(create_evidence(
                    asset_id=asset_id,
                    category="application",
                    type="unsafe_tool_call",
                    source="ai_evidence_scan",
                    confidence="high",
                    strength="strong",
                    observed_value=indicator,
                    raw_proof={
                        "url": url,
                        "indicator_found": indicator,
                        "status_code": resp.status_code,
                    }
                ))
                break  # Only record once per service
        
        # 🔹 NEW: Also scan for AI ethics and misuse risks
        scan_ai_ethics_risk(asset_id, url, timeout)
        
        return {
            "scanned": True,
            "url": url,
            "status_code": resp.status_code,
            "evidence_types": [
                "prompt_injection",
                "model_overexposure",
                "training_data_leak",
                "unsafe_tool_call",
                "ai_ethics_risks",
            ]
        }

    except requests.exceptions.Timeout:
        return {"scanned": False, "error": "Timeout"}
    except requests.exceptions.ConnectionError:
        return {"scanned": False, "error": "Connection refused"}
    except Exception as e:
        return {"scanned": False, "error": str(e)}
