# Obsidia Request Cost Ledger Protocol V0

## Status

Document type: Cost Measurement Protocol  
Status: V0 protocol  
Scope: Brody, real domains, Obsidure, Guard/X108, Sigma, runtime API  
Authority: measurement only  
Decision authority: KX108_ONLY  
Runtime action authority: none  

---

## 1. Objective

Obsidia must calculate the cost of every meaningful request family.

The goal is not only to measure Fast Path.

The goal is to measure:

- Brody request cost;
- memory / Graphiti / Neo4j cost;
- real domain cost;
- Obsidure generation and proof cost;
- Guard / X108 / Sigma cost;
- runtime API cost;
- cost avoided by routing, cache, compression, and boundary logic.

This ledger measures internal Obsidia cost.

It does not measure OpenAI billing, Fireworks billing, or any third-party invoice.

---

## 2. Cost families

| Family | Meaning |
|---|---|
| BRODY_CHAT | standard Brody response request |
| BRODY_MEMORY | memory, Graphiti, Neo4j, local index, context hydration |
| BRODY_FASTPATH | pre-compute optimized request path |
| DOMAIN_BANK | bank terrain proof request |
| DOMAIN_TRADING | trading / market risk request |
| DOMAIN_GPS_AVIATION | GPS / aviation / field-signal request |
| OBSIDURE_LEAN | Lean theorem / proof generation / repair request |
| OBSIDURE_CODE | code generation / patch / test / commit request |
| X108_GUARD | Guard decision boundary evaluation |
| SIGMA_REPORT | Sigma alert, report, freeze, or diagnostic |
| RUNTIME_API | local API route / bridge / adapter request |
| UNKNOWN | request family not classified yet |

---

## 3. Universal request cost envelope

Every measured request should emit one cost envelope.

Indented JSON shape:

    {
      "request_id": "REQ_20260630_000001",
      "trace_id": "TRACE_20260630_000001",
      "family": "BRODY_CHAT",
      "route": "CURRENT_STATE",
      "status": "PASS",
      "started_at": "2026-06-30T19:15:00+02:00",
      "ended_at": "2026-06-30T19:15:00+02:00",
      "elapsed_ms": 0.0,

      "internal_token_units_in": 0,
      "internal_token_units_out": 0,
      "internal_token_units_total": 0,
      "internal_token_estimate_method": "ceil(char_count / 4)",
      "native_token_ledger_available": false,

      "modules_considered": 0,
      "modules_activated": 0,
      "modules_skipped": 0,

      "files_read": 0,
      "files_written": 0,
      "memory_records_read": 0,
      "memory_records_written": 0,
      "cache_hit": false,
      "cache_miss": false,

      "domain_agents_used": 0,
      "domain_votes": 0,
      "domain_aggregates": 0,
      "contradictions": 0,
      "unknowns": 0,
      "risk_flags": 0,

      "guard_invoked": false,
      "guard_result": "NOT_INVOKED",
      "sigma_invoked": false,
      "sigma_reports": 0,

      "lean_runs": 0,
      "pytest_runs": 0,
      "repair_iterations": 0,

      "decision_authority": "KX108_ONLY",
      "emits_act": false,
      "memory_write": false,
      "proof_ready": false,

      "quality_score": 1.0,
      "boundary_ok": true
    }

---

## 4. Internal token units

Until the native Obsidia tokenizer / ledger is wired, V0 uses:

    internal_token_units = ceil(character_count / 4)

This is an explicit local proxy.

It must be labeled as:

- internal token/context budget estimate;
- not third-party billing;
- not exact native token count.

Future V1 should replace this with a native Obsidia token ledger.

---

## 5. Brody request cost

For BRODY_CHAT / BRODY_MEMORY / BRODY_FASTPATH, count:

| Metric | Meaning |
|---|---|
| route | semantic route selected |
| input chars | raw message + loaded context |
| semantic query chars | compressed query length |
| internal_token_units_in | estimated input budget |
| internal_token_units_out | estimated response budget |
| modules_considered | possible modules |
| modules_activated | actually activated modules |
| modules_skipped | avoided modules |
| files_read | local files read |
| memory_records_read | Graphiti / Neo4j / local index records |
| cache_hit | cache reused |
| elapsed_ms | total local elapsed time |
| boundary_ok | no false action boundary |

---

