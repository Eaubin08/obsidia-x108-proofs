"""
OBSIDIA / OpenJarvis Workspace Launcher V0.

PREPARE ONLY.

It resolves one governed Jarvis session to one isolated Git workspace
and produces the native OpenJarvis CLI launch plan.

It deliberately does NOT execute ``jarvis chat`` yet.

Reason:
the native OpenJarvis CLI has not yet been bound to the governed
Obsidia Cognitive Pilot. Launching it directly would bypass the
proved cognition/model-policy boundary.

Jarvis remains non-sovereign.
KX108 remains the sole decision authority.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

try:
    from scripts.obsidia_jarvis_workspace_binding_v0 import (
        WorkspaceBindingError,
        bind_workspace,
        close_binding,
        list_bindings,
        resolve_binding,
    )
except ModuleNotFoundError:
    from obsidia_jarvis_workspace_binding_v0 import (
        WorkspaceBindingError,
        bind_workspace,
        close_binding,
        list_bindings,
        resolve_binding,
    )


SCHEMA_VERSION = "OBSIDIA_JARVIS_WORKSPACE_LAUNCHER_V0"

AUTHORITY = "NONE"
DECISION_AUTHORITY = "KX108_ONLY"

OPENJARVIS_AUTHORITY = "NONE"
OPENJARVIS_MODEL_SELECTION = False

COGNITIVE_CLI_BOUND = False
REAL_LAUNCH_ENABLED = False


class WorkspaceLauncherError(RuntimeError):
    pass


def build_launch_plan(
    identifier: str,
    *,
    state_path=None,
    openjarvis_source: str | None = None,
    openjarvis_commit: str | None = None,
) -> dict:
    binding = resolve_binding(
        identifier,
        state_path=state_path,
    )

    workspace = Path(
        binding["workspace"]
    ).resolve(strict=False)

    if not workspace.exists():
        raise WorkspaceLauncherError(
            f"bound workspace no longer exists: {workspace}"
        )

    oj_source = (
        openjarvis_source
        or os.environ.get(
            "OBSIDIA_OPENJARVIS_SOURCE",
            "",
        ).strip()
    )

    oj_commit = (
        openjarvis_commit
        or os.environ.get(
            "OBSIDIA_OPENJARVIS_COMMIT",
            "",
        ).strip()
    )

    if not oj_source:
        raise WorkspaceLauncherError(
            "OBSIDIA_OPENJARVIS_SOURCE is required"
        )

    if not oj_commit:
        raise WorkspaceLauncherError(
            "OBSIDIA_OPENJARVIS_COMMIT is required"
        )

    source = Path(
        oj_source
    ).expanduser().resolve(strict=False)

    if not source.exists():
        raise WorkspaceLauncherError(
            f"OpenJarvis source missing: {source}"
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "READY_PREPARE_ONLY",
        "session_id": binding["session_id"],
        "session_label": binding["label"],
        "workspace": str(workspace),
        "workspace_head_at_bind": (
            binding["git_head_at_bind"]
        ),
        "workspace_branch_at_bind": (
            binding["git_branch_at_bind"]
        ),
        "openjarvis_source": str(source),
        "openjarvis_expected_commit": oj_commit,
        "native_cli": {
            "cwd": str(workspace),
            "argv": [
                "python",
                "-m",
                "openjarvis.cli",
                "chat",
            ],
            "environment": {
                "PYTHONPATH": str(
                    source / "src"
                ),
                "OBSIDIA_JARVIS_SESSION_ID": (
                    binding["session_id"]
                ),
                "OBSIDIA_JARVIS_SESSION_LABEL": (
                    binding["label"]
                ),
                "OBSIDIA_JARVIS_WORKSPACE": (
                    str(workspace)
                ),
                "OBSIDIA_OPENJARVIS_SOURCE": (
                    str(source)
                ),
                "OBSIDIA_OPENJARVIS_COMMIT": (
                    oj_commit
                ),
            },
        },
        "cognitive_cli_bound": False,
        "real_launch_enabled": False,
        "blocked_reason": (
            "OPENJARVIS_NATIVE_CLI_NOT_YET_BOUND_"
            "TO_OBSIDIA_COGNITIVE_PILOT"
        ),
        "authority": AUTHORITY,
        "openjarvis_authority": (
            OPENJARVIS_AUTHORITY
        ),
        "decision_authority": (
            DECISION_AUTHORITY
        ),
        "openjarvis_model_selection": False,
        "workspace_mutation": False,
        "native_memory_write": False,
        "emits_act": False,
        "kernel_mutation": False,
    }


def launch_workspace(
    identifier: str,
    *,
    state_path=None,
    openjarvis_source=None,
    openjarvis_commit=None,
) -> dict:
    plan = build_launch_plan(
        identifier,
        state_path=state_path,
        openjarvis_source=openjarvis_source,
        openjarvis_commit=openjarvis_commit,
    )

    return {
        **plan,
        "status": "BLOCKED",
        "launch_attempted": False,
        "launch_executed": False,
    }


def _emit(value) -> None:
    print(
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="obsidia-jarvis-workspace-launcher"
    )

    parser.add_argument(
        "--state",
        default=None,
    )

    parser.add_argument(
        "--openjarvis-source",
        default=None,
    )

    parser.add_argument(
        "--openjarvis-commit",
        default=None,
    )

    sub = parser.add_subparsers(
        dest="command",
        required=True,
    )

    bind_p = sub.add_parser("bind")
    bind_p.add_argument("label")
    bind_p.add_argument("workspace")

    prepare_p = sub.add_parser("prepare")
    prepare_p.add_argument("identifier")

    launch_p = sub.add_parser("launch")
    launch_p.add_argument("identifier")

    show_p = sub.add_parser("show")
    show_p.add_argument("identifier")

    sub.add_parser("list")

    close_p = sub.add_parser("close")
    close_p.add_argument("identifier")

    args = parser.parse_args(argv)

    try:
        if args.command == "bind":
            _emit(
                bind_workspace(
                    args.label,
                    args.workspace,
                    state_path=args.state,
                )
            )
            return 0

        if args.command == "prepare":
            _emit(
                build_launch_plan(
                    args.identifier,
                    state_path=args.state,
                    openjarvis_source=(
                        args.openjarvis_source
                    ),
                    openjarvis_commit=(
                        args.openjarvis_commit
                    ),
                )
            )
            return 0

        if args.command == "launch":
            _emit(
                launch_workspace(
                    args.identifier,
                    state_path=args.state,
                    openjarvis_source=(
                        args.openjarvis_source
                    ),
                    openjarvis_commit=(
                        args.openjarvis_commit
                    ),
                )
            )
            return 3

        if args.command == "show":
            _emit(
                resolve_binding(
                    args.identifier,
                    state_path=args.state,
                )
            )
            return 0

        if args.command == "list":
            _emit(
                list_bindings(
                    state_path=args.state,
                    active_only=True,
                )
            )
            return 0

        if args.command == "close":
            _emit(
                close_binding(
                    args.identifier,
                    state_path=args.state,
                )
            )
            return 0

    except (
        WorkspaceBindingError,
        WorkspaceLauncherError,
    ) as exc:
        _emit(
            {
                "status": "BLOCKED",
                "reason": str(exc),
                "authority": AUTHORITY,
                "decision_authority": (
                    DECISION_AUTHORITY
                ),
            }
        )
        return 2

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
