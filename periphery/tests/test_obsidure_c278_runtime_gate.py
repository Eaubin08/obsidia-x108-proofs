from __future__ import annotations

from dataclasses import dataclass

from periphery.agents import agent_obsidure as agent_module
from periphery.agents import obsidure_repair_bridge as bridge
from periphery.agents.agent_obsidure import AgentObsidure
from periphery.agents.obsidure_repair_contract import (
    REPAIR_BOUNDARY,
    RepairCandidateFile,
    RepairProposal,
    RepairRequest,
)
from periphery.language.proposal_meaning_validator import (
    EVIDENCE_CONTINUOUS,
    EVIDENCE_DIVERGENT,
    EVIDENCE_INCOMPLETE,
    EVIDENCE_NOT_APPLICABLE,
)


TARGET = "periphery/agents/c278_runtime_probe.py"
BASE_SHA = "a" * 64

BEFORE = """\
def run():
    return Widget()
"""

AFTER = """\
from periphery.helpers import Widget

def run():
    return Widget()
"""


@dataclass
class _FakeVerdict:
    status: str = "PASS"

    @property
    def compiled_files(self):
        return [TARGET]

    @property
    def errors(self):
        return []

    def to_dict(self):
        return {
            "verdict_id": "rv_gate",
            "request_id": "rr_gate",
            "proposal_id": "rp_gate",
            "status": self.status,
            "compiled_files": [TARGET],
            "errors": [],
        }


def _request(**overrides):
    data = {
        "request_id": "rr_gate",
        "objective": "restore the unresolved Widget dependency",
        "failure_mode": "NO_ARTIFACT_PRODUCED",
        "summary": "Widget dependency is required by run",
        "repo_targets": [TARGET],
        "target_excerpts": {TARGET: BEFORE},
        "tests_hint": [],
        "boundary": dict(REPAIR_BOUNDARY),
    }
    data.update(overrides)
    return RepairRequest(**data)


def _proposal(**overrides):
    data = {
        "proposal_id": "rp_gate",
        "request_id": "rr_gate",
        "engine": "R3C_TEST",
        "rationale": (
            "Restore the local dependency required by the requested target."
        ),
        "candidate_files": [
            RepairCandidateFile(
                path=TARGET,
                full_content=AFTER,
                change_kind="MODIFY",
                base_sha256=BASE_SHA,
                rationale="Import the Widget dependency used by run.",
            )
        ],
        "tests_to_run": [],
        "confidence": "HIGH",
        "boundary": dict(REPAIR_BOUNDARY),
    }
    data.update(overrides)
    return RepairProposal(**data)


def _agent(tmp_path, monkeypatch):
    monkeypatch.setattr(
        agent_module,
        "PROPOSALS_DIR",
        tmp_path / "proposals",
    )
    return AgentObsidure(
        api_base="http://127.0.0.1:1",
        verbose=False,
    )


def _install_fake_sandbox(monkeypatch):
    calls = []

    def fake_test_repair_proposal(
        proposal,
        request=None,
        run_tests=True,
        repo_root=None,
    ):
        calls.append({
            "proposal": proposal,
            "request": request,
            "run_tests": run_tests,
            "repo_root": repo_root,
        })
        return _FakeVerdict()

    monkeypatch.setattr(
        bridge,
        "test_repair_proposal",
        fake_test_repair_proposal,
    )

    monkeypatch.setattr(
        bridge,
        "resume_objective_from_verdict",
        lambda verdict, request: "",
    )

    return calls


def test_continuous_reaches_sandbox_exactly_once(
    tmp_path,
    monkeypatch,
):
    agent = _agent(tmp_path, monkeypatch)
    agent._last_repair_request = _request()

    calls = _install_fake_sandbox(monkeypatch)

    result = agent.evaluate_repair_proposal(
        _proposal(),
        run_tests=True,
    )

    assert result is not None
    assert result["status"] == "PASS"
    assert len(calls) == 1
    assert calls[0]["run_tests"] is True

    evidence = agent._last_proposal_meaning_validation
    assert evidence is not None
    assert evidence["evidence"] == EVIDENCE_CONTINUOUS
    assert evidence["request_id"] == "rr_gate"
    assert evidence["proposal_id"] == "rp_gate"

    assert evidence["readonly"] is True
    assert evidence["advisory_only"] is True
    assert evidence["allowed_to_decide"] is False
    assert evidence["allowed_to_act"] is False
    assert evidence["emits_act"] is False
    assert evidence["emits_verdict"] is False
    assert evidence["decision_authority"] == "KX108_ONLY"


def test_divergent_never_reaches_sandbox(
    tmp_path,
    monkeypatch,
):
    agent = _agent(tmp_path, monkeypatch)
    agent._last_repair_request = _request()

    calls = _install_fake_sandbox(monkeypatch)

    result = agent.evaluate_repair_proposal(
        _proposal(request_id="rr_forged"),
        run_tests=True,
    )

    assert result is None
    assert calls == []
    assert (
        agent._last_proposal_meaning_validation["evidence"]
        == EVIDENCE_DIVERGENT
    )


def test_incomplete_never_reaches_sandbox(
    tmp_path,
    monkeypatch,
):
    agent = _agent(tmp_path, monkeypatch)
    agent._last_repair_request = _request()

    calls = _install_fake_sandbox(monkeypatch)

    result = agent.evaluate_repair_proposal(
        _proposal(
            candidate_files=[
                RepairCandidateFile(
                    path=TARGET,
                    full_content="",
                    change_kind="MODIFY",
                    base_sha256=BASE_SHA,
                    rationale="Widget dependency",
                )
            ],
        ),
        run_tests=True,
    )

    assert result is None
    assert calls == []
    assert (
        agent._last_proposal_meaning_validation["evidence"]
        == EVIDENCE_INCOMPLETE
    )


