# GPS / DEFENSE / AVIATION — CANONICAL FUSION V0

Status: AUDITED / PRE-FORGE CANONICALIZATION  
Base: `feat/gps-live-controlled-receiver-readiness-v0`  
Authority: `KX108_ONLY`

## 1. Purpose

Unify the two GPS/Defense/Aviation trajectories without reviving obsolete architecture:

1. historical scientific / RF work (recorded-real GNSS, I/Q RF, FGI/GNSS-SDR/GSRx, blind benchmark discipline, PASS8/PASS9 lessons, terrain/HIL/aviation plan);
2. current physical-world forge (F12→F25, MMonde, measurement/evidence, Physical Signal Periphery, Physical Evidence Plane, Science/Constraint Engine, cross-modal coherence, GPS physical-world closure);
3. post-freeze physical continuation (P1→P7).

This is a semantic and evidence fusion, not a blind Git merge.

## 2. Canonical rule

```text
OLD VALIDATED EVIDENCE / METHODS
          +
CURRENT CANONICAL PHYSICAL WORLD
          +
POST-FREEZE TERRAIN GATES
          ↓
GPS / DEFENSE / AVIATION CANONICAL
```

Do not duplicate a subsystem that already exists in the current forge.

Do not promote an old experiment into a stronger claim than it originally supported.

## 3. What is retained from the historical GPS line

### 3.1 Recorded-real GNSS / RF

Retain:
- real RINEX evidence;
- real I/Q RF evidence;
- GNSS-SDR processing;
- immutable provenance/hashes where available;
- reproducible recorded runs;
- recorded hostile RF artifacts;
- measured navigation/PVT effects where the evidence exists.

Canonical destination:
- Physical Signal Periphery;
- Physical Evidence Plane;
- GPS/PNT DomainState;
- KX108;
- receipts/replay.

### 3.2 FGI / GSRx / GNSS-SDR work

Existing repository families under `hackathons/nativebuilder-gps-defense/` remain reusable evidence and tooling.

Examples already present:
- FGI GNSS-SDR configs/reports;
- FGI/GSRx runtime material;
- GNSS-SDR logs;
- RF attack benchmark material.

These are reused for P4/P5/P6. They are not rebuilt as a second RF stack.

### 3.3 PASS8 methodology

Retain the experimental discipline:
- DEV / FINAL separation;
- precommit before opening final truth;
- blind evaluation;
- deterministic classifier freezing;
- repeated runs;
- confusion-matrix style evaluation;
- no post-final tuning.

Do **not** retain an unsupported conclusion that PASS8 solved hostile detection.

Historical final baseline:
- 4 blind cases;
- 1 NOMINAL;
- 3 HOLD;
- 0 hostile attacks classified HOSTILE.

Interpretation:
PASS8 is a fail-closed scientific baseline, not a successful spoofing detector.

### 3.4 PASS9 direction

Historical PASS9 themes:
- richer temporal RF perception;
- physical constraints;
- world/reality relations;
- multi-source reasoning;
- IMU/independent source;
- causal attribution.

Most of this direction is now structurally absorbed by the current forge:
- F12 Situated World Dynamics;
- F15 Physical Evidence Plane;
- F18 Science / Constraint Engine;
- F20 Cross-Modal Coherence;
- F21 GPS Physical-World Closure.

Therefore PASS9 is not rebuilt as a parallel architecture.

### 3.5 Terrain / aviation plan

Historical progression remains valid:

```text
recorded data
→ hardware-in-the-loop
→ physical receiver
→ multiple receivers
→ avionics bench
→ ground shadow mode
→ in-flight shadow mode
→ onboard-system comparison
→ safety evaluation / certification
```

The old `FIELD-DEMO-AVIATION-001` / `aviation_robo.py` path is treated as structured terrain/demo plumbing, not proof of a real aircraft feed.

## 4. Current canonical physical-world stack

Already closed or materially built:
- F12 Situated World Dynamics;
- F13 Measurement / Evidence Contract;
- F14 Physical Signal Periphery;
- F15 Physical Evidence Plane;
- F16 real-image observation boundary;
- F17 GMS trajectory adapter;
- F18 Science / Constraint Engine;
- F19 physical thermodynamics adapter;
- F20 Cross-Modal Coherence;
- F21 GPS Physical-World Closure with explicit open physical blockers;
- F22 real recorded replay demos;
- F24 negative-test/global-regression hardening;
- F25 public claim freeze.

