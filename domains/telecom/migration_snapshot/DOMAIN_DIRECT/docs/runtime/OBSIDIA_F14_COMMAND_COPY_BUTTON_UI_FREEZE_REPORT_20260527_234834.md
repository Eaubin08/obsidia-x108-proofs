# OBSIDIA F14 — COMMAND COPY BUTTON UI FREEZE REPORT

Date: 2026-05-27 23:48
Phase: F14_COMMAND_COPY_BUTTON_UI
Status: F14_COMMAND_COPY_BUTTON_UI_PASS

---

## BOUNDARY

```
KX108_ONLY                  = true
ADVISORY_ONLY               = true
READONLY                    = true
COPY_ONLY                   = true
EXECUTION_ALLOWED_FOR_BRODY = false
BRODY_EXECUTE_ALLOWED       = false
PACKET_EXECUTED             = false
NO_SHELL_CALL               = true
NO_FETCH_CALL               = true
NO_EXEC_CALL                = true
NO_BACKEND_TOUCH            = true
NO_KERNEL_TOUCH             = true
NO_COMMIT                   = true (en attente validation)
```

---

## CHANGES

### Files modified

| File | Change |
|---|---|
| `apps/obsidia-workbench/src/views/ChatView.tsx` | +24 lignes — bouton COPY CMD dans BrodyTerminalView |

### Files created

| File | Role |
|---|---|
| `tests/ui/test_chatview_copy_command_button.py` | 7 tests source-assert F14 |
| `docs/runtime/OBSIDIA_F14_PRECHECK_GENERAL_PLAN_AUDIT_20260527_234105.md` | Audit READ_ONLY pré-F14 |
| `docs/runtime/OBSIDIA_F14_COMMAND_COPY_BUTTON_UI_FREEZE_REPORT_20260527_234834.md` | Ce rapport |

### Files NOT touched

- Backend : aucun fichier Python modifié
- brody_automation_orchestrator.py — inchangé
- brody_domain_raccord_adapter.py — inchangé
- routes/brody.py — inchangé
- Kernel / X108 / Lean / TLA+ / Merkle / seal / RFC3161 — inchangés

---

## WHAT CHANGED IN ChatView.tsx

### Added: `useState` hook for copy feedback

```tsx
const [cmdCopied, setCmdCopied] = useState(false)
```

Placé en premier dans `BrodyTerminalView` — avant le early return `if (!op) return null`.
Respecte les règles React hooks (appel inconditionnel).

### Added: derived values

```tsx
const copyableCommand = commandCopy?.["command"] as string | undefined
const hasCopyableCommand = Boolean(copyableCommand && copyableCommand !== "-")
```

`commandCopy` existait déjà (ligne 53 avant patch) — réutilisé, pas recréé.

### Added: handler (clipboard only — no exec)

```tsx
const handleCopyCommand = async () => {
  if (!copyableCommand || copyableCommand === "-") return
  await navigator.clipboard.writeText(copyableCommand)
  setCmdCopied(true)
  setTimeout(() => setCmdCopied(false), 1500)
}
```

Identique au pattern `handleCopy` existant (réponse entière). Zéro `fetch`, `exec`, `shell`, `spawn`.

### Added: conditional button in JSX

```tsx
{hasCopyableCommand && (
  <div className="mt-1.5 pt-1.5 border-t border-obs-proof/10 flex items-center gap-2">
    <span className="text-[8px] font-mono text-obs-dtext">
      copy_only=true · execution_allowed_for_brody=false · packet_executed=false
    </span>
    <button
      onClick={handleCopyCommand}
      className="ml-auto flex items-center gap-1 px-2 py-0.5 rounded text-[8px] font-mono
                 bg-obs-proof/10 border border-obs-proof/20 text-obs-proof
                 hover:bg-obs-proof/20 transition-colors"
      title="Copy command to clipboard — no execution"
    >
      {cmdCopied ? <Check size={8} className="text-obs-pass" /> : <Copy size={8} />}
      {cmdCopied ? 'COPIED' : 'COPY CMD'}
    </button>
  </div>
)}
```