def test_not_applicable_never_reaches_sandbox(
    tmp_path,
    monkeypatch,
):
    agent = _agent(tmp_path, monkeypatch)
    agent._last_repair_request = _request()

    calls = _install_fake_sandbox(monkeypatch)

    result = agent.evaluate_repair_proposal(
        _proposal(proposal_id=""),
        run_tests=True,
    )

    assert result is None
    assert calls == []
    assert (
        agent._last_proposal_meaning_validation["evidence"]
        == EVIDENCE_NOT_APPLICABLE
    )


def test_missing_runtime_request_fails_closed(
    tmp_path,
    monkeypatch,
):
    agent = _agent(tmp_path, monkeypatch)
    assert agent._last_repair_request is None

    calls = _install_fake_sandbox(monkeypatch)

    result = agent.evaluate_repair_proposal(
        _proposal(),
        run_tests=True,
    )

    assert result is None
    assert calls == []
    assert (
        agent._last_proposal_meaning_validation["evidence"]
        == EVIDENCE_NOT_APPLICABLE
    )


def test_validator_exception_fails_closed_before_sandbox(
    tmp_path,
    monkeypatch,
):
    agent = _agent(tmp_path, monkeypatch)
    agent._last_repair_request = _request()

    calls = _install_fake_sandbox(monkeypatch)

    import periphery.language.proposal_meaning_validator as validator

    def boom(*, request, proposal):
        raise RuntimeError("c278 synthetic failure")

    monkeypatch.setattr(
        validator,
        "validate_proposal_meaning",
        boom,
    )

    result = agent.evaluate_repair_proposal(
        _proposal(),
        run_tests=True,
    )

    assert result is None
    assert calls == []

    # Never fabricate evidence when the sensor itself failed.
    assert agent._last_proposal_meaning_validation is None



def test_r3e1_runtime_snapshot_retains_exact_repair_chain(
    tmp_path,
    monkeypatch,
):
    agent = _agent(tmp_path, monkeypatch)

    request = _request()
    proposal = _proposal()

    agent._last_repair_request = request

    calls = _install_fake_sandbox(monkeypatch)

    returned = agent.evaluate_repair_proposal(
        proposal,
        run_tests=True,
    )

    assert returned is not None
    assert returned["status"] == "PASS"
    assert len(calls) == 1

    snap = agent.get_last_repair_runtime_evidence()

    assert (
        snap["status"]
        == "REPAIR_RUNTIME_EVIDENCE_SNAPSHOT"
    )

    assert snap["request"]["request_id"] == "rr_gate"
    assert snap["proposal"]["proposal_id"] == "rp_gate"

    assert (
        snap["c278_evidence"]["evidence"]
        == EVIDENCE_CONTINUOUS
    )

    assert snap["verdict"]["verdict_id"] == "rv_gate"
    assert snap["verdict"]["request_id"] == "rr_gate"
    assert snap["verdict"]["proposal_id"] == "rp_gate"
    assert snap["verdict"]["status"] == "PASS"

    # Exact runtime objects were retained.
    assert agent._last_repair_proposal is proposal
    assert agent._last_repair_verdict is not None

    # Snapshot is provenance only.
    assert snap["readonly"] is True
    assert snap["authority"] == "NON_SOVEREIGN"
    assert snap["decision_authority"] == "KX108_ONLY"

    assert snap["execution_authority"] is False
    assert snap["work_unit_bound"] is False
    assert snap["human_approval_present"] is False
    assert snap["kx108_invoked"] is False
    assert snap["target_mutated"] is False

    forbidden = {
        "work_unit",
        "execution_worktree_path",
        "main_worktree_path",
        "branch_name",
        "base_sha",
        "execution_authority_hash",
        "human_authorization_reference",
    }

    assert forbidden.isdisjoint(snap)


def test_r3e1_noncontinuous_retains_proposal_but_no_verdict(
    tmp_path,
    monkeypatch,
):
    agent = _agent(tmp_path, monkeypatch)
    agent._last_repair_request = _request()

    calls = _install_fake_sandbox(monkeypatch)

    proposal = _proposal(
        request_id="rr_forged",
    )

    returned = agent.evaluate_repair_proposal(
        proposal,
        run_tests=True,
    )

    assert returned is None
    assert calls == []

    snap = agent.get_last_repair_runtime_evidence()

    assert snap["proposal"]["proposal_id"] == "rp_gate"

    assert (
        snap["c278_evidence"]["evidence"]
        == EVIDENCE_DIVERGENT
    )

    assert snap["verdict"] is None
    assert agent._last_repair_verdict is None


def test_r3e1_new_evaluation_clears_stale_verdict_on_sensor_failure(
    tmp_path,
    monkeypatch,
):
    agent = _agent(tmp_path, monkeypatch)
    agent._last_repair_request = _request()

    _install_fake_sandbox(monkeypatch)

    first = agent.evaluate_repair_proposal(
        _proposal(),
        run_tests=True,
    )

    assert first is not None
    assert agent._last_repair_verdict is not None

    import periphery.language.proposal_meaning_validator as validator

    def boom(*, request, proposal):
        raise RuntimeError("synthetic sensor failure")

    monkeypatch.setattr(
        validator,
        "validate_proposal_meaning",
        boom,
    )

    second = agent.evaluate_repair_proposal(
        _proposal(),
        run_tests=True,
    )

    assert second is None

    snap = agent.get_last_repair_runtime_evidence()

    # The new proposal is retained because it was successfully normalized.
    assert snap["proposal"]["proposal_id"] == "rp_gate"

    # Stale downstream evidence from the previous evaluation is gone.
    assert snap["c278_evidence"] is None
    assert snap["verdict"] is None
