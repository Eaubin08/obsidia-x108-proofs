# Education / Bias / Language / Ingestion — Implementation Report

**Date:** 2026-05-19

## Modules Created

### Education Score
- File: `periphery/education/education_score.py`
- Formula: `Score = w1*S + w2*C + w3*R + w4*F + w5*D`
  - w1=0.30 (skill), w2=0.20 (comprehension), w3=0.20 (retention), w4=0.15 (fluency), w5=0.15 (depth)
- Levels: ADVANCED (≥0.85), INTERMEDIATE (≥0.65), BASIC (≥0.40), BELOW_THRESHOLD (<0.40)
- Score clamped to [0.0, 1.0]

### Bias Gate
- File: `periphery/bias/bias_gate.py`
- Rule: Unvalidated bias → `gate=HOLD`, `blocked=True` always
- File: `periphery/bias/bias_trace.py` — audit trail for bias detection

### Language Router
- File: `periphery/language/language_router.py`
- Detects: "fr" (bonjour, monde, etc.), "en" (hello, world, etc.)
- Authority claim detection: "admin:", "root:", "system:", "sudo:", "authority:" → `routable=False`, `reason=AUTHORITY_NOT_ROUTABLE`

### Document Ingestion
- File: `periphery/ingestion/document_ingestion_pipeline.py` — IngestedDocument with hash verification
- File: `periphery/ingestion/source_classifier.py` — TRUSTED/UNTRUSTED/UNCLASSIFIED
- File: `periphery/ingestion/hash_ingestion.py` — SHA-256 hash + verify

### Context / X108 Ingress
- File: `periphery/context/context_packet_builder.py` — ContextPacket (can_decide=False always)
- File: `periphery/x108_ingress/readonly_context_ingress.py` — can_emit_act=False, can_write_memory=False

## Test Coverage

- `tests/periphery/test_education_score.py` — 4 tests
- `tests/periphery/test_bias_gate_blocks_unvalidated_bias.py` — 5 tests
- `tests/periphery/test_language_router_boundary_preserved.py` — 4 tests
- `tests/periphery/test_document_ingestion_requires_hash.py` — 4 tests
- `tests/periphery/test_x108_readonly_context_ingress_no_act.py` — 4 tests

## Key Invariants

- No bias module can call X-108 directly — only produces gate recommendations
- Language router never modifies memory
- Document ingestion requires hash verification before acceptance
- Context packets: `can_decide=False` always
