from brody_human_command_packet_readonly_v1 import build_human_command_packet

cases = [
    {
        "name": "verify_all_packet",
        "payload": {
            "command": "python proofs/verify_all.py",
            "claimed_purpose": "verify all proofs",
            "target_repo": "obsidia-x108-proofs",
            "expected_output": "PASS",
            "rollback_note": "No rollback needed; readonly verification.",
        },
    },
    {
        "name": "git_push_packet",
        "payload": {
            "command": "git -C obsidia-x108-proofs push",
            "claimed_purpose": "push committed proof pointer",
            "target_repo": "obsidia-x108-proofs",
            "expected_output": "main -> main",
            "rollback_note": "Do not execute automatically; human operator only.",
        },
    },
    {
        "name": "destructive_packet",
        "payload": {
            "command": "rm -rf ./tmp",
            "claimed_purpose": "destructive test",
            "target_repo": "obsidia-x108-proofs",
            "expected_output": "blocked / human-only",
            "rollback_note": "Do not execute.",
        },
    },
]

for case in cases:
    out = build_human_command_packet(case["payload"])

    assert out["status"] == "BRODY_HUMAN_COMMAND_PACKET_READONLY_V1_PACKETIZED"
    assert out["packet_kind"] == "HUMAN_OPERATOR_COMMAND_PACKET"
    assert out["brody_execute_allowed"] is False
    assert out["brody_authorize_allowed"] is False
    assert out["executed"] is False
    assert out["requires_human_operator"] is True
    assert out["readonly_analysis_only"] is True
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
    assert isinstance(out["classification"], str)
    assert len(out["classification"]) > 0

print("BRODY_HUMAN_COMMAND_PACKET_READONLY_V1_PASS")
