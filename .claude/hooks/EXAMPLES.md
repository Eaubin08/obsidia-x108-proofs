# Hook activation examples

> All hook scripts in this folder are **SCRIPTS ONLY** — they are NOT wired in `settings.json` by default.
> To activate any of them, copy the corresponding block below into `.claude/settings.local.json`
> (which Claude Code reads after `settings.json` and is gitignored by convention).

> **Conservative posture for this repo**: do NOT wire auto-format, auto-lint, auto-test, or any
> hook that touches files. The only safe hooks are read-only / warn-only / snapshot.

---

## SessionStart hook (recommended, read-only)

Prints branch, status, and reminders at session start.

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          { "type": "command", "command": "bash .claude/hooks/session-start.sh" }
        ]
      }
    ]
  }
}
```

## PreToolUse warn on protected paths (recommended, warn-only — does NOT block)

Prints a big warning if the Edit/Write target matches a protected glob. The user still has to approve via `freeze-guardian` — this hook is just a visible reminder.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "bash .claude/hooks/pre-edit-protected-warn.sh" }
        ]
      }
    ]
  }
}
```

## PreCompact snapshot (recommended, read+append only)

Copies `SCRATCH.md` and `CURRENT_FOCUS.md` into `.claude/memory/snapshots/<timestamp>/` before `/compact` runs.

```json
{
  "hooks": {
    "PreCompact": [
      {
        "matcher": "*",
        "hooks": [
          { "type": "command", "command": "bash .claude/hooks/pre-compact-snapshot.sh" }
        ]
      }
    ]
  }
}
```

---

## Hooks NOT recommended for this repo

Do **NOT** wire any of these without a separate sandbox evaluation:

- `PostToolUse` running auto-format / auto-lint on Edit / Write — risks invalidating proof seals.
- `PostToolUse` running pytest / `lake build` / TLC — token-expensive, noisy, can mask real failures.
- Any hook that runs `npm install` / `pip install` / `winget install`.
- `Stop` hooks that auto-commit or push.

If a future task ever needs one of these, document it as a one-off, scope-limited approval, and remove the hook afterwards.

---

## How to combine multiple hooks safely

Merge the `hooks` blocks above into a single object:

```json
{
  "hooks": {
    "SessionStart": [ { "matcher": "*", "hooks": [
      { "type": "command", "command": "bash .claude/hooks/session-start.sh" }
    ]}],
    "PreToolUse": [ { "matcher": "Edit|Write", "hooks": [
      { "type": "command", "command": "bash .claude/hooks/pre-edit-protected-warn.sh" }
    ]}],
    "PreCompact": [ { "matcher": "*", "hooks": [
      { "type": "command", "command": "bash .claude/hooks/pre-compact-snapshot.sh" }
    ]}]
  }
}
```

Place this in `.claude/settings.local.json`. Add `.claude/settings.local.json` to `.gitignore` if it isn't already.
