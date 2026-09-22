from __future__ import annotations

import subprocess
import sys
from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO_ROOT / "scripts"

if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))


import obsidia_jarvis_ingress_v0 as J
import obsidia_openjarvis_adapter_v0 as O


def _git(repo: Path, *args: str):
    return subprocess.run(
        ["git", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=True,
    )


def _make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()

    _git(repo, "init")
    _git(repo, "config", "user.email", "jarvis-v0@example.invalid")
    _git(repo, "config", "user.name", "Jarvis V0 Test")

    (repo / "README.txt").write_text(
        "jarvis-v0\n",
        encoding="utf-8",
    )

    _git(repo, "add", "README.txt")
    _git(repo, "commit", "-m", "initial")

    return repo


def _request(repo: Path, *, mode="READ_ONLY"):
    return J.JarvisRequest(
        command_id="cmd-test-001",
        correlation_id="corr-test-001",
        issued_at="2026-09-22T00:00:00+02:00",
        requested_outcome="read git state",
        repo_root=str(repo),
        requested_execution_mode=mode,
    )


def test_openjarvis_adapter_is_non_authority():
    assert O.OPENJARVIS_IS_AUTHORITY is False
    assert O.OPENJARVIS_MEMORY_IS_CANONICAL is False
    assert O.ADAPTER_CAN_EXPAND_SCOPE is False
    assert O.ADAPTER_CAN_DECIDE_KX is False
    assert O.ADAPTER_CAN_WRITE_NATIVE_MEMORY is False

    out = O.NotConnectedAdapter().execute(
        capability_id="GIT_STATE_READ",
        payload={},
    )

    assert out["status"] == "ADAPTER_NOT_CONNECTED"
    assert out["is_execution_authority"] is False
    assert out["is_kx_authority"] is False
    assert out["scope_expanded"] is False
    assert out["memory_written"] is False


def test_empty_allowlist_fails_closed(tmp_path):
    repo = _make_repo(tmp_path)
    store = tmp_path / "state"

    out = J.submit_readonly_git_state(
        _request(repo),
        allowed_repositories=[],
        store_dir=store,
    )

    assert out["status"] == "JARVIS_REJECTED"
    assert out["reason"] == "REPOSITORY_ALLOWLIST_EMPTY"


def test_repo_outside_allowlist_rejected(tmp_path):
    repo = _make_repo(tmp_path)
    other = tmp_path / "other"
    other.mkdir()
    store = tmp_path / "state"

    out = J.submit_readonly_git_state(
        _request(repo),
        allowed_repositories=[other],
        store_dir=store,
    )

    assert out["status"] == "JARVIS_REJECTED"
    assert out["reason"] == "REPOSITORY_NOT_ALLOWLISTED"


def test_non_readonly_mode_rejected(tmp_path):
    repo = _make_repo(tmp_path)
    store = tmp_path / "state"

    out = J.submit_readonly_git_state(
        _request(repo, mode="INTERNAL_OPERATIONAL_WRITE"),
        allowed_repositories=[repo],
        store_dir=store,
    )

    assert out["status"] == "JARVIS_REJECTED"
    assert out["reason"] == "READ_ONLY_MODE_REQUIRED"


def test_store_inside_repo_rejected(tmp_path):
    repo = _make_repo(tmp_path)

    out = J.submit_readonly_git_state(
        _request(repo),
        allowed_repositories=[repo],
        store_dir=repo / ".jarvis-state",
    )

    assert out["status"] == "JARVIS_REJECTED"
    assert out["reason"] == "STORE_DIR_INSIDE_REPOSITORY"


def test_e2e_readonly_git_state_no_mutation(tmp_path):
    repo = _make_repo(tmp_path)
    store = tmp_path / "jarvis-state"

    before_head = _git(repo, "rev-parse", "HEAD").stdout.strip()

    out = J.submit_readonly_git_state(
        _request(repo),
        allowed_repositories=[repo],
        store_dir=store,
    )

    after_head = _git(repo, "rev-parse", "HEAD").stdout.strip()

    assert out["status"] == "JARVIS_READ_ONLY_COMPLETE"

    assert out["relay_status"] == "MISSION_COMPLETE"
    assert out["mission_kind"] == "GIT_STATE_READ"

    assert out["kx108_invoked"] is False
    assert out["kx108_reason"] == "READ_ONLY_AUTHORITY_CLASS_NONE"

    assert out["memory_write"] is False
    assert out["emits_act"] is False
    assert out["kernel_mutation"] is False
    assert out["scope_expanded"] is False
    assert out["openjarvis_connected"] is False

    assert out["mutated_measured"] is False

    assert out["before_state"]["head"] == before_head
    assert out["after_state"]["head"] == after_head
    assert before_head == after_head

    assert out["receipt_integrity_complete"] is True
    assert len(out["receipt_ids"]) >= 3
    assert len(out["receipt_hashes"]) == len(out["receipt_ids"])
    assert isinstance(out["receipts_digest"], str)
    assert len(out["receipts_digest"]) == 64

    assert store.exists()
    assert not (repo / ".jarvis-state").exists()


def test_jarvis_v0_does_not_import_sovereign_or_memory_layers():
    ingress = (
        _SCRIPTS / "obsidia_jarvis_ingress_v0.py"
    ).read_text(encoding="utf-8")

    adapter = (
        _SCRIPTS / "obsidia_openjarvis_adapter_v0.py"
    ).read_text(encoding="utf-8")

    combined = ingress + "\n" + adapter

    banned = (
        "import sigma",
        "GuardX108",
        "run_and_persist_kx108",
        "brody_obsidia_native_memory",
        "atomic_replace_with_bytes",
        "run_governed_content_apply",
        "shell=True",
        "os.system",
    )

    for token in banned:
        assert token not in combined, token

def test_openjarvis_shadow_adapter_rejects_unknown_capability(tmp_path):
    adapter = O.OpenJarvisShadowAdapter(
        source_root=str(tmp_path),
        expected_commit="0" * 40,
    )

    out = adapter.execute(
        capability_id="SHELL_EXECUTE",
        payload={},
    )

    assert out["status"] == "CAPABILITY_NOT_ALLOWED"
    assert out["is_execution_authority"] is False
    assert out["scope_expanded"] is False


def test_openjarvis_shadow_adapter_requires_exact_source_identity(tmp_path):
    repo = tmp_path / "oj"
    repo.mkdir()

    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "Test")
    (repo / "x.txt").write_text("x\n", encoding="utf-8")
    _git(repo, "add", "x.txt")
    _git(repo, "commit", "-m", "x")

    adapter = O.OpenJarvisShadowAdapter(
        source_root=str(repo),
        expected_commit="0" * 40,
    )

    out = adapter.execute(
        capability_id="OPENJARVIS_RUNTIME_HANDSHAKE",
        payload={},
    )

    assert out["status"] == "OPENJARVIS_SOURCE_IDENTITY_MISMATCH"
    assert out["is_execution_authority"] is False


