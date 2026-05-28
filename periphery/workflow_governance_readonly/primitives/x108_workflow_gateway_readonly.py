from __future__ import annotations

from typing import Any, Dict

from ..adapters.x108_readonly_gateway_adapter import sop_to_x108_readonly_envelope
from ..boundary import validate_readonly_output

PRIMITIVE_SPEC = {
    "primitive_id": "X108_WORKFLOW_GATEWAY_READONLY_V4",
    "role": "Create readonly envelope candidate for X108 boundary inspection.",
    "direct_runtime_call": False,
    "x108_runtime_binding": False,
}


def build_x108_workflow_gateway_envelope_readonly(sop_text: str, title: str = "Untitled workflow") -> Dict[str, Any]:
    """Primitive 5 — X108_WORKFLOW_GATEWAY."""
    envelope = sop_to_x108_readonly_envelope(sop_text, title=title)
    validate_readonly_output(envelope, allow_descriptive_tokens=True)
    envelope["gateway_kind"] = "X108_WORKFLOW_GATEWAY_READONLY"
    envelope["direct_runtime_call"] = False
    envelope["candidate_only"] = True
    envelope["primitive_spec"] = PRIMITIVE_SPEC
    return envelope
