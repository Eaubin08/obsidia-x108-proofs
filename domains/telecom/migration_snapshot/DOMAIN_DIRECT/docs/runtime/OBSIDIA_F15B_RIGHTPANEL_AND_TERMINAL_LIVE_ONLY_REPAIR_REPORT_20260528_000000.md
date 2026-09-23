# OBSIDIA F15B — RIGHTPANEL + TERMINAL LIVE-ONLY REPAIR FREEZE REPORT

Date: 2026-05-28
Phase: F15B_RIGHTPANEL_AND_TERMINAL_LIVE_ONLY_REPAIR
Status: F15B_PASS — AWAITING COMMIT VALIDATION

---

## BOUNDARY

```
KX108_ONLY                  = true
ADVISORY_ONLY               = true
READONLY                    = true (surfaces read live payload only)
COPY_ONLY                   = true (no execution added)
EXECUTION_ALLOWED_FOR_BRODY = false
BRODY_EXECUTE_ALLOWED       = false
PACKET_EXECUTED             = false
NO_SHELL_CALL               = true
NO_FETCH_CALL               = true
NO_EXEC_CALL                = true
NO_BACKEND_TOUCH            = true (backend Python untouched)
NO_KERNEL_TOUCH             = true
NO_COMMIT                   = true (en attente validation)
```

---

## SCOPE

F15B = réparation live-only globale. Trois surfaces:

1. `apps/obsidia-workbench/src/components/RightPanel.tsx` — phantoms supprimés, mocks labellisés NOT_RUNTIME
2. `apps/obsidia-workbench/src/views/ChatView.tsx` — CLEAN (aucun patch nécessaire, confirmé en audit F15)
3. `tools/brody_chat.py` — BASE_URL corrigé 8012→8000

---

## CHANGES

### Files modified

| File | Change |
|---|---|
| `apps/obsidia-workbench/src/components/RightPanel.tsx` | 11 edits — suppression phantoms + labels NOT_RUNTIME + import nettoyé |
| `tools/brody_chat.py` | 2 lignes — BASE_URL 8012→8000, docstring 8012→8000 |

### Files created

| File | Role |
|---|---|
| `tests/ui/test_rightpanel_no_phantom_fields.py` | 11 tests source-assert F15B (RightPanel phantoms + labels) |
| `tests/cli/test_brody_chat_live_only_output.py` | 10 tests source-assert F15B (CLI live-only) |
| `docs/runtime/OBSIDIA_F15B_RIGHTPANEL_AND_TERMINAL_LIVE_ONLY_REPAIR_REPORT_20260528_000000.md` | Ce rapport |

### Files NOT touched

- `apps/obsidia-workbench/src/views/ChatView.tsx` — confirmé clean à l'audit F15 (aucun mock)
- Backend Python — aucun fichier modifié
- Kernel / X108 / Lean / TLA+ / Merkle / seal / RFC3161 — inchangés

---

## DETAIL DES MODIFICATIONS — RightPanel.tsx

### Edit 1 — Suppression const v18 hardcodée

Supprimé : `const v18: string = 'FAIL'` (ContextTab, était ligne ~335)

**Raison** : v18_hash_status FAIL était une constante hardcodée jamais lue du payload réel.

### Edit 2 — Correction tree_policy safe_trees path

**Avant** :
```tsx
v={String(Array.isArray(treePol.safe_trees) ? (treePol.safe_trees as unknown[]).length : 0)}
```

**Après** :
```tsx
v={String(
  Array.isArray((treePol.tree_policy as Record<string,unknown>)?.safe_trees)
    ? ((treePol.tree_policy as Record<string,unknown>).safe_trees as unknown[]).length
    : Array.isArray(treePol.safe_trees) ? (treePol.safe_trees as unknown[]).length : 0
)}
```

**Raison** : `treePol.safe_trees` = `['TREE_X108_BOUNDARY']` (label, 1 item). Les 13 vrais arbres sont dans `treePol.tree_policy.safe_trees`. Fallback conservé pour compatibilité.

### Edit 3 — Suppression carte Context Packet statique

Supprimé : bloc complet affichant `packet_id: cp_a1b2c3d4`, `query: 'What is the current governance context?'`, `v18_hash_status`, `git_branch: ci-strict-sigma`, et la liste des context_items statiques.