def test_real_openjarvis_shadow_handshake_when_configured():
    import os

    source = os.environ.get("OBSIDIA_OPENJARVIS_SOURCE")
    expected = os.environ.get("OBSIDIA_OPENJARVIS_COMMIT")

    if not source or not expected:
        import pytest
        pytest.skip("real OpenJarvis source not configured")

    adapter = O.OpenJarvisShadowAdapter(
        source_root=source,
        expected_commit=expected,
    )

    out = adapter.execute(
        capability_id="OPENJARVIS_RUNTIME_HANDSHAKE",
        payload={},
    )

    assert out["status"] == "OPENJARVIS_SHADOW_HANDSHAKE_OK"

    assert out["actual_commit"] == expected
    assert out["source_dirty"] is False

    assert out["agent_execution_enabled"] is False
    assert out["tool_execution_enabled"] is False
    assert out["scheduler_enabled"] is False
    assert out["memory_enabled"] is False

    assert out["is_execution_authority"] is False
    assert out["is_kx_authority"] is False
    assert out["scope_expanded"] is False
    assert out["memory_written"] is False

    surfaces = out["probe_evidence"]["module_availability"]

    assert surfaces["openjarvis"] is True
    assert surfaces["agents"] is True
    assert surfaces["agent_executor"] is True
    assert surfaces["agent_scheduler"] is True
    assert surfaces["tools"] is True
    assert surfaces["mcp"] is True


