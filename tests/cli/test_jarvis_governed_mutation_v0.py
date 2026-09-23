from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO / "scripts"

if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import obsidia_cognitive_governed_runtime_handoff_v0 as J3
import obsidia_governed_execution_driver_v0 as DRV
import obsidia_jarvis_governed_mutation_v0 as J5


def _proposal(tmp_path: Path) -> dict:
    return J3.prepare_cognitive_governed_handoff(
        mission_id="mission-j5-001",
        provider_id="jarvis-pc",
        capability=J5.CAPABILITY_ID,
        payload={
            "source_git_commit": "a" * 40,
            "source_historical_path": "source.txt",
            "target_path": "target.txt",
            "test_contract": {
                "checks": [],
            },
            "objective": "replace target",
        },
        domain="JARVIS_PC",
        action_id="action-j5-001",
        intent="replace governed target",
        action_type=J5.ACTION_TYPE,
        irreversible=False,
    )


def _runtime(tmp_path: Path) -> dict:
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "target.txt").write_bytes(b"A\n")

    dirs = {
        name: tmp_path / name
        for name in (
            "ledger",
            "selector",
            "execution",
            "pec",
            "kxpre",
            "kxpost",
            "tcr",
            "sar",
            "sre",
            "rollback",
        )
    }

    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)

    return {
        "repo": repo,
        **dirs,
    }


def test_boundary_constants():
    assert J5.JARVIS_AUTHORITY == "NONE"
    assert J5.DECISION_AUTHORITY == "KX108_ONLY"
    assert (
        J5.CAPABILITY_ID
        == "GOVERNED_UPDATE_TARGET_FROM_SOURCE"
    )


def test_invalid_j3_proposal_fails_closed(tmp_path):
    p = _proposal(tmp_path)
    p["plan_hash"] = "0" * 64

    with pytest.raises(
        J5.JarvisGovernedMutationSeamError,
        match="J3_PROPOSAL_INVALID",
    ):
        J5._verify_proposal(p)


def test_wrong_capability_fails_closed(tmp_path):
    p = _proposal(tmp_path)
    p["capability"] = "SHELL_EXECUTE"

    # restore a valid hash after changing plan field
    p["plan_hash"] = J3._compute_plan_hash(p)

    with pytest.raises(
        J5.JarvisGovernedMutationSeamError,
        match="CAPABILITY_NOT_ALLOWED",
    ):
        J5._verify_proposal(p)


def test_cognition_cannot_supply_runtime_paths(
    tmp_path,
):
    p = _proposal(tmp_path)

    p["payload"]["execution_dir"] = "evil"

    p["plan_hash"] = J3._compute_plan_hash(p)

    with pytest.raises(
        J5.JarvisGovernedMutationSeamError,
        match=(
            "COGNITIVE_RUNTIME_AUTHORITY_FIELDS_FORBIDDEN"
        ),
    ):
        J5._verify_proposal(p)


def test_prepare_calls_existing_driver_only_and_does_not_mutate(
    tmp_path,
    monkeypatch,
):
    p = _proposal(tmp_path)
    rt = _runtime(tmp_path)

    target = rt["repo"] / "target.txt"
    before = target.read_bytes()

    calls = []

    def fake_prepare(**kwargs):
        calls.append(kwargs)

        return {
            "status":
                DRV.PREPARED_AWAITING_HUMAN_APPROVAL,
            "authority": "NON_SOVEREIGN",
            "decision_authority": "KX108_ONLY",
            "target_mutated": False,
            "kx108_invocations": 0,
            "human_approval_created": False,
            "execution_authority_hash": "e" * 64,
            "batch_execution_id": "batch-exec-j5",
            "child_execution_id": "child-j5",
        }

    monkeypatch.setattr(
        DRV,
        "prepare_governed_execution",
        fake_prepare,
    )

    out = J5.prepare_jarvis_governed_mutation(
        p,
        execution_worktree_path=rt["repo"],
        main_worktree_path=tmp_path / "main",
        branch_name="j5-test",
        base_sha="b" * 40,
        ledger_dir=rt["ledger"],
        selector_dir=rt["selector"],
        execution_dir=rt["execution"],
        pre_execution_context_dir=rt["pec"],
    )

    assert len(calls) == 1
    assert target.read_bytes() == before

    assert out["j5_phase"] == "PREPARE"
    assert out["jarvis_authority"] == "NONE"
    assert (
        out["decision_authority"]
        == "KX108_ONLY"
    )
    assert out["execution_authorization"] is False
    assert (
        out["human_authorization_consumed"]
        is False
    )
    assert out["kx108_invocations"] == 0
    assert out["target_mutated"] is False


