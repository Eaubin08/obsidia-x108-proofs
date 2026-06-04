# P50 — Controlled Activation Readiness Plan

**Date :** 2026-06-04
**Branche :** p43-unconnected-runtime-surface-audit
**Statut :** `P50_CONTROLLED_ACTIVATION_READINESS_READY`
**Basé sur :** P49 Global Runtime Surface 100% Gate

---

## Rappel P49 — Surface 100% validée

| Catégorie       | Classifiés | Total | Couverture |
|-----------------|-----------|-------|-----------|
| Familles source | 8         | 8     | 100.0 %   |
| Routes API      | 147       | 147   | 100.0 %   |
| Vues Workbench  | 13        | 13    | 100.0 %   |
| Modules Python  | 121       | 121   | 100.0 %   |
| Fonctions Python| 548       | 548   | 100.0 %   |
| Adapters        | 10        | 10    | 100.0 %   |
| **TOTAL**       | **847**   | **847** | **100.0 %** |

`unclassified_total = 0` — `activation_allowed = false` — `KX108_ONLY`

---

## Niveaux d'activation

### LEVEL 0 — LOCKED (7 items)

Ne jamais activer. Aucun palier ne peut débloquer sans révision KX108 complète.

| Item | Catégorie | Raison |
|------|-----------|--------|
| Unknown external tools | EXTERNAL | Pas de frontière KX108 |
| Unsafe mutation | FILE_SYSTEM | Contourne freeze-guardian |
| Unverified local source packs | SOURCE_PACKS | Non validés P42A |
| Secrets / env file access | SECRETS | Verrouillage permanent |
| Kernel mutation | KERNEL | Fichiers crypto-ancrés |
| Action gateway open (runtime_allowed_now=True) | GATEWAY | Nécessite P51+ |
| activation_allowed toggle (→ True) | GATEWAY | Nécessite P51+ |

---

### LEVEL 1 — READONLY ACTIVE CANDIDATE (13 items)

Peut être activé en lecture réelle. Aucun ACT. Aucun write.

| Item | Catégorie | Mode |
|------|-----------|------|
| Brody context (READONLY_CONTEXT) | BRODY | READONLY_CONTEXT |
| OS Map (status + query) | OS_MAP | READONLY_CONTEXT |
| Source runtime preview | SOURCE_RUNTIME | READONLY_CONTEXT |
| ATLAS context packet | ATLAS | READONLY_CONTEXT |
| OS_TRAD reverse / interlanguage | OS_TRAD | READONLY_CONTEXT |
| Graphiti readonly client | GRAPHITI | READONLY_CONTEXT |
| Workbench views (13 vues) | WORKBENCH | READONLY_CONTEXT |
| Route status / readiness / metrics | ROUTES | READONLY_CONTEXT |
| Memory read (SCRATCH, FOCUS, RISKS) | MEMORY | READONLY_CONTEXT |
| Cognitive context packet | COGNITIVE | READONLY_CONTEXT |
| NPL context packet | NPL | READONLY_CONTEXT |
| Compliance / RSSI context packets | RSSI_COMPLIANCE | READONLY_CONTEXT |
| Capability path router (P36/P37) | CAPABILITY_ROUTER | READONLY_CONTEXT |

> **Invariant :** `any_real_action_in_level_1 = false`

---

### LEVEL 2 — DRY_RUN ACTIVE CANDIDATE (6 items)

Peut simuler sans effet réel. Aucune émission externe réelle.

| Item | Catégorie | Note |
|------|-----------|------|
| World action bus (dry-run) | WORLD_ACTION_BUS | No real emission |
| External signals advisory (Timeverse) | EXTERNAL_SIGNALS | No live API call |
| Simulation / preview routes | ROUTES | Dry path eval |
| Gencoin (dry-run) | GENCOIN | No token emission |
| Blockchain (dry-run, no real TX) | BLOCKCHAIN | Read-only chain state |
| OS3 evidence expansion (dry preview) | OS3 | No file write |

---

### LEVEL 3 — HOLD_GATE_CANDIDATE (5 items)

Peut être soumis à évaluation HOLD/BLOCK/ALLOW. Aucun ACT.

