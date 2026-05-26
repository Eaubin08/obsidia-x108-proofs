# GRAPHITI NEO4J LIVE READONLY CONNECTIVITY REPORT

**Report ID**: `GRAPHITI_NEO4J_LIVE_READONLY_CONNECTIVITY`  
**Timestamp**: 2026-05-22T14:56:00Z  
**Method**: `BRODY_NATURAL_LANGUAGE_QUALITY_16`  
**Verdict**: `GRAPHITI_NEO4J_LIVE_READONLY_CONNECTIVITY_BLOCKED_WITH_REASON`

---

## 1. Neo4j — Container Status

| Field | Value |
|-------|-------|
| Container | `deploy-neo4j-1` |
| Image | `neo4j:5.26-community` |
| Status | **Up** |
| Port (host) | `7688` |
| Port (container) | `7687` |
| Bolt URI | `bolt://127.0.0.1:7688` |
| Auth | `neo4j` / `obsidia_neo4j_2026` |
| Socket 7688 | **OPEN** |
| Connectivity test | **PASS** |

## 2. ObsidiaShell Bridge

| Field | Value |
|-------|-------|
| Port | `8011` |
| Socket | **OPEN** |
| File | `obsidiashell-main/obsidia_core/agent_bridge.py` |
| Connects via | `GRAPHITI_V20_NEO4J_URI=bolt://127.0.0.1:7688` |

## 3. Brody API

| Field | Value |
|-------|-------|
| Port | `8001` |
| Socket | **CLOSED** (not running) |
| Pipeline | `apps/obsidia_api/brody_real_response_pipeline.py` |
| Probe function | `_probe_graphiti()` checks: port 7688, port 8011, `NEO4J_PASSWORD` env |

## 4. Graphiti Live Module

| Field | Value |
|-------|-------|
| Exists | **Yes** |
| Path | `periphery/graphiti/graphiti_readonly_bridge.py` |
| Status | STUB — `query_graphiti_readonly()` returns empty result |
| Real queries | `brody_real_response_pipeline.py` uses `_CONTEXT_QUERY.query_neo4j()` for live bolt |

## 5. Graphiti Frozen V20

| Field | Value |
|-------|-------|
| Exists | **Yes** |
| Path | `obsidiashell-main/obsidia_core/agent_bridge.py` |
| Endpoints | `/graph/v20/frozen/status`, `/graph/v20/frozen/entities`, `/graph/v20/frozen/context`, `/graph/v20/frozen/relations` |

## 6. Environment Configuration

| File | Variables |
|------|-----------|
| `graphiti-lab/.env.graphiti.local` | `NEO4J_URI=bolt://127.0.0.1:7688`, `NEO4J_USER=neo4j`, `NEO4J_PASSWORD=obsidia_neo4j_2026` |
| `obsidiashell-main/.env.obsidiashell.local` | `GRAPHITI_V20_NEO4J_URI=bolt://127.0.0.1:7688`, `GRAPHITI_V20_NEO4J_PASSWORD=obsidia_neo4j_2026` |

## 7. Blockers

1. **NEO4J_PASSWORD_NOT_SET_IN_ENVIRONMENT** — The PowerShell session running Brody API (port 8001) must export `$env:NEO4J_PASSWORD="obsidia_neo4j_2026"` before launch.

## 8. Resolution

```powershell
# Terminal B — Brody API
cd "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs"
$env:SETUPTOOLS_ENABLE_FEATURES=""
$env:NEO4J_PASSWORD="obsidia_neo4j_2026"
python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8001
```

Then verify:
```powershell
curl -X POST http://127.0.0.1:8001/api/brody/chat -H "Content-Type: application/json" -d '{"message":"test","language":"fr","session_id":"diag"}'
```

Expected in response: `"graphiti_status": "GRAPHITI_LIVE_READONLY_PASS"`, `"source": "REAL_BRODY_GRAPHITI_LIVE"`.

## 9. Constraints Maintained

- `readonly` = **true** (unchanged)
- `decision_authority` = **KX108_ONLY** (unchanged)
- No Neo4j write
- No `force_bypass`
- No X108 mutation
