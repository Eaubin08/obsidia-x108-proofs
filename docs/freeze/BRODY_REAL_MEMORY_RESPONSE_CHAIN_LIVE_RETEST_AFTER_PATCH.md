# Brody Real Memory→Response Chain — Live Retest After Patch

**Date**: 2026-05-20
**Status**: BRODY_REAL_MEMORY_RESPONSE_CHAIN_LIVE_READY_FOR_OPERATOR_RETEST

---

## Objective

Replace the hard `ERROR/NEO4J_UNAVAILABLE` chain response with a real local Graphiti index
fallback + query-ladder. Brody now answers from indexed memory even when Neo4j is offline.

---

## Patches Applied

| File | Change |
|------|--------|
| `brody_semantic_query_router.py` | Added `primary_query` (short term) + `fallback_queries` ladder per topic |
| `brody_memory_response_chain_adapter.py` | Local Graphiti index fallback when Neo4j offline; query ladder |
| `brody_session_memory_adapter.py` | Strict followup patterns — removed `encore`, `suite`, `suivant`, `next` |
| `brody_session_memory_runtime.py` | Strict `_FOLLOWUP_KEYWORDS` aligned with spec |
| `brody_true_voice_adapter.py` | Synthesize answer from `selected_items` on `LOCAL_INDEX_FALLBACK_PARTIAL` |
| `RightPanel.tsx` | Added "Memory Response Chain" + "Semantic Query Router" panels |

---

## Live Chain Results

| Query | Status | Source Mode | Effective Query | Items |
|-------|--------|-------------|-----------------|-------|
| X108 kernel | LOCAL_INDEX_FALLBACK_PARTIAL | LOCAL_GRAPHITI_INDEX_FALLBACK | x108 | 8 |
| mémoire graphiti candidat | LOCAL_INDEX_FALLBACK_PARTIAL | LOCAL_GRAPHITI_INDEX_FALLBACK | memory | 8 |
| 34 arbres bloqués | LOCAL_INDEX_FALLBACK_PARTIAL | LOCAL_GRAPHITI_INDEX_FALLBACK | 34_arbres | 8 |
| gencoin jeton | LOCAL_INDEX_FALLBACK_PARTIAL | LOCAL_GRAPHITI_INDEX_FALLBACK | gencoin | 3 |

Local index: **3267 records** loaded from `_graphiti_readonly_indexes/GRAPHITI_READONLY_INDEX_V2_FUSION_20260512_224854/`.

---

## Followup Strict Fix

| Message | Old result | New result |
|---------|------------|------------|
| "encore trop protocolaires" | `followup=True` (bug) | `followup=False` |
| "reprends ce point" | `followup=True` | `followup=True` |
| "continue le travail" | `followup=True` (bug) | `followup=False` |
| "continue sur ça" | `followup=True` | `followup=True` |

---

## Test Results

```
New tests:    37/37  PASS
Full suite:  1261/1261 PASS
Sigma files:  0 diff (protected files untouched)
```

---

## Honest Classification

```
GRAPHITI_LIVE_FULL_READY      = false
NEO4J_MEMORY_READY            = false
LOCAL_GRAPHITI_INDEX_READY    = true  ← 3267 records, query ladder working
QUERY_LADDER_READY            = true  ← primary_query → fallback_queries
FOLLOWUP_STRICT_READY         = true  ← spec-compliant pattern list
```

---

## Boundary

```
readonly              = true
memory_write          = false
graphiti_write        = false
neo4j_write           = false
emits_act             = false
kernel_mutation       = false
decision_authority    = KX108_ONLY
graphiti_live         = false
neo4j_live            = false
```

---

## Not Modified

- `sigma/guard.py`, `sigma/contracts.py`, `sigma/protocols.py`, `sigma/aggregation.py`
- `proofs/lean/`, `formal/tla/`, `merkle_seal.json`
- Kernel X108
- BFCL V1 frozen adapter

---

**BRODY_REAL_MEMORY_RESPONSE_CHAIN_LIVE_READY_FOR_OPERATOR_RETEST**
