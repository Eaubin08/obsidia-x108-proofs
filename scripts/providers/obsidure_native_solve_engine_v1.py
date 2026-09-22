"""
R8-C3b4 — Obsidure Native Solve Engine V1.

Bounded native engineering solve engine.

The engine performs deterministic strategy search over the exact source
understood by Brody-native structural cognition.

Supported V1 strategies:

    INSERT_COMMENT_AFTER_MODULE_DOCSTRING
    REPLACE_EXACT_TEXT_ONCE
    SET_TOP_LEVEL_CONSTANT

A solve request may provide several candidate strategies.

If one strategy fails validation, the engine records the failure and
tries the next bounded strategy.

This is the first native:
    proposal -> failure -> evolved strategy -> valid source
loop inside the tooling generation rail.

This is NOT:
    arbitrary code intelligence,
    an LLM,
    autonomous repository mutation.

Authority:
    OBSIDURE_AUTHORITY = NONE
    DECISION_AUTHORITY = KX108_ONLY
"""

from __future__ import annotations

import ast
import json
import math
import re

from typing import Any

from scripts.providers.brody_native_tooling_analysis_v1 import (
    BrodyNativeToolingAnalysis,
    analyze_brody_native_tooling_prompt,
)

from scripts.providers.obsidia_tooling_generator_v1 import (
    ToolingBackendResult,
)


BACKEND_ID = (
    "OBSIDURE_NATIVE_SOLVE_ENGINE_V1"
)

MODEL_ID = (
    "obsidure-native-solve-v1"
)

OBSIDURE_AUTHORITY = "NONE"
DECISION_AUTHORITY = "KX108_ONLY"

MAX_STRATEGIES = 5
MAX_EXACT_TEXT_CHARS = 4096


_ALLOWED_TARGET_PREFIXES = (
    "scripts/obsidia_",
    "scripts/obsidure_",
    "scripts/providers/",
    "scripts/runtime_wiring/",
)


class ObsidureNativeSolveError(
    RuntimeError
):
    pass


def _validate_target(
    analysis: BrodyNativeToolingAnalysis,
) -> None:

    target = (
        analysis.context.target_path
    )

    normalized = target.replace(
        "\\",
        "/",
    )

    if normalized != target:
        raise ObsidureNativeSolveError(
            "SOLVE_TARGET_BACKSLASH_REJECTED"
        )


    if not normalized.endswith(
        ".py"
    ):
        raise ObsidureNativeSolveError(
            "SOLVE_TARGET_PYTHON_ONLY"
        )


    if not any(
        normalized.startswith(
            prefix
        )
        for prefix in (
            _ALLOWED_TARGET_PREFIXES
        )
    ):

        raise ObsidureNativeSolveError(
            "SOLVE_TARGET_OUTSIDE_TOOLING_SCOPE"
        )


    if not analysis.target_is_tooling:
        raise ObsidureNativeSolveError(
            "BRODY_TOOLING_SCOPE_REJECTED"
        )


def _extract_solve_spec(
    objective: str,
) -> dict[str, Any]:

    marker = (
        "NATIVE_SOLVE_JSON="
    )

    index = objective.rfind(
        marker
    )

    if index < 0:
        raise ObsidureNativeSolveError(
            "NATIVE_SOLVE_SPEC_REQUIRED"
        )


    raw = objective[
        index
        + len(marker):
    ].strip()


    try:
        spec = json.loads(
            raw
        )

    except Exception as exc:

        raise ObsidureNativeSolveError(
            "NATIVE_SOLVE_SPEC_INVALID_JSON"
        ) from exc


    if not isinstance(
        spec,
        dict,
    ):
        raise ObsidureNativeSolveError(
            "NATIVE_SOLVE_SPEC_NOT_OBJECT"
        )


    strategies = spec.get(
        "strategies"
    )


    if not isinstance(
        strategies,
        list,
    ):
        raise ObsidureNativeSolveError(
            "NATIVE_STRATEGIES_REQUIRED"
        )


    if (
        not strategies
        or len(
            strategies
        )
        > MAX_STRATEGIES
    ):
        raise ObsidureNativeSolveError(
            "NATIVE_STRATEGY_COUNT_INVALID"
        )


    for strategy in strategies:

        if not isinstance(
            strategy,
            dict,
        ):
            raise ObsidureNativeSolveError(
                "NATIVE_STRATEGY_NOT_OBJECT"
            )


    return spec


