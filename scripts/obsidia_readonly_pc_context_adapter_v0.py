from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any


VERSION = "OBSIDIA_READONLY_PC_CONTEXT_ADAPTER_V0"
CONTEXT_KIND = "READONLY_PC_CONTEXT"
DECISION_AUTHORITY = "KX108_ONLY"

HARD_LIMITS = {
    "max_paths": 8,
    "max_services": 12,
    "max_commands": 4,
    "max_string": 160,
}

DEFAULT_LIMITS = dict(HARD_LIMITS)

SAFE_ENV_KEYS = (
    "OBSIDIA_OPENJARVIS_SOURCE",
    "OBSIDIA_OPENJARVIS_COMMIT",
    "OBSIDIA_JARVIS_SESSION_ID",
)

SECRET_MARKERS = (
    "API_KEY",
    "SECRET",
    "TOKEN",
    "PASSWORD",
    "BEARER",
    "PRIVATE_KEY",
    ".ENV",
)


def _normalized_limits(
    limits: dict[str, int] | None,
) -> dict[str, int]:
    requested = limits if isinstance(limits, dict) else {}
    normalized: dict[str, int] = {}

    for name, hard_max in HARD_LIMITS.items():
        raw = requested.get(name, DEFAULT_LIMITS[name])
        try:
            value = int(raw)
        except (TypeError, ValueError):
            value = DEFAULT_LIMITS[name]

        if name == "max_string":
            value = max(32, value)
        else:
            value = max(0, value)

        normalized[name] = min(value, hard_max)

    return normalized


def _bounded_text(value: Any, limit: int) -> str:
    text = str(value)
    if len(text) <= limit:
        return text
    return f"{text[: max(0, limit - 12)]}...<bounded>"


def _hash_text(value: Any) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:16]


def _looks_sensitive(value: Any) -> bool:
    upper = str(value).upper()
    return any(marker in upper for marker in SECRET_MARKERS)


