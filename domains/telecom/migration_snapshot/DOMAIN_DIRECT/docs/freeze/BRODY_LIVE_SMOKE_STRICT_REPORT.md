# BRODY LIVE SMOKE STRICT REPORT
Date: 2026-05-20
Verdict: LIVE_SMOKE_BLOCKED_WITH_EXACT_REASON

---

## Service status at time of report

| Service | Port | Status | Reason |
|---|---|---|---|
| Neo4j | 7688 | OFFLINE | Not started — `NEO4J_PASSWORD` not set in env |
| ObsidiaShell | 8011 | OFFLINE | Not started |
| Obsidia API | 8000 | OFFLINE | Not started (test session used TestClient only) |
| Workbench | 5173 | OFFLINE | Not started |

**Blocker:** All services offline at time of test run.

## What was used instead

All 271 API tests ran via **FastAPI TestClient** — no network required. This is the standard Obsidia test mode.

```
python -m pytest tests/api -q
271 passed in 213.83s
```

## To run live smoke

**Step 1 — Start Neo4j:**
```
set NEO4J_PASSWORD=<your_password>
neo4j console
```

**Step 2 — Start ObsidiaShell:**
```
python -m uvicorn obsidia_shell.main:app --host 127.0.0.1 --port 8011 --reload
```

**Step 3 — Start Obsidia API:**
```
.\scripts\run_obsidia_api.ps1
# or: python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000 --reload
```

**Step 4 — Check stack:**
```
.\scripts\check_brody_live_stack.ps1
```

**Step 5 — Run smoke:**
```
.\scripts\smoke_brody_v1_4_12a_live.ps1
```

## Expected live smoke results (when services are online)

| Assertion | Expected |
|---|---|
| `response == final_answer` | true |
| `final_answer` natural French | true |
| `response_md` separate | true |
| `voice_runtime` | `BRODY_OBSIDIEN_V1_4_12A` |
| `source` | `REAL_BRODY_GRAPHITI_LIVE` (if Neo4j reachable) |
| `graphiti_status` | `GRAPHITI_LIVE_READONLY_PASS` |
| `neo4j_status` | `LIVE_READONLY` |
| `emits_act` | `false` |
| `memory_write` | `false` |
| `decision_authority` | `X108_ONLY` |
| `translation_trace.detected_language` | `fr` |
| `ir_candidate.allowed_to_decide` | `false` |

## Verdict

```
LIVE_SMOKE_BLOCKED_WITH_EXACT_REASON:
  All 4 services offline (Neo4j 7688, ObsidiaShell 8011, API 8000, Workbench 5173).
  TestClient-based tests (271/271) confirm correctness without live services.
  Live smoke requires manual service start — see steps above.
```
