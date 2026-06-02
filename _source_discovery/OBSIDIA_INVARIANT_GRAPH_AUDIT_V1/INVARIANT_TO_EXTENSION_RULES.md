# INVARIANT_TO_EXTENSION_RULES
# OBSIDIA_INVARIANT_GRAPH_AUDIT_V1
# Date: 2026-06-02

Pourquoi l'ajout de couches ne casse pas X-108 : règles par extension.

---

## Règle générale

Toute extension doit satisfaire :
```
1. Classifiée avant runtime (SOURCE_DISCOVERY → SPEC → TEST → RUNTIME)
2. Packet / boundary / test définis
3. Retombe vers X-108 si action critique
4. Si incertain → HOLD / BLOCK selon couche
```

La clé mathématique : `Refinement.x108_never_blocks` garantit que TOUT raffinement du kernel hérite de la propriété no-BLOCK.

---

## Table des extensions

| Extension | Rôle autorisé | Rôle interdit | Invariant requis | Boundary requise | Test futur |
|-----------|--------------|---------------|-----------------|-----------------|------------|
| **Brody** | Répondre, contextualiser, produire signal mémoire candidat | Décider, émettre ACT, écrire mémoire sans gate | `X108_kernel_never_blocks`, no-ACT tests | `readonly=True`, `memory_write=False` | `test_brody_no_decision_authority` |
| **Graphiti** | Fournir contexte readonly, alimenter context packets | Écrire en base sans gate humain, modifier état | `P17_AuditGrowth` (audit only), graphiti_write=False | `graphiti_write=False` par défaut | `test_graphiti_write_requires_gate` |
| **Sigma** | Router les signaux, enrichir le context packet | Émettre verdict ALLOW/HOLD/BLOCK, décider | `Refinement.x108_never_blocks`, KX108_ONLY | `KX108_ONLY; SIGNAL_ONLY` | `test_sigma_no_act` (650+ existants) |
| **Tree34** | Activer des signaux cognitifs [0,1] par arbre | Émettre ACT, émettre verdict final | non_decision_contract (Tree34 ↛ ACT) | `CONTEXT_ONLY; NO_ACT` | `test_no_act_from_tree34` (à créer) |
| **Agents 52** | Produire context packets, signaux, artefacts auditables | Émettre ALLOW/HOLD/BLOCK, décider, ACT | `X108_kernel_never_blocks` (par analogie) | `AgentPeripheral ↛ ACT` | `test_agent_output_is_context_packet` |
| **Balance/BUV** | Calculer score de balance multi-facteur [0,1] | Décider de l'action, émettre verdict final | [Python spec — FORMAL_PROOF_PENDING] | `BALANCE ↛ ALLOW/HOLD/BLOCK` | `test_balance_no_verdict` |
| **Gencoin** | Calculer valeur candidate post-preuve | Minter token réel, déployer on-chain, ACT sans X108 | `X108_kernel_never_blocks` (gencoin_candidate requis X108_ALLOW) | `mint_allowed=False si ¬X108_ALLOW` | `test_gencoin_not_a_token` |
| **GPS** | Calculer scores de confiance GPS (drift, conflict, time_skew, brownout) | Décider de la trajectoire, ACT physique sans DecisionTicket | `skew_negative_implies_hold`, `X108_no_act_before_tau` | `GPS ↛ ACT; proposed_verdict only` | `test_no_actuator_without_decisionticket` |
| **NPL** | Produire signaux contextuels narratifs (cultural_matrix, archive_gap, truth_regime) | Diagnostiquer, décider, émettre verdict culturel | [SPEC_CANDIDATE — récepteurs basés sur L5, L23] | `PERIPHERAL_READONLY; NO_ACT; NO_VERDICT_FINAL` | `test_npl_no_decision_authority` |
| **OS4** | Interface publique, routing des requêtes | Décider sans X108, modifier l'état kernel | `Refinement.x108_never_blocks`, `P17_AuditGrowth` | `KX108_ONLY; SPEC_BEFORE_RUNTIME` | `test_os4_no_kernel_bypass` |
| **External Signals** | Préfiltre temporel (anti-replay, stale, skew) | Réautoriser X108, émettre ALLOW, forcer ACT | `skew_negative_implies_hold`, `X108_no_act_before_tau`, C473 non-réautorisation | `SIGNAL_ONLY; NO_ACT; TEMPORAL_PREFILTER_ONLY` | `test_external_signal_cannot_authorize_act` |

---

## Mécanisme de stabilisation

Chaque extension est stabilisée par l'une de ces quatre propriétés Lean :

### 1. No-ACT (via `X108_no_act_before_tau`)
Toute couche ajoutée qui tente d'émettre ACT avant τ sera interceptée par le kernel Lean-prouvé.
```
Extension → tente ACT irréversible avant τ
→ X108_no_act_before_tau : irr=true ∧ elapsed<τ → HOLD
→ ACT BLOQUÉ
```

### 2. No-BLOCK (via `Refinement.x108_never_blocks`)
Toute couche qui raffine X108 hérite de la garantie no-BLOCK.
```
Extension raffine kernel
→ Refinement.x108_never_blocks : ¬(decide3X108 = BLOCK)
→ Refinement.refined_not_block : R_decision d d3 → ¬(d3 = BLOCK)
→ BLOCK IMPOSSIBLE dans la couche raffinée
```

### 3. Fail-closed (via `aggregate4_fail_closed`)
Toute couche distribuée sans quorum retourne BLOCK.
```
Extension distribuée perd quorum
→ aggregate4_fail_closed : ¬supermajACT ∧ ¬supermajHOLD ∧ ¬supermajBLOCK → BLOCK
→ FAIL_CLOSED = BLOCK
```

### 4. Immutabilité (via `P15_Immutability_Strong`)
Toute couche qui tente de modifier la trace sans détection échoue.
```
Extension modifie repo sans mise à jour du seal
→ P15_Immutability_Strong : repo ≠ repo' → globalSeal ≠ globalSeal'
→ MODIFICATION DÉTECTÉE
```