Conservé : section Dominant Trees, retitulée `"Dominant Trees — NOT_RUNTIME / STATIC ({cp.dominant_trees.length})"`.

**Raison** : Ces champs provenaient de MOCK_CONTEXT_PACKET (fixture statique). Un panel live ne doit pas afficher des données de fixture sans label NOT_RUNTIME.

### Edits 4-10 — Labels NOT_RUNTIME sur toutes sections mock

| Section | Label ajouté |
|---|---|
| GovernanceTab — OS3 Proof Ticket | `— NOT_RUNTIME` |
| GovernanceTab — Sovereign Ticket | `— NOT_RUNTIME` |
| GovernanceTab — WorldCall / Gateway | `— NOT_RUNTIME` |
| MemoryTab — Memory Candidates | `— NOT_RUNTIME / STATIC` |
| MemoryTab — Graphiti Status | `— STATIC / NOT_RUNTIME` |
| GencoinTab — Ledger Entries | `— NOT_RUNTIME / SYMBOLIC` |
| AuditTab — Audit Events | `Audit Events — NOT_RUNTIME / STATIC` |

### Edit 11 — Suppression import RefreshCw inutilisé

`RefreshCw` importé depuis lucide-react n'était plus utilisé après suppression de la carte Context Packet. Supprimé pour corriger l'erreur TS6133.

---

## DETAIL DES MODIFICATIONS — tools/brody_chat.py

### BASE_URL

**Avant** : `BASE_URL  = "http://127.0.0.1:8012"`
**Après** : `BASE_URL  = "http://127.0.0.1:8000"`

**Raison** : 8012 = port Graphiti. 8000 = port principal Obsidia stack. L'utilisateur passait `--url http://127.0.0.1:8000` en CLI arg pour overrider, mais le défaut était incorrect. Corrigé à la source.

### Docstring

**Avant** : `Dialogue direct avec le moteur Obsidia via http://127.0.0.1:8012/api/brody/chat`
**Après** : `Dialogue direct avec le moteur Obsidia via http://127.0.0.1:8000/api/brody/chat`

---

## TESTS

### Nouveaux (F15B) — source-assert

```
pytest tests/ui/test_rightpanel_no_phantom_fields.py -v → 11/11 PASS
pytest tests/cli/test_brody_chat_live_only_output.py -v → 10/10 PASS
```

| Test (RightPanel phantoms) | Résultat |
|---|---|
| test_no_hardcoded_v18_hash_status | PASS |
| test_no_hardcoded_git_branch | PASS |
| test_no_static_context_packet_id | PASS |
| test_no_static_context_query | PASS |
| test_tree_policy_uses_nested_path | PASS |
| test_not_runtime_labels_present | PASS |
| test_dominant_trees_labeled_not_runtime | PASS |
| test_governance_sections_labeled_not_runtime | PASS |
| test_memory_candidates_labeled_not_runtime | PASS |
| test_gencoin_ledger_labeled_not_runtime | PASS |
| test_audit_events_labeled_not_runtime | PASS |

| Test (CLI live-only) | Résultat |
|---|---|
| test_base_url_is_8000 | PASS |
| test_base_url_not_8012 | PASS |
| test_docstring_references_8000 | PASS |
| test_no_hardcoded_v18_hash_status | PASS |
| test_no_hardcoded_git_branch | PASS |
| test_no_subprocess_shell_exec | PASS |
| test_url_override_wiring | PASS |
| test_reads_true_voice_snapshot_from_payload | PASS |
| test_reads_domain_raccord_from_payload | PASS |
| test_clipboard_not_used | PASS |

### Régression UI (baseline + F14)

```
pytest tests/ui/ tests/cli/ → 34/34 PASS
```

(était 13/13 avant F15B → +11 RightPanel phantoms + 10 CLI = 34 total)

### API tests

Les tests `tests/api/` incluent des tests live backend (necesitent backend running). Les erreurs 404 sur `/bus/bridge` et `/bus/stats` sont **pre-existantes** — routes non implémentées. F15B ne touche aucun fichier Python backend.

