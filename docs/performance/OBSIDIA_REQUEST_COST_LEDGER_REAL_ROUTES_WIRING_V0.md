# Obsidia Request Cost Ledger Real Routes Wiring V0

## Status

Document type: wiring note
Status: V0 controlled wiring
Scope: real Obsidia routes and connectors
Runtime mutation: none
Decision authority: KX108_ONLY

---

## 1. Real routes

| Component | Port | Route |
|---|---:|---|
| Kernel Ragnarok | 3001 | /kernel/ragnarok |
| API Obsidia / Brody | 8000 | / |
| Brody Chat | 8000 | /api/brody/chat |
| Bank domain adapter | 8000 | /api/live/kernel/adapters/bank |
| Trading domain adapter | 8000 | /api/live/kernel/adapters/trading |
| GPS domain adapter | 8000 | /api/live/kernel/adapters/gps |
| Graphiti / ObsidiaShell | 8011 | /graph/v20/frozen/status |
| UI Workbench | 5173 | / |
| Neo4j Browser | 7475 | /browser |
| Neo4j Bolt | 7688 | bolt |

---

## 2. Added files

| File | Role |
|---|---|
| apps/obsidia_api/request_cost_event_writer.py | shared cost event builder and JSONL writer |
| scripts/performance/run_with_cost_event_v0.py | run any real command and append a cost event |
| scripts/run_costed_v0.ps1 | generic costed command wrapper |
| scripts/run_brody_route_costed_v0.ps1 | costed Brody /api/brody/chat wrapper |
| scripts/run_bank_route_costed_v0.ps1 | costed Bank connector wrapper |
| scripts/run_trading_route_costed_v0.ps1 | costed Trading connector wrapper |
| scripts/run_gps_route_costed_v0.ps1 | costed GPS/Aviation connector wrapper |
| scripts/run_graphiti_route_costed_v0.ps1 | costed Graphiti status wrapper |

---

## 3. Output

Each measured run appends one event to:

    .local_reports/REQUEST_COST_EVENTS/cost_events.jsonl

---

## 4. Usage

Brody route:

    .\scripts\run_brody_route_costed_v0.ps1 -Base "http://127.0.0.1:8000" -Message "Test Brody readonly stack."

Bank:

    .\scripts\run_bank_route_costed_v0.ps1 -ApiBase "http://127.0.0.1:8000"

Trading:

    .\scripts\run_trading_route_costed_v0.ps1 -ApiBase "http://127.0.0.1:8000"

GPS/Aviation:

    .\scripts\run_gps_route_costed_v0.ps1 -ApiBase "http://127.0.0.1:8000"

Graphiti:

    .\scripts\run_graphiti_route_costed_v0.ps1 -GraphBase "http://127.0.0.1:8011"

---

## 5. Boundary

This V0 does not decide.

This V0 does not emit ACT.

This V0 does not write memory.

It only measures the cost of real executions and real routes.

X108 governs action authority.
