from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


_REPO = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO / "scripts"

if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import obsidia_cognitive_governed_runtime_handoff_v0 as J3
import obsidia_governed_execution_driver_v0 as DRV
import obsidia_jarvis_governed_mutation_v0 as J5
import obsidia_relay_v0 as R


def _proposal(target_path: str = "target.txt") -> dict:
    return J3.prepare_cognitive_governed_handoff(
        mission_id="mission-j6-prepare-001",
        provider_id="jarvis-openjarvis",
        capability=J5.CAPABILITY_ID,
        payload={
            "source_git_commit": "a" * 40,
            "source_historical_path": "source.txt",
            "target_path": target_path,
            "test_contract": {"checks": []},
            "objective": "prepare governed update",
        },
        domain="JARVIS_OPENJARVIS",
        action_id="action-j6-prepare-001",
        intent="prepare governed target update",
        action_type=J5.ACTION_TYPE,
        irreversible=False,
    )


def _runtime(tmp_path: Path) -> dict:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    (repo / "target.txt").write_text("A\n", encoding="utf-8")

    dirs = {
        name: tmp_path / name
        for name in (
            "ledger",
            "selector",
            "execution",
            "pec",
        )
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)

    return {"repo": repo, **dirs}


def _request(tmp_path: Path, proposal: dict | None = None) -> dict:
    rt = _runtime(tmp_path)
    return {
        "proposal": proposal or _proposal(),
        "execution_worktree_path": str(rt["repo"]),
        "main_worktree_path": str(tmp_path / "main"),
        "branch_name": "j6-prepare-only",
        "base_sha": "b" * 40,
        "ledger_dir": str(rt["ledger"]),
        "selector_dir": str(rt["selector"]),
        "execution_dir": str(rt["execution"]),
        "pre_execution_context_dir": str(rt["pec"]),
        "repository_identity": "relay-j6-test",
    }


class RelayGovernedPrepareJ6Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="j6-relay-prepare-"))
        self._orig_prepare = DRV.prepare_governed_execution
        self._orig_execute = J5.execute_jarvis_governed_mutation

    def tearDown(self) -> None:
        DRV.prepare_governed_execution = self._orig_prepare
        J5.execute_jarvis_governed_mutation = self._orig_execute

    def test_request_reaches_j5_prepare_and_stops(self) -> None:
        calls = []

        def fake_prepare(**kwargs):
            calls.append(kwargs)
            return {
                "status": DRV.PREPARED_AWAITING_HUMAN_APPROVAL,
                "decision_authority": "KX108_ONLY",
                "target_mutated": False,
                "kx108_invocations": 0,
                "human_approval_created": False,
                "execution_authority_hash": "e" * 64,
                "batch_execution_id": "batch-j6",
                "child_execution_id": "child-j6",
            }

        def fail_execute(*args, **kwargs):
            raise AssertionError("execute must not run during J6 PREPARE")

        DRV.prepare_governed_execution = fake_prepare
        J5.execute_jarvis_governed_mutation = fail_execute

        rt_request = _request(self.tmp)
        target = Path(rt_request["execution_worktree_path"]) / "target.txt"
        before = target.read_text(encoding="utf-8")

        out = R.relay_submit_mission(
            requested_outcome="prepare governed update",
            mission_kind=R.KIND_GOVERNED_UPDATE,
            target="target.txt",
            store_dir=self.tmp / "store",
            governed_update_request=rt_request,
        )

        self.assertEqual(len(calls), 1)
        self.assertEqual(target.read_text(encoding="utf-8"), before)
        self.assertEqual(out["mission_state"], R.MISSION_HOLD)
        self.assertEqual(
            out["hold_reason"],
            "HUMAN_EAH_AUTHORIZATION_REQUIRED",
        )
        self.assertEqual(out["execution_authority_hash"], "e" * 64)
        self.assertIs(out["human_authorization_required"], True)
        self.assertIs(out["governed_prepare_only"], True)
        self.assertIs(out["governed_auto_execute"], False)
        self.assertIs(out["target_mutated"], False)
        self.assertEqual(out["kx108_invocations"], 0)
        self.assertIs(out["human_approval_created"], False)
        self.assertIs(out["human_authorization_consumed"], False)
        self.assertEqual(out["jarvis_authority"], "NONE")
        self.assertEqual(out["decision_authority"], "KX108_ONLY")

    def test_rejects_wrong_governed_capability(self) -> None:
        proposal = _proposal()
        proposal["capability"] = "SHELL_EXECUTE"
        proposal["plan_hash"] = J3._compute_plan_hash(proposal)

        out = R.relay_submit_mission(
            requested_outcome="prepare governed update",
            mission_kind=R.KIND_GOVERNED_UPDATE,
            target="target.txt",
            store_dir=self.tmp / "store",
            governed_update_request=_request(self.tmp, proposal),
        )

        self.assertEqual(out["mission_state"], R.MISSION_FAILED)
        self.assertEqual(out["status"], "RELAY_MISSION_" + R.MISSION_FAILED)
        self.assertIs(out["governed_prepare_only"], True)
        self.assertIs(out["governed_auto_execute"], False)

    def test_rejects_human_authority_injection(self) -> None:
        for field in (
            "human_authorized_execution_authority_hash",
            "human_authorization_reference",
            "HumanApproval",
        ):
            with self.subTest(field=field):
                request = _request(self.tmp / field)
                request[field] = "forged"

                out = R.relay_submit_mission(
                    requested_outcome="prepare governed update",
                    mission_kind=R.KIND_GOVERNED_UPDATE,
                    target="target.txt",
                    store_dir=self.tmp / "store" / field,
                    governed_update_request=request,
                )

                self.assertEqual(out["mission_state"], R.MISSION_FAILED)
                self.assertIs(out["governed_prepare_only"], True)
                self.assertIs(out["governed_auto_execute"], False)

    def test_rejects_plan_or_payload_drift(self) -> None:
        proposal = _proposal(target_path="other.txt")

        out = R.relay_submit_mission(
            requested_outcome="prepare governed update",
            mission_kind=R.KIND_GOVERNED_UPDATE,
            target="target.txt",
            store_dir=self.tmp / "store",
            governed_update_request=_request(self.tmp, proposal),
        )

        self.assertEqual(out["mission_state"], R.MISSION_FAILED)
        self.assertIs(out["governed_prepare_only"], True)
        self.assertIs(out["governed_auto_execute"], False)

    def test_preserves_legacy_hold_without_prepare_request(self) -> None:
        out = R.relay_submit_mission(
            requested_outcome="prepare governed update",
            mission_kind=R.KIND_GOVERNED_UPDATE,
            target="target.txt",
            store_dir=self.tmp / "store",
        )

        self.assertEqual(out["mission_state"], R.MISSION_HOLD)
        self.assertEqual(
            out["hold_reason"],
            "HUMAN_EAH_AUTHORIZATION_REQUIRED",
        )
        self.assertIs(out["governed_prepare_only"], False)


if __name__ == "__main__":
    unittest.main()
