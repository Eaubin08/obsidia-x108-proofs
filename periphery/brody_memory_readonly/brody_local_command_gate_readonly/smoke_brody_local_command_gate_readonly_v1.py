from brody_local_command_gate_readonly_v1 import evaluate_command

CASES = [
    {
        "name": "git_push_with_dash_c",
        "command": "git -C obsidia-x108-proofs push",
        "expected": "GIT_MUTATION_COMMAND_HUMAN_ONLY",
    },
    {
        "name": "git_commit_with_dash_c",
        "command": "git -C obsidia-x108-proofs commit -m test",
        "expected": "GIT_MUTATION_COMMAND_HUMAN_ONLY",
    },
    {
        "name": "filesystem_destructive_remove_item",
        "command": "Remove-Item -Recurse -Force .\\tmp",
        "expected": "FILESYSTEM_MUTATION_COMMAND_HUMAN_ONLY",
    },
    {
        "name": "filesystem_destructive_rm_rf",
        "command": "rm -rf ./tmp",
        "expected": "DESTRUCTIVE_COMMAND_BLOCKED",
    },
    {
        "name": "network_command_review_required",
        "command": "Invoke-WebRequest https://example.com",
        "expected": None,
    },
    {
        "name": "unknown_command_review_required",
        "command": "some-random-command --flag",
        "expected": None,
    },
]

for case in CASES:
    out = evaluate_command({
        "command": case["command"],
        "claimed_purpose": case["name"],
        "target_repo": "obsidia-x108-proofs",
    })

    if case["expected"] is not None:
        assert out["classification"] == case["expected"], (case["name"], out["classification"], out)

    assert out["brody_execute_allowed"] is False, (case["name"], out)
    assert out["executed"] is False, (case["name"], out)
    assert out["decision_authority"] == "KX108_ONLY", (case["name"], out)
    assert out["memory_decision"] is False, (case["name"], out)
    assert out["emits_act"] is False, (case["name"], out)
    assert out["emits_verdict"] is False, (case["name"], out)
    assert out["x108_runtime_binding"] is False, (case["name"], out)
    assert out["x108_merge"] is False, (case["name"], out)

print("BRODY_LOCAL_COMMAND_GATE_READONLY_V1_SMOKE_PASS")
