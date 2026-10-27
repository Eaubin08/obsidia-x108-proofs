# 09_PREUVES ET PROOF STACK — Lean 4 / TLA+ / Merkle / RFC3161

```
Mode:  READ_ONLY
Layer: DOCS
Scope: État de la stack de preuves formelles et du scellement
Risk:  NONE
Files touched: 09_PREUVES_ET_PROOF_STACK.md
```

**Sources : feuilles P05_Familles (famille PREUVES), P18_Freeze, Key_Metrics, P11_Agents (Guardians), _coverage_summary.json — CLAUDE.md (chemins fichiers protégés, structure TLA+)**

---

## Famille PREUVES — Chiffres scellés

| Métrique | Valeur | Verdict |
|---|---|---|
| Total items famille PREUVES | 500 | SEALED_NUMBER |
| OK complet | 0 | SEALED_NUMBER |
| Brody seul | 17 | BRODY_ONLY |
| Runtime partiel | 0 | SEALED_NUMBER |
| Non branchés | 483 | NOT_CONNECTED_STRICT |
| Instances présentes | ALL sauf UI | CONFIRMED_BY_TABLE |

**96,6% des items de la famille PREUVES sont non branchés.**

---

## Stack de preuves formelles

### Lean 4
- **Rôle** : Preuves formelles sans `sorry`
- **P35** (Preuve formelle sans sorry) : BRODY_ONLY — visible Brody Enriched, non lié au runtime domain — **CONFIRMED_BY_TABLE (P07)**
- **Freezes Lean** : existance confirmée par `.local_freezes/` — **CONFIRMED_BY_SUPPORT**
- **Verdict** : CONFIRMED_BY_TABLE pour P35 — NEEDS_PROOF pour le machine-checking complet

### TLA+
- **Rôle** : Spécification formelle / Model-checking
- **GUARDIAN_012 — TLA Verifier** : OK — branché Brody + Bank/Trading/GPS — **CONFIRMED_BY_TABLE (P11_Agents)**
- **Verdict** : CONFIRMED_BY_TABLE pour le Guardian — NEEDS_PROOF pour les specs elles-mêmes

### Merkle
- **P13** (Immutabilité par sceau Merkle) : BRODY_ONLY dans P07, ANCREE — **CONFIRMED_BY_TABLE**
- **GUARDIAN_010 — Merkle Verifier** : OK — branché Brody + Bank/Trading/GPS — **CONFIRMED_BY_TABLE (P11_Agents)**
- **Verdict** : CONFIRMED_BY_TABLE

### RFC3161
- **P17** (Croissance du log d'audit) : BRODY_ONLY, ANCREE — **CONFIRMED_BY_TABLE**
- **GUARDIAN_011 — RFC3161 Verifier** : OK — branché Brody + Bank/Trading/GPS — **CONFIRMED_BY_TABLE (P11_Agents)**
- **Verdict** : CONFIRMED_BY_TABLE

---

## Compléments issus de documents projet — non issus du support complet

> Les éléments ci-dessous proviennent de **CLAUDE.md / PROTECTED_SCOPE.md** (instructions du projet), non du XLSX/CSV/TXT de Downloads. Verdict : **CONFIRMED_BY_CLAUDE_MD**.

| Fichier / Chemin | Protection déclarée dans CLAUDE.md | Verdict |
|---|---|---|
| `proofs/V18_3_1/` (répertoire) | Crypto-ancré, scellé, frozen | CONFIRMED_BY_CLAUDE_MD |
| `proofs/V18_7/` (répertoire) | Crypto-ancré, scellé, frozen | CONFIRMED_BY_CLAUDE_MD |
| `proofs/V18_8/` (répertoire) | Crypto-ancré, scellé, frozen | CONFIRMED_BY_CLAUDE_MD |
| `proofs/tla/` (référence) + `formal/tla/` (CI) | Deux arbres TLA+ | CONFIRMED_BY_CLAUDE_MD |
| `merkle_root.json` | Scellé Merkle | CONFIRMED_BY_CLAUDE_MD |
| `merkle_seal.json` | Scellé Merkle | CONFIRMED_BY_CLAUDE_MD |
| `rfc3161_anchor.json` | Ancré RFC3161 | CONFIRMED_BY_CLAUDE_MD |
| `server.kernel.sealed.cjs` | Kernel scellé | CONFIRMED_BY_CLAUDE_MD |
| `sigma/contracts.broken-ragnarok.py` | Intentionnellement cassé | CONFIRMED_BY_CLAUDE_MD |

**DO_NOT_INFER** — Ces fichiers ne doivent pas être modifiés sans décision utilisateur explicite et plan de vérification.

---

## Guardians de preuves (agents actifs)

| Guardian | Rôle | Statut |
|---|---|---|
| GUARDIAN_009 — Sigma Verifier | Vérifie sigma/contracts.py | OK — Brody + Bank/Trading/GPS |
| GUARDIAN_010 — Merkle Verifier | Vérifie intégrité Merkle | OK — Brody + Bank/Trading/GPS |
| GUARDIAN_011 — RFC3161 Verifier | Vérifie ancrage temporel | OK — Brody + Bank/Trading/GPS |
| GUARDIAN_012 — TLA Verifier | Vérifie specs TLA+ | OK — Brody + Bank/Trading/GPS |

---

## Freezes Lean documentés (inventaire partiel)

- `LEAN_57_RECONCILIATION_FINAL_V0_FREEZE_20260619_014248`
- `LEAN_57_RECONCILIATION_FINAL_V0_FREEZE_20260619_014425`
- `LEAN_CANONICAL_SOURCE_SELECTION_AUDIT_V0_FREEZE_20260618_214301`
- `LEAN_PLACEHOLDER_REPAIR_PLAN_V0_FREEZE_20260618_213959`
- `TARGETED_LEAN_PROOFS_AUDIT_V0_FREEZE_KEEP_OPEN_20260618_180729`
- `TARGETED_TLA_FORMAL_AUDIT_V0_FREEZE_20260618_181534`
- `TARGETED_PROOF_REPLAY_RECEIPTS_READOUT_AUDIT_V0_FREEZE_20260618_175153`

**Verdict : CONFIRMED_BY_SUPPORT** pour les freezes existants.

---

## Ce qui n'est PAS implémenté (preuves)

| Élément | Statut | Verdict |
|---|---|---|
| Machine-checking complet des 500 items PREUVES | NON IMPLÉMENTÉ | NEEDS_PROOF |
| Tests adversariaux | NON IMPLÉMENTÉ | NOT_YET_IMPLEMENTED |
| Vue régulateur | NON IMPLÉMENTÉ | NOT_YET_IMPLEMENTED |

**DO_NOT_TEST** — Ne pas lancer lake build / pytest / tests formels sans décision explicite utilisateur.
