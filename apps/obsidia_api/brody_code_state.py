"""
Brody Code State V1.

Read-only structural observation of Python source.

Source -> factual semantic state.
No source generation.
No mutation.
"""

from __future__ import annotations

import ast
from dataclasses import asdict, dataclass, field
from typing import Any


STATE_ID = "BRODY_CODE_STATE_V1"


@dataclass
class FunctionState:
    name: str
    args: list[str] = field(default_factory=list)
    returns: str = ""
    arg_specs: list[dict[str, Any]] = field(default_factory=list)
    structural_fingerprint: str = ""
    rewrite_safe: bool = False


@dataclass
class FieldState:
    name: str
    annotation: str = ""
    structural_fingerprint: str = ""
    rewrite_safe: bool = False


@dataclass
class ClassState:
    name: str
    fields: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)
    field_states: dict[str, FieldState] = field(
        default_factory=dict
    )
    method_states: dict[str, FunctionState] = field(
        default_factory=dict
    )


@dataclass
class PythonCodeState:
    path: str
    source_present: bool
    parse_ok: bool

    imports: list[str] = field(default_factory=list)
    functions: dict[str, FunctionState] = field(default_factory=dict)
    classes: dict[str, ClassState] = field(default_factory=dict)

    syntax_error: str = ""

    readonly: bool = True
    can_generate_source: bool = False
    decision_authority: str = "KX108_ONLY"
    emits_act: bool = False
    kernel_mutation: bool = False
    memory_write: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _annotation_text(node: ast.expr | None) -> str:
    if node is None:
        return ""

    try:
        return ast.unparse(node)
    except Exception:
        return ""


_SAFE_COMPARE_OPS = (
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.In,
    ast.NotIn,
    ast.Is,
    ast.IsNot,
)

_SAFE_BINARY_OPS = (
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
)


def _expression_rewrite_safe(
    node: ast.expr,
) -> bool:

    if isinstance(
        node,
        (
            ast.Name,
            ast.Constant,
        ),
    ):
        return True

    if isinstance(node, ast.Attribute):
        return _expression_rewrite_safe(
            node.value
        )

    if isinstance(node, ast.Call):
        # Current semantic compiler route is kept
        # deliberately bounded here. Keyword calls
        # are not assumed safe for round-trip.
        return (
            not node.keywords
            and _expression_rewrite_safe(
                node.func
            )
            and all(
                _expression_rewrite_safe(arg)
                for arg in node.args
            )
        )

    if isinstance(
        node,
        (
            ast.List,
            ast.Tuple,
        ),
    ):
        return all(
            _expression_rewrite_safe(item)
            for item in node.elts
        )

    if isinstance(node, ast.Dict):
        return (
            all(
                key is not None
                and _expression_rewrite_safe(key)
                for key in node.keys
            )
            and all(
                _expression_rewrite_safe(value)
                for value in node.values
            )
        )

    if isinstance(node, ast.Compare):
        return (
            _expression_rewrite_safe(
                node.left
            )
            and all(
                isinstance(
                    op,
                    _SAFE_COMPARE_OPS,
                )
                for op in node.ops
            )
            and all(
                _expression_rewrite_safe(item)
                for item in node.comparators
            )
        )

    if isinstance(node, ast.BoolOp):
        return (
            isinstance(
                node.op,
                (
                    ast.And,
                    ast.Or,
                ),
            )
            and all(
                _expression_rewrite_safe(item)
                for item in node.values
            )
        )

    if isinstance(node, ast.UnaryOp):
        return (
            isinstance(node.op, ast.Not)
            and _expression_rewrite_safe(
                node.operand
            )
        )

    if isinstance(node, ast.BinOp):
        return (
            isinstance(
                node.op,
                _SAFE_BINARY_OPS,
            )
            and _expression_rewrite_safe(
                node.left
            )
            and _expression_rewrite_safe(
                node.right
            )
        )

    return False


def _statement_rewrite_safe(
    node: ast.stmt,
) -> bool:

    if isinstance(node, ast.Return):
        return (
            node.value is None
            or _expression_rewrite_safe(
                node.value
            )
        )

    if isinstance(node, ast.Assign):
        return (
            len(node.targets) == 1
            and isinstance(
                node.targets[0],
                ast.Name,
            )
            and _expression_rewrite_safe(
                node.value
            )
        )

    if isinstance(node, ast.Expr):
        return _expression_rewrite_safe(
            node.value
        )

    if isinstance(node, ast.If):
        return (
            bool(node.body)
            and _expression_rewrite_safe(
                node.test
            )
            and all(
                _statement_rewrite_safe(item)
                for item in node.body
            )
            and all(
                _statement_rewrite_safe(item)
                for item in node.orelse
            )
        )

    if isinstance(node, ast.Raise):
        return (
            node.exc is not None
            and node.cause is None
            and _expression_rewrite_safe(
                node.exc
            )
        )

    if isinstance(node, ast.Pass):
        return True

    return False


def _function_rewrite_safe(
    node: ast.AST,
) -> bool:

    if not isinstance(
        node,
        ast.FunctionDef,
    ):
        return False

    args = node.args

    if (
        args.posonlyargs
        or args.vararg is not None
        or args.kwonlyargs
        or args.kwarg is not None
        or args.defaults
        or args.kw_defaults
        or node.decorator_list
        or node.type_comment
    ):
        return False

    return (
        bool(node.body)
        and all(
            _statement_rewrite_safe(item)
            for item in node.body
        )
    )


