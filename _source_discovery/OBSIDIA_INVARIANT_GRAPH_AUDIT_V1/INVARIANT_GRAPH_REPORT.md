# OBSIDIA_INVARIANT_GRAPH_AUDIT_V1

**Date :** 2026-06-02
**Sources principales :** `proofs/lean/`, `formal/tla/`, `proofs/V18_7/`, `external_pack/PROOF_INDEX.md`

---

## 1. Mode

```
INVARIANT_GRAPH_AUDIT_ONLY
```

Aucun code patché. Aucune spec créée. Aucun commit.

---

## 2. Résumé exécutif

### Ce qui tient mathématiquement le système Obsidia

Le système Obsidia X-108 repose sur un graphe de **28 théorèmes Lean 4 prouvés formellement** qui forment le kernel de sécurité. Ces théorèmes ne sont pas des conventions — ils sont vérifiés par machine (`lake build`).

**Le cœur du système** est la composition de cinq propriétés :

1. **Déterminisme** (`D1_determinism`) — La décision est une fonction pure.
2. **Gate temporelle** (`X108_no_act_before_tau`) — Aucun ACT irréversible avant τ.
3. **Raffinement conservateur** (`Refinement.x108_never_blocks`) — Toute couche raffinant le kernel hérite de no-BLOCK.
4. **Immutabilité** (`P15_Immutability_Strong`) — Tout changement de corpus est détecté.
5. **Fail-closed** (`aggregate4_fail_closed`) — Sans quorum, BLOCK automatique.

Ces cinq propriétés sont **mutuellement renforcées** : le déterminisme rend la gate temporelle reproductible, la gate temporelle protège le raffinement, le raffinement garantit la composition des couches, l'immutabilité empêche la falsification, et le fail-closed empêche toute décision sous incertitude.

---

## 3. Graphe central des invariants

```
DÉTERMINISME (D1_determinism)
    │ [LEAN_PROVEN]
    ↓
SEUIL / NON-ACT (E2_no_act_below_threshold)
    │ [LEAN_PROVEN]
    ↓
TEMPORALITÉ X-108 (X108_no_act_before_tau)
    │    [LEAN_PROVEN + TLA SafetyX108]
    ├──→ X108_kernel_never_blocks
    ├──→ X108_after_tau_equals_base
    ├──→ skew_negative_implies_hold [External Signals]
    ↓
REFINEMENT (Refinement.x108_never_blocks)
    │    [LEAN_PROVEN — clé d'extension]
    ├──→ refined_not_block
    ├──→ P17_KernelNeverBlocks
    ↓
IMMUTABILITÉ / MERKLE / SEAL
    │    [LEAN_PROVEN sous hypothèse crypto]
    ├──→ P15_Immutability_Strong [Merkle]
    ├──→ P13_Immutability [Seal]
    ├──→ P17_AuditGrowth [Audit log]
    ↓
CONSENSUS / FAIL-CLOSED
    │    [LEAN_PROVEN + TLA DistributedX108]
    ├──→ aggregate4_fail_closed
    ├──→ no_two_distinct_supermajorities_4
    ↓
CANONICALISATION
    │    [LEAN_PROVEN]
    ├──→ canonicalize_preserves_nonneg
    ↓
SKEW NÉGATIF → HOLD
    │    [LEAN_PROVEN]
    ├──→ skew_negative_implies_hold
    ↓
OS3 / TICKET / REPLAY
    │    [PYTHON_SPEC + sha256 — FORMAL_PROOF_PENDING replay]
    ├──→ OS3ProofTicket (merkle_root, trace_hash)
    ↓
NON-SOUVERAINETÉ PÉRIPHÉRIQUE
    │    [PYTHON_TEST_ONLY — 1973 PASS]
    ├──→ No ACT Sigma / Brody / Tree34 / Agents / Balance / Gencoin / GPS
    ├──→ NPL PERIPHERAL_READONLY [SPEC_CANDIDATE]
    ├──→ External Signals SIGNAL_ONLY [F04 importé]
    ↓
EXTENSION CONTRÔLÉE DES COUCHES
    │    [DOC_ONLY + SPEC_ONLY pour nouvelles extensions]
    └──→ Règle : toute extension → spec → test → runtime → X108 gate
```

---

## 4. Pourquoi l'architecture est difficile à copier

### Ce qui est copiable

- La structure de dossiers (`periphery/`, `sigma/`, `proofs/lean/`)
- Les noms de composants (`Brody`, `Sigma`, `Tree34`, `X108`)
- Les conventions de naming (`KX108_ONLY`, `SIGNAL_ONLY`)
- Les fichiers de spec Plan 2 (163 fichiers Markdown)

### Ce qui est difficile à copier

**1. La composition cohérente des invariants**

Copier `TemporalKernel.lean` sans comprendre pourquoi `Refinement.x108_never_blocks` en dépend ne reproduit pas la garantie d'extensibilité. Les théorèmes sont liés — un système qui n'a que D1 mais pas le raffinement n'a pas de garantie d'extension.

**2. La raison mathématique pour laquelle chaque couche retombe vers X-108**

Cette raison est `Refinement.x108_never_blocks` :
```lean
theorem refined_not_block (d : Decision) (d3 : Decision3)
    (h : R_decision d d3) :
    Not (d3 = Decision3.BLOCK)
```
Une couche qui raffine X108 hérite de no-BLOCK. Une couche qui ne raffine pas X108 ne peut pas décider. Il n'existe pas de position intermédiaire souveraine.

