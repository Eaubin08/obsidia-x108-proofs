# AUDIT_GUIDE — Guide d'audit pratique

**Version :** 1.0.0 · **Date :** 2026-03-11

Ce guide permet à un auditeur externe d'ouvrir ce repo, lancer le moteur, lancer les tests, vérifier les artefacts et comprendre précisément ce qui est démontré.

---

## 1. Objectif du pack

Ce pack fournit le noyau moteur de décision Obsidia dans un état exécutable et auditable. Il permet de vérifier :

- Que le moteur produit des décisions déterministes (`BLOCK`, `HOLD`, `ACT/ALLOW`)
- Que les invariants de gouvernance (seuils, priorités, gates) sont respectés
- Que les agents domaine (Trading, Bank, Ecom) produisent des votes cohérents
- Que le Guard X-108 applique correctement les règles de blocage et de délai

---

## 2. Périmètre exact audité

| Composant | Auditable | Méthode |
|---|---|---|
| Kernel Python (`obsidia_kernel`) | ✅ | Tests + lecture code |
| Guard X-108 (`guard.py`) | ✅ | Tests + lecture code |
| Agrégation des votes (`aggregation.py`) | ✅ | Tests + lecture code |
| Pipeline CLI (`run_pipeline.py`) | ✅ | Exécution directe |
| Invariants D1/E2/G1/G2/G3 | ✅ | Tests automatisés |
| Simulations TypeScript (engines) | ✅ | Tests Vitest |
| Preuves Lean 4 | ❌ | Non fermées — voir LIMITS.md |
| Données de marché réelles | ❌ | Non intégrées |

---

## 3. Prérequis

```bash
# Python
python3 --version  # >= 3.11
pip install pytest  # >= 7.0

# Optionnel (tests TypeScript)
node --version     # >= 18
pnpm --version     # >= 8
```

---

## 4. Procédure d'installation

```bash
git clone https://github.com/Eaubin08/obsidia-engine-proof-core
cd obsidia-engine-proof-core

# Vérifier la structure
ls -la
# Attendu : engine/ agents/ governance/ tests/ examples/ audit/ ...

# Vérifier les hashes (intégrité des fichiers)
cd hashes/
python3 ../scripts/verify_hashes.py
```

---

## 5. Procédure d'exécution

### Exécution du pipeline complet

```bash
# Trading
python3 agents/run_pipeline.py trading "$(cat examples/trading_bullish.json)"

# Bank
python3 agents/run_pipeline.py bank "$(cat examples/bank_normal.json)"

# Ecom
python3 agents/run_pipeline.py ecom "$(cat examples/ecom_normal.json)"
```

**Vérifier dans la sortie JSON :**
- `x108_gate` est l'un de : `ALLOW`, `HOLD`, `BLOCK`
- `decision_id` est présent et non vide
- `trace_id` est un UUID valide
- `confidence` est dans [0.0, 1.0]
- `ticket_id` est présent si et seulement si `ticket_required = true`

---

## 6. Procédure de test

### Tests Python (invariants + agents)

```bash
cd tests/
pytest -v --tb=short 2>&1 | tee audit_test_results.txt
```

**Résultat attendu :** Tous les tests PASSED. Aucun FAILED, aucun ERROR.

### Tests TypeScript (optionnel)

```bash
cd ../os4-platform/
pnpm test 2>&1 | tee ../obsidia-engine-proof-core/logs/vitest_results.txt
```

**Résultat attendu :** 45/45 PASS.

---

## 7. Vérification de chaque invariant majeur

### D1 — Déterminisme

```bash
pytest tests/test_invariants_against_engine.py::test_determinism -v
```

Vérification manuelle supplémentaire :
```bash
python3 agents/run_pipeline.py trading "$(cat examples/trading_bullish.json)" | python3 -c "import sys,json; print(json.load(sys.stdin)['x108_gate'])"
# Répéter 3 fois → résultat identique
```

### E2 — Non-exécution avant seuil

```bash
pytest tests/test_invariants_against_engine.py::test_no_allow_before_tau -v
```

### G1/G2 — Seuil et frontière

```bash
pytest tests/test_invariants_against_engine.py::test_act_above_threshold tests/test_invariants_against_engine.py::test_hold_at_boundary -v
```

### G3 — Monotonie

```bash
pytest tests/test_invariants_against_engine.py::test_monotonicity -v
```

