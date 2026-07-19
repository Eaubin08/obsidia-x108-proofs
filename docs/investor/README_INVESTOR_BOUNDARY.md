# Investor Boundary — Obsidia X-108

**Généré :** P78 — Presentation Proof Public Private Split  
**Date :** 2026-06-09  
**Mode :** DOC_INDEX_ONLY — aucune modification runtime

---

## Principe

> **Narratif investisseur ≠ audit RSSI.**  
> **Les docs investisseurs ne doivent pas prétendre plus que P72/P77 autorise.**

Les narratifs investisseur sont séparés du proof technique. Ils peuvent être partagés avec des tiers mais doivent respecter les bornes de claims établies par `specs/00_SCOPE_DISCIPLINE/`.

---

## Fichiers identifiés — narratif investisseur

| Fichier | Catégorie | Action |
|---|---|---|
| `docs/demo/OBSIDIA_F41_PUBLIC_INVESTOR_PITCH.md` | DOC_INVESTOR_NARRATIVE | MOVE_LATER_INVESTOR — review claims avant publication |
| `docs/demo/OBSIDIA_F41_INVESTOR_JURY_FAQ.md` | DOC_INVESTOR_NARRATIVE | MOVE_LATER_INVESTOR |
| `docs/demo/OBSIDIA_F41_WHAT_IT_PROVES_AND_DOES_NOT_PROVE.md` | DOC_PUBLIC_SAFE | KEEP_AS_PUBLIC_SAFE — séparateur proof/pitch |
| `docs/civilization/` (4 fichiers) | DOC_INVESTOR_NARRATIVE | MOVE_LATER_INVESTOR — narratif AGI governance |
| `docs/roadmap/NOT_YET_IMPLEMENTED_AFTER_V2.md` | DOC_INVESTOR_NARRATIVE | MOVE_LATER_INVESTOR — roadmap interne |
| `docs/P2_ROADMAP.md` | DOC_INVESTOR_NARRATIVE | MOVE_LATER_INVESTOR |

---

## Règles claims investisseur

Les claims dans les narratifs investisseur doivent respecter :

1. **`specs/00_SCOPE_DISCIPLINE/PUBLIC_ASSERTION_ALLOWED_CLAIMS.md`** — liste des claims autorisés
2. **`specs/00_SCOPE_DISCIPLINE/CLAIM_SCOPE_DISCIPLINE_SPEC.md`** — discipline de scope
3. **`specs/00_SCOPE_DISCIPLINE/FORMAL_PROOF_VS_RUNTIME_APPROXIMATION.md`** — distinction proof/approximation

**Claims autorisés (P72 vérifié) :**
- GuardX108 = autorité finale (LEAN_PROVEN `GUARD_X108_FINAL_AUTHORITY`)
- Sigma = POST_GUARD_VETO_ONLY (P56D gel permanent)
- gamma = 1.0 (confirmé P75)
- RFC3161 timestamp = ancre cryptographique réelle
- Merkle root = ancre cryptographique réelle
- Fail-closed GPS/bank/trading = PYTHON_TESTED

**Claims qui nécessitent une review avant publication :**
- Claims de production live (pas encore autorisé)
- Claims de scaling (non testé hors P2)
- Claims Gencoin/token (review légale requise)

---

## Ce qui NE figure PAS ici

- Proof technique → `docs/proof/` et `proofs/`
- Archives terrain → `docs/freeze/` + `docs/runtime/`
- Moteur propriétaire → `periphery/`, `sigma/`, `runtime_wiring/`

---

**Verdict :** Narratifs investisseur identifiés. Séparation du proof technique confirmée. Review claims avant publication P80.
