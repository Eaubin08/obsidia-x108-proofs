# OBSIDIA F35.0 — OPERATOR / DEMO SURFACE AUDIT

Mode: AUDIT_ONLY_NO_PATCH
Commit: NO
Tag: NO
Push: NO

HEAD: `afce5b3`
Tags on HEAD: `BRODY_F34B_TRUE_LIVE_UVICORN_SERVER_SMOKE_PALIER_20260529`

## Live 8000 probe

```json
{"root_status":200,"total_routes":135,"f33_route_found":true,"workflow_route_found":true,"monitor_route_count":9}
```

## Summary

- Scanned files: 2493
- Active operator/demo records: 573
- Danger records: 1

## Candidate surfaces

- `F35_C01` — Operator Live Runtime Panel
  - purpose: Afficher la réponse F33/F34B live sur 8000 avec 7 surfaces READY et boundary KX108_ONLY.
  - route_needed: `GET /api/operator/runtime-panel or static HTML`
  - risk: LOW if readonly only
- `F35_C02` — Investor Demo Packet
  - purpose: Transformer la preuve runtime en endpoint/report lisible investisseur.
  - route_needed: `GET /api/demo/runtime-readiness`
  - risk: LOW if report-only
- `F35_C03` — Workbench Connector Surface
  - purpose: Brancher une surface opérateur sur F33 + workflow governance + monitor.
  - route_needed: `HTML/JSON readonly`
  - risk: MEDIUM if UI starts mixing runtime/context layers

## Recommendation

```text
NEXT_BEST_PALIER=F35.1_OPERATOR_LIVE_RUNTIME_PANEL_READONLY
WHY=F34B proves live backend readiness; next useful layer is an operator-readable readonly surface.
```

## Danger records

- `periphery/workflow_governance_readonly/repo_aware/obsidia_x108_repo_map.py`
  - L78 `write_transaction` — "session.write_transaction",
  - L79 `execute_write` — "execute_write",
  - L87 `os.system` — "os.system(",

## Boundary

```text
DECISION_AUTHORITY=KX108_ONLY
readonly=true
advisory_only=true
context_signal_only=true
emits_act=false
runtime_execute=false
kernel_mutation=false
x108_mutation=false
memory_write=false
graphiti_write=false
neo4j_write=false
```

## Status

F35_0_OPERATOR_DEMO_SURFACE_AUDIT_DONE
