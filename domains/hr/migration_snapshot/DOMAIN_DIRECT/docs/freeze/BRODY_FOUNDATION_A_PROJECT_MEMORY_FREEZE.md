# Foundation A — Project Memory Freeze

**Status**: FOUNDATION_A_PARTIAL
**Date**: 2026-05-20
**Result**: BRODY_FOUNDATION_A_PROJECT_MEMORY_FREEZE_PASS

---

## Pourquoi PARTIAL et non READY

`FOUNDATION_A_PARTIAL` — graphiti_v20 trouvé localement, mais `brody_memory_doc_available=false` car Neo4j est offline (`NEO4J_PASSWORD` non défini). Le status passe à `FOUNDATION_A_READY` quand Neo4j est live et que `context_packet_chain.status == CHAIN_PASS`.

---

## Sources disponibles

| Source | Présente |
|--------|---------|
| graphiti_v20 | **true** — `_graphiti_readonly_indexes/…/graphiti_readonly_index_v2.json` |
| brody_memory_doc | **false** — Neo4j offline |
| context_packets | **true** — `CURRENT_BRODY_CONTEXT_PACKET_QUERY*.txt` pointer présent |
| project_ledgers | **true** — `_local_audits/memory_candidate_ledger.jsonl` |
| tree_policy | **false** — auto_triage pointer absent |
| mmonde_or_34trees | **false** — NOT_FOUND_IN_EXISTING_SOURCES |

---

## Missing links

- `brody_memory_doc_not_available_via_neo4j` — Neo4j offline, BrodyMemoryDoc non accessible
- `project_intake_capture_not_found` — pointer `CURRENT_BRODY_PROJECT_INTAKE_CAPTURE*.txt` absent

---

## Invariants boundary

- `memory_write=false`
- `graphiti_write=false`
- `neo4j_write=false`
- `decision_authority=KX108_ONLY`
- `source_mode=EXISTING_PROJECT_MEMORY_ONLY`

---

## Snapshot JSON

Voir `BRODY_FOUNDATION_A_PROJECT_MEMORY_FREEZE.json`

---

**BRODY_FOUNDATION_A_PROJECT_MEMORY_FREEZE_PASS**
