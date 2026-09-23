# P51 — Brody Readonly Controlled Activation

**Date :** 2026-06-04
**Branche :** p43-unconnected-runtime-surface-audit
**Statut :** `P51_BRODY_READONLY_CONTROLLED_ACTIVATION_READY`
**Basé sur :** P50 Controlled Activation Readiness Matrix

---

## État P49/P50

| Palier | Statut |
|--------|--------|
| P49 Global Runtime Surface 100% | FULL_COVERAGE — 847/847 items, UNCLASSIFIED=0 |
| P50 Controlled Activation Matrix | READY — 5 niveaux définis |
| P51 Brody Readonly Activation | **ACTIVE_READONLY** — LEVEL_1 |

---

## Ce qui est activé (LEVEL_1 READONLY_CONTEXT)

| Capacité | Statut |
|----------|--------|
| Brody peut répondre (`brody_can_answer`) | ✓ true |
| Brody peut expliquer le runtime path | ✓ true |
| Brody peut utiliser le source context | ✓ true |
| Brody peut utiliser l'OS Map | ✓ true |
| Brody peut expliquer capability/modules/routes/adapters | ✓ true |
| `brody_readonly_enabled` | ✓ true |
| `activation_level` | `LEVEL_1_READONLY_ACTIVE` |

---

## Ce qui reste bloqué

| Capacité bloquée | Valeur |
|-----------------|--------|
| `brody_can_execute_actions` | false |
| `brody_can_write_memory` | false |
| `brody_can_write_graphiti` | false |
| `runtime_allowed_now` | false |
| `activation_allowed_now` (global) | false |
| `emits_act` | false |
| Modes bloqués | ACTION, MEMORY_WRITE, GRAPHITI_WRITE, WORLD_ACTION, BLOCKCHAIN_ACTION, EMAIL_SEND, KERNEL_MUTATION |

---

## Exemple : query « IR alphabet reverse OS »

```
Query: "IR alphabet reverse OS interlanguage"
→ brody_readonly_enabled: True
→ action_request_blocked: False
→ action_status: NO_ACTION_IN_QUERY
→ os_map_summary_status: CAPABILITY_ROUTER_RESOLVED
→ emits_act: False
→ decision_authority: KX108_ONLY
```

Brody reçoit :
- `selected_runtime_path` → chemin capability router
- `selected_modules` → modules runtime OS_TRAD_REVERSE
- `selected_routes` → routes /api/runtime-wiring/...
- `selected_adapters` → reverse_os_interlanguage_to_context_packet
- `selected_source_families` → [OS_TRAD_REVERSE]
- `selected_evidence_packs` → packs OS3 disponibles
- `hydration_plan` → plan sans extraction zip
- `x108_decision` → ALLOW_CONTEXT_ONLY

---

## Exemple : query « brody chat true voice »

```
Query: "brody chat true voice"
→ brody_readonly_enabled: True
→ action_request_blocked: False
→ action_status: NO_ACTION_IN_QUERY
→ os_map_summary_status: CAPABILITY_ROUTER_RESOLVED
→ emits_act: False
→ decision_authority: KX108_ONLY
```

Brody répond via `final_answer` enrichi avec :
- capability path router P36
- inventory linker P37
- source context P27
- X108 boundary
- aucune mutation

---

## Exemple : query action bloquée « envoie un mail »

```
Query: "envoie un mail maintenant"
→ brody_readonly_enabled: True
→ action_requested: True
→ action_request_blocked: True
→ action_status: ACTION_REQUEST_BLOCKED
→ emits_act: False
→ decision_authority: KX108_ONLY
```

Brody détecte le mot-clé d'action (`envoie`), retourne `ACTION_REQUEST_BLOCKED`.
Aucune action n'est émise. Aucun mail envoyé.

---

## Final Answer enrichissement

`/api/brody/chat` retourne désormais dans le payload :

```json
{
  "brody_readonly_activation_status": "ACTIVE_READONLY",
  "brody_activation_level": "LEVEL_1_READONLY_ACTIVE",
  "brody_readonly_enabled": true,
  "brody_can_answer": true,
  "brody_can_explain_runtime_path": true,
  "brody_can_execute_actions": false,
  "brody_can_write_memory": false,
  "brody_can_write_graphiti": false,
  "os_map_summary": { "os_map_summary_status": "CAPABILITY_ROUTER_RESOLVED", ... },
  "selected_runtime_path": { ... },
  "selected_modules": [...],
  "selected_routes": [...],
  "selected_adapters": [...],
  "selected_source_families": [...],
  "hydration_plan": { ... },
  "brody_no_act": true,
  "brody_no_write": true,
  "brody_kx108_only": true
}
```

---

## Preuve no ACT

- `emits_act = false` — invariant dur dans `_BRODY_READONLY_BOUNDARY`
- `memory_write = false` — jamais modifié
- `graph_write = false` — jamais modifié
- `kernel_mutation = false` — jamais modifié
- `world_action = false` — jamais modifié
- `action_request_blocked = true` pour toute query contenant un mot-clé d'action

---

## Preuve no write

Aucun fichier écrit par le runtime Brody P51 :
- Source context = lecture seule (`readonly_content_loader`)
- Hydration plan = plan seulement, pas d'extraction
- OS Map query = readonly endpoint
- `graph_write = false`, `memory_write = false`

---

## Preuve KX108_ONLY

- `decision_authority = "KX108_ONLY"` dans toutes les réponses
- `x108_decision = "ALLOW_CONTEXT_ONLY"` — seule décision autorisée
- Route X108 gate → BLOCK si `critical_action_requested=True` (jamais passé)

---

## Prochain palier : P52

`P52_GRAPHITI_READONLY_CONTROLLED_ACTIVATION`

P52 activera le client Graphiti en mode lecture seule pour enrichir
les réponses Brody avec le graphe de contexte, sans écriture.

---

*NO ACT — NO WRITE — NO GRAPHITI WRITE — NO KERNEL MUTATION — KX108_ONLY*
*brody_readonly_enabled = true — activation_allowed_now = false — runtime_allowed_now = false*
