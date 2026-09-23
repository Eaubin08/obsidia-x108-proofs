# Obsidia Fast Path Runtime — Technical Note V0

## Status

Document type: Technical Note  
Status: V0 / evidence-backed draft  
Authority: non-sovereign runtime optimization layer  
Decision authority: KX108_ONLY  
Runtime action authority: none  
Scope: latency, token-cost, routing, cache, context minimization

---

## 1. Executive summary

Obsidia Fast Path Runtime is not CUDA, ROCm, or a GPU runtime.

It is an architectural optimization layer designed to reduce latency, token cost, and unnecessary runtime work before compute is invoked.

Core principle:

> Before calculating faster, Obsidia avoids calculating, reading, routing, hydrating, or generating what is not necessary.

Current implementation evidence shows several concrete mechanisms:

- one primary layer and one active mode per task;
- canonical semantic queries instead of raw full-sentence memory queries;
- Graphiti JSONL index cache;
- compact runtime context envelope;
- short service timeouts and fallback behavior;
- adaptive response sizing;
- safe runtime module loading;
- dry-run-only bus routing.

---

## 2. Problem

Agentic systems often lose speed because they do too much work before producing a useful answer.

Typical latency sources:

1. activating too many agents or modes;
2. loading too much context;
3. querying memory with raw long prompts;
4. rescanning indexes repeatedly;
5. waiting too long for unavailable services;
6. generating long answers when short answers are enough;
7. crashing or blocking when one module is missing;
8. mixing propose/action paths too early.

Obsidia Fast Path Runtime addresses these issues by reducing work before compute.

---

## 3. Core architecture

Flow:

    User request
       ↓
    Agent Router
       ↓
    Semantic Query Router
       ↓
    Memory / Graphiti Cache
       ↓
    Runtime Context Adapter
       ↓
    Adaptive Response Policy
       ↓
    Readonly Response / Dry-run Bus

The objective is not to replace GPU acceleration.

The objective is to reduce the amount of work that must reach the compute layer.

---

## 4. Mechanism 1 — Agent Router

The local agent router classifies the request at the start of a task.

It chooses:

- one primary layer;
- one active mode;
- excluded modes;
- one next action.

This prevents multi-agent overactivation.

Principle:

    one request = one primary layer = one active mode

Effect on latency:

- fewer modules activated;
- less context loaded;
- fewer irrelevant branches explored;
- lower token cost.

---

## 5. Mechanism 2 — Semantic Query Router

The semantic query router converts the raw user message into a canonical query.

It does not send raw full-sentence queries to Neo4j.

It produces:

- topic;
- semantic_query;
- primary_query;
- fallback_queries;
- normalized_message;
- route.

Effect on latency:

- shorter memory queries;
- less noisy search;
- fewer irrelevant memory results;
- faster memory retrieval;
- lower hydration cost.

---

## 6. Mechanism 3 — Graphiti index cache

The memory response chain adapter uses a process-level cache:

    _GRAPHITI_INDEX_CACHE

The Graphiti JSONL index is loaded once per process and reused.

Effect on latency:

- avoids repeated JSONL parsing;
- reduces disk reads;
- speeds up repeated memory queries;
- improves local fallback speed.

---

## 7. Mechanism 4 — Runtime context envelope

The runtime context adapter assembles one top-level runtime_context from existing snapshots.

It does not invent new content.

It reuses already-produced snapshots:

- semantic query snapshot;
- authority snapshot;
- session memory snapshot;
- project memory snapshot;
- memory response chain snapshot;
- freeze metrics snapshot;
- automation snapshot;
- tree policy snapshot;
- temporal context snapshot;
- cognitive module snapshot;
- domain sigma envelope snapshot.

Effect on latency:

- compact context structure;
- less repeated assembly;
- easier frontend/backend access;
- lower context overhead.

---

## 8. Mechanism 5 — Short service timeouts and fallback

The runtime checks service availability with short socket timeouts.

Examples:

- Neo4j check timeout: 1.5 seconds;
- Graphiti / port probe timeout: 1 second.

If Neo4j or Graphiti is unavailable, the pipeline can fallback to:

- frozen Graphiti readonly;
- local index;
- terminal response fallback;
- backend stub last resort.

Effect on latency:

- avoids long blocking waits;
- keeps the pipeline responsive;
- surfaces real status instead of pretending success.

---

## 9. Mechanism 6 — Adaptive response sizing

The adaptive response policy classifies answer size:

- SHORT;
- MEDIUM;
- DEEP;
- BOUNDARY_COMPACT.

It considers:

- explicit user size hint;
- request type;
- domain;
- risk flags;
- memory availability;
- sigma pressure;
- boundary detection;
- observed answer size.

