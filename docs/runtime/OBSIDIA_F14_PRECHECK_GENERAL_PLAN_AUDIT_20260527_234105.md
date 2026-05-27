# OBSIDIA F14 — PRECHECK GENERAL PLAN AUDIT

Date: 2026-05-27 23:41
Phase: F14_PRECHECK_READ_ONLY_AUDIT
Status: READ_ONLY / NO_PATCH / AWAITING_USER_VALIDATION

---

## A. ÉTAT GIT

```
Branch: main...origin/main (clean — no divergence)
Last commit: 0df56f0  test: freeze Brody live UI chat smoke F13
Stash: EMPTY
diff --check: CLEAN
```

### Tags présents

```
BRODY_F10_EXISTING_COMMAND_PACKET_RECONNECT_FREEZE_20260527
BRODY_F11_LIVE_RUNTIME_TREE_SIGNAL_ORDER_FREEZE_20260527
BRODY_F12_DOMAIN_RACCORD_PRIORITY_TERMINAL_FREEZE_20260527
BRODY_F13_LIVE_UI_CHAT_SMOKE_FREEZE_20260527
```

### Commits F2A→F13 (séquence complète)

| Commit | Phase | Description |
|---|---|---|
| 0ec73cd | F2A-F4 | freeze Brody transverse value stack (+5992 lignes) |
| 74660af | F5 | freeze Brody tree signal runtime |
| 2cf533d | F6 | freeze Brody memory promotion guard |
| 6da0691 | F7 | freeze Brody operator view packet |
| 0b7678f | F8 | freeze RightPanel transverse operator view |
| 5c07997 | F9 | freeze Brody terminal chat view |
| e6212a8 | F10 | freeze Brody existing command packet reconnect |
| b3181ca | F11 | fix live runtime tree signal order |
| c01e97b | F12 | fix domain raccord priority + terminal visibility |
| 0df56f0 | F13 | freeze Brody live UI chat smoke |

---

## B. FICHIERS CLÉS — ÉTAT

| Fichier | Lignes | Statut |
|---|---|---|
| `apps/obsidia-workbench/src/views/ChatView.tsx` | 264 | OK — BRODY_TERMINAL_VIEW_V1 branché |
| `apps/obsidia-workbench/src/api/obsidiaClient.ts` | 335 | OK |
| `apps/obsidia_api/routes/brody.py` | 448 | OK — pipeline 6 steps + automation_snapshot |
| `apps/obsidia_api/brody_automation_orchestrator.py` | 491 | OK — command packet complet |
| `apps/obsidia_api/brody_domain_raccord_adapter.py` | 374 | OK — priority fix F12 |

---

## C. COMMAND PACKET — ÉTAT ACTUEL

### Backend (brody_automation_orchestrator.py) — PRÉSENT ET COMPLET

Champs exposés dans `operator_loop`:

```
human_command_packet_ready      : bool
command_gate_classification     : str
execution_allowed_for_brody     : false (HARDCODED)
brody_execute_allowed           : false (HARDCODED)
copy_only                       : true (quand packet ready)
present_packet_to_operator      : bool
packet_status                   : str
command_copy_block.command      : str (la commande à copier)
human_command_packet.packet_kind: str
human_command_packet.executed   : false (HARDCODED)
```

**Invariant confirmé** : `execution_allowed_for_brody=False` et `brody_execute_allowed=False` sont hardcodés — pas de risque d'exécution.

### UI ChatView.tsx — CE QUI EXISTE

Le bloc `BrodyTerminalView` lit et affiche les champs suivants en texte monospace dans la section `HUMAN_COMMAND_PACKET_READONLY` :

```
copy_command=${commandCopy?.command ?? "-"}
packet_kind=${humanPacket?.packet_kind ?? "-"}
packet_executed=${humanPacket?.executed ?? false}
```

**CE QUI MANQUE — GAP F14**:

La commande `copy_command` est affichée en texte dans le terminal mono.
Il n'existe **pas** de bouton "COPY COMMAND" interactif qui permet à l'opérateur de copier `commandCopy.command` dans le clipboard d'un seul clic.

