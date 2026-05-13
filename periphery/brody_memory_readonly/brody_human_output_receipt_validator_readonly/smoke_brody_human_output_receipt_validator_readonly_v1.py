from brody_human_output_receipt_validator_readonly_v1 import validate_human_output_receipt

cases = [
    {
        "name": "missing_output",
        "payload": {
            "command_id": "case_missing",
            "command": "python proofs/verify_all.py",
            "claimed_purpose": "missing output",
            "target_repo": "obsidia-x108-proofs",
        },
        "expected_status": "BRODY_HUMAN_OUTPUT_RECEIPT_VALIDATOR_READONLY_V1_WAITING_FOR_HUMAN_OUTPUT",
        "expected_valid": False,
        "expected_review": True,
    },
    {
        "name": "valid_output_with_token",
        "payload": {
            "command_id": "case_pass",
            "command": "python proofs/verify_all.py",
            "claimed_purpose": "verify all proof output",
            "target_repo": "obsidia-x108-proofs",
            "human_output": "PASS\nBRODY_TEST_PASS",
            "human_output_pasted": True,
            "human_execution_claimed": True,
            "exit_code": 0,
            "expected_success_token": "PASS",
        },
        "expected_status": "BRODY_HUMAN_OUTPUT_RECEIPT_VALIDATOR_READONLY_V1_PASS",
        "expected_valid": True,
        "expected_review": False,
    },
    {
        "name": "missing_expected_token",
        "payload": {
            "command_id": "case_missing_token",
            "command": "python proofs/verify_all.py",
            "claimed_purpose": "token missing",
            "target_repo": "obsidia-x108-proofs",
            "human_output": "SOMETHING ELSE",
            "human_output_pasted": True,
            "human_execution_claimed": True,
            "exit_code": 0,
            "expected_success_token": "PASS",
        },
        "expected_status": "BRODY_HUMAN_OUTPUT_RECEIPT_VALIDATOR_READONLY_V1_REVIEW_REQUIRED",
        "expected_valid": False,
        "expected_review": True,
    },
    {
        "name": "nonzero_exit",
        "payload": {
            "command_id": "case_nonzero",
            "command": "python proofs/verify_all.py",
            "claimed_purpose": "nonzero exit",
            "target_repo": "obsidia-x108-proofs",
            "human_output": "PASS",
            "human_output_pasted": True,
            "human_execution_claimed": True,
            "exit_code": 1,
            "expected_success_token": "PASS",
        },
        "expected_status": "BRODY_HUMAN_OUTPUT_RECEIPT_VALIDATOR_READONLY_V1_REVIEW_REQUIRED",
        "expected_valid": False,
        "expected_review": True,
    },
]

for case in cases:
    out = validate_human_output_receipt(case["payload"])

    assert out["status"] == case["expected_status"], (case["name"], out)
    assert out["receipt_valid"] is case["expected_valid"], (case["name"], out)
    assert out["requires_review"] is case["expected_review"], (case["name"], out)

    assert out["human_output_required"] is True
    assert out["brody_execute_allowed"] is False
    assert out["brody_authorize_allowed"] is False
    assert out["readonly_analysis_only"] is True
    assert out["command_executed"] is False
    assert out["network_executed"] is False
    assert out["filesystem_mutation_executed"] is False
    assert out["git_mutation_executed"] is False
    assert out["secrets_printed"] is False
    assert out["graphiti_write"] is False
    assert out["graphiti_index_write"] is False
    assert out["neo4j_write_executed"] is False
    assert out["memory_intake"] is False
    assert out["memory_decision"] is False
    assert out["allowed_to_decide"] is False
    assert out["emits_act"] is False
    assert out["emits_verdict"] is False
    assert out["decision_authority"] == "KX108_ONLY"
    assert out["kernel_mutation"] is False
    assert out["x108_runtime_binding"] is False
    assert out["x108_merge"] is False
    assert out["execution_verified"] is False

print("BRODY_HUMAN_OUTPUT_RECEIPT_VALIDATOR_READONLY_V1_PASS")
