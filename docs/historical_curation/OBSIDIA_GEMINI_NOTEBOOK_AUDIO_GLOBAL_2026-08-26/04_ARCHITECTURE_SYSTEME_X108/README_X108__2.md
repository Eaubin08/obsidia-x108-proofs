
# X–108 Temporal Safety Gate

This repository integrates **X–108**, a minimal temporal safety gate
that prevents any irreversible autonomous action unless temporal
stability is demonstrated.

## Why X–108

Even if an agent is:
- prompt-injected
- misaligned
- compromised
- overly optimized

it cannot act irreversibly without passing X–108.

## Core Rule

No irreversible action is executed instantly.

## API

X108.check(state, irreversible=True) → HOLD | ACT

## Scope

X–108 is a safety layer, not an intelligence module.
