# Invariant to Layer Map — P72

**Statut :** P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT_READY  
**Date :** 2026-06-07

Ce document mappe chaque invariant à sa couche architecturale et aux composants concrets qu'il protège.

---

## OS0_KERNEL — Noyau de décision déterministe

**Composants :** `decideX108`, `decision`, `beforeTau`, `decide3X108`, `aggregate4`, `countDec`  
**Fichiers Lean :** TemporalKernel.lean, TemporalBridge.lean, Consensus.lean, Basic.lean

| Invariant | Composant principal | Statut |
|---|---|---|
| DETERMINISM | `decision` / `aggregate4` / `countDec` | LEAN_PROVEN |
| NO_ACT_BEFORE_TAU | `decideX108` / `beforeTau` | LEAN_PROVEN |
| HOLD_BEFORE_TAU | `decideX108` / `decide3X108` | LEAN_PROVEN |
| IRREVERSIBLE_ACTION_DELAY | `decideX108` (branche τ≤elapsed) | LEAN_PROVEN |
| REVERSIBLE_ACTION_BASELINE | `decideX108` (branche irr=false) | LEAN_PROVEN |
| NEGATIVE_CLOCK_SKEW_TO_HOLD | `decide_with_skew_handling` / `canonicalize_elapsed` | LEAN_PROVEN |
| THRESHOLD_CONSERVATION | `aggregate4` / `countDec` | LEAN_PROVEN |
| BLOCK_PRIORITY_OVER_HOLD_ALLOW | `aggregate4` (else BLOCK) | LEAN_PROVEN |
| HOLD_PRIORITY_OVER_ALLOW | `decideX108` + `aggregate4` | LEAN_PROVEN |
| KX108_ONLY_DECISION_AUTHORITY | Contrainte architecturale globale | SPEC_ONLY |

---

## OS1_GUARD — Autorité finale Guard X-108

**Composants :** `decide3X108`, `liftDecision`  
**Fichiers Lean :** TemporalKernel.lean

| Invariant | Composant principal | Statut |
|---|---|---|
| GUARD_X108_FINAL_AUTHORITY | `decide3X108` (never BLOCK) | LEAN_PROVEN |

---

## OS2_SIGMA — Veto post-Guard

**Composants :** `sigma/` (gel permanent P56D)  
**Fichiers Lean :** aucun (SPEC_ONLY)

| Invariant | Composant principal | Statut |
|---|---|---|
| SIGMA_POST_GUARD_VETO_ONLY | sigma/ architecture P56D | SPEC_ONLY |

---

## OS3_AUDIT_PROOF — Trace et scellés

**Composants :** trace log, Merkle seal, archives  
**Fichiers Lean :** Basic.lean (G1, G2)

| Invariant | Composant principal | Statut |
|---|---|---|
| NO_KERNEL_MUTATION_FROM_PERIPHERY | trace / G1 immutabilité | LEAN_PROVEN |
| ARCHIVE_NOT_RUNTIME | Merkle seal / _freezes / G2 | MIXED_PROOF_STATUS |
| PYTHON_TESTED_NOT_LEAN_PROVEN | meta-documentation | DOC_ONLY |

---

## OS4_PERIPHERY — Périphérie non-décisionnelle

**Composants :** SRL, graphiti, agents, bus, connectors  
**Fichiers :** runtime_wiring/, connectors/, periphery/

| Invariant | Composant principal | Audit palier |
|---|---|---|
| NO_PERIPHERY_DECISION_AUTHORITY | tous composants périphériques | P66–P71 |
| NO_GRAPHITI_WRITE | `graphiti_v20_readonly_client.py` | P70 |
| NO_MEMORY_WRITE_WITHOUT_GATE | SRL / memory adapter | P66 |
| BUS_PROPOSE_ONLY | bus adapter | P61 |

---

## OS5_SOURCES — Sources et adapters

**Composants :** _source_packs/, runtime_wiring/source_runtime/, source_file_registry.json  
**Fichiers :** scripts/audit_source_runtime_source_packs_p71.py

| Invariant | Composant principal | Audit palier |
|---|---|---|
| DRY_RUN_ONLY_ADAPTERS | tous adapters source (14 classifiés P71) | P71 |
| SOURCE_PACK_NOT_CANON_BY_EXISTENCE | source_pack_resolver + registre | P71 |

---

## OS6_ROUTES — Auth API

**Composants :** apps/obsidia_api/routes/, `require_api_key`  
**Fichiers :** apps/obsidia_api/routes/source_runtime_status.py

| Invariant | Composant principal | Audit palier |
|---|---|---|
| ROUTE_AUTH_BOUNDARY | `Depends(require_api_key)` / OBSIDIA_API_KEY | P68/P69 |

---

## OS7_NETWORK — Egress réseau

**Composants :** connectors/ (aviation, bank, trading, graphiti)

| Invariant | Composant principal | Audit palier |
|---|---|---|
| NETWORK_EGRESS_REVIEW_REQUIRED | `requests.post()` / `while True` / `ccxt.binance()` | P70 |
