from __future__ import annotations

import ast
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from apps.obsidia_api.brody_real_cognitive_join import run_real_cognitive_join
from scripts.obsidia_readonly_pc_context_adapter_v0 import (
    build_readonly_pc_context,
    readonly_pc_context_to_context_item,
)


class ReadonlyPcContextAdapterV0Tests(unittest.TestCase):
    def test_snapshot_is_readonly_no_authority(self) -> None:
        snapshot = build_readonly_pc_context(
            session_id="missing-session",
            include_services=False,
        )

        self.assertEqual(snapshot["kind"], "READONLY_PC_CONTEXT")
        self.assertEqual(snapshot["pc_context_authority"], "NONE")
        self.assertTrue(snapshot["readonly"])
        self.assertFalse(snapshot["allowed_to_act"])
        self.assertFalse(snapshot["emits_act"])
        self.assertFalse(snapshot["memory_write"])
        self.assertFalse(snapshot["kernel_mutation"])
        self.assertFalse(snapshot["filesystem_mutation"])
        self.assertFalse(snapshot["git_mutation"])
        self.assertFalse(snapshot["process_mutation"])
        self.assertFalse(snapshot["command_execution"])

    def test_bounded_paths_and_command_policy_are_observational(self) -> None:
        snapshot = build_readonly_pc_context(
            session_id="missing-session",
            path_candidates=["scripts/obsidia_cli.py"],
            command_samples=["git status --short"],
            include_services=False,
            limits={
                "max_paths": 1,
                "max_services": 1,
                "max_commands": 1,
                "max_string": 80,
            },
        )

        self.assertEqual(len(snapshot["paths"]), 1)
        policy = snapshot["command_policy"]
        self.assertEqual(policy["status"], "READY:COMMAND_GATE_READONLY")
        observation = policy["observations"][0]
        self.assertTrue(observation["command_redacted"])
        self.assertFalse(observation["brody_execute_allowed"])
        self.assertFalse(observation["executed"])

    def test_context_item_is_context_packet_v2_compatible(self) -> None:
        snapshot = build_readonly_pc_context(
            session_id="missing-session",
            include_services=False,
        )

        item = readonly_pc_context_to_context_item(snapshot)
        self.assertTrue(item.startswith("READONLY_PC_CONTEXT:"))
        compact = json.loads(item.split(":", 1)[1])
        self.assertEqual(compact["authority"], "NONE")
        self.assertTrue(compact["readonly"])
        self.assertFalse(compact["allowed_to_act"])
        self.assertFalse(compact["memory_write"])

    def test_c1_context_packet_receives_compact_pc_context(self) -> None:
        snapshot = build_readonly_pc_context(
            session_id="missing-session",
            include_services=False,
        )

        result = run_real_cognitive_join(
            message="Bonjour",
            language="fr",
            session_id="j4s-test",
            precomputed_readonly_pc_context=snapshot,
        )

        self.assertEqual(
            result["components"]["READONLY_PC_CONTEXT"],
            "READY:ADVISORY_ONLY",
        )
        context_items = result["context_packet_v2"]["context_items"]
        self.assertTrue(
            any(
                item.startswith("READONLY_PC_CONTEXT:")
                for item in context_items
            )
        )
        self.assertIn(
            "jarvis:readonly_pc_context",
            result["context_packet_v2"]["source_refs"],
        )

    def test_secret_like_inputs_are_redacted(self) -> None:
        snapshot = build_readonly_pc_context(
            path_candidates=[
                "C:/tmp/.env",
                "C:/tmp/token-file.txt",
            ],
            command_samples=["echo TOKEN=abc123"],
            include_services=False,
        )

        encoded = json.dumps(snapshot, sort_keys=True)
        self.assertNotIn("TOKEN=abc123", encoded)
        self.assertNotIn("token-file", encoded)
        self.assertNotIn(".env", encoded)
        self.assertIn("path_hash", encoded)
        self.assertIn("command_redacted", encoded)

    def test_adapter_has_no_j3_bypass_calls(self) -> None:
        source_path = ROOT / "scripts" / (
            "obsidia_readonly_pc_context_adapter_v0.py"
        )
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        call_names = {
            getattr(node.func, "id", "")
            or getattr(node.func, "attr", "")
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
        }

        self.assertNotIn("run_governed_runtime_cycle", call_names)
        self.assertNotIn("run_cognitive_governed_handoff", call_names)
        self.assertNotIn("run_bounded_command", call_names)

    def test_adapter_source_compiles_without_bytecode(self) -> None:
        source_path = ROOT / "scripts" / (
            "obsidia_readonly_pc_context_adapter_v0.py"
        )
        source = source_path.read_text(encoding="utf-8")
        compile(source, str(source_path), "exec")

    def test_hard_limits_cannot_be_expanded_by_caller(self) -> None:
        snapshot = build_readonly_pc_context(
            workspace=ROOT,
            path_candidates=[
                f"candidate-{index}"
                for index in range(30)
            ],
            include_services=False,
            limits={
                "max_paths": 100000,
                "max_services": 100000,
                "max_commands": 100000,
                "max_string": 100000,
            },
        )

        self.assertLessEqual(
            len(snapshot["paths"]),
            8,
        )
        self.assertEqual(
            snapshot["limits"]["max_paths"],
            8,
        )
        self.assertEqual(
            snapshot["limits"]["max_string"],
            160,
        )

    def test_forged_authority_snapshot_is_rejected(self) -> None:
        snapshot = build_readonly_pc_context(
            include_services=False,
        )
        snapshot["allowed_to_act"] = True

        with self.assertRaises(ValueError):
            readonly_pc_context_to_context_item(snapshot)

    def test_compact_item_carries_material_observations(self) -> None:
        snapshot = build_readonly_pc_context(
            workspace=ROOT,
            path_candidates=[
                "scripts/obsidia_cli.py",
            ],
            include_services=False,
        )

        item = readonly_pc_context_to_context_item(snapshot)
        compact = json.loads(item.split(":", 1)[1])

        self.assertIn("paths", compact)
        self.assertEqual(len(compact["paths"]), 1)
        self.assertEqual(
            compact["paths"][0]["workspace_relative_path"],
            "scripts\\obsidia_cli.py"
            if sys.platform == "win32"
            else "scripts/obsidia_cli.py",
        )


if __name__ == "__main__":
    unittest.main()



def test_services_are_opt_in_by_default():
    from scripts.obsidia_readonly_pc_context_adapter_v0 import (
        build_readonly_pc_context,
    )

    snapshot = build_readonly_pc_context(
        workspace=".",
        path_candidates=[],
        command_samples=[],
    )

    assert (
        snapshot["services"]["status"]
        == "SKIPPED_BY_CALLER"
    )

    assert snapshot["readonly"] is True
    assert snapshot["allowed_to_decide"] is False
    assert snapshot["allowed_to_act"] is False
    assert snapshot["memory_write"] is False
    assert snapshot["kernel_mutation"] is False