def _function_fingerprint(
    node: ast.AST,
) -> str:
    return ast.dump(
        node,
        annotate_fields=True,
        include_attributes=False,
    )


def _field_fingerprint(
    node: ast.AST,
) -> str:
    return ast.dump(
        node,
        annotate_fields=True,
        include_attributes=False,
    )


def _field_state(
    node: ast.Assign | ast.AnnAssign,
    name: str,
) -> FieldState:
    if isinstance(node, ast.AnnAssign):
        rewrite_safe = (
            isinstance(node.target, ast.Name)
            and node.target.id == name
            and int(node.simple) == 1
        )

        annotation = _annotation_text(
            node.annotation
        )

    else:
        rewrite_safe = (
            len(node.targets) == 1
            and isinstance(
                node.targets[0],
                ast.Name,
            )
            and node.targets[0].id == name
        )

        annotation = ""

    return FieldState(
        name=name,
        annotation=annotation,
        structural_fingerprint=(
            _field_fingerprint(node)
        ),
        rewrite_safe=rewrite_safe,
    )


def analyze_python_code_state(
    path: str,
    source: str | None,
) -> PythonCodeState:

    normalized = str(path or "").replace("\\", "/")

    if source is None:
        return PythonCodeState(
            path=normalized,
            source_present=False,
            parse_ok=True,
        )

    try:
        tree = ast.parse(
            source,
            filename=normalized,
        )

    except SyntaxError as exc:
        return PythonCodeState(
            path=normalized,
            source_present=True,
            parse_ok=False,
            syntax_error=(
                f"{exc.lineno or 0}:"
                f"{exc.offset or 0}:"
                f"{exc.msg}"
            ),
        )

    imports: list[str] = []
    functions: dict[str, FunctionState] = {}
    classes: dict[str, ClassState] = {}

    for node in tree.body:

        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(
                    f"import {alias.name}"
                )

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = ", ".join(
                alias.name
                for alias in node.names
            )
            imports.append(
                f"from {module} import {names}"
            )

        elif isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef),
        ):
            functions[node.name] = FunctionState(
                name=node.name,
                args=[
                    arg.arg
                    for arg in node.args.args
                ],
                returns=_annotation_text(
                    node.returns
                ),
                arg_specs=[
                    {
                        "name": arg.arg,
                        "annotation": (
                            _annotation_text(
                                arg.annotation
                            )
                        ),
                    }
                    for arg in node.args.args
                ],
                structural_fingerprint=(
                    _function_fingerprint(node)
                ),
                rewrite_safe=(
                    _function_rewrite_safe(node)
                ),
            )

        elif isinstance(node, ast.ClassDef):

            fields: list[str] = []
            methods: list[str] = []
            field_states: dict[
                str,
                FieldState,
            ] = {}

            method_states: dict[
                str,
                FunctionState,
            ] = {}

            for child in node.body:

                if isinstance(child, ast.AnnAssign):
                    if isinstance(
                        child.target,
                        ast.Name,
                    ):
                        field_name = child.target.id

                        fields.append(
                            field_name
                        )

                        state = _field_state(
                            child,
                            field_name,
                        )

                        if field_name in field_states:
                            field_states[
                                field_name
                            ].rewrite_safe = False
                        else:
                            field_states[
                                field_name
                            ] = state

                elif isinstance(child, ast.Assign):
                    for target in child.targets:
                        if isinstance(
                            target,
                            ast.Name,
                        ):
                            field_name = target.id

                            fields.append(
                                field_name
                            )

                            state = _field_state(
                                child,
                                field_name,
                            )

                            if field_name in field_states:
                                field_states[
                                    field_name
                                ].rewrite_safe = False
                            else:
                                field_states[
                                    field_name
                                ] = state

                elif isinstance(
                    child,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                    ),
                ):
                    methods.append(
                        child.name
                    )

                    method_state = FunctionState(
                        name=child.name,
                        args=[
                            arg.arg
                            for arg in child.args.args
                        ],
                        returns=_annotation_text(
                            child.returns
                        ),
                        arg_specs=[
                            {
                                "name": arg.arg,
                                "annotation": (
                                    _annotation_text(
                                        arg.annotation
                                    )
                                ),
                            }
                            for arg in child.args.args
                        ],
                        structural_fingerprint=(
                            _function_fingerprint(
                                child
                            )
                        ),
                        rewrite_safe=(
                            _function_rewrite_safe(
                                child
                            )
                        ),
                    )

                    if child.name in method_states:
                        method_states[
                            child.name
                        ].rewrite_safe = False
                    else:
                        method_states[
                            child.name
                        ] = method_state

            classes[node.name] = ClassState(
                name=node.name,
                fields=sorted(
                    set(fields)
                ),
                methods=sorted(
                    set(methods)
                ),
                field_states=field_states,
                method_states=method_states,
            )

    return PythonCodeState(
        path=normalized,
        source_present=True,
        parse_ok=True,
        imports=sorted(
            set(imports)
        ),
        functions=functions,
        classes=classes,
    )


def self_check() -> dict[str, Any]:
    return {
        "state_id": STATE_ID,
        "role": "READ_ONLY_CODE_OBSERVATION",
        "can_generate_source": False,
        "decision_authority": "KX108_ONLY",
        "emits_act": False,
        "kernel_mutation": False,
        "memory_write": False,
    }
