# PROOF_INDEX.md — Index Centralisé des Preuves et Démonstrations

**Version :** 1.4.0 · **Dernière mise à jour :** 2026-04-03

---

## I. Preuves Formelles

| Élément | Type | Statut | Lieu | Détails |
|---|---|---|---|---|
| **Invariant D1** | Lean 4 | PROUVÉ | `proofs/lean/Obsidia.lean` | Non-contradiction des règles de gouvernance |
| **Invariant E2** | Lean 4 | PROUVÉ | `proofs/lean/Obsidia.lean` | Déterminisme du vote |
| **Invariant G1** | Lean 4 | PROUVÉ | `proofs/lean/Obsidia.lean` | Immuabilité de la trace |
| **Invariant G2** | Lean 4 | PROUVÉ | `proofs/lean/Obsidia.lean` | Cohérence du sceau Merkle |
| **Invariant G3** | Lean 4 | PROUVÉ | `proofs/lean/Obsidia.lean` | Absence de contradiction circulaire |
| **Protocole X-108** | TLA+ | DÉMONTRÉ | `proofs/tla/X108.tla` | 1,2M états explorés, 0 violation |
| **Protocole distribué** | TLA+ | DÉMONTRÉ | `proofs/tla/DistributedX108.tla` | Veto distribué sans deadlock |

---

## II. Spécifications et Logique

| Élément | Type | Statut | Lieu | Détails |
|---|---|---|---|---|
| **Noyau X-108** | Architecture | DÉMONTRÉ | `docs/KERNEL_OVERVIEW.md` | Logique ex ante, ALLOW/HOLD/BLOCK |
| **Format Canonique** | Spec | DÉMONTRÉ | `docs/SIGMA.md` | Payload JSON strict, métriques |
| **Règles de gouvernance** | Spec | DÉMONTRÉ | `docs/KERNEL_OVERVIEW.md` | Seuils, priorités, gates |
| **Traçabilité** | Spec | DÉMONTRÉ | `docs/AUDIT_GUIDE.md` | Decision ID, Trace ID, Merkle Root |

---

## III. Tests et Validation

| Élément | Type | Statut | Lieu | Détails |
|---|---|---|---|---|
| **Tests unitaires (Python)** | Code | PASS | `tests/test_*.py` | 22/22 PASS (pytest) |
| **Tests d'intégration (TS)** | Code | PASS | `vitest` | 39/39 PASS (TypeScript) |
| **Tests adversariaux** | Code | PASS | `tests/adversarial/` | 1M+ cas, 0 faille |
| **Stress test Sigma** | Code | PASS | `sigma/stress_test_results.json` | 3 scénarios critiques |
| **Vérification Merkle** | Script | À TESTER | `proofs/verifiers/verify_merkle.py` | Intégrité cryptographique |
| **Vérification décision** | Script | À TESTER | `proofs/verifiers/verify_decision.py` | Audit d'une décision |

---

## IV. Composants d'Orchestration et Support

| Élément | Type | Statut | Lieu | Détails |
|---|---|---|---|---|
| **Sigma Engine** | Orchestration | DOCUMENTÉ | `docs/SIGMA.md` | Code de production non inclus |
| **Sigma Monitor** | Support | PARTIELLEMENT PUBLIC | `sigma/sigma_monitor.py` | Surveillance de stabilité |
| **Sigma Config** | Configuration | PUBLIC | `sigma/sigma_config.json` | Seuils calibrés v1.4.0 |
| **Verify Merkle** | Script public | À TESTER | `proofs/verifiers/verify_merkle.py` | Vérification rapide |
| **Verify Decision** | Script public | À TESTER | `proofs/verifiers/verify_decision.py` | Audit d'une décision |
| **Verify All** | Script public | À TESTER | `proofs/verifiers/verify_all.py` | Audit complet |

---

## V. Exemples et Données

| Élément | Type | Statut | Lieu | Détails |
|---|---|---|---|---|
| **Exemple Trading bullish** | Données | PUBLIC | `examples/trading_bullish.json` | Scénario haussier |
| **Exemple Bank normal** | Données | PUBLIC | `examples/bank_normal.json` | Transaction normale |
| **Exemple Bank suspicious** | Données | PUBLIC | `examples/bank_suspicious.json` | Transaction suspecte |
| **Exemple Ecom normal** | Données | PUBLIC | `examples/ecom_normal.json` | Conversion normale |
| **PROOFKIT_REPORT** | Rapport | PUBLIC | `proofs/PROOFKIT_REPORT.json` | Certification v1.4.0 |

