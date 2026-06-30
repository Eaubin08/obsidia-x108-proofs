# Obsidia Live Stack Cost Metrics V0

## Status

Document type: live measurement runbook  
Status: V0  
Scope: Kernel 3001, API/Brody 8000, Graphiti 8011, UI 5173, domain connectors  
Decision authority: KX108_ONLY  

---

## 1. Objective

The Request Cost Ledger must measure real executions while the servers are running.

Read-only family scans are useful, but they are not sufficient for live route metrics.

This runbook starts the live stack and records cost events for real routes.

---

## 2. Real measured routes

| Component | Route |
|---|---|
| API root | / |
| Brody chat | /api/brody/chat |
| Graphiti status | /graph/v20/frozen/status |
| UI Workbench | 5173 root |
| Bank connector | /api/live/kernel/adapters/bank |
| Trading connector | /api/live/kernel/adapters/trading |
| GPS/Aviation connector | /api/live/kernel/adapters/gps |

---

## 3. Output

Cost events are appended to:

    .local_reports/REQUEST_COST_EVENTS/cost_events.jsonl

---

## 4. Command

Run:

    .\scripts\performance\run_live_stack_cost_metrics_v0.ps1

---

## 5. Boundary

This script launches servers and measures routes.

It does not change decision authority.

It does not emit ACT.

It does not write memory.

X108 remains the decision authority.