## 6. Real domain request cost

For DOMAIN_BANK / DOMAIN_TRADING / DOMAIN_GPS_AVIATION, count:

| Metric | Meaning |
|---|---|
| domain_agents_used | number of domain agents |
| domain_votes | AgentVote count |
| domain_aggregates | aggregate/meta aggregate count |
| contradictions | contradiction count |
| unknowns | unknown field count |
| risk_flags | risk flag count |
| guard_invoked | whether Guard/X108 was called |
| guard_result | HOLD / BLOCK / ALLOW / NOT_INVOKED |
| sigma_invoked | whether Sigma report/alert was triggered |
| decision_envelope_size | canonical decision envelope size |
| elapsed_ms | domain pipeline latency |
| internal_token_units_total | domain context budget |

Domain cost is not only latency.

Domain cost includes uncertainty cost, contradiction cost, and governance cost.

---

## 7. Obsidure request cost

For OBSIDURE_LEAN and OBSIDURE_CODE, count:

| Metric | Meaning |
|---|---|
| generation_attempts | proposal generations |
| apply_attempts | patch/apply attempts |
| lean_runs | Lean verification runs |
| pytest_runs | Python test runs |
| repair_iterations | repair loops |
| files_read | files inspected |
| files_written | files changed |
| diff_lines_added | added lines |
| diff_lines_deleted | deleted lines |
| proof_status | PASS / FAIL / PARTIAL |
| commit_created | true/false |
| elapsed_ms | total request duration |
| internal_token_units_total | prompt + patch + proof budget |

Obsidure cost is proof-loop cost.

The important metric is not only "tokens".

The important metric is:

    cost_to_reach_validated_commit

---

## 8. X108 / Guard / Sigma cost

For X108_GUARD and SIGMA_REPORT, count:

| Metric | Meaning |
|---|---|
| guard_invoked | Guard was evaluated |
| guard_result | HOLD / BLOCK / ALLOW |
| contradictions | contradiction count |
| unknowns | unknown count |
| risk_flags | risk flag count |
| sigma_invoked | Sigma was triggered |
| sigma_reports | report count |
| freeze_triggered | true/false |
| decision_authority | must remain KX108_ONLY |
| emits_act | must remain false unless authorized path exists |
| memory_write | must remain false unless explicit memory-write protocol exists |

---

## 9. Cost deltas

Every optimized path should compare against a baseline.

Required deltas:

    latency_delta_pct
    internal_token_delta_pct
    module_skip_pct
    file_read_delta_pct
    memory_read_delta_pct
    repair_iteration_delta_pct

For Obsidure, the key comparison is:

    baseline_repair_loop_cost vs obsidure_controlled_apply_cost

For domains, the key comparison is:

    ungated_domain_action_cost vs guarded_domain_decision_cost

---

## 10. Reporting outputs

A cost run should produce:

    .local_reports/REQUEST_COST_LEDGER_<timestamp>/cost_events.jsonl
    .local_reports/REQUEST_COST_LEDGER_<timestamp>/summary.json
    .local_reports/REQUEST_COST_LEDGER_<timestamp>/summary.md

Future committed artifacts can include:

    docs/performance/OBSIDIA_REQUEST_COST_LEDGER_PROTOCOL_V0.md
    scripts/performance/obsidia_request_cost_ledger_v0.py

---

## 11. Valid claims

Valid:

> Obsidia measures internal request cost across Brody, domains, Obsidure, X108, Sigma, and runtime paths.

Valid:

> Obsidia can compare optimized and non-optimized request paths using internal token/context budget, latency, module activation, file/memory reads, proof runs, and repair iterations.

Invalid:

- Obsidia measures third-party invoice cost without provider billing data.
- Obsidia proves production cost without production traces.
- Obsidia proves exact native token cost before the native token ledger is wired.
- Obsidia reduces every request cost equally.
- Obsidia replaces hardware acceleration.

---

## 12. Final formula

Request cost is multi-dimensional:

    RequestCost =
      internal token/context budget
      + latency
      + module activation
      + file and memory reads
      + domain uncertainty
      + guard/sigma overhead
      + proof/test/repair loop cost

Fast Path reduces avoidable pre-compute.

Obsidure reduces uncontrolled proof-loop drift.

Domains expose terrain-specific uncertainty cost.

X108 governs action authority.