**3. La composition temporelle + skew + fail-closed**

Avoir `X108_no_act_before_tau` sans `skew_negative_implies_hold` laisse une faille : un composant externe avec skew négatif pourrait présenter `elapsed < 0` comme `elapsed < τ` n'étant pas satisfait. Le théorème `skew_negative_implies_hold` ferme cette faille — il est prouvé séparément et composé dans `TemporalBridge`.

**4. L'immutabilité sous hypothèse cryptographique explicite**

`SealAssumptions.combine_inj` est axiomatisé — pas prouvé de première hypothèse. Copier le code sans axiomatiser correctement la fonction de hachage produit un système qui ne détecte pas les collisions. Le fait que cet axiome soit explicite est lui-même une garantie d'honnêteté intellectuelle difficile à reproduire dans une copie rapide.

**5. La discipline de composition**

La composition `SOURCE_DISCOVERY → SPEC → TEST → RUNTIME → X108_GATE → CLAIM` est une discipline de processus que le code seul ne capture pas. C'est elle qui empêche les couches périphériques de devenir souveraines par glissement progressif.

---

## 5. Statut global

| Zone | Statut | Source | Risque |
|------|--------|--------|--------|
| OS0 kernel (décision de base) | LEAN_PROVEN | `Basic.lean` | Aucun |
| OS1 temporal kernel | LEAN_PROVEN | `TemporalKernel.lean` | Aucun |
| OS1 temporal bridge (skew) | LEAN_PROVEN | `TemporalBridge.lean` | Aucun |
| OS2 refinement | LEAN_PROVEN | `Refinement.lean` | Aucun |
| OS2 system model | LEAN_PROVEN | `SystemModel.lean` | Aucun |
| OS3 Merkle/Seal | LEAN_PROVEN (sous hypothèse crypto) | `Sensitivity.lean`, `Seal.lean` | combine_inj est axiome |
| OS3 Consensus | LEAN_PROVEN + TLA_SPEC | `Consensus.lean`, `formal/tla/DistributedX108.tla` | TLC non relancé |
| OS3 OS3ProofTicket | PYTHON_SPEC | `periphery/os3_ticket.py` | FORMAL_PROOF_PENDING |
| OS3 replay | ABSENT (replay_status=NOT_RUN) | `periphery/os3_ticket.py` | GAP — à implémenter |
| Sigma non-souveraineté | PYTHON_TEST_ONLY | `tests/sigma/` | LEAN_PROOF_ABSENT |
| Brody readonly | PYTHON_TEST_ONLY | `tests/api/` | LEAN_PROOF_ABSENT |
| Graphiti isolation | PYTHON_TEST_ONLY | `tests/sigma/test_f70_*.py` | LEAN_PROOF_ABSENT |
| Tree34 non-décision | DOC_ONLY | `non_decision_contract.md` | Test exécutable absent |
| Lyapunov / PoG | PYTHON_SPEC | `periphery/math_core/` | FORMAL_PROOF_PENDING |
| External Signals | SPEC_CANDIDATE (F04 importé) | `specs/external_signals/` | Adapter non créé |
| NPL | SPEC_CANDIDATE | `specs/12_NARRATIVE_PROVENANCE_LAYER/` | Runtime absent |
| TLA specs | TLA_SPEC_PRESENT — TLC_UNKNOWN | `formal/tla/` | TLC non relancé |

---

## 6. Gaps formels

### Gaps critiques

| Gap | Impact | Action recommandée |
|-----|--------|-------------------|
| Lyapunov Python spec → Lean | Claim-scope risk sur stabilité | Formaliser en Lean Plan 3+ |
| ProofOfGovernance Python → Lean | Idem | Formaliser en Lean Plan 3+ |
| Sigma non-souveraineté → Lean | Claim limité aux tests | Tests suffisants pour l'instant |
| replay_status = NOT_RUN | Replay non fonctionnel | Implémenter Plan 3 P4 |
| TLC non relancé | TLA non vérifié actuellement | Relancer TLC avant claim public |
| Tree34 test exécutable absent | Non-décision doc uniquement | Créer `test_no_act_from_tree34` |

### Gaps non bloquants

- `TemporalX108.lean` non lu directement — couvert par AuditX108Roots
- `proofs/tla/` non lus complètement — doublon de `formal/tla/`
- RFC3161 non relancé — preuve d'horodatage non vérifiée actuellement

---

## 7. Verdict

```
INVARIANT_GRAPH_READY
```

**Justification :**

- 28 théorèmes Lean 4 inventoriés et sourcés
- Graphe de dépendances complet (CONFIRMED pour kernel, INFERRED pour périphéries)
- 4 specs TLA+ présentes (TLC_UNKNOWN — ne pas clamer "vérifié")
- Gaps formels identifiés et documentés
- Claim-scope warnings établis
- La question centrale ("pourquoi difficile à copier") a une réponse sourcée : `Refinement.x108_never_blocks` + composition temporelle + fail-closed

**Qualification :** Le graphe est READY pour le kernel X108. Il est PARTIAL pour les couches périphériques (Python-test-only, pas de Lean proof).
