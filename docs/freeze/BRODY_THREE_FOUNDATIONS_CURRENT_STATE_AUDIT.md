# BRODY THREE FOUNDATIONS — Current State Audit

**Date**: 2026-05-20
**Result**: BRODY_THREE_FOUNDATIONS_CURRENT_STATE_AUDIT_PASS

---

## Résumé exécutif

Les trois fondations Brody existent sous forme d'**adaptateurs** (`_adapter.py`) mais pas encore de **runtimes** (`_runtime.py`). Le `brody_full_runtime_reconnect.py` et `brody_true_voice_adapter.py` existent et importent ces adaptateurs. Le route `/api/brody/chat` ne les appelle pas encore.

---

## État par couche

### Foundation A — PROJECT MEMORY

| Élément | État | Fichier |
|---------|------|---------|
| `brody_project_memory_adapter.py` | **BRANCHÉ** — `build_project_memory_snapshot()` fonctionnel | `apps/obsidia_api/` |
| `brody_project_memory_runtime.py` | **MANQUANT** — à créer (wrapper + champs spec) | — |
| Graphiti readonly index V2 | **DÉCOUVERT** — `_graphiti_readonly_indexes/…/graphiti_readonly_index_v2.json` | local |
| Memory candidate ledger | **DÉCOUVERT** — `_local_audits/memory_candidate_ledger.jsonl` | local |
| Context packet query module | **DÉCOUVERT** — `CURRENT_BRODY_CONTEXT_PACKET_QUERY*.txt` pointer présent | periphery |
| BrodyMemoryDoc live (Neo4j) | **OFFLINE** — `NEO4J_PASSWORD` non défini | — |
| Utilisé par API | **NON** — `routes/brody.py` ne l'appelle pas | — |

### Foundation B — SESSION MEMORY / FOLLOW-UP

| Élément | État | Fichier |
|---------|------|---------|
| `brody_session_memory_adapter.py` | **BRANCHÉ** — `build_session_memory_snapshot()` fonctionnel | `apps/obsidia_api/` |
| `brody_session_memory_runtime.py` | **MANQUANT** — à créer (+ `remember_session_turn`, `resolve_session_followup`) | — |
| Session memory ledger V2 | **DÉCOUVERT** — `brody_session_memory_ledger_readonly_v2.py` dans periphery | periphery |
| Presave buffer | **DÉCOUVERT** — `CURRENT_BRODY_SESSION_PRESAVE_BUFFER_READONLY.txt` trouvé | local |
| Follow-up resolver | **PARTIAL** — session_ledger_found mais pas de ledger actif pour session `local` | — |
| Utilisé par API | **NON** — `routes/brody.py` ne l'appelle pas | — |

### Foundation C — TRUE RESPONSE STRUCTURE / TRUE VOICE

| Élément | État | Fichier |
|---------|------|---------|
| `brody_true_response_structure_adapter.py` | **BRANCHÉ** — `build_true_response_structure_snapshot()` fonctionnel | `apps/obsidia_api/` |
| `brody_true_response_structure_runtime.py` | **MANQUANT** — à créer (wrapper + champs spec) | — |
| `terminal_structural_dialogue_readonly_v1.py` | **DÉCOUVERT** — importable, `run_once`, `build_response`, `:who`, `:boundary` présents | periphery |
| `local_response_engine_readonly_v1.py` | **DÉCOUVERT** — importable, `build_response`, `extract_packet`, `validate_boundary` | periphery |
| V1.4.12A freeze pointer | **DÉCOUVERT** — `CURRENT_BRODY_RUNTIME_FREEZE_V1_4_12A_READONLY.txt` | local |
| Creator context pattern | **NOT_FOUND_IN_EXISTING_SOURCES** — aucun fichier ne référence "Étienne" par nom | — |
| Utilisé par API | **NON** — `routes/brody.py` ne l'appelle pas | — |

---

## Couches supérieures

### `brody_full_runtime_reconnect.py`