This stack is the canonical host for historical GPS evidence.

## 5. Post-freeze fusion path

### P1 — Controlled receiver readiness — VERIFIED

Already hardened:

`configured receiver candidate != observed live capture`

`eligible_for_physical_claim != sensor_attestation_proven`

No environment variable or configured device can become `REAL_PASSIVE_GNSS` without observed live evidence.

### P2 — Real passive GNSS capture — CURRENT

Required before any live claim:
- actual passive receiver / SDR output;
- immutable capture hash;
- capture timestamp;
- receiver identity and configuration;
- current observables;
- calibration/configuration evidence where applicable;
- provenance;
- explicit limitations;
- normalized Physical Signal Periphery envelope;
- GPS domain → KX108 fail-closed path.

Target:
`REAL_PASSIVE_GNSS`

### P3 — Multi-source physical corroboration

Add a genuinely independent physical source, such as justified IMU/INS or another suitable source.

Required:
- independent source provenance;
- clock alignment;
- frame alignment;
- calibration;
- uncertainty;
- no synthetic independence from distinct IDs alone.

### P4 — Recorded hostile RF closure

Reuse historical FGI/GSRx/GNSS-SDR evidence and current canonical contracts.

Required:
- accepted pre-attack baseline;
- stable evaluable pre/post windows;
- official attack onset only for post-run scoring;
- no label leakage;
- reproducible output;
- attack classification separated from governance HOLD.

### P5 — Causal attribution

Separate:
- anomaly;
- correlation;
- causal spoofing attribution.

No `CAUSAL_PROVEN` from temporal coincidence alone.

### P6 — Benchmark matrix

Populate materially:
- TP;
- TN;
- FP;
- FN;
- detection rate;
- false positive rate;
- false negative rate;
- detection delay;
- drift before detection;
- reproducibility.

No public spoofing-resistance claim before this gate is materially closed.

### P7 — Controlled live hostile test

Only after P4/P5/P6:
- authorized controlled environment;
- cable / RF enclosure / shielded lab;
- no uncontrolled RF transmission;
- real receiver;
- capture-first evidence;
- KX108 fail-closed;
- receipts/replay;
- compare live behavior to recorded benchmark.

## 6. After P7

```text
P7 controlled live hostile
→ HIL
→ multiple receiver families
→ avionics bench
→ ground shadow
→ flight shadow, no actuation authority
→ onboard-system comparison
→ safety / industrial / certification track
```

Early aviation phases remain observation/shadow only. Obsidia does not acquire flight-control authority from this roadmap.

## 7. Fusion matrix

| Historical asset / lesson | Canonical destination | Action |
|---|---|---|
| Real RINEX | Physical Signal Periphery / F21-F22 | reuse |
| Real I/Q RF | Physical Signal Periphery / P4 | reuse |
| GNSS-SDR | existing GPS periphery | reuse |
| FGI / GSRx assets | P4/P5/P6 | reuse, audit inputs |
| DEV/FINAL blind discipline | P4/P6 evaluation protocol | preserve |
| PASS8 fail-closed result | historical baseline | preserve, never overclaim |
| PASS9 temporal/constraints ideas | F12/F15/F18/F20 | already absorbed |
| old terrain connector | demo/adapter reference | reuse only if current interface-compatible |
| FIELD-DEMO-AVIATION-001 | structured demo evidence | not real-flight proof |
| HIL plan | post-P7 validation | preserve |
| shadow ground/flight | aviation validation ladder | preserve |

## 8. Explicit non-goals

This fusion does not:
- merge old branches blindly;
- rewrite F12→F25;
- reintroduce Graphiti;
- add decision authority outside KX108;
- treat provenance as authenticity;
- treat configuration as physical observation;
- treat HOLD as proof of hostile classification;
- claim certification;
- claim real-aircraft validation;
- claim live hostile success before controlled evidence exists.

## 9. Immediate next action

The architecture fusion is conceptually closed enough to proceed physically.

The next executable gate is **P2**:

```text
real passive receiver
→ observed capture
→ hash / timestamp / receiver identity / config
→ observables
→ Physical Signal Periphery
→ GPS DomainState
→ KX108
→ receipt / replay
```

If no actual receiver capture is available, the correct state remains BLOCKED / STRUCTURED_STATE rather than inventing physical proof.