# ======================================================================
# JARVIS V0.3 ? RELAY-FIRST OPENJARVIS SHADOW CAPABILITY
# ======================================================================

def _make_fake_openjarvis_source(tmp_path):
    repo = tmp_path / "fake-openjarvis"
    repo.mkdir()

    package = repo / "src" / "openjarvis"

    for directory in (
        package,
        package / "agents",
        package / "tools",
        package / "mcp",
        package / "server",
        package / "learning",
    ):
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        (directory / "__init__.py").write_text(
            "",
            encoding="utf-8",
        )

    (package / "__init__.py").write_text(
        '__version__ = "test-shadow"\n',
        encoding="utf-8",
    )

    for module in (
        "executor.py",
        "scheduler.py",
        "operative.py",
        "monitor_operative.py",
    ):
        (
            package / "agents" / module
        ).write_text(
            "# fake OpenJarvis surface\n",
            encoding="utf-8",
        )

    _git(repo, "init")
    _git(
        repo,
        "config",
        "user.email",
        "jarvis-v03@example.invalid",
    )
    _git(
        repo,
        "config",
        "user.name",
        "Jarvis V03",
    )

    _git(repo, "add", ".")
    _git(
        repo,
        "commit",
        "-m",
        "fake OpenJarvis runtime",
    )

    commit = _git(
        repo,
        "rev-parse",
        "HEAD",
    ).stdout.strip()

    return repo, commit


def test_openjarvis_v03_registered_non_authority():
    import obsidia_capability_graph_v0 as G
    import obsidia_relay_v0 as R
    import obsidia_stack_native_routes_v0 as NAT

    cap = G.get_capability(
        "OPENJARVIS_RUNTIME_HANDSHAKE"
    )

    assert cap is not None
    assert cap["owner"] == "OPENJARVIS_RUNTIME"
    assert cap["route"] == "STACK_NATIVE_ROUTE"
    assert cap["authority_class"] == "NONE"

    assert cap["grants_authority"] is False
    assert cap["is_execution_authority"] is False

    resolved = R.relay_resolve_capability(
        R.KIND_OPENJARVIS_RUNTIME_HANDSHAKE
    )

    assert (
        resolved["capability_id"]
        == "OPENJARVIS_RUNTIME_HANDSHAKE"
    )

    assert resolved["authority_class"] == "NONE"
    assert resolved["grants_authority"] is False

    assert (
        "OPENJARVIS_RUNTIME_HANDSHAKE"
        in NAT.NATIVE_CAPABILITIES
    )


def test_openjarvis_v03_requires_configuration(
    tmp_path,
    monkeypatch,
):
    import obsidia_stack_native_routes_v0 as NAT

    monkeypatch.delenv(
        "OBSIDIA_OPENJARVIS_SOURCE",
        raising=False,
    )

    monkeypatch.delenv(
        "OBSIDIA_OPENJARVIS_COMMIT",
        raising=False,
    )

    ev = NAT.run_openjarvis_runtime_handshake(
        "0" * 40,
        source_root=tmp_path,
    )

    assert ev["ok"] is False

    assert (
        ev["reason"]
        == "OPENJARVIS_RUNTIME_NOT_CONFIGURED"
    )


def test_openjarvis_v03_blocks_source_scope_expansion(
    tmp_path,
    monkeypatch,
):
    import obsidia_stack_native_routes_v0 as NAT

    repo, commit = _make_fake_openjarvis_source(
        tmp_path
    )

    other = tmp_path / "other"
    other.mkdir()

    monkeypatch.setenv(
        "OBSIDIA_OPENJARVIS_SOURCE",
        str(repo),
    )

    monkeypatch.setenv(
        "OBSIDIA_OPENJARVIS_COMMIT",
        commit,
    )

    ev = NAT.run_openjarvis_runtime_handshake(
        commit,
        source_root=other,
    )

    assert ev["ok"] is False

    assert (
        ev["reason"]
        == "OPENJARVIS_SOURCE_NOT_AUTHORIZED"
    )