Effect on latency and token cost:

- shorter answer when memory is absent;
- compact answer for boundary/risk requests;
- deeper answer only when domain complexity requires it;
- less overgeneration.

---

## 10. Mechanism 7 — Runtime loader

The runtime loader imports modules safely and reports real status:

- REAL_MODULE;
- BACKEND_STUB;
- MODULE_ERROR.

Effect on latency and stability:

- missing modules do not crash the full pipeline;
- module errors are surfaced honestly;
- fallback paths remain available;
- runtime startup remains predictable.

---

## 11. Mechanism 8 — Dry-run-only bus router

The bus router is dry-run only.

It enforces:

    DRY_RUN_ONLY = True

It refuses ACTION modules at registration time.

Effect:

- proposal routing remains lightweight;
- no heavy or dangerous action path is triggered;
- action authority remains outside the bus;
- X108 remains the sole decision authority.

---

## 12. Evidence found in local repo

| Evidence family | Local evidence |
|---|---|
| Agent routing | `.agents/skills/agent-router-obsidia/SKILL.md` |
| Agentic routing doctrine | `.claude/context/AGENTIC_ROUTING.md` |
| Semantic query routing | `apps/obsidia_api/brody_semantic_query_router.py` |
| Runtime context envelope | `apps/obsidia_api/brody_runtime_context_adapter.py` |
| Memory response chain | `apps/obsidia_api/brody_memory_response_chain_adapter.py` |
| Graphiti index cache | `_GRAPHITI_INDEX_CACHE` |
| Adaptive response policy | `apps/obsidia_api/brody_adaptive_response_policy.py` |
| Runtime loader | `apps/obsidia_api/runtime_loader.py` |
| Dry-run bus | `apps/obsidia_api/bus/router.py` |
| Validation scale | `pytest tests/ -q --tb=short → 3667 passed in 192.80s` |

---

## 13. What this is not

Obsidia Fast Path Runtime is not:

- CUDA;
- ROCm;
- a GPU kernel;
- a low-level tensor runtime;
- a replacement for AMD/Nvidia compute;
- a sovereign decision layer;
- a full Thermodynamic Path Engine runtime;
- an action executor.

It does not emit ACT.

It does not emit ALLOW / HOLD / BLOCK.

It does not mutate X108.

It does not write memory.

It does not replace GuardX108.

---

## 14. Relationship with AMD / Fireworks

AMD / ROCm / Fireworks can accelerate the compute that remains necessary.

Obsidia Fast Path Runtime reduces what must be sent to compute.

Positioning:

    AMD accelerates execution.
    Obsidia Fast Path reduces unnecessary execution.
    X108 governs action authority.

For an AMD hackathon, this can become:

    User request
       ↓
    Obsidia Fast Path
       ↓
    local answer / memory answer / Fireworks call / HOLD
       ↓
    token and latency trace
       ↓
    X108 boundary

The value is not “we built CUDA.”

The value is:

> We built an architectural fast path that decides when compute is needed, how much context is needed, and how large the response should be.

---

## 15. Technical positioning sentence

Obsidia Fast Path Runtime is a non-GPU architectural optimization layer that reduces latency and token cost through targeted routing, semantic query compression, memory cache reuse, compact runtime context, adaptive response sizing, safe fallback, and dry-run routing.

---

## 16. Current status

Current status: V0 documented and evidence-backed.

Implemented or evidenced:

- routing doctrine;
- semantic query routing;
- cache pattern;
- compact runtime context;
- adaptive response policy;
- safe runtime loader;
- dry-run bus;
- test-scale evidence.

Not yet implemented as a single packaged product:

- benchmark dashboard;
- latency before/after measurements;
- token-cost dashboard;
- AMD/Fireworks routing adapter;
- formal Fast Path API contract;
- public demo trace.

---

## 17. Next recommended work

1. Add a small benchmark script measuring:
   - raw query path;
   - semantic query path;
   - cache cold start;
   - cache warm path;
   - adaptive SHORT / MEDIUM / DEEP response sizes.

2. Add a Fast Path trace envelope:
   - route_selected;
   - modules_skipped;
   - context_items_loaded;
   - cache_hit;
   - graphiti_status;
   - response_size;
   - estimated_tokens_saved;
   - elapsed_ms.

3. Add AMD/Fireworks routing later:
   - local answer when enough;
   - Fireworks call when remote model needed;
   - HOLD when cost/risk/material is insufficient.

---

## 18. Final formula

Latency reduction:

    less activation
    + shorter queries
    + cached memory
    + compact context
    + bounded generation
    + fast fallback

Compute separation:

    Compute acceleration = AMD / ROCm / Fireworks
    Compute avoidance = Obsidia Fast Path Runtime
    Decision authority = X108


