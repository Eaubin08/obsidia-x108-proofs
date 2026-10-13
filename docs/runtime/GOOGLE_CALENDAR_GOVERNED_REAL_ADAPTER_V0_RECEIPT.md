# Google Calendar Governed Real Adapter V0 — Proof Receipt

Date: 2026-10-07

Branch:
`feat/world-action-google-calendar-adapter-v0`

Draft PR:
`#65`

Main merge:
`NO`

## Real provider result

- provider: GOOGLE_CALENDAR
- CREATE_EVENT: confirmed
- readback after create: verified
- cleanup: cancelled
- active event left: NO
- real external effect: YES
- governed invocation: YES
- direct in-process Obsidia network client: NO
- transport bridge: Google Calendar connector

## Privacy

- raw provider event id persisted: NO
- authenticated email persisted: NO
- provider event URL persisted: NO
- provider event id SHA-256 persisted: YES

## Exact receipt

Receipt id:
`gcalreceipt-efe12a8ebab5edbec0b4ca831205277b`

Receipt hash:
`76449aaaf81f2e02c6b7c438206174aac2fe86cd2e024524cba4f0c21874cb6b`

Invocation hash:
`ce6f3654729cbfce79600b90e96e6001fc6b3e1915934599a24e3079d111c86c`

KX108 gate:
`ALLOW`

Decision authority:
`KX108_ONLY`

## Verdict

`GOOGLE_CALENDAR_GOVERNED_REAL_PROVIDER_PILOT_V0_PROVEN`
