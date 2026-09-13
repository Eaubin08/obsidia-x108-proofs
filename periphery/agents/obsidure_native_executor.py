"""
Obsidure Native Executor V1.

Executes bounded NativePlan primitives against source text.

Properties:
- no repository write
- no external model
- no autonomous decision
- every generated Python source is reparsed before acceptance
"""

from __future__ import annotations

import ast
from dataclasses import asdict, dataclass, field
from typing import Any

from periphery.agents.obsidure_native_plan import NativePlanStep


EXECUTOR_ID = "OBSIDURE_NATIVE_EXECUTOR_V1"


class NativeExecutionError(RuntimeError):
    pass


@dataclass
class NativeExecutionResult:
    status: str
    step_id: str
    primitive: str
    target_path: str

    generated_source: str = ""
    errors: list[str] = field(default_factory=list)

    decision_authority: str = "KX108_ONLY"
    emits_act: bool = False
    kernel_mutation: bool = False
    memory_write: bool = False
    canonical_write: bool = False
    world_action: bool = False
    external_engine_called: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _parse_python(source: str, label: str) -> ast.Module:
    try:
        return ast.parse(source, filename=label)
    except SyntaxError as exc:
        raise NativeExecutionError(
            f"GENERATED_SOURCE_SYNTAX_ERROR:{exc.lineno}:{exc.msg}"
        ) from exc


def _validate_fragment(
    source: str,
    allowed: tuple[type, ...],
    label: str,
) -> ast.AST:
    try:
        tree = ast.parse(source, filename=label)
    except SyntaxError as exc:
        raise NativeExecutionError(
            f"FRAGMENT_SYNTAX_ERROR:{exc.lineno}:{exc.msg}"
        ) from exc

    if len(tree.body) != 1:
        raise NativeExecutionError("FRAGMENT_MUST_CONTAIN_ONE_TOP_LEVEL_NODE")

    node = tree.body[0]

    if not isinstance(node, allowed):
        raise NativeExecutionError(
            f"FRAGMENT_NODE_TYPE_UNSUPPORTED:{type(node).__name__}"
        )

    return node


def _finalize(source: str, target: str) -> str:
    _parse_python(source, target)
    return source


def _insert_after_imports(
    current_source: str,
    statement: str,
    target: str,
) -> str:
    tree = _parse_python(current_source, target)
    lines = current_source.splitlines(keepends=True)

    anchor = 0

    for node in tree.body:
        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
            and anchor == 0
        ):
            anchor = int(getattr(node, "end_lineno", node.lineno) or node.lineno)
            continue

        if isinstance(node, (ast.Import, ast.ImportFrom)):
            anchor = max(
                anchor,
                int(getattr(node, "end_lineno", node.lineno) or node.lineno),
            )

    normalized = statement.rstrip() + "\n"

    if normalized.strip() in {
        line.strip()
        for line in lines
    }:
        raise NativeExecutionError("IMPORT_ALREADY_PRESENT")

    generated = "".join(
        lines[:anchor]
        + [normalized]
        + lines[anchor:]
    )

    return _finalize(generated, target)


def _append_top_level_fragment(
    current_source: str,
    fragment: str,
    target: str,
    allowed: tuple[type, ...],
) -> str:
    _parse_python(current_source, target)
    _validate_fragment(fragment, allowed, target)

    prefix = current_source.rstrip()

    generated = (
        prefix
        + ("\n\n" if prefix else "")
        + fragment.strip()
        + "\n"
    )

    return _finalize(generated, target)


def _replace_named_definition(
    current_source: str,
    name: str,
    fragment: str,
    target: str,
    allowed: tuple[type, ...],
) -> str:
    tree = _parse_python(current_source, target)
    replacement = _validate_fragment(fragment, allowed, target)

    replacement_name = getattr(replacement, "name", "")

    if replacement_name != name:
        raise NativeExecutionError(
            f"REPLACEMENT_NAME_MISMATCH:{replacement_name}:{name}"
        )

    matches = [
        node
        for node in tree.body
        if isinstance(node, allowed)
        and getattr(node, "name", "") == name
    ]

    if len(matches) != 1:
        raise NativeExecutionError(
            f"TARGET_DEFINITION_COUNT:{name}:{len(matches)}"
        )

    node = matches[0]

    start = int(node.lineno) - 1
    end = int(getattr(node, "end_lineno", node.lineno))

    lines = current_source.splitlines(keepends=True)

    replacement_text = fragment.strip() + "\n"

    generated = "".join(
        lines[:start]
        + [replacement_text]
        + lines[end:]
    )

    return _finalize(generated, target)


