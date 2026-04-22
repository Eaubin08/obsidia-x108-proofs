# Limits

## Purpose

This document states the structural limits of the public P1 perimeter.

## External TSA dependencies

RFC3161 TSA providers are third-party services.
Network reachability can vary by environment and over time.

A successful TSA reachability result means:
- the public QA probe succeeded in the validated environment

It does not mean:
- long-term control over the external service
- guaranteed uptime of all third-party endpoints
- sovereignty over those providers

## RFC3161 local vs RFC3161 network

Two different things are validated in P1:

RFC3161 local:
- local tooling such as `openssl`
- local ability to inspect or exercise RFC3161-related tooling

RFC3161 network:
- public reachability checks against external TSA endpoints
- current public QA probe logic includes `HEAD -> GET` fallback to reduce false negatives

These two layers must not be confused.

## TLC and Lean prerequisites

P1 assumes the local environment can provide:
- Java / `tla2tools.jar`
- Lean 4 / Lake
- Python 3.11+ recommended

If one of these prerequisites is missing, the corresponding public run may fail locally without invalidating the frozen public state itself.

## Formal model vs production reality

Lean and TLA+ results in this public repository validate the public model perimeter.
They do not automatically claim complete production equivalence for every proprietary integration layer.

## Public perimeter vs production engine

This repository is a public proof and verification perimeter.
It is not the complete proprietary production engine.

It does not claim:
- complete production publication
- complete business deployment
- final operator cockpit publication

## Generated artifacts

Some logs and state artifacts can be regenerated locally by running the public scripts.
These generated artifacts are not the canonical freeze reference by themselves.
The canonical freeze reference remains:
- public freeze commit `99e966a`
- tag `p1-freeze-2026-04-22`