# AI Breach Platform - Copilot Instructions

## Project Overview
AI External Breach & Attack Simulation Platform - a FastAPI-based system that discovers external assets, evaluates their cybersecurity risks using AI, simulates attack chains, and identifies crown jewel impact.

## Core Architecture

### Data Flow Pipeline
```
Target (domain/IP) → Type Detection → Discovery → AI Risk Classification 
→ Asset Normalization/Deduplication → Asset Snapshot → Attack Simulation 
→ Crown Jewel Impact Evaluation → Attack Path Scoring
```

### Key Components

**Discovery Engine** (`app/engines/discovery/`)
- `target_classifier.py`: Detect scan type (DOMAIN/IP/API) using regex patterns
- `domain_discovery.py`: Root domain + passive subdomain enumeration (Certificate Transparency via crt.sh)
- `subdomain_discovery.py`: Enumerate via crt.sh, validate against root domain, deduplicate  
- `ip_discovery.py`: Return IP as-is with `internet_exposed` tag
- `service_discovery.py`: Parallel port scanning using `ThreadPoolExecutor` (50 workers); mode-based port selection from config (curated/extended/full)
- `http_fingerprinting.py`: Safe keyword-based detection (login/admin/API); records evidence via `add_evidence()`
- **Returns**: `Asset` objects with fields: `asset_id`, `asset_type` (domain/ip/service), `identifier`, `source` (dns_lookup/cert_transparency/http_fingerprint), `risk_tags`, `risk_score`

**Risk Classification** (`app/agents/asset_risk_agent.py`)
- Calls LLM (Ollama) via `ai_client.call_llm()` with cybersecurity prompt
- Returns JSON-parsed response with `risk_score` (0-100) and `risk_tags` list
- Pattern: Stateless agent; wraps LLM call with domain-specific prompt

**Asset Processing Pipeline** (`app/core/asset_*.py`)
- `asset_normalizer.py`: Remove invalid assets (regex validation on domains, ensure subdomains belong to root_domain)
- `asset_deduplicator.py`: Deduplicate by `(asset_type, identifier)` tuple; keep first occurrence
- `asset_diff.py`: Compare old vs new snapshots; return added/removed/unchanged lists
- `evidence_store.py`: In-memory `EVIDENCE_STORE` dict (keyed by asset_id); stores discovered indicators with category/type/source/confidence/strength

**Attack Simulation** (`app/core/bas_*` modules)
- `bas_dsl_validator.py`: Validate YAML attack chain structure; enforce required fields (steps, chain_id, stages, asset_types)
- `bas_dsl_loader.py`: Parse YAML; convert stages to `AttackStage` enum; build `AttackChain` and `AttackStep` objects
- `bas_simulator.py`: Iterate steps; check `asset_matches_conditions()` against `(asset.asset_type, asset.risk_tags, evidence)`; apply `success_effects` to matching asset's tags
- `crown_jewel_evaluator.py`: Match reached assets against `CROWN_JEWELS` registry; return impact objects
- `attack_path_scorer.py`: Calculate `path_score = (success_rate * max_impact) / 100`; return likelihood/impact breakdown

**Scan Orchestration** (`app/core/scan_orchestrator.py`)
- `run_scan(job_id, target)`: Full pipeline - classify target → discover assets → enrich with risk classification → apply BAS simulation → return results
- `run_domain_scan(job_id, domain)`: Legacy domain-only path
- **Background execution**: FastAPI `BackgroundTasks` prevents blocking; passes same `job_id` to background tasks via `create_scan_job()` factory

**State Management** (in-memory stores)
- `app/core/scan_store.py`: `SCAN_JOBS` (dict of job_id→ScanJob), `SCAN_RESULTS` (dict of job_id→assets list), `create_scan_job()` factory
- `app/core/snapshot_store.py`: `ASSET_SNAPSHOTS` (dict of target→[AssetSnapshot] list); tracks historical snapshots per target
- `app/core/evidence_store.py`: `EVIDENCE_STORE` (dict of asset_id→[Evidence] list); query via `get_evidence_by_type(asset_id, type)`
- `app/core/crown_jewel_registry.py`: Static `CROWN_JEWELS` list; CrownJewel has `jewel_id`, `asset_type`, `impact_score` (1-100), `data_types` list

## Critical Patterns & Conventions

### Asset Lifecycle
1. **Discovery**: Engines return Asset objects with `asset_type` (domain/ip/service), `identifier`, `source`, initial `risk_tags` (e.g., internet_exposed)
2. **Evidence Collection**: Discovery engines call `add_evidence(Evidence(...))` to record findings (http_service_detected, login_page_detected, subdomain_found, etc.)
3. **Risk Enrichment**: `classify_asset()` calls LLM → returns risk_score + risk_tags (e.g., "weak_auth", "outdated_framework"); tags merged into asset
4. **Normalization**: `normalize_assets()` removes invalid assets (bad domain regex, out-of-scope subdomains)
5. **Deduplication**: `deduplicate_assets()` merges duplicates by (asset_type, identifier) tuple
6. **Snapshotting**: `AssetSnapshot` created; historical diffs via `asset_diff()` (added/removed/unchanged)