def _validate_generated_python(
    generated: str,
) -> str:

    try:
        ast.parse(
            generated
        )

    except SyntaxError as exc:

        raise ObsidureNativeSolveError(
            "GENERATED_PYTHON_SYNTAX_INVALID"
        ) from exc


    return generated


def _comment_value(
    value: Any,
) -> str:

    if not isinstance(
        value,
        str,
    ):
        raise ObsidureNativeSolveError(
            "COMMENT_NOT_TEXT"
        )


    comment = value.strip()


    if not comment:
        raise ObsidureNativeSolveError(
            "COMMENT_EMPTY"
        )


    if len(comment) > 160:
        raise ObsidureNativeSolveError(
            "COMMENT_TOO_LONG"
        )


    if (
        "\n" in comment
        or "\r" in comment
    ):
        raise ObsidureNativeSolveError(
            "COMMENT_MULTILINE_REJECTED"
        )


    if not re.fullmatch(
        r"[A-Za-z0-9 _.:/\-]+",
        comment,
    ):
        raise ObsidureNativeSolveError(
            "COMMENT_CHARSET_REJECTED"
        )


    return comment


def _insert_comment(
    analysis: BrodyNativeToolingAnalysis,
    strategy: dict[str, Any],
) -> str:

    source = (
        analysis.context.current_source
    )

    comment = _comment_value(
        strategy.get(
            "comment"
        )
    )

    marker = (
        "# "
        + comment
    )


    if marker in source:
        raise ObsidureNativeSolveError(
            "COMMENT_ALREADY_PRESENT"
        )


    tree = ast.parse(
        source
    )

    lines = source.splitlines(
        keepends=True
    )

    newline = (
        "\r\n"
        if "\r\n" in source
        else "\n"
    )


    insertion = 0


    if tree.body:

        first = tree.body[0]

        if (
            isinstance(
                first,
                ast.Expr,
            )
            and isinstance(
                first.value,
                ast.Constant,
            )
            and isinstance(
                first.value.value,
                str,
            )
        ):

            if first.end_lineno is None:
                raise ObsidureNativeSolveError(
                    "DOCSTRING_END_UNKNOWN"
                )

            insertion = (
                first.end_lineno
            )


    lines.insert(
        insertion,
        marker
        + newline,
    )


    generated = "".join(
        lines
    )


    if generated == source:
        raise ObsidureNativeSolveError(
            "COMMENT_NO_CHANGE"
        )


    return _validate_generated_python(
        generated
    )


def _replace_exact_once(
    analysis: BrodyNativeToolingAnalysis,
    strategy: dict[str, Any],
) -> str:

    source = (
        analysis.context.current_source
    )


    old = strategy.get(
        "old"
    )

    new = strategy.get(
        "new"
    )


    if not isinstance(
        old,
        str,
    ) or not old:

        raise ObsidureNativeSolveError(
            "EXACT_OLD_REQUIRED"
        )


    if not isinstance(
        new,
        str,
    ):

        raise ObsidureNativeSolveError(
            "EXACT_NEW_REQUIRED"
        )


    if (
        len(old)
        > MAX_EXACT_TEXT_CHARS
        or len(new)
        > MAX_EXACT_TEXT_CHARS
    ):

        raise ObsidureNativeSolveError(
            "EXACT_TEXT_TOO_LARGE"
        )


    if (
        "\x00" in old
        or "\x00" in new
    ):

        raise ObsidureNativeSolveError(
            "EXACT_TEXT_NUL_REJECTED"
        )


    count = source.count(
        old
    )


    if count == 0:
        raise ObsidureNativeSolveError(
            "EXACT_OLD_NOT_FOUND"
        )


    if count != 1:
        raise ObsidureNativeSolveError(
            "EXACT_OLD_NOT_UNIQUE"
        )


    generated = source.replace(
        old,
        new,
        1,
    )


    if generated == source:
        raise ObsidureNativeSolveError(
            "EXACT_REPLACE_NO_CHANGE"
        )


    return _validate_generated_python(
        generated
    )


