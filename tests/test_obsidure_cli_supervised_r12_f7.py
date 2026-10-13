from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import obsidure_cli_supervised_r12 as cli
import obsidure_cli as terminal


def _payload(tmp_path: Path) -> Path:
    path = tmp_path / "prepare.json"
    path.write_text(
        json.dumps(
            {
                "human_request": "Prepare a bounded fixture.",
                "repository_context": {
                    "repository_identity": "repo://f7",
                    "local_root": str(tmp_path),
                    "worktree": str(tmp_path),
                    "branch": "f7",
                    "base_sha": "a" * 40,
                },
                "human_mandate": {
                    "mission_id": "mission-f7",
                    "status": "ACTIVE",
                    "mission_authority": "KX108_ONLY",
                },
            }
        ),
        encoding="utf-8",
    )
    return path


def test_prepare_requires_explicit_payload_and_calls_prepare_only(monkeypatch, tmp_path, capsys):
    calls = []

    def fake_api(api, method, path, *, query=None, body=None):
        calls.append((api, method, path, query, body))
        return 200, {
            "status": "PREPARED_AWAITING_APPROVAL",
            "state": "PREPARED_AWAITING_APPROVAL",
            "mission_id": "mission-f7",
            "checkpoint_id": "chk-f7",
            "approval_created": False,
            "executor_invoked": False,
        }

    monkeypatch.setattr(cli, "_api_json", fake_api)

    rc = cli.run_supervised(
        "prepare",
        "http://obsidia.test",
        {"payload_file": str(_payload(tmp_path)), "json": True},
    )

    assert rc == 0
    assert calls[0][1:3] == ("POST", "/api/supervised-missions/prepare-only")
    assert calls[0][4]["human_mandate"]["mission_authority"] == "KX108_ONLY"
    out = json.loads(capsys.readouterr().out)
    assert out["checkpoint_id"] == "chk-f7"
    assert out["approval_created"] is False
    assert out["executor_invoked"] is False


def test_prepare_missing_payload_fails_before_api(monkeypatch, capsys):
    monkeypatch.setattr(cli, "_api_json", lambda *a, **k: pytest.fail("api must not be called"))

    rc = cli.run_supervised("prepare", "http://obsidia.test", {"json": True})

    assert rc == 1
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "REJECTED"
    assert out["reason"] == "PAYLOAD_FILE_REQUIRED"
    assert out["physical_mutation"] is False


def test_inspect_by_checkpoint_uses_opaque_checkpoint_projection(monkeypatch, capsys):
    calls = []

    def fake_api(api, method, path, *, query=None, body=None):
        calls.append((method, path, query))
        return 200, {
            "status": "PROJECTED",
            "mission_id": "mission-f7",
            "checkpoint": {"checkpoint_id": "chk-f7"},
            "unique_next_ticket_id": "ticket-a",
            "tickets": [{"ticket_id": "ticket-a", "phase": "PREPARED"}],
            "binder_replay": {"limitations": ["BINDER_DECISION_RECONSTRUCTION_REQUIRED"]},
        }

    monkeypatch.setattr(cli, "_api_json", fake_api)

    rc = cli.run_supervised("inspect", "http://obsidia.test", {"checkpoint_id": "chk-f7", "json": True})

    assert rc == 0
    assert calls == [("GET", "/api/supervised-missions/checkpoints/chk-f7/projection", {})]
    out = json.loads(capsys.readouterr().out)
    assert out["unique_next_ticket_id"] == "ticket-a"
    assert out["executor_invoked"] is False


def test_holds_and_evidence_preserve_limited_verification(monkeypatch, capsys):
    projection = {
        "status": "PROJECTED",
        "mission_id": "mission-f7",
        "checkpoint": {"checkpoint_id": "chk-f7"},
        "tickets": [
            {"ticket_id": "ticket-a", "status": "HELD", "phase": "PREPARED", "hold_reason": "PREPARED_AWAITING_APPROVAL"}
        ],
        "hold": {"root_blocks": [{"ticket_id": "ticket-a", "reason": "PREPARED_AWAITING_APPROVAL"}]},
        "evidence": {"action_evidence_refs": ["aev-f7"]},
        "verification": {"ticket_levels": {"ticket-a": "VERIFIED_WITH_LIMITS"}},
        "binder_replay": {"limitations": ["BINDER_DECISION_RECONSTRUCTION_REQUIRED"]},
    }

    monkeypatch.setattr(cli, "_api_json", lambda *a, **k: (200, dict(projection)))

    rc = cli.run_supervised(
        "holds",
        "http://obsidia.test",
        {"mission_id": "mission-f7", "checkpoint_id": "chk-f7", "json": True},
    )
    assert rc == 0
    holds = json.loads(capsys.readouterr().out)
    assert holds["ticket_holds"][0]["hold_reason"] == "PREPARED_AWAITING_APPROVAL"

    rc = cli.run_supervised(
        "evidence",
        "http://obsidia.test",
        {"mission_id": "mission-f7", "checkpoint_id": "chk-f7", "json": True},
    )
    assert rc == 0
    evidence = json.loads(capsys.readouterr().out)
    assert evidence["execution_observed_is_verified"] is False
    assert evidence["binder_replay"]["limitations"] == ["BINDER_DECISION_RECONSTRUCTION_REQUIRED"]


