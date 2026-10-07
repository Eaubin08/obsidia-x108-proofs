import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "release" / "premiere_mise_au_monde_release_candidate_v0.json"


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_f25_release_candidate_keeps_kx108_only_and_no_act():
    m = _manifest()
    assert m["decision_authority"] == "KX108_ONLY"
    inv = m["authority_invariants"]
    assert inv["allowed_to_decide"] is False
    assert inv["allowed_to_act"] is False
    assert inv["intelligence_is_authority"] is False
    assert inv["domain_is_authority"] is False
    assert inv["proof_is_permission"] is False
    assert inv["observation_is_truth"] is False


def test_f25_supported_gps_claims_remain_recorded_not_live():
    m = _manifest()
    claims = {c["id"]: c for c in m["public_claims"]}
    assert claims["recorded_real_gnss"]["proof_level"] == "RECORDED_REAL_GNSS"
    assert claims["recorded_real_rf"]["proof_level"] == "RECORDED_REAL_RF"
    joined = " ".join(c["wording"] for c in m["public_claims"]).upper()
    assert "LIVE_GNSS_CLOSED" not in joined
    assert "LIVE_RF_CLOSED" not in joined


def test_f25_forbids_unsupported_physical_and_certification_claims():
    forbidden = set(_manifest()["forbidden_claims"])
    required = {
        "LIVE_GNSS_CLOSED",
        "LIVE_RF_CLOSED",
        "HOSTILE_LIVE_SPOOFING_RESISTANCE_PROVEN",
        "CAUSAL_SPOOFING_ATTRIBUTION_PROVEN",
        "PRODUCTION_AVIATION_CERTIFIED",
        "PRODUCTION_DEFENSE_CERTIFIED",
        "PRIVATE_SENSOR_ATTESTATION_PROVEN",
        "IMU_RADAR_CORROBORATION_PROVEN",
        "PHYSICAL_AUTHENTICITY_GLOBALLY_PROVEN",
    }
    assert required <= forbidden


def test_f25_does_not_claim_general_world_science_gms_or_vision_completion():
    forbidden = set(_manifest()["forbidden_claims"])
    assert {
        "GENERAL_WORLD_MODEL_COMPLETE",
        "GENERAL_SCIENCE_SOLVER_COMPLETE",
        "GMS_SEMANTIC_TRUTH_PROVEN",
        "VISION_RECONSTRUCTION_TRUTH_PROVEN",
    } <= forbidden


def test_f25_manifest_binds_verified_f24_regression():
    validation = _manifest()["validation"]
    assert validation["f24_code_sha"] == "accb5c0a0902c29de04ca59b56859e9324e611d9"
    assert validation["f24_run_id"] == 37575196459
    result = validation["global_result"]
    assert result["passed"] == 12556
    assert result["failed_historical_baseline"] == 11
    assert result["new_failures"] == 0


def test_f25_excludes_monde_ui_from_this_repo_release_chain():
    m = _manifest()
    assert any("F23 Monde UI is outside this repository" in x for x in m["known_limits"])
    assert "F23_MONDE_UI" not in set(m["verified_phases"])