### Required_Conditions Matching Logic
Attack steps match assets if **ALL** conditions are satisfied. Conditions can be:
- **Simple tag match**: `required_conditions: ["internet_exposed"]` → asset.risk_tags must contain
- **Asset type match**: `asset_type: service` → technique applies only to services
- **Evidence-based**: `requires_evidence: http_service_detected` → asset must have evidence of this type in EVIDENCE_STORE
  
**Example** (from `external_service_attack.yaml`):
```yaml
required_conditions:
  - asset_type: service           # Technique only fires on services
  - requires_evidence: http_service_detected  # Must have HTTP evidence
success_effects:
  - foothold  # Adds "foothold" tag to asset if condition met
```

### Evidence Creation & Querying
Create standardized evidence via factory:
```python
from app.core.evidence_factory import create_evidence
from app.core.evidence_store import add_evidence

evidence = create_evidence(
    asset_id=asset.asset_id,
    category="discovery|application|exposure|identity",  # Broad category
    type="http_service_detected",  # Specific finding type
    source="http_fingerprint|cert_transparency|port_scan",
    confidence="high|medium|low",
    strength="strong|moderate|weak",
    observed_value=actual_value,  # What was found
    raw_proof=raw_response  # Raw data for audit trail
)
add_evidence(evidence)
```

Query evidence:
```python
from app.core.evidence_store import get_evidence_by_type
evidence_list = get_evidence_by_type(asset_id, "http_service_detected")
```

### Configuration Loading Pattern
Use centralized `config_loader.py`:
```python
from app.core.config_loader import load_easm_config
config = load_easm_config()  # Returns dict from app/config/easm.yaml

# Access port scan config
port_mode = config["port_scan"]["mode"]  # "curated" | "extended" | "full"
```

### Attack Chain DSL Structure (YAML)
Attack chains in `app/attack_chains/` follow this pattern:
```yaml
chain_id: unique_id
name: Human readable name
steps:
  - step_id: step_1
    technique:
      technique_id: T-001
      name: Technique Name
      stage: initial_access  # From AttackStage enum: recon, initial_access, execution, lateral_movement, privilege_escalation, data_exfiltration
      required_conditions:
        - internet_exposed  # Simple tag
        - asset_type: ip    # Asset type constraint
        - requires_evidence: admin_panel_found  # Evidence-based condition
      success_effects:
        - foothold  # Tags to add if successful
    target_asset_type: ip  # Which asset type this targets
```

Validation in `bas_dsl_validator.py` ensures: required_conditions non-empty, valid stages, valid asset_types from ALLOWED_ASSET_TYPES set.

