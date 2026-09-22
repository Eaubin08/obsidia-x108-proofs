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

# ======================================================================
# JARVIS ADVANCED V0.5
# REAL OPENJARVIS ORCHESTRATOR -> ONE OBSIDIA SELF-BUILD TOOL
# ======================================================================

class OpenJarvisObsidiaSelfBuildPilotAdapter:
    """
    Real OpenJarvis OrchestratorAgent integration.

    OpenJarvis is the persistent operational pilot only.

    It receives exactly ONE executable tool:
        obsidia_self_build_phase1

    That tool does NOT write the repository directly.
    It calls the canonical Obsidia Relay:

        OpenJarvis
          -> obsidia_self_build_phase1
          -> Obsidia Relay
          -> Brody
          -> Obsidure
          -> candidate.patch
          -> PLAN_PROPOSED
          -> STOP

    No real model in this bootstrap.
    No OpenJarvis memory.
    No scheduler.
    No shell.
    No file_write.
    No git_commit.
    No Phase2.
    """

    adapter_id = (
        "OPENJARVIS_OBSIDIA_SELF_BUILD_PILOT_ADAPTER_V0"
    )

    capability_id = (
        "OPENJARVIS_OBSIDIA_SELF_BUILD_PILOT_SHADOW"
    )

    def __init__(
        self,
        *,
        source_root: str,
        expected_commit: str,
    ):
        self.source_root = Path(
            source_root
        ).resolve(strict=False)

        self.expected_commit = str(
            expected_commit
        ).strip().lower()

    @staticmethod
    def _git(
        repo: Path,
        *args: str,
    ):
        import subprocess

        proc = subprocess.run(
            ["git", *args],
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=20,
        )

        return (
            proc.returncode,
            proc.stdout or "",
        )

    def _source_state(self):
        rc_h, head = self._git(
            self.source_root,
            "rev-parse",
            "HEAD",
        )

        rc_s, status = self._git(
            self.source_root,
            "status",
            "--porcelain=v1",
        )

        return {
            "ok": (
                rc_h == 0
                and rc_s == 0
            ),
            "head": head.strip(),
            "status": status,
        }

    def execute(
        self,
        *,
        capability_id: str,
        payload: dict,
    ) -> dict:

        import hashlib
        import json
        import os
        import sys

        allowed_keys = {
            "objective",
            "target_path",
            "obsidia_repo_root",
        }

        if capability_id != self.capability_id:
            return {
                "status": "CAPABILITY_NOT_ALLOWED",
                "is_execution_authority": False,
                "is_kx_authority": False,
                "scope_expanded": False,
            }

        if not isinstance(payload, dict):
            return {
                "status": "PAYLOAD_INVALID",
                "is_execution_authority": False,
                "is_kx_authority": False,
                "scope_expanded": False,
            }

        if set(payload) - allowed_keys:
            return {
                "status": "PAYLOAD_SCOPE_NOT_ALLOWED",
                "is_execution_authority": False,
                "is_kx_authority": False,
                "scope_expanded": False,
            }

        objective = str(
            payload.get("objective")
            or ""
        ).strip()

        target_path = str(
            payload.get("target_path")
            or ""
        ).strip()

        obsidia_repo_root = Path(
            payload.get("obsidia_repo_root")
            or ""
        ).resolve(strict=False)

        if not objective:
            return {
                "status": "OBJECTIVE_REQUIRED",
                "is_execution_authority": False,
                "is_kx_authority": False,
                "scope_expanded": False,
            }

        if not target_path:
            return {
                "status": "TARGET_REQUIRED",
                "is_execution_authority": False,
                "is_kx_authority": False,
                "scope_expanded": False,
            }

        if not obsidia_repo_root.is_dir():
            return {
                "status": "OBSIDIA_REPO_REQUIRED",
                "is_execution_authority": False,
                "is_kx_authority": False,
                "scope_expanded": False,
            }

        before = self._source_state()

        if not before["ok"]:
            return {
                "status": "OPENJARVIS_SOURCE_GIT_STATE_UNAVAILABLE",
                "is_execution_authority": False,
                "is_kx_authority": False,
                "scope_expanded": False,
            }

        if (
            before["head"]
            != self.expected_commit
        ):
            return {
                "status": "OPENJARVIS_SOURCE_IDENTITY_MISMATCH",
                "actual_commit": before["head"],
                "expected_commit": self.expected_commit,
                "is_execution_authority": False,
                "is_kx_authority": False,
                "scope_expanded": False,
            }

        if before["status"]:
            return {
                "status": "OPENJARVIS_SOURCE_DIRTY",
                "is_execution_authority": False,
                "is_kx_authority": False,
                "scope_expanded": False,
            }

        package_root = (
            self.source_root
            / "src"
        )

        package_root_text = str(
            package_root
        )

        if (
            package_root_text
            not in sys.path
        ):
            sys.path.insert(
                0,
                package_root_text,
            )

        from openjarvis.agents.orchestrator import (
            OrchestratorAgent,
        )

        from openjarvis.core.types import (
            ToolResult,
        )

        from openjarvis.tools._stubs import (
            BaseTool,
            ToolSpec,
        )

        # ----------------------------------------------------------
        # The ONLY OpenJarvis tool.
        # Repository path / target / objective are bound by Obsidia,
        # not selected through arbitrary tool parameters.
        # ----------------------------------------------------------

        bound_objective = objective
        bound_target = target_path
        bound_repo = obsidia_repo_root

        local_app = str(
            os.environ.get(
                "LOCALAPPDATA",
                "",
            )
            or ""
        ).strip()

        state_base = (
            Path(local_app)
            if local_app
            else Path.home()
        )

        digest = hashlib.sha256(
            (
                str(bound_repo)
                + "\n"
                + bound_target
                + "\n"
                + bound_objective
            ).encode("utf-8")
        ).hexdigest()[:20]

        nested_store = (
            state_base
            / "Obsidia"
            / "openjarvis_selfbuild_relay"
            / digest
        )

        class ObsidiaSelfBuildPhase1Tool(
            BaseTool
        ):
            tool_id = (
                "obsidia_self_build_phase1"
            )

            @property
            def spec(self):
                return ToolSpec(
                    name=(
                        "obsidia_self_build_phase1"
                    ),
                    description=(
                        "Ask canonical Obsidia to prepare "
                        "one bounded Brody->Obsidure "
                        "self-build candidate. "
                        "Phase1 only; no apply."
                    ),
                    parameters={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                    },
                    category="obsidia-governed",
                    requires_confirmation=False,
                    timeout_seconds=180.0,
                    required_capabilities=[],
                    metadata={
                        "authority": "NONE",
                        "phase2": False,
                        "direct_repo_write": False,
                    },
                )

            def execute(
                self,
                **params,
            ):
                if params:
                    return ToolResult(
                        tool_name=self.tool_id,
                        content=(
                            "OBSIDIA_TOOL_PARAMETER_SCOPE_DENIED"
                        ),
                        success=False,
                    )

                # Late import avoids turning OpenJarvis into
                # the canonical runtime owner.
                import obsidia_relay_v0 as RELAY

                nested = (
                    RELAY.relay_submit_mission(
                        requested_outcome=(
                            bound_objective
                        ),
                        mission_kind=(
                            RELAY
                            .KIND_OBSIDIA_NATIVE_SELF_BUILD_PHASE1
                        ),
                        target=bound_target,
                        repo_root=bound_repo,
                        store_dir=nested_store,
                    )
                )

                ev = dict(
                    nested.get(
                        "native_evidence"
                    )
                    or {}
                )

                # Never expose any human approval material.
                summary = {
                    "status": (
                        nested.get(
                            "mission_state"
                        )
                    ),
                    "relay_mission_id": (
                        nested.get(
                            "relay_mission_id"
                        )
                    ),
                    "ok": ev.get("ok"),
                    "phase1_status": (
                        ev.get(
                            "phase1_status"
                        )
                    ),
                    "target_path": (
                        ev.get(
                            "target_path"
                        )
                    ),
                    "candidate_patch_hash": (
                        ev.get(
                            "candidate_patch_hash"
                        )
                    ),
                    "plan_summary": (
                        ev.get(
                            "plan_summary"
                        )
                    ),
                    "phase2_executed": False,
                    "repo_mutation": (
                        ev.get(
                            "repo_mutation"
                        )
                    ),
                    "authority": "NONE",
                    "decision_authority": (
                        ev.get(
                            "decision_authority"
                        )
                    ),
                }

                encoded = json.dumps(
                    summary,
                    sort_keys=True,
                )

                if (
                    ("HUMAN_APPROVED_" + "BUILD_SESSION=")
                    in encoded
                ):
                    return ToolResult(
                        tool_name=self.tool_id,
                        content=(
                            "OBSIDIA_HUMAN_TOKEN_LEAK_BLOCKED"
                        ),
                        success=False,
                    )

                ok = (
                    nested.get(
                        "mission_state"
                    )
                    == "MISSION_COMPLETE"
                    and ev.get(
                        "ok"
                    )
                    is True
                    and ev.get(
                        "phase2_executed"
                    )
                    is False
                    and ev.get(
                        "repo_mutation"
                    )
                    is False
                )

                return ToolResult(
                    tool_name=self.tool_id,
                    content=encoded,
                    success=ok,
                    metadata={
                        "relay_mission_id": (
                            nested.get(
                                "relay_mission_id"
                            )
                        ),
                        "authority": "NONE",
                        "phase2": False,
                    },
                )

        # ----------------------------------------------------------
        # Deterministic engine:
        # turn 1 -> call exactly the single Obsidia tool.
        # turn 2 -> return final result.
        #
        # This proves real OpenJarvis tool-calling code without
        # introducing model variance yet.
        # ----------------------------------------------------------

        class ObsidiaPilotEngine:
            engine_id = (
                "obsidia-openjarvis-pilot-engine-v0"
            )

            _publishes_events = False

            def __init__(self):
                self.calls = 0

            def generate(
                self,
                messages,
                *,
                model,
                temperature,
                max_tokens,
                **kwargs,
            ):
                self.calls += 1

                if self.calls == 1:
                    tools = (
                        kwargs.get("tools")
                        or []
                    )

                    tool_names = []

                    for item in tools:
                        try:
                            tool_names.append(
                                item["function"]["name"]
                            )
                        except Exception:
                            pass

                    if tool_names != [
                        "obsidia_self_build_phase1"
                    ]:
                        return {
                            "content": (
                                "PILOT_TOOL_SURFACE_MISMATCH"
                            ),
                            "tool_calls": [],
                            "usage": {},
                        }

                    return {
                        "content": "",
                        "tool_calls": [
                            {
                                "id": (
                                    "call-obsidia-selfbuild"
                                ),
                                "name": (
                                    "obsidia_self_build_phase1"
                                ),
                                "arguments": "{}",
                            }
                        ],
                        "usage": {},
                    }

                return {
                    "content": (
                        "OBSIDIA_SELF_BUILD_PHASE1_RETURNED"
                    ),
                    "tool_calls": [],
                    "usage": {},
                }

        engine = ObsidiaPilotEngine()

        tool = ObsidiaSelfBuildPhase1Tool()

        agent = OrchestratorAgent(
            engine=engine,
            model=(
                "obsidia-deterministic-pilot-v0"
            ),
            tools=[tool],
            max_turns=3,
            temperature=0.0,
            parallel_tools=False,
            system_prompt=(
                "You are an OpenJarvis pilot surface. "
                "You have exactly one non-sovereign "
                "Obsidia tool."
            ),
        )

        result = agent.run(
            (
                "Prepare the bounded Obsidia "
                "self-build Phase1 mission."
            )
        )

        after = self._source_state()

        source_mutated = (
            not after["ok"]
            or before["head"]
            != after["head"]
            or before["status"]
            != after["status"]
        )

        tool_results = list(
            result.tool_results
            or []
        )

        one_tool = (
            tool_results[0]
            if len(tool_results) == 1
            else None
        )

        ok = (
            result.content
            == "OBSIDIA_SELF_BUILD_PHASE1_RETURNED"
            and engine.calls == 2
            and result.turns == 2
            and len(tool_results) == 1
            and one_tool is not None
            and one_tool.tool_name
            == "obsidia_self_build_phase1"
            and one_tool.success is True
            and not source_mutated
        )

        nested_relay_id = None

        if one_tool is not None:
            nested_relay_id = (
                one_tool.metadata.get(
                    "relay_mission_id"
                )
            )

        return {
            "status": (
                "OPENJARVIS_OBSIDIA_SELF_BUILD_PILOT_OK"
                if ok
                else "OPENJARVIS_OBSIDIA_SELF_BUILD_PILOT_FAILED"
            ),

            "adapter_id": self.adapter_id,

            "agent_class": "OrchestratorAgent",
            "agent_id": "orchestrator",

            "engine": engine.engine_id,
            "engine_calls": engine.calls,

            "turns": result.turns,
            "tool_results": len(
                tool_results
            ),

            "tool_name": (
                one_tool.tool_name
                if one_tool is not None
                else None
            ),

            "tool_success": (
                one_tool.success
                if one_tool is not None
                else False
            ),

            "nested_relay_mission_id": (
                nested_relay_id
            ),

            "real_openjarvis_agent_code": True,
            "real_openjarvis_tool_executor": True,

            "real_model_enabled": False,

            "agent_execution_enabled": True,
            "tool_execution_enabled": True,

            "available_tool_count": 1,
            "available_tools": [
                "obsidia_self_build_phase1"
            ],

            "shell_tool_enabled": False,
            "file_write_tool_enabled": False,
            "git_commit_tool_enabled": False,

            "memory_enabled": False,
            "scheduler_enabled": False,
            "network_enabled": False,

            "is_execution_authority": False,
            "is_kx_authority": False,
            "is_human_authority": False,

            "external_runtime_authority": "NONE",

            "scope_expanded": False,
            "memory_written": False,

            "source_mutated": (
                source_mutated
            ),

            "expected_commit": (
                self.expected_commit
            ),

            "actual_commit": (
                after.get("head")
            ),

            "final_content": (
                result.content
            ),
        }