def _inside(base: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False
    except OSError:
        return False


def _path_observation(
    candidate: Any,
    *,
    workspace: Path | None,
    string_limit: int,
) -> dict[str, Any]:
    raw = str(candidate)
    if _looks_sensitive(raw):
        return {
            "path_hash": _hash_text(raw),
            "redacted": True,
            "status": "SKIPPED_SENSITIVE_PATH",
        }

    path = Path(raw)
    if workspace is not None and not path.is_absolute():
        path = workspace / path

    item: dict[str, Any] = {
        "path": _bounded_text(str(path), string_limit),
        "exists": path.exists(),
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
        "readonly_observation_only": True,
    }
    if workspace is not None and _inside(workspace, path):
        try:
            item["workspace_relative_path"] = _bounded_text(
                str(path.resolve().relative_to(workspace.resolve())),
                string_limit,
            )
        except OSError:
            item["workspace_relative_path"] = None
    return item


def _workspace_binding(session_id: str | None) -> dict[str, Any]:
    if not session_id:
        return {"status": "SKIPPED_NO_SESSION_ID"}
    try:
        from scripts.obsidia_jarvis_workspace_binding_v0 import resolve_binding

        binding = resolve_binding(session_id)
    except Exception as exc:
        return {
            "status": "UNAVAILABLE",
            "error_type": type(exc).__name__,
        }

    if binding is None:
        return {"status": "UNBOUND"}

    if not isinstance(binding, dict):
        return {
            "status": "UNAVAILABLE",
            "error_type": "INVALID_BINDING_TYPE",
        }

    return {
        "status": "READY:WORKSPACE_BINDING",
        "session_id": binding.get("session_id"),
        "workspace": binding.get("workspace"),
        "git_head_at_bind": binding.get("git_head_at_bind"),
        "git_branch_at_bind": binding.get("git_branch_at_bind"),
        "git_status_source": "NOT_RECALCULATED_DEDUP_WORKSPACE_BINDING",
        "workspace_mutation_by_binding": binding.get(
            "workspace_mutation_by_binding",
            False,
        ),
    }


def _service_snapshot(include_services: bool, limit: int) -> dict[str, Any]:
    if not include_services:
        return {"status": "SKIPPED_BY_CALLER"}
    try:
        from scripts.obsidia_cli import build_runtime_service_map_v1

        service_map = build_runtime_service_map_v1()
    except Exception as exc:
        return {
            "status": "UNAVAILABLE",
            "error_type": type(exc).__name__,
        }

    if not isinstance(service_map, dict):
        return {
            "status": "UNAVAILABLE",
            "error_type": "INVALID_SERVICE_MAP_TYPE",
        }

    services = service_map.get("services", [])
    if not isinstance(services, list):
        services = []

    bounded = []
    for item in services[:limit]:
        if not isinstance(item, dict):
            continue
        bounded.append(
            {
                "name": item.get("name"),
                "label": item.get("label"),
                "status": item.get("status"),
                "required": item.get("required"),
            }
        )

    return {
        "status": "READY:RUNTIME_SERVICE_MAP_V1",
        "terminal_state": service_map.get("terminal_state"),
        "service_count": len(services) if isinstance(services, list) else 0,
        "services": bounded,
    }


def _command_policy_snapshot(
    commands: list[str],
    *,
    limit: int,
) -> dict[str, Any]:
    if not commands:
        return {"status": "SKIPPED_NO_COMMAND_SAMPLES"}

    root = Path(__file__).resolve().parents[1]
    gate_dir = (
        root
        / "periphery"
        / "brody_memory_readonly"
        / "brody_local_command_gate_readonly"
    )
    if str(gate_dir) not in sys.path:
        sys.path.insert(0, str(gate_dir))

    try:
        from brody_local_command_gate_readonly_v1 import evaluate_command
    except Exception as exc:
        return {
            "status": "UNAVAILABLE",
            "error_type": type(exc).__name__,
        }

    observations = []
    for command in commands[:limit]:
        try:
            result = evaluate_command({"command": command})
        except Exception as exc:
            observations.append(
                {
                    "status": "UNAVAILABLE",
                    "error_type": type(exc).__name__,
                    "command_hash": _hash_text(command),
                    "command_redacted": True,
                    "brody_execute_allowed": False,
                    "executed": False,
                }
            )
            continue

        if not isinstance(result, dict):
            result = {}

        observations.append(
            {
                "status": result.get("status"),
                "classification": result.get("classification"),
                "command_hash": _hash_text(command),
                "command_redacted": True,
                "brody_execute_allowed": result.get(
                    "brody_execute_allowed",
                    False,
                ),
                "executed": result.get("executed", False),
            }
        )

    return {
        "status": "READY:COMMAND_GATE_READONLY",
        "observations": observations,
    }


def build_readonly_pc_context(
    *,
    session_id: str | None = None,
    workspace: str | Path | None = None,
    path_candidates: list[str] | None = None,
    command_samples: list[str] | None = None,
    include_services: bool = False,
    limits: dict[str, int] | None = None,
) -> dict[str, Any]:
    effective_limits = _normalized_limits(limits)
    string_limit = effective_limits["max_string"]
    workspace_path = Path(workspace).resolve() if workspace else None

    binding = _workspace_binding(session_id)
    if workspace_path is None and isinstance(binding.get("workspace"), str):
        workspace_path = Path(binding["workspace"]).resolve()

    path_observations = [
        _path_observation(
            candidate,
            workspace=workspace_path,
            string_limit=string_limit,
        )
        for candidate in (path_candidates or [])[
            : effective_limits["max_paths"]
        ]
    ]

    env_observations = {
        key: {
            "present": key in os.environ,
            "value_hash": _hash_text(os.environ[key])
            if key in os.environ
            else None,
        }
        for key in SAFE_ENV_KEYS
    }

    snapshot: dict[str, Any] = {
        "kind": CONTEXT_KIND,
        "version": VERSION,
        "status": "READY:READONLY_PC_CONTEXT",
        "decision_authority": DECISION_AUTHORITY,
        "pc_context_authority": "NONE",
        "readonly": True,
        "advisory_only": True,
        "context_signal_only": True,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
        "emits_verdict": False,
        "memory_write": False,
        "kernel_mutation": False,
        "filesystem_mutation": False,
        "git_mutation": False,
        "process_mutation": False,
        "command_execution": False,
        "producers_reused": [
            "obsidia_jarvis_workspace_binding_v0.resolve_binding",
            "obsidia_cli.build_runtime_service_map_v1",
            "brody_local_command_gate_readonly_v1.evaluate_command",
        ],
        "workspace": {
            "binding": binding,
            "effective_workspace": _bounded_text(
                str(workspace_path),
                string_limit,
            )
            if workspace_path is not None
            else None,
        },
        "paths": path_observations,
        "services": _service_snapshot(
            include_services,
            effective_limits["max_services"],
        ),
        "environment": env_observations,
        "command_policy": _command_policy_snapshot(
            command_samples or [],
            limit=effective_limits["max_commands"],
        ),
        "limits": effective_limits,
    }
    snapshot["material_hash"] = _hash_text(
        json.dumps(snapshot, sort_keys=True, default=str)
    )
    return snapshot


def _validate_readonly_snapshot(
    snapshot: dict[str, Any],
) -> None:
    required = {
        "kind": CONTEXT_KIND,
        "decision_authority": DECISION_AUTHORITY,
        "pc_context_authority": "NONE",
        "readonly": True,
        "advisory_only": True,
        "context_signal_only": True,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
        "emits_verdict": False,
        "memory_write": False,
        "kernel_mutation": False,
        "filesystem_mutation": False,
        "git_mutation": False,
        "process_mutation": False,
        "command_execution": False,
    }

    for key, expected in required.items():
        if snapshot.get(key) != expected:
            raise ValueError(
                f"invalid readonly PC context invariant: {key}"
            )


def readonly_pc_context_to_context_item(
    snapshot: dict[str, Any],
) -> str:
    _validate_readonly_snapshot(snapshot)

    limits = _normalized_limits(
        snapshot.get("limits")
        if isinstance(snapshot.get("limits"), dict)
        else None
    )

    workspace = (
        snapshot.get("workspace", {})
        if isinstance(snapshot.get("workspace"), dict)
        else {}
    )
    binding = (
        workspace.get("binding", {})
        if isinstance(workspace.get("binding"), dict)
        else {}
    )

    compact_paths: list[dict[str, Any]] = []
    paths = snapshot.get("paths", [])
    if isinstance(paths, list):
        for item in paths[: limits["max_paths"]]:
            if not isinstance(item, dict):
                continue

            if item.get("redacted") is True:
                compact_paths.append(
                    {
                        "path_hash": item.get("path_hash"),
                        "redacted": True,
                        "status": item.get("status"),
                    }
                )
                continue

            relative = item.get("workspace_relative_path")
            compact_paths.append(
                {
                    "workspace_relative_path": (
                        _bounded_text(relative, limits["max_string"])
                        if relative
                        else None
                    ),
                    "path_hash": (
                        None
                        if relative
                        else _hash_text(item.get("path"))
                    ),
                    "exists": bool(item.get("exists")),
                    "is_file": bool(item.get("is_file")),
                    "is_dir": bool(item.get("is_dir")),
                }
            )

    services_packet = (
        snapshot.get("services", {})
        if isinstance(snapshot.get("services"), dict)
        else {}
    )
    compact_services: list[dict[str, Any]] = []
    services = services_packet.get("services", [])
    if isinstance(services, list):
        for item in services[: limits["max_services"]]:
            if not isinstance(item, dict):
                continue
            compact_services.append(
                {
                    "name": _bounded_text(
                        item.get("name"),
                        limits["max_string"],
                    ),
                    "status": _bounded_text(
                        item.get("status"),
                        limits["max_string"],
                    ),
                    "required": bool(item.get("required")),
                }
            )

    command_packet = (
        snapshot.get("command_policy", {})
        if isinstance(snapshot.get("command_policy"), dict)
        else {}
    )
    compact_commands: list[dict[str, Any]] = []
    observations = command_packet.get("observations", [])
    if isinstance(observations, list):
        for item in observations[: limits["max_commands"]]:
            if not isinstance(item, dict):
                continue
            compact_commands.append(
                {
                    "status": item.get("status"),
                    "classification": item.get("classification"),
                    "command_hash": item.get("command_hash"),
                    "brody_execute_allowed": bool(
                        item.get("brody_execute_allowed", False)
                    ),
                    "executed": bool(item.get("executed", False)),
                }
            )

    env_packet = (
        snapshot.get("environment", {})
        if isinstance(snapshot.get("environment"), dict)
        else {}
    )
    compact_env = {
        key: {
            "present": bool(value.get("present"))
        }
        for key, value in env_packet.items()
        if key in SAFE_ENV_KEYS and isinstance(value, dict)
    }

    compact = {
        "kind": CONTEXT_KIND,
        "status": snapshot.get("status"),
        "material_hash": snapshot.get("material_hash"),
        "authority": "NONE",
        "readonly": True,
        "allowed_to_act": False,
        "emits_act": False,
        "memory_write": False,
        "kernel_mutation": False,

        "workspace_binding": {
            "status": binding.get("status"),
            "git_head_at_bind": binding.get("git_head_at_bind"),
            "git_branch_at_bind": binding.get("git_branch_at_bind"),
        },

        "paths": compact_paths,

        "services": {
            "status": services_packet.get("status"),
            "terminal_state": services_packet.get("terminal_state"),
            "items": compact_services,
        },

        "environment": compact_env,

        "command_policy": {
            "status": command_packet.get("status"),
            "observations": compact_commands,
        },
    }

    return "READONLY_PC_CONTEXT:" + json.dumps(
        compact,
        sort_keys=True,
        separators=(",", ":"),
    )


__all__ = [
    "VERSION",
    "CONTEXT_KIND",
    "build_readonly_pc_context",
    "readonly_pc_context_to_context_item",
]