def test_invalid_checkpoint_selector_and_authorize_fail_closed(monkeypatch, capsys):
    monkeypatch.setattr(cli, "_api_json", lambda *a, **k: pytest.fail("api must not be called"))

    rc = cli.run_supervised("inspect", "http://obsidia.test", {"json": True})
    assert rc == 1
    assert json.loads(capsys.readouterr().out)["reason"] == "MISSION_ID_OR_CHECKPOINT_ID_REQUIRED"

    rc = cli.run_supervised(
        "authorize",
        "http://obsidia.test",
        {"mission_id": "mission-f7", "checkpoint_id": "chk-f7", "json": True},
    )
    assert rc == 1
    out = json.loads(capsys.readouterr().out)
    assert out["reason"] == "AUTHORIZATION_HANDOFF_NOT_EXPOSED_IN_F7"
    assert out["approval_created"] is False


class _FakeProposal:
    proposal_id = "proposal-f7"
    patches = [{"path": "src/demo.py"}]


class _FakeAgent:
    phase = type("Phase", (), {"value": "READY"})()

    def __init__(self, *, api_base, max_cycles, verbose):
        self._cycle = 0
        self._max_cycles = max_cycles
        self.proposals = []

    def run_cycle(self, objective):
        self._cycle += 1
        proposal = _FakeProposal()
        self.proposals.append(proposal)
        return proposal