### Guard X-108 — BLOCK sur contradictions

```bash
pytest tests/test_agents_functional.py::test_guard_block_on_contradictions -v
```

---

## 8. Comment lire les logs et traces

### Structure d'une `CanonicalDecisionEnvelope`

```
domain          → domaine de décision (trading/bank/ecom)
market_verdict  → verdict des agents (EXECUTE_LONG, AUTHORIZE, PAY, etc.)
confidence      → score de confiance agrégé [0.0, 1.0]
contradictions  → liste des contradictions détectées
unknowns        → liste des inconnues détectées
risk_flags      → flags de risque (FRAUD_PATTERN, VELOCITY_ANOMALY, etc.)
x108_gate       → décision finale Guard X-108 (ALLOW/HOLD/BLOCK)
reason_code     → code de raison de la décision
severity        → sévérité (S0=normal, S1=attention, S2=hold, S3=alerte, S4=block)
decision_id     → identifiant unique de la décision
trace_id        → UUID de traçabilité
ticket_required → true si ALLOW (ticket d'exécution requis)
ticket_id       → identifiant du ticket (présent si ticket_required=true)
attestation_ref → hash SHA-256 des evidence_refs (24 chars)
evidence_refs   → hashes des votes agents individuels
metrics         → métriques détaillées (scores par verdict)
```

### Lecture des logs de test

```bash
# Voir les résultats détaillés
cat logs/audit_test_results.txt

# Filtrer les PASS/FAIL
grep -E "PASSED|FAILED|ERROR" logs/audit_test_results.txt
```

---

## 9. Vérification des hashes

```bash
cd hashes/
cat engine_files.sha256
# Vérifier avec sha256sum
sha256sum -c engine_files.sha256
```

---

## 10. Checklist finale d'audit

| # | Étape | Résultat attendu | Vérifié |
|---|---|---|---|
| 1 | `git clone` réussi | Repo cloné sans erreur | ☐ |
| 2 | Structure conforme | Tous les dossiers présents | ☐ |
| 3 | `pip install pytest` | Pas d'erreur | ☐ |
| 4 | `pytest tests/ -v` | 100% PASS | ☐ |
| 5 | Pipeline Trading exécuté | JSON valide retourné | ☐ |
| 6 | Pipeline Bank exécuté | JSON valide retourné | ☐ |
| 7 | Pipeline Ecom exécuté | JSON valide retourné | ☐ |
| 8 | Déterminisme vérifié (3 appels) | `x108_gate` identique | ☐ |
| 9 | BLOCK sur 2 contradictions | `x108_gate = BLOCK` | ☐ |
| 10 | FRAUD_PATTERN → BLOCK | `x108_gate = BLOCK` | ☐ |
| 11 | Hashes vérifiés | `sha256sum -c` OK | ☐ |
| 12 | LIMITS.md lu | Limites comprises | ☐ |

---

## 11. Verdicts possibles

| Verdict | Condition |
|---|---|
| **Démontré** | Test automatisé PASS + exécution manuelle cohérente |
| **Partiellement démontré** | Test présent mais couverture incomplète, ou logique lisible sans test dédié |
| **Non démontré** | Affirmé dans la documentation mais sans test ni artefact vérifiable |

---

## 12. Ce que ce pack prouve réellement

- **Déterminisme du kernel** : prouvé par tests automatisés (D1)
- **Respect du seuil theta_S** : prouvé par tests automatisés (E2, G1, G2, G3)
- **Priorité BLOCK sur contradictions** : prouvé par test fonctionnel
- **FRAUD_PATTERN force BLOCK** : prouvé par test fonctionnel
- **Pipeline complet exécutable** : prouvé par exécution directe (Trading, Bank, Ecom)
- **Déterminisme des simulations** : prouvé par tests Vitest (45/45 PASS)
- **Format `CanonicalDecisionEnvelope` conforme** : prouvé par tests de contrats

## 13. Ce que ce pack ne prouve pas

- **Correction formelle complète** : les preuves Lean 4 ne sont pas fermées
- **Comportement sur données réelles** : uniquement testé sur données synthétiques
- **Résistance aux attaques adversariales** : non testée
- **Performance à l'échelle** : non benchmarkée
- **Non-anticipation formelle** : déclarative, non vérifiée à l'exécution
- **Intégration production** : le moteur est autonome mais non connecté à des sources de données réelles dans ce repo
