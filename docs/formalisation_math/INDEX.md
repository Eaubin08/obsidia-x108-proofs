# FORMALISATION MATHÉMATIQUE — INDEX MAÎTRE
**Obsidia X-108 | Kernel déterministe souverain**
**Créé le :** 2026-06-25  
**Autorité :** ROLE_005 (Architecte)  
**Décision finale :** KX108_ONLY — aucune IA ne décide seule de la promotion d'un concept en preuve.

---

## SOURCES AUDITÉES

| Fichier dans ce dossier | Source d'origine | Date source |
|---|---|---|
| `THEOREMES_LEAN_INVENTAIRE.md` | `BUREAU_OBSIDIA_2026/1_AUDITS_TECHNIQUES/x108_current_lean_theorems.txt` | Audit continu |
| `STATUTS_FORMALISATION.md` | `CHECKPOINT_V1/09_FORMALISATIONS_MATH_A_VENIR.md` | 2026-06-20 |
| `FILE_DE_PREUVE.md` | `V3_2_ACTIONABLE/08_FORMALIZATION_AND_PROOF_QUEUE.md` | 2026-06-21 |
| `LYAPUNOV_ET_POG.md` | `docs/MATH_CORE_POG_INTEGRATION_REPORT.md` | 2026-05-19 |
| `SCOPE_ET_PERIMETRE.md` | `docs/PROOF_SCOPE.md` | 2026-04-22 (P1 freeze) |
| `THEOREMES_LEAN4_TLA_BRUTS.md` | `proofs/lean/Obsidia/*.lean` + `proofs/tla/*.tla` | Freeze V18 |

---

## ÉTAT GLOBAL DES PREUVES (snapshot 2026-06-25)

| Catégorie | Nombre | Statut |
|---|---|---|
| Preuves Lean 4 formelles compilées (sans sorry) | **57** | `FREEZE_CONFIRMED` — DO_NOT_TOUCH |
| Pépites formalisées documentées (P1–P94+) | **70+** | `FORMALISE` ou `ANCREE` |
| Concepts à formaliser mathématiquement | **11** | `TO_FORMALIZE` |
| Nouveaux théorèmes Lean à écrire | **7** | `TO_PROVE` |
| Concepts à tester en code (pas Lean) | **10** | `TO_TEST_LATER` |
| Différés / recherche | **12** | `DO_NOT_PROVE_NOW` ou `TO_KEEP_AS_RESEARCH` |

---

## NAVIGATION RAPIDE

- **Voir tous les théorèmes Lean existants** → `THEOREMES_LEAN_INVENTAIRE.md`
- **Voir quoi est formalisé / pas encore** → `STATUTS_FORMALISATION.md`
- **File de 7 nouveaux théorèmes à prouver** → `FILE_DE_PREUVE.md`
- **Fonction de Lyapunov L(x) et PoG(x)** → `LYAPUNOV_ET_POG.md`
- **Règles du périmètre de preuve publique** → `SCOPE_ET_PERIMETRE.md`
- **Théorèmes bruts des fichiers .lean et .tla** → `THEOREMES_LEAN4_TLA_BRUTS.md`

---

## RÈGLES ABSOLUES

```
kernel_mutation     = False
decision_authority  = KX108_ONLY
emits_verdict       = False  (ce dossier est READ_ONLY)
sorry_policy        = ZERO_TOLERANCE
promotion_gate      = HUMAN_APPROVED_WRITE uniquement
```

Aucun théorème ne passe de TO_PROVE à ALREADY_PROVEN sans :
1. Lake build SUCCESS sans sorry
2. Validation par ROLE_005 (Architecte)
3. Commit signé sur `main`
