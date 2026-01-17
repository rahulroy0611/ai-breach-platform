import requests
from app.core.evidence_store import add_evidence
from app.core.evidence_factory import create_evidence

LOGIN_KEYWORDS = ["login", "sign in", "signin", "password", "username", "auth"]
ADMIN_KEYWORDS = ["admin", "administrator", "dashboard", "manage"]
API_KEYWORDS = ["swagger", "openapi", "/api", "json"]


def fingerprint_http_service(
    asset_id: str,
    url: str,
    timeout: float = 5.0
):
    try:
        resp = requests.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": "AI-Breach-Scanner/1.0"}
        )

        headers = {k.lower(): v for k, v in resp.headers.items()}
        body = resp.text.lower()

        # -----------------------------------
        # EVIDENCE: HTTP SERVICE PRESENT
        # -----------------------------------
        add_evidence(create_evidence(
            asset_id=asset_id,
            type="http_service_detected",
            category="application",
            source="http_fingerprint",
            confidence="high",              # 🔥 Escalated
            strength="moderate",
            observed_value=url,
            raw_proof={
                "status_code": resp.status_code,
                "server": headers.get("server"),
                "x-powered-by": headers.get("x-powered-by")
            }
        ))

        # -----------------------------------
        # LOGIN INTERFACE DETECTED
        # -----------------------------------
        has_login = any(k in body for k in LOGIN_KEYWORDS)
        if has_login:
            add_evidence(create_evidence(
                asset_id=asset_id,
                type="login_interface_detected",
                category="application",
                source="http_fingerprint",
                confidence="medium",
                strength="moderate",
                observed_value=url
            ))

        # -----------------------------------
        # ADMIN INTERFACE DETECTED
        # -----------------------------------
        if any(k in body for k in ADMIN_KEYWORDS):
            add_evidence(create_evidence(
                asset_id=asset_id,
                type="admin_interface_detected",
                category="application",
                source="http_fingerprint",
                confidence="high",
                strength="strong",
                observed_value=url
            ))

        # -----------------------------------
        # API DETECTED
        # -----------------------------------
        if any(k in body for k in API_KEYWORDS):
            add_evidence(create_evidence(
                asset_id=asset_id,
                type="api_endpoint_detected",
                category="application",
                source="http_fingerprint",
                confidence="medium",
                strength="moderate",
                observed_value=url
            ))

        # -----------------------------------
        # 🔥 AUTH MISSING (CRITICAL)
        # -----------------------------------
        auth_headers_present = "www-authenticate" in headers

        if (
            resp.status_code in [200, 301, 302]
            and not auth_headers_present
        ):
            add_evidence(create_evidence(
                asset_id=asset_id,
                type="auth_missing",
                category="application",
                source="http_fingerprint",
                confidence="medium",
                strength="moderate",
                observed_value=url,
                raw_proof={
                    "status_code": resp.status_code,
                    "login_detected": has_login,
                    "auth_headers": auth_headers_present
                }
            ))

    except requests.Timeout:
        pass
    except requests.ConnectionError:
        pass
    except Exception as e:
        print(f"HTTP fingerprint error for {url}: {e}")
