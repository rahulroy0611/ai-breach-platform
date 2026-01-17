# Testing AI Breach Platform Against testfire.net

## Quick Start

### 1. Start Backend
```bash
$env:OLLAMA_URL = "http://192.168.1.8:11434"
docker-compose up -d
```

### 2. Run Test Script
```bash
python test_platform.py
```

The test script automatically:
- Checks backend health
- Initiates scan against testfire.net
- Polls scan status
- Retrieves discovered assets
- Checks collected evidence
- Shows BAS simulation results
- Displays enterprise features

---

## What Gets Tested

### Discovery Capabilities
- **Domain Classification**: testfire.net identified as domain target
- **Subdomain Enumeration**: Discovers subdomains via Certificate Transparency (crt.sh)
- **IP Resolution**: Resolves domain to IP address
- **Service Discovery**: Port scanning on resolved IPs
- **HTTP Fingerprinting**: Detects web services, login pages, admin panels

### Evidence Collection
- **HTTP Service Detection**: Records HTTP/HTTPS service presence
- **Login/Admin Detection**: Keyword-based identification
- **Tech Stack Detection**: Server headers, frameworks
- **AI-Specific Evidence**: Prompt injection, model exposure risks
- **AI Ethics Evidence**: Jailbreak patterns, harmful intent indicators, context overrides

### Risk Assessment
- **Asset Classification**: LLM-based risk scoring
- **Risk Tagging**: Automatic tag generation (internet_exposed, weak_auth, etc.)
- **Evidence Categorization**: discovery, application, exposure, identity, ai_ethics

### Attack Simulation
- **Attack Chain Loading**: Loads YAML-based attack chains
- **Asset Matching**: Evaluates conditions against discovered assets
- **Success Effects**: Applies tags when techniques succeed
- **Crown Jewel Evaluation**: Identifies business-critical impacts
- **Attack Path Scoring**: Calculates likelihood + impact

### Enterprise Features
- **Immutable Snapshots**: Assets snapshot with SHA256 hash, version numbering
- **BAS Run Versioning**: Each simulation gets unique run_id, sequence number
- **Evidence Traceability**: Links evidence to specific BAS runs
- **Deterministic Replay**: Same inputs produce same outputs
- **Confidence Scoring**: Evidence-based confidence levels

---

## Expected Output Structure

### Scan Result
```json
{
  "assets": [
    {
      "asset_id": "...",
      "asset_type": "domain|ip|service",
      "identifier": "testfire.net",
      "risk_score": 65,
      "risk_tags": ["internet_exposed", "weak_auth"]
    }
  ]
}
```

### Evidence
```json
{
  "evidence_id": "...",
  "asset_id": "...",
  "type": "http_service_detected|login_page_detected|prompt_injection_detected",
  "category": "discovery|application|exposure|ai_ethics",
  "confidence": "high|medium|low",
  "strength": "strong|moderate|weak",
  "observed_value": "actual_finding",
  "bas_run_ids": ["run_1", "run_2"]  // Enterprise feature
}
```

### BAS Result
```json
{
  "chain_id": "external_to_internal",
  "attack_path": [
    {
      "step_id": "step_1",
      "technique": "Exploit HTTP Service",
      "success": true,
      "confidence": 0.9,
      "outcome": "Attack step succeeded based on evidence: ..."
    }
  ],
  "attack_path_score": {
    "likelihood": 66,
    "impact": 90,
    "path_score": 60
  },
  "crown_jewels_reached": [
    {
      "jewel_id": "CJ-001",
      "jewel_name": "Customer Database",
      "impact_score": 90
    }
  ],
  "bas_run": {  // Enterprise feature
    "run_id": "uuid",
    "run_sequence": 1,
    "deterministic_seed": "chain_id:snapshot_id:asset_count",
    "evidence_used_count": 5
  }
}
```

---

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Check backend availability |
| `/scan/start?target=testfire.net` | POST | Initiate domain scan |
| `/scan/status/{job_id}` | GET | Poll scan progress |
| `/scan/results/{job_id}` | GET | Get discovered assets |
| `/scan/bas/{job_id}` | GET | Get attack simulation results |
| `/evidence/{asset_id}` | GET | Get evidence for asset |

---

## Capabilities Verified by Test

✓ Target classification (domain detection)
✓ Passive subdomain discovery
✓ IP resolution
✓ Service scanning and fingerprinting
✓ HTTP keyword-based fingerprinting
✓ AI-specific risk detection
✓ AI ethics and misuse detection
✓ Evidence collection and categorization
✓ Risk scoring via LLM
✓ Attack chain execution
✓ Crown jewel impact evaluation
✓ Attack path scoring with likelihood/impact
✓ Confidence scoring based on evidence
✓ Immutable snapshot versioning
✓ BAS run tracking and sequencing
✓ Evidence traceability to BAS runs
✓ Deterministic replay capability

---

## Manual Testing

### Curl Examples

```bash
# Health check
curl http://localhost:8000/health

# Start scan
curl -X POST "http://localhost:8000/scan/start?target=testfire.net"

# Check status
curl http://localhost:8000/scan/status/{job_id}

# Get results
curl http://localhost:8000/scan/results/{job_id}

# Get BAS results
curl http://localhost:8000/scan/bas/{job_id}

# Get evidence
curl http://localhost:8000/evidence/{asset_id}
```

### Docker Logs
```bash
docker logs -f ai-breach-backend
```

Shows real-time scan progress, discovery events, BAS simulation execution.

---

## Testing Timeouts

- **Domain Discovery**: 5-10 seconds (CT logs, IP resolution)
- **Service Discovery**: 15-30 seconds (50 concurrent port scans)
- **HTTP Fingerprinting**: 5-15 seconds (per service)
- **AI Evidence Scanning**: 5-10 seconds (pattern matching)
- **Risk Classification**: 10-30 seconds (LLM call via Ollama)
- **BAS Simulation**: 1-5 seconds (attack chain execution)
- **Total Scan**: 45-90 seconds (end-to-end)

---

## Common Issues

| Issue | Solution |
|---|---|
| Connection refused on :8000 | Check `docker ps`, restart with `docker-compose up -d` |
| OLLAMA_URL not set | `$env:OLLAMA_URL = "http://192.168.1.8:11434"` before compose up |
| Scan stuck at PENDING | Normal - check docker logs, may be waiting for Ollama |
| Evidence not returned | Depends on what discovery engines found |
| BAS not in results | Normal - only runs if valid attack path exists |

---

## Features Demonstrated

**By Test Script:**
1. Health check validates backend connectivity
2. Scan initiation with domain target
3. Async scan execution with status polling
4. Asset discovery results with risk tags
5. Evidence collection and categorization
6. BAS simulation if conditions met
7. Attack path scoring
8. Enterprise run versioning display

**Available but Not Shown in Test:**
- Continuous EASM scanning
- Evidence store queries
- Snapshot version diffs
- BAS run replay
- Crown jewel registry queries

Use the API endpoints directly to explore these features.
