import pytest
from periphery.context.context_packet_builder import build_context_packet
from periphery.x108_ingress.readonly_context_ingress import ingest_readonly_context


def test_readonly_ingress_no_act():
    pkt = build_context_packet("x", ["sig1", "sig2"], "READY")
    ingress = ingest_readonly_context("x", pkt)
    assert ingress.can_emit_act is False
    assert ingress.can_write_memory is False


def test_readonly_ingress_stale_rejected():
    pkt = build_context_packet("x", ["sig1"], "STALE")
    ingress = ingest_readonly_context("x", pkt)
    assert ingress.context_accepted is False


def test_context_packet_cannot_decide():
    pkt = build_context_packet("x", ["sig1"], "READY")
    assert pkt.can_decide is False
    pkt.assert_cannot_decide()


def test_invalid_status_raises():
    with pytest.raises(ValueError, match="INVALID_STATUS"):
        build_context_packet("x", [], "GARBAGE")
