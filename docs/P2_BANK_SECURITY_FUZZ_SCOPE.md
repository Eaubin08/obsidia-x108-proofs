# P2 Bank Security Fuzz Scope

## Status

P2 BANK / SECURITY / FUZZ / HOSTILE-INPUT PACK

## Purpose

This layer tests the public bank runner against hostile inputs and malformed payloads.

Covered in this pack:
- unknown fields
- broken types
- missing required fields
- malformed shapes
- invalid payload paths
- replay hostility
- extreme pressure profiles

## What this pack proves

This pack publicly tests that:
- malformed inputs are rejected cleanly or fail closed
- hostile valid profiles do not drift into ALLOW
- suspicious replay remains stable
- invalid path inputs do not produce unsafe behavior

## What this pack does not prove

This pack does not prove:
- live API hardening
- auth bypass resistance
- privilege escalation resistance
- RCE resistance
- network rate-limit hardening
- dependency CVE hygiene
