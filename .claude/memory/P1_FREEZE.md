# P1 Freeze Inventory

> Authoritative source: `P1_FREEZE_NOTE.md` at the repo root. This file is a Claude-facing summary.
> **Entries marked `TO_VERIFY` were NOT confirmed against the live repo by Claude — verify before relying on them.**

---

## Phase status

- **Phase**: P1 (public proof perimeter, not the production platform)
- **Status**: Frozen publicly. Active work happens on P2+ on the `main` branch.

## Tag and commit

- Tag (per repo README excerpt): `p1-freeze-2026-04-22`  — **TO_VERIFY** against `git tag -l 'p1-freeze*'`
- Commit (per repo README excerpt): `99e966a` — **TO_VERIFY** against `git rev-parse p1-freeze-2026-04-22`

To verify both at once:

```powershell
git tag -l 'p1-freeze*'
git rev-parse p1-freeze-2026-04-22
git show --no-patch --pretty=format:'%H %s' p1-freeze-2026-04-22
```

If the tag is absent or the commit hash differs, **update this file** and notify the user. Do not silently override.

---

## Frozen folders / files (high confidence)

These were observed in the inspection report:

| Path | Type | Confidence |
|---|---|---|
| `proofs/V18_3_1/**` | Versioned proof bundle | HIGH (visible in inspection) |
| `proofs/V18_7/**` | Versioned proof bundle | HIGH |
| `proofs/V18_8/**` | Versioned proof bundle | HIGH |
| `proofs/lean/**` | Lean 4 sources | HIGH |
| `proofs/tla/**` | TLA+ reference specs | HIGH |
| `formal/tla/**` | TLA+ CI specs | HIGH |
| `proofs/merkle_root.json` | Crypto anchor | HIGH |
| `proofs/merkle_seal.json` | Crypto anchor | HIGH (named in inspection) |
| `merkle_root.json` (root) | Crypto anchor (root copy) | HIGH |
| `merkle_seal.json` (root) | Crypto anchor (root copy) | HIGH |
| `proofs/rfc3161_anchor.json` | TSA anchor | HIGH |
| `server.kernel.sealed.cjs` | Sealed bridge | HIGH |
| `RECUPE_SCORING/aggregation_stable.py` | Frozen scoring | HIGH |
| `RECUPE_SCORING/contracts_stable.py` | Frozen contracts | HIGH |
| `sigma/contracts.broken-ragnarok.py` | Intentional fixture | HIGH |
| `P1_FREEZE_NOTE.md` | Status doc | HIGH |
| `PUBLIC_STATUS.md` | Status doc | HIGH |

## Possibly frozen — TO_VERIFY

These are flagged by name pattern but not explicitly confirmed in the inspection:

| Path / pattern | Why flagged | Confidence |
|---|---|---|
| Any file matching `**/*root*` | Anchor-likely | TO_VERIFY |
| Any file matching `**/*seal*` | Anchor-likely | TO_VERIFY |
| Any file matching `**/*hash*` | Anchor-likely | TO_VERIFY |
| Any file matching `**/*anchor*` | Anchor-likely | TO_VERIFY |
| Any file matching `**/*freeze*` | Freeze-likely | TO_VERIFY |

To resolve, run:

```powershell
Get-ChildItem -Recurse -File |
  Where-Object { $_.Name -match '(root|seal|hash|anchor|freeze)' -and $_.FullName -notmatch 'node_modules|\.git' } |
  Select-Object FullName
```

Then add concrete entries above and remove TO_VERIFY rows.

---

## Why this file exists

So Claude can answer "is X frozen?" without re-scanning the repo every session. It is read by the `freeze-guardian` skill and the `/freeze-check` command. **Keep it accurate. When unsure, mark TO_VERIFY rather than guess.**
