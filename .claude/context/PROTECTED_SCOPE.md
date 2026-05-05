# Protected Scope

> Read this BEFORE any edit anywhere in the repo. When in doubt, run `/freeze-check`.

## Protected globs

| Glob | Why |
|---|---|
| `proofs/V18_3_1/**` | Versioned proof freeze bundle |
| `proofs/V18_7/**` | Versioned proof freeze bundle |
| `proofs/V18_8/**` | Versioned proof freeze bundle |
| `proofs/lean/**` | Lean 4 formal proof sources |
| `proofs/tla/**` | TLA+ reference specs |
| `formal/tla/**` | TLA+ CI-running specs |
| `proofs/merkle_root.json` | Crypto anchor — change invalidates seal |
| `merkle_root.json` | Crypto anchor (root copy) |
| `proofs/merkle_seal.json` | Crypto anchor |
| `merkle_seal.json` | Crypto anchor (root copy) |
| `proofs/rfc3161_anchor.json` | TSA anchor — re-anchoring requires external TSA call |
| `server.kernel.sealed.cjs` | Sealed / tamper-evident — silent integrity break |
| `RECUPE_SCORING/aggregation_stable.py` | Frozen — CI does `py_compile` only |
| `RECUPE_SCORING/contracts_stable.py` | Frozen — CI does `py_compile` only |
| `sigma/contracts.broken-ragnarok.py` | INTENTIONAL negative fixture — do NOT "fix" |
| `P1_FREEZE_NOTE.md` | Freeze status doc, frozen wording |
| `PUBLIC_STATUS.md` | Public status doc, frozen wording |
| Any file with `root`, `seal`, `hash`, `anchor`, `freeze` in its name | Treat as protected by default |
| `vendor/wheels/**` | Vendored Python wheels |
| `System.*/`, `Google.Protobuf.*/` | Vendored .NET deps |
| `.env`, `.env.*` | Secrets |
| `secrets/**` | Secrets |
| `**/*.pem` | Private keys |
| `audit/local/**` | Local-only audit data, never commit |

## What "protected" means

Without explicit user approval AND a verification plan posted first:

- ❌ Do not edit
- ❌ Do not reformat
- ❌ Do not normalize line endings
- ❌ Do not change encoding (UTF-8 BOM, UTF-16, etc.)
- ❌ Do not rename
- ❌ Do not regenerate
- ❌ Do not delete
- ❌ Do not move

Even a "trivial" whitespace-only diff in an anchored file silently invalidates the seal.

## What IS allowed

- ✅ `Read` (read-only)
- ✅ `Glob` / `Grep` to locate
- ✅ `git log` / `git show` / `git diff` (read-only)
- ✅ Inspect with the `explorer` subagent
- ✅ Diagnose with the `proof-sentinel` skill
- ✅ Discuss the contents conceptually with the user

## When the user asks to modify a protected file

Mandatory output before any change:

```
Protected scope:           <which glob(s)>
Canonical / freeze status: <FROZEN | SEALED | ANCHORED | VENDORED | INTENTIONAL_FIXTURE>
Modification allowed?      ONLY_WITH_APPROVAL
Risk:                      HIGH
Required approval:         user must reply "Approved." in this session
Safe alternative:          <e.g. write a patch into staging/, or open a new V18 bundle, or use a verifier override>
Verification:              <exact command sequence to confirm the change>
```

Then **wait** for the explicit `Approved.` before any `Edit` / `Write`.

## When in doubt

Run `/freeze-check <path>`. The skill will return `YES / NO / ONLY_WITH_APPROVAL` and the matching rule.