def test_execute_wrong_eah_never_reaches_driver(
    tmp_path,
    monkeypatch,
):
    called = []

    def fake_execute(*args, **kwargs):
        called.append((args, kwargs))
        raise AssertionError(
            "driver must not be called"
        )

    monkeypatch.setattr(
        DRV,
        "execute_governed_remediation",
        fake_execute,
    )

    prepared = {
        "status":
            DRV.PREPARED_AWAITING_HUMAN_APPROVAL,
        "j5_phase": "PREPARE",
        "execution_authority_hash": "e" * 64,
        "batch_execution_id": "be-j5",
        "child_execution_id": "ce-j5",
        "j5_plan_hash": "p" * 64,
    }

    with pytest.raises(
        J5.JarvisGovernedMutationSeamError,
        match="HUMAN_AUTHORIZED_EAH_MISMATCH",
    ):
        J5.execute_jarvis_governed_mutation(
            prepared,
            human_authorized_execution_authority_hash=(
                "f" * 64
            ),
            human_authorization_reference="human-j5",
            execution_dir=tmp_path / "exec",
            pre_execution_context_dir=tmp_path / "pec",
            selector_dir=tmp_path / "selector",
            ledger_dir=tmp_path / "ledger",
            kx108_pre_decision_dir=tmp_path / "pre",
            kx108_post_decision_dir=tmp_path / "post",
            test_contract_results_dir=tmp_path / "tcr",
            sealed_receipt_dir=tmp_path / "sar",
            sealed_rollback_evidence_dir=tmp_path / "sre",
            rollback_result_dir=tmp_path / "rbk",
            repo_root=tmp_path,
        )

    assert called == []


def test_execute_passes_exact_human_authority_to_existing_driver(
    tmp_path,
    monkeypatch,
):
    calls = []

    def fake_execute(*args, **kwargs):
        calls.append((args, kwargs))

        return {
            "status": "DRIVER_EXECUTED",
            "kx108_pre_gate": "ALLOW",
        }

    monkeypatch.setattr(
        DRV,
        "execute_governed_remediation",
        fake_execute,
    )

    eah = "e" * 64

    prepared = {
        "status":
            DRV.PREPARED_AWAITING_HUMAN_APPROVAL,
        "j5_phase": "PREPARE",
        "execution_authority_hash": eah,
        "batch_execution_id": "be-j5",
        "child_execution_id": "ce-j5",
        "j5_plan_hash": "p" * 64,
    }

    out = J5.execute_jarvis_governed_mutation(
        prepared,
        human_authorized_execution_authority_hash=eah,
        human_authorization_reference=(
            "HUMAN_J5_EXPLICIT_TEST"
        ),
        execution_dir=tmp_path / "exec",
        pre_execution_context_dir=tmp_path / "pec",
        selector_dir=tmp_path / "selector",
        ledger_dir=tmp_path / "ledger",
        kx108_pre_decision_dir=tmp_path / "pre",
        kx108_post_decision_dir=tmp_path / "post",
        test_contract_results_dir=tmp_path / "tcr",
        sealed_receipt_dir=tmp_path / "sar",
        sealed_rollback_evidence_dir=tmp_path / "sre",
        rollback_result_dir=tmp_path / "rbk",
        repo_root=tmp_path,
    )

    assert len(calls) == 1

    args, kwargs = calls[0]

    assert args == (
        "be-j5",
        "ce-j5",
    )

    assert (
        kwargs[
            "human_authorized_execution_authority_hash"
        ]
        == eah
    )

    assert (
        kwargs["human_authorization_reference"]
        == "HUMAN_J5_EXPLICIT_TEST"
    )

    assert (
        kwargs["authority_mode"]
        == DRV.AUTHORITY_MODE_PER_ACTION_HUMAN_EAH
    )

    assert kwargs["mission_id"] is None
    assert kwargs["mission_store_dir"] is None

    assert out["j5_phase"] == "EXECUTE"
    assert out["jarvis_authority"] == "NONE"
    assert (
        out["decision_authority"]
        == "KX108_ONLY"
    )
    assert (
        out["human_authorization_consumed"]
        is True
    )


