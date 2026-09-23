from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


_REPO = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO / "scripts"

if str(_SCRIPTS) not in sys.path:
    sys.path.insert(
        0,
        str(_SCRIPTS),
    )


import obsidia_jarvis_governed_chat_v0 as CHAT
import obsidia_jarvis_governed_prepare_builder_v0 as B5

# IMPORTANT:
# Use the exact module object owned by the builder.
# Loading obsidia_isolated_work_unit_v0 separately under another
# module name creates a distinct IsolatedWorkUnit class identity.
WU = B5._WU


def _git(
    root: Path,
    *args: str,
) -> str:
    r = subprocess.run(
        [
            "git",
            *args,
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )

    return r.stdout.strip()


def _world(
    tmp_path: Path,
):
    repo = (
        tmp_path
        / "main-repo"
    )

    repo.mkdir()

    _git(
        repo,
        "init",
        "-q",
    )

    _git(
        repo,
        "config",
        "user.name",
        "J9 B5 Test",
    )

    _git(
        repo,
        "config",
        "user.email",
        "j9b5@test.invalid",
    )

    # Important on Windows: exact candidate bytes.
    _git(
        repo,
        "config",
        "core.autocrlf",
        "false",
    )

    target_rel = (
        "periphery/j9b5_target.txt"
    )

    target = (
        repo
        / target_rel
    )

    target.parent.mkdir(
        parents=True
    )

    state_a = (
        b"J9_B5\nstate: A\n"
    )

    state_b = (
        b"J9_B5\nstate: B\n"
    )

    target.write_bytes(
        state_a
    )

    _git(
        repo,
        "add",
        ".",
    )

    _git(
        repo,
        "commit",
        "-q",
        "-m",
        "base",
    )

    base = _git(
        repo,
        "rev-parse",
        "HEAD",
    )

    target.write_bytes(
        state_b
    )

    diff = _git(
        repo,
        "diff",
        "--",
        target_rel,
    )

    patch = (
        tmp_path
        / "candidate.patch"
    )

    patch.write_text(
        diff + "\n",
        encoding="utf-8",
        newline="\n",
    )

    _git(
        repo,
        "checkout",
        "--",
        target_rel,
    )

    assert (
        target.read_bytes()
        == state_a
    )

    assert (
        _git(
            repo,
            "status",
            "--porcelain",
        )
        == ""
    )

    return {
        "repo":
            repo,
        "target":
            target,
        "target_rel":
            target_rel,
        "a":
            state_a,
        "b":
            state_b,
        "patch":
            patch,
        "base":
            base,
    }


class _NoCognitionAdapter:
    def __getattr__(
        self,
        name,
    ):
        raise AssertionError(
            "COGNITION_MUST_NOT_RUN:"
            + name
        )


def _chat_session(
    workspace: Path,
):
    s = (
        CHAT.GovernedJarvisChatSession
        .__new__(
            CHAT.GovernedJarvisChatSession
        )
    )

    s.session_id = (
        "jws-j9b5-real"
    )

    s.session_label = (
        "j9b5-real"
    )

    s.workspace = str(
        workspace
    )

    s.turn_count = 0
    s.last_turn = None
    s.pending_governed_mission = None
    s.adapter = _NoCognitionAdapter()

    return s


def test_builder_reaches_real_j6_hold_without_execution(
    tmp_path,
):
    w = _world(
        tmp_path
    )

    bundle = (
        B5.prepare_governed_candidate(
            repo_root=w["repo"],
            candidate_patch_path=w["patch"],
            requested_outcome=(
                "J9 B5 prepare candidate"
            ),
            relay_store_dir=(
                tmp_path
                / "relay"
            ),
            runtime_root=(
                tmp_path
                / "runtime"
            ),
            operation_key=(
                "builder-real-1"
            ),
        )
    )

    assert (
        bundle["status"]
        == (
            "J9_B5_PREPARED_"
            "AWAITING_HUMAN_EAH"
        )
    )

    relay = bundle[
        "relay_result"
    ]

    assert (
        relay["mission_state"]
        == "MISSION_HOLD"
    )

    assert (
        relay["hold_reason"]
        == (
            "HUMAN_EAH_"
            "AUTHORIZATION_REQUIRED"
        )
    )

    assert (
        relay[
            "governed_prepare_only"
        ]
        is True
    )

    assert (
        relay[
            "governed_auto_execute"
        ]
        is False
    )

    assert (
        relay[
            "target_mutated"
        ]
        is False
    )

    assert (
        relay[
            "kx108_invocations"
        ]
        == 0
    )

    assert (
        relay[
            "human_approval_created"
        ]
        is False
    )

    eah = relay[
        "execution_authority_hash"
    ]

    assert (
        isinstance(
            eah,
            str,
        )
        and len(eah) == 64
    )

    # Main worktree never changes.
    assert (
        w["target"].read_bytes()
        == w["a"]
    )

    # Isolated execution worktree exists but is still A.
    exec_target = (
        Path(
            bundle[
                "execution_worktree_path"
            ]
        )
        / w["target_rel"]
    )

    assert (
        exec_target.read_bytes()
        == w["a"]
    )

    assert (
        bundle[
            "test_contract"
        ]["checks"]
    )

    # Clean up this PREPARE-only fixture.
    disposed = (
        WU.dispose_isolated_work_unit(
            work_unit=(
                bundle[
                    "work_unit"
                ]
            ),
            require_branch_disposition_done=(
                False
            ),
        )
    )

    assert (
        disposed["status"]
        == WU.WORK_UNIT_DISPOSED
    ), disposed


def test_chat_candidate_prepare_requires_no_json(
    tmp_path,
    monkeypatch,
):
    w = _world(
        tmp_path
    )

    monkeypatch.setenv(
        "LOCALAPPDATA",
        str(
            tmp_path
            / "localapp"
        ),
    )

    s = _chat_session(
        w["repo"]
    )

    turn = s.ask(
        (
            "/governed-prepare-candidate "
            f'"{w["patch"]}"'
        )
    )

    assert (
        "GOVERNED CANDIDATE PREPARED"
        in turn[
            "surface_text"
        ]
    )

    assert (
        "NO ACTION WAS EXECUTED"
        in turn[
            "surface_text"
        ]
    )

    assert (
        "NO KX108 WAS INVOKED"
        in turn[
            "surface_text"
        ]
    )

    pending = (
        s.pending_governed_mission
    )

    assert isinstance(
        pending,
        dict,
    )

    assert (
        pending["target"]
        == w["target_rel"]
    )

    assert len(
        pending[
            "execution_authority_hash"
        ]
    ) == 64

    assert (
        w["target"].read_bytes()
        == w["a"]
    )

    # Fixture cleanup while still HOLD.
    wu = WU.IsolatedWorkUnit(
        work_unit_id=(
            "j9b5-test-reconstructed"
        ),
        repo_root=str(
            w["repo"]
        ),
        main_worktree_path=str(
            w["repo"]
        ),
        base_sha=w["base"],
        branch_name=pending[
            "branch_name"
        ],
        worktree_path=pending[
            "execution_worktree_path"
        ],
        created_by_this_component=True,
    )

    disposed = (
        WU.dispose_isolated_work_unit(
            work_unit=wu,
            require_branch_disposition_done=(
                False
            ),
        )
    )

    assert (
        disposed["status"]
        == WU.WORK_UNIT_DISPOSED
    )


def test_real_chat_candidate_to_exact_eah_to_kx_keep(
    tmp_path,
    monkeypatch,
):
    w = _world(
        tmp_path
    )

    monkeypatch.setenv(
        "LOCALAPPDATA",
        str(
            tmp_path
            / "localapp"
        ),
    )

    s = _chat_session(
        w["repo"]
    )

    prepare = s.ask(
        (
            "/governed-prepare-candidate "
            f'"{w["patch"]}"'
        )
    )

    assert (
        prepare[
            "real_execution"
        ]
        is False
    )

    pending = dict(
        s.pending_governed_mission
    )

    eah = pending[
        "execution_authority_hash"
    ]

    exec_root = Path(
        pending[
            "execution_worktree_path"
        ]
    )

    exec_target = (
        exec_root
        / w["target_rel"]
    )

    assert (
        exec_target.read_bytes()
        == w["a"]
    )

    # Ambiguous language still cannot authorize.
    rejected = s.ask(
        "yes"
    )

    assert (
        "NATURAL_LANGUAGE_APPROVAL_IS_NOT_AUTHORITY"
        in rejected[
            "surface_text"
        ]
    )

    assert (
        exec_target.read_bytes()
        == w["a"]
    )

    # Exact explicit EAH does.
    executed = s.ask(
        (
            "/governed-authorize "
            + eah
        )
    )

    assert (
        executed[
            "real_execution"
        ]
        is True
    )

    surface = executed[
        "surface_text"
    ]

    assert (
        "state=MISSION_COMPLETE"
        in surface
    )

    assert (
        "kx108_pre=ALLOW"
        in surface
    )

    assert (
        "kx108_post=ALLOW"
        in surface
    )

    assert (
        "human_authorization_consumed=True"
        in surface
    )

    assert (
        exec_target.read_bytes()
        == w["b"]
    )

    # Main workspace is still untouched.
    assert (
        w["target"].read_bytes()
        == w["a"]
    )

    # No Git disposition.
    assert (
        _git(
            exec_root,
            "rev-parse",
            "HEAD",
        )
        == w["base"]
    )

    assert (
        _git(
            exec_root,
            "diff",
            "--name-only",
        )
        == w["target_rel"]
    )


def test_builder_failure_disposes_its_clean_worktree(
    tmp_path,
    monkeypatch,
):
    w = _world(
        tmp_path
    )

    def fail_relay(**kwargs):
        return {
            "status":
                "RELAY_MISSION_MISSION_FAILED",
            "mission_state":
                "MISSION_FAILED",
            "governed_prepare_only":
                True,
            "governed_auto_execute":
                False,
            "target_mutated":
                False,
            "decision_authority":
                "KX108_ONLY",
        }

    monkeypatch.setattr(
        B5._RELAY,
        "relay_submit_mission",
        fail_relay,
    )

    runtime = (
        tmp_path
        / "runtime"
    )

    result = (
        B5.prepare_governed_candidate(
            repo_root=w["repo"],
            candidate_patch_path=w["patch"],
            requested_outcome="fail",
            relay_store_dir=(
                tmp_path
                / "relay"
            ),
            runtime_root=runtime,
            operation_key="failure-cleanup",
        )
    )

    assert (
        result["status"]
        == "J9_B5_PREPARE_REJECTED"
    )

    assert (
        result["cleanup"]["status"]
        == WU.WORK_UNIT_DISPOSED
    )

    # No registered J9-B5 execution worktree left.
    wt_list = _git(
        w["repo"],
        "worktree",
        "list",
        "--porcelain",
    )

    assert (
        "jarvis/j9b5-"
        not in wt_list
    )


def test_j9b5_has_no_execution_authority_implementation():
    src = Path(
        B5.__file__
    ).read_text(
        encoding="utf-8-sig"
    )

    assert (
        src.count(
            "_MAT.materialize_candidate_patch("
        )
        == 1
    )

    assert (
        src.count(
            "_WU.create_isolated_work_unit("
        )
        == 1
    )

    assert (
        src.count(
            "_J3.prepare_cognitive_governed_handoff("
        )
        == 1
    )

    assert (
        src.count(
            "_RELAY.relay_submit_mission("
        )
        == 1
    )

    for forbidden in (
        "execute_jarvis_governed_mutation(",
        "execute_governed_remediation(",
        "run_governed_content_apply(",
        "store_approval_artifact(",
        "run_and_persist_kx108(",
        "update_parental_control(",
    ):
        assert forbidden not in src

    assert (
        'AUTHORITY = "NONE"'
        in src
    )

    assert (
        'DECISION_AUTHORITY = "KX108_ONLY"'
        in src
    )

    assert (
        "AUTO_EXECUTE = False"
        in src
    )

    assert (
        "AUTO_AUTHORIZE = False"
        in src
    )
