from apps.obsidia_api.brody_code_concept_engine import (
    CodeConcept,
    match_code_concept,
)

from apps.obsidia_api.brody_code_concepts_v1 import (
    DEFAULT_CODE_CONCEPTS,
)

from apps.obsidia_api.brody_code_intent_adapter import (
    BrodyCodeIntentPacket,
    build_brody_code_intent_packet,
)


TARGET = "periphery/harness/semantic_calibration.py"


def test_existing_brody_cognition_builds_code_intent_packet():

    packet = build_brody_code_intent_packet(
        "implement bounded semantic calibration",
        target_paths=[TARGET],
    )

    assert packet.request_text
    assert packet.target_paths == [
        TARGET
    ]

    assert packet.can_generate_source is False
    assert packet.can_decide is False
    assert packet.decision_authority == "KX108_ONLY"


def test_semantic_calibration_concept_resolves():

    packet = BrodyCodeIntentPacket(
        request_text=(
            "implement bounded semantic calibration "
            "for unknown terms"
        ),
        intent_type="code_debug",
        semantic_query=(
            "semantic calibration unknown terms"
        ),
        target_paths=[
            TARGET
        ],
        confidence="HIGH",
    )

    result = match_code_concept(
        packet,
        DEFAULT_CODE_CONCEPTS,
    )

    assert (
        result.status
        == "CODE_CONCEPT_RESOLVED"
    )

    assert (
        result.concept_id
        == "SEMANTIC_CALIBRATION_V1"
    )

    assert result.desired_state is not None

    target = (
        result.desired_state[
            "targets"
        ][0]
    )

    assert target["path"] == TARGET

    assert (
        target["classes"][0]["name"]
        == "SemanticCalibrationResult"
    )

    assert (
        target["functions"][0]["name"]
        == "calibrate_semantics"
    )


def test_unknown_concept_is_not_invented():

    packet = BrodyCodeIntentPacket(
        request_text=(
            "invent a completely unknown capability"
        ),
        intent_type="code_debug",
        target_paths=[
            TARGET
        ],
    )

    result = match_code_concept(
        packet,
        DEFAULT_CODE_CONCEPTS,
    )

    assert (
        result.status
        == "UNKNOWN_CODE_CONCEPT"
    )

    assert result.desired_state is None

    assert result.unknowns == [
        "BRODY_CODE_CONCEPT_NOT_EDUCATED"
    ]


def test_concept_engine_is_generic_and_injectable():

    concept = CodeConcept(
        concept_id="EXAMPLE_CAPABILITY",

        required_terms=(
            "example",
        ),

        desired_state_template={
            "targets": [
                {
                    "path": "$TARGET0",
                    "functions": [],
                    "classes": [],
                    "imports": [],
                }
            ]
        },
    )

    packet = BrodyCodeIntentPacket(
        request_text="build example capability",
        intent_type="code_debug",
        target_paths=[
            "periphery/example.py"
        ],
    )

    result = match_code_concept(
        packet,
        [concept],
    )

    assert (
        result.status
        == "CODE_CONCEPT_RESOLVED"
    )

    assert (
        result.desired_state[
            "targets"
        ][0]["path"]
        == "periphery/example.py"
    )
