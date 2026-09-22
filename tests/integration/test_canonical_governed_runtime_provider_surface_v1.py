"""
R7-H — the real internal providers traverse the SAME governed rail.

R6 proved the chain with a local sandbox handler. This suite proves the
rail is not limited to a test double: the real Brody and Obsidure runtime
flow adapters, already shipped under scripts/providers/, execute behind the
same verified KX108 ALLOW, through the same CanonicalExecutionFlow, and
produce the same sealed envelope and terminal receipt.

Provider classification observed here:

    brody_runtime_flow_adapter_v1     INTERNAL_SAFE_EXECUTABLE
    obsidure_runtime_flow_adapter_v1  INTERNAL_SAFE_EXECUTABLE
    local sandbox handlers            SANDBOX_ONLY
    world action bus / gateway        EXTERNAL_CONSENT_REQUIRED (not activated)

Both real adapters are pure: they compute a result and a runtime id, with
no filesystem write, no network call and no authority flag set.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (
    str(_REPO_ROOT),
    str(_REPO_ROOT / "scripts"),
    str(Path(__file__).resolve().parent),
):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import obsidia_kx108_decision_store as DS  # noqa: E402
from obsidia_governed_runtime_cycle_v1 import (  # noqa: E402
    EXECUTION_AUTHORIZED,
    run_governed_runtime_cycle,
)
from scripts.providers.brody_runtime_flow_adapter_v1 import (  # noqa: E402
    BrodyRuntimeFlowAdapter,
)
from scripts.providers.canonical_runtime_receipt_flow_v1 import (  # noqa: E402
    CanonicalRuntimeReceiptFlow,
)
from scripts.providers.obsidure_runtime_flow_adapter_v1 import (  # noqa: E402
    ObsidureRuntimeFlowAdapter,
)
from _r7_domain_fixtures import action_for, bank_allow, bank_block  # noqa: E402

AGENT_ID = "DATA_PURITY_AGENT"


class BrodyHandler:
    """Routes the canonical call into the real Brody flow adapter."""

    provider_id = "brody"

    def __init__(self):
        self.adapter = BrodyRuntimeFlowAdapter()
        self.invocations = 0
        self.last = None

    def __call__(self, **kwargs):
        self.invocations += 1
        self.last = self.adapter.execute_flow(
            mission_id=kwargs.get("mission_id", ""),
            capability=kwargs.get("capability", ""),
            payload=dict(kwargs.get("payload") or {}),
        )
        return self.last


class ObsidureHandler:
    """Routes the canonical call into the real Obsidure flow adapter."""

    provider_id = "obsidure"

    def __init__(self):
        self.adapter = ObsidureRuntimeFlowAdapter()
        self.invocations = 0
        self.last = None

    def __call__(self, **kwargs):
        self.invocations += 1
        payload = dict(kwargs.get("payload") or {})
        self.last = self.adapter.execute_flow(
            mission_id=kwargs.get("mission_id", ""),
            capability=kwargs.get("capability", ""),
            proof_target=payload.get("proof_target", "r7-proof-target"),
            payload=payload,
        )
        return self.last


@pytest.fixture
def rig(tmp_path):
    flow = CanonicalRuntimeReceiptFlow()
    handlers = {"brody": BrodyHandler(), "obsidure": ObsidureHandler()}
    for provider_id, handler in handlers.items():
        flow.register_provider(provider_id, handler)
    return {
        "flow": flow,
        "handlers": handlers,
        "ctx_dir": tmp_path / "agent_contexts",
        "dec_dir": tmp_path / "kx108_decisions",
    }


def _run(rig, provider_id, state, action_id, capability="analysis"):
    return run_governed_runtime_cycle(
        AGENT_ID,
        action_for("bank", action_id),
        state,
        execution_surface=rig["flow"],
        mission_id=f"mission-{action_id}",
        provider_id=provider_id,
        capability=capability,
        execution_payload={"proof_target": "r7-proof-target", "scope": "bounded"},
        agent_context_store_dir=rig["ctx_dir"],
        decision_store_dir=rig["dec_dir"],
    )


@pytest.mark.parametrize("provider_id", ["brody", "obsidure"])
def test_real_provider_executes_only_behind_a_verified_allow(rig, provider_id):
    handler = rig["handlers"][provider_id]
    result = _run(rig, provider_id, bank_allow(), f"r7_real_{provider_id}")

    assert result.x108_gate == "ALLOW"
    assert result.decision_record_verified is True
    assert result.execution_plan_binding_verified is True
    assert result.execution_authorization_reason == EXECUTION_AUTHORIZED

    assert handler.invocations == 1
    assert result.flow_status == "COMPLETED"
    assert result.envelope_status == "SEALED"
    assert result.runtime_id == handler.last["runtime_id"]
    assert result.runtime_id.startswith(provider_id)

    assert result.receipt["status"] == "COMPLETED"
    assert result.receipt["result_ref"] == result.runtime_id
    assert result.receipt["provider_id"] == provider_id


@pytest.mark.parametrize("provider_id", ["brody", "obsidure"])
def test_real_provider_is_never_reached_on_a_refusal(rig, provider_id):
    handler = rig["handlers"][provider_id]
    result = _run(rig, provider_id, bank_block(), f"r7_real_block_{provider_id}")

    assert result.x108_gate == "BLOCK"
    assert result.decision_record_verified is True
    assert result.execution_authorized is False
    assert handler.invocations == 0
    assert result.receipt is None


@pytest.mark.parametrize("provider_id", ["brody", "obsidure"])
def test_real_provider_declares_no_authority(rig, provider_id):
    handler = rig["handlers"][provider_id]
    _run(rig, provider_id, bank_allow(), f"r7_real_auth_{provider_id}")

    output = handler.last
    assert output["decision_authority"] is False
    assert output["execution_authority"] is False
    assert output["memory_write"] is False
    assert output["kernel_mutation"] is False
    assert output["emits_act"] is False


def test_both_real_providers_coexist_on_one_runtime(rig):
    brody = _run(rig, "brody", bank_allow(), "r7_coexist_brody")
    obsidure = _run(rig, "obsidure", bank_allow(), "r7_coexist_obsidure")

    assert rig["handlers"]["brody"].invocations == 1
    assert rig["handlers"]["obsidure"].invocations == 1

    assert brody.runtime_id != obsidure.runtime_id
    assert brody.decision_record_id != obsidure.decision_record_id
    assert brody.agent_pre_execution_context_id != (
        obsidure.agent_pre_execution_context_id
    )
    assert brody.receipt["provider_id"] == "brody"
    assert obsidure.receipt["provider_id"] == "obsidure"

    for cycle in (brody, obsidure):
        stored = DS.load_kx108_decision_record(cycle.decision_record_id, rig["dec_dir"])
        ok, reason = DS.verify_kx108_decision_record(stored)
        assert ok is True, reason
        cycle.assert_non_sovereign()


def test_real_provider_execution_is_bound_to_its_own_plan(rig):
    """A record produced for brody does not describe the obsidure execution."""
    brody = _run(rig, "brody", bank_allow(), "r7_bind_brody")
    obsidure = _run(rig, "obsidure", bank_allow(), "r7_bind_obsidure")

    brody_rec = DS.load_kx108_decision_record(brody.decision_record_id, rig["dec_dir"])
    obsidure_rec = DS.load_kx108_decision_record(
        obsidure.decision_record_id, rig["dec_dir"]
    )

    assert brody_rec["agent_execution_plan_digest"] == brody.execution_plan_digest
    assert obsidure_rec["agent_execution_plan_digest"] == obsidure.execution_plan_digest
    assert brody_rec["agent_execution_plan_digest"] != (
        obsidure_rec["agent_execution_plan_digest"]
    )


def test_real_providers_write_nothing_outside_the_canonical_stores(rig, tmp_path, monkeypatch):
    """The adapters are pure: running one creates no stray file."""
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    monkeypatch.chdir(scratch)

    _run(rig, "brody", bank_allow(), "r7_pure_brody")

    assert list(scratch.iterdir()) == []
