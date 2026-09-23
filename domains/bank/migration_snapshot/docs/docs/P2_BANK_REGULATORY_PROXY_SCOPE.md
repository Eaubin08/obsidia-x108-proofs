# P2 Bank Regulatory Proxy Scope

## Status

P2 BANK / REGULATORY PROXY PACK

## Purpose

This pack introduces a regulatory-style proxy layer with an explicit HOLD zone.

Families:
- aml
- kyc
- beneficiary
- urgency
- anomaly
- combined

Zones:
- allow
- hold
- block

## Main objective

Break the current ALLOW / BLOCK binary and make the sovereign middle zone publicly testable.

## What this pack proves

It proves that the public bank perimeter can be replayed against:
- nominal cases expected to stay ALLOW
- borderline pre-maturity cases expected to become HOLD
- hard risk cases expected to become BLOCK

## What this pack does not prove

It does not prove:
- legal certification
- regulatory sign-off
- real production banking validation
