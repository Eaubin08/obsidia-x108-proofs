from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import sys


GATE_DIR = Path(__file__).resolve().parent.parent / "brody_local_command_gate_readonly"
if GATE_DIR.exists():
    sys.path.insert(0, str(GATE_DIR))

try:
    from brody_local_command_gate_readonly_v1 import evaluate_command
except Exception:
    evaluate_command = None


@dataclass(frozen=True)
class HumanCommandPacketRequest:
    command: str
    claimed_purpose: str
    target_repo: str = "obsidia-x108-proofs"
    expected_output: str = ""
    rollback_note: str = ""
    proof_required: bool = True
    human_operator_required: bool = True


def _classify(request: HumanCommandPacketRequest) -> Dict[str, Any]:
    if evaluate_command is None:
        return {
            "status": "BRODY_LOCAL_COMMAND_GATE_UNAVAILABLE",
            "classification": "UNKNOWN_COMMAND_REVIEW_REQUIRED",
            "brody_execute_allowed": False,
            "executed": False,
            "decision_authority": "KX108_ONLY",
            "memory_decision": False,
            "emits_act": False,
            "emits_verdict": False,
            "x108_runtime_binding": False,
            "x108_merge": False,
        }

    return evaluate_command({
        "command": request.command,
        "claimed_purpose": request.claimed_purpose,
        "target_repo": request.target_repo,
    })


def build_human_command_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    request = HumanCommandPacketRequest(
        command=str(payload.get("command", "")).strip(),
        claimed_purpose=str(payload.get("claimed_purpose", "")).strip(),
        target_repo=str(payload.get("target_repo", "obsidia-x108-proofs")).strip(),
        expected_output=str(payload.get("expected_output", "")).strip(),
        rollback_note=str(payload.get("rollback_note", "")).strip(),
        proof_required=bool(payload.get("proof_required", True)),
        human_operator_required=bool(payload.get("human_operator_required", True)),
    )

    classification = _classify(request)

    return {
        "status": "BRODY_HUMAN_COMMAND_PACKET_READONLY_V1_PACKETIZED",
        "packet_kind": "HUMAN_OPERATOR_COMMAND_PACKET",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "request": asdict(request),
        "classification": classification.get("classification", "UNKNOWN_COMMAND_REVIEW_REQUIRED"),
        "classification_status": classification.get("status"),
        "operator_action": "MANUAL_REVIEW_AND_MANUAL_EXECUTION_ONLY",
        "brody_execute_allowed": False,
        "brody_authorize_allowed": False,
        "executed": False,
        "requires_human_operator": True,
        "readonly_analysis_only": True,
        "proof_required": request.proof_required,
        "expected_output": request.expected_output,
        "rollback_note": request.rollback_note,
        "network_executed": False,
        "filesystem_mutation_executed": False,
        "git_mutation_executed": False,
        "secrets_printed": False,
        "graphiti_write": False,
        "graphiti_index_write": False,
        "neo4j_write_executed": False,
        "memory_intake": False,
        "memory_decision": False,
        "allowed_to_decide": False,
        "emits_act": False,
        "emits_verdict": False,
        "decision_authority": "KX108_ONLY",
        "kernel_mutation": False,
        "x108_runtime_binding": False,
        "x108_merge": False,
        "source_gate_decision": classification,
    }


if __name__ == "__main__":
    import json

    sample = {
        "command": "python proofs/verify_all.py",
        "claimed_purpose": "verify proofs",
        "target_repo": "obsidia-x108-proofs",
        "expected_output": "PASS",
        "rollback_note": "No mutation expected.",
    }

    print(json.dumps(build_human_command_packet(sample), indent=2, ensure_ascii=False))
