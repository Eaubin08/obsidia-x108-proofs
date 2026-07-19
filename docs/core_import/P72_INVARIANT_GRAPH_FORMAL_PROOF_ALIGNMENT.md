# P72 — Invariant Graph & Formal Proof Alignment

**Audit ID :** P72  
**Statut :** `P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT_READY`  
**Mode :** `AUDIT + DOCS` — aucun patch runtime, aucune modification Sigma, aucune modification Lean existant  
**Branche :** `p72-invariant-graph-formal-proof-alignment`  
**Date :** 2026-06-07

---

## 1. Verdict court

| Statut formel | Nb invariants | Théorèmes Lean |
|---|---:|---:|
| `LEAN_PROVEN` | 11 | 16 mappés |
| `PYTHON_TESTED` | 8 | — |
| `SPEC_ONLY` | 2 | — |
| `DOC_ONLY` | 1 | — |
| `MIXED_PROOF_STATUS` | 1 | 1 (G2) |
| **Total** | **23** | |

**Invariants CRITIQUES :** DETERMINISM, NO_ACT_BEFORE_TAU, HOLD_BEFORE_TAU, IRREVERSIBLE_ACTION_DELAY, THRESHOLD_CONSERVATION, BLOCK_PRIORITY_OVER_HOLD_ALLOW, HOLD_PRIORITY_OVER_ALLOW, GUARD_X108_FINAL_AUTHORITY, NO_PERIPHERY_DECISION_AUTHORITY, NO_KERNEL_MUTATION_FROM_PERIPHERY, KX108_ONLY_DECISION_AUTHORITY

**Claim public autorisé :**  
> « Le périmètre public de preuves / vérification / exécution P1 d'Obsidia X-108 est fermé, reproductible et publiquement gelé. »

---

## 2. Couches architecturales

| Couche | Description | Nb invariants |
|---|---|---:|
| `OS0_KERNEL` | Noyau de décision déterministe X-108 | 9 |
| `OS1_GUARD` | Guard X-108 — autorité finale | 1 |
| `OS2_SIGMA` | Sigma — veto post-Guard (gel P56D) | 1 |
| `OS3_AUDIT_PROOF` | Audit/preuve/trace (Merkle, immutabilité) | 3 |
| `OS4_PERIPHERY` | Périphérie non-décisionnelle | 5 |
| `OS5_SOURCES` | Source packs et adapters | 2 |
| `OS6_ROUTES` | Routes API et frontière auth | 1 |
| `OS7_NETWORK` | Egress réseau | 1 |

---

## 3. Graphe des invariants — 23 entrées

### OS0_KERNEL — Noyau déterministe

#### DETERMINISM — `LEAN_PROVEN`
Le noyau de décision est déterministe : même entrée → même sortie, toujours.  
**Théorèmes :** `Obsidia.E2`, `aggregate4_unanimous`, `no_two_distinct_supermajorities_4`  
**Dépend de :** —  
**Bloque extension de :** OS1_GUARD, OS2_SIGMA, OS4_PERIPHERY  
**Règle :** Toute extension qui introduit un état non-déterministe dans le chemin de décision est INTERDITE.

#### NO_ACT_BEFORE_TAU — `LEAN_PROVEN`
Si irr=true et elapsed<τ, la décision est toujours HOLD. Aucune action irréversible avant τ.  
**Théorèmes :** `X108_no_act_before_tau`, `canonicalize_preserves_nonneg`  
**Dépend de :** DETERMINISM  
**Règle :** Aucune extension ne peut court-circuiter le test `beforeTau` pour des décisions irréversibles.

#### HOLD_BEFORE_TAU — `LEAN_PROVEN`
Conséquence directe de NO_ACT_BEFORE_TAU : l'état actif avant τ est HOLD (jamais BLOCK, jamais ACT).  
**Théorèmes :** `X108_no_act_before_tau`, `X108_kernel_never_blocks`  
**Dépend de :** NO_ACT_BEFORE_TAU, DETERMINISM

#### IRREVERSIBLE_ACTION_DELAY — `LEAN_PROVEN`
Pour irr=true et τ≤elapsed, le noyau retombe sur `decision metrics theta`.  
**Théorèmes :** `X108_irreversible_after_tau_equals_base`, `X108_after_tau_equals_base`

#### REVERSIBLE_ACTION_BASELINE — `LEAN_PROVEN`
Pour irr=false, decideX108 = decision de base. Pas de délai τ appliqué.  
**Théorème :** `X108_reversible_equals_base`