def test_j5_has_no_write_or_authority_implementation():
    src = inspect.getsource(J5)

    banned = (
        "atomic_replace_with_bytes(",
        "run_governed_content_apply(",
        "run_and_persist_kx108_pre_execution_decision(",
        "store_approval_artifact(",
        ".write_bytes(",
        ".write_text(",
        "os.replace(",
        "subprocess.run(",
        "subprocess.Popen(",
        "os.system(",
        "git commit",
        "git push",
        "git merge",
    )

    for token in banned:
        assert token not in src, token



# ==========================================================================
# J5-E ? REAL GOVERNED MUTATION E2E
# ==========================================================================

import hashlib
import subprocess
import sys

import obsidia_test_contract as TC
import obsidia_sealed_evidence_v0 as SEV


_J5E_TARGET_REL = (
    "periphery/xdomain/j5e_target_v0.txt"
)

_J5E_SOURCE_REL = (
    "periphery/xdomain/j5e_source_v0.txt"
)

_J5E_A = (
    b"JARVIS_GOVERNED_MUTATION_FIXTURE\n"
    b"state: BEFORE\n"
)

_J5E_B = (
    b"JARVIS_GOVERNED_MUTATION_FIXTURE\n"
    b"state: AFTER_GOVERNED_APPLY\n"
)


def _j5e_sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _j5e_git(
    repo: Path,
    *args: str,
) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0, (
        f"git {args}: {proc.stderr}"
    )

    return proc.stdout.strip()


@pytest.fixture
def j5e_world(tmp_path):
    main = tmp_path / "main"

    (
        main
        / "periphery"
        / "xdomain"
    ).mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        main
        / _J5E_TARGET_REL
    ).write_bytes(
        _J5E_A
    )

    (
        main
        / _J5E_SOURCE_REL
    ).write_bytes(
        _J5E_B
    )

    _j5e_git(
        main,
        "init",
        "-q",
    )

    _j5e_git(
        main,
        "config",
        "user.email",
        "j5e@example.com",
    )

    _j5e_git(
        main,
        "config",
        "user.name",
        "j5e",
    )

    _j5e_git(
        main,
        "config",
        "commit.gpgsign",
        "false",
    )

    _j5e_git(
        main,
        "add",
        _J5E_TARGET_REL,
        _J5E_SOURCE_REL,
    )

    _j5e_git(
        main,
        "commit",
        "-q",
        "-m",
        "j5e seed",
    )

    base_sha = _j5e_git(
        main,
        "rev-parse",
        "HEAD",
    )

    exec_wt = (
        tmp_path
        / "exec_wt"
    )

    _j5e_git(
        main,
        "worktree",
        "add",
        str(exec_wt),
        "-b",
        "j5e-br",
        base_sha,
    )

    stores = {
        name: tmp_path / name
        for name in (
            "ledger",
            "selector",
            "exec",
            "pec",
            "kxpre",
            "kxpost",
            "tcr",
            "sar",
            "sre",
            "rbk",
        )
    }

    return {
        "main": main,
        "exec_wt": exec_wt,
        "base_sha": base_sha,
        "stores": stores,
        "target_abs": (
            exec_wt
            / _J5E_TARGET_REL
        ),
    }


