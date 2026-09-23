# OBSIDIA X-108 — File Map V4
## Audit Date : 2026-05-30 | Mode : READ-ONLY

---

## Légende statuts

| Statut | Signification |
|---|---|
| PRESENT | Fichier présent local, confirmé |
| MISSING | Fichier absent du repo local |
| LOCAL_ONLY | Présent local, non vérifiable GitHub (pas d'auth) |
| REMOTE_ONLY | Non trouvé local, possiblement sur GitHub |
| STALE | Présent mais possiblement obsolète |
| DOC_ONLY | Présent mais contenu documentaire sans implémentation |
| NEEDS_REVIEW | Présent mais contenu à vérifier |

---

## 1. Fichiers racine et config

| Chemin | Rôle | Statut local | Note |
|---|---|---|---|
| README.md | Point d'entrée public | PRESENT | 50+ lignes, complet |
| PROOF_INDEX.md | Index centralisé preuves | PRESENT | ⚠ Annonce "1,2M états" non étayé par logs |
| REPRODUCIBILITY_CHECKLIST.md | Checklist reproductibilité | PRESENT | |
| START_HERE.md | Navigation débutant | PRESENT | |
| package.json | Node.js root | PRESENT | |
| requirements.txt | Python deps | PRESENT | pytest, cryptography, openssl, requests, yaml |
| pyproject.toml | Python config | MISSING | |
| CURRENT_BRODY_SIGMA_READONLY_CHAIN_F68.txt | Pointer F68 | PRESENT | Créé 2026-05-30 |

---

## 2. Preuves formelles Lean 4

| Chemin | Rôle | Statut | Sorry | Note |
|---|---|---|---|---|
| proofs/lean/lakefile.lean | Build config Lean | PRESENT | 0 | |
| proofs/lean/Obsidia/TemporalKernel.lean | 5 théorèmes kernel | PRESENT | 0 | LEAN_PROVEN |
| proofs/lean/Obsidia/TemporalX108.lean | Bridge #print axioms | PRESENT | 0 | LEAN_PROVEN |
| proofs/lean/Obsidia/AuditX108Roots.lean | Axiomes audit | PRESENT | 0 | LEAN_PROVEN |
| proofs/lean/Obsidia/Basic.lean | D1, E2 fondamentaux | PRESENT | 0 | LEAN_PROVEN |
| proofs/lean/Obsidia/Refinement.lean | Lifting 2-state→3-state | PRESENT | 0 | LEAN_PROVEN |
| proofs/lean/Obsidia/Seal.lean | P13 sceau | PRESENT | 0 | LEAN_PROVEN |
| proofs/lean/Obsidia/Sensitivity.lean | P15 Merkle immutabilité | PRESENT | 0 | LEAN_PROVEN |
| proofs/lean/Obsidia/Merkle.lean | Arbres hash | PRESENT | 0 | LEAN_PROVEN |
| proofs/lean/Obsidia/Consensus.lean | aggregate4 fail-closed | PRESENT | 0 | LEAN_PROVEN |
| proofs/lean/Obsidia/SystemModel.lean | P17 AuditGrowth | PRESENT | 0 | LEAN_PROVEN |
| proofs/lean/Obsidia/TemporalBridge.lean | Bridge temporel | PRESENT | 0 | LEAN_PROVEN |
| proofs/lean/Obsidia/TemporalRaw.lean | Fondations brutes | PRESENT | 0 | LEAN_PROVEN |
| proofs/lean/Obsidia/CryptoAssumptions.lean | Hypothèses crypto | PRESENT | 0 | LEAN_PROVEN |
| proofs/lean/Obsidia/AuditRoots.lean | 12 #print vérifications | PRESENT | 0 | LEAN_PROVEN |
| proofs/lean/Obsidia/Main.lean | Root module | PRESENT | 0 | LEAN_PROVEN |
| proofs/lean/Obsidia/Audit.lean | Vérifications compilation | PRESENT | 0 | LEAN_PROVEN |
| formal/tla/tlc_results/lean_build.log | Log build Lean | PRESENT | — | BUILD SUCCESS (0 jobs) |

**Total .lean locaux** : 27 fichiers | **sorry** : 0

---

## 3. Preuves Lean squelettes P36/P107/P161 (DOC_ONLY)

| Chemin | Pépite | Contenu | Statut |
|---|---|---|---|
| periphery/.../08_PREUVES_LEAN_TLA/P36__Quintuplet_etat_canonique/P36.lean | P36 | Squelette trivial `by rfl`, marqué TODO V4 | DOC_ONLY |
| periphery/.../08_PREUVES_LEAN_TLA/P107__Stabilite_Lyapunov_delta_epsilon/P107.lean | P107 | Squelette trivial `by rfl`, marqué TODO V4 | DOC_ONLY |
| periphery/.../08_PREUVES_LEAN_TLA/P161__Calibration_energetique_temporelle/P161.lean | P161 | Squelette trivial `by rfl`, marqué TODO V4 | DOC_ONLY |

---

## 4. TLA+ / TLC

| Chemin | Rôle | Statut | Note |
|---|---|---|---|
| formal/tla/X108.tla | Spec abstraite X-108 | PRESENT | 50 lignes, SafetyX108 définie |
| formal/tla/X108_MC.tla | Model-checking config | PRESENT | |
| formal/tla/X108_MC.cfg | TLC config (TauMax=5) | PRESENT | |
| formal/tla/DistributedX108.tla | Variante distribuée | PRESENT | |
| formal/tla/DistributedX108_MC.cfg | Config distribuée | PRESENT | |
| formal/tla/tlc_results/X108_MC_results.log | TLC run X108 | PRESENT | 264 états, 0 violations |
| formal/tla/tlc_results/DistributedX108_results.log | TLC run Dist | PRESENT | 528 états, 0 violations |
| formal/tla/tlc_results/verify_all.log | verify_all.py run | PRESENT | ⚠ CONTENU = FAIL |
| formal/tla/tlc_results/verify_all_full.log | verify_all.py full | PRESENT | CONTENU = PASS |
| proofs/tla/ | Variantes + snapshots TLA | PRESENT | 9+ fichiers .tla/.cfg |

---

## 5. Vérificateurs Python

| Chemin | Rôle | Statut | Note |
|---|---|---|---|
| proofs/verify_all.py | Orchestrateur vérifications | PRESENT | Retourne FAIL sur version courte |
| proofs/verify_decision.py | Vérification décision X-108 | PRESENT | Logs multiples dans tlc_results/ |
| proofs/verify_merkle.py | Vérification Merkle | PRESENT | |

---

## 6. Sigma

| Chemin | Rôle | Statut |
|---|---|---|
| sigma/registry.py | Registry domains (F60) | PRESENT — modifié non-commité |
| sigma/evaluate.py | Dispatcher (F61) | PRESENT — modifié non-commité |
| sigma/packets.py | Packets F62 | PRESENT — non-commité |
| sigma/connectors.py | Connectors F64 | PRESENT — non-commité |
| sigma/orchestrator_preview.py | Orchestrateur preview F66 | PRESENT — non-commité |
| sigma/graphiti_readonly_bridge.py | Bridge Graphiti F70 | PRESENT — non-commité |
| sigma/trees_activation_readonly.py | 34 arbres F71 | PRESENT — non-commité |
| sigma/domains/ | Domaines bank/trading/ecom/gps | PRESENT |
| sigma/tests/ | 20 fichiers test | PRESENT |

---

## 7. Tests

| Catégorie | Chemin | Fichiers | Fonctions test | Statut |
|---|---|---|---|---|
| API tests | tests/api/ | 54 | ~800 | PRESENT |
| Integration | tests/integration/ | 15 | ~200 | PRESENT |
| Non-sovereignty | tests/non_sovereignty/ | 30+ | ~400 | PRESENT |
| Legacy root | tests/legacy_root/ | 4 | ~50 | PRESENT — état uncertain |
| Sigma tests | sigma/tests/ | 20 | ~400 | PRESENT |
| F60-F73 tests | tests/sigma/ + tests/api/ | 13 | ~400 | PRESENT — non-commités |
| TypeScript tests | apps/obsidia-workbench/ | 0 | 0 | MISSING |
| Chaos/Load tests | tests/ | 0 | 0 | MISSING |
| **TOTAL** | | **~262** | **~1967+** | |

---

## 8. CI/CD

| Fichier | Rôle | Statut |
|---|---|---|
| .github/workflows/verify-proofs.yml | Lean + TLA + Python + Sigma | PRESENT |
| .github/workflows/x108-periphery-ci.yml | Python syntax + pytest + manifest | PRESENT |

---

## 9. Connectors

| Fichier | Domaine | Statut |
|---|---|---|
| connectors/bank_normal_flow.py | Bank | PRESENT |
| connectors/trading_live.py | Trading | PRESENT |
| connectors/aviation_robo.py | Aviation | PRESENT |
| connectors/context_packet_flow.py | Context | PRESENT |
| connectors/brody_memory_readonly_flow.py | Memory readonly | PRESENT |

---

## 10. Docs clés

| Chemin | Rôle | Statut |
|---|---|---|
| docs/KERNEL_OVERVIEW.md | Spécification kernel | PRESENT |
| docs/PROOF_SCOPE.md | Périmètre des preuves | PRESENT |
| docs/status/PUBLIC_STATUS.md | Statut public | PRESENT |
| docs/status/P1_FREEZE_NOTE.md | Note gel P1 | PRESENT |
| docs/LIMITS.md | Limites structurelles | PRESENT |
| docs/GLOSSAIRE.md | Glossaire | PRESENT |
| docs/RFC3161.md | RFC3161 | PRESENT |
| docs/SECURITY.md | Policy sécurité | PRESENT |
| docs/demo/ | Pack externe | PRESENT — 5+ fichiers |
| docs/ARCHITECTURE.md | Architecture générale | NEEDS_REVIEW |
| docs/WHAT_IS_X108.md | Explication X-108 | NEEDS_REVIEW |

---

## 11. Fichiers critiques MANQUANTS

| Fichier attendu | Gate | Priorité |
|---|---|---|
| TLC_X108_RESULTS.json dans docs/runtime/ | G1/TLA | P1 |
| P36 preuve complète (non squelette) | G1 | P0 |
| P107 preuve complète (non squelette) | G1 | P0 |
| P161 preuve complète (non squelette) | G1 | P0 |
| Tests OS3/OS4 isolation exécutables | G3 | P1 |
| Tests ADeLe scénarios bank/trading/aviation | G3 | P1 |
| Tests modules A1-A24 runtime | G3 | P1 |
| TypeScript test suite (vitest) | G3 | P2 |
| Chaos / Load tests | G3 | P2 |
| P162r-P169r fichiers | G4 | P3 |

---

## 12. GitHub remote

| Paramètre | Valeur |
|---|---|
| Remote local configuré | https://github.com/Eaubin08/obsidia-x108-proofs.git |
| Repo demandé dans l'audit | Eaubin08/Demo-obsidia-x108-proof |
| **Écart** | **Le remote local est `obsidia-x108-proofs`, pas `Demo-obsidia-x108-proof`** |
| Vérification GitHub | Non disponible (gh CLI non authentifié) |

---

_Audit READ-ONLY — 2026-05-30 — Aucun patch, aucun commit_
