from __future__ import annotations

import ast
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TESTS_ROOT = ROOT / "tests"


@dataclass(frozen=True)
class ModuleAnalysis:
    path: str
    sink_functions: tuple[str, ...]
    deselected_tests: tuple[str, ...]


def _call_name(
    node: ast.Call,
) -> str:
    function = node.func

    if isinstance(function, ast.Name):
        return function.id

    if isinstance(function, ast.Attribute):
        parts: list[str] = []
        current: ast.AST = function

        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value

        if isinstance(current, ast.Name):
            parts.append(current.id)

        return ".".join(
            reversed(parts)
        )

    return ""


def _string_literals(
    node: ast.AST,
) -> list[str]:
    return [
        child.value
        for child in ast.walk(node)
        if isinstance(child, ast.Constant)
        and isinstance(child.value, str)
    ]


def _is_nested_pytest_call(
    node: ast.Call,
) -> bool:
    name = _call_name(
        node
    ).lower()

    literals = _string_literals(
        node
    )

    normalized = " ".join(
        literals
    ).lower()

    if (
        name == "pytest.main"
        or name.endswith(
            ".pytest.main"
        )
    ):
        return True

    subprocess_like = any(
        name == candidate
        or name.endswith(
            "." + candidate
        )
        for candidate in (
            "subprocess.run",
            "subprocess.popen",
            "subprocess.call",
            "subprocess.check_call",
            "subprocess.check_output",
        )
    )

    return (
        subprocess_like
        and "pytest" in normalized
    )


class _FunctionBodyVisitor(
    ast.NodeVisitor,
):
    def __init__(self) -> None:
        self.direct_sink = False
        self.local_calls: set[str] = set()

    def visit_FunctionDef(
        self,
        node: ast.FunctionDef,
    ) -> None:
        # Nested function definitions are separate scopes.
        return

    def visit_AsyncFunctionDef(
        self,
        node: ast.AsyncFunctionDef,
    ) -> None:
        return

    def visit_Lambda(
        self,
        node: ast.Lambda,
    ) -> None:
        return

    def visit_Call(
        self,
        node: ast.Call,
    ) -> None:
        if _is_nested_pytest_call(
            node
        ):
            self.direct_sink = True

        if isinstance(
            node.func,
            ast.Name,
        ):
            self.local_calls.add(
                node.func.id
            )

        self.generic_visit(
            node
        )


def _function_data(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
) -> tuple[bool, set[str]]:
    visitor = _FunctionBodyVisitor()

    for statement in function.body:
        visitor.visit(
            statement
        )

    return (
        visitor.direct_sink,
        visitor.local_calls,
    )


def analyze_test_file(
    path: Path,
) -> ModuleAnalysis:
    source = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    tree = ast.parse(
        source,
        filename=str(path),
    )

    functions = {
        node.name: node
        for node in tree.body
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
    }

    direct_sinks: set[str] = set()
    calls: dict[str, set[str]] = {}

    for name, function in functions.items():
        sink, local_calls = _function_data(
            function
        )

        if sink:
            direct_sinks.add(
                name
            )

        calls[
            name
        ] = {
            called
            for called in local_calls
            if called in functions
        }

    memo: dict[str, bool] = {}

    def reaches_sink(
        name: str,
        active: set[str] | None = None,
    ) -> bool:
        if name in memo:
            return memo[
                name
            ]

        if name in direct_sinks:
            memo[
                name
            ] = True
            return True

        active = set(
            active or set()
        )

        if name in active:
            memo[
                name
            ] = False
            return False

        active.add(
            name
        )

        result = any(
            reaches_sink(
                child,
                active,
            )
            for child in calls.get(
                name,
                set(),
            )
        )

        memo[
            name
        ] = result

        return result

    relative = path.relative_to(
        ROOT
    ).as_posix()

    deselected = tuple(
        sorted(
            f"{relative}::{name}"
            for name in functions
            if name.startswith(
                "test_"
            )
            and reaches_sink(
                name
            )
        )
    )

    return ModuleAnalysis(
        path=relative,
        sink_functions=tuple(
            sorted(
                direct_sinks
            )
        ),
        deselected_tests=deselected,
    )


def discover_nested_pytest_tests() -> tuple[
    ModuleAnalysis,
    ...,
]:
    analyses = []

    for path in sorted(
        TESTS_ROOT.rglob(
            "*.py"
        )
    ):
        analysis = analyze_test_file(
            path
        )

        if analysis.deselected_tests:
            analyses.append(
                analysis
            )

    return tuple(
        analyses
    )


def discover_deselected_nodeids() -> tuple[
    str,
    ...,
]:
    return tuple(
        nodeid
        for analysis in discover_nested_pytest_tests()
        for nodeid in analysis.deselected_tests
    )


def main(
    arguments: list[str] | None = None,
) -> int:
    arguments = list(
        sys.argv[1:]
        if arguments is None
        else arguments
    )

    if arguments and arguments[0] == "--":
        arguments = arguments[1:]

    if not arguments:
        arguments = [
            "tests/",
            "-q",
            "--tb=short",
        ]

    analyses = discover_nested_pytest_tests()
    nodeids = discover_deselected_nodeids()

    print(
        "NESTED_PYTEST_MODULE_COUNT="
        f"{len(analyses)}"
    )

    print(
        "NESTED_PYTEST_TEST_COUNT="
        f"{len(nodeids)}"
    )

    for nodeid in nodeids:
        print(
            f"DESELECTED_NESTED_TEST={nodeid}"
        )

    command = [
        sys.executable,
        "-X",
        "utf8",
        "-m",
        "pytest",
        *arguments,
        *[
            f"--deselect={nodeid}"
            for nodeid in nodeids
        ],
    ]

    process = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
    )

    return process.returncode


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
