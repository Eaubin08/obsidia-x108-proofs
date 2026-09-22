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