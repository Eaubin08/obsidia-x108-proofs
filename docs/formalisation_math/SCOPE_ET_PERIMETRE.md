# SCOPE ET PÉRIMÈTRE DES PREUVES — Obsidia X-108
**Source :** `docs/PROOF_SCOPE.md` (freeze P1 — 2026-04-22)

---

## CATÉGORIES CANONIQUES DE PREUVES

### 1. Preuves formelles Lean 4
- Répertoire : `proofs/lean/`
- Outil : Lean 4 + Lake
- PASS = le périmètre public compile sans erreur, sans sorry

### 2. Model-checking TLA+ / TLC
- Répertoire : `formal/tla/`
- Outil : TLC via `tla2tools.jar` (Java 17+)
- PASS = aucune violation détectée dans l'ensemble de runs validés

### 3. Vérification exécutable Python
- Scripts : `verify_all.py`, `verify_decision.py`
- Répertoire : `proofs/`
- PASS = les scénarios canoniques publics valident

### 4. Couche Sigma minimale publique
- Répertoires : `sigma/run_pipeline.py`, `sigma/sigma_monitor.py`, `sigma/examples/`, `sigma/tests/`
- PASS = les smoke tests et la structure publique Sigma passent

### 5. QA et sondage réseau
- `qa/cross-platform/test_rfc3161_anchor_schema.py`
- `qa/cross-platform/test_rfc3161_cross_platform.py`
- PASS = QA public passe (pas de garantie permanente des TSA tiers)

---

## DÉCOMPOSITION DU COMPTEUR 8007

Le commit `feat: stabilize kernel at 8007 proofs` couvre les 5 catégories ci-dessus.

Pour recalculer localement :
```bash
python RECUPE_SCORING/aggregation_stable.py
```

**Note :** 8007 est une ligne de base de stabilité, pas un absolu. Peut augmenter sur `main`.  
La cible d'audit P1 reste le tag `p1-freeze-2026-04-22`.

---

## CE QU'EST LE REPO PUBLIC

- Une couche publique de preuves
- Une couche publique de vérification  
- Une couche publique d'exécution pour P1

## CE QUE N'EST PAS LE REPO PUBLIC

- Le moteur propriétaire de production complet
- La couche Sigma de production complète
- Le cockpit opérateur final
- Tous les adaptateurs métier de production

---

## HIÉRARCHIE D'INTERPRÉTATION

En cas de doute, lire dans cet ordre :
1. `docs/status/P1_FREEZE_NOTE.md`
2. `docs/status/PUBLIC_STATUS.md`
3. `README.md`
4. `docs/PROOF_SCOPE.md`

---

## FICHIERS SCELLÉS / DO_NOT_TOUCH

```
server.kernel.sealed.cjs    ← sceau cryptographique du kernel
proofs/V18_*/               ← bundles freeze V18
proofs/lean/57_preuves      ← 57 preuves formelles compilées
merkle_seal.json            ← ancrage Merkle
rfc3161/                    ← ancre temporelle RFC3161
```

**Règle :** Aucune édition, reformatage, renommage ou régénération sans plan de vérification approuvé par ROLE_005.