Source-assert tests (non-backend) : tous PASS avant F15B, aucune régression.

---

## BUILD FRONTEND

```
tsc -b    → 0 erreurs TypeScript (après correction import RefreshCw)
vite build → ✓ built in 1.95s
dist/assets/index-z-J_TMGu.js  351.83 kB (gzip: 95.25 kB)
```

---

## GIT DIFF STAT

```
apps/obsidia-workbench/src/components/RightPanel.tsx | ~45 lines changed
tools/brody_chat.py                                   |   2 lines changed
```

## GIT STATUS

```
M  apps/obsidia-workbench/src/components/RightPanel.tsx
 M tools/brody_chat.py
?? docs/runtime/F15_RIGHTPANEL_LIVE_PAYLOAD_8000.json
?? docs/runtime/OBSIDIA_F15_RIGHTPANEL_REAL_PAYLOAD_ALIGNMENT_AUDIT_20260527_235913.md
?? docs/runtime/OBSIDIA_F15B_RIGHTPANEL_AND_TERMINAL_LIVE_ONLY_REPAIR_REPORT_20260528_000000.md
?? tests/cli/
?? tests/ui/test_rightpanel_no_phantom_fields.py
```

## DIFF --CHECK

```
CLEAN — no trailing whitespace, no mixed line endings
```

---

## PROOFS

```
F15B_UI_TESTS_11_11_PASS=true
F15B_CLI_TESTS_10_10_PASS=true
F15B_REGRESSION_34_34_PASS=true
F15B_BUILD_PASS=true
DIFF_CHECK_CLEAN=true
NO_PHANTOM_V18_HASH_STATUS=true
NO_PHANTOM_GIT_BRANCH=true
NO_STATIC_CONTEXT_PACKET_IN_LIVE_VIEW=true
TREE_POLICY_READS_NESTED_PATH=true
ALL_MOCK_SECTIONS_LABELED_NOT_RUNTIME=true
BASE_URL_CORRECTED_8012_TO_8000=true
NO_BACKEND_TOUCHED=true
NO_KERNEL_TOUCHED=true
NO_EXEC=true
NO_SHELL=true
NO_FETCH=true
CHATVIEW_CONFIRMED_CLEAN_NO_PATCH_NEEDED=true
```

---

## COMMIT PROPOSÉ (EN ATTENTE VALIDATION)

```
feat: freeze F15B live-only surface repair — RightPanel phantoms purged, CLI BASE_URL corrected
```

Tag proposé :
```
BRODY_F15B_LIVE_ONLY_REPAIR_20260528
```

Fichiers à stager :
```
apps/obsidia-workbench/src/components/RightPanel.tsx
tools/brody_chat.py
tests/ui/test_rightpanel_no_phantom_fields.py
tests/cli/test_brody_chat_live_only_output.py
docs/runtime/OBSIDIA_F15B_RIGHTPANEL_AND_TERMINAL_LIVE_ONLY_REPAIR_REPORT_20260528_000000.md
docs/runtime/OBSIDIA_F15_RIGHTPANEL_REAL_PAYLOAD_ALIGNMENT_AUDIT_20260527_235913.md
docs/runtime/F15_RIGHTPANEL_LIVE_PAYLOAD_8000.json
```

---

## VALIDATION PHRASE

```
F15B_RIGHTPANEL_AND_TERMINAL_LIVE_ONLY_REPAIR_PASS
PHANTOM_V18_REMOVED=true
PHANTOM_GIT_BRANCH_REMOVED=true
STATIC_CONTEXT_PACKET_REMOVED_FROM_LIVE_VIEW=true
TREE_POLICY_NESTED_PATH_FIXED=true
ALL_MOCK_SECTIONS_LABELED_NOT_RUNTIME=true
BASE_URL_8012_TO_8000=true
CHATVIEW_CLEAN=true
NO_BACKEND_TOUCH=true
NO_KERNEL_TOUCH=true
COPY_ONLY=true
NO_EXEC=true
NO_SHELL=true
NO_FETCH=true
TESTS_34_34_PASS=true
BUILD_PASS=true
DIFF_CHECK_CLEAN=true
KX108_ONLY=true
AWAITING_COMMIT_VALIDATION=true
```