| État | Détail |
|------|--------|
| **EXISTS** | Complet, fonctionnel |
| Imports actuels | `brody_project_memory_adapter`, `brody_session_memory_adapter`, `brody_true_response_structure_adapter` |
| À mettre à jour | Imports → `_runtime.py` files ; `source_mode` → `THREE_FOUNDATIONS_RECONNECTED` |
| Appelé par API | **NON** |

### `brody_true_voice_adapter.py`

| État | Détail |
|------|--------|
| **EXISTS** | Complet, `build_true_brody_answer()` fonctionnel |
| Sources utilisées | `brody_full_context`, `freeze_metrics`, `rights_authority_matrix` |
| Chat vs panel | Implémenté — réponse fluide, pas de dump métrique |
| Appelé par API | **NON** |

### `routes/brody.py` (état actuel)

**Appels actuels :**
- `run_brody_real_response_pipeline` ✓
- `make_structured_response_snapshot` ✓
- `build_freeze_metrics_snapshot` ✓
- `run_brody_v1_4_12a_final_answer` ✓
- `run_brody_automation_layer` ✓

**Appels MANQUANTS (Phase 7) :**
- `build_brody_full_context()` — non appelé
- `build_true_brody_answer()` — non appelé
- Payload : `project_memory_snapshot`, `session_memory_snapshot`, `true_response_structure_snapshot`, `brody_full_context`, `true_voice_snapshot` — absents

---

## Modules periphery disponibles

| Module | Fichier principal | Importable |
|--------|------------------|-----------|
| `terminal_structural_dialogue_readonly` | `brody_terminal_structural_dialogue_readonly_v1.py` | OUI |
| `local_response_engine_readonly` | `brody_local_response_engine_readonly_v1.py` | OUI |
| `context_packet_query_readonly` | `brody_context_packet_query_readonly_v1.py` | OUI (requiert Neo4j) |
| `context_packet_consumer_readonly` | `brody_context_packet_consumer_readonly_v1.py` | OUI |
| `session_memory_ledger_readonly` | `brody_session_memory_ledger_readonly_v2.py` | OUI |
| `auto_triage_memory_intake_readonly` | présent | OUI |

---

## Ce qui est mock / placeholder

- `used_by_api_now: False` dans tous les adaptateurs — hardcodé, non mis à jour dynamiquement.
- `creator_context_pattern_found: False` — aucune source Étienne, détection keyword seulement via `brody_full_runtime_reconnect`.
- `mmonde_or_34trees: False` — non implémenté dans aucune source.

---

## Ce qui est freeze-sourced

- `brody_freeze_metrics_snapshot.py` — entièrement sourced depuis `CURRENT_BRODY_*.txt` pointers.
- `brody_true_response_structure_adapter.py` — lit les modules periphery en dry-run (`:who`, fonction checks).

---

## Ce qui est runtime actif

- `brody_real_response_pipeline.py` — appelle `local_response_engine` quand Neo4j est live, sinon `terminal.build_response` (offline path).
- `brody_session_memory_adapter.py` — lit `SESSION_LEDGER.jsonl` si présent.

---

## Ce qui manque pour Brody LLM obsidien

1. `brody_project_memory_runtime.py` — avec champs `foundation`, `status=FOUNDATION_A_READY/PARTIAL`
2. `brody_session_memory_runtime.py` — avec `remember_session_turn`, `resolve_session_followup`
3. `brody_true_response_structure_runtime.py` — avec champs `foundation`, `status=FOUNDATION_C_READY/PARTIAL`
4. Mise à jour `brody_full_runtime_reconnect.py` imports → `_runtime.py`
5. Wiring `/api/brody/chat` → `build_brody_full_context` + `build_true_brody_answer`
6. Payload API étendu : `project_memory_snapshot`, `session_memory_snapshot`, `true_response_structure_snapshot`, `brody_full_context`, `true_voice_snapshot`

---

**BRODY_THREE_FOUNDATIONS_CURRENT_STATE_AUDIT_PASS**
