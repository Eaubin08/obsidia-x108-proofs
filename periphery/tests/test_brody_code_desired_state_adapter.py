from apps.obsidia_api.brody_code_desired_state_adapter import (
    derive_learned_desired_state,
)


TARGET = "periphery/harness/semantic_calibration.py"


def engineering_spec(objective: str):

    return {
        "request_id": "rr_learned_code",
        "spec_id": "BRODY_ENGINEERING_SPEC_V1",
        "objective": objective,
        "targets": [
            {
                "path": TARGET,
                "target_state": "CREATE",
                "source_present": False,
                "source_sha256": "",
                "source_lines": 0,
            }
        ],
        "acceptance_criteria": [],
    }


def test_known_concept_produces_desired_state():

    result = derive_learned_desired_state(
        engineering_spec(
            "implement bounded semantic calibration "
            "for unknown terms"
        )
    )

    assert (
        result.status
        == "DESIRED_STATE_DERIVED"
    )

    assert (
        "desired_state"
        in result.engineering_spec
    )

    assert (
        result.engineering_spec[
            "code_cognition"
        ]["concept"]["concept_id"]
        == "SEMANTIC_CALIBRATION_V1"
    )

    target = (
        result.engineering_spec[
            "desired_state"
        ]["targets"][0]
    )

    assert target["path"] == TARGET

    assert (
        target["functions"][0]["name"]
        == "calibrate_semantics"
    )


def test_unknown_concept_is_not_invented():

    result = derive_learned_desired_state(
        engineering_spec(
            "implement teleportation banana runtime"
        )
    )

    assert (
        result.status
        == "UNKNOWN_CODE_CONCEPT"
    )

    assert (
        "desired_state"
        not in result.engineering_spec
    )

    assert result.unknowns == [
        "BRODY_CODE_CONCEPT_NOT_EDUCATED"
    ]

    assert (
        result.engineering_spec[
            "code_cognition"
        ]["concept"]["status"]
        == "UNKNOWN_CODE_CONCEPT"
    )


def test_missing_target_does_not_fabricate_one():

    spec = engineering_spec(
        "implement bounded semantic calibration"
    )

    spec["targets"] = []

    result = derive_learned_desired_state(
        spec
    )

    assert (
        result.status
        == "NEEDS_CONTEXT"
    )

    assert (
        "desired_state"
        not in result.engineering_spec
    )

    assert (
        "CODE_TARGET_UNKNOWN"
        in result.unknowns
    )
