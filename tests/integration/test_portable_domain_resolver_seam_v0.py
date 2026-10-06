from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from periphery.common import ActionCandidate
from scripts.providers.canonical_runtime_receipt_flow_v1 import CanonicalRuntimeReceiptFlow
from sigma.contracts import DomainAggregate
from sigma.guard import GuardX108

from scripts.obsidia_governed_runtime_cycle_v1 import (
    EXECUTION_AUTHORIZED,
    REFUSED_GATE_NOT_ALLOW,
    REFUSED_UNSUPPORTED_DOMAIN,
    is_supported_domain,
    resolve_domain_pipeline,
    run_governed_feedback_cycle,
    run_governed_runtime_cycle,
)


AGENT_ID = "DATA_PURITY_AGENT"


@dataclass(frozen=True)
class _PortableDomainValue:
    value: str


class _AdministrationExtensionResolver:
    def __init__(self):
        self.support_checks: list[str] = []
        self.resolve_calls: list[str] = []

    def is_supported_domain(self, domain: str) -> bool:
        self.support_checks.append(domain)
        return domain == "administration"

    def resolve_domain_pipeline(self, domain: str):
        self.resolve_calls.append(domain)
        if domain != "administration":
            raise KeyError(domain)

        def _pipeline(state, packet):
            packet.assert_non_sovereign()

            aggregate = DomainAggregate(
                domain=_PortableDomainValue("administration"),
                market_verdict="HOLD",
                confidence=float(state.get("confidence", 0.90)),
                contradictions=list(state.get("contradictions", ()))
                + list(packet.contradictions),
                unknowns=list(state.get("unknowns", ())) + list(packet.unknowns),
                risk_flags=list(state.get("risk_flags", ())) + list(packet.risk_flags),
                evidence_refs=list(state.get("evidence_refs", ()))
                + list(packet.evidence_refs),
                agent_votes=[],
                extra_metrics={
                    "source": "F25_TEST_EXTENSION",
                    "extension_can_decide": False,
                    "extension_can_act": False,
                },
            )
            return GuardX108().decide(aggregate)

        return _pipeline


class _ShadowAttemptResolver:
    def __init__(self):
        self.support_checks = 0
        self.resolve_calls = 0

    def is_supported_domain(self, domain: str) -> bool:
        self.support_checks += 1
        return True

    def resolve_domain_pipeline(self, domain: str):
        self.resolve_calls += 1
        raise AssertionError("extension must not shadow canonical domain")


class _CountingProvider:
    def __init__(self):
        self.invocations = 0
        self.runtime_id = "runtime-f25-administration"

    def __call__(self, **kwargs):
        self.invocations += 1
        return {
            "runtime_id": self.runtime_id,
            "provider": "administration_provider",
        }


@pytest.fixture
def rig(tmp_path):
    flow = CanonicalRuntimeReceiptFlow()
    provider = _CountingProvider()
    flow.register_provider("administration_provider", provider)
    return {
        "flow": flow,
        "provider": provider,
        "ctx_dir": tmp_path / "agent_contexts",
        "dec_dir": tmp_path / "kx108_decisions",
    }


def _action(action_id: str, domain: str = "administration") -> ActionCandidate:
    return ActionCandidate(
        action_id=action_id,
        domain=domain,
        actor_id="f25",
        intent="inspect",
        action_type="analysis",
        irreversible=False,
        timestamp_plan="",
        payload={
            "freshness_score": 1.0,
            "source_count": 2,
            "clean_json_ready": True,
            "critical": False,
        },
    )


def _state(**overrides):
    state = {
        "confidence": 0.90,
        "unknowns": (),
        "contradictions": (),
        "risk_flags": (),
        "evidence_refs": ("admin:e1",),
    }
    state.update(overrides)
    return state


def _run(rig, resolver, state, action_id):
    return run_governed_runtime_cycle(
        AGENT_ID,
        _action(action_id),
        state,
        execution_surface=rig["flow"],
        mission_id=f"mission-{action_id}",
        provider_id="administration_provider",
        capability="analysis",
        execution_payload={"domain": "administration"},
        agent_context_store_dir=rig["ctx_dir"],
        decision_store_dir=rig["dec_dir"],
        domain_extension_resolver=resolver,
    )


