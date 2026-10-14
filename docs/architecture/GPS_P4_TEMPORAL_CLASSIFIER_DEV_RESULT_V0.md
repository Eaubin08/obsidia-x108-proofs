# GPS P4 — TEMPORAL CLASSIFIER DEVELOPMENT RESULT V0

Status: VERIFIED DEVELOPMENT DETECTION / NOT BLIND  
Decision authority: KX108_ONLY

## Test result

Unit tests:

```text
5 passed
```

## Calibration

Source: successful full GNSS-SDR real8 replay log.

Development-only calibration window:

- receiver time: 0–120 s
- positions: 156
- transitions: 155
- truth/onset consumed: false
- status: `DEVELOPMENT_POST_HOC_NOT_BLIND`

Observed baseline maxima:

- ECEF step: `16.963550135639597 m`
- GNSS clock residual: `0.5 s`
- receiver continuity gap: `1.0 s`

Frozen V0 development thresholds:

- ECEF step: `169.63550135639596 m`
- GNSS clock residual: `5.0 s`
- receiver continuity gap: `10.0 s`

Decision rule:

- `ANOMALY`: at least two simultaneous threshold violations
- `UNKNOWN`: exactly one threshold violation
- `NOMINAL`: no threshold violation

Calibration/input log SHA-256:

`233968690585d90bfa0e1255c6e7148f4168a0f346378c50ca8d5223dafa29fc`

## Detection result on inspected FGI recording

Overall classification:

`ANOMALY`

First anomaly:

- transition receiver time: `132 s -> 174 s`
- GNSS UTC: `2023-Nov-10 14:06:53.000000 -> 2023-Nov-10 23:55:24.500000`
- ECEF step: `14639.905457614153 m`
- receiver gap: `42.0 s`
- GNSS UTC delta: `35311.5 s`
- clock residual: `35269.5 s`

Violations:

- ECEF step: true
- clock residual: true
- receiver continuity gap: true
- violation count: 3

The detector did not consume the official 135 s onset or hostile truth label.

## Claim boundary

This is a deterministic trajectory-integrity anomaly detector result.

It does **not** yet prove:

- that the anomaly was caused by spoofing;
- a validated `HOSTILE` classification;
- spoofing resistance;
- TP/TN/FP/FN on a blind corpus;
- P2 live-passive closure;
- P3 independent physical corroboration;
- aviation validation/certification.

Because the FGI recording and its behavior were already inspected during development, this run cannot serve as the final blind benchmark.

The next use of this detector must preserve the frozen algorithm/threshold contract and validate it against data kept outside classifier development.