def _j5e_positive_contract() -> dict:
    checks = [
        TC.build_check(
            "post-sha",
            TC.CHECK_TYPE_TARGET_SHA256,
            target_path=_J5E_TARGET_REL,
            expected_target_sha256=(
                _j5e_sha(_J5E_B)
            ),
            required=True,
        ),
        TC.build_check(
            "diff-scope",
            TC.CHECK_TYPE_DIFF_SCOPE,
            expected_diff_paths=[
                _J5E_TARGET_REL
            ],
            required=True,
        ),
        TC.build_check(
            "marker",
            TC.CHECK_TYPE_SUBPROCESS,
            argv=[
                sys.executable,
                "-c",
                (
                    "import pathlib,sys;"
                    "c=pathlib.Path("
                    + repr(_J5E_TARGET_REL)
                    + ").read_text();"
                    "sys.exit("
                    "0 if "
                    "'AFTER_GOVERNED_APPLY' "
                    "in c and "
                    "'state: BEFORE' "
                    "not in c "
                    "else 1)"
                ),
            ],
            expected_exit_code=0,
            required=True,
        ),
    ]

    return TC.build_test_contract(
        "j5e-positive-v0",
        "jarvis",
        "j5e-batch",
        _J5E_TARGET_REL,
        checks,
    )


def _j5e_proposal(
    world: dict,
    contract: dict,
) -> dict:
    return J3.prepare_cognitive_governed_handoff(
        mission_id="mission-j5-e2e-001",
        provider_id="jarvis-pc",
        capability=J5.CAPABILITY_ID,
        payload={
            "source_git_commit":
                world["base_sha"],
            "source_historical_path":
                _J5E_SOURCE_REL,
            "target_path":
                _J5E_TARGET_REL,
            "test_contract":
                contract,
            "objective":
                "Jarvis governed file replacement",
        },
        domain="JARVIS_PC",
        action_id="action-j5-e2e-001",
        intent=(
            "replace exact target from exact "
            "git-bound source"
        ),
        action_type=J5.ACTION_TYPE,
        irreversible=False,
    )


