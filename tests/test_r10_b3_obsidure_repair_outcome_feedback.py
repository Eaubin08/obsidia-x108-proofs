from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS = WORKTREE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import obsidia_canonical_receipt_envelope_v1 as CRE
import obsidia_pc_capabilities_v2 as PC2
from periphery.agents import agent_obsidure as agent_module
from periphery.agents.agent_obsidure import AgentObsidure
from periphery.agents.obsidure_repair_contract import (
    ErrorContextRecord,
    REPAIR_BOUNDARY,
    RepairCandidateFile,
    RepairProposal,
    RepairRequest,
    RepairVerdict,
)


TARGET = "periphery/repair_target.py"
BEFORE = "value = 1\n"
AFTER = "value = 2\n"
REPO_REF = "obsidia-openjarvis-install-v0"


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)
    assert proc.returncode == 0, f"git {list(args)}: {proc.stderr}"
    return proc.stdout.strip()


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _world(tmp_path):
    main = tmp_path / "main"
    (main / "periphery").mkdir(parents=True)
    (main / TARGET).write_text(BEFORE, encoding="utf-8")
    _git(main, "init", "-q")
    _git(main, "config", "user.email", "r10b3@test.com")
    _git(main, "config", "user.name", "r10b3")
    _git(main, "config", "commit.gpgsign", "false")
    _git(main, "add", ".")
    _git(main, "commit", "-q", "-m", "seed")
    base_sha = _git(main, "rev-parse", "HEAD")
    exec_wt = tmp_path / "exec_wt"
    branch = "r10-b3-branch"
    _git(main, "worktree", "add", str(exec_wt), "-b", branch, base_sha)
    return {
        "main": main,
        "exec_wt": exec_wt,
        "base_sha": base_sha,
        "branch": branch,
        "stores": tmp_path / "stores",
    }


def _agent(tmp_path, monkeypatch):
    monkeypatch.setattr(agent_module, "PROPOSALS_DIR", tmp_path / "proposals")
    return AgentObsidure(api_base="http://127.0.0.1:1", verbose=False)


def _install_snapshot(agent: AgentObsidure, world, *, full_content=AFTER):
    request = RepairRequest(
        request_id="rr_r10b3",
        objective="repair target",
        failure_mode="BUILD_ERROR",
        summary="failure_mode=BUILD_ERROR",
        repo_targets=[TARGET],
        attempts_spent=2,
        error_contexts=[
            ErrorContextRecord(attempt=1, error_type="BUILD_ERROR", raw_details="first failure"),
            ErrorContextRecord(attempt=2, error_type="BUILD_ERROR", raw_details="second failure"),
        ],
        tests_hint=["repair-sandbox-verdict"],
        boundary=dict(REPAIR_BOUNDARY),
    )
    proposal = RepairProposal(
        proposal_id="rp_r10b3",
        request_id="rr_r10b3",
        rationale="repair target",
        candidate_files=[
            RepairCandidateFile(
                path=TARGET,
                full_content=full_content,
                change_kind="MODIFY",
                base_sha256=_sha_file(world["exec_wt"] / TARGET),
                rationale="fix value",
            )
        ],
        tests_to_run=["repair-sandbox-verdict"],
        confidence="HIGH",
        boundary=dict(REPAIR_BOUNDARY),
    )
    verdict = RepairVerdict(
        verdict_id="rv_r10b3",
        request_id="rr_r10b3",
        proposal_id="rp_r10b3",
        status="PASS",
        tested_artifacts=[{"path": TARGET, "sha256": _sha_text(full_content)}],
        tests_executed=[{"command": "pytest", "status": "PASS"}],
        boundary=dict(REPAIR_BOUNDARY),
    )
    agent._last_repair_request = request
    agent._last_repair_proposal = proposal
    agent._last_proposal_meaning_validation = {
        "evidence": "CONTINUOUS",
        "request_id": "rr_r10b3",
        "proposal_id": "rp_r10b3",
        "readonly": True,
        "advisory_only": True,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "decision_authority": "KX108_ONLY",
    }
    agent._last_repair_verdict = verdict
    return request, proposal, verdict


def _prepare(agent, world, **kwargs):
    return agent.prepare_last_validated_repair(
        base_commit_sha=world["base_sha"],
        repo_identity_ref=REPO_REF,
        execution_worktree_path=world["exec_wt"],
        main_worktree_path=world["main"],
        branch_name=world["branch"],
        stores_base_dir=world["stores"],
        session_id="r10-b3",
        **kwargs,
    )


