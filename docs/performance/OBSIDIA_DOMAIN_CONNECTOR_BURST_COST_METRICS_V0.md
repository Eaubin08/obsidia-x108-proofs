# Obsidia Domain Connector Burst Cost Metrics V0

## Status

Document type: live measurement correction
Status: V0
Scope: Bank / Trading / GPS domain connector cost metrics
Decision authority: KX108_ONLY

---

## 1. Problem

The domain connector scripts can behave like long-running live processes.

Therefore, measuring them as commands that must terminate can block the cost runner.

---

## 2. Correction

Domain connector metrics are measured as bounded bursts.

The connector is started, allowed to run for a short live window, then stopped.

This records a cost event without treating a live connector as a finite command.

---

## 3. Routes

| Domain | Route |
|---|---|
| Bank | /api/live/kernel/adapters/bank |
| Trading | /api/live/kernel/adapters/trading |
| GPS/Aviation | /api/live/kernel/adapters/gps |

---

## 4. Command

Run:

    .\scripts\performance\run_domain_connector_burst_cost_metrics_v0.ps1 -ApiBase "http://127.0.0.1:8000" -BurstSeconds 10

---

## 5. Boundary

This script measures live connector bursts.

It does not decide.

It does not emit ACT.

It does not write memory.

X108 remains the decision authority.
