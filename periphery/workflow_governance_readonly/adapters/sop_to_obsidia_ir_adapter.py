from __future__ import annotations

from typing import Any, Dict

from ..agents.orchestrator_readonly import run_readonly_swarm
from ..boundary import validate_readonly_output

ADAPTER_SPEC = {
    "adapter_id": "SOP_TO_OBSIDIA_IR_ADAPTER_READONLY_V4",
    "input": "raw SOP text",
    "output": "Obsidia IR candidate dict",
    "runtime_binding": False,
    "kernel_binding": False,
}


def sop_to_obsidia_ir(sop_text: str, title: str = "Untitled workflow") -> Dict[str, Any]:
    """Convert SOP text into Obsidia IR candidate via the full readonly swarm."""
    result = run_readonly_swarm(sop_text=sop_text, title=title)
    ir = result["obsidia_ir"]
    validate_readonly_output(ir, allow_descriptive_tokens=True)
    ir["adapter_spec"] = ADAPTER_SPEC
    return ir