def _python_literal(
    value: Any,
) -> str:

    if value is None:
        return "None"


    if isinstance(
        value,
        bool,
    ):
        return (
            "True"
            if value
            else "False"
        )


    if isinstance(
        value,
        int,
    ):
        return repr(
            value
        )


    if isinstance(
        value,
        float,
    ):

        if not math.isfinite(
            value
        ):
            raise ObsidureNativeSolveError(
                "CONSTANT_FLOAT_NONFINITE"
            )

        return repr(
            value
        )


    if isinstance(
        value,
        str,
    ):

        if len(value) > 1024:
            raise ObsidureNativeSolveError(
                "CONSTANT_STRING_TOO_LONG"
            )

        return repr(
            value
        )


    raise ObsidureNativeSolveError(
        "CONSTANT_VALUE_TYPE_REJECTED"
    )


def _set_top_level_constant(
    analysis: BrodyNativeToolingAnalysis,
    strategy: dict[str, Any],
) -> str:

    source = (
        analysis.context.current_source
    )


    name = strategy.get(
        "name"
    )


    if not isinstance(
        name,
        str,
    ):

        raise ObsidureNativeSolveError(
            "CONSTANT_NAME_REQUIRED"
        )


    if not re.fullmatch(
        r"[A-Z][A-Z0-9_]{0,63}",
        name,
    ):

        raise ObsidureNativeSolveError(
            "CONSTANT_NAME_REJECTED"
        )


    if name not in (
        analysis.top_level_constants
    ):

        raise ObsidureNativeSolveError(
            "CONSTANT_NOT_FOUND"
        )


    literal = _python_literal(
        strategy.get(
            "value"
        )
    )


    tree = ast.parse(
        source
    )


    matches: list[
        ast.Assign | ast.AnnAssign
    ] = []


    for node in tree.body:

        if isinstance(
            node,
            ast.Assign,
        ):

            names = [
                target.id
                for target in node.targets
                if isinstance(
                    target,
                    ast.Name,
                )
            ]

            if name in names:
                matches.append(
                    node
                )


        elif isinstance(
            node,
            ast.AnnAssign,
        ):

            if (
                isinstance(
                    node.target,
                    ast.Name,
                )
                and node.target.id
                == name
            ):

                matches.append(
                    node
                )


    if len(matches) != 1:
        raise ObsidureNativeSolveError(
            "CONSTANT_ASSIGNMENT_NOT_UNIQUE"
        )


    node = matches[0]


    if (
        node.end_lineno is None
        or node.lineno
        != node.end_lineno
    ):

        raise ObsidureNativeSolveError(
            "CONSTANT_MULTILINE_REJECTED"
        )


    lines = source.splitlines(
        keepends=True
    )


    index = (
        node.lineno
        - 1
    )


    original_line = lines[
        index
    ]


    newline = (
        "\r\n"
        if original_line.endswith(
            "\r\n"
        )
        else (
            "\n"
            if original_line.endswith(
                "\n"
            )
            else ""
        )
    )


    lines[
        index
    ] = (
        name
        + " = "
        + literal
        + newline
    )


    generated = "".join(
        lines
    )


    if generated == source:
        raise ObsidureNativeSolveError(
            "CONSTANT_SET_NO_CHANGE"
        )


    return _validate_generated_python(
        generated
    )


def _apply_strategy(
    analysis: BrodyNativeToolingAnalysis,
    strategy: dict[str, Any],
) -> tuple[
    str,
    str,
]:

    operation = str(
        strategy.get(
            "op",
            "",
        )
        or ""
    ).strip()


    if operation == (
        "insert_comment_after_docstring"
    ):

        return (
            _insert_comment(
                analysis,
                strategy,
            ),
            "INSERT_COMMENT_AFTER_MODULE_DOCSTRING",
        )


    if operation == (
        "replace_exact_text_once"
    ):

        return (
            _replace_exact_once(
                analysis,
                strategy,
            ),
            "REPLACE_EXACT_TEXT_ONCE",
        )


    if operation == (
        "set_top_level_constant"
    ):

        return (
            _set_top_level_constant(
                analysis,
                strategy,
            ),
            "SET_TOP_LEVEL_CONSTANT",
        )


    raise ObsidureNativeSolveError(
        "STRATEGY_OPERATION_UNSUPPORTED"
    )


