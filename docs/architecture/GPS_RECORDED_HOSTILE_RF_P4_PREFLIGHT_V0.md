# GPS RECORDED HOSTILE RF — P4 PREFLIGHT V0

Status: AUDITED / NOT YET ELIGIBLE FOR P4 CLOSURE  
Branch: `feat/gps-recorded-hostile-p4-preflight-v0`  
Authority: `KX108_ONLY`

## Purpose

Audit and freeze the exact historical hostile-RF assets that P4 will reuse after P2/P3.

This preflight does not reopen PASS8 as a parallel architecture and does not reinterpret an old HOLD as hostile classification success.

## Reusable historical assets

Canonical historical family:
`hackathons/nativebuilder-gps-defense/rf_attack_benchmark/`

Retain:
- `dataset_manifest.json`
- `blind_input_manifest.json`
- `private_truth_manifest.json`
- `frozen_config_manifest.json`
- `label_leak_report.json`
- `pre_attack_baseline.json`
- `temporal_detection_report.json`
- `truth_alignment_report.json`
- `confusion_matrix.json`
- `metrics.json`
- `reproducibility_report.json`
- GNSS-SDR run logs and outputs
- FGI/GSRx runtime windows and results
- exact configuration hashes
- existing X108 receipts

These assets are evidence and benchmark history. They are not a proof that P4 already passed.

## Historical truth preserved

### Label isolation

The executed pipeline passed the label-leak check:
- truth manifest not read before decisions;
- opaque pipeline path;
- labels not exposed to receiver configuration;
- official attack onset used only after execution for interpretation.

This discipline is retained for P4.

### Official onset

Historical FGI-SpoofRepo truth:
- official hostile onset: `135 s`

The onset is scoring truth only. It must never be injected into the online decision path.

### Receiver blocker

The decisive historical blocker is:

`PRE_ATTACK_RECEIVER_FAILURE`

The attempted receiver configurations did not produce stable NAV/PVT before the official 135 s onset.

Observed historical facts include:
- tracking occurred;
- loss-of-lock occurred before the official onset;
- NAV message count remained zero in the pre-attack baseline attempts;
- PVT position count remained zero;
- repeated runs reproduced the receiver/no-PVT problem.

Therefore:

`loss of lock before 135 s != spoofing detection`

and:

`X108 HOLD != hostile-classification true positive`

### Metrics boundary

Historical state:
- TP/TN/FP/FN: not computed;
- detection rate: not computed;
- false positive rate: not computed;
- false negative rate: not computed;
- detection delay: not computed;
- drift before detection: not computed;
- confusion matrix: not validly populated.

The old benchmark must remain fail-closed.

## P4 entry conditions

P4 implementation/closure may start only after the following are available:

1. P2 has a real passive GNSS capture with a verified receiver/config binding.
2. P3 has a genuinely independent physical corroboration source.
3. The recorded FGI receiver path produces an accepted pre-attack baseline before 135 s.
4. The same frozen receiver/configuration family is used across the evaluated pre/post windows unless a change is explicitly versioned and justified.
5. NAV/PVT or another explicitly justified evaluable trajectory output exists for scoring.
6. Official onset/truth remains inaccessible to the online classification path.
7. Repeated runs are reproducible enough to support benchmark scoring.

No arbitrary success threshold is introduced here.

## Search-before-build result

Do not rebuild:
- FGI corpus ingestion;
- GNSS-SDR historical execution plumbing;
- GSRx compatibility work;
- blind input manifest discipline;
- label leak report;
- truth-alignment artifacts;
- old receipt plumbing.

P4 should connect these assets to the current canonical Physical Signal / Evidence / GPS closure contracts.

## What P4 must add

Only the missing closure:

```text
accepted pre-attack receiver baseline
→ stable evaluable trajectory/NAV/PVT
→ recorded hostile window
→ deterministic attack-classification output
→ blind post-run truth scoring
→ reproducible P4 receipt bundle
```

The attack classifier must remain distinct from the governance verdict.

`hostile classification != HOLD/BLOCK/ACT`

KX108 remains the only decision authority.

## Relationship to P5/P6

P4 closes only recorded hostile classification evidence.

It does not by itself prove causal attribution.

After P4:
- P5 evaluates causal attribution;
- P6 populates TP/TN/FP/FN and benchmark metrics.

## Current canonical state

```text
P1  receiver readiness                 VERIFIED
P2  real passive capture               RUNTIME READY / PHYSICAL PENDING
P3  independent corroboration          CONTRACT READY / BLOCKED BY P2
P4  recorded hostile RF closure        PREFLIGHT AUDITED / BLOCKED BY P2+P3+BASELINE
```

The historical RF corpus is therefore preserved and ready for reuse, but no P4 PASS is claimed.