#### NEGATIVE_CLOCK_SKEW_TO_HOLD — `LEAN_PROVEN`
Si elapsed_raw<0 et irr=true et τ≥0 → HOLD. Protection skew horloge.  
**Théorème :** `skew_negative_implies_hold`

#### THRESHOLD_CONSERVATION — `LEAN_PROVEN`
Deux supermajorités distinctes (≥3/4) sont impossibles simultanément sur 4 votants.  
**Théorèmes :** `no_two_distinct_supermajorities_4`, `aggregate4_fail_closed` + aux  
**Règle :** Conserver exactement `aggregate4` (4 votants, seuil 3/4). Modifier le quorum invalide les preuves.

#### BLOCK_PRIORITY_OVER_HOLD_ALLOW — `LEAN_PROVEN`
Sans supermajorité, `aggregate4` retourne BLOCK (fail-fermé).  
**Théorème :** `aggregate4_fail_closed`  
**Règle :** Le default fail-closed est prouvé. Ne pas ajouter `else ACT` ou `else HOLD`.

#### HOLD_PRIORITY_OVER_ALLOW — `LEAN_PROVEN`
HOLD a priorité sur ACT quand la condition τ est active.  
**Théorèmes :** `X108_no_act_before_tau`, `aggregate4_act`

#### KX108_ONLY_DECISION_AUTHORITY — `SPEC_ONLY`
Seul le noyau X-108 peut prendre des décisions ACT/HOLD/BLOCK finales.  
**Théorèmes liés :** `X108_kernel_never_blocks`, `X108_no_act_before_tau`  
**Note :** Contrainte architecturale — partiellement couverte par Lean, globalement SPEC.

---

### OS1_GUARD — Autorité finale

#### GUARD_X108_FINAL_AUTHORITY — `LEAN_PROVEN`
Le noyau X-108 ne peut jamais BLOQUER (`X108_kernel_never_blocks`). La décision finale passe toujours.  
**Théorème :** `X108_kernel_never_blocks`  
**Règle :** Aucune couche périphérique ne peut prendre une décision finale. Guard seul est autorité.

---

### OS2_SIGMA — Veto post-Guard

#### SIGMA_POST_GUARD_VETO_ONLY — `SPEC_ONLY`
Sigma = veto post-Guard uniquement (P56D). Elle ne décide pas.  
**Note :** Pas de preuve Lean formelle. Architecture décidée P56D, gel permanent.  
**Règle :** Tout ajout à sigma/ doit rester en mode veto-only.

---

### OS3_AUDIT_PROOF — Trace et scellés

#### NO_KERNEL_MUTATION_FROM_PERIPHERY — `LEAN_PROVEN`
G1 (immutabilité de trace) : le kernel ne peut pas être muté depuis la périphérie.  
**Théorème :** `Obsidia.G1`

#### ARCHIVE_NOT_RUNTIME — `MIXED_PROOF_STATUS`
G2 (Merkle seal) : archives scellées, non runtime-loadables. Lean prouve la cohérence du sceau. Python confirme l'exclusion du registre.  
**Théorème Lean :** `Obsidia.G2`  
**Python :** tests/test_p71 — SOURCE_ARCHIVE_ONLY ne figure pas dans source_file_registry.

#### PYTHON_TESTED_NOT_LEAN_PROVEN — `DOC_ONLY`
Meta-invariant : un test Python n'est pas une preuve formelle Lean. Les deux statuts sont distincts.  
**Règle :** Ne jamais écrire « prouvé » pour un test pytest. Utiliser LEAN_PROVEN uniquement si `#print axioms` valide.

---

### OS4_PERIPHERY — Périphérie non-décisionnelle

#### NO_PERIPHERY_DECISION_AUTHORITY — `PYTHON_TESTED`
Aucun composant périphérique n'a d'autorité décisionnelle. Tous sont advisory_only.  
**Tests :** P66/P67/P68/P69/P70/P71

#### NO_GRAPHITI_WRITE — `PYTHON_TESTED`
`graphiti_v20_readonly_client.py` — GET uniquement, write=False. P70 confirmé.

#### NO_MEMORY_WRITE_WITHOUT_GATE — `PYTHON_TESTED`
SRL = lecture seule. memory_write_enabled=False confirmé P66.

#### BUS_PROPOSE_ONLY — `PYTHON_TESTED`
Bus Obsidia = PROPOSE_ONLY. emits_act=False. P61 confirmé.

---

### OS5_SOURCES — Sources et adapters