def _execute(world, prepared):
    return PC2.pc_v2_apply_patch_execute(
        prepared["prepared_action"],
        prepared["prepared_action"]["execution_authority_hash"],
        "human-r10-b3-test-authorization",
        stores_base_dir=world["stores"],
        repo_root=world["exec_wt"],
        session_id="r10-b3",
    )


def _ingest(agent, world, prepared, action_evidence_id, **kwargs):
    return agent.ingest_repair_execution_outcome(
        action_evidence_id=action_evidence_id,
        stores_base_dir=world["stores"],
        prepared_repair=prepared,
        **kwargs,
    )


def _receipt_path(world, action_evidence_id):
    return world["stores"] / "receipts" / f"{action_evidence_id}.json"


def _receipt(world, action_evidence_id):
    return json.loads(_receipt_path(world, action_evidence_id).read_text(encoding="utf-8"))


def _write_receipt(world, action_evidence_id, envelope):
    _receipt_path(world, action_evidence_id).write_text(
        json.dumps(envelope, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _store_apply_patch_outcome(
    world,
    prepared,
    *,
    outcome=CRE.OUTCOME_SUCCESS,
    gate="ALLOW",
    physical=True,
    mutation=True,
    verified=True,
    dispatch=CRE.DISPATCH_POST_CONFIRMED,
    executor_status="INVOKED",
    execution_state="POSTCONDITION_CONFIRMED",
    after_changed=True,
    uncertainty="NONE",
    reason="",
):
    st = PC2._stores(world["stores"])
    pa = prepared["prepared_action"]
    v2id = pa["v2_exec_id"]
    child = pa["child_id"]
    eah = pa["execution_authority_hash"]
    descriptor_record = PC2._load_desc(v2id, st["v2exec"])
    assert descriptor_record is not None
    apr = PC2._approval(v2id, child, eah, pa["patch_sha256"])
    stored = PC2._E.store_approval_artifact(apr, st["approval"])
    assert stored["status"] in {"STORED", "IDEMPOTENT_ALREADY_EXISTS"}
    kx = PC2._kx108_pre(
        v2id,
        child,
        eah,
        apr["approval_id"],
        pa["desc_hash"],
        world["base_sha"],
        pa["manifest_hash"],
        pa["target_paths"],
        PC2.OP_APPLY_PATCH,
        kxpre=st["kxpre"],
    )
    if gate != "ALLOW":
        kx["x108_gate"] = gate
        kx["record"]["x108_gate"] = gate
        canonical = dict(kx["record"].get("canonical_envelope") or {})
        canonical["x108_gate"] = gate
        kx["record"]["canonical_envelope"] = canonical
        kx["record"]["decision_record_hash"] = PC2._DS.compute_kx108_decision_record_hash(kx["record"])
        PC2._DS.store_kx108_decision_record(kx["record"], store_dir=st["kxpre"])
    before = dict(pa["before_digests"])
    after = {
        rel: ("f" * 64 if after_changed else before[rel])
        for rel in pa["target_paths"]
    }
    runtime_status = PC2.EXECUTED_OK if outcome in {CRE.OUTCOME_SUCCESS, CRE.OUTCOME_NOOP} else PC2.EXECUTE_REJECTED
    runtime_receipt = PC2._rcpt(
        PC2._CAP_PATCH_EXECUTE,
        PC2.OP_APPLY_PATCH,
        runtime_status,
        "r10-b3",
        target_paths=pa["target_paths"],
        after_digests=after,
    )
    envelope, store_status = PC2._build_apply_patch_envelope(
        stores=st,
        v2id=v2id,
        child=child,
        exp_eah=eah,
        mh=pa["manifest_hash"],
        dh=pa["desc_hash"],
        descriptor_record=descriptor_record,
        patch_sha256=pa["patch_sha256"],
        target_paths=list(pa["target_paths"]),
        before_digests=before,
        runtime_receipt=runtime_receipt,
        outcome=outcome,
        failure_stage=CRE.STATUS_NOT_APPLICABLE if verified else CRE.STAGE_POST_OBSERVATION,
        dispatch_boundary=dispatch,
        physical_effect_dispatched=physical,
        mutation_performed=mutation,
        execution_state=execution_state,
        executor_status=executor_status,
        apr=apr,
        kx=kx,
        after_digests=after if physical or outcome in {CRE.OUTCOME_SUCCESS, CRE.OUTCOME_NOOP, CRE.OUTCOME_REALIZED_STATE_MISMATCH} else None,
        proof_strength="STRONG" if verified else "UNCERTAIN",
        realized_state_verified=verified,
        uncertainty_state=uncertainty,
        uncertainty_reason=reason,
        reason_code=reason,
    )
    assert store_status in {CRE.STATUS_STORED, CRE.STATUS_IDEMPOTENT}
    return {
        "status": runtime_status,
        "action_evidence_id": envelope["action_evidence_id"],
        "canonical_receipt_envelope": envelope,
        "canonical_receipt_store_status": store_status,
    }


def _prepared_fixture(tmp_path, monkeypatch, *, full_content=AFTER):
    world = _world(tmp_path)
    agent = _agent(tmp_path, monkeypatch)
    _install_snapshot(agent, world, full_content=full_content)
    prepared = _prepare(agent, world)
    assert prepared["status"] == "R10_REPAIR_PREPARED"
    return world, agent, prepared


def test_verified_success_stops_success_and_preserves_receipt(tmp_path, monkeypatch):
    world, agent, prepared = _prepared_fixture(tmp_path, monkeypatch)
    before_receipt_count = len(list((world["stores"] / "receipts").glob("*.json"))) if (world["stores"] / "receipts").exists() else 0

    execution = _store_apply_patch_outcome(world, prepared)
    action_id = execution["action_evidence_id"]
    before = _receipt_path(world, action_id).read_bytes()

    out = _ingest(
        agent,
        world,
        prepared,
        action_id,
        mission_context={"status": "ACTIVE", "allowed_targets": [TARGET], "max_attempts": 3, "attempt_index": 1},
    )

    assert out["derived_outcome_classification"] == "EXECUTED_VERIFIED"
    assert out["recommendation"] == "STOP_SUCCESS"
    assert out["r8_decision_verdict"] == "MATCH"
    assert out["r8_reconciliation_status"] == "MATCH"
    assert out["executor_invoked"] is False
    assert out["physical_mutation"] is False
    assert out["memory_promotion"] is False
    assert out["canonical_receipt_mutation"] is False
    assert _receipt_path(world, action_id).read_bytes() == before
    assert len(list((world["stores"] / "receipts").glob("*.json"))) == before_receipt_count + 1


def test_verified_noop_can_stop_success_when_equivalence_is_proven(tmp_path, monkeypatch):
    world, agent, prepared = _prepared_fixture(tmp_path, monkeypatch)
    execution = _store_apply_patch_outcome(
        world,
        prepared,
        outcome=CRE.OUTCOME_NOOP,
        physical=False,
        mutation=False,
        after_changed=False,
    )
    action_id = execution["action_evidence_id"]
    import obsidia_realized_state_reconciliation_v1 as r8_reconcile

    real_reconcile = r8_reconcile.reconcile_action_evidence

    def proven_noop(action_evidence_id, *, stores_base_dir):
        result = real_reconcile(action_evidence_id, stores_base_dir=stores_base_dir)
        result["reconciliation_status"] = r8_reconcile.STATUS_NOOP_CONFIRMED
        return result

    monkeypatch.setattr(r8_reconcile, "reconcile_action_evidence", proven_noop)

    out = _ingest(agent, world, prepared, action_id)

    assert out["derived_outcome_classification"] == "EXECUTED_VERIFIED"
    assert out["recommendation"] == "STOP_SUCCESS"
    assert out["r8_reconciliation_status"] == "NOOP_CONFIRMED"


def test_prepared_only_and_missing_evidence_do_not_claim_success(tmp_path, monkeypatch):
    world, agent, prepared = _prepared_fixture(tmp_path, monkeypatch)

    prepared_only = _ingest(agent, world, prepared, "")
    assert prepared_only["derived_outcome_classification"] == "PREPARED_ONLY"
    assert prepared_only["recommendation"] == "ESCALATE"

    missing = _ingest(agent, world, prepared, "aev-" + "0" * 32)
    assert missing["reason"] == "ACTION_EVIDENCE_NOT_FOUND"
    assert missing["derived_outcome_classification"] == "EVIDENCE_INCOMPLETE"


def test_verified_pre_dispatch_failure_can_be_bounded_retry_candidate(tmp_path, monkeypatch):
    world, agent, prepared = _prepared_fixture(tmp_path, monkeypatch)
    execution = _store_apply_patch_outcome(
        world,
        prepared,
        outcome=CRE.OUTCOME_TOCTOU_ABORTED,
        physical=False,
        mutation=False,
        verified=False,
        dispatch=CRE.DISPATCH_PRE_FAILURE,
        executor_status=CRE.STATUS_NOT_REACHED,
        execution_state="PATCH_MODIFIED_AFTER_PREPARE",
        after_changed=False,
    )

    out = _ingest(
        agent,
        world,
        prepared,
        execution["action_evidence_id"],
        mission_context={"status": "ACTIVE", "allowed_targets": [TARGET], "max_attempts": 3, "attempt_index": 1},
        repair_budget=5,
    )

    assert out["derived_outcome_classification"] == "PRE_DISPATCH_FAILURE"
    assert out["recommendation"] == "RETRY_CANDIDATE"
    assert out["retry_scope_verified"] is True
    assert out["r8_reconciliation_status"] == "NOT_REALIZED"


def test_kx_hold_block_do_not_auto_retry(tmp_path, monkeypatch):
    import obsidia_canonical_receipt_replay_v1 as evidence_replay
    import obsidia_governance_decision_replay_v1 as decision_replay
    import obsidia_realized_state_reconciliation_v1 as reconciliation

    for gate, outcome in (("HOLD", CRE.OUTCOME_KX108_HOLD), ("BLOCK", CRE.OUTCOME_KX108_BLOCK)):
        world, agent, prepared = _prepared_fixture(tmp_path / gate.lower(), monkeypatch)
        execution = _store_apply_patch_outcome(
            world,
            prepared,
        )
        env = _receipt(world, execution["action_evidence_id"])
        env["authorization"]["kx108_verdict"] = gate
        env["realized_state"]["outcome"] = outcome
        env["realized_state"]["physical_effect_dispatched"] = False
        env["execution"]["physical_effect_dispatched"] = False
        env["execution"]["executor_status"] = CRE.STATUS_NOT_REACHED
        env["envelope_hash"] = CRE.compute_envelope_hash(env)
        _write_receipt(world, execution["action_evidence_id"], env)

        monkeypatch.setattr(
            evidence_replay,
            "replay_action_evidence",
            lambda action_evidence_id, *, stores_base_dir: {
                "replay_verdict": evidence_replay.VERDICT_VERIFIED,
                "outcome": outcome,
                "evidence_missing": [],
                "evidence_conflicts": [],
            },
        )
        monkeypatch.setattr(
            decision_replay,
            "replay_governance_decision",
            lambda action_evidence_id, *, stores_base_dir: {
                "replay_verdict": decision_replay.VERDICT_MATCH,
                "evidence_limits": [],
                "conflicts": [],
            },
        )
        monkeypatch.setattr(
            reconciliation,
            "reconcile_action_evidence",
            lambda action_evidence_id, *, stores_base_dir: {
                "reconciliation_status": reconciliation.STATUS_NOT_REALIZED,
                "evidence_limits": [],
                "conflicts": [],
            },
        )

        out = _ingest(
            agent,
            world,
            prepared,
            execution["action_evidence_id"],
            mission_context={"status": "ACTIVE", "allowed_targets": [TARGET]},
        )

        assert out["derived_outcome_classification"] == "PRE_DISPATCH_FAILURE"
        assert out["recommendation"] == "STOP_BLOCKED"


def test_uncertain_dispatch_escalates(tmp_path, monkeypatch):
    world, agent, prepared = _prepared_fixture(tmp_path, monkeypatch)
    execution = _store_apply_patch_outcome(
        world,
        prepared,
        outcome=CRE.OUTCOME_DISPATCHED_OUTCOME_UNCERTAIN,
        physical=True,
        mutation=True,
        verified=False,
        dispatch=CRE.DISPATCH_POST_UNCERTAINTY,
        executor_status="INVOKED",
        execution_state=CRE.OUTCOME_DISPATCHED_OUTCOME_UNCERTAIN,
        uncertainty=CRE.OUTCOME_DISPATCHED_OUTCOME_UNCERTAIN,
        reason="CONTROLLED_FINAL_OBSERVATION_UNAVAILABLE",
    )
    action_id = execution["action_evidence_id"]

    out = _ingest(agent, world, prepared, action_id)

    assert out["derived_outcome_classification"] == "DISPATCHED_OUTCOME_UNCERTAIN"
    assert out["recommendation"] == "ESCALATE"


def test_incomplete_policy_limit_is_preserved_without_promotion(tmp_path, monkeypatch):
    world, agent, prepared = _prepared_fixture(tmp_path, monkeypatch)
    execution = _store_apply_patch_outcome(world, prepared)
    action_id = execution["action_evidence_id"]

    out = _ingest(agent, world, prepared, action_id)

    assert out["limited_verdict"] is True
    assert "KX108_POLICY_VERSION_NOT_SEPARATELY_BOUND" in out["r8_evidence_limits"]
    assert out["recommendation"] == "STOP_SUCCESS"

    (world["stores"] / "v2exec" / f"{prepared['prepared_action']['v2_exec_id']}.json").unlink()
    incomplete = _ingest(agent, world, prepared, action_id)
    assert incomplete["derived_outcome_classification"] == "EVIDENCE_INCOMPLETE"
    assert incomplete["recommendation"] == "ESCALATE"


def test_decision_mismatch_tamper_and_wrong_lineage_are_blocked(tmp_path, monkeypatch):
    world, agent, prepared = _prepared_fixture(tmp_path, monkeypatch)
    execution = _store_apply_patch_outcome(world, prepared)
    action_id = execution["action_evidence_id"]
    env = _receipt(world, action_id)

    import obsidia_governance_decision_replay_v1 as decision_replay

    real_decision_replay = decision_replay.replay_governance_decision
    monkeypatch.setattr(
        decision_replay,
        "replay_governance_decision",
        lambda action_evidence_id, *, stores_base_dir: {
            "replay_verdict": decision_replay.VERDICT_MISMATCH,
            "conflicts": ["TEST_DECISION_REPLAY_MISMATCH"],
            "evidence_limits": [],
        },
    )
    out = _ingest(agent, world, prepared, action_id)
    assert out["derived_outcome_classification"] == "GOVERNANCE_MISMATCH"
    assert out["recommendation"] == "STOP_BLOCKED"
    monkeypatch.setattr(decision_replay, "replay_governance_decision", real_decision_replay)

    tampered = copy.deepcopy(env)
    tampered["realized_state"]["outcome"] = CRE.OUTCOME_NOOP
    _write_receipt(world, action_id, tampered)
    out = _ingest(agent, world, prepared, action_id)
    assert out["derived_outcome_classification"] == "EVIDENCE_TAMPERED"
    assert out["recommendation"] == "STOP_BLOCKED"

    _write_receipt(world, action_id, env)
    wrong = dict(prepared)
    wrong["r9_handoff"] = {"handoff_id": "other"}
    wrong["prepared_action"] = dict(wrong["prepared_action"])
    wrong["prepared_action"]["builder_lineage"] = dict(wrong["prepared_action"]["builder_lineage"])
    wrong["prepared_action"]["builder_lineage"]["builder_handoff_id"] = "other"
    out = _ingest(agent, world, wrong, action_id)
    assert out["reason"] == "ACTION_EVIDENCE_LINEAGE_MISMATCH"
    assert out["derived_outcome_classification"] == "GOVERNANCE_MISMATCH"


def test_wrong_repair_attempt_rejected_before_r8_trust(tmp_path, monkeypatch):
    world, agent, prepared = _prepared_fixture(tmp_path, monkeypatch)
    execution = _execute(world, prepared)
    agent._last_repair_request.request_id = "rr_other"

    out = _ingest(agent, world, prepared, execution["action_evidence_id"])

    assert out["reason"] == "PREPARED_REPAIR_LINEAGE_MISMATCH"
    assert out["derived_outcome_classification"] == "GOVERNANCE_MISMATCH"


def test_no_executor_physical_memory_or_receipt_mutation_and_deterministic(tmp_path, monkeypatch):
    world, agent, prepared = _prepared_fixture(tmp_path, monkeypatch)
    execution = _execute(world, prepared)
    action_id = execution["action_evidence_id"]
    before_target = (world["exec_wt"] / TARGET).read_text(encoding="utf-8")
    before_receipt = _receipt_path(world, action_id).read_bytes()

    out1 = _ingest(agent, world, prepared, action_id, attempt_history=({"agent_attempt": 2},))
    out2 = _ingest(agent, world, prepared, action_id, attempt_history=({"agent_attempt": 2},))

    for out in (out1, out2):
        assert out["executor_invoked"] is False
        assert out["physical_mutation"] is False
        assert out["memory_promotion"] is False
        assert out["canonical_receipt_mutation"] is False
        assert out["automatic_retry"] is False
        assert out["attempt_history_preserved"] is True
        assert out["attempt_history_input_count"] == 1
    assert out1["derived_outcome_classification"] == out2["derived_outcome_classification"]
    assert out1["recommendation"] == out2["recommendation"]
    assert (world["exec_wt"] / TARGET).read_text(encoding="utf-8") == before_target
    assert _receipt_path(world, action_id).read_bytes() == before_receipt
