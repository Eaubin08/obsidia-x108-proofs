# OBSIDIA X-108 — TODO Matrix V4
## Audit Date : 2026-05-30 | Mode : READ-ONLY

---

## Format

`ID | Domaine | Gate | Priorité | Type | Fichier/Chemin | Action | Risque si non fait | Validation`

**Priorités** : P0=BLOCKER_V4 | P1=REQUIRED | P2=SHOULD | P3=LATER  
**Types** : FORMAL | TLA | TEST | DOC | CODE | SECURITY | OPS | PACK | CI | GOVERNANCE | RISK

---

## P0 — BLOCKERS V4 (Gate non franchissable sans)

| ID | Domaine | Gate | Type | Chemin | Action | Risque | Validation |
|---|---|---|---|---|---|---|---|
| T01 | LEAN | G1 | FORMAL | periphery/.../P36.lean | Remplacer squelette `by rfl` par preuve complète P36 sans sorry | G1 BLOQUÉE — ne pas clamer V4 proof-complete | `lake build` + `grep -r sorry proofs/lean` = 0 |
| T02 | LEAN | G1 | FORMAL | periphery/.../P107.lean | Remplacer squelette P107 par preuve Lyapunov substantive | G1 BLOQUÉE | idem T01 |
| T03 | LEAN | G1 | FORMAL | periphery/.../P161.lean | Remplacer squelette P161 par preuve calibration énergétique | G1 BLOQUÉE | idem T01 |
| T04 | DOCS | ALL | DOC | PROOF_INDEX.md | Corriger "1,2M états explorés" → états réels (264/528) — affirmation non étayée par logs TLC | Claim faux communicable à externes | Vérification logs TLC vs claims docs |
| T05 | VERIFY | G1 | TEST | proofs/verify_all.py | Diagnostiquer verify_all.log=FAIL vs verify_all_full.log=PASS — réconcilier | Incohérence preuve/vérification | `python proofs/verify_all.py` → exit 0 |

---

## P1 — Requis pour V4 (gates G2-G3)

| ID | Domaine | Gate | Type | Chemin | Action | Risque | Validation |
|---|---|---|---|---|---|---|---|
| T06 | TLA | G1 | TLA | docs/runtime/ | Créer TLC_X108_RESULTS.json horodaté depuis logs existants | RR-10 : traçabilité TLC manquante | JSON créé + checksum |
| T07 | OS3/OS4 | G3 | TEST | tests/ | Créer tests isolation OS3/OS4 (non-contamination L25) | G3 non franchissable sans tests exécutables | pytest OS3/OS4 = PASS |
| T08 | ADELE | G3 | TEST | tests/ | Créer tests ADeLe bank/trading/aviation scénarios | G3 non franchissable | pytest ADeLe 8 scénarios = PASS |
| T09 | MODULES | G3 | TEST | tests/ | Créer mapping A1-A24 → tests runtime | G3 — modules non vérifiables | 24 tests A* PASS |
| T10 | MODULES | G3 | TEST | tests/ | Créer tests T1-T12 exécutables | G3 | 12 tests T* PASS |
| T11 | TLA | G2 | TLA | formal/tla/ | Vérifier que TLC peut être rejoué sur machine fraîche (Java 17 requis) | Reproductibilité non garantie | TLC run reproductible depuis zero |
| T12 | DOCS | G2 | DOC | periphery/ | Créer script vérification cohérence canon 161 (17 blocs × 161 pépites) | G2 reste DOC_ONLY | Script retourne 0 violations |
| T13 | CI | ALL | CI | .github/workflows/ | Ajouter step CI qui rejette si verify_all.py = FAIL | FAIL silencieux en CI | CI gate sur verify_all |
| T14 | WORKTREE | ALL | CODE | (local) | Committer/taguer la chaîne F60-F73 (80+ fichiers untracked, 15 modifiés) | Perte de travail, drift durée | `git status` clean + tag BRODY_F68 |

---

## P2 — Should (amélioration significative)

| ID | Domaine | Gate | Type | Chemin | Action | Risque | Validation |
|---|---|---|---|---|---|---|---|
| T15 | TEST | G3 | TEST | apps/obsidia-workbench/ | Ajouter vitest/jest suite frontend | Frontend sans couverture test | vitest PASS |
| T16 | TEST | G3 | TEST | tests/ | Ajouter tests chaos/load (bank_scale déjà partiel) | Robustesse non attestée | chaos tests PASS |
| T17 | SECURITY | ALL | SECURITY | docs/ | Formaliser threat model + matrice risques GDPR/PCI-DSS | Conformité non documentée | Threat model v1 validé |
| T18 | SECURITY | ALL | SECURITY | .github/workflows/ | Ajouter dep-check/SAST scan en CI | Vulnérabilités non détectées | SAST 0 critical |
| T19 | DOCS | ALL | DOC | docs/ | Corriger PROOF_INDEX.md ref `proofs/lean/Obsidia.lean` → `proofs/lean/Obsidia/` (répertoire) | Référence cassée pour utilisateurs | Links vérifiés |
| T20 | OPS | ALL | OPS | (local) | Documenter fresh-clone Windows vs Linux — SQL Server/Lean/TLC requis | Clone fresh peut bloquer | Checklist reproductible |

---

## P3 — Later (post-G5)

| ID | Domaine | Gate | Type | Chemin | Action | Risque | Validation |
|---|---|---|---|---|---|---|---|
| T21 | FORMAL | G4 | FORMAL | periphery/ | Créer P162r-P169r (extensions R&D) | G4 manquant — non bloquant pour P1 | G4 franchie |
| T22 | PACK | ALL | PACK | docs/demo/ | Mettre à jour pack externe avec statuts réels | Décalage claim/reality | Pack reviewé |
| T23 | GOVERNANCE | G5 | GOVERNANCE | docs/ | Créer document G5 attestation formelle | G5 ne peut pas être déclarée | G5 doc validé |
| T24 | TEST | G3 | TEST | — | Ajouter tests aviation domain (domaine absent des tests actuels) | Aviation non couvert | Aviation tests PASS |

---

## Matrice de dépendances critiques

```
T01 + T02 + T03 → G1 PASS → G5 possible
T05 → T13 (CI gate)
T06 → T11 (TLA reproductible)
T07 + T08 + T09 + T10 → G3 PASS
T12 → G2 PASS
T14 → Clean worktree → Freeze possible
G1 + G2 + G3 + T21 → G4 + G5
```

---

_Audit READ-ONLY — 2026-05-30 — Aucune action exécutée_
