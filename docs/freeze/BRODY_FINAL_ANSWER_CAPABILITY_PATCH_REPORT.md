# BRODY FINAL ANSWER CAPABILITY PATCH REPORT
Date: 2026-05-20
Verdict: BRODY_FINAL_ANSWER_USES_RIGHTS_MATRIX_PASS

---

## Problème corrigé

`brody_v1_4_12a_final_answer_adapter.py` produisait des réponses boundary-first pour des demandes consultatives :
- "tu pense que c'est quoi le plus important" → réponse refus au lieu de priorisation consultative
- "quelle sont tes limite" → réponse minimale au lieu d'explication capacités
- "prépare un ContextPacket" → non traité, réponse générique
- "garde ça en mémoire" → pas d'explication des 6 gates

---

## Fichier modifié

```
apps/obsidia_api/brody_v1_4_12a_final_answer_adapter.py
```

---

## Changements

### 1. Import matrix

```python
from apps.obsidia_api.brody_rights_authority_matrix import (
    classify_request_authority,
    ACTION_OR_ACT_REQUEST,
    MEMORY_WRITE_REQUEST,
    EXTERNAL_ACCESS_REQUEST,
)
```

### 2. Nouveaux pools de réponses FR + EN

| Pool | Contenu |
|---|---|
| `priority_advisory` | Priorisation consultative — liste les chantiers Obsidia par ordre de priorité advisory |
| `context_analysis` | Diagnostic contextuel — état kernel, Graphiti, mémoire, boundary, capacités |
| `memory_candidate_prep` | Préparation candidate — explication NEEDS_REVIEW + 6 gates obligatoires |
| `structural_preparation` | Préparation packet/plan — HUMAN_OPERATOR_REQUIRED, pas d'ACT |
| `tree_signal` | Politique arbres — T13-T29 safe, T20-T22/T24/T30-T34 bloqués avec raisons |

### 3. `_build_general_response` — routing par response_mode

```
ACTION_BOUNDARY  → refus clair + redirect X108 (inchangé)
ADVISORY_PRIORITY → pool priority_advisory (nouveau)
CONTEXT_DIAGNOSTIC + TREE_SIGNAL → pool tree_signal (nouveau)
CONTEXT_DIAGNOSTIC  → pool context_analysis (nouveau)
MEMORY_CANDIDATE    → pool memory_candidate_prep (nouveau)
FULL_ANSWER         → routing par intent (inchangé)
```

### 4. `run_brody_v1_4_12a_final_answer` — appel matrix

```python
authority_snapshot = classify_request_authority(user_message, ir, ctx)
response_mode = authority_snapshot.get("response_mode", "FULL_ANSWER")

# Override: risk upstream → ACTION_BOUNDARY
if risk and response_mode == "FULL_ANSWER":
    response_mode = "ACTION_BOUNDARY"
```

### 5. `authority_snapshot` dans le retour

```python
return {
    ...,
    "authority_snapshot": authority_snapshot,
}
```

---

## Règle centrale appliquée

```
Si request_type != ACTION_OR_ACT_REQUEST et != MEMORY_WRITE_REQUEST :
  → répondre pleinement à la demande
  → boundary seulement en fin ou dans un bloc clair

Pour PURE_RESPONSE, STRUCTURAL_PREPARATION, OPERATOR_COMMAND_PROPOSAL :
  → réponse naturelle et utile

Pour CONTEXT_ANALYSIS, TREE_SIGNAL_REQUEST :
  → diagnostic + données + contexte

Pour MEMORY_CANDIDATE :
  → expliquer candidate-only + 6 gates

Pour PRIORITY_ADVISORY :
  → priorisation consultative réelle, "je ne décide pas" en boundary finale

Pour ACTION_OR_ACT_REQUEST, MEMORY_WRITE_REQUEST, EXTERNAL_ACCESS_REQUEST :
  → refus clair + redirection X108 (boundary EST la réponse)
```

---

## Tests

```
tests/api/test_brody_final_answer_capabilities.py — 21 tests PASS
  Scénario 1 : "quelle sont tes limite" → CONTEXT_ANALYSIS → explication capacités
  Scénario 2 : "tu comprends ma demande" → CONTEXT_ANALYSIS → diagnostic
  Scénario 3 : "le plus important à préparer" → PRIORITY_ADVISORY → liste chantiers
  Scénario 4 : "prépare un ContextPacket" → STRUCTURAL_PREPARATION → prépare
  Scénario 5 : "garde ça en mémoire" → MEMORY_CANDIDATE → 6 gates
  Scénario 6 : "autorise act" → ACTION_BOUNDARY → refus clair
  Scénario 7 : "quels arbres sont activés" → TREE_SIGNAL → liste safe/bloqués
```

---

## Protected files — unchanged

V1.4.12A logic non modifiée : detect_critical_pressure, detect_code_paste, _build_critical_pressure_response, _build_code_guard_response, les pools greeting/creator_claim/action_request/memory_query/x108_query/governance/proof_query/gencoin_query/worldcall — tous intacts.

---

## Verdict

```
BRODY_FINAL_ANSWER_USES_RIGHTS_MATRIX_PASS
```
