# Obsidure Real Case Cost Metrics V0

## Status

Document type: real-case measurement runbook
Status: V0
Scope: Obsidure code, proposal/apply surface, Lean proof checks
Decision authority: KX108_ONLY

---

## 1. Problem

The previous live route metrics covered:

- API
- Brody
- Graphiti
- UI
- Bank
- Trading
- GPS/Aviation

But they did not measure Obsidure.

Obsidure is not a live HTTP domain route. It is a code/proof execution chain:

    proposal -> apply/check -> Lean/pytest -> repair loop -> validated commit

---

## 2. Added Obsidure families

| Family | Meaning |
|---|---|
| OBSIDURE_CODE | CLI, runner scripts, apply proposal surface, Python Obsidure scripts |
| OBSIDURE_LEAN | Lean proof surface manifest and real Lean checks |

---

## 3. Measured cases

OBSIDURE_CODE:

- obsidure_cli_py_compile
- obsidure_agent_runner_ps1_present
- obsidure_apply_proposal_ps1_present
- run_obsidure_scripts_py_compile

OBSIDURE_LEAN:

- lean_proof_surface_manifest_generate
- targeted lake env lean checks over selected proof files

---

## 4. Output

Every case appends one cost_event to:

    .local_reports/REQUEST_COST_EVENTS/cost_events.jsonl

A run summary is written to:

    .local_reports/OBSIDURE_REAL_CASE_COST_METRICS_<timestamp>/summary.json
    .local_reports/OBSIDURE_REAL_CASE_COST_METRICS_<timestamp>/summary.md

---

## 5. Boundary

This runner measures Obsidure execution cost.

It does not apply unknown proposals.

It does not emit ACT.

It does not write memory.

It does not alter X108 authority.

X108 remains the decision authority.