Le seul bouton copy existant (`line 109`) copie `msg.content` (réponse Brody entière) — pas la commande spécifique du packet.

---

## D. UI — INVENTAIRE DES BOUTONS COPY EXISTANTS

| Bouton | Localisation | Action | Scope |
|---|---|---|---|
| `handleCopy` (Copy icon) | `MessageBubble` header | `navigator.clipboard.writeText(msg.content)` | Réponse Brody entière |
| Aucun | `BrodyTerminalView` command block | — | **MANQUE** |

---

## E. TESTS EXISTANTS — BASELINE

**16/16 PASS**

| Fichier | Tests | Statut |
|---|---|---|
| `tests/ui/test_chatview_brody_terminal_view.py` | 2 | PASS |
| `tests/ui/test_chatview_human_command_packet_display.py` | 2 | PASS |
| `tests/ui/test_rightpanel_operator_view_packet.py` | 2 | PASS |
| `tests/api/test_brody_f10c_existing_command_packet_reconnect.py` | 4 | PASS |
| `tests/api/test_brody_f11c_tree_signal_runtime_order.py` | 2 | PASS |
| `tests/api/test_brody_f12c_domain_raccord_priority.py` | 4 | PASS |

**Aucun test existant ne vérifie l'existence d'un bouton COPY COMMAND.**

---

## F. ÉTAT PARTIEL — PLAN GLOBAL F14→F20

### 1. OS Trad / IR / Reverse OS
- **Présent dans l'UI** : bloc `TracePanel` dans ChatView (ligne 16-41) — affiche `os_trad_status`, `ir.intent_type`, `risk_flags`, `contradictions`
- **Route** : pipeline `runOSTradPipeline` + `translation_trace` dans backendPayload
- **Statut** : PARTIEL — affiché UI mais non audité comme pipeline live complet backend
- **Verdict** : NON AUDITÉ LIVE — F17 requis avant conclusion

### 2. Thermodynamics / Coherence / Time
- **Branché** : `brody_thermodynamics_signal.py` → route step 4 → `thermodynamics_packet` dans payload
- **Runtime** : affiche `hard_risks=["THERMO_HOT"]`, `value_layer_scores_null=true`
- **Statut** : BRANCHÉ / WARNING — scoring non finalisé
- **Verdict** : SIGNAL OK, SCORING NULL — F18 requis

### 3. Gencoin / Shadow Value / Economy
- **Branché** : F4 shadow value + F2A transverse interface
- **Runtime** : shadow scores non-nuls si préconditions OK, `economic_projection=null`
- **Statut** : BRANCHÉ PARTIEL — économie non finalisée
- **Verdict** : F19 requis après F18

### 4. Memory / Graphiti
- **8000** : `GRAPHITI_LIVE_BLOCKED`, mémoire locale 3267 records fallback OK
- **8012** : `GRAPHITI_LIVE_READONLY_PASS` (port séparé)
- **Décision architecture** : fusion/proxy/séparation officielle non encore prise
- **Verdict** : F16 requis — BLOQUER tout patch mémoire avant

### 5. Command Operator UX — **F14**
- **Packet existant** : `command_copy_block.command` est lu et affiché en texte
- **Manque** : bouton interactif COPY COMMAND dans `BrodyTerminalView`
- **Scope** : UI-only, `copy_only=true`, `brody_execute_allowed=false` maintenu
- **Verdict** : GO — petit, propre, sans risque kernel

### 6. Runtime Freeze Dashboard
- **Statut** : NON FAIT — F20

---

## G. ANALYSE DU GAP F14

### Ce qui existe déjà (ne pas recréer)

```
backend:   operator_loop.command_copy_block.command  ← commande à copier
backend:   operator_loop.copy_only = true             ← déjà forcé
backend:   brody_execute_allowed = false              ← déjà hardcodé
UI:        commandCopy lu ligne 53 ChatView.tsx       ← déjà parsé
UI:        copy_command affiché dans terminal text    ← déjà visible
```

### Ce qui manque (scope exact F14)

