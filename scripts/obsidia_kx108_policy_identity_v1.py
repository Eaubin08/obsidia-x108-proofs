"""
obsidia_kx108_policy_identity_v1.py
===================================

Deterministic, read-only identity for the KX108 tooling_build policy surface.

This does not decide, authorize, execute, or mutate.  It fingerprints the
bounded source surface that currently feeds GuardX108 for tooling_build:
run_tooling_build_pipeline -> tooling agents -> meta agents ->
aggregate_tooling_build -> GuardX108.decide.

The coverage is intentionally declared as bounded, not complete: Python
runtime semantics, import resolution, and transitive base-class behavior are
not claimed as fully captured by this source fingerprint.
"""
from __future__ import annotations

import hashlib
import inspect
import json
from typing import Any

POLICY_IDENTITY_SCHEMA_VERSION = "KX108_POLICY_IDENTITY_V1"
POLICY_VERSION = "KX108_TOOLING_BUILD_POLICY_IDENTITY_V1"
POLICY_COVERAGE = "BOUNDED_SOURCE_FINGERPRINT"
POLICY_COVERAGE_COMPLETE = False
POLICY_UNCOVERED_SURFACE = (
    "PYTHON_INTERPRETER_SEMANTICS",
    "IMPORT_RESOLUTION_AND_DEPENDENCY_GRAPH",
    "UNFINGERPRINTED_BASE_CLASS_DYNAMIC_BEHAVIOR",
)
STATUS_MATCH = "MATCH"
STATUS_MISMATCH = "MISMATCH"
STATUS_UNAVAILABLE = "UNAVAILABLE"


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_json(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _source_component(name: str, obj: Any) -> dict[str, str]:
    try:
        source = inspect.getsource(obj)
    except (OSError, TypeError):
        source = repr(obj)
    return {
        "component_id": name,
        "source_sha256": _sha256_text(source),
    }


def _tooling_policy_components() -> list[dict[str, str]]:
    from sigma import aggregation, protocols
    from sigma import guard
    from sigma.contracts import AgentVote, CanonicalDecisionEnvelope, DomainAggregate, ToolingBuildState
    from sigma.domains import meta_agents, tooling_build_agents

    components: list[tuple[str, Any]] = [
        ("sigma.protocols.run_tooling_build_pipeline", protocols.run_tooling_build_pipeline),
        ("sigma.protocols._apply_meta_agents", protocols._apply_meta_agents),
        ("sigma.aggregation._common", aggregation._common),
        ("sigma.aggregation.aggregate_tooling_build", aggregation.aggregate_tooling_build),
        ("sigma.guard.GuardConfig", guard.GuardConfig),
        ("sigma.guard.GuardX108.decide", guard.GuardX108.decide),
        ("sigma.contracts.ToolingBuildState", ToolingBuildState),
        ("sigma.contracts.AgentVote", AgentVote),
        ("sigma.contracts.DomainAggregate", DomainAggregate),
        ("sigma.contracts.CanonicalDecisionEnvelope", CanonicalDecisionEnvelope),
        ("sigma.domains.tooling_build_agents.ScopeIntegrityAgent.evaluate", tooling_build_agents.ScopeIntegrityAgent.evaluate),
        ("sigma.domains.tooling_build_agents.TestGateAgent.evaluate", tooling_build_agents.TestGateAgent.evaluate),
        ("sigma.domains.tooling_build_agents.SessionIntegrityAgent.evaluate", tooling_build_agents.SessionIntegrityAgent.evaluate),
        ("sigma.domains.tooling_build_agents.CommitGuardAgent.evaluate", tooling_build_agents.CommitGuardAgent.evaluate),
        ("sigma.domains.tooling_build_agents.build_tooling_build_agents", tooling_build_agents.build_tooling_build_agents),
        ("sigma.domains.meta_agents.UnknownsAgent.evaluate", meta_agents.UnknownsAgent.evaluate),
        ("sigma.domains.meta_agents.ConflictResolutionAgent.evaluate", meta_agents.ConflictResolutionAgent.evaluate),
        ("sigma.domains.meta_agents.PolicyScopeAgent.evaluate", meta_agents.PolicyScopeAgent.evaluate),
        ("sigma.domains.meta_agents.TicketReadinessAgent.evaluate", meta_agents.TicketReadinessAgent.evaluate),
        ("sigma.domains.meta_agents.TraceIntegrityAgent.evaluate", meta_agents.TraceIntegrityAgent.evaluate),
        ("sigma.domains.meta_agents.AttestationReadinessAgent.evaluate", meta_agents.AttestationReadinessAgent.evaluate),
        ("sigma.domains.meta_agents.HumanOverrideEligibilityAgent.evaluate", meta_agents.HumanOverrideEligibilityAgent.evaluate),
        ("sigma.domains.meta_agents.SeverityClassifierAgent.evaluate", meta_agents.SeverityClassifierAgent.evaluate),
        ("sigma.domains.meta_agents.ReplayConsistencyAgent.evaluate", meta_agents.ReplayConsistencyAgent.evaluate),
        ("sigma.domains.meta_agents.ProofConsistencyAgent.evaluate", meta_agents.ProofConsistencyAgent.evaluate),
        ("sigma.domains.meta_agents.build_meta_agents", meta_agents.build_meta_agents),
    ]
    return [_source_component(name, obj) for name, obj in components]


def compute_policy_content_hash(*, components: list[dict[str, str]], coverage: str, uncovered_surface: list[str]) -> str:
    return _sha256_json(
        {
            "schema_version": POLICY_IDENTITY_SCHEMA_VERSION,
            "policy_version": POLICY_VERSION,
            "coverage": coverage,
            "coverage_complete": POLICY_COVERAGE_COMPLETE,
            "components": components,
            "uncovered_surface": uncovered_surface,
        }
    )


def build_tooling_build_policy_identity() -> dict[str, Any]:
    components = _tooling_policy_components()
    uncovered = list(POLICY_UNCOVERED_SURFACE)
    return {
        "schema_version": POLICY_IDENTITY_SCHEMA_VERSION,
        "policy_version": POLICY_VERSION,
        "policy_content_hash": compute_policy_content_hash(
            components=components,
            coverage=POLICY_COVERAGE,
            uncovered_surface=uncovered,
        ),
        "coverage": POLICY_COVERAGE,
        "coverage_complete": POLICY_COVERAGE_COMPLETE,
        "components": components,
        "uncovered_surface": uncovered,
        "decision_authority": "KX108_ONLY",
    }


def verify_policy_identity(identity: Any) -> dict[str, Any]:
    if not isinstance(identity, dict):
        return {"status": STATUS_UNAVAILABLE, "reason": "KX108_POLICY_IDENTITY_MISSING"}
    if identity.get("schema_version") != POLICY_IDENTITY_SCHEMA_VERSION:
        return {"status": STATUS_MISMATCH, "reason": "KX108_POLICY_IDENTITY_SCHEMA_MISMATCH"}
    if identity.get("policy_version") != POLICY_VERSION:
        return {"status": STATUS_UNAVAILABLE, "reason": "KX108_POLICY_HISTORICAL_VERSION_UNAVAILABLE"}
    components = identity.get("components")
    if not isinstance(components, list) or not components:
        return {"status": STATUS_MISMATCH, "reason": "KX108_POLICY_COMPONENTS_MISSING"}
    uncovered = identity.get("uncovered_surface")
    if not isinstance(uncovered, list):
        return {"status": STATUS_MISMATCH, "reason": "KX108_POLICY_UNCOVERED_SURFACE_MISSING"}
    expected = compute_policy_content_hash(
        components=components,
        coverage=str(identity.get("coverage") or ""),
        uncovered_surface=[str(item) for item in uncovered],
    )
    if identity.get("policy_content_hash") != expected:
        return {"status": STATUS_MISMATCH, "reason": "KX108_POLICY_CONTENT_HASH_MISMATCH"}
    current = build_tooling_build_policy_identity()
    if identity.get("policy_content_hash") != current.get("policy_content_hash"):
        return {"status": STATUS_MISMATCH, "reason": "KX108_POLICY_CURRENT_VERSION_CONTENT_MISMATCH"}
    return {
        "status": STATUS_MATCH,
        "reason": "KX108_POLICY_IDENTITY_MATCH",
        "coverage": identity.get("coverage"),
        "coverage_complete": identity.get("coverage_complete") is True,
        "policy_version": identity.get("policy_version"),
        "policy_content_hash": identity.get("policy_content_hash"),
    }