#### DRY_RUN_ONLY_ADAPTERS — `PYTHON_TESTED`
Tous les adapters source : DRY_RUN_ONLY=True, advisory_only=True, runtime_allowed_now=0 (P71).

#### SOURCE_PACK_NOT_CANON_BY_EXISTENCE — `PYTHON_TESTED`
Présence dans _source_packs/ ≠ canonisation. Exige manifest + hashes + registre officiel.

---

### OS6_ROUTES — Auth API

#### ROUTE_AUTH_BOUNDARY — `PYTHON_TESTED`
Routes sensibles = `Depends(require_api_key)`. 503 fail-fermé. Finding ouvert : POST /preview (P69/P71).

---

### OS7_NETWORK — Egress réseau

#### NETWORK_EGRESS_REVIEW_REQUIRED — `PYTHON_TESTED`
Connecteurs actifs (aviation/bank/trading) = DO_NOT_RUN sans dry_run gate (P70).

---

## 4. Théorèmes Lean mappés — 16 entrées

| Théorème | Fichier Lean | Invariants couverts |
|---|---|---|
| `X108_no_act_before_tau` | TemporalKernel.lean | NO_ACT_BEFORE_TAU, HOLD_BEFORE_TAU, KX108_ONLY |
| `X108_after_tau_equals_base` | TemporalKernel.lean | IRREVERSIBLE_ACTION_DELAY, REVERSIBLE_ACTION_BASELINE |
| `X108_kernel_never_blocks` | TemporalKernel.lean | GUARD_X108_FINAL_AUTHORITY, HOLD_BEFORE_TAU, KX108_ONLY |
| `X108_reversible_equals_base` | TemporalKernel.lean | REVERSIBLE_ACTION_BASELINE |
| `X108_irreversible_after_tau_equals_base` | TemporalKernel.lean | IRREVERSIBLE_ACTION_DELAY |
| `skew_negative_implies_hold` | TemporalBridge.lean | NEGATIVE_CLOCK_SKEW_TO_HOLD, NO_ACT_BEFORE_TAU |
| `canonicalize_preserves_nonneg` | TemporalBridge.lean | NO_ACT_BEFORE_TAU, NEGATIVE_CLOCK_SKEW_TO_HOLD |
| `no_two_distinct_supermajorities_4` | Consensus.lean | THRESHOLD_CONSERVATION, DETERMINISM |
| `aggregate4_fail_closed` | Consensus.lean | BLOCK_PRIORITY_OVER_HOLD_ALLOW, THRESHOLD_CONSERVATION |
| `aggregate4_unanimous` | Consensus.lean | DETERMINISM, THRESHOLD_CONSERVATION |
| `aggregate4_act` | Consensus.lean | HOLD_PRIORITY_OVER_ALLOW, THRESHOLD_CONSERVATION |
| `Obsidia.D1` | Basic.lean | DETERMINISM |
| `Obsidia.E2` | Basic.lean | DETERMINISM |
| `Obsidia.G1` | Basic.lean | NO_KERNEL_MUTATION_FROM_PERIPHERY |
| `Obsidia.G2` | Basic.lean | ARCHIVE_NOT_RUNTIME |
| `Obsidia.G3` | Basic.lean | BLOCK_PRIORITY_OVER_HOLD_ALLOW, HOLD_PRIORITY_OVER_ALLOW |

---

## 5. Matrice LEAN_PROVEN vs PYTHON_TESTED

| Claim | Lean | Python | Public claimable |
|---|:---:|:---:|:---:|
| Aucune action irréversible avant τ | `X108_no_act_before_tau` | ✓ | **OUI** |
| Noyau X108 ne bloque jamais | `X108_kernel_never_blocks` | ✓ | **OUI** |
| Déterminisme du vote (aggregate4) | `aggregate4_unanimous` | ✓ | **OUI** |
| Fail-closed par défaut (BLOCK) | `aggregate4_fail_closed` | ✓ | **OUI** |
| Skew négatif → HOLD | `skew_negative_implies_hold` | ✓ | **OUI** |
| Immutabilité de la trace | `Obsidia.G1` | ✓ | **OUI** |
| Merkle seal cohérent | `Obsidia.G2` | ✓ | **OUI** |
| Graphiti en lecture seule | ✗ | ✓ | NON |
| Routes API sécurisées | ✗ | ✓ | NON |
| Adapters source DRY_RUN_ONLY | ✗ | ✓ | NON |
| Sigma = veto post-Guard | ✗ | ✓ | NON |
| Connecteurs actifs DO_NOT_RUN | ✗ | ✓ | NON |

---

