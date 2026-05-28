from __future__ import annotations

from typing import Any, Dict

from ..agents.orchestrator_readonly import run_readonly_swarm
from ..boundary import validate_readonly_output

ADAPTER_SPEC = {
    "adapter_id": "X108_READONLY_GATEWAY_ADAPTER_V4",
    "input": "raw SOP text",
    "output": "X108 readonly ingress envelope dict",
    "runtime_binding": False,
    "x108_merge": False,
    "kernel_binding": False,
}


def sop_to_x108_readonly_envelope(sop_text: str, title: str = "Untitled workflow") -> Dict[str, Any]:
    """Create a readonly X108 ingress envelope candidate from SOP text."""
    result = run_readonly_swarm(sop_text=sop_text, title=title)
    envelope = result["x108_readonly_ingress_envelope"]
    validate_readonly_output(envelope, allow_descriptive_tokens=True)
    envelope["adapter_spec"] = ADAPTER_SPEC
    return envelope