def test_interactive_avdr_offer_prepares_r12_and_projects_checkpoint(monkeypatch, tmp_path, capsys):
    payload_file = _payload(tmp_path)
    calls = []

    class FakeSupervised:
        SCHEMA_VERSION = cli.SCHEMA_VERSION
        NO_AUTHORITY = dict(cli.NO_AUTHORITY)

        @staticmethod
        def _load_payload(path):
            return cli._load_payload(path)

        @staticmethod
        def _api_json(api, method, path, *, query=None, body=None):
            calls.append((method, path, query, body))
            if method == "POST":
                return 200, {
                    "status": "PREPARED_AWAITING_APPROVAL",
                    "mission_id": "mission-f7",
                    "checkpoint_id": "Chk-F7",
                    "hold": {"reason": "PREPARED_AWAITING_APPROVAL"},
                    "executor_invoked": False,
                }
            return 200, {
                "status": "PROJECTED",
                "mission_id": "mission-f7",
                "checkpoint": {"checkpoint_id": "Chk-F7"},
                "hold": {"reason": "PREPARED_AWAITING_APPROVAL"},
                "binder_replay": {"limitations": ["BINDER_DECISION_RECONSTRUCTION_REQUIRED"]},
                "verification": {"ticket_levels": {"ticket-a": "VERIFIED_WITH_LIMITS"}},
            }

    monkeypatch.setattr(terminal, "AgentObsidure", _FakeAgent)
    monkeypatch.setattr(terminal, "_load_supervised_client", lambda: FakeSupervised)
    monkeypatch.setattr(sys, "argv", ["obsidure"])
    inputs = iter(["build fixture", "o", str(payload_file), "quit"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    rc = terminal.main()

    assert rc == 0
    assert calls[0][0:2] == ("POST", "/api/supervised-missions/prepare-only")
    assert calls[1][0:3] == ("GET", "/api/supervised-missions/checkpoints/Chk-F7/projection", None)
    out = capsys.readouterr().out
    assert "mission_id    : mission-f7" in out
    assert "checkpoint_id : Chk-F7" in out
    assert "PREPARED_AWAITING_APPROVAL" in out
    assert "BINDER_DECISION_RECONSTRUCTION_REQUIRED" in out
    assert "VERIFIED_WITH_LIMITS" in out


def test_interactive_checkpoint_reopen_preserves_case_and_evidence(monkeypatch, capsys):
    calls = []

    class FakeSupervised:
        SCHEMA_VERSION = cli.SCHEMA_VERSION
        NO_AUTHORITY = dict(cli.NO_AUTHORITY)

        @staticmethod
        def _api_json(api, method, path, *, query=None, body=None):
            calls.append((method, path, query, body))
            return 200, {
                "status": "PROJECTED",
                "mission_id": "mission-f7",
                "checkpoint": {"checkpoint_id": "Chk-MixedCase"},
                "evidence": {"action_evidence_refs": ["aev-f7"]},
                "verification": {"ticket_levels": {"ticket-a": "VERIFIED_WITH_LIMITS"}},
                "binder_replay": {"limitations": ["BINDER_DECISION_RECONSTRUCTION_REQUIRED"]},
            }

        _evidence = staticmethod(cli._evidence)
        _holds = staticmethod(cli._holds)

    monkeypatch.setattr(terminal, "_load_supervised_client", lambda: FakeSupervised)

    handled = terminal.handle_special_command("r12 evidence Chk-MixedCase", _FakeAgent(api_base="", max_cycles=None, verbose=False), "http://obsidia.test")

    assert handled is True
    assert calls == [("GET", "/api/supervised-missions/checkpoints/Chk-MixedCase/projection", None, None)]
    out = capsys.readouterr().out
    assert "Chk-MixedCase" in out
    assert "VERIFIED_WITH_LIMITS" in out
    assert "BINDER_DECISION_RECONSTRUCTION_REQUIRED" in out


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, timeout=20)
    assert proc.returncode == 0, proc.stderr or proc.stdout
    return proc.stdout.strip()


def _native_avdr_repo(tmp_path: Path) -> tuple[Path, Path, object]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "f7d2@test.invalid")
    _git(repo, "config", "user.name", "f7d2")
    _git(repo, "config", "commit.gpgsign", "false")
    (repo / ".gitignore").write_text("_PATCH_PROPOSALS/\n", encoding="utf-8")
    (repo / "periphery").mkdir()
    (repo / "periphery" / "demo.py").write_text('VALUE = "old"\n', encoding="utf-8", newline="\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "seed")

    proposal_dir = repo / "_PATCH_PROPOSALS" / "proposal-native"
    sandbox_dir = proposal_dir / "sandbox"
    sandbox_dir.mkdir(parents=True)
    (sandbox_dir / "demo.py").write_text('VALUE = "new"\n', encoding="utf-8", newline="\n")
    proposal_json = proposal_dir / "proposal.json"
    proposal_json.write_text(
        json.dumps(
            {
                "proposal_id": "proposal-native",
                "objective": "Prepare periphery demo change",
                "human_approved": False,
                "patches": [{"path": "periphery/demo.py", "sandbox_path": "sandbox/demo.py"}],
            }
        ),
        encoding="utf-8",
    )

    class Proposal:
        proposal_id = "proposal-native"
        objective = "Prepare periphery demo change"

    return repo, proposal_json, Proposal()


def _native_evidence_files(tmp_path: Path, patch_hash: str) -> tuple[Path, Path]:
    provider = tmp_path / "provider.json"
    provider.write_text(
        json.dumps(
            {
                "provider_id": "OBSIDURE_PERIPHERY_PROPOSAL_EXPORT_V1",
                "status": "VERIFIED",
                "availability_evidence_id": "provider-f7d2",
                "decision_authority": "KX108_ONLY",
            }
        ),
        encoding="utf-8",
    )
    evidence = tmp_path / "evidence.json"
    evidence.write_text(
        json.dumps(
            {
                "inventory_snapshot": {
                    "inventory_snapshot_id": "inv-f7d2",
                    "status": "VERIFIED",
                    "capabilities": ["OBSIDURE_PERIPHERY_PROPOSAL_EXPORT_V1"],
                },
                "deficiency_evidence": {
                    "deficiency_evidence_id": "def-f7d2",
                    "status": "VERIFIED",
                    "summary": "operator-selected AVDR proposal",
                },
                "validation_evidence": {
                    "validation_evidence_id": "val-f7d2",
                    "status": "PASS",
                    "candidate_patch_hash": patch_hash,
                    "tests": ["python -m pytest tests/test_obsidure_cli_supervised_r12_f7.py"],
                },
            }
        ),
        encoding="utf-8",
    )
    return provider, evidence


def test_native_avdr_handoff_exports_candidate_requires_explicit_mandate_and_calls_prepare_only(monkeypatch, tmp_path, capsys):
    repo, proposal_json, proposal = _native_avdr_repo(tmp_path)
    import obsidure_candidate_export_v1 as export_mod

    artifact = export_mod.export_proposal_candidate(repo, proposal_json, tmp_path / "precomputed")
    provider, evidence = _native_evidence_files(tmp_path, artifact.patch_sha256)
    calls = []

    class FakeSupervised:
        SCHEMA_VERSION = cli.SCHEMA_VERSION
        NO_AUTHORITY = dict(cli.NO_AUTHORITY)

        @staticmethod
        def _load_payload(path):
            return cli._load_payload(path)

        @staticmethod
        def _api_json(api, method, path, *, query=None, body=None):
            calls.append((method, path, query, body))
            if method == "POST":
                return 200, {
                    "status": "PREPARED_AWAITING_APPROVAL",
                    "mission_id": "mission-native",
                    "checkpoint_id": "chk-native",
                    "executor_invoked": False,
                    "approval_created": False,
                }
            return 200, {
                "status": "PROJECTED",
                "mission_id": "mission-native",
                "checkpoint": {"checkpoint_id": "chk-native"},
                "hold": {"reason": "PREPARED_AWAITING_APPROVAL"},
                "binder_replay": {"limitations": ["BINDER_DECISION_RECONSTRUCTION_REQUIRED"]},
            }

    monkeypatch.setattr(terminal, "_REPO_ROOT", repo)
    monkeypatch.setattr(terminal, "_load_supervised_client", lambda: FakeSupervised)
    inputs = iter(
        [
            "o",
            "",
            "mission-native",
            "mandate-native",
            "",
            "",
            "python -m pytest tests/test_obsidure_cli_supervised_r12_f7.py",
            "demo value changed",
            str(provider),
            str(evidence),
            "o",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    terminal._maybe_prepare_r12_after_proposal("http://obsidia.test", proposal)

    assert calls[0][0:2] == ("POST", "/api/supervised-missions/prepare-only")
    body = calls[0][3]
    assert body["human_mandate"]["human_mandate_reference"] == "mandate-native"
    assert body["phase1_candidate"]["candidate_patch_hash"] == artifact.patch_sha256
    assert body["validation_evidence"]["candidate_patch_hash"] == artifact.patch_sha256
    assert body["phase1_candidate"]["phase2_executed"] is False
    assert body["phase1_candidate"]["human_approval_synthesized"] is False
    assert calls[1][0:3] == ("GET", "/api/supervised-missions/checkpoints/chk-native/projection", None)
    out = capsys.readouterr().out
    assert "mission_id    : mission-native" in out
    assert "checkpoint_id : chk-native" in out


def test_native_avdr_handoff_refuses_missing_evidence_bundle(monkeypatch, tmp_path, capsys):
    repo, _, proposal = _native_avdr_repo(tmp_path)
    provider = tmp_path / "provider.json"
    provider.write_text(json.dumps({"provider_id": "p", "status": "VERIFIED"}), encoding="utf-8")
    evidence = tmp_path / "evidence.json"
    evidence.write_text(json.dumps({"inventory_snapshot": {"status": "VERIFIED"}}), encoding="utf-8")

    class FakeSupervised:
        SCHEMA_VERSION = cli.SCHEMA_VERSION
        NO_AUTHORITY = dict(cli.NO_AUTHORITY)

        @staticmethod
        def _api_json(*args, **kwargs):
            pytest.fail("api must not be called")

    monkeypatch.setattr(terminal, "_REPO_ROOT", repo)
    monkeypatch.setattr(terminal, "_load_supervised_client", lambda: FakeSupervised)
    inputs = iter(["o", "", "mission-native", "mandate-native", "", "", "", "", str(provider), str(evidence)])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    terminal._maybe_prepare_r12_after_proposal("http://obsidia.test", proposal)

    assert "EVIDENCE_BUNDLE_INCOMPLETE" in capsys.readouterr().out


def test_native_avdr_handoff_refuses_scope_violation_before_api(monkeypatch, tmp_path, capsys):
    repo, proposal_json, proposal = _native_avdr_repo(tmp_path)
    import obsidure_candidate_export_v1 as export_mod

    artifact = export_mod.export_proposal_candidate(repo, proposal_json, tmp_path / "precomputed")
    provider, evidence = _native_evidence_files(tmp_path, artifact.patch_sha256)

    class FakeSupervised:
        NO_AUTHORITY = dict(cli.NO_AUTHORITY)

        @staticmethod
        def _api_json(*args, **kwargs):
            pytest.fail("api must not be called")

    monkeypatch.setattr(terminal, "_REPO_ROOT", repo)
    monkeypatch.setattr(terminal, "_load_supervised_client", lambda: FakeSupervised)
    inputs = iter(["o", "", "mission-native", "mandate-native", "periphery/other.py", "", "", "", str(provider), str(evidence)])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    terminal._maybe_prepare_r12_after_proposal("http://obsidia.test", proposal)

    assert "SCOPE_VIOLATION" in capsys.readouterr().out