---

## 19. Benchmark V0 â€” local measured metrics

Status: local microbenchmark / V0.

This section adds measured local numbers. It does not claim production-grade benchmarking yet.

- Branch: `feat/path-brody-r02-thermo-mcp-closure`
- HEAD: `8f80edb5d151913027c35ba4c9703ee34dc5fbe4`

### 19.1 Existing recorded validation

| Metric | Value |
|---|---:|
| Tests passed | 3667 |
| Total time | 192.8 s |
| Throughput | 19.02 tests/s |

### 19.2 Semantic query compression

| Case | Topic | Raw chars | Semantic query chars | Query reduction | Avg route time |
|---|---|---:|---:|---:|---:|
| Explique moi exactement oÃ¹ on en est sur O... | `X108` | 142 | 32 | 77.46% | 0.0519 ms |
| Je veux savoir pourquoi la latence baisse ... | `GENERAL` | 121 | 20 | 83.47% | 0.1743 ms |
| Peux-tu vÃ©rifier les preuves Lean, Merkle,... | `X108` | 112 | 32 | 71.43% | 0.0347 ms |
| RÃ©sumÃ© court du statut actuel.... | `CURRENT_STATE` | 30 | 25 | 16.67% | 0.1187 ms |
| DÃ©taille l'architecture complÃ¨te du Fast P... | `MEMORY_QUERY` | 105 | 32 | 69.52% | 0.0856 ms |

### 19.3 Graphiti local index cache

| Metric | Value |
|---|---:|
| Records loaded | 3267 |
| Cold load | 277.718 ms |
| Warm load | 0.3199 ms |
| Warm speedup | 868.14x |
| Latency reduction | 99.88% |

### 19.4 Runtime context assembly

| Metric | Value |
|---|---:|
| Repetitions | 1000 |
| Min | 0.0032 ms |
| Avg | 0.0042 ms |
| Max | 0.1223 ms |
| Boundary readonly | True |

### 19.5 Adaptive response policy

| Case | Response size | Estimated word cap | Saving vs DEEP cap | Avg policy time |
|---|---|---:|---:|---:|
| short_user_hint | `SHORT` | 55 | 85.53% | 0.0068 ms |
| deep_user_hint | `DEEP` | 380 | 0.0% | 0.0124 ms |
| boundary_action | `BOUNDARY_COMPACT` | 80 | 78.95% | 0.0161 ms |
| memory_available | `MEDIUM` | 180 | 52.63% | 0.0163 ms |
| no_memory | `SHORT` | 55 | 85.53% | 0.0086 ms |

### 19.6 Runtime loader

| Metric | Value |
|---|---:|
| First call | 47.6648 ms |
| Warm avg | 0.0042 ms |
| Warm speedup | 11348.76x |

Component statuses:

| Component | Status |
|---|---|
| `brody` | `REAL_MODULE` |
| `language` | `REAL_MODULE` |
| `context` | `REAL_MODULE` |
| `x108_ingress` | `REAL_MODULE` |
| `reverse_os` | `REAL_MODULE` |
| `memory` | `REAL_MODULE` |
| `graphiti` | `REAL_MODULE` |
| `gencoin` | `REAL_MODULE` |

### 19.7 External dependency offline probe — not internal Fast Path speed

| Metric | Value |
|---|---:|
| Probe time | 2011.8792 ms |
| Status | `GRAPHITI_UNAVAILABLE` |
| Neo4j status | `NEO4J_BLOCKED` |
| Graphiti V20 status | `GRAPHITI_V20_FROZEN_UNAVAILABLE` |
| Port 7688 open | False |
| Port 8011 open | False |

### 19.8 Internal vs external interpretation

The microsecond / low-millisecond measurements above are internal Fast Path measurements.

The offline service probe is different: it measures an external dependency timeout path when Neo4j and Graphiti are unavailable. It must not be compared directly to runtime_context assembly or adaptive policy timings.

For reporting, the service probe should be read as bounded offline fallback behavior, not as internal compute latency.

V1 target: reduce offline dependency probe below 500 ms through shorter bounded timeouts, parallel probing, or short-lived service availability cache.

### 19.9 Interpretation

The current V0 numbers measure compute avoidance, not GPU acceleration.

The gains come from:

- semantic query compression before memory search;
- cache warm path instead of repeated JSONL reads;
- sub-millisecond or low-millisecond routing/context policy functions when imports are warm;
- bounded answer size instead of default deep generation;
- fallback behavior instead of long blocking service waits.

This supports the technical claim:

> Obsidia Fast Path reduces the amount of work sent to compute. AMD / ROCm / Fireworks can then accelerate the compute that remains.


