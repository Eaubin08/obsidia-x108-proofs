from sigma.contracts import AgentVote, calculate_immutable_vote


def vote(v, confidence=1.0):
    return AgentVote(agent_id=f"agent_{v}", vote=v, proposed_verdict=v, confidence=confidence)


def test_all_allow_votes_positive_score():
    out = calculate_immutable_vote([vote("ALLOW"), vote("ALLOW"), vote("ALLOW")], x108_gate="HOLD")
    assert out["harmonic_score"] > 0.30
    assert out["advisory_verdict"] == "ALLOW"


def test_all_block_votes_negative_score():
    out = calculate_immutable_vote([vote("BLOCK"), vote("BLOCK"), vote("BLOCK")], x108_gate="HOLD")
    assert out["harmonic_score"] < -0.30
    assert out["advisory_verdict"] == "BLOCK"


def test_all_hold_votes_neutral_score():
    out = calculate_immutable_vote([vote("HOLD"), vote("HOLD"), vote("HOLD")], x108_gate="HOLD")
    assert out["harmonic_score"] == 0.0
    assert out["advisory_verdict"] == "HOLD"


def test_mixed_votes_weighted():
    out = calculate_immutable_vote(
        [vote("ALLOW", 0.8), vote("ALLOW", 0.8), vote("BLOCK", 0.2)],
        x108_gate="HOLD",
    )
    assert out["harmonic_score"] > 0.30
    assert out["advisory_verdict"] == "ALLOW"


def test_empty_votes_returns_hold():
    out = calculate_immutable_vote([], x108_gate="HOLD")
    assert out["vote_count"] == 0
    assert out["harmonic_score"] == 0.0
    assert out["advisory_verdict"] == "HOLD"


def test_output_is_readonly():
    assert calculate_immutable_vote([vote("ALLOW")])["readonly"] is True


def test_decision_authority_kx108_only():
    assert calculate_immutable_vote([vote("ALLOW")])["decision_authority"] == "KX108_ONLY"


def test_emits_act_false():
    assert calculate_immutable_vote([vote("ALLOW")])["emits_act"] is False


def test_emits_verdict_false():
    assert calculate_immutable_vote([vote("ALLOW")])["emits_verdict"] is False


def test_immutable_flag():
    assert calculate_immutable_vote([vote("ALLOW")])["immutable"] is True


def test_x108_gate_preserved():
    out = calculate_immutable_vote([vote("ALLOW")], x108_gate="BLOCK")
    assert out["x108_gate_preserved"] == "BLOCK"


def test_advisory_does_not_override_x108_block():
    out = calculate_immutable_vote([vote("ALLOW"), vote("ALLOW")], x108_gate="BLOCK")
    assert out["advisory_verdict"] == "ALLOW"
    assert out["x108_gate_preserved"] == "BLOCK"
    assert out["decision_authority"] == "KX108_ONLY"
    assert out["advisory_verdict_never_runtime_decision"] is True


def test_confidence_clamped():
    out = calculate_immutable_vote([vote("ALLOW", 9999)], x108_gate="HOLD")
    assert out["harmonic_score"] == 1.0


def test_score_clamped_to_minus_one_one():
    out = calculate_immutable_vote([vote("BLOCK", 9999), vote("BLOCK", 9999)], x108_gate="HOLD")
    assert -1.0 <= out["harmonic_score"] <= 1.0
    assert out["harmonic_score"] == -1.0


def test_boundary_fields_false():
    out = calculate_immutable_vote([vote("ALLOW")], x108_gate="HOLD")
    assert out["memory_write"] is False
    assert out["graphiti_write"] is False
    assert out["kernel_mutation"] is False
    assert out["x108_mutation"] is False
