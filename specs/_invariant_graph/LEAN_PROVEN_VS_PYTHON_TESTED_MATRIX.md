# Lean Proven vs Python Tested Matrix — P72

**Statut :** P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT_READY  
**Date :** 2026-06-07

Ce document distingue explicitement les claims couverts par une preuve Lean 4 formelle des claims validés uniquement par des tests Python.

**Règle fondamentale :** Un test Python qui passe n'est PAS une preuve formelle. LEAN_PROVEN requiert `#print axioms` sans axiomes non-standard.

---

## Claims publiquement revendicables (LEAN_PROVEN)

| Claim | Théorème Lean | Fichier | Python test aussi |
|---|---|---|:---:|
| Aucune action irréversible avant τ | `X108_no_act_before_tau` | TemporalKernel.lean | ✓ |
| Noyau X108 ne bloque jamais | `X108_kernel_never_blocks` | TemporalKernel.lean | ✓ |
| Déterminisme du vote (aggregate4) | `aggregate4_unanimous` + `no_two_distinct_supermajorities_4` | Consensus.lean | ✓ |
| Fail-closed par défaut (BLOCK) | `aggregate4_fail_closed` | Consensus.lean | ✓ |
| Skew négatif → HOLD | `skew_negative_implies_hold` | TemporalBridge.lean | ✓ |
| Immutabilité de la trace | `Obsidia.G1` | Basic.lean | ✓ |
| Merkle seal cohérent | `Obsidia.G2` | Basic.lean | ✓ |
| Non-contradiction des règles | `Obsidia.D1` | Basic.lean | — |
| Déterminisme du vote (base) | `Obsidia.E2` | Basic.lean | — |
| Actions réversibles = base (irr=false) | `X108_reversible_equals_base` | TemporalKernel.lean | ✓ |
| Post-τ = base (τ≤elapsed) | `X108_irreversible_after_tau_equals_base` | TemporalKernel.lean | ✓ |
| canonicalize_elapsed préserve ≥0 | `canonicalize_preserves_nonneg` | TemporalBridge.lean | — |
| Pas de contradiction circulaire | `Obsidia.G3` | Basic.lean | — |

---

## Claims validés par tests uniquement (PYTHON_TESTED — non claimables comme preuves formelles)

| Claim | Test principal | Palier |
|---|---|---|
| Graphiti en lecture seule | test_p66_srl_readonly_memory_layer.py | P66 |
| Routes API sécurisées par OBSIDIA_API_KEY | test_p68_api_auth_route_exposure_audit.py | P68 |
| Adapters source en DRY_RUN_ONLY | test_p71_source_runtime_source_packs_deep_audit.py | P71 |
| Sigma = veto post-Guard | test_p56e_post_patch_metric_reaudit.py | P56E |
| Connecteurs actifs = DO_NOT_RUN | test_p70_network_egress_connectors_audit.py | P70 |
| SRL lecture seule (memory_write=False) | test_p66_srl_readonly_memory_layer.py | P66 |
| Bus = PROPOSE_ONLY | test_p61_bus_adapter_batch.py | P61 |
| Source packs non-canonisés par existence | test_p71_source_runtime_source_packs_deep_audit.py | P71 |

---

## Claims TLA+ model-checked (bornés — non équivalents à Lean)

| Claim | Fichier TLA+ | États vérifiés | Note |
|---|---|---|---|
| X-108 core invariants (états finis) | X108.tla | 1.2M states, 0 violations | Bornage fini, pas universel |
| Distributed X-108 | DistributedX108.tla | vérifiés | Bornage fini |

**Note :** TLA+ model-checking vérifie un espace d'états borné. Il ne remplace pas une preuve Lean universelle.

---

## Tableau de correspondance statut → communication autorisée

| Statut | Communication autorisée | Sur-claims interdits |
|---|---|---|
| LEAN_PROVEN | « Prouvé formellement en Lean 4 » | « Prouvé universellement » sans précision Lean |
| PYTHON_TESTED | « Validé par tests » ou « testé » | « Prouvé », « garanti formellement » |
| TLA+ CHECKED | « Vérifié par model-checking (espace borné) » | « Prouvé » sans préciser le bornage |
| SPEC_ONLY | « Contrainte architecturale documentée » | « Prouvé », « garanti » |
| MIXED_PROOF_STATUS | Préciser la partie Lean et la partie Python séparément | Unifier sous « prouvé » |

---

## Résumé des counts

| Catégorie | Nb claims |
|---|---:|
| LEAN_PROVEN (public claimable) | 7 |
| LEAN_PROVEN (technique interne) | 6 |
| PYTHON_TESTED uniquement | 8 |
| TLA+ checked | 2 |
| SPEC_ONLY | 2 |
| DOC_ONLY | 1 |
| MIXED | 1 |
