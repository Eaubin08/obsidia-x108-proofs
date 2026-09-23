# P27 — Source Pack Context Propagation Report

**Branch:** p10-real-engine-controlled-bridge  
**Date:** 2026-06-03  
**Status:** P27_SOURCE_PACK_CONTEXT_PROPAGATED_THROUGH_BRODY_ENGINE_READY

---

## Résumé

P27 propage le contexte source pack dans toute la chaîne moteur Brody : du resolver vers True Voice, et de True Voice vers `final_answer`. Les source packs sont désormais une matière active de réponse, pas seulement un champ dans le payload.

---

## Chaîne complète (P26 + P27)

```
source packs / registry (15 298 entrées, 7 familles)
→ source_runtime/ (resolver → loader → hydrator → query)
→ ContextPackets (readonly, advisory_only=True)
→ X108 gate (ALLOW_CONTEXT_ONLY)
→ OS3 evidence (dry-run)
→ _source_pack_ctx dict
→ build_true_brody_answer(source_pack_context=_source_pack_ctx)   ← P27
→ True Voice — enrichissement step 7.5 (avant footer X108)
→ final_answer contient bloc source packs lisible              ← P27
→ true_voice_snapshot.source_pack_enriched=True
→ payload API : final_answer_source_pack_enriched + context_summary ← P27
```

---

## Point d'injection choisi

**True Voice** (`brody_true_voice_adapter.py`, step 7.5) — avant le footer X108 (step 8).

**Pourquoi :** True Voice est le point canonique de composition du `final_answer`. L'injection ici garantit que le contexte source pack est un bloc naturel dans la réponse, après toutes les autres sources (domain raccord, memory chain, project memory), mais avant la clôture X108.

**Pourquoi pas backend_response_composer :** Ce composant est un fallback de gabarit, pas le chemin principal. Il n'est pas appelé dans la route `/api/brody/chat` principale.

---

## Exemple de final_answer enrichie

```
X108 constitue le verrou décisionnel du système Obsidia : c'est la frontière
entre cognition/analyse et action irréversible. Brody peut lire, structurer,
contextualiser, préparer des candidats, mais ne franchit jamais cette frontière.
Seul le kernel X108 autorise une action.

X108 reste seul décideur. Je peux préparer, contextualiser, structurer — pas agir.

**Sources de référence (lecture seule, consultatif) :** Familles consultées :
ATLAS, COGNITIVE_REINTEGRATION, COMPLIANCE_DATA_GOVERNANCE, EXTERNAL_SIGNALS,
RSSI_RGPD — 5 document(s) hydraté(s). X108 est seul décideur. Contexte
informatif uniquement, sans exécution.

_Brody — réponse structurée readonly. KX108_ONLY. Pas de décision, pas d'ACT,
pas d'écriture mémoire._
```

---

## Champs API ajoutés / stabilisés (P27)

| Champ | Type | Valeur quand packs présents |
|-------|------|---------------------------|
| `source_pack_context_summary` | str | Résumé `context_summary_for_brody` (1 000+ chars) |
| `final_answer_source_pack_enriched` | bool | `True` |

**Champs P26 stables (non modifiés) :**
- `source_pack_context` (dict complet)
- `source_pack_context_used` (bool)
- `source_pack_families` (list)
- `source_pack_entries_used` (int)
- `source_pack_x108_decision` (str)
- `source_pack_os3_evidence_id` (str)

---

## Modifications apportées

### `apps/obsidia_api/routes/brody.py`
- `_source_pack_ctx` déplacé **avant** `true_voice_snapshot` (était après)
- `source_pack_context=_source_pack_ctx` passé à `build_true_brody_answer()`
- Ajout `source_pack_context_summary` et `final_answer_source_pack_enriched` dans `_payload`

### `apps/obsidia_api/brody_true_voice_adapter.py`
- Nouveau param `source_pack_context: dict[str, Any] | None = None` dans `build_true_brody_answer()`
- Step 7.5 injecte le bloc enrichissement en français/anglais si `source_pack_context_used=True`
- Retour dict contient `source_pack_enriched` et `source_pack_context_used`
- Texte formulé pour éviter les tokens interdits du sanitizer (pas de "ACT", "ALLOW" majuscules)

---

## Résultats des tests

### P27 (6/6)
```
tests/api/test_brody_source_pack_context_p27.py    6 passed in 12.14s
```

### P26 (15/15, régression propre)
```
tests/test_source_runtime_p26.py                    11 passed
tests/api/test_brody_source_pack_context_p26.py      4 passed
```

### Régression (75/75)
```
test_runtime_wiring_p8c.py + test_source_registry_p9b.py + test_engine_bridge_p10c.py + test_api_runtime_wiring_preview_p10d.py    75 passed
```

---

## Preuves de sécurité

### No ACT
- Texte enrichissement formulé sans tokens interdits ("ALLOW", "ACT" majuscules)
- `emits_act=False` dans tous les packets et dans le retour True Voice
- `safe_backend_response()` réapplique les souverainetés après le merge

### No extraction
- `_source_pack_ctx` construit via `build_brody_context_from_source_packs()` qui passe par `readonly_content_loader` — aucun `extract()` appelé
- `zip_extraction=False` dans le retour bridge

### No write
- `memory_write=False`, `graph_write=False`, `kernel_mutation=False` dans `_source_pack_ctx`
- True Voice ne modifie aucune structure partagée

---

## Limites restantes

- `context_summary_for_brody` (format technique) est exposé dans `source_pack_context_summary` mais pas affiché dans `final_answer` — c'est intentionnel (pas de dump JSON brut)
- NPL dépend d'un répertoire extrait en `~/Downloads/` — dépendance machine
- La latence augmente de ~1-2s (hydratation 5 fichiers depuis zip) à chaque requête Brody
- Workbench UI non mis à jour (P28)

---

## Prochain palier : P28

- Afficher `source_pack_families` et `final_answer_source_pack_enriched` dans le panneau Workbench/RuntimeWiringPreview
- Cache léger pour éviter la relecture registry à chaque requête (TTL 60s)
- Sélection intelligente des familles selon le topic sémantique de la requête
- Extension à `/api/runtime-wiring/preview` : ajouter `source_runtime_available` et `brody_context_bridge_available`