- N'apparaît que si `commandCopy.command` est non-null et non `"-"`.
- Labels de boundary affichés à côté du bouton (visibles en permanence).
- Feedback visuel : `Check` + `COPIED` pendant 1.5s.

---

## TESTS

### Nouveaux (F14)

```
pytest tests/ui/test_chatview_copy_command_button.py -v → 7/7 PASS
```

| Test | Résultat |
|---|---|
| test_copy_command_button_present_in_brody_terminal_view | PASS |
| test_copy_command_only_when_command_present | PASS |
| test_copy_command_clipboard_writetext_only | PASS |
| test_copy_command_no_exec_no_fetch_no_shell | PASS |
| test_copy_command_boundary_labels_displayed | PASS |
| test_copy_command_feedback_visual | PASS |
| test_existing_copy_response_not_broken | PASS |

### Régression (baseline)

```
pytest tests/ui/ → 13/13 PASS  (était 6/6 avant F14 → +7 nouveaux = 13)
pytest tests/api/test_brody_f10c... + test_brody_f12c... → 8/8 PASS
```

**Zéro nouvelle failure.**

---

## BUILD FRONTEND

```
tsc -b    → 0 erreurs TypeScript
vite build → ✓ built in 1.13s
dist/assets/index-B4ieXVlY.js  352.86 kB (gzip: 95.40 kB)
```

---

## GIT DIFF STAT

```
apps/obsidia-workbench/src/views/ChatView.tsx | 24 ++++++++++++++++++++++++
1 file changed, 24 insertions(+)
```

## GIT STATUS

```
## main...origin/main
 M apps/obsidia-workbench/src/views/ChatView.tsx
?? docs/runtime/OBSIDIA_F14_PRECHECK_GENERAL_PLAN_AUDIT_20260527_234105.md
?? docs/runtime/OBSIDIA_F14_COMMAND_COPY_BUTTON_UI_FREEZE_REPORT_20260527_234834.md
?? tests/ui/test_chatview_copy_command_button.py
```

## DIFF --CHECK

```
CLEAN — no trailing whitespace, no mixed line endings
```

---

## PROOFS

```
F14_UI_TESTS_7_7_PASS=true
F14_BUILD_PASS=true
F14_REGRESSION_UI_13_13_PASS=true
F14_REGRESSION_API_8_8_PASS=true
DIFF_CHECK_CLEAN=true
NO_BACKEND_TOUCHED=true
NO_KERNEL_TOUCHED=true
COPY_ONLY=true
NO_EXEC=true
NO_SHELL=true
NO_FETCH=true
```

---

## COMMIT PROPOSÉ (EN ATTENTE VALIDATION)

```
feat: freeze Brody copy command button UI F14
```

Tag proposé :
```
BRODY_F14_COMMAND_COPY_BUTTON_UI_FREEZE_20260527
```

Fichiers à stager :
```
apps/obsidia-workbench/src/views/ChatView.tsx
tests/ui/test_chatview_copy_command_button.py
docs/runtime/OBSIDIA_F14_PRECHECK_GENERAL_PLAN_AUDIT_20260527_234105.md
docs/runtime/OBSIDIA_F14_COMMAND_COPY_BUTTON_UI_FREEZE_REPORT_20260527_234834.md
```

---

## VALIDATION PHRASE

```
F14_COMMAND_COPY_BUTTON_UI_PASS
COPY_CMD_BUTTON_WIRED=true
CONDITIONAL_ON_COMMAND_PRESENT=true
CLIPBOARD_ONLY=true
NO_EXEC=true
NO_SHELL=true
NO_FETCH=true
COPY_ONLY=true
EXECUTION_ALLOWED_FOR_BRODY=false
BRODY_EXECUTE_ALLOWED=false
PACKET_EXECUTED=false
KX108_ONLY=true
BUILD_PASS=true
TESTS_7_7_PASS=true
REGRESSION_CLEAN=true
DIFF_CHECK_CLEAN=true
NO_BACKEND_TOUCH=true
NO_KERNEL_TOUCH=true
AWAITING_COMMIT_VALIDATION=true
```