## 6. Règles de stabilisation périphérie

| Domaine | Statut | Palier audit | Action si violation |
|---|---|---|---|
| MEMORY_SRL | COMPLIANT | P66 | IMMEDIATE_HOLD |
| GRAPHITI | COMPLIANT | P70 | IMMEDIATE_HOLD |
| AGENTS | COMPLIANT | P71 | CLASSIFIER_HOLD |
| BUS | COMPLIANT | P61 | IMMEDIATE_HOLD |
| CONNECTORS | REVIEW_REQUIRED | P70 | DO_NOT_RUN |
| SOURCE_PACKS | COMPLIANT | P71 | AUDIT_REQUIRED |
| UI_ROUTES | PARTIAL_REVIEW | P69 | APPLY_AUTH |

---

## 7. Règles d'extension sûre

| Règle | Titre | Invariants Lean protégés |
|---|---|---|
| EXT_SAFE_01 | Déclarer invariant_coverage | DETERMINISM, NO_ACT_BEFORE_TAU, GUARD_X108_FINAL_AUTHORITY |
| EXT_SAFE_02 | Ne pas modifier proofs/lean/ | NO_ACT_BEFORE_TAU, IRREVERSIBLE_ACTION_DELAY, THRESHOLD_CONSERVATION |
| EXT_SAFE_03 | Ne pas modifier sigma/ | SIGMA_POST_GUARD_VETO_ONLY, GUARD_X108_FINAL_AUTHORITY |
| EXT_SAFE_04 | DRY_RUN_ONLY=True obligatoire | DRY_RUN_ONLY_ADAPTERS, NO_PERIPHERY_DECISION_AUTHORITY |
| EXT_SAFE_05 | X108 autorité finale — no court-circuit | KX108_ONLY_DECISION_AUTHORITY, GUARD_X108_FINAL_AUTHORITY |
| EXT_SAFE_06 | aggregate4 (3/4) seul agrégateur valide | THRESHOLD_CONSERVATION, BLOCK_PRIORITY_OVER_HOLD_ALLOW |
| EXT_SAFE_07 | Nouveau connecteur réseau → audit palier | NETWORK_EGRESS_REVIEW_REQUIRED |

---

## 8. Sur-claims interdits

1. Ne pas écrire « prouvé formellement » pour un test pytest
2. Ne pas écrire « Lean prouve X » si X n'est pas dans `#print axioms`
3. Ne pas confondre TLA+ model-checking (état fini) et preuve Lean (universel)
4. Ne pas prétendre que PYTHON_TESTED = LEAN_PROVEN

---

## 9. Décision

P72 ne patche pas. P72 aligne.

**Invariants LEAN_PROVEN (11) :** DETERMINISM, NO_ACT_BEFORE_TAU, HOLD_BEFORE_TAU, IRREVERSIBLE_ACTION_DELAY, REVERSIBLE_ACTION_BASELINE, NEGATIVE_CLOCK_SKEW_TO_HOLD, THRESHOLD_CONSERVATION, BLOCK_PRIORITY_OVER_HOLD_ALLOW, HOLD_PRIORITY_OVER_ALLOW, GUARD_X108_FINAL_AUTHORITY, NO_KERNEL_MUTATION_FROM_PERIPHERY

**Invariants PYTHON_TESTED (8) :** NO_PERIPHERY_DECISION_AUTHORITY, NO_GRAPHITI_WRITE, NO_MEMORY_WRITE_WITHOUT_GATE, DRY_RUN_ONLY_ADAPTERS, BUS_PROPOSE_ONLY, ROUTE_AUTH_BOUNDARY, NETWORK_EGRESS_REVIEW_REQUIRED, SOURCE_PACK_NOT_CANON_BY_EXISTENCE

**Invariants SPEC/DOC (3) :** SIGMA_POST_GUARD_VETO_ONLY (SPEC), KX108_ONLY_DECISION_AUTHORITY (SPEC), PYTHON_TESTED_NOT_LEAN_PROVEN (DOC)

**Mixed (1) :** ARCHIVE_NOT_RUNTIME (G2 Lean + Python)

**Findings ouverts portés P72 :**
- POST /preview + POST /os-map/query sans auth (P69/P71 → ADD_REQUIRE_API_KEY)
- Connecteurs aviation/bank/trading = CONNECTOR_ACTIVE_REVIEW (P70)
- source_pack_resolver downloads path absolu (P69/P71)

**Prochain geste : P73 — Agents Complementary Reconciliation.**

---

**Verdict :** `P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT_READY`
