"""
Obsidure Native Semantic Compiler V2.

Structured semantic IR -> bounded Python AST -> NativeDelta.

Brody describes program semantics with structured objects.
Obsidure owns Python syntax generation.

No external model.
No repository mutation.
No decision authority.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Any

from periphery.agents.obsidure_native_decomposer import (
    NativeDelta,
)


COMPILER_ID = "OBSIDURE_NATIVE_SEMANTIC_COMPILER_V2"


class NativeSemanticCompileError(RuntimeError):
    pass


@dataclass(frozen=True)
class SemanticOperation:
    kind: str
    target_path: str
    payload: dict[str, Any] = field(default_factory=dict)
    rationale: str = ""
    operation_id: str = ""


# ---------------------------------------------------------------------------
# Basic helpers
# ---------------------------------------------------------------------------


def _annotation(
    value: str | None,
) -> ast.expr | None:

    text = str(value or "").strip()

    if not text:
        return None

    try:
        return ast.parse(
            text,
            mode="eval",
        ).body

    except SyntaxError as exc:
        raise NativeSemanticCompileError(
            f"ANNOTATION_INVALID:{text}"
        ) from exc


def _symbol_expr(
    value: str,
) -> ast.expr:

    text = str(value or "").strip()

    if not text:
        raise NativeSemanticCompileError(
            "SYMBOL_REQUIRED"
        )

    parts = text.split(".")

    for part in parts:
        if not part.isidentifier():
            raise NativeSemanticCompileError(
                f"SYMBOL_INVALID:{text}"
            )

    node: ast.expr = ast.Name(
        id=parts[0],
        ctx=ast.Load(),
    )

    for part in parts[1:]:
        node = ast.Attribute(
            value=node,
            attr=part,
            ctx=ast.Load(),
        )

    return node


def _render(
    node: ast.AST,
) -> str:

    ast.fix_missing_locations(node)

    try:
        source = ast.unparse(node)
    except Exception as exc:
        raise NativeSemanticCompileError(
            f"AST_UNPARSE_FAILED:{type(exc).__name__}"
        ) from exc

    ast.parse(source)

    return source.rstrip() + "\n"


# ---------------------------------------------------------------------------
# Expression IR
# ---------------------------------------------------------------------------


_COMPARE_OPS: dict[str, type[ast.cmpop]] = {
    "EQ": ast.Eq,
    "NE": ast.NotEq,
    "LT": ast.Lt,
    "LTE": ast.LtE,
    "GT": ast.Gt,
    "GTE": ast.GtE,
    "IN": ast.In,
    "NOT_IN": ast.NotIn,
    "IS": ast.Is,
    "IS_NOT": ast.IsNot,
}


_BINARY_OPS: dict[str, type[ast.operator]] = {
    "ADD": ast.Add,
    "SUB": ast.Sub,
    "MULT": ast.Mult,
    "DIV": ast.Div,
    "FLOOR_DIV": ast.FloorDiv,
    "MOD": ast.Mod,
    "POW": ast.Pow,
}


def _expression(
    spec: dict[str, Any],
) -> ast.expr:

    if not isinstance(spec, dict):
        raise NativeSemanticCompileError(
            "EXPRESSION_SPEC_NOT_OBJECT"
        )

    kind = str(
        spec.get("kind", "")
        or ""
    ).upper()

    if kind == "NAME":

        return _symbol_expr(
            str(spec.get("id", "") or "")
        )

    if kind == "CONSTANT":

        return ast.Constant(
            value=spec.get("value")
        )

    if kind == "ATTRIBUTE":

        value_spec = spec.get("value")
        attr = str(
            spec.get("attr", "")
            or ""
        ).strip()

        if not isinstance(value_spec, dict):
            raise NativeSemanticCompileError(
                "ATTRIBUTE_VALUE_REQUIRED"
            )

        if not attr.isidentifier():
            raise NativeSemanticCompileError(
                f"ATTRIBUTE_NAME_INVALID:{attr}"
            )

        return ast.Attribute(
            value=_expression(value_spec),
            attr=attr,
            ctx=ast.Load(),
        )

    if kind == "CALL":

        func_spec = spec.get("func_expr")

        if isinstance(func_spec, dict):
            func = _expression(func_spec)
        else:
            func = _symbol_expr(
                str(
                    spec.get("func", "")
                    or ""
                )
            )

        raw_args = (
            spec.get("args")
            or []
        )

        if not isinstance(raw_args, list):
            raise NativeSemanticCompileError(
                "CALL_ARGS_NOT_LIST"
            )

        raw_keywords = (
            spec.get("keywords")
            or {}
        )

        if not isinstance(
            raw_keywords,
            dict,
        ):
            raise NativeSemanticCompileError(
                "CALL_KEYWORDS_NOT_OBJECT"
            )

        return ast.Call(
            func=func,
            args=[
                _expression(item)
                for item in raw_args
            ],
            keywords=[
                ast.keyword(
                    arg=str(key),
                    value=_expression(value),
                )
                for key, value
                in raw_keywords.items()
            ],
        )

    if kind == "LIST":

        values = (
            spec.get("items")
            or []
        )

        if not isinstance(values, list):
            raise NativeSemanticCompileError(
                "LIST_ITEMS_NOT_LIST"
            )

        return ast.List(
            elts=[
                _expression(item)
                for item in values
            ],
            ctx=ast.Load(),
        )

    if kind == "TUPLE":

        values = (
            spec.get("items")
            or []
        )

        if not isinstance(values, list):
            raise NativeSemanticCompileError(
                "TUPLE_ITEMS_NOT_LIST"
            )

        return ast.Tuple(
            elts=[
                _expression(item)
                for item in values
            ],
            ctx=ast.Load(),
        )

    if kind == "DICT":

        items = (
            spec.get("items")
            or []
        )

        if not isinstance(items, list):
            raise NativeSemanticCompileError(
                "DICT_ITEMS_NOT_LIST"
            )

        keys: list[ast.expr] = []
        values: list[ast.expr] = []

        for item in items:

            if not isinstance(item, dict):
                raise NativeSemanticCompileError(
                    "DICT_ITEM_NOT_OBJECT"
                )

            key_spec = item.get("key")
            value_spec = item.get("value")

            if not isinstance(key_spec, dict):
                raise NativeSemanticCompileError(
                    "DICT_KEY_REQUIRED"
                )

            if not isinstance(value_spec, dict):
                raise NativeSemanticCompileError(
                    "DICT_VALUE_REQUIRED"
                )

            keys.append(
                _expression(key_spec)
            )

            values.append(
                _expression(value_spec)
            )

        return ast.Dict(
            keys=keys,
            values=values,
        )

    if kind == "COMPARE":

        left = spec.get("left")
        right = spec.get("right")

        if not isinstance(left, dict):
            raise NativeSemanticCompileError(
                "COMPARE_LEFT_REQUIRED"
            )

        if not isinstance(right, dict):
            raise NativeSemanticCompileError(
                "COMPARE_RIGHT_REQUIRED"
            )

        op_name = str(
            spec.get("op", "")
            or ""
        ).upper()

        op_type = _COMPARE_OPS.get(
            op_name
        )

        if op_type is None:
            raise NativeSemanticCompileError(
                f"COMPARE_OP_UNSUPPORTED:{op_name}"
            )

        return ast.Compare(
            left=_expression(left),
            ops=[
                op_type(),
            ],
            comparators=[
                _expression(right),
            ],
        )

    if kind == "BOOL_OP":

        op_name = str(
            spec.get("op", "")
            or ""
        ).upper()

        values = (
            spec.get("values")
            or []
        )

        if not isinstance(values, list):
            raise NativeSemanticCompileError(
                "BOOL_VALUES_NOT_LIST"
            )

        if len(values) < 2:
            raise NativeSemanticCompileError(
                "BOOL_VALUES_TOO_FEW"
            )

        if op_name == "AND":
            op: ast.boolop = ast.And()

        elif op_name == "OR":
            op = ast.Or()

        else:
            raise NativeSemanticCompileError(
                f"BOOL_OP_UNSUPPORTED:{op_name}"
            )

        return ast.BoolOp(
            op=op,
            values=[
                _expression(item)
                for item in values
            ],
        )

    if kind == "NOT":

        operand = spec.get("operand")

        if not isinstance(operand, dict):
            raise NativeSemanticCompileError(
                "NOT_OPERAND_REQUIRED"
            )

        return ast.UnaryOp(
            op=ast.Not(),
            operand=_expression(
                operand
            ),
        )

    if kind == "BIN_OP":

        left = spec.get("left")
        right = spec.get("right")

        if not isinstance(left, dict):
            raise NativeSemanticCompileError(
                "BIN_LEFT_REQUIRED"
            )

        if not isinstance(right, dict):
            raise NativeSemanticCompileError(
                "BIN_RIGHT_REQUIRED"
            )

        op_name = str(
            spec.get("op", "")
            or ""
        ).upper()

        op_type = _BINARY_OPS.get(
            op_name
        )

        if op_type is None:
            raise NativeSemanticCompileError(
                f"BIN_OP_UNSUPPORTED:{op_name}"
            )

        return ast.BinOp(
            left=_expression(left),
            op=op_type(),
            right=_expression(right),
        )

    raise NativeSemanticCompileError(
        f"EXPRESSION_KIND_UNSUPPORTED:{kind}"
    )


# ---------------------------------------------------------------------------
# Statement IR
# ---------------------------------------------------------------------------


def _statement(
    spec: dict[str, Any],
) -> ast.stmt:

    if not isinstance(spec, dict):
        raise NativeSemanticCompileError(
            "STATEMENT_SPEC_NOT_OBJECT"
        )

    kind = str(
        spec.get("kind", "")
        or ""
    ).upper()

    if kind == "RETURN":

        expr = spec.get("expr")

        if expr is None:
            return ast.Return(
                value=None
            )

        if not isinstance(expr, dict):
            raise NativeSemanticCompileError(
                "RETURN_EXPR_NOT_OBJECT"
            )

        return ast.Return(
            value=_expression(expr)
        )

    if kind == "ASSIGN":

        name = str(
            spec.get("target", "")
            or ""
        ).strip()

        if not name.isidentifier():
            raise NativeSemanticCompileError(
                f"ASSIGN_TARGET_INVALID:{name}"
            )

        value = spec.get("value")

        if not isinstance(value, dict):
            raise NativeSemanticCompileError(
                "ASSIGN_VALUE_REQUIRED"
            )

        return ast.Assign(
            targets=[
                ast.Name(
                    id=name,
                    ctx=ast.Store(),
                )
            ],
            value=_expression(value),
        )

    if kind == "EXPR":

        expr = spec.get("expr")

        if not isinstance(expr, dict):
            raise NativeSemanticCompileError(
                "EXPR_VALUE_REQUIRED"
            )

        return ast.Expr(
            value=_expression(expr)
        )

    if kind == "IF":

        test = spec.get("test")

        if not isinstance(test, dict):
            raise NativeSemanticCompileError(
                "IF_TEST_REQUIRED"
            )

        raw_body = (
            spec.get("body")
            or []
        )

        raw_else = (
            spec.get("else")
            or []
        )

        if not isinstance(raw_body, list):
            raise NativeSemanticCompileError(
                "IF_BODY_NOT_LIST"
            )

        if not isinstance(raw_else, list):
            raise NativeSemanticCompileError(
                "IF_ELSE_NOT_LIST"
            )

        body = [
            _statement(item)
            for item in raw_body
        ]

        if not body:
            raise NativeSemanticCompileError(
                "IF_BODY_EMPTY"
            )

        return ast.If(
            test=_expression(test),
            body=body,
            orelse=[
                _statement(item)
                for item in raw_else
            ],
        )

    if kind == "RAISE":

        expr = spec.get("expr")

        if not isinstance(expr, dict):
            raise NativeSemanticCompileError(
                "RAISE_EXPR_REQUIRED"
            )

        return ast.Raise(
            exc=_expression(expr),
            cause=None,
        )

    if kind == "PASS":

        return ast.Pass()

    raise NativeSemanticCompileError(
        f"STATEMENT_KIND_UNSUPPORTED:{kind}"
    )


# ---------------------------------------------------------------------------
# Structures
# ---------------------------------------------------------------------------


def _render_function(
    payload: dict[str, Any],
) -> str:

    name = str(
        payload.get("name", "")
        or ""
    ).strip()

    if not name.isidentifier():
        raise NativeSemanticCompileError(
            f"FUNCTION_NAME_INVALID:{name}"
        )

    raw_args = (
        payload.get("args")
        or []
    )

    if not isinstance(raw_args, list):
        raise NativeSemanticCompileError(
            "FUNCTION_ARGS_NOT_LIST"
        )

    args: list[ast.arg] = []

    for item in raw_args:

        if not isinstance(item, dict):
            raise NativeSemanticCompileError(
                "FUNCTION_ARG_NOT_OBJECT"
            )

        arg_name = str(
            item.get("name", "")
            or ""
        ).strip()

        if not arg_name.isidentifier():
            raise NativeSemanticCompileError(
                f"FUNCTION_ARG_INVALID:{arg_name}"
            )

        args.append(
            ast.arg(
                arg=arg_name,
                annotation=_annotation(
                    item.get("annotation")
                ),
            )
        )

    raw_body = payload.get("body")

    if raw_body is not None:

        if not isinstance(
            raw_body,
            list,
        ):
            raise NativeSemanticCompileError(
                "FUNCTION_BODY_NOT_LIST"
            )

        body = [
            _statement(item)
            for item in raw_body
        ]

        if not body:
            raise NativeSemanticCompileError(
                "FUNCTION_BODY_EMPTY"
            )

    else:
        # V1 compatibility.
        return_spec = payload.get(
            "return_expr"
        )

        if not isinstance(
            return_spec,
            dict,
        ):
            raise NativeSemanticCompileError(
                "FUNCTION_BODY_OR_RETURN_EXPR_REQUIRED"
            )

        body = [
            ast.Return(
                value=_expression(
                    return_spec
                )
            )
        ]

    function = ast.FunctionDef(
        name=name,
        args=ast.arguments(
            posonlyargs=[],
            args=args,
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[],
        ),
        body=body,
        decorator_list=[],
        returns=_annotation(
            payload.get("returns")
        ),
        type_comment=None,
    )

    return _render(function)


def function_payload_fingerprint(
    payload: dict[str, Any],
) -> str:
    """
    Compile a desired function payload through the
    canonical Obsidure semantic compiler and return
    its location-independent AST fingerprint.

    No repository mutation.
    No external model.
    """
    source = _render_function(payload)

    tree = ast.parse(source)

    if (
        len(tree.body) != 1
        or not isinstance(
            tree.body[0],
            ast.FunctionDef,
        )
    ):
        raise NativeSemanticCompileError(
            "FUNCTION_FINGERPRINT_INVALID"
        )

    return ast.dump(
        tree.body[0],
        annotate_fields=True,
        include_attributes=False,
    )


def _render_class(
    payload: dict[str, Any],
) -> str:

    name = str(
        payload.get("name", "")
        or ""
    ).strip()

    if not name.isidentifier():
        raise NativeSemanticCompileError(
            f"CLASS_NAME_INVALID:{name}"
        )

    raw_bases = (
        payload.get("bases")
        or []
    )

    if not isinstance(raw_bases, list):
        raise NativeSemanticCompileError(
            "CLASS_BASES_NOT_LIST"
        )

    cls = ast.ClassDef(
        name=name,
        bases=[
            _symbol_expr(str(base))
            for base in raw_bases
        ],
        keywords=[],
        body=[
            ast.Pass()
        ],
        decorator_list=[],
    )

    return _render(cls)


def _render_field(
    payload: dict[str, Any],
) -> str:

    name = str(
        payload.get("name", "")
        or ""
    ).strip()

    if not name.isidentifier():
        raise NativeSemanticCompileError(
            f"FIELD_NAME_INVALID:{name}"
        )

    annotation = _annotation(
        payload.get("annotation")
    )

    if annotation is None:
        raise NativeSemanticCompileError(
            "FIELD_ANNOTATION_REQUIRED"
        )

    default_spec = payload.get(
        "default_expr"
    )

    value = None

    if default_spec is not None:

        if not isinstance(
            default_spec,
            dict,
        ):
            raise NativeSemanticCompileError(
                "FIELD_DEFAULT_EXPR_NOT_OBJECT"
            )

        value = _expression(
            default_spec
        )

    node = ast.AnnAssign(
        target=ast.Name(
            id=name,
            ctx=ast.Store(),
        ),
        annotation=annotation,
        value=value,
        simple=1,
    )

    return _render(
        node
    ).strip()


def field_payload_fingerprint(
    payload: dict[str, Any],
) -> str:
    """
    Compile one desired field through Obsidure's
    canonical field renderer and return a
    location-independent AST fingerprint.

    No repository mutation.
    No external model.
    """
    source = _render_field(payload)
    tree = ast.parse(source)

    if (
        len(tree.body) != 1
        or not isinstance(
            tree.body[0],
            (ast.Assign, ast.AnnAssign),
        )
    ):
        raise NativeSemanticCompileError(
            "FIELD_FINGERPRINT_INVALID"
        )

    return ast.dump(
        tree.body[0],
        annotate_fields=True,
        include_attributes=False,
    )


# ---------------------------------------------------------------------------
# Semantic operations -> NativeDelta
# ---------------------------------------------------------------------------


def compile_semantic_operations(
    operations: list[SemanticOperation],
) -> list[NativeDelta]:

    if not operations:
        raise NativeSemanticCompileError(
            "SEMANTIC_OPERATIONS_REQUIRED"
        )

    deltas: list[NativeDelta] = []

    for operation in operations:

        kind = str(
            operation.kind
            or ""
        ).upper()

        target = str(
            operation.target_path
            or ""
        ).replace("\\", "/").strip()

        if not target:
            raise NativeSemanticCompileError(
                "SEMANTIC_TARGET_REQUIRED"
            )

        payload = dict(
            operation.payload
            or {}
        )

        if kind == "CREATE_MODULE":

            docstring = str(
                payload.get(
                    "docstring",
                    "",
                )
                or ""
            )

            module = ast.Module(
                body=(
                    [
                        ast.Expr(
                            value=ast.Constant(
                                value=docstring
                            )
                        )
                    ]
                    if docstring
                    else [
                        ast.Pass()
                    ]
                ),
                type_ignores=[],
            )

            primitive = "CREATE_FILE"

            parameters = {
                "source": _render(module),
            }

        elif kind == "IMPORT_FROM":

            module = str(
                payload.get(
                    "module",
                    "",
                )
                or ""
            ).strip()

            names = (
                payload.get("names")
                or []
            )

            if not module:
                raise NativeSemanticCompileError(
                    "IMPORT_MODULE_REQUIRED"
                )

            if (
                not isinstance(names, list)
                or not names
            ):
                raise NativeSemanticCompileError(
                    "IMPORT_NAMES_REQUIRED"
                )

            statement = (
                f"from {module} import "
                + ", ".join(
                    str(name)
                    for name in names
                )
            )

            ast.parse(statement)

            primitive = "ADD_IMPORT"

            parameters = {
                "statement": statement,
            }

        elif kind == "ADD_CLASS":

            primitive = "ADD_CLASS"

            parameters = {
                "source": _render_class(
                    payload
                )
            }

        elif kind == "ADD_FIELD":

            class_name = str(
                payload.get(
                    "class_name",
                    "",
                )
                or ""
            ).strip()

            if not class_name.isidentifier():
                raise NativeSemanticCompileError(
                    f"FIELD_CLASS_INVALID:{class_name}"
                )

            primitive = "ADD_FIELD"

            parameters = {
                "class_name": class_name,
                "source": _render_field(
                    payload
                ),
            }

        elif kind == "MODIFY_FIELD":

            class_name = str(
                payload.get(
                    "class_name",
                    "",
                )
                or ""
            ).strip()

            name = str(
                payload.get(
                    "name",
                    "",
                )
                or ""
            ).strip()

            if not class_name.isidentifier():
                raise NativeSemanticCompileError(
                    f"FIELD_CLASS_INVALID:{class_name}"
                )

            if not name.isidentifier():
                raise NativeSemanticCompileError(
                    f"FIELD_NAME_INVALID:{name}"
                )

            primitive = "MODIFY_FIELD"

            parameters = {
                "class_name": class_name,
                "name": name,
                "source": _render_field(
                    payload
                ),
            }

        elif kind in (
            "ADD_METHOD",
            "MODIFY_METHOD",
        ):

            class_name = str(
                payload.get(
                    "class_name",
                    "",
                )
                or ""
            ).strip()

            name = str(
                payload.get(
                    "name",
                    "",
                )
                or ""
            ).strip()

            if not class_name.isidentifier():
                raise NativeSemanticCompileError(
                    f"METHOD_CLASS_INVALID:{class_name}"
                )

            if not name.isidentifier():
                raise NativeSemanticCompileError(
                    f"METHOD_NAME_INVALID:{name}"
                )

            primitive = kind

            parameters = {
                "class_name": class_name,
                "source": _render_function(
                    payload
                ),
            }

            if kind == "MODIFY_METHOD":
                parameters["name"] = name

        elif kind == "ADD_FUNCTION":

            primitive = "ADD_FUNCTION"

            parameters = {
                "source": _render_function(
                    payload
                )
            }

        elif kind == "MODIFY_FUNCTION":

            name = str(
                payload.get(
                    "name",
                    "",
                )
                or ""
            ).strip()

            primitive = "MODIFY_FUNCTION"

            parameters = {
                "name": name,
                "source": _render_function(
                    payload
                ),
            }

        else:

            raise NativeSemanticCompileError(
                f"SEMANTIC_OPERATION_UNSUPPORTED:{kind}"
            )

        deltas.append(
            NativeDelta(
                primitive=primitive,
                target_path=target,
                parameters=parameters,
                rationale=(
                    operation.rationale
                    or f"Semantic operation {kind}"
                ),
                delta_id=operation.operation_id,
            )
        )

    return deltas


def self_check() -> dict[str, Any]:

    return {
        "compiler_id": COMPILER_ID,
        "semantic_operations": [
            "CREATE_MODULE",
            "IMPORT_FROM",
            "ADD_CLASS",
            "ADD_FIELD",
            "MODIFY_FIELD",
            "ADD_METHOD",
            "MODIFY_METHOD",
            "ADD_FUNCTION",
            "MODIFY_FUNCTION",
        ],
        "expressions": [
            "NAME",
            "CONSTANT",
            "ATTRIBUTE",
            "CALL",
            "LIST",
            "TUPLE",
            "DICT",
            "COMPARE",
            "BOOL_OP",
            "NOT",
            "BIN_OP",
        ],
        "statements": [
            "RETURN",
            "ASSIGN",
            "EXPR",
            "IF",
            "RAISE",
            "PASS",
        ],
        "decision_authority": "KX108_ONLY",
        "emits_act": False,
        "kernel_mutation": False,
        "memory_write": False,
        "canonical_write": False,
        "world_action": False,
        "external_engine_called": False,
    }