def test_openjarvis_v03_e2e_relay_shadow_handshake(
    tmp_path,
    monkeypatch,
):
    import obsidia_relay_v0 as R

    repo, commit = _make_fake_openjarvis_source(
        tmp_path
    )

    monkeypatch.setenv(
        "OBSIDIA_OPENJARVIS_SOURCE",
        str(repo),
    )

    monkeypatch.setenv(
        "OBSIDIA_OPENJARVIS_COMMIT",
        commit,
    )

    out = R.relay_submit_mission(
        requested_outcome=(
            "verify pinned OpenJarvis runtime"
        ),
        mission_kind=(
            R.KIND_OPENJARVIS_RUNTIME_HANDSHAKE
        ),
        target=commit,
        repo_root=repo,
        store_dir=tmp_path / "relay-store",
    )

    assert out["mission_state"] == R.MISSION_COMPLETE

    assert out["metrics"]["native_route_count"] == 1
    assert out["metrics"]["cognitive_request_count"] == 0

    ev = out["native_evidence"]

    assert ev["ok"] is True

    assert (
        ev["native_route_kind"]
        == "OPENJARVIS_RUNTIME_HANDSHAKE"
    )

    assert (
        ev["openjarvis_status"]
        == "OPENJARVIS_SHADOW_HANDSHAKE_OK"
    )

    assert ev["expected_commit"] == commit
    assert ev["actual_commit"] == commit

    assert ev["external_runtime_authority"] == "NONE"

    assert ev["agent_execution_enabled"] is False
    assert ev["tool_execution_enabled"] is False
    assert ev["scheduler_enabled"] is False
    assert ev["memory_enabled"] is False
    assert ev["memory_written"] is False
    assert ev["scope_expanded"] is False
    assert ev["mutated_repo"] is False

    assert (
        _git(repo, "rev-parse", "HEAD")
        .stdout.strip()
        == commit
    )

    assert (
        _git(repo, "status", "--porcelain")
        .stdout.strip()
        == ""
    )



# ======================================================================
# JARVIS V0.4 ? REAL OPENJARVIS SIMPLEAGENT / DETERMINISTIC SHADOW
# ======================================================================

def test_openjarvis_v04_capability_registered():
    import obsidia_capability_graph_v0 as G
    import obsidia_relay_v0 as R
    import obsidia_stack_native_routes_v0 as NAT

    cap = G.get_capability(
        "OPENJARVIS_SIMPLE_AGENT_SHADOW"
    )

    assert cap is not None
    assert cap["owner"] == "OPENJARVIS_RUNTIME"
    assert cap["authority_class"] == "NONE"
    assert cap["route"] == "STACK_NATIVE_ROUTE"
    assert cap["mode"] == "DETERMINISTIC_BOUNDED"
    assert cap["read_write"] == "NONE"

    assert cap["grants_authority"] is False
    assert cap["is_execution_authority"] is False

    resolved = R.relay_resolve_capability(
        R.KIND_OPENJARVIS_SIMPLE_AGENT_SHADOW
    )

    assert (
        resolved["capability_id"]
        == "OPENJARVIS_SIMPLE_AGENT_SHADOW"
    )

    assert resolved["authority_class"] == "NONE"

    assert (
        "OPENJARVIS_SIMPLE_AGENT_SHADOW"
        in NAT.NATIVE_CAPABILITIES
    )


