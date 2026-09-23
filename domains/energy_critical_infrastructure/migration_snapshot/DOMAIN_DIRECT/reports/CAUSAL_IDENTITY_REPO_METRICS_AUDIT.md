# CAUSAL IDENTITY REPO METRICS AUDIT

Status: AUDIT_DERIVED_DRAFT

Source audit:
.local_audits\CIC_FAST_RULES_AUDIT_20260613_013837\04_high_value_cic_sources.txt

Mapping:
registries/cic_metric_mapping_v0.yaml

## Confirmed metric families

- guard_metrics: REPO_CONFIRMED
- timing_metrics: REPO_CONFIRMED
- reversibility_metrics: REPO_CONFIRMED
- proof_metrics: REPO_CONFIRMED
- trace_metrics: REPO_CONFIRMED
- context_metrics: REPO_CONFIRMED
- score_threshold_metrics: REPO_CONFIRMED
- missing_data_metrics: REPO_CONFIRMED

## Partial metric families

- source_metrics: PARTIAL
- capacity_metrics: PARTIAL
- resource_metrics: PARTIAL
- behavior_metrics: PARTIAL
- path_metrics: PARTIAL
- projection_metrics: PARTIAL
- memory_metrics: PARTIAL

## Not found / not activated

- causal capacity formula: NEEDS_DOMAIN_CALIBRATION
- anomaly formula: NEEDS_DOMAIN_CALIBRATION
- NCP targeted fetch: MISSING / inactive
- scraping: MISSING / inactive
- kernel binding: MISSING / inactive

## Central rules

Invariant > Reversibilité > Score > Projection

A score cannot authorize what an invariant forbids.

Critical missing data on irreversible action triggers HOLD / BLOCK / REVIEW.

Memory is not sovereign.

Projection is not prediction.
