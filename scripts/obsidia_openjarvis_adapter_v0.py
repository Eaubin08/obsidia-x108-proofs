#!/usr/bin/env python3
"""OpenJarvis peripheral runtime contract V0.

V0 intentionally provides no real OpenJarvis execution.
The adapter is a transport/execution boundary only and grants no authority.
"""

from __future__ import annotations

from typing import Any, Mapping, Protocol


OPENJARVIS_IS_AUTHORITY = False
OPENJARVIS_MEMORY_IS_CANONICAL = False
ADAPTER_CAN_EXPAND_SCOPE = False
ADAPTER_CAN_DECIDE_KX = False
ADAPTER_CAN_WRITE_NATIVE_MEMORY = False


class OpenJarvisRuntimeAdapter(Protocol):
    def execute(
        self,
        *,
        capability_id: str,
        payload: Mapping[str, Any],
    ) -> dict:
        ...


class NotConnectedAdapter:
    """Fail-closed placeholder used by Jarvis V0 READ_ONLY."""

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