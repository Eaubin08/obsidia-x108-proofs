"""M32 RED — R6..R10 (spec §36), plus result taxonomy reds (§23)."""
from __future__ import annotations

import pytest

from tests.m32 import _harness as H
from tests.m32.test_m32_r01_r05_red import _OutcomeWithExtra


# R6 — primitive cannot write durable memory.
def test_r6a_memory_write_true_unregistrable(m32):
    reg = m32.PrimitiveRegistry("TEST_REGISTRY")
    spec = H.type_spec(m32, "test.mem", effects=H.no_effects(m32, memory_write=True))
    H.raises_code(m32, "INVALID_TYPE_SPEC", reg.register_type_spec, spec)


def test_r6b_outcome_with_memory_write_field_rejected(m32):
    test_registry = H.build_test_registry(m32)
    reg = test_registry
    reg.register_implementation(H.impl(
        m32, "test.unknown", "impl.memwrite",
        lambda f, c: _OutcomeWithExtra(m32.PrimitiveResultStatus.UNKNOWN, "memory_write")))
    fin = H.finalize(m32, reg, "test.unknown", [("x", H.text(m32, "v"))])
    H.raises_code(m32, "INVALID_RESULT", m32.execute, fin, reg, "impl.memwrite")


# R7 — primitive cannot mutate B8: (a) declaration, (b) closed outcome; (c) sealed oracle lives in
# test_m32_foundation_boundary_red.py::test_r7c_b8_sealed_oracle.
@pytest.mark.parametrize("flag", ["b8_mutation", "binder_mutation", "kernel_mutation", "kx108_mutation"])
def test_r7a_mutation_flags_unregistrable(m32, flag):
    reg = m32.PrimitiveRegistry("TEST_REGISTRY")
    spec = H.type_spec(m32, "test.mut", effects=H.no_effects(m32, **{flag: True}))
    H.raises_code(m32, "INVALID_TYPE_SPEC", reg.register_type_spec, spec)


def test_r7b_outcome_with_b8_mutation_field_rejected(m32):
    test_registry = H.build_test_registry(m32)
    reg = test_registry
    reg.register_implementation(H.impl(
        m32, "test.unknown", "impl.b8",
        lambda f, c: _OutcomeWithExtra(m32.PrimitiveResultStatus.UNKNOWN, "b8_mutation")))
    fin = H.finalize(m32, reg, "test.unknown", [("x", H.text(m32, "v"))])
    H.raises_code(m32, "INVALID_RESULT", m32.execute, fin, reg, "impl.b8")


def test_run_receives_no_effect_capable_handle(m32):
    test_registry = H.build_test_registry(m32)
    seen = {}

    def probe(fin, cfg):
        seen["args"] = (fin, cfg)
        return H.outcome(m32, "UNKNOWN")

    reg = test_registry
    reg.register_implementation(H.impl(m32, "test.unknown", "impl.probe", probe))
    fin = H.finalize(m32, reg, "test.unknown", [("x", H.text(m32, "v"))])
    m32.execute(fin, reg, "impl.probe")
    got_fin, got_cfg = seen["args"]
    assert got_fin is fin or got_fin == fin
    assert not isinstance(got_cfg, type(reg))


# R8 — UNKNOWN does not become FALSE.
def test_r8_unknown_status_and_null_output(m32):
    test_registry = H.build_test_registry(m32)
    fin = H.finalize(m32, test_registry, "test.unknown", [("x", H.text(m32, "v"))])
    rec = m32.execute(fin, test_registry, "impl.a")
    assert rec.result.status is m32.PrimitiveResultStatus.UNKNOWN
    assert rec.result.output is None
    assert {s.name for s in m32.PrimitiveResultStatus} == H.STATUS_NAMES


# R9 — NOT_APPLICABLE distinct from FAILED_RUNTIME; no exception escapes execute.
def test_r9_not_applicable_vs_failed_runtime(m32):
    test_registry = H.build_test_registry(m32)
    na = m32.execute(H.finalize(m32, test_registry, "test.na", [("x", H.text(m32, "v"))]), test_registry, "impl.a")
    fr = m32.execute(H.finalize(m32, test_registry, "test.failure", [("x", H.text(m32, "v"))]), test_registry, "impl.a")
    assert na.result.status is m32.PrimitiveResultStatus.NOT_APPLICABLE
    assert fr.result.status is m32.PrimitiveResultStatus.FAILED_RUNTIME
    assert na.result.status != fr.result.status


# R10 — FAILED_RUNTIME is not semantic FALSE; implementation attempted; diagnostics = class __name__.
def test_r10_failed_runtime_shape(m32):
    test_registry = H.build_test_registry(m32)
    spy = H.Spy(lambda f, c: (_ for _ in ()).throw(H.ControlledFailure("x")))
    reg = test_registry
    reg.register_implementation(H.impl(m32, "test.failure", "impl.spy", spy))
    fin = H.finalize(m32, reg, "test.failure", [("x", H.text(m32, "v"))])
    rec = m32.execute(fin, reg, "impl.spy")
    assert spy.calls == 1
    assert rec.result.status is m32.PrimitiveResultStatus.FAILED_RUNTIME
    assert rec.result.output is None
    assert rec.result.diagnostics[0] == "ControlledFailure"
    assert rec.invocation_id == fin.invocation_id


# Result taxonomy (§23): output presence rules, exact fields, no boolean semantics.
def test_result_output_rules_enforced_at_construction(m32):
    test_registry = H.build_test_registry(m32)
    fin = H.finalize(m32, test_registry, "test.echo", [("x", H.text(m32, "v"))])
    prov = m32.execute(fin, test_registry, "impl.a").provenance
    S = m32.PrimitiveResultStatus
    H.raises_code(m32, "INVALID_RESULT", m32.PrimitiveResult, H.RESULT_SCHEMA, fin.invocation_id,
                  S.PRODUCED, None, prov, ())
    for name in ("NOT_APPLICABLE", "INSUFFICIENT_INPUT", "UNKNOWN", "FAILED_RUNTIME"):
        H.raises_code(m32, "INVALID_RESULT", m32.PrimitiveResult, H.RESULT_SCHEMA, fin.invocation_id,
                      getattr(S, name), H.text(m32, "leak"), prov, ())


def test_statuses_are_branched_on_enum_not_truthiness(m32):
    S = m32.PrimitiveResultStatus
    members = list(S)
    assert len(members) == 5
    assert S.UNKNOWN != S.PRODUCED and S.FAILED_RUNTIME != S.NOT_APPLICABLE
    assert S.INSUFFICIENT_INPUT != S.UNKNOWN
    assert not hasattr(S, "FALSE") and not hasattr(S, "TRUE") and not hasattr(S, "VERIFIED")
