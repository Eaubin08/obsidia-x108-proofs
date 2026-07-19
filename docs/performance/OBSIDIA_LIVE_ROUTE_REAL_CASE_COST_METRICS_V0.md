# Obsidia Live Route Real Case Cost Metrics V0

## Status

Document type: live real-case measurement runbook
Status: V0
Scope: API, Brody, Bank, Trading, GPS/Aviation, Graphiti, UI
Decision authority: KX108_ONLY

---

## 1. Correction

Live connectors are not finite tests.

They are live processes.

Therefore, cost metrics must be collected by injecting real cases into live HTTP routes, not by waiting for connector scripts to terminate.

---

## 2. Measured live routes

| Family | Route |
|---|---|
| RUNTIME_API | / |
| BRODY_CHAT | /api/brody/chat |
| BRODY_MEMORY | /graph/v20/frozen/status |
| RUNTIME_API | UI_WORKBENCH_5173 |
| DOMAIN_BANK | /api/live/kernel/adapters/bank |
| DOMAIN_TRADING | /api/live/kernel/adapters/trading |
| DOMAIN_GPS_AVIATION | /api/live/kernel/adapters/gps |

---

## 3. Real cases

Bank uses existing sigma examples:

- bank_normal
- bank_suspicious
- bank_blocked

GPS/Aviation uses existing sigma examples:

- gps_brownout
- gps_no_source
- gps_source_conflict
- gps_time_skew

Trading uses bounded synthetic terrain scenarios until canonical trading JSON examples are added:

- trading_normal_signal
- trading_flashcrash

Brody uses readonly chat cases.

---

## 4. Output

Every case appends one cost_event to:

    .local_reports/REQUEST_COST_EVENTS/cost_events.jsonl

A run summary is written to:

    .local_reports/LIVE_ROUTE_REAL_CASE_COST_METRICS_<timestamp>/summary.json
    .local_reports/LIVE_ROUTE_REAL_CASE_COST_METRICS_<timestamp>/summary.md

---

## 5. Boundary

This runner measures routes.

It does not emit ACT.

It does not write memory.

It does not alter X108 authority.

X108 remains the decision authority.
