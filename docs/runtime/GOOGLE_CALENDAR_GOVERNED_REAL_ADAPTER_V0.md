# WORLD_ACTION Google Calendar Governed Real Adapter V0

Date: 2026-10-07

Branch:
`feat/world-action-google-calendar-adapter-v0`

Base:
`feat/world-action-calendar-real-provider-pilot-v0`

Draft PR:
`#65`

Main mutation:
`NO`

## Purpose

Prove the first real external provider effect governed by the universal
WORLD_ACTION rail.

Google Calendar remains a peripheral transport. It is not part of the kernel.

## Chain actually exercised

```text
administration domain
→ exact WorldActionRequest
→ exact HumanApproval
→ WORLD_ACTION_PRE_EXECUTION
→ GuardX108 ALLOW
→ immutable KX108 decision record
→ explicit activation policy
→ LiveSovereignTicketV0
→ ObsidiaLiveGatewayV0
→ GoogleCalendarInvocationEnvelopeV0
→ Google Calendar provider create
→ provider readback
→ provider delete
→ provider readback = cancelled
→ GoogleCalendarRealProviderReceiptV0
```

## Exact governed invocation

KX108 decision:

`ALLOW`

Bound hashes:

- request: `acc2e98f744fa96656cbdf2923687075d0f689ccc6cc042af7abcf189dc4d6a7`
- human approval: `a8e65b9b1237716f9fe74af7728acc9a2a0930ee1817759a47e821e3f982006a`
- KX108 decision record: `c437053c56183c937e65cf497a27cb780447d494ac114ae1e678da2cd657463c`
- activation policy: `9d9c7fb9a3bdebcca17ce0fd4288cfa007e301c28ef27ce5d2cb48fdde5c4ef0`
- sovereign ticket: `0b5ccbb5db7eb6e600924a35f1bb8bd1e84e11f10308354fa2515ef88155effc`
- connector call: `946cf9f289c9e12b5a7a534ca1cdf3d892edd4467e23f51ba132e9559805d1a4`
- idempotency key: `cee6e59d6835a23243756cdb942d64adf436c99a3fc580fb8c24b26fcfaad760`
- invocation: `ce6f3654729cbfce79600b90e96e6001fc6b3e1915934599a24e3079d111c86c`

## Pilot restrictions

The adapter itself refuses widening outside the pilot:

- primary calendar only
- title must begin with `[OBSIDIA PILOT]`
- no attendees
- private visibility
- transparent event
- no Google Meet
- authenticated user omitted as attendee
- reminders disabled
- timezone = Europe/Paris
- duration <= 30 minutes
- CREATE_EVENT only

## Real provider observation

The exact invocation envelope was executed through the connected Google
Calendar transport.

Observed provider sequence:

1. CREATE_EVENT -> confirmed
2. readback -> confirmed, exact title/times, zero attendees
3. DELETE -> provider accepted
4. readback -> cancelled

No active test event remains.

The raw Google event id, authenticated email and provider URL are not persisted
in repository evidence.

Only the SHA-256 of the event id is retained.

## Receipt

`GoogleCalendarRealProviderReceiptV0` binds:

- invocation id/hash
- action id
- sovereign ticket hash
- request hash
- connector-call hash
- idempotency key
- provider identity
- hashed provider event id
- confirmed create status
- readback verification
- cancelled cleanup status
- no active event left
- real_external_effect=true
- obsidia_governed_invocation=true
- KX108_ONLY

## Important truth boundary

Proven:

`REAL_EXTERNAL_EFFECT = TRUE`

Proven:

`OBSIDIA_GOVERNED_INVOCATION = TRUE`

Not claimed:

`DIRECT_IN_PROCESS_OBSIDIA_NETWORK_TRANSPORT = TRUE`

The network transport was the Google Calendar connector available to the
runtime. Obsidia generated and governed the exact call envelope; the transport
executed it.

This is the desired architecture: connector transport remains peripheral and
replaceable.

## Previous universal proofs retained

Before this pilot the universal rail already had:

- WORLD_ACTION_PRE: 76/76 PASS
- LIVE Gateway: 64/64 PASS
- bounded executor/recovery: 78/78 PASS
- multi-métier conformance: 96/96 PASS
- first raw provider calibration: 69/69 PASS

## Verdict

`GOOGLE_CALENDAR_GOVERNED_REAL_PROVIDER_PILOT_V0_PROVEN`

The first real external provider effect has now been bound to a complete
Obsidia governance chain.

## Next

Reuse the same connector-boundary pattern for another low-risk surface.

Recommended order:

1. TASKS
2. CRM
3. MAIL draft
4. MAIL send only after explicit sender-mailbox authority

Payment, real trading and physical-device actuation remain outside this
low-risk progression.