### LLM Integration Pattern
All LLM calls through centralized `ai_client.py`:
```python
from app.core.ai_client import call_llm

prompt = """Your instructions here. Return JSON only."""
result = call_llm(prompt, model="llama3")  # Returns dict (JSON-parsed)
```
- **Connection**: Ollama at `OLLAMA_URL` env var (default http://192.168.1.8:11434)
- **Timeout**: 120s
- **Expected output**: JSON string that is parsed to dict
- **Used by**: `asset_risk_agent.py` for risk scoring

### Job ID Management
Always use centralized factory to avoid ID mismatches:
```python
from app.core.scan_store import create_scan_job
job = create_scan_job(target)  # Returns ScanJob with auto-generated job_id

# Pass same job_id to background tasks
background_tasks.add_task(run_scan, job.job_id, target)
```
- `SCAN_JOBS` stores metadata (status: PENDING/RUNNING/COMPLETED/FAILED, created_at, completed_at, error)
- `SCAN_RESULTS` stores assets indexed by job_id
- Querying status: `SCAN_JOBS[job_id].status`

## Discovery Engine Details

### Domain Discovery Flow (`domain_discovery.py`)
1. Create root domain asset → IP resolve via `socket.gethostbyname()` → creates IP asset
2. Call `discover_subdomains(domain)` → queries crt.sh Certificate Transparency logs
3. For each discovered subdomain: create domain asset + resolve IP + record Evidence
4. Evidence recorded with type="subdomain_found", source="cert_transparency"

### Service Discovery (`service_discovery.py`)
- **Port selection**: Driven by `easm.yaml` config
  - `curated`: Only specific ports (21, 22, 80, 443, 3306, 5432, 6379, 9200, 27017, etc.)
  - `extended`: Port range (default 1-1024)
  - `full`: All 65535 ports (disabled by default, high legal risk)
- **Scanning**: ThreadPoolExecutor with 50 concurrent workers, 0.5s timeout per port
- **Returns**: Asset objects of type "service" with risk_tags like ["ftp", "ssh", "http"]

### HTTP Fingerprinting (`http_fingerprinting.py`)
Keyword-based detection (no crawling, safe):
- **Login detection**: Keywords like "login", "sign in", "password", "username" → records Evidence type="login_page_detected"
- **Admin detection**: Keywords like "admin", "dashboard", "manage" → tags "admin_panel"
- **API detection**: Keywords like "swagger", "openapi", "/api" → tags "api_endpoint"
- **Tech headers**: Extracts Server, X-Powered-By headers
- **Evidence recording**: All findings stored in EVIDENCE_STORE for attack chain matching

### Subdomain Discovery (`subdomain_discovery.py`)
- Queries `https://crt.sh/?q=%25.{domain}&output=json` for Certificate Transparency data
- **Validation**: Domain must match root_domain, pass regex, no @ symbols
- **Deduplication**: Uses set() to prevent duplicate subdomains
- **Returns**: List of Asset objects (type="domain", source="cert_transparency")

## Attack Simulation Engine Deep Dive

### Asset Condition Matching (`bas_simulator.py`)
Function `asset_matches_conditions(asset, conditions)` evaluates if an asset satisfies all required conditions:
- Simple string tags: Check if tag in `asset.risk_tags`
- Dict-based conditions: Match `asset_type` or evidence presence via `get_evidence_by_type(asset_id, type)`
- **Returns**: (success: bool, failed_conditions: list)

### Simulator Flow (`simulate_attack`)
1. For each step in chain:
   - Try all assets; if ONE satisfies all required_conditions → success = True
   - **Apply success_effects**: Add effect tags to asset's risk_tags
   - Break after first success (one asset per step sufficient)
2. If NO asset matches → success = False, record all failed_conditions
3. **Returns**: List of AttackStep objects with success/outcome/failed_conditions populated

### Crown Jewel Evaluation
`evaluate_crown_jewel_impact()` walks successful steps and matches `target_asset_type` against CROWN_JEWELS registry:
```python
CROWN_JEWELS = [
    CrownJewel(jewel_id="CJ-001", name="Customer Database", 
               asset_type="internal_service", impact_score=90, 
               data_types=["pii", "financial"]),
]
```
Returns list of impact objects: `{jewel_id, jewel_name, impact_score, reached_via_step}`

### Attack Path Scoring
```python
# likelihood = % of successful steps
likelihood = int((success_steps / total_steps) * 100)
# impact = highest crown jewel impact_score reached
impact = max(j["impact_score"] for j in jewel_impacts)
# final score = combined metric
path_score = int((likelihood * impact) / 100)
```
Returns `{likelihood, impact, path_score}`

## Integration Points

- **Ollama LLM**: `OLLAMA_URL` env var; required for risk classification
- **External APIs**: Discovery engines call real services (DNS, Shodan, HTTP, etc.)
- **FastAPI Background Tasks**: Long-running scans use `BackgroundTasks` to avoid blocking

## Common Gotchas
- **Job ID mismatches**: Always use centralized `create_scan_job()` factory; background tasks receive same job_id
- **Asset deduplication**: Same asset discovered multiple times gets merged; use `asset_deduplicator.deduplicate_assets()`
- **Snapshot versioning**: Each scan creates new snapshot; diffs via `asset_diff.py`
- **YAML parsing**: Attack chains require strict YAML structure; missing fields cause simulator to skip steps
- **EVIDENCE_STORE dict bug**: `add_evidence()` calls `.append()` on dict instead of `.setdefault()` - creates assets but not evidence entries; check actual implementation when adding evidence-based conditions
- **Asset normalization**: `normalize_assets()` removes domains not under root_domain; pass root_domain explicitly or all subdomains filtered out
- **Port scan threading**: 50 concurrent threads with 0.5s timeout is aggressive; tune in `service_discovery.py` for slower networks

## Development Workflow

**Running Locally**
```bash
docker-compose up -d  # Starts backend on :8000, requires OLLAMA_URL env var
curl -X POST http://localhost:8000/scan/start -d '{"target": "8.8.8.8"}'
```

**Adding New Discovery Engines**
1. Create `app/engines/discovery/new_engine.py`
2. Return `List[Asset]` with required fields
3. Call `add_evidence()` for findings
4. Import in `scan_orchestrator.py` and call in `run_scan()`

**Adding New Attack Chains**
1. Create YAML in `app/attack_chains/new_chain.yaml`
2. Define required_conditions, success_effects, target_asset_type, stage
3. Load via `bas_dsl_loader.load_attack_chain("attack_chains/new_chain.yaml")`
4. Validate with `bas_dsl_validator.validate_attack_chain()`

**Continuous Scanning**
`scheduler.py` provides `schedule_scan(target, interval_sec)` - spawns daemon thread that loops:
```python
job = create_scan_job(target)  # Always use factory
run_scan(job.job_id, target)   # Runs synchronously in loop
time.sleep(interval_sec)
```

## Testing Quick Start
```bash
cd backend
pytest tests/  # Runs test_bas_simulator.py, test_target_classifier.py
```
