# GPS P4 — CROSS-RECEIVER FGI TEMPORAL CONVERGENCE V0

Status: VERIFIED CROSS-RECEIVER TEMPORAL EFFECT / NO CAUSAL CLAIM  
Authority: KX108_ONLY

## Source

FGI-SpoofRepo UT_DFMC, source SHA-256:

`e8da962e92cfdbcb677361ce769a54f26dc385417bac9fd618492dcd02fb2d72`

Official hostile onset is used only for post-run scoring:

`135 s`

## Receiver A — FGI-GSRx

Historical FGI-GSRx result:

- pre-onset window A: stable NAV/PVT;
- post-onset window C: stable but displaced NAV/PVT;
- first-valid-PVT A→C ECEF delta: `14638.366 m`;
- last-valid-PVT A→C ECEF delta: `14639.336 m`;
- governance verdict: `HOLD`;
- no validated spoofing classifier.

## Receiver B — GNSS-SDR corrected real8

Current GNSS-SDR real8 full replay:

- first PVT fix at receiver second ~43;
- last pre-onset PVT at receiver second 132;
- first post-onset PVT at receiver second 174;
- post-onset PVT continues to end of recording;
- last-pre to first-post geodesic displacement: `14586.871 m`;
- last-pre to final geodesic displacement: `14587.374 m`;
- NAV remains available after onset;
- PVT remains available after the transition.

## Cross-receiver comparison

Using the first pre/post displacement figures:

- FGI-GSRx: `14638.366 m`
- GNSS-SDR real8: `14586.871 m`
- absolute difference: `51.495 m`
- relative difference versus GSRx: approximately `0.352 %`

The two independent receiver implementations therefore converge on the same approximately 14.6 km post-onset displacement effect.

## Additional GNSS-SDR temporal evidence

The GNSS-SDR full replay also shows:

- last pre-onset PVT UTC: `2023-11-10 14:06:53.000000`;
- first post-onset PVT UTC: `2023-11-10 23:55:24.500000`;
- observed GNSS-time discontinuity across the PVT transition: `35311.5 s`;
- receiver-time gap between the last pre-onset and first post-onset PVT epochs: `42 s`.

These are observed receiver outputs only.

## Claim boundary

This materially strengthens the observation that the recorded hostile RF produces a reproducible temporal/position discontinuity across two receiver implementations.

It does not, by itself, prove:

- causal attribution to spoofing;
- production spoofing resistance;
- a validated hostile classifier;
- TP/TN/FP/FN;
- P2 live-passive closure;
- P3 independent physical corroboration;
- aviation validation or certification.

The next P4 step is to freeze a deterministic classifier that does not consume the official onset/truth label, then score it post-run.
