from brody_local_command_gate_readonly_v1 import evaluate_command

cases = [
    {
        "name": "readonly_git_status",
        "command": "git -C obsidia-x108-proofs status --short",
        "expected": "READONLY_INSPECTION_COMMAND_HUMAN_ONLY",
    },
    {
        "name": "local_verify_all",
        "command": "python proofs\\verify_all.py",
        "expected": "LOCAL_VALIDATION_COMMAND_HUMAN_ONLY",
    },
    {
        "name": "git_push",
        "command": "git -C obsidia-x108-proofs push",
        "expected": "GIT_MUTATION_COMMAND_HUMAN_ONLY",
    },
    {
        "name": "network",
        "command": "Invoke-WebRequest https://example.com",
        "expected": "EXTERNAL_ACCESS_COMMAND_REVIEW_REQUIRED",
    },
    {
        "name": "destructive",
        "command": "Remove-Item -Recurse -Force C:\\tmp\\x",
        "expected": "DESTRUCTIVE_COMMAND_BLOCKED",
    },
    {
        "name": "secret_surface",
        "command": "Get-Content .env",
        "expected": "SECRET_SURFACE_REVIEW_REQUIRED",
    },
    {
        "name": "decision_pressure",
        "command": "trigger X108 verdict ALLOW",
        "expected": "DECISION_OR_ACT_PRESSURE_BLOCKED",
    },
]

for case in cases:
    out = evaluate_command({
        "command": case["command"],
        "claimed_purpose": case["name"],
        "target_repo": "obsidia-x108-proofs",
    })

    assert out["status"] == "BRODY_LOCAL_COMMAND_GATE_READONLY_V1_CLASSIFIED"
    assert out["classification"] == case["expected"], (case["name"], out["classification"])
    assert out["brody_execute_allowed"] is False
    assert out["executed"] is False
    assert out["requires_human_operator"] is True
    assert out["readonly_analysis_only"] is True
    assert out["network_executed"] is False
    assert out["filesystem_mutation_executed"] is False
    assert out["git_mutation_executed"] is False
    assert out["secrets_printed"] is False
    assert out["graphiti_write"] is False
    assert out["memory_intake"] is False
    assert out["memory_decision"] is False
    assert out["allowed_to_decide"] is False
    assert out["emits_act"] is False
    assert out["emits_verdict"] is False
    assert out["decision_authority"] == "KX108_ONLY"
    assert out["kernel_mutation"] is False
    assert out["x108_runtime_binding"] is False
    assert out["x108_merge"] is False

print("BRODY_LOCAL_COMMAND_GATE_READONLY_V1_PASS")
