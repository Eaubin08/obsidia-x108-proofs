"""
R8-C3b4 — Brody Native Tooling Analysis V1.

Richer readonly cognition for native Obsidia self-engineering.

This organ consumes the already-canonical Brody native context and
extracts structural facts from the exact current Python source.

It does not generate source and cannot mutate the repository.

Extracted cognition includes:
    source identity,
    source size,
    module docstring presence,
    imports,
    top-level constants,
    functions,
    classes,
    tooling-scope classification.

Authority:
    BRODY_AUTHORITY = NONE
    DECISION_AUTHORITY = KX108_ONLY
"""

from __future__ import annotations

import ast
import hashlib

from dataclasses import dataclass
from typing import Any

from scripts.providers.brody_native_tooling_context_v1 import (
    BrodyNativeToolingContext,
    build_brody_native_tooling_context,
)


ANALYSIS_ID = (
    "BRODY_NATIVE_TOOLING_ANALYSIS_V1"
)

BRODY_AUTHORITY = "NONE"
DECISION_AUTHORITY = "KX108_ONLY"


class BrodyNativeAnalysisError(
    RuntimeError
):
    pass


@dataclass(
    frozen=True
)
class BrodyNativeToolingAnalysis:

    analysis_id: str

    context: BrodyNativeToolingContext

    source_sha256: str
    source_bytes: int
    source_lines: int

    module_docstring_present: bool

    import_roots: tuple[str, ...]
    top_level_constants: tuple[str, ...]
    function_names: tuple[str, ...]
    class_names: tuple[str, ...]

    target_is_tooling: bool

    readonly: bool = True
    can_decide: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False
    emits_act: bool = False
    world_action: bool = False


def _tooling_target(
    target_path: str,
) -> bool:

    normalized = target_path.replace(
        "\\",
        "/",
    )

    return any(
        normalized.startswith(
            prefix
        )
        for prefix in (
            "scripts/obsidia_",
            "scripts/obsidure_",
            "scripts/providers/",
            "scripts/runtime_wiring/",
        )
    )


def analyze_brody_native_tooling_prompt(
    prompt: str,
) -> BrodyNativeToolingAnalysis:

    context = (
        build_brody_native_tooling_context(
            prompt
        )
    )


    try:
        tree = ast.parse(
            context.current_source
        )

    except SyntaxError as exc:

        raise BrodyNativeAnalysisError(
            "BRODY_SOURCE_SYNTAX_INVALID"
        ) from exc


    imports: set[str] = set()

    constants: list[str] = []

    functions: list[str] = []

    classes: list[str] = []


    for node in tree.body:

        if isinstance(
            node,
            ast.Import,
        ):

            for alias in node.names:

                imports.add(
                    alias.name.split(
                        "."
                    )[0]
                )


        elif isinstance(
            node,
            ast.ImportFrom,
        ):

            if node.module:

                imports.add(
                    node.module.split(
                        "."
                    )[0]
                )


        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):

            functions.append(
                node.name
            )


        elif isinstance(
            node,
            ast.ClassDef,
        ):

            classes.append(
                node.name
            )


        elif isinstance(
            node,
            ast.Assign,
        ):

            for target in node.targets:

                if (
                    isinstance(
                        target,
                        ast.Name,
                    )
                    and target.id.isupper()
                ):

                    constants.append(
                        target.id
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
                and node.target.id.isupper()
            ):

                constants.append(
                    node.target.id
                )


    source_bytes = (
        context.current_source.encode(
            "utf-8"
        )
    )


    return BrodyNativeToolingAnalysis(
        analysis_id=ANALYSIS_ID,
        context=context,
        source_sha256=(
            hashlib.sha256(
                source_bytes
            ).hexdigest()
        ),
        source_bytes=len(
            source_bytes
        ),
        source_lines=len(
            context.current_source.splitlines()
        ),
        module_docstring_present=(
            ast.get_docstring(
                tree,
                clean=False,
            )
            is not None
        ),
        import_roots=tuple(
            sorted(
                imports
            )
        ),
        top_level_constants=tuple(
            constants
        ),
        function_names=tuple(
            functions
        ),
        class_names=tuple(
            classes
        ),
        target_is_tooling=(
            _tooling_target(
                context.target_path
            )
        ),
    )


def self_check() -> dict[str, Any]:

    return {
        "analysis_id": ANALYSIS_ID,
        "role": (
            "READONLY_STRUCTURAL_COGNITION"
        ),
        "brody_authority": (
            BRODY_AUTHORITY
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
        "can_decide": False,
        "world_action": False,
    }
