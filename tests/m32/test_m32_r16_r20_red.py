"""M32 RED — R18..R20 (spec §36), test-registry isolation (§30). R15/R16/R17/R7(c) sealed oracles live in
test_m32_foundation_boundary_red.py."""
from __future__ import annotations

from tests.m32 import _harness as H


# R18 — different implementation/provider does not masquerade; no fusion.
def test_r18_two_implementations_same_id_distinct_records(m32):
    test_registry = H.build_test_registry(m32)
    fin = H.finalize(m32, test_registry, "test.echo", [("x", H.text(m32, "v"))])
    a = m32.execute(fin, test_registry, "impl.a")
    b = m32.execute(fin, test_registry, "impl.b")
    assert a.invocation_id == b.invocation_id == fin.invocation_id
    assert a.provenance.implementation_id == "impl.a" and b.provenance.implementation_id == "impl.b"
    assert a.provenance.provider_id != b.provenance.provider_id
    assert a.result.output.value == "v" and b.result.output.value == "v!"
    assert a is not b and a.result is not b.result


def test_provenance_metadata_canonical(m32):
    test_registry = H.build_test_registry(m32)
    fin = H.finalize(m32, test_registry, "test.echo", [("x", H.text(m32, "v", refs=("b", "a")))])
    up = H.ref_invocation_id("test.echo", "v1", [("x", H.ref_datum(H.TEXT_T, H.TEXT_V1, "z"))], {})
    rec1 = m32.execute(fin, test_registry, "impl.a", derived_from_invocation_ids=(up, fin.invocation_id))
    rec2 = m32.execute(fin, test_registry, "impl.a", derived_from_invocation_ids=(fin.invocation_id, up, up))
    assert rec1.provenance.source_refs == rec2.provenance.source_refs == ("a", "b")
    assert rec1.provenance.derived_from_invocation_ids == tuple(sorted({up, fin.invocation_id}))
    assert rec1.provenance.derived_from_invocation_ids == rec2.provenance.derived_from_invocation_ids


# R19 — output cannot self-label VERIFIED/PROMOTED.
def test_r19_result_closed_shape(m32):
    test_registry = H.build_test_registry(m32)
    fin = H.finalize(m32, test_registry, "test.echo", [("x", H.text(m32, "v"))])
    rec = m32.execute(fin, test_registry, "impl.a")
    r = rec.result
    for field in ("schema_version", "invocation_id", "status", "output", "provenance", "diagnostics"):
        assert hasattr(r, field)
    assert r.schema_version == H.RESULT_SCHEMA
    assert not hasattr(r, "verified") and not hasattr(r, "promoted")
    S = m32.PrimitiveResultStatus
    for extra in ("verified", "promoted"):
        H.raises_code(m32, "INVALID_RESULT", m32.PrimitiveResult, H.RESULT_SCHEMA, fin.invocation_id,
                      S.PRODUCED, r.output, r.provenance, (), **{extra: True})
    H.raises_code(m32, "INVALID_RESULT", m32.PrimitiveResult, H.RESULT_SCHEMA, fin.invocation_id,
                  "VERIFIED", r.output, r.provenance, ())


# R20 — cannot silently consume UNKNOWN as FALSE.
def test_r20_unknown_upstream_yields_insufficient_input_downstream(m32):
    test_registry = H.build_test_registry(m32)
    reg = test_registry
    up = m32.execute(H.finalize(m32, reg, "test.unknown", [("x", H.text(m32, "v"))]), reg, "impl.a")
    assert up.result.output is None
    spy = H.Spy(lambda f, c: H.outcome(m32, "PRODUCED", H.text(m32, "false")))
    reg.register_implementation(H.impl(m32, "test.echo", "impl.spy20", spy))
    bindings = [("x", up.result.output)] if up.result.output is not None else []
    down = m32.execute(H.finalize(m32, reg, "test.echo", bindings), reg, "impl.spy20",
                       derived_from_invocation_ids=(up.invocation_id,))
    assert down.result.status is m32.PrimitiveResultStatus.INSUFFICIENT_INPUT
    assert down.result.output is None and spy.calls == 0


# Test-registry isolation (§30).
def test_test_namespace_rejected_in_production(m32):
    prod = m32.PrimitiveRegistry("PRODUCTION_REGISTRY")
    H.raises_code(m32, "TEST_PRIMITIVE_IN_PRODUCTION", prod.register_type_spec, H.type_spec(m32, "test.echo"))


def test_test_registry_accepts_test_namespace(m32):
    test_registry = H.build_test_registry(m32)
    reg = m32.PrimitiveRegistry("TEST_REGISTRY")
    reg.register_type_spec(H.type_spec(m32, "test.echo"))
    H.finalize(m32, reg, "test.echo", [("x", H.text(m32, "v"))])
