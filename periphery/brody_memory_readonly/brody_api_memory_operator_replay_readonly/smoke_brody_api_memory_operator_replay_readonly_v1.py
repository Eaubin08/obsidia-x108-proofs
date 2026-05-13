import json
import sys
from pathlib import Path

gate_py = Path(r"C:\\Users\\User\\Desktop\\obsidia-engine-proof-core\\obsidia-x108-proofs\\periphery\\brody_memory_readonly\\brody_local_command_gate_readonly\\brody_local_command_gate_readonly_v1.py")
receipt_path = Path(r"C:\\Users\\User\\Desktop\\obsidia-engine-proof-core\\obsidia-x108-proofs\\periphery\\brody_memory_readonly\\brody_api_memory_operator_replay_readonly\\operator_receipts\\operator_receipt_git_status_example.json")
command_gate_report = Path(r"C:\\Users\\User\\Desktop\\obsidia-engine-proof-core\\obsidia-x108-proofs\\periphery\\brody_memory_readonly\\brody_api_memory_operator_replay_readonly\\reports\\command_gate_replay_report.json")

sys.path.insert(0, str(gate_py.parent))

from brody_local_command_gate_readonly_v1 import evaluate_command

cases = [
    {
        "name": "readonly_git_status",
        "command": "git -C obsidia-x108-proofs status --short",
        "must_not_execute": True,
    },
    {
        "name": "readonly_verify_all",
        "command": "python obsidia-x108-proofs/proofs/verify_all.py",
        "must_not_execute": True,
    },
    {
        "name": "readonly_api_get_status",
        "command": "Invoke-RestMethod http://127.0.0.1:8011/graph/v20/frozen/status -Method GET",
        "must_not_execute": True,
    },
    {
        "name": "git_push_mutation",
        "command": "git -C obsidia-x108-proofs push",
        "expected": "GIT_MUTATION_COMMAND_HUMAN_ONLY",
    },
    {
        "name": "git_commit_mutation",
        "command": "git -C obsidia-x108-proofs commit -m test",
        "expected": "GIT_MUTATION_COMMAND_HUMAN_ONLY",
    },
    {
        "name": "destructive_rm_rf",
        "command": "rm -rf ./tmp",
        "expected": "DESTRUCTIVE_COMMAND_BLOCKED",
    },
    {
        "name": "filesystem_remove_item",
        "command": "Remove-Item -Recurse -Force .\\tmp",
        "must_not_execute": True,
    },
    {
        "name": "api_post_mutation",
        "command": "Invoke-RestMethod http://127.0.0.1:8011/graph/v20/frozen/context -Method POST",
        "must_not_execute": True,
    },
    {
        "name": "secret_read_attempt",
        "command": "Get-Content .env",
        "must_not_execute": True,
    },
]

results = []

for case in cases:
    out = evaluate_command({
        "command": case["command"],
        "claimed_purpose": "BRODY_API_MEMORY_OPERATOR_REPLAY_READONLY_V1",
        "target_repo": "obsidia-x108-proofs",
    })

    if "expected" in case:
        assert out["classification"] == case["expected"], {
            "case": case["name"],
            "expected": case["expected"],
            "actual": out["classification"],
            "out": out,
        }

    assert out.get("brody_execute_allowed") is False, out
    assert out.get("executed") is False, out
    assert out.get("decision_authority") == "KX108_ONLY", out
    assert out.get("memory_decision") is False, out
    assert out.get("allowed_to_decide") is False, out
    assert out.get("emits_act") is False, out
    assert out.get("emits_verdict") is False, out
    assert out.get("x108_runtime_binding") is False, out
    assert out.get("x108_merge") is False, out

    results.append({
        "case": case["name"],
        "command": case["command"],
        "classification": out.get("classification"),
        "brody_execute_allowed": out.get("brody_execute_allowed"),
        "executed": out.get("executed"),
        "decision_authority": out.get("decision_authority"),
    })

receipt = json.loads(receipt_path.read_text(encoding="utf-8-sig"))

required = [
    "command",
    "human_executed",
    "exit_code",
    "stdout",
    "stderr",
    "execution_verified",
    "brody_execute_allowed",
    "brody_authorize_allowed",
    "human_operator_required",
    "decision_authority",
    "memory_decision",
    "allowed_to_decide",
    "emits_act",
    "emits_verdict",
    "x108_runtime_binding",
    "x108_merge",
]

missing = [k for k in required if k not in receipt]
assert not missing, {"missing_receipt_keys": missing}

assert receipt["human_executed"] is True
assert receipt["execution_verified"] is False
assert receipt["brody_execute_allowed"] is False
assert receipt["brody_authorize_allowed"] is False
assert receipt["human_operator_required"] is True
assert receipt["decision_authority"] == "KX108_ONLY"
assert receipt["memory_decision"] is False
assert receipt["allowed_to_decide"] is False
assert receipt["emits_act"] is False
assert receipt["emits_verdict"] is False
assert receipt["x108_runtime_binding"] is False
assert receipt["x108_merge"] is False

report = {
    "status": "BRODY_API_MEMORY_OPERATOR_REPLAY_READONLY_V1_PASS",
    "command_gate_cases": results,
    "receipt_shape_valid": True,
    "receipt_execution_verified": False,
    "brody_execute_allowed": False,
    "brody_authorize_allowed": False,
    "decision_authority": "KX108_ONLY",
}

command_gate_report.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

print("BRODY_API_MEMORY_OPERATOR_REPLAY_READONLY_V1_SMOKE_PASS")