| Item | Catégorie |
|------|-----------|
| X108 gate evaluation | X108_GATE |
| OS3 evidence expansion (HOLD candidate) | OS3 |
| Decision tickets (classification only) | DECISION |
| HOLD/BLOCK/ALLOW simulation | X108_GATE |
| Brody authority escalation (evaluate only) | BRODY |

---

### LEVEL 4 — FUTURE ACTION GATE (8 items)

Action réelle. Nécessite palier dédié et validation KX108.

| Item | Catégorie | Palier requis |
|------|-----------|--------------|
| Memory write | MEMORY | P51+ |
| Graphiti write | GRAPHITI | P51+ |
| Real external API action | EXTERNAL_API | P52+ |
| Real blockchain transaction | BLOCKCHAIN | P53+ |
| Real wallet / Gencoin | GENCOIN | P53+ |
| File mutation | FILE_SYSTEM | Approval explicite |
| Email / notification sending | EXTERNAL_COMMS | P52+ |
| Irreversible workflow (deploy, migration) | WORKFLOW | P54+ |

---

## Brody Activation Readiness

**Mode autorisé :** `READONLY_CONTEXT`
**Niveau :** `LEVEL_1_READONLY_ACTIVE_CANDIDATE`

| Instance | Statut |
|----------|--------|
| `/api/brody/chat` | LEVEL_1 READONLY |
| `brody_source_context_bridge` | LEVEL_1 READONLY |
| `true_voice / final_answer` | LEVEL_1 READONLY |
| Source runtime context injection | LEVEL_1 READONLY |
| OS Map path explanation | LEVEL_1 READONLY |

**Invariants Brody :**
- `can_execute_actions = false`
- `can_write_memory = false`
- `can_mutate_graph = false`
- `can_explain_runtime_path = true`
- `emits_act = false`
- `decision_authority = KX108_ONLY`

---

## Graphiti / Memory Readiness

| Ressource | Niveau | Write | Palier write |
|-----------|--------|-------|--------------|
| Graphiti readonly | LEVEL_1 | non | — |
| Graphiti write | LEVEL_4 | non | P51+ |
| Memory read | LEVEL_1 | non | — |
| Memory write | LEVEL_4 | non | P51+ |

---

## World Action Bus Readiness

| Mode | Niveau | Effet réel | Statut |
|------|--------|-----------|--------|
| Dry-run | LEVEL_2 | non | Candidat simulé |
| Real action | LEVEL_4 | oui | Bloqué P52+ |
| Action request | — | — | `ACTION_REQUEST_BLOCKED` |

> Toute action request nécessite évaluation X108 avant tout.

---

## Pourquoi `activation_allowed` reste `false`

1. **P51 non validé** — Le palier Brody READONLY_CONTROLLED_ACTIVATION n'a pas encore été exécuté.
2. **Graphiti write non audité** — Le chemin d'écriture graph n'a pas de plan de rollback documenté.
3. **Irreversibilité non maîtrisée** — Les items LEVEL_4 n'ont pas de procédure de rollback approuvée.
4. **KX108 gate non togglé** — Aucun code path ne peut setter `activation_allowed=True` sans palier dédié.

---

## Ce qui peut être activé au prochain palier (P51)

- Brody chat en mode `READONLY_CONTEXT` — injection contexte runtime sans ACT
- Graphiti readonly client — lecture graph pour enrichir réponses Brody
- Memory read — chargement SCRATCH/FOCUS dans contexte Brody
- OS Map query enrichie — réponse complète avec path routing et inventory

---

## Ce qui reste bloqué

- Toute écriture (memory, graph, fichiers)
- Tout ACT (actions externes, blockchain, email)
- Tout toggle `activation_allowed=True` ou `runtime_allowed_now=True`
- Tous les items LEVEL_0 et LEVEL_4

---

## Prochain palier : P51

`P51_BRODY_READONLY_CONTROLLED_ACTIVATION`

P51 activera Brody en mode `READONLY_CONTEXT` strictement contrôlé :
- Injection context runtime → Brody chat
- OS Map path explanation → Brody réponses
- Aucun ACT, aucun write, aucune mutation

---

*NO ACT — NO WRITE — NO GRAPHITI WRITE — NO KERNEL MUTATION — KX108_ONLY*
*activation_allowed = false — runtime_allowed_now = false*
