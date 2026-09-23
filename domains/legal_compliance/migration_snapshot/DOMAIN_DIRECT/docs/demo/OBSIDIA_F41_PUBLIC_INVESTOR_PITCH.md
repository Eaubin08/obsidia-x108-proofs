# Obsidia X-108 — Public Investor Pitch (F41 RC1)

**Mode:** READONLY · KX108_ONLY · emits_act=false  
**Date:** 2026-05-29

---

## One-liner

> **Obsidia X-108 is a deterministic governance kernel that enforces a hard boundary between advisory AI and decision authority — by construction, not by convention.**

---

## The Problem

AI systems deployed in high-stakes environments (financial transactions, air traffic, medical decisions, defense logistics) increasingly act as decision-makers — but their guardrails are enforced by convention: prompts, guidelines, post-hoc filters. These fail silently, are invisible to auditors, and cannot be formally verified.

**The industry doesn't have a trustable enforcement boundary. It has a suggestion.**

Regulatory frameworks (EU AI Act, financial sector AI governance requirements) are tightening around this exact gap: demonstrable, auditable proof that an AI component is not the decision authority. Today, no mainstream solution provides this proof at the architecture layer.

---

## What Obsidia X-108 Does

Obsidia X-108 is a kernel-layer governance component. It intercepts every AI-generated output before it reaches an execution surface, checks it against a deterministic rule engine, and ensures the AI operates as advisory context only — never as a decision authority.

**Brody** (the advisory AI component) consults 7 runtime surfaces (nominal configuration — reported dynamically at runtime) and generates context-only responses. It cannot decide, execute, or mutate state. This constraint is not a configuration — it is enforced simultaneously at:

1. **Module level** — every Python function returns a 15-flag BOUNDARY dict
2. **Route level** — every FastAPI endpoint calls `safe_backend_response()` which enforces the boundary
3. **Response level** — a word-boundary regex scan verifies absence of forbidden decision tokens in every output

---

## The Live Demo

Start the server (any machine with Python + FastAPI):

```powershell
python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8011
```

Call the multi-domain advisory endpoint (4 domains in a single packet):

```powershell
$resp = (Invoke-WebRequest "http://127.0.0.1:8011/api/periphery/brody-runtime/f38/multi-domain-scenarios" `
  -Method POST -Body "{}" -ContentType "application/json" -UseBasicParsing).Content | ConvertFrom-Json
$resp | Select-Object packet_id, global_status, scenario_count, all_mutations_false, forbidden_tokens_found
```

Every response carries — verifiable live:

| Field | Value |
|-------|-------|
| `decision_authority` | `KX108_ONLY` |
| `allowed_to_decide` | `false` |
| `emits_act` | `false` |
| `kernel_mutation` | `false` |
| `x108_mutation` | `false` |
| `neo4j_write` | `false` |

---

## Core Proof (F40 RC1 — verified 2026-05-29)

| Metric | Value |
|--------|-------|
| Palier chain | F32 → F39 (10 paliers, incl. F34B/F36B) |
| Git tags | 10/10 present |
| Unit tests | **103/103 PASS** |
| Smoke checks (cumulative) | **474** |
| Live-server proofs | **3** (F34B port 9010, F36B port 8011, F38 port 8011) |
| API routes | 7 READY_READONLY |
| Forbidden decision tokens found | **0** |
| Mutation flags triggered | **0** |

The proof chain is fully traceable: each palier has a git tag, a SHA256-signed proof JSON, a markdown report, and at least one smoke script.

---

## Why It Matters

**For regulators and auditors:** Obsidia provides machine-readable, SHA256-signed proof that an AI component is not the decision authority. The proof is verifiable independently from the codebase (run the tests yourself, check the git tags, inspect the live server).

**For system integrators:** Obsidia wraps the output layer — the underlying AI model is unchanged. The boundary enforcement layer is model-agnostic.

**For compliance teams:** Every response carries a BOUNDARY dict that can be logged, hashed, and archived for regulatory audit trails. `decision_authority=KX108_ONLY` appears in every packet — no exceptions.

**For operators:** A live HTML dashboard (`/api/periphery/operator/runtime-panel.html`) shows READY_READONLY status and boundary flags in real time.

---

## Domains Demonstrated

| Domain | Status | Surfaces |
|--------|--------|----------|
| `bank` — financial transactions | READY_READONLY | 7 |
| `gps_defense_aviation` — precision navigation | READY_READONLY | 7 |
| `trading` — financial markets | READY_READONLY | 7 |
| `unknown_refusal` — out-of-scope rejection | REFUSAL_READONLY | — |

---

## Current Stage

**F40 RC1 — Demo-ready, audit-ready.**

This is a proof-of-concept demonstration layer. The boundary enforcement is verified by runtime smoke tests and unit tests (not formal Lean proof at this layer). The KX108 kernel is referenced as decision authority; full kernel integration is the F50+ roadmap. See `OBSIDIA_F41_WHAT_IT_PROVES_AND_DOES_NOT_PROVE.md` for a full honest audit of the proof perimeter.

---

## Competitive Positioning

| Approach | Boundary enforcement | Auditable proof | Model-agnostic |
|----------|---------------------|-----------------|----------------|
| System prompts | Convention only | No | Yes |
| RLHF fine-tuning | Internal/behavioral | No | No |
| Post-hoc filters | Output layer | Partial | Yes |
| **Obsidia X-108** | **Architecture layer** | **Yes (SHA256, git tags, 103 tests)** | **Yes** |

---

*F41 RC1 · Public Investor Pitch · READONLY · KX108_ONLY · Generated 2026-05-29*
