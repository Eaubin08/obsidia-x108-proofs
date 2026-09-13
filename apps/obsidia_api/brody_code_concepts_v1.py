"""
Initial Brody code-semantic education V1.

These are semantic capabilities, not source-code templates.
"""

from __future__ import annotations

from apps.obsidia_api.brody_code_concept_engine import (
    CodeConcept,
)


SEMANTIC_CALIBRATION_V1 = CodeConcept(
    concept_id="SEMANTIC_CALIBRATION_V1",

    required_terms=(
        "semantic",
    ),

    any_terms=(
        "calibration",
        "calibrate",
        "calibrer",
        "unknown",
        "inconnu",
    ),

    desired_state_template={
        "targets": [
            {
                "path": "$TARGET0",

                "module_docstring": (
                    "Bounded semantic calibration."
                ),

                "imports": [],

                "classes": [
                    {
                        "name": (
                            "SemanticCalibrationResult"
                        ),

                        "fields": [
                            {
                                "name": "status",
                                "annotation": "str",
                            },
                            {
                                "name": "confidence",
                                "annotation": "float",
                                "default_expr": {
                                    "kind": "CONSTANT",
                                    "value": 0.0,
                                },
                            },
                            {
                                "name": "unknowns",
                                "annotation": "list[str]",
                                "default_expr": {
                                    "kind": "LIST",
                                    "items": [],
                                },
                            },
                            {
                                "name": "ambiguities",
                                "annotation": "list[str]",
                                "default_expr": {
                                    "kind": "LIST",
                                    "items": [],
                                },
                            },
                            {
                                "name": "provenance",
                                "annotation": "list[str]",
                                "default_expr": {
                                    "kind": "LIST",
                                    "items": [],
                                },
                            },
                        ],
                    }
                ],

                "functions": [
                    {
                        "name": "calibrate_semantics",

                        "args": [
                            {
                                "name": "term",
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
                    }
                ],
            }
        ]
    },
)


DEFAULT_CODE_CONCEPTS = (
    SEMANTIC_CALIBRATION_V1,
)