def test_openjarvis_v04_adapter_rejects_payload_scope(
    tmp_path,
):
    import obsidia_openjarvis_adapter_v0 as O

    adapter = O.OpenJarvisSimpleAgentShadowAdapter(
        source_root=str(tmp_path),
        expected_commit="0" * 40,
    )

    out = adapter.execute(
        capability_id="OPENJARVIS_SIMPLE_AGENT_SHADOW",
        payload={
            "input_text": "ping",
            "shell": "whoami",
        },
    )

    assert out["status"] == "PAYLOAD_SCOPE_NOT_ALLOWED"
    assert out["scope_expanded"] is False
    assert out["is_execution_authority"] is False


def test_openjarvis_v04_real_simple_agent_when_configured():
    import os
    import pytest

    import obsidia_openjarvis_adapter_v0 as O

    source = os.environ.get(
        "OBSIDIA_OPENJARVIS_SOURCE"
    )

    commit = os.environ.get(
        "OBSIDIA_OPENJARVIS_COMMIT"
    )

    if not source or not commit:
        pytest.skip(
            "real OpenJarvis source not configured"
        )

    adapter = O.OpenJarvisSimpleAgentShadowAdapter(
        source_root=source,
        expected_commit=commit,
    )

    out = adapter.execute(
        capability_id="OPENJARVIS_SIMPLE_AGENT_SHADOW",
        payload={
            "input_text": "ping from Obsidia V0.4",
        },
    )

    assert (
        out["status"]
        == "OPENJARVIS_SIMPLE_AGENT_SHADOW_OK"
    )

    assert out["agent_class"] == "SimpleAgent"
    assert out["agent_id"] == "simple"

    assert out["engine"] == "obsidia-shadow-engine-v0"
    assert out["engine_calls"] == 1

    assert out["turns"] == 1
    assert out["tool_results"] == 0

    assert out["real_openjarvis_agent_code"] is True
    assert out["real_model_enabled"] is False

    assert out["agent_execution_enabled"] is True
    assert out["tool_execution_enabled"] is False

    assert out["memory_enabled"] is False
    assert out["scheduler_enabled"] is False
    assert out["network_enabled"] is False

    assert out["is_execution_authority"] is False
    assert out["is_kx_authority"] is False

    assert out["scope_expanded"] is False
    assert out["memory_written"] is False
    assert out["source_mutated"] is False


def test_openjarvis_v04_e2e_relay_when_configured(
    tmp_path,
):
    import os
    import pytest

    import obsidia_relay_v0 as R

    source = os.environ.get(
        "OBSIDIA_OPENJARVIS_SOURCE"
    )

    commit = os.environ.get(
        "OBSIDIA_OPENJARVIS_COMMIT"
    )

    if not source or not commit:
        pytest.skip(
            "real OpenJarvis source not configured"
        )

    out = R.relay_submit_mission(
        requested_outcome=(
            "run real OpenJarvis SimpleAgent "
            "through deterministic Obsidia shadow engine"
        ),

        mission_kind=(
            R.KIND_OPENJARVIS_SIMPLE_AGENT_SHADOW
        ),

        target="ping from Relay V0.4",

        repo_root=source,

        store_dir=tmp_path / "relay-v04",
    )

    assert out["mission_state"] == R.MISSION_COMPLETE

    assert out["metrics"]["native_route_count"] == 1
    assert out["metrics"]["cognitive_request_count"] == 0
    assert out["metrics"]["hold_count"] == 0

    ev = out["native_evidence"]

    assert ev["ok"] is True

    assert (
        ev["native_route_kind"]
        == "OPENJARVIS_SIMPLE_AGENT_SHADOW"
    )

    assert (
        ev["openjarvis_status"]
        == "OPENJARVIS_SIMPLE_AGENT_SHADOW_OK"
    )

    assert ev["agent_class"] == "SimpleAgent"
    assert ev["agent_id"] == "simple"

    assert ev["engine"] == "obsidia-shadow-engine-v0"
    assert ev["engine_calls"] == 1

    assert ev["turns"] == 1
    assert ev["tool_results"] == 0

    assert ev["real_openjarvis_agent_code"] is True
    assert ev["real_model_enabled"] is False

    assert ev["agent_execution_enabled"] is True
    assert ev["tool_execution_enabled"] is False

    assert ev["memory_enabled"] is False
    assert ev["scheduler_enabled"] is False
    assert ev["network_enabled"] is False

    assert ev["external_runtime_authority"] == "NONE"

    assert ev["scope_expanded"] is False
    assert ev["memory_written"] is False
    assert ev["mutated_repo"] is False

    status = R.relay_get_status(
        out["relay_mission_id"],
        store_dir=tmp_path / "relay-v04",
    )

    assert status["mission_state"] == R.MISSION_COMPLETE

    assert len(status["receipt_ids"]) >= 4


