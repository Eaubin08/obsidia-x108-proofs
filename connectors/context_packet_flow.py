"""
Demo connector: Context packet build → validate → sanitize → export flow.
"""
from periphery.context.context_packet_builder_v2 import build_context_packet_v2
from periphery.context.context_packet_validator import validate_context_packet
from periphery.context.context_packet_sanitizer import sanitize_context_packet
from periphery.context.context_packet_exporter import export_context_packet
from periphery.x108_ingress.x108_context_boundary import check_x108_context_boundary


def run_context_packet_flow():
    packet = build_context_packet_v2(
        packet_id="demo_cp_01",
        query="What is the active governance context?",
        language="en",
        context_items=["Session started", "Governance mode ACTIVE"],
    )
    packet_dict = packet.to_dict()

    validation = validate_context_packet(packet_dict)
    assert validation.valid is True, f"Violations: {validation.violations}"

    sanitized = sanitize_context_packet(
        "demo_cp_01",
        ["Session context", "No forbidden tokens here"],
    )
    assert sanitized.readonly is True

    boundary = check_x108_context_boundary(packet_dict)
    assert boundary.passed is True, f"Boundary violations: {boundary.violations}"

    exported = export_context_packet(packet_dict)
    assert exported.dry_run_only is True
    assert exported.readonly is True

    return {
        "validation": validation.to_dict(),
        "sanitized": sanitized.to_dict(),
        "boundary": boundary.to_dict(),
        "exported_hash": exported.export_hash,
        "flow": "CONTEXT_PACKET_FLOW_OK",
    }


if __name__ == "__main__":
    import json
    result = run_context_packet_flow()
    print(json.dumps(result, indent=2))
