# OBSIDIA SOURCE ORGANIZED SPEC FREEZE V1

**Freeze name:** OBSIDIA_SOURCE_ORGANIZED_SPEC_FREEZE_V1
**Date:** 2026-06-02
**Mode:** SPEC_ONLY
**Runtime patch:** false
**Authority:** KX108_ONLY
**Sources:** Plan 1 (_source_discovery/OBSIDIA_SOURCE_DISCOVERY_MAP_V1/) + Plan 1 NPL Extension (_source_discovery/OBSIDIA_SOURCE_DISCOVERY_MAP_V1_NPL_EXTENSION/)
**Purpose:** Rendre Obsidia lisible, traçable, sourcé, contractuel — avant tout runtime futur.

---

## Règle fondamentale

```
Source réelle → Import readonly → Spec contractuelle → Test futur → Runtime futur → Claim public
KX108_ONLY pour toute décision
```

---

## Structure

| Dossier | Contenu |
|---------|---------|
| `_source_index/` | Index de toutes les sources + mappings |
| `_imports_readonly/` | Imports readonly des sources existantes (pas de copie de code) |
| `00_SCOPE_DISCIPLINE/` | Limites de claim-scope public |
| `01_X108_AUTHORITY/` | Autorité décisionnelle KX108 |
| `02_INTERLAYER_CONSTITUTION/` | Constitution intercouche |
| `03_ENTROPY_DISCIPLINE/` | Entropie / état gouverné / Lyapunov |
| `04_AGI_TREE34_FLUX/` | 34 arbres / flux / AGI boundary |
| `05_BALANCE_BUV_GEOMETRIES/` | Balance / BUV / géométries |
| `06_HIGH_PERIPHERY_SYSTEMS/` | Shazam / BDF / HexaFlux / Reverse OS / MCP Bridge |
| `07_AGENTS_CONNECTORS_MCP/` | Agents 52 / connectors / MCP |
| `08_MEMORY_BRODY_GRAPHITI/` | Brody / Graphiti / mémoire |
| `09_CRITICAL_WORLDS/` | GPS / aviation / bank / trading |
| `10_VALUE_GENCOIN_JCOIN/` | Gencoin / Jcoin / valeur |
| `11_PROOF_REPLAY_OS3/` | OS3 ticket / replay / preuve formelle |
| `12_NARRATIVE_PROVENANCE_LAYER/` | NPL — couche narrative readonly |
| `_invariant_graph/` | Graphe d'invariants — Lean-proven vs Future Targets |

---

## Navigation rapide → OBSIDIA_READING_GUIDE.md

---

## DELTA_2026_06_02 — NPL / Audio / Entropy / P107 / P161

**Source :** `specs/PLAN2_DELTA_NPL_AUDIO_ENTROPY_REPORT.md`
**Audits :** P107_P161_AUDIT_READY_FOR_PLAN3 · NPL_AUDIO_ENTROPY_AUDIT_READY_FOR_PLAN3 · INVARIANT_GRAPH_READY

### Nouveaux fichiers créés

| Fichier | Dossier | Statut |
|---------|---------|--------|
| `P107_LYAPUNOV_FORMALIZATION_TARGET.md` | `03_ENTROPY_DISCIPLINE/` | FUTURE_FORMAL_TARGET / DOC_ONLY |
| `P161_ENERGETIC_CALIBRATION_FORMALIZATION_TARGET.md` | `03_ENTROPY_DISCIPLINE/` | FUTURE_FORMAL_TARGET / DOC_ONLY |
| `AUDIO_ENTROPY_SOURCE_CONSTRAINTS.md` | `03_ENTROPY_DISCIPLINE/` | SOURCE_PARTIAL / SPEC_CANDIDATE / CLAIM_SCOPE_LOCKED |
| `NPL_TO_PLAN3_CONSTRAINTS.md` | `12_NARRATIVE_PROVENANCE_LAYER/` | SPEC_FUTURE / ADVISORY_ONLY |
| `NPL_CLAIM_SCOPE_LOCKS.md` | `12_NARRATIVE_PROVENANCE_LAYER/` | SPEC_FUTURE / CLAIM_SCOPE_LOCKED |
| `NPL_METRICS_ADVISORY_ONLY.md` | `12_NARRATIVE_PROVENANCE_LAYER/` | SPEC_FUTURE / 37 métriques ADVISORY |
| `FUTURE_FORMAL_TARGETS.md` | `_invariant_graph/` | DOC_ONLY — registre P107/P161/NPL/Thermo |
| `LEAN_PROVEN_VS_FUTURE_TARGETS_DELTA.md` | `_invariant_graph/` | DOC_ONLY — 28 Lean-proven vs FUTURE_TARGETS |

### Fichiers mis à jour (section DELTA ajoutée)

| Fichier | Dossier | Modification |
|---------|---------|-------------|
| `THERMODYNAMIC_DEBT_BOUNDARY.md` | `03_ENTROPY_DISCIPLINE/` | DELTA_2026_06_02 — lien P161, claim-scope renforcé |
| `COGNITIVE_THERMODYNAMICS_METRICS.md` | `03_ENTROPY_DISCIPLINE/` | DELTA_2026_06_02 — métriques candidates, lien P107/P161 |

### Claim-scope locks validés

- P107 = FUTURE_FORMAL_TARGET / DOC_ONLY → ❌ "Lean-prouvé" / ✅ "signal advisory"
- P161 = FUTURE_FORMAL_TARGET / DOC_ONLY → ❌ "loi formelle" / ✅ "signal advisory"
- NPL  = SPEC_FUTURE / ADVISORY_ONLY → ❌ "décide" ❌ "diagnostique" / ✅ "hypothèse de provenance"
- Audio/Entropy = SOURCE_PARTIAL → ❌ "thermodynamique prouvée" / ✅ "métaphore architecturale"