```
UI: bouton <button> dans BrodyTerminalView quand commandCopy?.command est non-null et !== "-"
    → onClick: navigator.clipboard.writeText(commandCopy.command)
    → label: "COPY CMD" ou icône Copy
    → feedback visuel: Check icon 1.5s (comme handleCopy existant)
    → NO shell exec, NO fetch, NO state mutation
```

### Fichiers candidats F14

| Fichier | Changement |
|---|---|
| `apps/obsidia-workbench/src/views/ChatView.tsx` | Ajouter bouton copy dans `BrodyTerminalView` quand `commandCopy?.command` présent |

### Tests candidats F14

| Fichier | Tests |
|---|---|
| `tests/ui/test_chatview_copy_command_button.py` (NEW) | 3-5 tests source-assert |

Tests à écrire :
1. `test_copy_command_button_present_in_terminal_view` — assert `navigator.clipboard.writeText` dans `BrodyTerminalView` context
2. `test_copy_command_only_when_command_present` — assert condition `commandCopy?.command`
3. `test_copy_command_no_exec_boundary` — assert pas de `fetch`, `exec`, `shell` dans le handler copy command
4. `test_copy_command_feedback_visual` — assert `Check` icon ou state toggle présent
5. `test_existing_copy_response_not_broken` — assert `handleCopy` / `msg.content` inchangé

### Régression à vérifier

- `tests/ui/test_chatview_human_command_packet_display.py` — 2 tests (doivent rester PASS)
- `tests/ui/test_chatview_brody_terminal_view.py` — 2 tests (doivent rester PASS)
- `tests/ui/test_rightpanel_operator_view_packet.py` — 2 tests (doivent rester PASS)

---

## H. RISQUES

| Risque | Niveau | Mitigation |
|---|---|---|
| Exécution accidentelle de commande shell | NIL | `copy_only=true` hardcodé backend, pas de fetch/exec dans handler |
| Casser l'affichage texte existant du terminal | LOW | Bouton conditionnel — n'apparaît que si `command` présent et non `-` |
| Régression `handleCopy` (réponse entière) | LOW | Handler séparé, pas de conflit |
| `navigator.clipboard` non disponible hors HTTPS | LOW | Même pattern que `handleCopy` existant — acceptable |

---

## I. RECOMMANDATION

```
GO F14_COMMAND_COPY_BUTTON_UI

Scope confirmé:
  FILES MODIFIED: apps/obsidia-workbench/src/views/ChatView.tsx (1 seul fichier)
  FILES CREATED:  tests/ui/test_chatview_copy_command_button.py
                  docs/runtime/OBSIDIA_F14_COMMAND_COPY_BUTTON_UI_REPORT.md

Boundary:
  copy_only=true (hérité du backend — pas à toucher)
  brody_execute_allowed=false (hardcodé backend — pas à toucher)
  navigator.clipboard.writeText(commandCopy.command) UNIQUEMENT
  PAS de fetch
  PAS d'exec
  PAS de shell
  PAS de mutation kernel / X108

Précondition:
  commandCopy?.command && commandCopy.command !== "-"
  → si faux: bouton absent (pas affiché)

Taille estimée:
  ~15-25 lignes ajoutées dans BrodyTerminalView
  ~50-80 lignes de tests source-assert

Régression attendue: 0 nouvelle failure
Tests baseline: 16/16 PASS avant patch
```

---

## VALIDATION PHRASE

```
F14_PRECHECK_READ_ONLY_AUDIT_PASS
GIT_CLEAN=true
DIFF_CHECK_CLEAN=true
STASH_EMPTY=true
BASELINE_TESTS_16_16_PASS=true
COMMAND_PACKET_PRESENT_BACKEND=true
COMMAND_COPY_BLOCK_READ_UI=true
COPY_BUTTON_MISSING=true
SCOPE_F14_CONFIRMED=UI_ONLY_CHATVIEW_TSX
KERNEL_UNTOUCHED=true
NO_ACT=true
NO_WRITE=true
KX108_ONLY=true
RECOMMENDATION=GO_F14
```

---

STOP — AWAITING USER VALIDATION BEFORE ANY PATCH
