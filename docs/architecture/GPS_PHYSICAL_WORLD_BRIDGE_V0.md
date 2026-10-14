# F5 — GPS physical-world bridge V0

Status: implementation candidate.

This stage reuses existing recorded-real GPS evidence. It does not claim that the hostile LIVE/recorded-RF benchmark is closed.

Evidence already present in the repository includes a NOAA CORS RINEX capture classified as RECORDED_REAL_GNSS with source hashes/provenance, and the FGI UT_DFMC RF benchmark whose receiver path remains BLOCKED_RECEIVER_CONFIGURATION before the official 135 s attack onset.

The bridge is:

```text
recorded GNSS / RF evidence
  -> RecordedGpsEvidenceV0
  -> WorldObservationV0 / WorldStateV0
  -> DomainStateRefV0[gps_defense_aviation]
  -> GovernancePayloadV0
  -> KX108_ONLY
```

Invariants:

- recorded provenance != physical authenticity;
- observation != truth;
- temporal sequence != causality;
- a receiver/configuration blocker remains an explicit unknown/risk;
- blocked pre-attack receiver behavior cannot be promoted to spoofing detection;
- GPS/domain code cannot decide or act;
- KX108 remains the authority boundary;
- physical-domain laws and thresholds remain in the GPS/Defense/Aviation Domain Pack.

F5 V0 deliberately does not close LIVE, RF attack classification, IMU/radar fusion, the 135 s baseline, confusion metrics, or causal attribution. Those require real evidence and/or a receiver configuration that produces stable NAV/PVT before attack onset.
