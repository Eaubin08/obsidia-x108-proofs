from __future__ import annotations

from typing import Any, Dict

from ..agents.orchestrator_readonly import run_readonly_swarm
from ..boundary import validate_readonly_output

ADAPTER_SPEC = {
    "adapter_id": "WORKFLOW_CONTEXT_PACKET_ADAPTER_READONLY_V4",
    "input": "raw SOP text",
    "output": "Context packet dict",
    "runtime_binding": False,
    "kernel_binding": False,
}


def sop_to_context_packet(sop_text: str, title: str = "Untitled workflow") -> Dict[str, Any]:
    """Convert SOP text into a context packet candidate via full readonly swarm."""
    result = run_readonly_swarm(sop_text=sop_text, title=title)
    packet = result["context_packet"]
    validate_readonly_output(packet, allow_descriptive_tokens=True)
    packet["adapter_spec"] = ADAPTER_SPEC
    return packet
