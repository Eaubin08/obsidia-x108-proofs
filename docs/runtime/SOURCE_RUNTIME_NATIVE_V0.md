# SOURCE_RUNTIME_NATIVE_V0

Date: 2026-10-07

Branch:
`feat/source-runtime-native-v0`

Draft PR:
`#69`

Base:
`feat/native-tasks-crm-v0`

Main merge:
`NO`

## Purpose

Own external source identity, provenance and READONLY observations inside
Obsidia rather than inside a métier domain such as CSSA.

Supported source kinds:

- MAILBOX
- DOCUMENT_REPOSITORY
- CALENDAR
- FORM_INBOX
- API_READONLY

## Chain

```text
provider adapter
→ observed source candidate
→ exact human source authorization
→ immutable native source registration
→ READONLY observation
→ provenance-complete source context packet
→ domain interpretation
```

No provider adapter is active in this phase.

## Authority

Every source object remains:

```text
decision_authority = KX108_ONLY
allowed_to_decide = false
allowed_to_act = false
external_mutation_allowed = false
is_execution_authority = false
```

## Two-key onboarding

A connector-observed source cannot self-promote.

Activation requires:

1. exact observed source candidate
2. exact human source authorization

Account/source identity drift or observed capability drift changes the
candidate hash and invalidates prior authorization.

Approved capabilities may only reduce the observed capability set.

## Registry

Native source registrations are immutable.

Revocation is append-only.

A revoked source can no longer create new observations and previously issued
context packets fail active-source verification.

## Privacy / provenance

Canonical observations retain only hashes for:

- provider item id
- content
- metadata
- source registration

Raw credentials, raw source identity, provider item ids and raw content are
not persisted by the native source runtime contract.

## Context packet

Each observation produces a deterministic
`OBSIDIA_NATIVE_SOURCE_CONTEXT_PACKET_V0` binding:

- source id/kind/provider
- registration hash
- observation id/hash
- content hash
- metadata hash
- observed timestamp
- provenance_complete=true
- KX108_ONLY
- no decision/action authority

## Runtime fact

`native_source_runtime_present=true`

This says only that the native source runtime code is present.

It does not claim:

- a live mailbox connection
- a live document repository
- a live calendar
- network I/O
- external mutation authority

## Proof

Run:
`37618281703`

Result:
`103 passed in 0.77s`

Includes source-runtime tests plus native TASKS/CRM and WORLD_ACTION
regressions.

## Verdict

`SOURCE_RUNTIME_NATIVE_V0_PROVEN`

## Next

Build provider-neutral native connectors:

- MAIL_NATIVE_CONNECTOR_V0
- DOCUMENT_NATIVE_CONNECTOR_V0
- CALENDAR_NATIVE_CONNECTOR_V0

using local/simulated providers first.
