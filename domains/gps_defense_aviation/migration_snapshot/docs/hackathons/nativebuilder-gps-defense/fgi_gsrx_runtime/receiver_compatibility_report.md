# Receiver Compatibility Report - FGI UT_DFMC

Date: 2026-08-03

## Verdict

FGI-GSRx is now executable in the hackathon Docker/Octave runtime far enough to decode UT_DFMC GPS L1 to NAV/PVT.

This supersedes the earlier GNSS-SDR blocker for UT_DFMC. GNSS-SDR remained useful for nominal CTTC RF, but FGI-GSRx is the technically faithful receiver path for this FGI corpus.

## Evidence

| Window | Time span | Acquisition | Tracking | NAV/ephemeris | PVT |
|---|---:|---|---|---|---|
| A | `0-60 s` | 14 GPS L1 PRNs | complete, 60 s | ephemeris found for 13 PRNs | 539 valid epochs |
| C | `135-180 s` | 12 GPS L1 PRNs | complete, 45 s | ephemeris found for 12 PRNs | 368 valid epochs |

## X-108 chain

Both windows were normalized into physical observation envelopes, passed through:

```text
FGI-GSRx NAV/PVT
-> Physical Reality Gate
-> DomainState GPS
-> P3-05
-> P4-20
-> X-108 live HTTP POST
-> receipt / kernel evidence
```

Live kernel HTTP status was `200` for both windows. X-108 returned `HOLD` with reason `UNKNOWNS_OR_CONFIDENCE_LOW`; P3-05/P4-20 also fail closed because there is no inertial/radar corroboration.

## Claim boundary

This proves hostile RF decoding to NAV/PVT plus governance fail-closed behavior. It does not yet prove spoofing resistance or correct hostile classification, because the observed `HOLD` is caused by missing multi-source corroboration, not by a validated RF spoofing detector.
