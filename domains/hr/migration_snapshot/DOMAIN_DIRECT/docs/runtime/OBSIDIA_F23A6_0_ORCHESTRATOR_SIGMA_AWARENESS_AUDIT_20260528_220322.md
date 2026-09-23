# OBSIDIA F23A6.0 — ORCHESTRATOR SIGMA AWARENESS AUDIT

Mode: AUDIT_ONLY_NO_PATCH
Commit: NO
Tag: NO
Freeze: NO

HEAD: `587018a`
Tags on HEAD: `BRODY_F23A5_AGENT_GOVERNANCE_AUDIT_PALIER_20260528`

## Summary

- Candidate files: 9
- Existing files: 9
- Missing files: 0
- Sigma-aware files: 2
- Sigma-blind files: 7
- Danger count: 0
- Monitoring status: `SIGMA_AWARE_CONFIRMED`

## Sigma-aware files

- `apps/obsidia_api/routes/brody_monitoring.py`
  - L42 `evaluate_sigma_domain` — from sigma.evaluate import evaluate_sigma_domain
  - L42 `sigma.evaluate` — from sigma.evaluate import evaluate_sigma_domain
  - L150 `domain_sigma_envelope` — - domain_sigma_envelope from evaluate_sigma_domain(domain, state.__dict__)
  - L150 `evaluate_sigma_domain` — - domain_sigma_envelope from evaluate_sigma_domain(domain, state.__dict__)
  - L157 `domain_sigma_envelope` — domain_sigma_envelope = evaluate_sigma_domain(domain, state_payload)
  - L157 `evaluate_sigma_domain` — domain_sigma_envelope = evaluate_sigma_domain(domain, state_payload)
  - L163 `domain_sigma_envelope` — "domain_sigma_envelope": domain_sigma_envelope,
  - L164 `domain_sigma_attached` — "domain_sigma_attached": True,
- `sigma/evaluate.py`
  - L103 `SIGMA_UNIFIED_DISPATCHER` — "source": "SIGMA_UNIFIED_DISPATCHER_V1",
  - L104 `READONLY_DOMAIN_SIGMA_ENVELOPE` — "mode": "READONLY_DOMAIN_SIGMA_ENVELOPE",
  - L105 `domain_sigma_envelope` — "domain_sigma_envelope": True,
  - L109 `evaluate_sigma_domain` — def evaluate_sigma_domain(
  - L135 `SIGMA_UNIFIED_DISPATCHER` — "source": "SIGMA_UNIFIED_DISPATCHER_V1",
  - L136 `READONLY_DOMAIN_SIGMA_ENVELOPE` — "mode": "READONLY_DOMAIN_SIGMA_ENVELOPE",
  - L137 `domain_sigma_envelope` — "domain_sigma_envelope": True,
  - L150 `evaluate_sigma_domain` — return evaluate_sigma_domain(domain, payload)

## Sigma-blind files

- `apps/obsidia_api/brody_operator_view_packet.py`
- `apps/obsidia_api/brody_runtime_context_adapter.py`
- `apps/obsidia_api/brody_automation_orchestrator.py`
- `apps/obsidia_api/brody_operator_loop_adapter.py`
- `apps/obsidia_api/routes/periphery_ops.py`
- `apps/obsidia_api/routes/brody.py`
- `periphery/sigma_bridge.py`

## Gaps

- `G08` — Brody operator view packet is blind to Sigma envelope.
  - target_phase: F23A6.1
  - target_file: `apps/obsidia_api/brody_operator_view_packet.py`
  - patch_now: False
- `G08B` — Runtime context adapter does not carry domain_sigma_envelope.
  - target_phase: F23A6.1
  - target_file: `apps/obsidia_api/brody_runtime_context_adapter.py`
  - patch_now: False
- `G05` — No explicit /api/periphery/sigma/evaluate route detected.
  - target_phase: F23A6.2
  - target_file: `apps/obsidia_api/routes/periphery_ops.py`
  - patch_now: False

## Boundary

```text
DECISION_AUTHORITY=KX108_ONLY
readonly=true
emits_act=false
kernel_mutation=false
x108_mutation=false
```

## Next

F23A6.1_DOMAIN_SIGMA_ENVELOPE_IN_BRODY

## Status

F23A6_0_ORCHESTRATOR_SIGMA_AWARENESS_AUDIT_DONE
