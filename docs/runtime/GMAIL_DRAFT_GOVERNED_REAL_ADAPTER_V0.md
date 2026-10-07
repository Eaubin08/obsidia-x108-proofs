# WORLD_ACTION Gmail Governed Real Draft Adapter V0

Date: 2026-10-07

Branch:
`feat/world-action-gmail-draft-adapter-v0`

Base:
`feat/world-action-google-calendar-adapter-v0`

Draft PR:
`#66`

Main mutation:
`NO`

Real sent email:
`NO`

## Purpose

Prove a second real external provider surface through the universal WORLD_ACTION rail, using Gmail draft creation only.

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
→ GmailDraftInvocationEnvelopeV0
→ Gmail create draft
→ Gmail draft readback
→ Gmail draft cleanup
→ GmailDraftRealProviderReceiptV0
```

## Pilot restrictions

The adapter refuses any widening outside the pilot:

- authenticated self only
- recipient bound by SHA-256, raw address not persisted
- draft only
- no send
- no CC
- no BCC
- no attachment
- no reply thread
- plain text only
- subject prefix `[OBSIDIA PILOT]`

## Real provider observation

Observed sequence:

1. CREATE_DRAFT -> provider draft created
2. list/readback -> exact pilot draft present
3. cleanup -> provider delete/trash succeeded
4. post-cleanup list -> pilot draft absent
5. `send_draft` was never invoked

## Exact governed chain

- request hash: `38882b6e931ac8815fc76757bcf96103d4c39692ac69ef8f52f0825049407cc6`
- human approval hash: `e88df6106507ea03e0b81edf9eaae0d242489f0bf1981522d934bbd405e47aff`
- KX108 decision record hash: `1a582a9f536996c8baf070c54ab629d08f35c24e1b5d83870f111890058fa442`
- activation policy hash: `cf91334c80ddd9546260e0f23cd06217e4f1aefe0d692ac6a5e88b3f1efc2072`
- sovereign ticket hash: `5c26a9e74c64edffd6395169c0590a11ba7db5367f369f35993b960b689c9e5f`
- connector call hash: `df92b7a01e7aaac9284790da47450faa37cae0475d5e627683e86571f261c412`
- idempotency key: `78c98521236ef0b3cc0dbee4e0bdd61f9f5757a542fb8275f708af6268c0b87b`
- invocation hash: `c9cb880ea8af220e31c777c54c45d9f248b6c0e3a5c43c2ff982d2a17dfa08ee`

## Privacy

The repository stores no raw Gmail address, draft id, message id or Gmail URL.

Only SHA-256 bindings are retained.

## Truth boundary

Proven:

- REAL_EXTERNAL_EFFECT = TRUE
- OBSIDIA_GOVERNED_INVOCATION = TRUE
- DRAFT_READBACK = TRUE
- DRAFT_CLEANUP = TRUE
- SENT_MESSAGE_CREATED = FALSE

Not claimed:

- direct in-process Obsidia Gmail network transport

The Gmail transport remains peripheral.

## Verdict

`GMAIL_DRAFT_GOVERNED_REAL_PROVIDER_PILOT_V0_PROVEN`

No email was sent.
