# Sigma Public P1

## Purpose

This document explains what Sigma means in the public P1 perimeter of `obsidia-x108-proofs`.

## What Sigma public P1 is

Sigma public P1 is the public minimal Sigma layer exposed in this repository.

It includes:
- `sigma/run_pipeline.py`
- `sigma/sigma_monitor.py`
- `sigma/contracts.py`
- `sigma/protocols.py`
- `sigma/examples/`
- `sigma/tests/`

This public layer is sufficient to:
- run public Sigma smoke scenarios
- inspect public Sigma inputs and outputs
- verify that Sigma public entry points behave correctly inside the P1 perimeter

## What Sigma public P1 is not

Sigma public P1 is not:
- the full proprietary production Sigma layer
- the full production orchestration system
- the final business operating layer

The public repository exposes a minimal, auditable, runnable Sigma perimeter.
It does not claim to publish all production internals.

## Public Sigma entry points

Primary public commands:

Run the public Sigma pipeline on a normal bank example:
`python .\sigma\run_pipeline.py bank .\sigma\examples\bank_normal.json`

Run the public Sigma monitor:
`python .\sigma\sigma_monitor.py --json`

Run Sigma tests:
`python -W ignore -m pytest .\sigma\tests -v`

## What a successful Sigma public run means

A successful Sigma public run means:
- the public minimal Sigma layer is present
- the public Sigma entry points execute correctly
- the public examples and smoke tests pass
- the public outputs remain readable and structured inside P1

It does not mean:
- the full production Sigma layer is published
- all proprietary production adapters are exposed
- P1 has become a complete business product

## Public output reading

Typical public output includes:
- `market_verdict`
- `x108_gate`
- `reason_code`
- `decision_id`
- `trace_id`
- `ticket_required`
- `ticket_id`
- `attestation_ref`
- `sigma_report`

Interpretation:
- these outputs show that the public minimal Sigma layer is connected to the public P1 verification perimeter
- they do not imply that the full proprietary production Sigma implementation is included

## Position inside P1

Sigma public P1 belongs to the public proof / verification / execution perimeter.
It is one public layer of P1, not the whole private production architecture.