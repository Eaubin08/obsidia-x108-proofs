"""ClosureCertificate — audit-only record of why a local closure was safe.

Never written to /output/results.json, never appended to answer text,
never a source of authority. Deterministic serialization for audit
sidecars only.
"""
from __future__ import annotations

import json


def build_closure_certificate(
    solver_family: str,
    semantic_signature: str,
    derivation_steps: list[str],
    checks_passed: list[str],
    entities: list[str] | None = None,
    quantities: list[str] | None = None,
    constraints: list[str] | None = None,
    unknowns: list[str] | None = None,
    contradictions: list[str] | None = None,
    confidence: float = 1.0,
) -> dict:
    cert = {
        "solver_family": solver_family,
        "semantic_signature": semantic_signature,
        "entities": sorted(entities or []),
        "quantities": sorted(quantities or []),
        "constraints": sorted(constraints or []),
        "derivation_steps": list(derivation_steps),
        "validation_checks": sorted(checks_passed),
        "unknowns": sorted(unknowns or []),
        "contradictions": sorted(contradictions or []),
        "confidence": confidence,
        "closure_safe": not (unknowns or contradictions),
    }
    # Deterministic round-trip guard: the certificate must always serialize.
    json.dumps(cert, sort_keys=True)
    return cert