class ObsidureNativeSolveEngine:

    backend_id = BACKEND_ID


    def __init__(
        self,
    ) -> None:

        self.last_attempts: list[
            dict[str, Any]
        ] = []


    def generate_text(
        self,
        prompt: str,
    ) -> ToolingBackendResult:

        analysis = (
            analyze_brody_native_tooling_prompt(
                prompt
            )
        )


        _validate_target(
            analysis
        )


        spec = _extract_solve_spec(
            analysis.context.objective
        )


        strategies = spec[
            "strategies"
        ]


        attempts: list[
            dict[str, Any]
        ] = []


        for index, strategy in enumerate(
            strategies,
            start=1,
        ):

            operation = str(
                strategy.get(
                    "op",
                    "",
                )
                or ""
            )


            try:

                generated, selected = (
                    _apply_strategy(
                        analysis,
                        strategy,
                    )
                )


                attempts.append(
                    {
                        "attempt": index,
                        "operation": (
                            operation
                        ),
                        "status": "PASS",
                        "error": "",
                    }
                )


                self.last_attempts = list(
                    attempts
                )


                metadata = {
                    "engine": (
                        "OBSIDURE_NATIVE_SOLVE_ENGINE_V1"
                    ),
                    "selected_strategy": (
                        selected
                    ),
                    "selected_attempt": (
                        index
                    ),
                    "attempt_count": len(
                        attempts
                    ),
                    "attempts": list(
                        attempts
                    ),
                    "brody_analysis_id": (
                        analysis.analysis_id
                    ),
                    "source_sha256": (
                        analysis.source_sha256
                    ),
                    "source_lines": (
                        analysis.source_lines
                    ),
                    "source_bytes": (
                        analysis.source_bytes
                    ),
                    "imports": list(
                        analysis.import_roots
                    ),
                    "constants": list(
                        analysis.top_level_constants
                    ),
                    "functions": list(
                        analysis.function_names
                    ),
                    "classes": list(
                        analysis.class_names
                    ),
                    "native": True,
                    "external_model": False,
                    "deterministic": True,
                    "backend_authority": (
                        "NONE"
                    ),
                    "decision_authority": (
                        "KX108_ONLY"
                    ),
                    "memory_write": False,
                    "kernel_mutation": False,
                    "emits_act": False,
                    "world_action": False,
                }


                return ToolingBackendResult(
                    backend_id=BACKEND_ID,
                    model_id=MODEL_ID,
                    output_text=generated,
                    metadata=metadata,
                )


            except ObsidureNativeSolveError as exc:

                attempts.append(
                    {
                        "attempt": index,
                        "operation": (
                            operation
                        ),
                        "status": "FAIL",
                        "error": str(
                            exc
                        ),
                    }
                )


        self.last_attempts = list(
            attempts
        )


        error_codes = ",".join(
            item[
                "error"
            ]
            for item in attempts
        )


        raise ObsidureNativeSolveError(
            "NATIVE_SOLVE_EXHAUSTED:"
            + error_codes
        )


def self_check() -> dict[str, Any]:

    return {
        "backend_id": BACKEND_ID,
        "model_id": MODEL_ID,
        "role": (
            "BOUNDED_NATIVE_SOLVE_ENGINE"
        ),
        "strategies": [
            (
                "INSERT_COMMENT_AFTER_"
                "MODULE_DOCSTRING"
            ),
            "REPLACE_EXACT_TEXT_ONCE",
            "SET_TOP_LEVEL_CONSTANT",
        ],
        "strategy_fallback": True,
        "max_strategies": (
            MAX_STRATEGIES
        ),
        "native": True,
        "external_model": False,
        "deterministic": True,
        "backend_authority": (
            OBSIDURE_AUTHORITY
        ),
        "decision_authority": (
            DECISION_AUTHORITY
        ),
        "network": False,
        "filesystem_write": False,
        "repo_mutation": False,
        "memory_write": False,
        "kernel_mutation": False,
        "emits_act": False,
        "auto_apply": False,
        "auto_commit": False,
        "push": False,
        "merge": False,
        "kx108_invoked": False,
        "world_action": False,
    }