def _add_class_field(
    current_source: str,
    class_name: str,
    field_source: str,
    target: str,
) -> str:
    tree = _parse_python(current_source, target)

    classes = [
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        and node.name == class_name
    ]

    if len(classes) != 1:
        raise NativeExecutionError(
            f"TARGET_CLASS_COUNT:{class_name}:{len(classes)}"
        )

    cls = classes[0]

    field_node = _validate_fragment(
        field_source,
        (ast.Assign, ast.AnnAssign),
        target,
    )

    field_names: set[str] = set()

    if isinstance(field_node, ast.Assign):
        for item in field_node.targets:
            if isinstance(item, ast.Name):
                field_names.add(item.id)

    elif isinstance(field_node, ast.AnnAssign):
        if isinstance(field_node.target, ast.Name):
            field_names.add(field_node.target.id)

    if not field_names:
        raise NativeExecutionError("FIELD_NAME_NOT_RESOLVED")

    for node in cls.body:
        existing: set[str] = set()

        if isinstance(node, ast.Assign):
            existing.update(
                item.id
                for item in node.targets
                if isinstance(item, ast.Name)
            )

        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name):
                existing.add(node.target.id)

        if existing & field_names:
            raise NativeExecutionError(
                "FIELD_ALREADY_PRESENT:"
                + ",".join(sorted(existing & field_names))
            )

    lines = current_source.splitlines(keepends=True)

    if cls.body:
        first = cls.body[0]
        insertion_line = int(first.lineno) - 1

        if (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            insertion_line = int(
                getattr(first, "end_lineno", first.lineno)
                or first.lineno
            )
    else:
        insertion_line = int(cls.lineno)

    indented = "\n".join(
        "    " + line if line.strip() else line
        for line in field_source.strip().splitlines()
    ) + "\n"

    generated = "".join(
        lines[:insertion_line]
        + [indented]
        + lines[insertion_line:]
    )

    return _finalize(generated, target)


def _replace_class_field(
    current_source: str,
    class_name: str,
    field_name: str,
    field_source: str,
    target: str,
) -> str:
    tree = _parse_python(
        current_source,
        target,
    )

    classes = [
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        and node.name == class_name
    ]

    if len(classes) != 1:
        raise NativeExecutionError(
            f"TARGET_CLASS_COUNT:"
            f"{class_name}:{len(classes)}"
        )

    cls = classes[0]

    replacement = _validate_fragment(
        field_source,
        (ast.Assign, ast.AnnAssign),
        target,
    )

    replacement_names: set[str] = set()

    if isinstance(replacement, ast.Assign):
        replacement_names.update(
            item.id
            for item in replacement.targets
            if isinstance(item, ast.Name)
        )

        # Fail closed: replacing
        #   field = other.attr = value
        # would silently introduce/mutate another target.
        if not (
            len(replacement.targets) == 1
            and isinstance(
                replacement.targets[0],
                ast.Name,
            )
            and replacement.targets[0].id
            == field_name
        ):
            raise NativeExecutionError(
                "FIELD_REPLACEMENT_NOT_ISOLATED:"
                f"{class_name}.{field_name}"
            )

    elif isinstance(replacement, ast.AnnAssign):
        if not (
            isinstance(
                replacement.target,
                ast.Name,
            )
            and replacement.target.id
            == field_name
            and replacement.simple == 1
        ):
            raise NativeExecutionError(
                "FIELD_REPLACEMENT_NOT_ISOLATED:"
                f"{class_name}.{field_name}"
            )

        replacement_names.add(
            replacement.target.id
        )

    if replacement_names != {field_name}:
        raise NativeExecutionError(
            "FIELD_REPLACEMENT_NAME_MISMATCH:"
            + ",".join(
                sorted(replacement_names)
            )
            + f":{field_name}"
        )

    matches: list[ast.stmt] = []

    for node in cls.body:
        names: set[str] = set()

        if isinstance(node, ast.Assign):
            names.update(
                item.id
                for item in node.targets
                if isinstance(item, ast.Name)
            )

        elif (
            isinstance(node, ast.AnnAssign)
            and isinstance(
                node.target,
                ast.Name,
            )
        ):
            names.add(node.target.id)

        if field_name in names:
            # Never trust the reduced name set alone.
            # An Assign may also contain Attribute/Subscript
            # targets that are not represented in `names`.
            if isinstance(node, ast.Assign):
                isolated = (
                    len(node.targets) == 1
                    and isinstance(
                        node.targets[0],
                        ast.Name,
                    )
                    and node.targets[0].id
                    == field_name
                )

            elif isinstance(
                node,
                ast.AnnAssign,
            ):
                isolated = (
                    isinstance(
                        node.target,
                        ast.Name,
                    )
                    and node.target.id
                    == field_name
                    and node.simple == 1
                )

            else:
                isolated = False

            if not isolated:
                raise NativeExecutionError(
                    "FIELD_TARGET_NOT_ISOLATED:"
                    f"{class_name}.{field_name}"
                )

            matches.append(node)

    if len(matches) != 1:
        raise NativeExecutionError(
            "TARGET_FIELD_COUNT:"
            f"{class_name}.{field_name}:"
            f"{len(matches)}"
        )

    node = matches[0]

    start = int(node.lineno) - 1
    end = int(
        getattr(
            node,
            "end_lineno",
            node.lineno,
        )
    )

    lines = current_source.splitlines(
        keepends=True
    )

    current_line = lines[start]

    indent = current_line[
        : len(current_line)
        - len(current_line.lstrip())
    ]

    replacement_text = (
        "\n".join(
            indent + line
            if line.strip()
            else line
            for line in (
                field_source
                .strip()
                .splitlines()
            )
        )
        + "\n"
    )

    generated = "".join(
        lines[:start]
        + [replacement_text]
        + lines[end:]
    )

    return _finalize(
        generated,
        target,
    )



def _add_class_method(
    current_source: str,
    class_name: str,
    method_source: str,
    target: str,
) -> str:
    tree = _parse_python(
        current_source,
        target,
    )

    classes = [
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        and node.name == class_name
    ]

    if len(classes) != 1:
        raise NativeExecutionError(
            "TARGET_CLASS_COUNT:"
            f"{class_name}:{len(classes)}"
        )

    cls = classes[0]

    replacement = _validate_fragment(
        method_source,
        (ast.FunctionDef,),
        target,
    )

    method_name = replacement.name

    matches = [
        node
        for node in cls.body
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
        and node.name == method_name
    ]

    if matches:
        raise NativeExecutionError(
            "METHOD_ALREADY_PRESENT:"
            f"{class_name}.{method_name}"
        )

    lines = current_source.splitlines(
        keepends=True
    )

    if cls.body:
        last = cls.body[-1]
        insertion_line = int(
            getattr(
                last,
                "end_lineno",
                last.lineno,
            )
        )
    else:
        insertion_line = int(cls.lineno)

    indented = (
        "\n".join(
            "    " + line
            if line.strip()
            else line
            for line in (
                method_source
                .strip()
                .splitlines()
            )
        )
        + "\n"
    )

    prefix = ""

    if (
        insertion_line > 0
        and insertion_line <= len(lines)
        and lines[insertion_line - 1].strip()
    ):
        prefix = "\n"

    generated = "".join(
        lines[:insertion_line]
        + [prefix + indented]
        + lines[insertion_line:]
    )

    return _finalize(
        generated,
        target,
    )


def _replace_class_method(
    current_source: str,
    class_name: str,
    method_name: str,
    method_source: str,
    target: str,
) -> str:
    tree = _parse_python(
        current_source,
        target,
    )

    classes = [
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        and node.name == class_name
    ]

    if len(classes) != 1:
        raise NativeExecutionError(
            "TARGET_CLASS_COUNT:"
            f"{class_name}:{len(classes)}"
        )

    cls = classes[0]

    replacement = _validate_fragment(
        method_source,
        (ast.FunctionDef,),
        target,
    )

    if replacement.decorator_list:
        raise NativeExecutionError(
            "METHOD_REPLACEMENT_REWRITE_UNSAFE:"
            f"{class_name}.{method_name}"
        )

    if replacement.name != method_name:
        raise NativeExecutionError(
            "METHOD_REPLACEMENT_NAME_MISMATCH:"
            f"{replacement.name}:{method_name}"
        )

    matches = [
        node
        for node in cls.body
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
        and node.name == method_name
    ]

    if len(matches) != 1:
        raise NativeExecutionError(
            "TARGET_METHOD_COUNT:"
            f"{class_name}.{method_name}:"
            f"{len(matches)}"
        )

    node = matches[0]

    if (
        not isinstance(
            node,
            ast.FunctionDef,
        )
        or node.decorator_list
    ):
        raise NativeExecutionError(
            "METHOD_TARGET_REWRITE_UNSAFE:"
            f"{class_name}.{method_name}"
        )

    start = int(node.lineno) - 1
    end = int(
        getattr(
            node,
            "end_lineno",
            node.lineno,
        )
    )

    lines = current_source.splitlines(
        keepends=True
    )

    current_line = lines[start]

    indent = current_line[
        : len(current_line)
        - len(current_line.lstrip())
    ]

    replacement_text = (
        "\n".join(
            indent + line
            if line.strip()
            else line
            for line in (
                method_source
                .strip()
                .splitlines()
            )
        )
        + "\n"
    )

    generated = "".join(
        lines[:start]
        + [replacement_text]
        + lines[end:]
    )

    return _finalize(
        generated,
        target,
    )


def execute_native_step(
    step: NativePlanStep,
    current_source: str,
) -> NativeExecutionResult:
    primitive = step.primitive
    params = dict(step.parameters or {})
    target = step.target_path

    try:
        if primitive == "CREATE_FILE":
            if current_source.strip():
                raise NativeExecutionError(
                    "CREATE_FILE_TARGET_ALREADY_EXISTS"
                )

            source = str(
                params.get("source", "")
                or ""
            )

            if not source.strip():
                raise NativeExecutionError(
                    "CREATE_FILE_SOURCE_REQUIRED"
                )

            generated = _finalize(
                source.rstrip() + "\n",
                target,
            )

        elif primitive == "ADD_IMPORT":
            statement = str(params.get("statement", "") or "").strip()

            if not statement.startswith(("import ", "from ")):
                raise NativeExecutionError(
                    "ADD_IMPORT_STATEMENT_REQUIRED"
                )

            generated = _insert_after_imports(
                current_source,
                statement,
                target,
            )

        elif primitive in ("ADD_FUNCTION", "ADD_TEST"):
            fragment = str(
                params.get("source", "")
                or ""
            )

            generated = _append_top_level_fragment(
                current_source,
                fragment,
                target,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            )

        elif primitive == "ADD_CLASS":
            fragment = str(
                params.get("source", "")
                or ""
            )

            generated = _append_top_level_fragment(
                current_source,
                fragment,
                target,
                (ast.ClassDef,),
            )

        elif primitive == "MODIFY_FUNCTION":
            name = str(params.get("name", "") or "")
            fragment = str(params.get("source", "") or "")

            if not name:
                raise NativeExecutionError(
                    "MODIFY_FUNCTION_NAME_REQUIRED"
                )


            # Fail closed independently of the planner.
            # Native semantic generation currently owns only
            # synchronous, undecorated functions.
            replacement_node = _validate_fragment(
                fragment,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
                target,
            )

            if (
                not isinstance(
                    replacement_node,
                    ast.FunctionDef,
                )
                or replacement_node.decorator_list
            ):
                raise NativeExecutionError(
                    "FUNCTION_REPLACEMENT_REWRITE_UNSAFE:"
                    f"{name}"
                )

            current_tree = _parse_python(
                current_source,
                target,
            )

            current_matches = [
                node
                for node in current_tree.body
                if isinstance(
                    node,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                    ),
                )
                and node.name == name
            ]

            if len(current_matches) == 1:
                current_node = current_matches[0]

                if (
                    not isinstance(
                        current_node,
                        ast.FunctionDef,
                    )
                    or current_node.decorator_list
                ):
                    raise NativeExecutionError(
                        "FUNCTION_TARGET_REWRITE_UNSAFE:"
                        f"{name}"
                    )

            generated = _replace_named_definition(
                current_source,
                name,
                fragment,
                target,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            )

        elif primitive == "MODIFY_CLASS":
            name = str(params.get("name", "") or "")
            fragment = str(params.get("source", "") or "")

            if not name:
                raise NativeExecutionError(
                    "MODIFY_CLASS_NAME_REQUIRED"
                )

            generated = _replace_named_definition(
                current_source,
                name,
                fragment,
                target,
                (ast.ClassDef,),
            )

        elif primitive == "ADD_FIELD":
            class_name = str(
                params.get("class_name", "")
                or ""
            )
            field_source = str(
                params.get("source", "")
                or ""
            )

            if not class_name:
                raise NativeExecutionError(
                    "ADD_FIELD_CLASS_REQUIRED"
                )

            generated = _add_class_field(
                current_source,
                class_name,
                field_source,
                target,
            )

        elif primitive == "MODIFY_FIELD":
            class_name = str(
                params.get(
                    "class_name",
                    "",
                )
                or ""
            )

            field_name = str(
                params.get(
                    "name",
                    "",
                )
                or ""
            )

            field_source = str(
                params.get(
                    "source",
                    "",
                )
                or ""
            )

            if not class_name:
                raise NativeExecutionError(
                    "MODIFY_FIELD_CLASS_REQUIRED"
                )

            if not field_name:
                raise NativeExecutionError(
                    "MODIFY_FIELD_NAME_REQUIRED"
                )

            generated = _replace_class_field(
                current_source,
                class_name,
                field_name,
                field_source,
                target,
            )

        elif primitive == "ADD_METHOD":
            class_name = str(
                params.get(
                    "class_name",
                    "",
                )
                or ""
            )

            method_source = str(
                params.get(
                    "source",
                    "",
                )
                or ""
            )

            if not class_name:
                raise NativeExecutionError(
                    "ADD_METHOD_CLASS_REQUIRED"
                )

            generated = _add_class_method(
                current_source,
                class_name,
                method_source,
                target,
            )

        elif primitive == "MODIFY_METHOD":
            class_name = str(
                params.get(
                    "class_name",
                    "",
                )
                or ""
            )

            method_name = str(
                params.get(
                    "name",
                    "",
                )
                or ""
            )

            method_source = str(
                params.get(
                    "source",
                    "",
                )
                or ""
            )

            if not class_name:
                raise NativeExecutionError(
                    "MODIFY_METHOD_CLASS_REQUIRED"
                )

            if not method_name:
                raise NativeExecutionError(
                    "MODIFY_METHOD_NAME_REQUIRED"
                )

            generated = _replace_class_method(
                current_source,
                class_name,
                method_name,
                method_source,
                target,
            )

        else:
            raise NativeExecutionError(
                f"NATIVE_EXECUTOR_UNSUPPORTED:{primitive}"
            )

        return NativeExecutionResult(
            status="PASS",
            step_id=step.step_id,
            primitive=primitive,
            target_path=target,
            generated_source=generated,
        )

    except NativeExecutionError as exc:
        return NativeExecutionResult(
            status="BLOCKED",
            step_id=step.step_id,
            primitive=primitive,
            target_path=target,
            errors=[str(exc)],
        )


def self_check() -> dict[str, Any]:
    return {
        "executor_id": EXECUTOR_ID,
        "supported": [
            "CREATE_FILE",
            "ADD_IMPORT",
            "ADD_FUNCTION",
            "ADD_TEST",
            "ADD_CLASS",
            "MODIFY_FUNCTION",
            "ADD_METHOD",
            "MODIFY_METHOD",
            "MODIFY_CLASS",
            "ADD_FIELD",
            "MODIFY_FIELD",
        ],
        "decision_authority": "KX108_ONLY",
        "emits_act": False,
        "kernel_mutation": False,
        "memory_write": False,
        "canonical_write": False,
        "world_action": False,
        "external_engine_called": False,
    }
