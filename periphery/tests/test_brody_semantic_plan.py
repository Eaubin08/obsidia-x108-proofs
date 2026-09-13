import json

from apps.obsidia_api.brody_semantic_plan import (
    build_brody_semantic_plan,
)

from periphery.agents.obsidure_native_engineering_consumer import (
    consume_brody_engineering_spec,
)

from periphery.agents.obsidure_reasoning_provider import (
    DiagnosisStatus,
    RepairDiagnosis,
)


TARGET = "periphery/generated_from_brody.py"


def semantic_objective():

    payload = {
        "operations": [
            {
                "kind": "CREATE_MODULE",
                "target_path": TARGET,
                "payload": {
                    "docstring": (
                        "Generated from structured semantics."
                    )
                },
            },
            {
                "kind": "ADD_FUNCTION",
                "target_path": TARGET,
                "payload": {
                    "name": "calibrate",
                    "args": [
                        {
                            "name": "value",
                            "annotation": "str",
                        },
                        {
                            "name": "known",
                            "annotation": "bool",
                        },
                    ],
                    "returns": "str",
                    "body": [
                        {
                            "kind": "IF",
                            "test": {
                                "kind": "NAME",
                                "id": "known",
                            },
                            "body": [
                                {
                                    "kind": "RETURN",
                                    "expr": {
                                        "kind": "CONSTANT",
                                        "value": "RESOLVED",
                                    },
                                }
                            ],
                        },
                        {
                            "kind": "RETURN",
                            "expr": {
                                "kind": "CONSTANT",
                                "value": "UNKNOWN",
                            },
                        },
                    ],
                },
            },
        ]
    }

    return (
        "implement semantic calibration "
        "SEMANTIC_PLAN_JSON="
        + json.dumps(
            payload,
            separators=(",", ":"),
        )
    )


def engineering_spec():

    return {
        "request_id": "rr_semantic_plan",
        "spec_id": "BRODY_ENGINEERING_SPEC_V1",
        "objective": semantic_objective(),
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


def test_brody_semantic_plan_contains_no_source():

    plan = build_brody_semantic_plan(
        engineering_spec()
    )

    assert (
        plan.status
        == "SEMANTIC_PLAN_READY"
    )

    assert plan.can_generate_source is False
    assert len(plan.operations) == 2

    serialized = json.dumps(
        plan.to_dict()
    )

    assert '"source"' not in serialized
    assert '"full_content"' not in serialized
    assert '"patch"' not in serialized


def test_consumer_compiles_brody_semantics_to_native_plan():

    diagnosis = RepairDiagnosis(
        provider="BRODY",
        request_id="rr_semantic_plan",
        status=(
            DiagnosisStatus.NEEDS_NATIVE_ENGINE
        ),
        defect_class="IMPLEMENTATION_REQUEST",
        findings=[
            {
                "type": "BRODY_ENGINEERING_SPEC",
                "spec": engineering_spec(),
            }
        ],
    )

    result = consume_brody_engineering_spec(
        diagnosis
    )

    assert result.status == "NATIVE_PLAN_READY"

    assert result.missing_capabilities == []

    assert result.semantic_plan is not None
    assert result.native_plan is not None

    primitives = [
        step["primitive"]
        for step in (
            result.native_plan["steps"]
        )
    ]

    assert primitives == [
        "CREATE_FILE",
        "ADD_FUNCTION",
    ]


def test_raw_python_source_in_semantic_plan_is_rejected():

    spec = engineering_spec()

    spec["semantic_plan"] = {
        "operations": [
            {
                "kind": "ADD_FUNCTION",
                "target_path": TARGET,
                "payload": {
                    "source": (
                        "def forbidden(): pass"
                    )
                },
            }
        ]
    }

    plan = build_brody_semantic_plan(
        spec
    )

    assert (
        plan.status
        == "INVALID_SEMANTIC_PLAN"
    )

    assert any(
        item.startswith(
            "RAW_SOURCE_FIELD_FORBIDDEN"
        )
        for item
        in plan.missing_information
    )
