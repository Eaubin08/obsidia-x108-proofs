#!/usr/bin/env python3
"""OpenJarvis peripheral runtime adapter V0.2.

This adapter establishes a real process boundary to an external OpenJarvis
source checkout, but V0.2 is SHADOW-HANDSHAKE ONLY.

It may:
- verify source identity,
- launch a bounded Python subprocess,
- import OpenJarvis,
- discover selected runtime modules,
- return evidence.

It may NOT:
- invoke an agent,
- invoke a tool,
- start a scheduler,
- start a service,
- access OpenJarvis memory,
- mutate Obsidia,
- expand scope,
- grant authority.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Protocol


OPENJARVIS_IS_AUTHORITY = False
OPENJARVIS_MEMORY_IS_CANONICAL = False
ADAPTER_CAN_EXPAND_SCOPE = False
ADAPTER_CAN_DECIDE_KX = False
ADAPTER_CAN_WRITE_NATIVE_MEMORY = False

OPENJARVIS_AGENT_EXECUTION_ENABLED = False
OPENJARVIS_TOOL_EXECUTION_ENABLED = False
OPENJARVIS_SCHEDULER_ENABLED = False
OPENJARVIS_MEMORY_ENABLED = False

ADAPTER_MODE = "SHADOW_HANDSHAKE_ONLY"


class OpenJarvisRuntimeAdapter(Protocol):
    def execute(
        self,
        *,
        capability_id: str,
        payload: Mapping[str, Any],
    ) -> dict:
        ...


class NotConnectedAdapter:
    """Fail-closed adapter retained for V0 compatibility."""

    adapter_id = "OPENJARVIS_NOT_CONNECTED_V0"
    connected = False
    is_authority = False

    def execute(
        self,
        *,
        capability_id: str,
        payload: Mapping[str, Any],
    ) -> dict:
        return {
            "status": "ADAPTER_NOT_CONNECTED",
            "adapter_id": self.adapter_id,
            "capability_id": str(capability_id),
            "connected": False,
            "is_execution_authority": False,
            "is_kx_authority": False,
            "is_human_authority": False,
            "scope_expanded": False,
            "memory_written": False,
        }


def _git_head(repo: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=10,
            shell=False,
        )
    except Exception:
        return None

    if result.returncode != 0:
        return None

    value = (result.stdout or "").strip()
    return value if len(value) == 40 else None


def _git_dirty(repo: Path) -> bool | None:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=10,
            shell=False,
        )
    except Exception:
        return None

    if result.returncode != 0:
        return None

    return bool((result.stdout or "").strip())


class OpenJarvisShadowAdapter:
    """Read-only runtime identity/capability handshake.

    No OpenJarvis agent or tool is executed in this V0.2 adapter.
    """

    adapter_id = "OPENJARVIS_SHADOW_ADAPTER_V02"
    connected = True
    is_authority = False

    def __init__(
        self,
        *,
        source_root: str,
        expected_commit: str,
        python_executable: str | None = None,
    ) -> None:

        self.source_root = Path(source_root).resolve(strict=False)
        self.expected_commit = str(expected_commit)
        self.python_executable = (
            str(python_executable)
            if python_executable
            else sys.executable
        )

    def execute(
        self,
        *,
        capability_id: str,
        payload: Mapping[str, Any],
    ) -> dict:

        if capability_id != "OPENJARVIS_RUNTIME_HANDSHAKE":
            return {
                "status": "CAPABILITY_NOT_ALLOWED",
                "adapter_id": self.adapter_id,
                "capability_id": str(capability_id),
                "is_execution_authority": False,
                "is_kx_authority": False,
                "scope_expanded": False,
                "memory_written": False,
            }

        if payload:
            return {
                "status": "PAYLOAD_NOT_ALLOWED_IN_HANDSHAKE",
                "adapter_id": self.adapter_id,
                "is_execution_authority": False,
                "is_kx_authority": False,
                "scope_expanded": False,
                "memory_written": False,
            }

        if not self.source_root.is_dir():
            return {
                "status": "OPENJARVIS_SOURCE_NOT_FOUND",
                "adapter_id": self.adapter_id,
                "source_root": str(self.source_root),
                "is_execution_authority": False,
            }

        actual_commit = _git_head(self.source_root)

        if actual_commit != self.expected_commit:
            return {
                "status": "OPENJARVIS_SOURCE_IDENTITY_MISMATCH",
                "adapter_id": self.adapter_id,
                "expected_commit": self.expected_commit,
                "actual_commit": actual_commit,
                "is_execution_authority": False,
            }

        dirty = _git_dirty(self.source_root)

        if dirty is None:
            return {
                "status": "OPENJARVIS_SOURCE_STATUS_UNAVAILABLE",
                "adapter_id": self.adapter_id,
                "is_execution_authority": False,
            }

        if dirty:
            return {
                "status": "OPENJARVIS_SOURCE_DIRTY",
                "adapter_id": self.adapter_id,
                "actual_commit": actual_commit,
                "is_execution_authority": False,
            }

        source_package = self.source_root / "src"

        probe = r'''
import importlib.util
import json
import sys

import openjarvis

modules = {
    "openjarvis": "openjarvis",
    "agents": "openjarvis.agents",
    "agent_executor": "openjarvis.agents.executor",
    "agent_scheduler": "openjarvis.agents.scheduler",
    "operative_agent": "openjarvis.agents.operative",
    "monitor_operative_agent": "openjarvis.agents.monitor_operative",
    "tools": "openjarvis.tools",
    "mcp": "openjarvis.mcp",
    "server": "openjarvis.server",
    "learning": "openjarvis.learning",
}

availability = {
    key: (importlib.util.find_spec(module_name) is not None)
    for key, module_name in modules.items()
}

print(json.dumps({
    "python": sys.executable,
    "openjarvis_version": getattr(openjarvis, "__version__", None),
    "module_availability": availability,
}, sort_keys=True))
'''

        env = os.environ.copy()

        existing = env.get("PYTHONPATH", "")

        env["PYTHONPATH"] = (
            str(source_package)
            if not existing
            else str(source_package) + os.pathsep + existing
        )

        try:
            result = subprocess.run(
                [
                    self.python_executable,
                    "-c",
                    probe,
                ],
                cwd=str(self.source_root),
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
                shell=False,
            )
        except Exception as exc:
            return {
                "status": "OPENJARVIS_PROBE_ERROR",
                "adapter_id": self.adapter_id,
                "error_type": type(exc).__name__,
                "is_execution_authority": False,
            }

        if result.returncode != 0:
            return {
                "status": "OPENJARVIS_PROBE_FAILED",
                "adapter_id": self.adapter_id,
                "exit_code": result.returncode,
                "stderr": (result.stderr or "")[-2000:],
                "is_execution_authority": False,
            }

        try:
            evidence = json.loads(
                (result.stdout or "").strip()
            )
        except json.JSONDecodeError:
            return {
                "status": "OPENJARVIS_PROBE_INVALID_JSON",
                "adapter_id": self.adapter_id,
                "stdout": (result.stdout or "")[-2000:],
                "is_execution_authority": False,
            }

        availability = (
            evidence.get("module_availability")
            if isinstance(evidence, dict)
            else {}
        ) or {}

        required = (
            "openjarvis",
            "agents",
            "agent_executor",
            "agent_scheduler",
            "tools",
            "mcp",
        )

        missing = [
            key
            for key in required
            if not availability.get(key)
        ]

        status = (
            "OPENJARVIS_SHADOW_HANDSHAKE_OK"
            if not missing
            else "OPENJARVIS_SHADOW_HANDSHAKE_INCOMPLETE"
        )

        return {
            "status": status,
            "adapter_id": self.adapter_id,

            "source_root": str(self.source_root),
            "expected_commit": self.expected_commit,
            "actual_commit": actual_commit,
            "source_dirty": False,

            "probe_evidence": evidence,
            "missing_required_surfaces": missing,

            "agent_execution_enabled": False,
            "tool_execution_enabled": False,
            "scheduler_enabled": False,
            "memory_enabled": False,

            "is_execution_authority": False,
            "is_kx_authority": False,
            "is_human_authority": False,

            "scope_expanded": False,
            "memory_written": False,
        }