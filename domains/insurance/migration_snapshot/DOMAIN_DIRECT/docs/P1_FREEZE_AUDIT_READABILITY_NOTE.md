# P1 Freeze Audit Readability Note

## Status

P1 AUDIT READABILITY NOTE

## Purpose

This note exists to remove ambiguity between:
- the canonical public freeze of P1
- the ongoing public work that may continue on `main` after that freeze

## Canonical P1 audit target

For any external audit of the P1 public perimeter, the canonical target is:

- technical closure commit: `bd87e15`
- public freeze commit: `99e966a`
- official freeze tag: `p1-freeze-2026-04-22`

For readability and public audit, the primary reference is:

- tag: `p1-freeze-2026-04-22`
- public freeze commit: `99e966a`

## Branch interpretation rule

`main` is an active branch.

It may contain post-freeze work after P1, including:
- P2-bank
- public benchmark overlays
- proxy packs
- confusion / scale / fuzz packs
- later public verification extensions

These later commits do not redefine the frozen P1 perimeter.

## Auditor reading rule

If the objective is to evaluate the public P1 perimeter, the reader should:

1. target `p1-freeze-2026-04-22`
2. use `99e966a` as the public freeze commit
3. read later commits on `main` as post-freeze continuation work
4. avoid interpreting the moving HEAD of `main` as the canonical definition of P1

## What this note clarifies

This note clarifies that:
- P1 is closed as a public frozen perimeter
- post-freeze work may continue publicly on `main`
- CI or commit activity after the freeze does not invalidate the canonical P1 freeze
- the audit object for P1 is the tagged freeze, not the moving branch head

## What this note does not claim

This note does not claim:
- that all later work on `main` belongs to P1
- that post-freeze checks must remain identical to freeze-time checks
- that P2-bank or later public packs are part of the original P1 perimeter
- that a moving branch should replace a frozen audit target

## Immediate practical reading

Cold reading for an external auditor:

- if you audit P1, audit the tag
- if you inspect ongoing work, inspect `main`
- do not merge these two readings into one perimeter

## Related files

- `README.md`
- `docs/status/P1_FREEZE_NOTE.md`
- `docs/status/PUBLIC_STATUS.md`