def test_j5_e2e_real_governed_mutation_keep(
    j5e_world,
):
    world = j5e_world
    stores = world["stores"]

    contract = (
        _j5e_positive_contract()
    )

    proposal = _j5e_proposal(
        world,
        contract,
    )

    # J3 proposal integrity is real.
    ok, reason = (
        J3.verify_cognitive_governed_handoff(
            proposal
        )
    )

    assert ok is True, reason

    before = (
        world["target_abs"]
        .read_bytes()
    )

    assert before == _J5E_A

    # --------------------------------------------------------------
    # PHASE 1 ? J5 PREPARE
    # No HumanApproval, no KX108, no target mutation.
    # --------------------------------------------------------------

    prepared = (
        J5.prepare_jarvis_governed_mutation(
            proposal,
            execution_worktree_path=(
                world["exec_wt"]
            ),
            main_worktree_path=(
                world["main"]
            ),
            branch_name="j5e-br",
            base_sha=world["base_sha"],
            ledger_dir=stores["ledger"],
            selector_dir=stores["selector"],
            execution_dir=stores["exec"],
            pre_execution_context_dir=(
                stores["pec"]
            ),
        )
    )

    assert (
        prepared["status"]
        == DRV.PREPARED_AWAITING_HUMAN_APPROVAL
    )

    assert (
        prepared["j5_phase"]
        == J5.PREPARE_PHASE
    )

    assert (
        prepared["jarvis_authority"]
        == "NONE"
    )

    assert (
        prepared["decision_authority"]
        == "KX108_ONLY"
    )

    assert (
        prepared["target_mutated"]
        is False
    )

    assert (
        prepared["kx108_invocations"]
        == 0
    )

    assert (
        prepared[
            "human_approval_created"
        ]
        is False
    )

    assert (
        prepared[
            "human_authorization_consumed"
        ]
        is False
    )

    assert (
        len(
            prepared[
                "execution_authority_hash"
            ]
        )
        == 64
    )

    assert (
        world["target_abs"]
        .read_bytes()
        == _J5E_A
    )

    assert not list(
        stores["kxpre"].rglob(
            "*.json"
        )
    )

    assert not list(
        stores["sar"].rglob(
            "*.json"
        )
    )

    assert not list(
        stores["sre"].rglob(
            "*.json"
        )
    )

    # --------------------------------------------------------------
    # HUMAN AUTHORIZATION BOUND TO EXACT EAH.
    # --------------------------------------------------------------

    human_eah = prepared[
        "execution_authority_hash"
    ]

    human_ref = (
        "HUMAN_EXPLICIT_J5_E2E_001"
    )

    # --------------------------------------------------------------
    # PHASE 2 ? J5 EXECUTE
    # Existing canonical driver owns all authority-sensitive work.
    # --------------------------------------------------------------

    result = (
        J5.execute_jarvis_governed_mutation(
            prepared,
            human_authorized_execution_authority_hash=(
                human_eah
            ),
            human_authorization_reference=(
                human_ref
            ),
            execution_dir=stores["exec"],
            pre_execution_context_dir=(
                stores["pec"]
            ),
            selector_dir=stores["selector"],
            ledger_dir=stores["ledger"],
            kx108_pre_decision_dir=(
                stores["kxpre"]
            ),
            kx108_post_decision_dir=(
                stores["kxpost"]
            ),
            test_contract_results_dir=(
                stores["tcr"]
            ),
            sealed_receipt_dir=(
                stores["sar"]
            ),
            sealed_rollback_evidence_dir=(
                stores["sre"]
            ),
            rollback_result_dir=(
                stores["rbk"]
            ),
            repo_root=world["exec_wt"],
        )
    )

    # --------------------------------------------------------------
    # END-TO-END GOVERNANCE PROOF
    # --------------------------------------------------------------

    assert (
        result["status"]
        == DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW
    ), result

    assert (
        result["kx108_pre_gate"]
        == "ALLOW"
    )

    assert (
        result["kx108_post_gate"]
        == "ALLOW"
    )

    assert (
        result["j5_phase"]
        == J5.EXECUTE_PHASE
    )

    assert (
        result["jarvis_authority"]
        == "NONE"
    )

    assert (
        result["decision_authority"]
        == "KX108_ONLY"
    )

    assert (
        result[
            "human_authorization_consumed"
        ]
        is True
    )

    assert (
        result[
            "human_authorization_reference"
        ]
        == human_ref
    )

    # Actual governed mutation A -> B.
    after = (
        world["target_abs"]
        .read_bytes()
    )

    assert after == _J5E_B

    assert (
        _j5e_sha(after)
        == _j5e_sha(_J5E_B)
    )

    # Sealed proof exists and verifies.
    sre = (
        SEV.load_sealed_rollback_evidence(
            result[
                "sealed_rollback_evidence_id"
            ],
            stores["sre"],
        )
    )

    sar = (
        SEV.load_sealed_apply_receipt(
            result[
                "sealed_apply_receipt_id"
            ],
            stores["sar"],
        )
    )

    assert (
        SEV.verify_sealed_rollback_evidence(
            sre
        )[0]
        is True
    )

    assert (
        SEV.verify_sealed_apply_receipt(
            sar
        )[0]
        is True
    )

    # No automatic Git disposition.
    assert (
        _j5e_git(
            world["exec_wt"],
            "rev-parse",
            "HEAD",
        )
        == world["base_sha"]
    )

    assert (
        _j5e_git(
            world["exec_wt"],
            "diff",
            "--name-only",
        )
        == _J5E_TARGET_REL
    )

    assert (
        result["driver_git_disposition"]
        is False
    )
