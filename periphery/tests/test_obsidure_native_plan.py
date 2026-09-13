from periphery.agents.obsidure_native_plan import (
    PRIMITIVES,
    compile_engineering_spec_to_native_plan,
)


def test_native_plan_compiles_existing_create_and_verification():
    spec = {
        "request_id": "rr_plan",
        "spec_id": "BRODY_ENGINEERING_SPEC_V1",
        "objective": "implement bounded multi-file change",
        "targets": [
            {
                "path": "apps/obsidia_api/existing.py",
                "target_state": "EXISTING",
            },
            {
                "path": "periphery/harness/new_module.py",
                "target_state": "CREATE",
            },
        ],
        "acceptance_criteria": [
            "known term resolves",
            "unknown term produces HOLD",
        ],
    }

    plan = compile_engineering_spec_to_native_plan(spec)

    assert [step.primitive for step in plan.steps] == [
        "MODIFY_FILE",
        "CREATE_FILE",
        "VERIFY_TESTS",
    ]

    assert (
        "SEMANTIC_EDIT_DECOMPOSITION_MISSING:"
        "apps/obsidia_api/existing.py"
        in plan.missing_capabilities
    )

    assert (
        "FILE_CONTENT_SYNTHESIS_MISSING:"
        "periphery/harness/new_module.py"
        in plan.missing_capabilities
    )

    assert plan.steps[1].depends_on == (
        plan.steps[0].step_id,
    )

    assert plan.steps[2].depends_on == (
        plan.steps[1].step_id,
    )


def test_native_primitive_registry_has_composable_vocabulary():
    expected = {
        "CREATE_FILE",
        "MODIFY_FILE",
        "ADD_IMPORT",
        "REMOVE_IMPORT",
        "ADD_FUNCTION",
        "MODIFY_FUNCTION",
        "ADD_CLASS",
        "MODIFY_CLASS",
        "ADD_FIELD",
        "MODIFY_SIGNATURE",
        "ADD_CALL",
        "ADD_BRANCH",
        "ADD_TEST",
        "WIRE_COMPONENT",
        "VERIFY_TESTS",
    }

    assert expected.issubset(PRIMITIVES)
