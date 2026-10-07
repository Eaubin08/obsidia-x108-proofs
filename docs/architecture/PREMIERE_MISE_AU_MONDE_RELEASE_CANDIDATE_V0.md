# F25 — Première Mise au Monde — Public Freeze / Release Candidate V0

Status: FROZEN / NO F25 REGRESSION

## Scope

F25 freezes the verified first-world chain without adding a new runtime layer.

Included:
- F12 Situated World Dynamics
- F13 Measurement / Evidence
- F14 Physical Signal Periphery
- F15 Physical Evidence Plane
- F16 Vision / Real Image
- F17 GMS Trajectory Adapter
- F18 Science / Constraint Engine
- F19 Physical Thermodynamics Adapter
- F20 Cross-Modal Coherence
- F21 GPS Physical-World Closure
- F22 Real E2E Demonstrations
- F24 Global Regression / Negative Tests

F23 Monde UI is deliberately outside this repository freeze and remains a separate `monde-obsidia` concern.

## Frozen authority boundary

The release candidate preserves:

`INTELLIGENCE != AUTHORITY`

`DOMAIN != AUTHORITY`

`PROOF != PERMISSION`

`WORLD_STATE != MEMORY`

`WORLD_STATE != COGNITION`

`OBSERVATION != TRUTH`

`KX108_ONLY`

No component introduced by F12→F25 gains decision or ACT authority.

## Supported public claims

### 1. Recorded-real GNSS

Supported wording:

> A real NOAA/NGS RINEX observation traversed the recorded-real GPS chain and remained fail-closed when live attestation and multisource corroboration were not proven.

Bounded proof level: `RECORDED_REAL_GNSS`.

### 2. Recorded-real RF

Supported wording:

> A public recorded GNSS I/Q dataset was processed through GNSS-SDR and traversed the recorded-real RF chain while remaining bounded to recorded evidence.

Bounded proof level: `RECORDED_REAL_RF`.

### 3. Canonical replay

Supported wording:

> Stored recorded-real GPS artifacts can be re-ingested through the current canonical world, domain and reality-authenticity contracts without claim promotion.

### 4. Authority separation

Supported wording:

> The first-world periphery, domain bridges, scientific layers and proof layers do not gain decision or action authority; decision authority remains KX108_ONLY.

## Explicitly forbidden claims

The release candidate does **not** support claims that:
- live GNSS closure is complete;
- live RF closure is complete;
- hostile live spoofing resistance is proven;
- causal spoofing attribution is proven;
- aviation production certification exists;
- defense production certification exists;
- private sensor attestation is proven;
- IMU/radar corroboration is proven;
- global physical authenticity is proven;
- a complete general world model exists;
- a complete general science solver exists;
- GMS distance/trajectory proves semantic truth;
- vision reconstructs hidden reality as truth.

## GPS evidence boundary

Existing GPS evidence supports:
- recorded NOAA/NGS RINEX;
- recorded public CTTC GNSS I/Q processed with GNSS-SDR;
- real fail-closed governance behavior;
- canonical replay under the current contracts.

Existing GPS evidence does not support:
- production certification;
- live receiver closure;
- validated spoofing-resistance metrics;
- causal hostile-RF attribution.

## Scientific boundary

F18/F19 remain representation and constraint layers.

`model reference != model execution`

`equation reference != solved equation`

`empirical evidence != formal proof`

`model-scoped impossibility != metaphysical impossibility`

Physical thermodynamics remains separate from computational/cognitive thermodynamic signals.

## Vision boundary

Real-image contracts preserve asset provenance, capture governance and visual primitive evidence.

They do not:
- promote generated imagery into physical truth;
- infer hidden regions as observed facts;
- create causal proof;
- grant authority.

## GMS boundary

The F17 adapter consumes the existing Brody 21D cognitive point cloud and represents semantic drift/trajectory.

It does not rebuild the full SENS/GMS intelligence and does not claim:

`distance = truth`

or

`trajectory = causality`.

## Regression basis

F24 verified code SHA:

`accb5c0a0902c29de04ca59b56859e9324e611d9`

GitHub Actions run:

`37575196459`

Result:

```text
12556 passed
11 failed — historical baseline families
46 skipped
207 deselected
0 new F24 failures
```

The 11 remaining failures are not repaired in this freeze branch because they predate this first-world chain and are outside its scope.

## Machine-readable release boundary

See:

`release/premiere_mise_au_monde_release_candidate_v0.json`

This manifest is the bounded release claim surface for F25.

## Freeze rule

F25 can move from `RELEASE CANDIDATE` to `FROZEN` only if:
1. the release-manifest tests pass;
2. the complete regression introduces no new F12→F25 failure;
3. no supported claim exceeds the evidence already present in the repository;
4. the forbidden claim list remains explicit;
5. KX108_ONLY remains unchanged.

No feature work belongs in F25.

## F25 verification

- Verified code SHA: `afefb316f400473388967b22acbcabd91d08ac67`
- GitHub Actions run: `37575789814`
- Global result: `12562 passed / 11 failed / 46 skipped / 207 deselected`
- New F25 failures: `0`
- The 11 remaining failures match the historical baseline families already present before this release chain.

**Freeze verdict:** F25 `FROZEN`.
