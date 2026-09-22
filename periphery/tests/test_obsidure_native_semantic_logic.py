import ast

from periphery.agents.obsidure_native_decomposer import (
    compile_native_deltas_to_plan,
)
from periphery.agents.obsidure_native_program_executor import (
    execute_native_plan,
)
from periphery.agents.obsidure_native_semantic_compiler import (
    SemanticOperation,
    compile_semantic_operations,
)


TARGET = "periphery/generated_logic.py"


def run_operations(operations):

    deltas = compile_semantic_operations(
        operations
    )

    plan = compile_native_deltas_to_plan(
        request_id="rr_logic",
        spec_id="BRODY_ENGINEERING_SPEC_V1",
        objective="native semantic logic",
        deltas=deltas,
    )

    return execute_native_plan(
        plan,
        {},
    )


def test_if_compare_bool_and_multiple_returns():

    operations = [
        SemanticOperation(
            kind="CREATE_MODULE",
            target_path=TARGET,
            payload={
                "docstring": "semantic logic",
            },
        ),

        SemanticOperation(
            kind="ADD_FUNCTION",
            target_path=TARGET,
            payload={
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
                            "kind": "BOOL_OP",
                            "op": "AND",
                            "values": [
                                {
                                    "kind": "NAME",
                                    "id": "known",
                                },
                                {
                                    "kind": "COMPARE",
                                    "op": "NE",
                                    "left": {
                                        "kind": "NAME",
                                        "id": "value",
                                    },
                                    "right": {
                                        "kind": "CONSTANT",
                                        "value": "",
                                    },
                                },
                            ],
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
        ),
    ]

    result = run_operations(
        operations
    )

    assert result.status == "PASS"

    source = result.generated_sources[
        TARGET
    ]

    assert "if known and value != ''" in source
    assert "return 'RESOLVED'" in source
    assert "return 'UNKNOWN'" in source

    ast.parse(source)


def test_assignment_method_call_and_return():

    operations = [
        SemanticOperation(
            kind="CREATE_MODULE",
            target_path=TARGET,
            payload={
                "docstring": "normalize",
            },
        ),

        SemanticOperation(
            kind="ADD_FUNCTION",
            target_path=TARGET,
            payload={
                "name": "normalize",
                "args": [
                    {
                        "name": "value",
                        "annotation": "str",
                    },
                ],
                "returns": "str",
                "body": [
                    {
                        "kind": "ASSIGN",
                        "target": "cleaned",
                        "value": {
                            "kind": "CALL",
                            "func": "value.strip",
                            "args": [],
                        },
                    },
                    {
                        "kind": "RETURN",
                        "expr": {
                            "kind": "NAME",
                            "id": "cleaned",
                        },
                    },
                ],
            },
        ),
    ]

    result = run_operations(
        operations
    )

    assert result.status == "PASS"

    source = result.generated_sources[
        TARGET
    ]

    assert (
        "cleaned = value.strip()"
        in source
    )

    assert "return cleaned" in source

    ast.parse(source)


def test_dict_and_arithmetic_expression():

    operations = [
        SemanticOperation(
            kind="CREATE_MODULE",
            target_path=TARGET,
            payload={
                "docstring": "score",
            },
        ),

        SemanticOperation(
            kind="ADD_FUNCTION",
            target_path=TARGET,
            payload={
                "name": "score",
                "args": [
                    {
                        "name": "base",
                        "annotation": "float",
                    },
                    {
                        "name": "bonus",
                        "annotation": "float",
                    },
                ],
                "returns": "dict",
                "body": [
                    {
                        "kind": "RETURN",
                        "expr": {
                            "kind": "DICT",
                            "items": [
                                {
                                    "key": {
                                        "kind": "CONSTANT",
                                        "value": "score",
                                    },
                                    "value": {
                                        "kind": "BIN_OP",
                                        "op": "ADD",
                                        "left": {
                                            "kind": "NAME",
                                            "id": "base",
                                        },
                                        "right": {
                                            "kind": "NAME",
                                            "id": "bonus",
                                        },
                                    },
                                }
                            ],
                        },
                    }
                ],
            },
        ),
    ]

    result = run_operations(
        operations
    )

    assert result.status == "PASS"

    source = result.generated_sources[
        TARGET
    ]

    assert "'score': base + bonus" in source

    ast.parse(source)


def test_raise_can_be_generated_from_semantics():

    operations = [
        SemanticOperation(
            kind="CREATE_MODULE",
            target_path=TARGET,
            payload={
                "docstring": "validation",
            },
        ),

        SemanticOperation(
            kind="ADD_FUNCTION",
            target_path=TARGET,
            payload={
                "name": "require_value",
                "args": [
                    {
                        "name": "value",
                        "annotation": "str",
                    },
                ],
                "returns": "str",
                "body": [
                    {
                        "kind": "IF",
                        "test": {
                            "kind": "COMPARE",
                            "op": "EQ",
                            "left": {
                                "kind": "NAME",
                                "id": "value",
                            },
                            "right": {
                                "kind": "CONSTANT",
                                "value": "",
                            },
                        },
                        "body": [
                            {
                                "kind": "RAISE",
                                "expr": {
                                    "kind": "CALL",
                                    "func": "ValueError",
                                    "args": [
                                        {
                                            "kind": "CONSTANT",
                                            "value": "empty value",
                                        }
                                    ],
                                },
                            }
                        ],
                    },
                    {
                        "kind": "RETURN",
                        "expr": {
                            "kind": "NAME",
                            "id": "value",
                        },
                    },
                ],
            },
        ),
    ]

    result = run_operations(
        operations
    )

    assert result.status == "PASS"

    source = result.generated_sources[
        TARGET
    ]

    assert (
        "raise ValueError('empty value')"
        in source
    )

    ast.parse(source)