def test_default_unknown_domain_behavior_is_unchanged(rig):
    result = run_governed_runtime_cycle(
        AGENT_ID,
        _action("default-unknown", domain="administration"),
        _state(),
        execution_surface=rig["flow"],
        mission_id="mission-default-unknown",
        provider_id="administration_provider",
        capability="analysis",
        agent_context_store_dir=rig["ctx_dir"],
        decision_store_dir=rig["dec_dir"],
    )

    assert is_supported_domain("administration") is False
    assert result.execution_authorization_reason.startswith(REFUSED_UNSUPPORTED_DOMAIN)
    assert result.decision_rendered is False
    assert result.decision_record_persisted is False
    assert result.execution_authorized is False
    assert rig["provider"].invocations == 0


def test_canonical_domain_cannot_be_shadowed_by_extension():
    resolver = _ShadowAttemptResolver()

    canonical = resolve_domain_pipeline("bank")
    from scripts.obsidia_governed_runtime_cycle_v1 import (
        _resolve_domain_pipeline_with_extension,
    )

    resolved = _resolve_domain_pipeline_with_extension("bank", resolver)
    assert resolved is canonical
    assert resolver.support_checks == 0
    assert resolver.resolve_calls == 0


def test_first_class_extension_full_cycle_allow(rig):
    resolver = _AdministrationExtensionResolver()
    result = _run(rig, resolver, _state(), "admin-allow")

    assert result.domain == "administration"
    assert result.x108_gate == "ALLOW"
    assert result.decision_rendered is True
    assert result.agent_pre_execution_context_verified is True
    assert result.decision_record_persisted is True
    assert result.decision_record_verified is True
    assert result.replay_status == "PASS"
    assert result.execution_authorized is True
    assert result.execution_authorization_reason == EXECUTION_AUTHORIZED
    assert result.provider_invoked is True
    assert rig["provider"].invocations == 1
    assert result.receipt["status"] == "COMPLETED"
    result.assert_non_sovereign()


def test_first_class_extension_hold_never_executes(rig):
    resolver = _AdministrationExtensionResolver()
    result = _run(
        rig,
        resolver,
        _state(unknowns=("u1", "u2")),
        "admin-hold",
    )

    assert result.x108_gate == "HOLD"
    assert result.decision_record_verified is True
    assert result.execution_authorized is False
    assert result.execution_authorization_reason == REFUSED_GATE_NOT_ALLOW
    assert result.provider_invoked is False
    assert rig["provider"].invocations == 0
    assert result.receipt is None


def test_first_class_extension_block_never_executes(rig):
    resolver = _AdministrationExtensionResolver()
    result = _run(
        rig,
        resolver,
        _state(contradictions=("c1", "c2")),
        "admin-block",
    )

    assert result.x108_gate == "BLOCK"
    assert result.decision_record_verified is True
    assert result.execution_authorized is False
    assert result.provider_invoked is False
    assert rig["provider"].invocations == 0


def test_feedback_cycle_propagates_extension_resolver(rig):
    resolver = _AdministrationExtensionResolver()

    t0 = _run(rig, resolver, _state(), "admin-feedback-t0")
    assert t0.x108_gate == "ALLOW"
    assert t0.provider_invoked is True

    t1 = run_governed_feedback_cycle(
        t0,
        _action("admin-feedback-t1"),
        _state(unknowns=("u1", "u2")),
        execution_surface=rig["flow"],
        mission_id="mission-admin-feedback-t1",
        provider_id="administration_provider",
        capability="analysis",
        execution_payload={"domain": "administration"},
        agent_context_store_dir=rig["ctx_dir"],
        decision_store_dir=rig["dec_dir"],
        domain_extension_resolver=resolver,
    )

    assert t1.domain == "administration"
    assert t1.x108_gate == "HOLD"
    assert t1.decision_record_verified is True
    assert t1.execution_authorized is False
    assert t1.provider_invoked is False
    assert rig["provider"].invocations == 1


def test_invalid_extension_resolver_fails_closed(rig):
    class BadResolver:
        pass

    with pytest.raises(Exception, match="INVALID_DOMAIN_EXTENSION_RESOLVER"):
        _run(rig, BadResolver(), _state(), "bad-resolver")
