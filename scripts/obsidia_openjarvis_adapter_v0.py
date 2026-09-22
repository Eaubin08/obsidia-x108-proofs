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

        # READ_ONLY means the probe must not even materialize Python bytecode
        # inside the external OpenJarvis checkout.
        env["PYTHONDONTWRITEBYTECODE"] = "1"

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


class OpenJarvisSimpleAgentShadowAdapter:
    """Execute the real OpenJarvis SimpleAgent with a deterministic engine.

    V0.4 intentionally provides:
      - no real LLM,
      - no network,
      - no tools,
      - no memory,
      - no scheduler,
      - no authority,
      - no external effect.

    The purpose is to prove the real OpenJarvis agent execution path before
    any probabilistic model or effectful capability is introduced.
    """

    adapter_id = "OPENJARVIS_SIMPLE_AGENT_SHADOW_ADAPTER_V04"

    connected = True
    is_authority = False

    def __init__(
        self,
        *,
        source_root: str,
        expected_commit: str,
        python_executable: str | None = None,
    ) -> None:

        self.source_root = Path(
            source_root
        ).resolve(strict=False)

        self.expected_commit = str(
            expected_commit
        ).strip().lower()

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

        if capability_id != "OPENJARVIS_SIMPLE_AGENT_SHADOW":
            return {
                "status": "CAPABILITY_NOT_ALLOWED",
                "adapter_id": self.adapter_id,
                "is_execution_authority": False,
                "is_kx_authority": False,
                "scope_expanded": False,
                "memory_written": False,
            }

        if not isinstance(payload, Mapping):
            return {
                "status": "INVALID_PAYLOAD",
                "adapter_id": self.adapter_id,
                "is_execution_authority": False,
            }

        allowed = {"input_text"}

        unknown = set(payload.keys()) - allowed

        if unknown:
            return {
                "status": "PAYLOAD_SCOPE_NOT_ALLOWED",
                "adapter_id": self.adapter_id,
                "unknown_fields": sorted(unknown),
                "is_execution_authority": False,
                "scope_expanded": False,
            }

        input_text = payload.get("input_text")

        if not isinstance(input_text, str):
            return {
                "status": "INPUT_TEXT_REQUIRED",
                "adapter_id": self.adapter_id,
                "is_execution_authority": False,
            }

        input_text = input_text.strip()

        if not input_text:
            return {
                "status": "INPUT_TEXT_REQUIRED",
                "adapter_id": self.adapter_id,
                "is_execution_authority": False,
            }

        if len(input_text) > 2000:
            return {
                "status": "INPUT_TEXT_TOO_LONG",
                "adapter_id": self.adapter_id,
                "max_chars": 2000,
                "is_execution_authority": False,
            }

        if not self.source_root.is_dir():
            return {
                "status": "OPENJARVIS_SOURCE_NOT_FOUND",
                "adapter_id": self.adapter_id,
                "is_execution_authority": False,
            }

        actual_commit = _git_head(
            self.source_root
        )

        if actual_commit != self.expected_commit:
            return {
                "status": "OPENJARVIS_SOURCE_IDENTITY_MISMATCH",
                "adapter_id": self.adapter_id,
                "expected_commit": self.expected_commit,
                "actual_commit": actual_commit,
                "is_execution_authority": False,
            }

        source_dirty = _git_dirty(
            self.source_root
        )

        if source_dirty is None:
            return {
                "status": "OPENJARVIS_SOURCE_STATUS_UNAVAILABLE",
                "adapter_id": self.adapter_id,
                "is_execution_authority": False,
            }

        if source_dirty:
            return {
                "status": "OPENJARVIS_SOURCE_DIRTY",
                "adapter_id": self.adapter_id,
                "actual_commit": actual_commit,
                "is_execution_authority": False,
            }

        source_package = self.source_root / "src"

        probe = r"""
import hashlib
import json
import sys

from openjarvis.agents.simple import SimpleAgent
from openjarvis.agents._stubs import AgentContext
from openjarvis.core.types import Conversation, Message, Role


request = json.loads(sys.stdin.read())

input_text = request["input_text"]


class ObsidiaShadowEngine:
    engine_id = "obsidia-shadow-engine-v0"
    is_cloud = False

    def __init__(self):
        self.calls = []

    def generate(
        self,
        messages,
        *,
        model,
        temperature=0.7,
        max_tokens=1024,
        **kwargs,
    ):
        self.calls.append({
            "roles": [m.role.value for m in messages],
            "texts": [m.text for m in messages],
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
        })

        return {
            "content":
                "OBSIDIA_OPENJARVIS_SIMPLE_AGENT_SHADOW_OK",

            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },

            "model": model,
            "finish_reason": "stop",
        }

    def list_models(self):
        return ["obsidia-shadow-model"]

    def health(self):
        return True


engine = ObsidiaShadowEngine()

conversation = Conversation()

conversation.add(
    Message(
        role=Role.SYSTEM,
        content=(
            "OBSIDIA SHADOW EXECUTION. "
            "NO TOOLS. NO MEMORY. "
            "NO NETWORK. NO EXTERNAL EFFECT."
        ),
    )
)

context = AgentContext(
    conversation=conversation,
    tools=[],
    memory_results=[],
    metadata={
        "authority": "NONE",
        "mode": "SHADOW",
    },
)

agent = SimpleAgent(
    engine,
    "obsidia-shadow-model",
    temperature=0.0,
    max_tokens=32,
)

result = agent.run(
    input_text,
    context=context,
)

assert result.turns == 1
assert result.tool_results == []

assert len(engine.calls) == 1

call = engine.calls[0]

assert call["model"] == "obsidia-shadow-model"
assert call["temperature"] == 0.0
assert call["max_tokens"] == 32

assert call["roles"] == [
    "system",
    "user",
]

assert call["texts"][-1] == input_text

print(
    json.dumps(
        {
            "status":
                "OPENJARVIS_SIMPLE_AGENT_SHADOW_OK",

            "agent_class":
                type(agent).__name__,

            "agent_id":
                agent.agent_id,

            "engine":
                engine.engine_id,

            "engine_calls":
                len(engine.calls),

            "turns":
                result.turns,

            "tool_results":
                len(result.tool_results),

            "content":
                result.content,

            "input_sha256":
                hashlib.sha256(
                    input_text.encode("utf-8")
                ).hexdigest(),

            "tools_enabled":
                False,

            "memory_enabled":
                False,

            "scheduler_enabled":
                False,

            "network_enabled":
                False,

            "external_effect":
                False,

            "authority":
                "NONE",
        },
        sort_keys=True,
    )
)
"""

        env = os.environ.copy()

        env["PYTHONDONTWRITEBYTECODE"] = "1"

        existing = env.get(
            "PYTHONPATH",
            "",
        )

        env["PYTHONPATH"] = (
            str(source_package)
            if not existing
            else str(source_package)
            + os.pathsep
            + existing
        )

        request = json.dumps(
            {
                "input_text": input_text,
            },
            sort_keys=True,
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
                input=request,
                capture_output=True,
                text=True,
                timeout=30,
                shell=False,
            )

        except Exception as exc:
            return {
                "status": "OPENJARVIS_SIMPLE_AGENT_PROBE_ERROR",
                "adapter_id": self.adapter_id,
                "error_type": type(exc).__name__,
                "is_execution_authority": False,
            }

        if result.returncode != 0:
            return {
                "status": "OPENJARVIS_SIMPLE_AGENT_PROBE_FAILED",
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
                "status": "OPENJARVIS_SIMPLE_AGENT_INVALID_JSON",
                "adapter_id": self.adapter_id,
                "stdout": (result.stdout or "")[-2000:],
                "is_execution_authority": False,
            }

        post_commit = _git_head(
            self.source_root
        )

        post_dirty = _git_dirty(
            self.source_root
        )

        source_mutated = (
            post_commit != actual_commit
            or post_dirty is not False
        )

        expected_status = (
            evidence.get("status")
            == "OPENJARVIS_SIMPLE_AGENT_SHADOW_OK"
        )

        expected_shape = (
            evidence.get("agent_class") == "SimpleAgent"
            and evidence.get("agent_id") == "simple"
            and evidence.get("engine")
                == "obsidia-shadow-engine-v0"
            and evidence.get("engine_calls") == 1
            and evidence.get("turns") == 1
            and evidence.get("tool_results") == 0
            and evidence.get("tools_enabled") is False
            and evidence.get("memory_enabled") is False
            and evidence.get("scheduler_enabled") is False
            and evidence.get("network_enabled") is False
            and evidence.get("external_effect") is False
            and evidence.get("authority") == "NONE"
        )

        ok = (
            expected_status
            and expected_shape
            and not source_mutated
        )

        return {
            "status": (
                "OPENJARVIS_SIMPLE_AGENT_SHADOW_OK"
                if ok
                else "OPENJARVIS_SIMPLE_AGENT_SHADOW_INVALID"
            ),

            "adapter_id": self.adapter_id,

            "source_root": str(self.source_root),

            "expected_commit": self.expected_commit,
            "actual_commit": actual_commit,

            "source_dirty": False,
            "source_mutated": source_mutated,

            "agent_class": evidence.get("agent_class"),
            "agent_id": evidence.get("agent_id"),

            "engine": evidence.get("engine"),
            "engine_calls": evidence.get("engine_calls"),

            "turns": evidence.get("turns"),
            "tool_results": evidence.get("tool_results"),

            "content": evidence.get("content"),
            "input_sha256": evidence.get("input_sha256"),

            "real_openjarvis_agent_code": True,
            "real_model_enabled": False,

            "agent_execution_enabled": True,
            "tool_execution_enabled": False,
            "memory_enabled": False,
            "scheduler_enabled": False,
            "network_enabled": False,

            "is_execution_authority": False,
            "is_kx_authority": False,
            "is_human_authority": False,

            "scope_expanded": False,
            "memory_written": False,
        }
