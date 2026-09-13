from fastapi.testclient import TestClient

from apps.obsidia_api.main import app


client = TestClient(app)


def _call(text: str) -> dict:
    response = client.post(
        "/api/ir/candidate",
        json={
            "text": text,
            "language": "fr",
            "alphabet_units": [],
            "tree_context": {},
            "memory_context": {},
            "graphiti_context": {},
        },
    )

    assert response.status_code == 200
    return response.json()


def test_ir_candidate_surfaces_unknown_lexical_term_readonly():
    payload = _call(
        "explique le florvaxium"
    )

    ir = payload["ir_candidate"]

    assert "unknowns" in ir
    assert isinstance(
        ir["unknowns"],
        list,
    )

    normalized = [
        str(item).lower()
        for item in ir["unknowns"]
    ]

    assert "florvaxium" in normalized

    # Ordinary request grammar must not become lexical debt.
    assert "explique" not in normalized
    assert "le" not in normalized

    assert payload["readonly"] is True
    assert payload["advisory_only"] is True
    assert payload["decision_authority"] == "KX108_ONLY"
    assert payload["emits_act"] is False
    assert payload["emits_verdict"] is False
    assert payload["memory_write"] is False
    assert payload["graphiti_write"] is False
    assert payload["kernel_mutation"] is False
    assert payload["x108_mutation"] is False
    assert payload["real_action"] is False


def test_ir_candidate_recognizes_educated_interlanguage_concept():
    payload = _call(
        "explique le reverse os"
    )

    ir = payload["ir_candidate"]

    assert "unknowns" in ir
    assert "lexical_calibration" in ir

    calibration = ir["lexical_calibration"]

    assert calibration["status"] == "CALIBRATED"
    assert calibration["readonly"] is True
    assert calibration["decision_authority"] == "KX108_ONLY"
    assert (
        calibration["unknown_policy"]
        == "UNKNOWN_OR_REFUSE_IF_NOT_REDUCIBLE_TO_IR"
    )

    assert "reverse_os" in calibration["known_concept_ids"]

    normalized = [
        str(item).lower()
        for item in ir["unknowns"]
    ]

    assert "reverse" not in normalized
    assert "os" not in normalized