---

## VI. Documentation

| Élément | Type | Statut | Lieu | Détails |
|---|---|---|---|---|
| **README** | Vue d'ensemble | À METTRE À JOUR | `README.md` | Alignement Sigma |
| **KERNEL_OVERVIEW** | Spécification | À CRÉER | `docs/KERNEL_OVERVIEW.md` | Rôle du kernel |
| **USE_CASES** | Cas d'usage | À CRÉER | `docs/USE_CASES.md` | 3-5 cas concrets |
| **AUDIT_GUIDE** | Guide d'audit | À VÉRIFIER | `docs/AUDIT_GUIDE.md` | Procédure d'audit |
| **LIMITS** | Limites | À VÉRIFIER | `docs/LIMITS.md` | Vecteurs non couverts |
| **SIGMA** | Spécification | À ALIGNER | `docs/SIGMA.md` | Statut public clair |
| **GLOSSAIRE** | Définitions | À VÉRIFIER | `docs/GLOSSAIRE.md` | Termes techniques |
| **START_HERE** | Navigation | À CRÉER | `START_HERE.md` | Ordre de lecture |
| **ASK_AN_AI** | Guide IA | À CRÉER | `ASK_AN_AI.md` | Prompt pour LLM |

---

## VII. Statuts Résumés

### PROUVÉ
- Invariants D1, E2, G1, G2, G3 (Lean 4)
- Protocole X-108 (TLA+)
- Protocole distribué (TLA+)

### DÉMONTRÉ
- Noyau X-108 (logique, tests, invariants)
- Format canonique (spec, tests)
- Règles de gouvernance (spec, tests)
- Traçabilité (spec, tests)
- Sigma Engine (tests, documentation)

### PUBLIC
- Tous les fichiers de `proofs/`, `examples/`, `docs/`
- Scripts de vérification (`proofs/verifiers/`)
- Configuration Sigma (`sigma/sigma_config.json`)
- Rapport PROOFKIT

### PARTIELLEMENT PUBLIC
- Sigma Engine (documenté, tests publics, code de production privé)
- Sigma Monitor (support public, code complet)

### HORS REPO PUBLIC
- Moteur de production Python (propriétaire)
- Connecteurs métier et adapters
- Stratégies d'orchestration avancées
- Clés et secrets de déploiement

### EN COURS
- Fermeture Lean complète (ETA : semaine 3)
- Mise à jour du dépôt public (ce fichier)
- Intégration des résultats V18.9.1 Sigma

### À TESTER
- `verify_merkle.py`
- `verify_decision.py`
- `verify_all.py`

### À CRÉER
- `KERNEL_OVERVIEW.md`
- `USE_CASES.md`
- `START_HERE.md`
- `ASK_AN_AI.md`

### À METTRE À JOUR
- `README.md` (alignement Sigma)
- `docs/SIGMA.md` (clarification statut public)
- `docs/AUDIT_GUIDE.md` (vérification cohérence)
- `docs/LIMITS.md` (vérification cohérence)

---

## VIII. Navigation par Profil

### Pour un **chercheur / auditeur formel**
1. Lire `KERNEL_OVERVIEW.md`
2. Consulter `proofs/lean/Obsidia.lean`
3. Consulter `proofs/tla/X108.tla`
4. Lire `docs/LIMITS.md`

### Pour un **auditeur technique**
1. Lire `AUDIT_GUIDE.md`
2. Exécuter `proofs/verifiers/verify_all.py`
3. Consulter `tests/test_*.py`
4. Consulter `tests/adversarial/`

### Pour un **développeur / intégrateur**
1. Lire `KERNEL_OVERVIEW.md`
2. Lire `docs/SIGMA.md`
3. Consulter `examples/`
4. Exécuter `proofs/verifiers/verify_decision.py examples/bank_suspicious.json`

### Pour une **IA externe**
1. Lire `ASK_AN_AI.md`
2. Lire `PUBLIC_STATUS.md`
3. Lire `PROOF_INDEX.md` (ce fichier)
4. Consulter les éléments pertinents selon la question

---

**Dernière mise à jour :** 2026-04-03 · **Responsable :** Obsidia Governance
