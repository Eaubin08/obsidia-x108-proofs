from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class HumanOutputReceiptInput:
    command_id: str
    command: str
    claimed_purpose: str
    target_repo: str
    human_output: str = ""
    human_output_pasted: bool = False
    human_execution_claimed: bool = False
    exit_code: Optional[int] = None
    expected_success_token: Optional[str] = None


@dataclass(frozen=True)
class HumanOutputReceipt:
    status: str
    receipt_created: bool
    receipt_valid: bool
    requires_review: bool
    reason: str

    human_output_required: bool
    human_output_pasted: bool
    human_execution_claimed: bool
    output_structurally_verified: bool
    execution_verified: bool

    brody_execute_allowed: bool
    brody_authorize_allowed: bool
    readonly_analysis_only: bool
    command_executed: bool
    network_executed: bool
    filesystem_mutation_executed: bool
    git_mutation_executed: bool
    secrets_printed: bool

    graphiti_write: bool
    graphiti_index_write: bool
    neo4j_write_executed: bool
    memory_intake: bool
    memory_decision: bool
    allowed_to_decide: bool
    emits_act: bool
    emits_verdict: bool
    decision_authority: str
    kernel_mutation: bool
    x108_runtime_binding: bool
    x108_merge: bool

    created_at: str
    receipt: Dict[str, Any]


def _coerce_exit_code(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except Exception:
        return None


def validate_human_output_receipt(payload: Dict[str, Any]) -> Dict[str, Any]:
    inp = HumanOutputReceiptInput(
        command_id=str(payload.get("command_id", "UNSPECIFIED")),
        command=str(payload.get("command", "")),
        claimed_purpose=str(payload.get("claimed_purpose", "")),
        target_repo=str(payload.get("target_repo", "obsidia-x108-proofs")),
        human_output=str(payload.get("human_output", "")),
        human_output_pasted=bool(payload.get("human_output_pasted", False)),
        human_execution_claimed=bool(payload.get("human_execution_claimed", False)),
        exit_code=_coerce_exit_code(payload.get("exit_code", None)),
        expected_success_token=payload.get("expected_success_token", None),
    )

    output_present = bool(inp.human_output.strip())
    human_output_pasted = bool(inp.human_output_pasted or output_present)
    expected_token = None if inp.expected_success_token is None else str(inp.expected_success_token)
    token_required = bool(expected_token)
    token_found = bool(expected_token and expected_token in inp.human_output)
    exit_code_present = inp.exit_code is not None
    exit_code_zero = bool(exit_code_present and inp.exit_code == 0)
    exit_code_nonzero = bool(exit_code_present and inp.exit_code != 0)

    if not output_present:
        status = "BRODY_HUMAN_OUTPUT_RECEIPT_VALIDATOR_READONLY_V1_WAITING_FOR_HUMAN_OUTPUT"
        reason = "HUMAN_OUTPUT_MISSING"
        receipt_created = False
        receipt_valid = False
        requires_review = True
        output_structurally_verified = False
    elif exit_code_nonzero:
        status = "BRODY_HUMAN_OUTPUT_RECEIPT_VALIDATOR_READONLY_V1_REVIEW_REQUIRED"
        reason = "NONZERO_EXIT_CODE_REVIEW_REQUIRED"
        receipt_created = True
        receipt_valid = False
        requires_review = True
        output_structurally_verified = False
    elif token_required and not token_found:
        status = "BRODY_HUMAN_OUTPUT_RECEIPT_VALIDATOR_READONLY_V1_REVIEW_REQUIRED"
        reason = "EXPECTED_SUCCESS_TOKEN_MISSING"
        receipt_created = True
        receipt_valid = False
        requires_review = True
        output_structurally_verified = False
    else:
        status = "BRODY_HUMAN_OUTPUT_RECEIPT_VALIDATOR_READONLY_V1_PASS"
        reason = "HUMAN_OUTPUT_STRUCTURAL_RECEIPT_VALID"
        receipt_created = True
        receipt_valid = True
        requires_review = False
        output_structurally_verified = True

    receipt = {
        "command_id": inp.command_id,
        "command": inp.command,
        "claimed_purpose": inp.claimed_purpose,
        "target_repo": inp.target_repo,
        "human_output_pasted": human_output_pasted,
        "human_execution_claimed": inp.human_execution_claimed,
        "exit_code": inp.exit_code,
        "exit_code_present": exit_code_present,
        "exit_code_zero": exit_code_zero,
        "expected_success_token": expected_token,
        "expected_success_token_found": token_found,
        "human_output_line_count": len(inp.human_output.splitlines()) if output_present else 0,
        "human_output_char_count": len(inp.human_output),
    }

    out = HumanOutputReceipt(
        status=status,
        receipt_created=receipt_created,
        receipt_valid=receipt_valid,
        requires_review=requires_review,
        reason=reason,

        human_output_required=True,
        human_output_pasted=human_output_pasted,
        human_execution_claimed=inp.human_execution_claimed,
        output_structurally_verified=output_structurally_verified,
        execution_verified=False,

        brody_execute_allowed=False,
        brody_authorize_allowed=False,
        readonly_analysis_only=True,
        command_executed=False,
        network_executed=False,
        filesystem_mutation_executed=False,
        git_mutation_executed=False,
        secrets_printed=False,

        graphiti_write=False,
        graphiti_index_write=False,
        neo4j_write_executed=False,
        memory_intake=False,
        memory_decision=False,
        allowed_to_decide=False,
        emits_act=False,
        emits_verdict=False,
        decision_authority="KX108_ONLY",
        kernel_mutation=False,
        x108_runtime_binding=False,
        x108_merge=False,

        created_at=datetime.now(timezone.utc).isoformat(),
        receipt=receipt,
    )

    return asdict(out)


if __name__ == "__main__":
    import json

    sample = {
        "command_id": "sample",
        "command": "python proofs/verify_all.py",
        "claimed_purpose": "sample_human_output_receipt",
        "target_repo": "obsidia-x108-proofs",
        "human_output": "PASS",
        "human_output_pasted": True,
        "human_execution_claimed": True,
        "exit_code": 0,
        "expected_success_token": "PASS",
    }

    print(json.dumps(validate_human_output_receipt(sample), indent=2, ensure_ascii=False))
