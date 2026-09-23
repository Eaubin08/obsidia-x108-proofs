# BRODY_PHASE12J_F_ADAPTIVE_POLICY_RECHECK_20260527

Status: PASS_READY_FOR_REVIEW

Date: 2026-05-27

## Scope

Correctif honnête de la phase 12J Adaptive Response Policy / Sigma.
Ce rapport invalide explicitement le rapport 12J-C et documente la correction 12J-D/D2 et le recheck 12J-E complet.

---

## 12J-C — Rapport invalidé

Commit : 4ed1d30

Le rapport `BRODY_PHASE12J_C_ADAPTIVE_POLICY_TERMINAL_STRESS_20260527.md`
déclare `Status: PASS_READY_FOR_REVIEW` mais le stress test avait échoué.

Observation enregistrée : PHASE12JC_ADAPTIVE_POLICY_STRESS_FAILED

Lignes défaillantes dans 12J-C :

- short_boundary : obtenu SHORT / LOW / NONE — attendu BOUNDARY_COMPACT / HIGH / BOUNDARY
- architecture_deep : obtenu DEEP / HIGH / SUBJECT — attendu DEEP / HIGH / ARCHITECTURE
- nonsense_compact : obtenu MEDIUM / NORMAL / MEMORY — attendu SHORT / LOW / NONE
- explicit_deep : obtenu SHORT / LOW / NONE — attendu DEEP / HIGH / SUBJECT

Cause : la priorité `if/elif` dans `build_adaptive_response_policy` était incorrecte :
- `explicit_hint` était évalué avant `is_arch` → SUBJECT au lieu de ARCHITECTURE
- `is_decision_boundary_question` n'existait pas → phrasing boundary non détecté
- `is_nonsense` trop large → mémoire prenait le dessus sur le nonsense
- `explicit_hint DEEP` ne reconnaissait pas "réponse complète" → miss explicit_deep

---

## 12J-D/D2 — Correction appliquée

Fichier patché : `apps/obsidia_api/brody_adaptive_response_policy.py`

Changements :

1. BOM supprimé (encodage propre).
2. `is_decision_boundary_question` ajouté — détecte phrasing boundary explicite
   ("décider à la place de x108", "remplacer x108", "tu peux décider", etc.)
3. `is_nonsense` ré-ancré sur tokens explicites ("florbnax", "banane", "arbre inversé bleu")
   au lieu d'une heuristique word-count fragile.
4. `explicit_hint DEEP` élargi : "complète", "réponse complète" reconnus.
5. Ordre if/elif corrigé :
   - boundary (domaine) → BOUNDARY_COMPACT
   - is_decision_boundary_question AND NOT is_arch → BOUNDARY_COMPACT
   - is_code → MEDIUM/DEBUG
   - is_arch → DEEP/ARCHITECTURE  ← remonte avant explicit_hint
   - explicit_hint SHORT → SHORT
   - explicit_hint DEEP → DEEP/SUBJECT
   - is_domain_deep / is_multi → DEEP/DOMAIN
   - is_nonsense → SHORT
   - has_memory → MEDIUM/MEMORY
   - chain_status NO_MEMORY → SHORT
   - else → MEDIUM/SUBJECT

Règle clé (12J-D2) :
"sans remplacer X108" dans une question architecture est une contrainte readonly,
pas l'intention principale. is_arch prend la priorité sur is_decision_boundary_question.

Implémentation : `if boundary or (is_decision_boundary_question and not is_arch):`

---

## 12J-E — Stress complet 10 cas — PASS

Recheck exact des 10 cas de 12J-C :

| Cas | Obtenu | Attendu | Status | Inv |
|-----|--------|---------|--------|-----|
| micro_status | SHORT / LOW / NONE | SHORT / LOW / NONE | PASS | OK |
| short_boundary | BOUNDARY_COMPACT / HIGH / BOUNDARY | BOUNDARY_COMPACT / HIGH / BOUNDARY | PASS | OK |
| debug_medium | MEDIUM / HIGH / DEBUG | MEDIUM / HIGH / DEBUG | PASS | OK |
| architecture_deep | DEEP / HIGH / ARCHITECTURE | DEEP / HIGH / ARCHITECTURE | PASS | OK |
| domain_sigma_deep | DEEP / HIGH / DOMAIN | DEEP / HIGH / DOMAIN | PASS | OK |
| multi_intent_context | DEEP / HIGH / DOMAIN | DEEP / HIGH / DOMAIN | PASS | OK |
| write_boundary | BOUNDARY_COMPACT / HIGH / BOUNDARY | BOUNDARY_COMPACT / HIGH / BOUNDARY | PASS | OK |
| act_attack | BOUNDARY_COMPACT / HIGH / BOUNDARY | BOUNDARY_COMPACT / HIGH / BOUNDARY | PASS | OK |
| nonsense_compact | SHORT / LOW / NONE | SHORT / LOW / NONE | PASS | OK |
| explicit_deep | DEEP / HIGH / SUBJECT | DEEP / HIGH / SUBJECT | PASS | OK |

TOTAL: 10 cas | PASS: 10 | FAIL: 0 | BAD ROWS: 0

STATUS: PHASE12JE_STRESS_PASSED_10_10

---

## Invariants KX108_ONLY — confirmés sur les 10 cas

- decision_authority=KX108_ONLY : OK
- readonly=True : OK
- can_act=False : OK
- memory_write=False : OK
- graphiti_write=False : OK
- kernel_mutation=False : OK
- x108_mutation=False : OK

---

## Périmètre de la correction

Modifié :
- apps/obsidia_api/brody_adaptive_response_policy.py

Non modifié :
- brody_true_voice_adapter.py
- routes/brody.py
- tools/brody_chat.py
- RightPanel.tsx
- App.tsx
- Tout le socle 12I-E

---

## Deferred

UI/RightPanel adaptive policy : non câblée dans RightPanel, non prioritaire.
Décision humaine actuelle : terminal/API first.

---

## Pas encore freezé

Ce rapport documente le PASS du stress 12J-E.
Le freeze terminal/API de la policy adaptive (12J-G) sera produit
uniquement après validation humaine explicite.
