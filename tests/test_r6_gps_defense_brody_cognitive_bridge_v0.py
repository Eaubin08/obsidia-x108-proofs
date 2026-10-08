from __future__ import annotations

from apps.obsidia_api.brody_real_cognitive_join import (
    run_real_cognitive_join,
)


def _gps_sigma_envelope(**overrides):
    envelope = {
        "source": "GPS_DEFENSE_RECORDED_EVIDENCE_TEST",
        "mode": "READONLY_DOMAIN_SIGMA_ENVELOPE",
        "domain_sigma_envelope": True,
        "domain": "gps_defense_aviation",
        "proof_status": "RECORDED_REAL_RF_TEST_EVIDENCE",
        "x108_gate": "HOLD",
        "contradictions": ["SOURCE_CONFLICT"],
        "unknowns": ["INDEPENDENT_PHYSICAL_SOURCE_MISSING"],
        "risk_flags": ["TEMPORAL_INTEGRITY_ANOMALY"],
        "readonly": True,
        "advisory_only": True,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
        "emits_verdict": False,
        "memory_write": False,
        "graphiti_write": False,
        "neo4j_write": False,
        "kernel_mutation": False,
        "x108_mutation": False,
        "decision_authority": "KX108_ONLY",
    }
    envelope.update(overrides)
    return envelope


def _gps_micro():
    return {
        "micro_core_version": "TEST_GPS_DOMAIN",
        "domain_detected": "gps_defense_aviation",
        "hold_required": False,
        "is_adversarial": False,
        "survival_risk_flag": False,
        "projection_not_prediction_signal": {
            "is_prediction_claim": False,
        },
        "bio_animal_signal": {
            "dead_path_detection": [],
        },
    }


def test_defense_bridge_preserves_precomputed_gps_sigma_evidence():
    envelope = _gps_sigma_envelope()

    result = run_real_cognitive_join(
        message="Analyse en lecture seule l'intégrité GPS de cette mission.",
        language="fr",
        session_id="r6-defense-precomputed-gps",
        precomputed_micro_core=_gps_micro(),
        precomputed_domain_sigma_envelope=envelope,
    )

    assert result["status"] == "READY_SHADOW_READONLY"
    assert result["domain_detected"] == "gps_defense_aviation"
    assert (
        result["components"]["SIGMA"]
        == "READY:PRECOMPUTED_READONLY:gps_defense_aviation"
    )
    assert result["sigma_domain_packet"] == envelope
    assert result["sigma_domain_packet_source"] == "PRECOMPUTED_READONLY"
    assert len(result["sigma_domain_packet_sha256"]) == 64

    assert result["decision_authority"] == "KX108_ONLY"
    assert result["allowed_to_decide"] is False
    assert result["allowed_to_act"] is False
    assert result["emits_act"] is False
    assert result["emits_verdict"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False

    ticket = result["decision_ticket_dry_run"]
    assert ticket["dry_run"] is True
    assert ticket["decision_authority"] == "KX108_ONLY"
    assert ticket["emits_act"] is False


def test_defense_bridge_can_take_domain_from_precomputed_evidence_when_text_has_none():
    result = run_real_cognitive_join(
        message="Analyse cette preuve en lecture seule.",
        language="fr",
        session_id="r6-defense-domain-from-proof",
        precomputed_micro_core={
            **_gps_micro(),
            "domain_detected": None,
        },
        precomputed_domain_sigma_envelope=_gps_sigma_envelope(),
    )

    assert result["status"] == "READY_SHADOW_READONLY"
    assert result["domain_detected"] == "gps_defense_aviation"
    assert result["sigma_domain_packet_source"] == "PRECOMPUTED_READONLY"


def test_defense_bridge_domain_mismatch_fails_closed_before_kx_admission():
    result = run_real_cognitive_join(
        message="Analyse une preuve bancaire.",
        language="fr",
        session_id="r6-defense-domain-mismatch",
        precomputed_micro_core={
            **_gps_micro(),
            "domain_detected": "bank",
        },
        precomputed_domain_sigma_envelope=_gps_sigma_envelope(),
    )

    assert result["status"] == "BLOCKED_READONLY"
    assert result["blocked_stage"] == "SIGMA_PRECOMPUTED"
    assert result["kx108_admission"] == "DRY_RUN_NOT_COMPLETED"
    assert any(
        "PRECOMPUTED_SIGMA_DOMAIN_MISMATCH" in error
        for error in result["errors"]
    )
    assert result["emits_act"] is False
    assert result["decision_authority"] == "KX108_ONLY"


def test_defense_bridge_rejects_sovereign_or_mutating_sigma_input():
    for field, bad_value in (
        ("readonly", False),
        ("allowed_to_decide", True),
        ("emits_act", True),
        ("emits_verdict", True),
        ("memory_write", True),
        ("kernel_mutation", True),
        ("x108_mutation", True),
        ("decision_authority", "BRODY"),
    ):
        result = run_real_cognitive_join(
            message="Analyse en lecture seule la preuve GPS.",
            language="fr",
            session_id=f"r6-defense-boundary-{field}",
            precomputed_micro_core=_gps_micro(),
            precomputed_domain_sigma_envelope=_gps_sigma_envelope(
                **{field: bad_value}
            ),
        )

        assert result["status"] == "BLOCKED_READONLY"
        assert result["blocked_stage"] == "SIGMA_PRECOMPUTED"
        assert result["kx108_admission"] == "DRY_RUN_NOT_COMPLETED"
        assert result["emits_act"] is False
        assert result["decision_authority"] == "KX108_ONLY"


def test_defense_bridge_does_not_promote_observed_sigma_gate_to_brody_authority():
    envelope = _gps_sigma_envelope(
        x108_gate="BLOCK",
        contradictions=[],
        unknowns=[],
        risk_flags=[],
    )

    result = run_real_cognitive_join(
        message="Explique uniquement le statut GPS observé.",
        language="fr",
        session_id="r6-defense-no-gate-promotion",
        precomputed_micro_core=_gps_micro(),
        precomputed_domain_sigma_envelope=envelope,
    )

    assert result["sigma_domain_packet"]["x108_gate"] == "BLOCK"
    assert result["sigma_domain_packet_source"] == "PRECOMPUTED_READONLY"

    # Brody consumes evidence only. The actual cognition admission remains
    # a separate KX108 dry-run ticket and never emits ACT/verdict.
    assert result["kx108_admission"] == "DRY_RUN"
    assert result["decision_ticket_dry_run"]["decision_authority"] == "KX108_ONLY"
    assert result["decision_ticket_dry_run"]["emits_act"] is False
    assert result["emits_verdict"] is False