# ======================================================================
# JARVIS ADVANCED V0.6
# DISTINCT OPENJARVIS -> OBSIDIA COGNITIVE PILOT
#
# OpenJarvis is a pilot surface only.
#
# Exactly one tool is visible:
#     obsidia_cognitive_query
#
# The query text is bound outside the tool call.
# The tool accepts ZERO parameters.
#
# OpenJarvis cannot choose:
# - model activation,
# - model/provider,
# - Brody routing,
# - KX108 verdict,
# - execution authority,
# - memory writes,
# - action.
#
# Canonical cognitive path:
#
#     OpenJarvis
#       -> obsidia_cognitive_query
#       -> run_cognitive_ingress
#       -> OS Trad
#       -> AMD Router
#       -> Brody
#       -> sufficiency gate
#       -> optional Qwen local evidence
#       -> W1
#       -> W2 / KX108
#
# Self-build pilot V0.5 remains separate.
# ======================================================================


class OpenJarvisObsidiaCognitivePilotAdapter:
    """Non-sovereign OpenJarvis pilot for canonical Obsidia cognition."""

    adapter_id = (
        "OPENJARVIS_OBSIDIA_COGNITIVE_PILOT_ADAPTER_V0"
    )

    capability_id = (
        "OPENJARVIS_OBSIDIA_COGNITIVE_PILOT"
    )

    connected = True
    is_authority = False

    def __init__(
        self,
        *,
        source_root: str,
        expected_commit: str,
    ) -> None:

        self.source_root = Path(
            source_root
        ).resolve(strict=False)

        self.expected_commit = str(
            expected_commit
        ).strip().lower()

    def execute(
        self,
        *,
        capability_id: str,
        payload: Mapping[str, Any],
    ) -> dict:

        import hashlib
        import json

        # ----------------------------------------------------------
        # Capability boundary.
        # ----------------------------------------------------------

        if capability_id != self.capability_id:
            return {
                "status": "CAPABILITY_NOT_ALLOWED",
                "adapter_id": self.adapter_id,
                "is_execution_authority": False,
                "is_kx_authority": False,
                "scope_expanded": False,
            }

        if not isinstance(
            payload,
            Mapping,
        ):
            return {
                "status": "PAYLOAD_INVALID",
                "adapter_id": self.adapter_id,
                "is_execution_authority": False,
                "is_kx_authority": False,
                "scope_expanded": False,
            }

        # OpenJarvis may provide ONLY the user text.
        # It cannot request a model/provider/policy.
        allowed = {
            "input_text",
        }

        unknown = (
            set(payload.keys())
            - allowed
        )

        if unknown:
            return {
                "status": "PAYLOAD_SCOPE_NOT_ALLOWED",
                "adapter_id": self.adapter_id,
                "unknown_fields": sorted(
                    str(item)
                    for item in unknown
                ),
                "is_execution_authority": False,
                "is_kx_authority": False,
                "scope_expanded": False,
            }

        input_text = payload.get(
            "input_text"
        )

        if not isinstance(
            input_text,
            str,
        ):
            return {
                "status": "INPUT_TEXT_REQUIRED",
                "adapter_id": self.adapter_id,
                "is_execution_authority": False,
                "is_kx_authority": False,
                "scope_expanded": False,
            }

        bound_text = input_text.strip()

        if not bound_text:
            return {
                "status": "INPUT_TEXT_REQUIRED",
                "adapter_id": self.adapter_id,
                "is_execution_authority": False,
                "is_kx_authority": False,
                "scope_expanded": False,
            }

        if len(bound_text) > 50000:
            return {
                "status": "INPUT_TEXT_TOO_LONG",
                "adapter_id": self.adapter_id,
                "max_chars": 50000,
                "is_execution_authority": False,
                "is_kx_authority": False,
                "scope_expanded": False,
            }

        # ----------------------------------------------------------
        # Pinned OpenJarvis source identity.
        # ----------------------------------------------------------

        if not self.source_root.is_dir():
            return {
                "status": "OPENJARVIS_SOURCE_NOT_FOUND",
                "adapter_id": self.adapter_id,
                "is_execution_authority": False,
                "is_kx_authority": False,
                "scope_expanded": False,
            }

        before_head = _git_head(
            self.source_root
        )

        before_dirty = _git_dirty(
            self.source_root
        )

        if (
            before_head
            != self.expected_commit
        ):
            return {
                "status": (
                    "OPENJARVIS_SOURCE_IDENTITY_MISMATCH"
                ),
                "adapter_id": self.adapter_id,
                "expected_commit": self.expected_commit,
                "actual_commit": before_head,
                "is_execution_authority": False,
                "is_kx_authority": False,
                "scope_expanded": False,
            }

        if before_dirty is None:
            return {
                "status": (
                    "OPENJARVIS_SOURCE_STATUS_UNAVAILABLE"
                ),
                "adapter_id": self.adapter_id,
                "is_execution_authority": False,
                "is_kx_authority": False,
                "scope_expanded": False,
            }

        if before_dirty:
            return {
                "status": "OPENJARVIS_SOURCE_DIRTY",
                "adapter_id": self.adapter_id,
                "is_execution_authority": False,
                "is_kx_authority": False,
                "scope_expanded": False,
            }

        package_root = (
            self.source_root
            / "src"
        )

        package_root_text = str(
            package_root
        )

        if (
            package_root_text
            not in sys.path
        ):
            sys.path.insert(
                0,
                package_root_text,
            )

        # Exact same OpenJarvis API proven by V0.5.
        from openjarvis.agents.orchestrator import (
            OrchestratorAgent,
        )

        from openjarvis.core.types import (
            ToolResult,
        )

        from openjarvis.tools._stubs import (
            BaseTool,
            ToolSpec,
        )

        # ----------------------------------------------------------
        # Obsidia binds the session deterministically.
        #
        # OpenJarvis cannot select or alter it.
        # ----------------------------------------------------------

        digest = hashlib.sha256(
            (
                self.expected_commit
                + "\n"
                + bound_text
            ).encode("utf-8")
        ).hexdigest()[:24]

        bound_session_id = (
            "ojc-"
            + digest
        )

        # ----------------------------------------------------------
        # The ONLY OpenJarvis tool.
        #
        # ZERO tool parameters:
        # the input is already bound by Obsidia.
        # ----------------------------------------------------------

        class ObsidiaCognitiveQueryTool(
            BaseTool
        ):
            tool_id = (
                "obsidia_cognitive_query"
            )

            @property
            def spec(self):
                return ToolSpec(
                    name=self.tool_id,
                    description=(
                        "Submit the already-bound user text "
                        "to canonical Obsidia cognition. "
                        "OpenJarvis cannot choose models, "
                        "providers, authority or actions."
                    ),
                    parameters={
                        "type": "object",
                        "properties": {},
                        "required": [],
                        "additionalProperties": False,
                    },
                    category="obsidia-governed",
                    timeout_seconds=120.0,
                    required_capabilities=[],
                    metadata={
                        "authority": "NONE",
                        "decision_authority": (
                            "KX108_ONLY"
                        ),
                        "input_bound": True,
                        "tool_parameters": 0,
                    },
                )

            def execute(
                self,
                **params,
            ):

                if params:
                    return ToolResult(
                        tool_name=self.tool_id,
                        content=(
                            "OBSIDIA_COGNITIVE_TOOL_"
                            "PARAMETER_SCOPE_DENIED"
                        ),
                        success=False,
                    )

                # Late import:
                # OpenJarvis never becomes the owner
                # of Obsidia cognition.
                from scripts.obsidia_cognitive_ingress_v0 import (
                    run_cognitive_ingress,
                )

                result = run_cognitive_ingress(
                    text=bound_text,
                    session_id=(
                        bound_session_id
                    ),

                    # Policy is bound INSIDE Obsidia integration.
                    # OpenJarvis cannot set this field.
                    allow_local_model=True,
                )

                if not isinstance(
                    result,
                    dict,
                ):
                    return ToolResult(
                        tool_name=self.tool_id,
                        content=(
                            "OBSIDIA_COGNITIVE_RESULT_INVALID"
                        ),
                        success=False,
                    )

                local_model = dict(
                    result.get(
                        "local_model_stage"
                    )
                    or {}
                )

                receipt = dict(
                    result.get(
                        "route_receipt"
                    )
                    or {}
                )

                summary = {
                    "session_id": (
                        bound_session_id
                    ),

                    "next_stage": (
                        result.get(
                            "next_stage"
                        )
                    ),

                    "kx108_admission": (
                        result.get(
                            "kx108_admission"
                        )
                    ),

                    "model_attempted": bool(
                        local_model.get(
                            "attempted"
                        )
                    ),

                    "model_call_used": bool(
                        local_model.get(
                            "model_call_used"
                        )
                    ),

                    "model_status": (
                        local_model.get(
                            "status"
                        )
                    ),

                    "finish_reason": (
                        local_model.get(
                            "finish_reason"
                        )
                    ),

                    "evidence_applied": bool(
                        local_model.get(
                            "evidence_applied"
                        )
                    ),

                    "receipt_status": (
                        receipt.get(
                            "result_status"
                        )
                    ),

                    "real_execution": bool(
                        result.get(
                            "real_execution"
                        )
                    ),

                    "authority": "NONE",
                    "decision_authority": (
                        "KX108_ONLY"
                    ),
                }

                encoded = json.dumps(
                    summary,
                    ensure_ascii=False,
                    sort_keys=True,
                )

                return ToolResult(
                    tool_name=self.tool_id,
                    content=encoded,
                    success=True,
                    metadata={
                        "session_id": (
                            bound_session_id
                        ),
                        "cognitive_result": result,
                        "cognitive_summary": summary,
                        "authority": "NONE",
                        "decision_authority": (
                            "KX108_ONLY"
                        ),
                    },
                )

        # ----------------------------------------------------------
        # Deterministic OpenJarvis pilot engine.
        #
        # It cannot reason about tool choice because there is
        # exactly ONE visible tool.
        # ----------------------------------------------------------

        class ObsidiaCognitivePilotEngine:
            engine_id = (
                "obsidia-openjarvis-cognitive-pilot-engine-v0"
            )

            _publishes_events = False

            def __init__(self):
                self.calls = 0

            def generate(
                self,
                messages,
                *,
                model,
                temperature,
                max_tokens,
                **kwargs,
            ):
                self.calls += 1

                if self.calls == 1:
                    tools = (
                        kwargs.get("tools")
                        or []
                    )

                    tool_names = []

                    for item in tools:
                        try:
                            tool_names.append(
                                item[
                                    "function"
                                ][
                                    "name"
                                ]
                            )
                        except Exception:
                            pass

                    if tool_names != [
                        "obsidia_cognitive_query"
                    ]:
                        return {
                            "content": (
                                "COGNITIVE_PILOT_"
                                "TOOL_SURFACE_MISMATCH"
                            ),
                            "tool_calls": [],
                            "usage": {},
                        }

                    return {
                        "content": "",
                        "tool_calls": [
                            {
                                "id": (
                                    "call-obsidia-cognitive"
                                ),
                                "name": (
                                    "obsidia_cognitive_query"
                                ),
                                "arguments": "{}",
                            }
                        ],
                        "usage": {},
                    }

                return {
                    "content": (
                        "OBSIDIA_COGNITIVE_QUERY_RETURNED"
                    ),
                    "tool_calls": [],
                    "usage": {},
                }

        engine = (
            ObsidiaCognitivePilotEngine()
        )

        tool = (
            ObsidiaCognitiveQueryTool()
        )

        agent = OrchestratorAgent(
            engine=engine,
            model=(
                "obsidia-deterministic-"
                "cognitive-pilot-v0"
            ),
            tools=[tool],
            max_turns=3,
            temperature=0.0,
            parallel_tools=False,
            system_prompt=(
                "You are an OpenJarvis pilot surface. "
                "You have exactly one non-sovereign "
                "Obsidia cognitive tool. "
                "Do not select models, providers, "
                "actions or authority."
            ),
        )

        result = agent.run(
            "Submit the bound request to canonical "
            "Obsidia cognition."
        )

        # ----------------------------------------------------------
        # Source non-mutation proof.
        # ----------------------------------------------------------

        after_head = _git_head(
            self.source_root
        )

        after_dirty = _git_dirty(
            self.source_root
        )

        source_mutated = (
            after_head != before_head
            or after_dirty is None
            or after_dirty is True
        )

        tool_results = list(
            result.tool_results
            or []
        )

        one_tool = (
            tool_results[0]
            if len(tool_results) == 1
            else None
        )

        cognitive_result = None
        cognitive_summary = None

        if one_tool is not None:
            cognitive_result = (
                one_tool.metadata.get(
                    "cognitive_result"
                )
            )

            cognitive_summary = (
                one_tool.metadata.get(
                    "cognitive_summary"
                )
            )

        ok = (
            result.content
            == "OBSIDIA_COGNITIVE_QUERY_RETURNED"
            and engine.calls == 2
            and result.turns == 2
            and len(tool_results) == 1
            and one_tool is not None
            and one_tool.tool_name
            == "obsidia_cognitive_query"
            and one_tool.success is True
            and isinstance(
                cognitive_result,
                dict,
            )
            and not source_mutated
        )

        return {
            "status": (
                "OPENJARVIS_OBSIDIA_COGNITIVE_PILOT_OK"
                if ok
                else (
                    "OPENJARVIS_OBSIDIA_"
                    "COGNITIVE_PILOT_FAILED"
                )
            ),

            "adapter_id": self.adapter_id,

            "agent_class": (
                "OrchestratorAgent"
            ),

            "agent_id": "orchestrator",

            "engine": (
                engine.engine_id
            ),

            "engine_calls": (
                engine.calls
            ),

            "turns": (
                result.turns
            ),

            "tool_results": len(
                tool_results
            ),

            "tool_name": (
                one_tool.tool_name
                if one_tool is not None
                else None
            ),

            "tool_success": (
                one_tool.success
                if one_tool is not None
                else False
            ),

            "available_tool_count": 1,

            "available_tools": [
                "obsidia_cognitive_query"
            ],

            # OpenJarvis itself has no model.
            "openjarvis_real_model_enabled": False,

            # Obsidia alone may conditionally activate
            # its governed local model.
            "obsidia_model_policy_enabled": True,

            "bound_session_id": (
                bound_session_id
            ),

            "cognitive_summary": (
                cognitive_summary
            ),

            "cognitive_result": (
                cognitive_result
            ),

            "shell_tool_enabled": False,
            "file_write_tool_enabled": False,
            "git_commit_tool_enabled": False,

            "memory_enabled": False,
            "scheduler_enabled": False,

            "external_runtime_authority": "NONE",

            "is_execution_authority": False,
            "is_kx_authority": False,

            "memory_written": False,
            "scope_expanded": False,

            "source_mutated": (
                source_mutated
            ),

            "decision_authority": (
                "KX108_ONLY"
            ),
        }
