"""
OBSIDIA / OpenJarvis Session-Workspace Binding V0.

Operational binding only.

One active Jarvis session <-> one Git workspace/worktree.

This module:
- does not mutate the target Git workspace;
- does not mutate OpenJarvis;
- does not write Native Memory;
- does not make decisions;
- does not grant execution authority;
- persists only non-canonical operational binding metadata.

Jarvis remains non-sovereign.
KX108 remains the sole decision authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


SCHEMA_VERSION = "OBSIDIA_JARVIS_SESSION_WORKSPACE_BINDING_V0"
AUTHORITY = "NONE"
DECISION_AUTHORITY = "KX108_ONLY"

JARVIS_IS_AUTHORITY = False
JARVIS_MEMORY_IS_CANONICAL = False
NATIVE_MEMORY_WRITE = False
EMITS_ACT = False
KERNEL_MUTATION = False
WORKSPACE_MUTATION = False


class WorkspaceBindingError(RuntimeError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_state_path() -> Path:
    override = os.environ.get(
        "OBSIDIA_JARVIS_SESSION_STATE",
        "",
    ).strip()

    if override:
        return Path(override).expanduser().resolve(
            strict=False
        )

    local = os.environ.get(
        "LOCALAPPDATA",
        "",
    ).strip()

    if local:
        base = Path(local)
    else:
        base = Path.home() / ".local" / "share"

    return (
        base
        / "Obsidia"
        / "jarvis"
        / "session_workspace_v0.json"
    ).resolve(strict=False)


def _run_git(
    workspace: Path,
    *args: str,
) -> str:
    proc = subprocess.run(
        [
            "git",
            "-C",
            str(workspace),
            *args,
        ],
        capture_output=True,
        text=True,
        shell=False,
        timeout=10,
    )

    if proc.returncode != 0:
        detail = (
            proc.stderr.strip()
            or proc.stdout.strip()
            or "git command failed"
        )

        raise WorkspaceBindingError(detail)

    return proc.stdout.strip()


def inspect_workspace(
    workspace: str | os.PathLike[str],
) -> dict:
    candidate = Path(workspace).expanduser().resolve(
        strict=False
    )

    if not candidate.exists():
        raise WorkspaceBindingError(
            f"workspace does not exist: {candidate}"
        )

    if not candidate.is_dir():
        raise WorkspaceBindingError(
            f"workspace is not a directory: {candidate}"
        )

    root_raw = _run_git(
        candidate,
        "rev-parse",
        "--show-toplevel",
    )

    root = Path(root_raw).resolve(strict=False)

    if root != candidate:
        raise WorkspaceBindingError(
            "workspace must be the Git/worktree root: "
            f"{root}"
        )

    head = _run_git(
        root,
        "rev-parse",
        "HEAD",
    )

    branch_proc = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "symbolic-ref",
            "--quiet",
            "--short",
            "HEAD",
        ],
        capture_output=True,
        text=True,
        shell=False,
        timeout=10,
    )

    branch = (
        branch_proc.stdout.strip()
        if branch_proc.returncode == 0
        else "DETACHED"
    )

    common_dir_raw = _run_git(
        root,
        "rev-parse",
        "--git-common-dir",
    )

    common_dir_path = Path(common_dir_raw)

    if not common_dir_path.is_absolute():
        common_dir_path = (
            root / common_dir_path
        )

    common_dir = str(
        common_dir_path.resolve(strict=False)
    )

    return {
        "workspace": str(root),
        "head": head,
        "branch": branch,
        "git_common_dir": common_dir,
    }


def _empty_state() -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "authority": AUTHORITY,
        "decision_authority": DECISION_AUTHORITY,
        "jarvis_is_authority": False,
        "jarvis_memory_is_canonical": False,
        "native_memory_write": False,
        "emits_act": False,
        "kernel_mutation": False,
        "workspace_mutation": False,
        "bindings": [],
    }


def _load_state(path: Path) -> dict:
    if not path.exists():
        return _empty_state()

    try:
        obj = json.loads(
            path.read_text(encoding="utf-8")
        )
    except Exception as exc:
        raise WorkspaceBindingError(
            f"invalid binding state: {exc}"
        ) from exc

    if not isinstance(obj, dict):
        raise WorkspaceBindingError(
            "binding state must be an object"
        )

    if obj.get("schema_version") != SCHEMA_VERSION:
        raise WorkspaceBindingError(
            "unexpected binding state schema"
        )

    bindings = obj.get("bindings")

    if not isinstance(bindings, list):
        raise WorkspaceBindingError(
            "bindings must be a list"
        )

    return obj


def _save_state(
    path: Path,
    state: dict,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    tmp = path.with_name(
        path.name + f".{os.getpid()}.tmp"
    )

    payload = json.dumps(
        state,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"

    tmp.write_text(
        payload,
        encoding="utf-8",
        newline="\n",
    )

    os.replace(tmp, path)


@contextmanager
def _state_lock(
    state_path: Path,
) -> Iterator[None]:
    state_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    lock = state_path.with_name(
        state_path.name + ".lock"
    )

    acquired = False

    for _ in range(60):
        try:
            fd = os.open(
                str(lock),
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            )

            with os.fdopen(
                fd,
                "w",
                encoding="utf-8",
            ) as handle:
                handle.write(
                    json.dumps(
                        {
                            "pid": os.getpid(),
                            "created_at": _utc_now(),
                        }
                    )
                )

            acquired = True
            break

        except FileExistsError:
            try:
                age = (
                    time.time()
                    - lock.stat().st_mtime
                )

                if age > 30:
                    lock.unlink(missing_ok=True)
                    continue

            except FileNotFoundError:
                continue

            time.sleep(0.05)

    if not acquired:
        raise WorkspaceBindingError(
            "binding state is locked"
        )

    try:
        yield
    finally:
        lock.unlink(missing_ok=True)


def _session_id(
    label: str,
    workspace: str,
) -> str:
    digest = hashlib.sha256(
        (
            SCHEMA_VERSION
            + "\n"
            + label
            + "\n"
            + workspace
        ).encode("utf-8")
    ).hexdigest()

    return "jws-" + digest[:20]


def bind_workspace(
    label: str,
    workspace: str | os.PathLike[str],
    *,
    state_path: str | os.PathLike[str] | None = None,
) -> dict:
    clean_label = label.strip()

    if not clean_label:
        raise WorkspaceBindingError(
            "session label is required"
        )

    if len(clean_label) > 100:
        raise WorkspaceBindingError(
            "session label too long"
        )

    info = inspect_workspace(workspace)

    path = (
        Path(state_path).expanduser().resolve(
            strict=False
        )
        if state_path is not None
        else _default_state_path()
    )

    with _state_lock(path):
        state = _load_state(path)

        active = [
            item
            for item in state["bindings"]
            if item.get("active") is True
        ]

        for item in active:
            same_label = (
                item.get("label")
                == clean_label
            )

            same_workspace = (
                item.get("workspace")
                == info["workspace"]
            )

            if same_label and same_workspace:
                return dict(item)

            if same_label:
                raise WorkspaceBindingError(
                    "session label already bound "
                    "to another active workspace"
                )

            if same_workspace:
                raise WorkspaceBindingError(
                    "workspace already bound "
                    "to another active session"
                )

        binding = {
            "session_id": _session_id(
                clean_label,
                info["workspace"],
            ),
            "label": clean_label,
            "workspace": info["workspace"],
            "git_head_at_bind": info["head"],
            "git_branch_at_bind": info["branch"],
            "git_common_dir": info[
                "git_common_dir"
            ],
            "active": True,
            "created_at": _utc_now(),
            "closed_at": None,
            "authority": AUTHORITY,
            "decision_authority": (
                DECISION_AUTHORITY
            ),
            "jarvis_memory_is_canonical": False,
            "native_memory_write": False,
            "emits_act": False,
            "kernel_mutation": False,
            "workspace_mutation_by_binding": False,
        }

        state["bindings"].append(binding)
        _save_state(path, state)

        return dict(binding)


def list_bindings(
    *,
    state_path: str | os.PathLike[str] | None = None,
    active_only: bool = False,
) -> list[dict]:
    path = (
        Path(state_path).expanduser().resolve(
            strict=False
        )
        if state_path is not None
        else _default_state_path()
    )

    state = _load_state(path)

    bindings = [
        dict(item)
        for item in state["bindings"]
    ]

    if active_only:
        bindings = [
            item
            for item in bindings
            if item.get("active") is True
        ]

    return bindings


def resolve_binding(
    identifier: str,
    *,
    state_path: str | os.PathLike[str] | None = None,
) -> dict:
    needle = identifier.strip()

    for item in list_bindings(
        state_path=state_path,
        active_only=True,
    ):
        if needle in (
            item.get("session_id"),
            item.get("label"),
        ):
            return item

    raise WorkspaceBindingError(
        f"active session not found: {needle}"
    )


def close_binding(
    identifier: str,
    *,
    state_path: str | os.PathLike[str] | None = None,
) -> dict:
    path = (
        Path(state_path).expanduser().resolve(
            strict=False
        )
        if state_path is not None
        else _default_state_path()
    )

    needle = identifier.strip()

    with _state_lock(path):
        state = _load_state(path)

        found = None

        for item in state["bindings"]:
            if (
                item.get("active") is True
                and needle
                in (
                    item.get("session_id"),
                    item.get("label"),
                )
            ):
                item["active"] = False
                item["closed_at"] = _utc_now()
                found = dict(item)
                break

        if found is None:
            raise WorkspaceBindingError(
                f"active session not found: {needle}"
            )

        _save_state(path, state)

        return found


def _print(value) -> None:
    print(
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


def main(
    argv: list[str] | None = None,
) -> int:
    parser = argparse.ArgumentParser(
        prog="obsidia-jarvis-workspace",
    )

    parser.add_argument(
        "--state",
        default=None,
    )

    sub = parser.add_subparsers(
        dest="command",
        required=True,
    )

    bind_p = sub.add_parser("bind")
    bind_p.add_argument("label")
    bind_p.add_argument("workspace")

    list_p = sub.add_parser("list")
    list_p.add_argument(
        "--all",
        action="store_true",
    )

    show_p = sub.add_parser("show")
    show_p.add_argument("identifier")

    close_p = sub.add_parser("close")
    close_p.add_argument("identifier")

    args = parser.parse_args(argv)

    try:
        if args.command == "bind":
            _print(
                bind_workspace(
                    args.label,
                    args.workspace,
                    state_path=args.state,
                )
            )
            return 0

        if args.command == "list":
            _print(
                list_bindings(
                    state_path=args.state,
                    active_only=not args.all,
                )
            )
            return 0

        if args.command == "show":
            _print(
                resolve_binding(
                    args.identifier,
                    state_path=args.state,
                )
            )
            return 0

        if args.command == "close":
            _print(
                close_binding(
                    args.identifier,
                    state_path=args.state,
                )
            )
            return 0

    except WorkspaceBindingError as exc:
        print(
            json.dumps(
                {
                    "status": "BLOCKED",
                    "reason": str(exc),
                    "authority": AUTHORITY,
                    "decision_authority": (
                        DECISION_AUTHORITY
                    ),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 2

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
