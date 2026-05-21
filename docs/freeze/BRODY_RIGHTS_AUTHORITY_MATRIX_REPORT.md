# BRODY RIGHTS / AUTHORITY / CAPABILITY MATRIX REPORT
Date: 2026-05-20
Verdict: BRODY_RIGHTS_AUTHORITY_MATRIX_PASS

---

## Problème corrigé

Brody répondait trop souvent comme si toute demande était une demande de décision ou d'ACT.
Il répétait "je ne décide pas" au lieu de répondre pleinement quand la demande était consultative.

**Clarification structurelle appliquée :**
- Répondre n'est pas décider
- Analyser n'est pas décider
- Préparer un ContextPacket n'est pas décider
- Préparer un IR candidate n'est pas décider
- Préparer une mémoire candidate n'est pas écrire mémoire
- Proposer une priorisation advisory n'est pas ACT
- Classifier une intention n'est pas exécuter

---

## Fichier créé

```
apps/obsidia_api/brody_rights_authority_matrix.py
```

Expose :
- `get_brody_capability_matrix()` — matrice complète, 10 catégories
- `classify_request_authority(user_message, ir_candidate, context_packet)` — classification par requête

---

## Sources canoniques fusionnées

| Source | Extraction |
|---|---|
| BRODY_SESSION_CHECKPOINT_FINAL (2026-05-13) | Brody = LLM obsidien, X108/KX108 = seule autorité, Graphiti readonly, memory intake candidate only, operator loop validé |
| BRODY_REAL_ARCHITECTURE_MAP_READONLY (2026-05-13) | Flux opérateur → command gate → API/Graphiti → ContextPacket → Brody → réponse structurée → validation → handoff → X108 |
| CURRENT_BRODY_HUMAN_COMMAND_PACKET_READONLY | HUMAN_OPERATOR_REQUIRED=true, BRODY_EXECUTE_ALLOWED=false, BRODY_AUTHORIZE_ALLOWED=false, READONLY_ANALYSIS_ONLY=true |
| CURRENT_BRODY_API_BRIDGE_RUNTIME_ACTIVATION_GATE_READONLY | ACTIVATION_BLOCKED=true, HUMAN_AUTHORIZATION_REQUIRED=true, DECISION_AUTHORITY=KX108_ONLY |
| T13_T34_SIGNAL_DISCOVERY_READONLY (2026-05-14) | 13 arbres safe, 9 bloqués, signal PATH_SLUG, 117 safe docs |
| WRITABLE_MEMORY_ACTIVATION_CHECKLIST (2026-05-14) | writable_memory_active=false, 6 gates obligatoires, 0/6 pass |
| X108_boundary___kernel_decision_authority.json | validated=true, decision_authority=KX108_ONLY, kernel_mutation=false |

---

## 10 catégories de la matrice

| # | Catégorie | response_mode | Brody peut | Brody ne peut pas |
|---|---|---|---|---|
| 1 | PURE_RESPONSE | FULL_ANSWER | Répondre, contextualiser, structurer | Décider, ACT, write |
| 2 | CONTEXT_ANALYSIS | CONTEXT_DIAGNOSTIC | Lire Graphiti, diagnostic, expliquer capacités | Modifier mémoire, décider |
| 3 | STRUCTURAL_PREPARATION | FULL_ANSWER | Produire ContextPacket candidat, IR candidate, plan | Exécuter, write, ACT |
| 4 | MEMORY_CANDIDATE | MEMORY_CANDIDATE | Préparer candidat, expliquer 6 gates | Écrire Graphiti/Neo4j auto |
| 5 | OPERATOR_COMMAND_PROPOSAL | FULL_ANSWER | Préparer Human Command Packet, classifier commandes | Exécuter à la place de l'humain |
| 6 | EXTERNAL_ACCESS_REQUEST | ACTION_BOUNDARY | GET-only si allowlist, dry-run packet | Runtime si activation gate blocked, POST |
| 7 | ACTION_OR_ACT_REQUEST | ACTION_BOUNDARY | Expliquer refus, produire action candidate pour X108 | Émettre ACT/HOLD/BLOCK, bypass X108 |
| 8 | MEMORY_WRITE_REQUEST | ACTION_BOUNDARY | Candidate only, review gate, template approbation | Écrire Graphiti/Neo4j auto |
| 9 | TREE_SIGNAL_REQUEST | CONTEXT_DIAGNOSTIC | Lire arbres safe T13-T19/T23/T25-T29, citer bloqués | Déclencher T20-T22, écrire T24, activer T30-T34 AGI |
| 10 | PRIORITY_ADVISORY | ADVISORY_PRIORITY | Priorisation consultative, classement chantiers | Décision finale, ACT |

---

## Invariants maintenus

```
readonly=true, advisory_only=true, emits_act=false, emits_verdict=false
memory_write=false, graphiti_write=false, neo4j_write=false
kernel_mutation=false, decision_authority=KX108_ONLY
```

---

## Tests

```
tests/api/test_brody_rights_authority_matrix.py — 55 tests PASS
  - get_brody_capability_matrix: sources, catégories, invariants
  - classify_request_authority: 10 catégories, patterns, response_mode
  - decision_authority KX108_ONLY sur tous les messages
  - tree_policy toujours présent
```

---

## Verdict

```
BRODY_RIGHTS_AUTHORITY_MATRIX_PASS
```
