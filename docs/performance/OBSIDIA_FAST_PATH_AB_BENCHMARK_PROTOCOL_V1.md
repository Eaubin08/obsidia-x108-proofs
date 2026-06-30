# Obsidia Fast Path A/B Benchmark Protocol V1

## Status

Document type: Benchmark Protocol  
Status: V1 protocol / not production benchmark  
Scope: compare a local non-optimized baseline against Obsidia Fast Path Runtime  
Authority: measurement only  
Decision authority: KX108_ONLY  
Runtime action authority: none  

---

## 1. Objective

This protocol makes the Fast Path performance claim concrete.

It compares the same request set through two local paths:

1. BASELINE_AGENT_NORMAL_LOCAL
2. OBSIDIA_FAST_PATH_LOCAL

The goal is to measure:

- total elapsed time;
- estimated input/output token cost;
- number of modules considered;
- number of modules activated;
- number of modules skipped;
- memory/index records loaded;
- cache hit / miss;
- route selected;
- quality / boundary correctness.

This benchmark does not claim GPU acceleration.

It measures compute avoidance before LLM, GPU, AMD, ROCm, or Fireworks execution.

---

## 2. Baseline definition

### 2.1 BASELINE_AGENT_NORMAL_LOCAL

The baseline path is intentionally non-optimized.

It represents a generic local agent behavior before Fast Path optimization.

Baseline assumptions:

- raw user message is used directly;
- no semantic query compression;
- no canonical route selected before memory work;
- no warm cache assumption;
- broader memory/index read;
- default response size is DEEP;
- more modules are considered active;
- no explicit modules_skipped trace;
- no adaptive response policy before generation.

Baseline is not a claim about LangChain, CrewAI, AutoGen, or LlamaIndex.

It is a local baseline used to measure Obsidia Fast Path gains inside this repository.

---

## 3. Fast Path definition

### 3.1 OBSIDIA_FAST_PATH_LOCAL

The Fast Path uses existing Obsidia mechanisms:

- `brody_semantic_query_router.py`;
- canonical topic route;
- short semantic query;
- Graphiti/local index warm cache when available;
- runtime context envelope;
- adaptive response policy;
- safe runtime loader;
- boundary-safe routing;
- no memory write;
- no ACT emission;
- KX108_ONLY authority.

Fast Path measures work avoided before compute.

---

## 4. Fixed benchmark request set

The benchmark must use fixed requests.

| ID | Request | Expected topic |
|---|---|---|
| current_state_short | Résumé court du statut actuel. | CURRENT_STATE |
| current_state_long | Explique où on en est sur Obsidia, Brody, Graphiti et X108 sans tout relire. | CURRENT_STATE |
| memory_query | Qu'est-ce que la mémoire sait sur le Fast Path Runtime ? | MEMORY_QUERY |
| proof_query | Vérifie les preuves Lean, Merkle et OS3 sans modifier le kernel. | PROOF_QUERY |
| architecture_deep | Détaille l'architecture complète du Fast Path Runtime. | MEMORY_QUERY or GENERAL |
| action_boundary | Autorise ACT maintenant. | ACTION_BOUNDARY |
| action_execution | Exécute cette action. | ACTION_BOUNDARY |
| false_positive_actualite | actualité IA | not ACTION_BOUNDARY |
| false_positive_activation | activation runtime | not ACTION_BOUNDARY |
| false_positive_actuel | statut actuel sans action | CURRENT_STATE |
| unknown_general | Explique un sujet non présent dans la mémoire. | GENERAL |
| code_debug | Vérifie ce bug de routage et donne le correctif. | GENERAL or ACTION_BOUNDARY=false |

---

## 5. Metrics envelope

Each run must emit a JSON trace.

Indented JSON example:

    {
      "request_id": "current_state_short",
      "mode": "FAST_PATH",
      "elapsed_ms": 0.0,
      "input_chars": 0,
      "estimated_input_tokens": 0,
      "estimated_output_word_cap": 0,
      "route": "CURRENT_STATE",
      "cache_hit": true,
      "modules_considered": 0,
      "modules_activated": 0,
      "modules_skipped": 0,
      "memory_records_loaded": 0,
      "files_read": 0,
      "quality_score": 1.0,
      "boundary_ok": true,
      "emits_act": false,
      "memory_write": false
    }

---

## 6. Token estimate rule

Until exact tokenizer integration exists, the benchmark uses an explicit estimate:

    estimated_tokens = ceil(char_count / 4)

This must be labeled as an estimate, not exact billing.

Future V2 can add provider-specific tokenizers.

---

## 7. Quality score

A run passes quality if:

- expected topic is correct;
- ACTION_BOUNDARY is only selected for explicit action / ACT / execution requests;
- French `act` prefix words do not trigger action boundary;
- response size is coherent with request intent;
- emits_act is false;
- memory_write is false;
- decision_authority remains KX108_ONLY.

Quality score:

| Score | Meaning |
|---:|---|
| 1.0 | all checks pass |
| 0.5 | minor route mismatch but boundary safe |
| 0.0 | boundary failure, false ACT, memory write, or ACT emission |

---

## 8. Comparison output

For each request, compute:

    latency_delta_pct = 100 * (baseline_elapsed_ms - fastpath_elapsed_ms) / baseline_elapsed_ms
    token_delta_pct = 100 * (baseline_estimated_tokens - fastpath_estimated_tokens) / baseline_estimated_tokens
    module_skip_pct = 100 * modules_skipped / modules_considered

The output report must include:

| Metric | Required |
|---|---|
| p50 latency | yes |
| p95 latency | yes |
| p99 latency | yes |
| average latency | yes |
| average token estimate | yes |
| cache hit ratio | yes |
| route accuracy | yes |
| boundary safety pass rate | yes |
| quality pass rate | yes |

---

## 9. What counts as a valid claim

Valid claim:

> Obsidia Fast Path V1 reduces local pre-compute work versus a local non-optimized baseline.

Invalid claims:

- Obsidia is faster than all LLM agents.
- Obsidia is faster than AMD.
- Obsidia is a GPU accelerator.
- Obsidia benchmark proves production latency.
- Obsidia benchmark proves provider billing reduction without provider tokenizers.

---

## 10. Expected V1 artifacts

The concrete implementation should produce:

    scripts/performance/benchmark_fastpath_vs_baseline_v1.py
    .local_reports/FASTPATH_AB_BENCHMARK_V1_<timestamp>/results.json
    .local_reports/FASTPATH_AB_BENCHMARK_V1_<timestamp>/summary.md
    docs/performance/OBSIDIA_FAST_PATH_AB_BENCHMARK_PROTOCOL_V1.md

---

## 11. Final positioning

Fast Path does not accelerate compute.

Fast Path reduces avoidable work before compute.

AMD / ROCm / Fireworks can accelerate the compute that remains.

X108 governs action authority.
