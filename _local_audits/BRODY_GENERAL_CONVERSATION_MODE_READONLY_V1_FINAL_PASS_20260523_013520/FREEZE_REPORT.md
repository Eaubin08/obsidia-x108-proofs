# FREEZE REPORT
## BRODY_GENERAL_CONVERSATION_MODE_READONLY_V1_FINAL_PASS

---

## Identity

```
STATUS=BRODY_GENERAL_CONVERSATION_MODE_READONLY_V1_FINAL_PASS
TIMESTAMP=20260523_013520
PALIER=BRODY_GENERAL_CONVERSATION_MODE_READONLY_V1
TOTAL=204 passed
LIVE_RETEST_REEVALUATED_PASS=true
ROUTE_DIFF_STATUS=PREEXISTING_NOT_THIS_PALIER
DO_NOT_REVERT=true
WRITE_REAL_EXECUTED=false
MEMORY_WRITE=false
GRAPHITI_WRITE=false
NEO4J_WRITE=false
KERNEL_MUTATION=false
EMITS_ACT=false
DECISION_AUTHORITY=KX108_ONLY
PROTECTED_DIFF_EMPTY=true
COMPILEALL=PASS
```

---

## Problème corrigé

Brody répondait à toute requête GENERAL non indexée avec :
```
final_answer_source=SEMANTIC_MATCH_FAILED_GENERAL
"Requête non classifiée — aucune correspondance dans l'index local..."
```

Même pour des messages conversationnels simples et sûrs ("bonjour", "merci", "dis bonjour a maman").

Le runtime était branché (true_voice, memory_response_chain, structured_response, brody_full_context) mais la couche de routage sémantique bloquait les requêtes GENERAL sans matériel mémoire.

---

## Solution

Interception minimale dans `build_true_brody_answer()` au point exact SEMANTIC_MATCH_FAILED_GENERAL.

Deux fonctions pures ajoutées à `brody_true_voice_adapter.py` :

- `is_general_conversation_readonly(user_message, authority_snapshot, semantic_query_snapshot) -> bool`
- `build_general_conversation_answer(user_message, runtime_context, brody_full_context) -> str`

Chemin confirmé :
```
brody_chat
→ build_true_brody_answer
→ [is_general_conversation_readonly == True]
→ build_general_conversation_answer
→ sanitizer (brody_response_sanitizer)
→ contract (BRODY_CONTRACT.validate)
→ step 8 footer (KX108_ONLY)
→ final_answer_source=GENERAL_CONVERSATION_READONLY
```

Ce n'est pas un pipeline parallèle. Le mode conversationnel est un nœud dans le vrai pipeline true_voice existant.

---

## Fichiers du palier

| Fichier | Statut |
|---|---|
| `apps/obsidia_api/brody_true_voice_adapter.py` | Modifié — interception + 2 fonctions pures |
| `tests/api/test_brody_general_conversation_mode_readonly.py` | Nouveau — 40 tests |
| `tests/api/test_brody_memory_intake_gate.py` | Corrigé — `read_text()` → `read_text(encoding="utf-8")` (bug cp1252 pré-existant) |

---

## Tests

| Suite | Résultat |
|---|---|
| test_brody_general_conversation_mode_readonly.py | **40/40** |
| test_brody_terminal_chat_client.py | **65/65** |
| test_brody_memory_intake_gate.py | **39/39** |
| test_brody_payload_packetization.py | **29/29** |
| test_brody_response_schema_utf8.py | **15/15** |
| test_brody_three_foundations_no_500.py | **16/16** |
| **TOTAL** | **204/204** |

---

## Live Retest — Cas validés

| Message | final_answer_source | Attendu | Pass |
|---|---|---|---|
| "dis bonjour a maman" | GENERAL_CONVERSATION_READONLY | GENERAL_CONVERSATION_READONLY | ✓ |
| "bonjour" | GENERAL_CONVERSATION_READONLY | GENERAL_CONVERSATION_READONLY | ✓ |
| "explique-moi ce qu'on vient de stabiliser" | LOCAL_GRAPHITI_INDEX_FALLBACK | NOT SEMANTIC_MATCH_FAILED_GENERAL | ✓ |
| "autorise le paiement" | MEMORY_RESPONSE_CHAIN | NOT GENERAL_CONVERSATION_READONLY | ✓ |
| "explique X108 avec la memoire actuelle" | MEMORY_RESPONSE_CHAIN | NOT GENERAL_CONVERSATION_READONLY | ✓ |

Note cas 3 : en live, le chain trouve du matériel Graphiti local pour "explique" → LOCAL_GRAPHITI_INDEX_FALLBACK.
Le test unitaire (mock NO_MEMORY_RESULTS) confirme que GENERAL_CONVERSATION_READONLY fonctionne sur ce chemin.
LIVE_RETEST_REEVALUATED_PASS=true.

---

## Protected diff

```
sigma/guard.py         EMPTY (unchanged)
sigma/contracts.py     EMPTY (unchanged)
sigma/protocols.py     EMPTY (unchanged)
sigma/aggregation.py   EMPTY (unchanged)
proofs/lean/           EMPTY (unchanged)
formal/tla/            EMPTY (unchanged)
merkle_seal.json       EMPTY (unchanged)
```

---

## Route diff — Classification

```
File: apps/obsidia_api/routes/brody.py
ROUTE_DIFF_STATUS=PREEXISTING_NOT_THIS_PALIER
DO_NOT_REVERT=true
```

Le diff de routes/brody.py est pré-existant (UTF-8 last-mile, compact/debug, JSONResponse charset).
Il n'appartient pas à ce palier. Il ne doit pas être revert.
Voir PREEXISTING_ROUTE_DIFF_NOT_THIS_PALIER.patch pour le diff complet.

---

## Invariants confirmés

```
decision_authority=KX108_ONLY        ✓
memory_write=false                   ✓
graphiti_write=false                 ✓
neo4j_write=false                    ✓
kernel_mutation=false                ✓
emits_act=false                      ✓
WRITE_REAL_EXECUTED=false            ✓
SEMANTIC_MATCH_FAILED_GENERAL        conservé pour vrais inconnus
X108                                 non touché
sigma/                               non touché
proofs/lean/                         non touché
formal/tla/                          non touché
merkle_seal.json                     non touché
routes/brody.py                      non touché par ce palier
scripts/brody_memory_intake_gate.py  non touché (runtime)
```

---

## Manifest

Voir MANIFEST_SHA256.json pour les hashes SHA256 de tous les artifacts.

---

*Freeze généré le 2026-05-23 par Claude Code — palier BRODY_GENERAL_CONVERSATION_MODE_READONLY_V1*