# ======================================================================
# JARVIS / OBSIDIA NATIVE SELF-BUILD PHASE 1
# ======================================================================

def _make_native_selfbuild_repo(tmp_path):
    repo = (
        tmp_path
        / "native-selfbuild-repo"
    )

    repo.mkdir()

    _git(
        repo,
        "init",
    )

    _git(
        repo,
        "config",
        "user.email",
        "selfbuild@example.invalid",
    )

    _git(
        repo,
        "config",
        "user.name",
        "Self Build Test",
    )

    scripts = (
        repo
        / "scripts"
    )

    scripts.mkdir()

    target = (
        scripts
        / "obsidia_selfbuild_fixture.py"
    )

    target.write_text(
        '"""Self-build fixture."""\n'
        "\n"
        "from __future__ import annotations\n"
        "\n"
        "VALUE = 1\n",
        encoding="utf-8",
        newline="\n",
    )

    _git(
        repo,
        "add",
        "scripts/obsidia_selfbuild_fixture.py",
    )

    _git(
        repo,
        "commit",
        "-m",
        "self-build fixture",
    )

    return repo


def _native_selfbuild_objective():
    import json

    spec = {
        "strategies": [
            {
                "op": (
                    "insert_comment_after_docstring"
                ),
                "comment": (
                    "JARVIS NATIVE SELF BUILD "
                    "CANDIDATE ONLY"
                ),
            }
        ]
    }

    return (
        "Prepare a bounded peripheral tooling "
        "candidate for the Jarvis integration "
        "surface. Candidate only. "
        "No apply. No commit. No push. No merge.\n"
        "NATIVE_SOLVE_JSON="
        + json.dumps(
            spec,
            sort_keys=True,
            separators=(",", ":"),
        )
    )


def test_jarvis_selfbuild_phase1_capability_registered():
    import obsidia_capability_graph_v0 as G
    import obsidia_relay_v0 as R
    import obsidia_stack_native_routes_v0 as NAT

    cap = G.get_capability(
        "OBSIDIA_NATIVE_SELF_BUILD_PHASE1"
    )

    assert cap is not None
    assert cap["owner"] == "OBSIDIA_STACK"
    assert cap["authority_class"] == "NONE"
    assert cap["route"] == "STACK_NATIVE_ROUTE"
    assert cap["grants_authority"] is False
    assert cap["is_execution_authority"] is False

    resolved = R.relay_resolve_capability(
        R.KIND_OBSIDIA_NATIVE_SELF_BUILD_PHASE1
    )

    assert (
        resolved["capability_id"]
        == "OBSIDIA_NATIVE_SELF_BUILD_PHASE1"
    )

    assert resolved["authority_class"] == "NONE"

    assert (
        "OBSIDIA_NATIVE_SELF_BUILD_PHASE1"
        in NAT.NATIVE_CAPABILITIES
    )


