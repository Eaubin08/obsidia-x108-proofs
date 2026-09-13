from pathlib import Path

from periphery.agents.obsidure_native_engineering_consumer import (
    consume_brody_engineering_spec,
)

from periphery.agents.obsidure_reasoning_provider import (
    DiagnosisStatus,
    RepairDiagnosis,
)


TARGET = "periphery/consumer_desired.py"


def make_spec(
    *,
    source_present: bool,
):
    return {
        "request_id": "rr_consumer_desired",
        "spec_id": "BRODY_ENGINEERING_SPEC_V1",
        "objective": "semantic calibration",
        "targets": [
            {
                "path": TARGET,
                "target_state": (
                    "EXISTING"
                    if source_present
                    else "CREATE"
                ),
                "source_present": source_present,
            }
        ],
        "acceptance_criteria": [],
        "desired_state": {
            "targets": [
                {
                    "path": TARGET,
                    "module_docstring": "semantic calibration",
                    "imports": [
                        {
                            "module": "typing",
                            "names": ["Any"],
                        }
                    ],
                    "classes": [
                        {
                            "name": "SemanticResult",
                            "fields": [
                                {
                                    "name": "confidence",
                                    "annotation": "float",
                                    "default_expr": {
                                        "kind": "CONSTANT",
                                        "value": 0.0,
                                    },
                                }
                            ],
                        }
                    ],
                    "functions": [
                        {
                            "name": "calibrate",
                            "args": [
                                {
                                    "name": "value",
                                    "annotation": "Any",
                                }
                            ],
                            "returns": "str",
                            "body": [
                                {
                                    "kind": "RETURN",
                                    "expr": {
                                        "kind": "CONSTANT",
                                        "value": "RESOLVED",
                                    },
                                }
                            ],
                        }
                    ],
                }
            ]
        },
    }


def diagnosis(spec):
    return RepairDiagnosis(
        provider="BRODY",
        request_id=spec["request_id"],
        status=DiagnosisStatus.NEEDS_NATIVE_ENGINE,
        defect_class="IMPLEMENTATION_REQUEST",
        findings=[
            {
                "type": "BRODY_ENGINEERING_SPEC",
                "spec": spec,
            }
        ],
    )


def test_consumer_prefers_desired_state_for_new_target():

    spec = make_spec(
        source_present=False
    )

    result = consume_brody_engineering_spec(
        diagnosis(spec)
    )

    assert result.status == "NATIVE_PLAN_READY"
    assert result.desired_state is not None
    assert result.semantic_plan is None

    primitives = [
        step["primitive"]
        for step
        in result.native_plan["steps"]
    ]

    assert primitives == [
        "CREATE_FILE",
        "ADD_IMPORT",
        "ADD_CLASS",
        "ADD_FIELD",
        "ADD_FUNCTION",
    ]


def test_consumer_uses_real_repo_state_for_minimal_delta(
    tmp_path: Path,
):

    target = tmp_path / TARGET

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    target.write_text(
        (
            "from typing import Any\n\n"
            "class SemanticResult:\n"
            "    pass\n\n"
            "def calibrate(value: Any) -> str:\n"
            "    return 'RESOLVED'\n"
        ),
        encoding="utf-8",
    )

    spec = make_spec(
        source_present=True
    )

    result = consume_brody_engineering_spec(
        diagnosis(spec),
        repo_root=tmp_path,
    )

    assert result.status == "NATIVE_PLAN_READY"

    primitives = [
        step["primitive"]
        for step
        in result.native_plan["steps"]
    ]

    assert primitives == [
        "ADD_FIELD",
    ]


def test_consumer_returns_no_change_when_target_matches(
    tmp_path: Path,
):

    target = tmp_path / TARGET

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    target.write_text(
        (
            "from typing import Any\n\n"
            "class SemanticResult:\n"
            "    confidence: float = 0.0\n\n"
            "def calibrate(value: Any) -> str:\n"
            "    return 'RESOLVED'\n"
        ),
        encoding="utf-8",
    )

    spec = make_spec(
        source_present=True
    )

    result = consume_brody_engineering_spec(
        diagnosis(spec),
        repo_root=tmp_path,
    )

    assert result.status == "NO_CHANGE_REQUIRED"
    assert result.native_plan is None
    assert result.missing_capabilities == []
