# Proof Scope

## Purpose

This document defines how to read the public proof perimeter of `obsidia-x108-proofs` after the P1 freeze.

## Core rule

Not all PASS results describe the same kind of object.

The public P1 perimeter contains several categories that must be read separately.

## Canonical categories

### 1. Lean formal proofs
These are machine-checked formal proofs inside the public Lean perimeter.

### 2. TLA+ / TLC model checking
These are bounded model-checking runs over the public TLA+ specifications.

### 3. Python executable verification
These are public verification scripts such as:
- `verify_all.py`
- `verify_decision.py`

### 4. Public Sigma minimal layer
These are public Sigma entry points, examples and smoke tests.

### 5. QA and network probing
These are public QA checks such as:
- RFC3161 anchor schema checks
- cross-platform QA
- TSA endpoint probing

## What the public repo is

This repository is:
- a public proof layer
- a public verification layer
- a public execution layer for P1

## What the public repo is not

This repository is not:
- the complete proprietary production engine
- the complete production Sigma layer
- the final operator cockpit
- a claim that every production adapter is published here

## Interpretation hierarchy

When in doubt, read in this order:
1. `P1_FREEZE_NOTE.md`
2. `PUBLIC_STATUS.md`
3. `README.md`
4. this file
5. the actual scripts and tests

## Allowed public claim

The allowed public claim is:

The public P1 proof / verification / execution perimeter of Obsidia X-108 is closed, reproducible, and publicly frozen.

## Not allowed public over-claim

The following over-claims should be avoided:
- "the full production engine is public"
- "all production business adapters are public"
- "external TSA availability is guaranteed"
- "P1 equals final production deployment"