def test_jarvis_selfbuild_phase1_e2e_no_repo_mutation(
    tmp_path,
    monkeypatch,
):
    import json

    import obsidia_relay_v0 as R

    repo = _make_native_selfbuild_repo(
        tmp_path
    )

    local = (
        tmp_path
        / "localappdata"
    )

    local.mkdir()

    monkeypatch.setenv(
        "LOCALAPPDATA",
        str(local),
    )

    before_head = _git(
        repo,
        "rev-parse",
        "HEAD",
    ).stdout.strip()

    before_status = _git(
        repo,
        "status",
        "--porcelain=v1",
    ).stdout

    assert before_status == ""

    out = R.relay_submit_mission(
        requested_outcome=(
            _native_selfbuild_objective()
        ),
        mission_kind=(
            R.KIND_OBSIDIA_NATIVE_SELF_BUILD_PHASE1
        ),
        target=(
            "scripts/obsidia_selfbuild_fixture.py"
        ),
        repo_root=repo,
        store_dir=(
            tmp_path
            / "relay-store"
        ),
    )

    assert (
        out["mission_state"]
        == R.MISSION_COMPLETE
    )

    assert (
        out["metrics"]["native_route_count"]
        == 1
    )

    assert (
        out["metrics"]["cognitive_request_count"]
        == 0
    )

    ev = out["native_evidence"]

    assert ev["ok"] is True

    assert (
        ev["native_route_kind"]
        == "OBSIDIA_NATIVE_SELF_BUILD_PHASE1"
    )

    assert (
        ev["phase1_status"]
        == "PLAN_PROPOSED"
    )

    assert ev["phase2_executed"] is False

    assert (
        ev["human_approval_synthesized"]
        is False
    )

    assert (
        ev["approval_token_exposed"]
        is False
    )

    assert ev["producer_authority"] == "NONE"
    assert ev["backend_authority"] == "NONE"

    assert ev["decision_authority"] == "KX108_ONLY"

    assert ev["memory_write"] is False
    assert ev["memory_written"] is False

    assert ev["kernel_mutation"] is False
    assert ev["emits_act"] is False

    assert ev["scope_expanded"] is False
    assert ev["kx108_invoked"] is False
    assert ev["world_action"] is False

    assert ev["repo_mutation"] is False
    assert ev["mutated_repo"] is False

    plan = ev["plan_summary"]

    assert (
        plan["scope_mode"]
        == "EXPLICIT_CHILD_TARGET"
    )

    assert (
        plan["candidate_files"]
        == [
            "scripts/obsidia_selfbuild_fixture.py"
        ]
    )

    assert (
        plan["human_approval_required"]
        is True
    )

    assert (
        plan["approval_token_exposed"]
        is False
    )

    serialized = json.dumps(
        ev,
        sort_keys=True,
    )

    assert (
        "HUMAN_APPROVED_BUILD_SESSION="
        not in serialized
    )

    assert "next_human_action" not in serialized

    patch_path = Path(
        plan["candidate_patch_source"]
    )

    assert patch_path.is_file()

    assert (
        "JARVIS NATIVE SELF BUILD CANDIDATE ONLY"
        in patch_path.read_text(
            encoding="utf-8"
        )
    )

    after_head = _git(
        repo,
        "rev-parse",
        "HEAD",
    ).stdout.strip()

    after_status = _git(
        repo,
        "status",
        "--porcelain=v1",
    ).stdout

    assert after_head == before_head
    assert after_status == before_status


def test_jarvis_selfbuild_phase1_rejects_dirty_repo(
    tmp_path,
    monkeypatch,
):
    import obsidia_relay_v0 as R

    repo = _make_native_selfbuild_repo(
        tmp_path
    )

    monkeypatch.setenv(
        "LOCALAPPDATA",
        str(
            tmp_path
            / "localappdata"
        ),
    )

    (
        repo
        / "dirty.txt"
    ).write_text(
        "dirty\n",
        encoding="utf-8",
    )

    out = R.relay_submit_mission(
        requested_outcome=(
            _native_selfbuild_objective()
        ),
        mission_kind=(
            R.KIND_OBSIDIA_NATIVE_SELF_BUILD_PHASE1
        ),
        target=(
            "scripts/obsidia_selfbuild_fixture.py"
        ),
        repo_root=repo,
        store_dir=(
            tmp_path
            / "relay-store"
        ),
    )

    assert (
        out["mission_state"]
        == R.MISSION_FAILED
    )

    ev = out["native_evidence"]

    assert ev["ok"] is False

    assert (
        ev["reason"]
        == "SELF_BUILD_REPO_MUST_BE_CLEAN"
    )

    assert ev["mutated_repo"] is False
