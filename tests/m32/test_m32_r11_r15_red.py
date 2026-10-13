"""M32 RED — R11..R14 (spec §36), validation origins (§20/§33), canonical values (§15), slots (§18),
registry/versioning (§27/§28), composition (§26), adapters (§25). R15 sealed oracle: foundation file."""
from __future__ import annotations

import math
import unicodedata

import pytest

from tests.m32 import _harness as H


# R11 — invalid/untyped input fails closed at its certified phase; run never called.
@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_r11_non_canonical_number_phase_b(m32, bad):
    H.raises_code(m32, "NON_CANONICAL_VALUE", m32.TypedCognitiveDatum, H.TEXT_V1, H.TEXT_T, bad)


@pytest.mark.parametrize("bad", [{1, 2}, frozenset({"a"})])
def test_r11_unordered_container_phase_b(m32, bad):
    H.raises_code(m32, "NON_CANONICAL_VALUE", m32.TypedCognitiveDatum, H.TEXT_V1, H.TEXT_T, bad)


def test_r11_integer_bound_phase_b(m32):
    H.raises_code(m32, "NON_CANONICAL_VALUE", m32.TypedCognitiveDatum, H.TEXT_V1, H.TEXT_T, 2 ** 53)


def test_r11_datum_header_codes_phase_b(m32):
    H.raises_code(m32, "INVALID_DATUM_SCHEMA", m32.TypedCognitiveDatum, "", H.TEXT_T, "v")
    H.raises_code(m32, "INVALID_DATUM_TYPE", m32.TypedCognitiveDatum, H.TEXT_V1, "", "v")


def test_r11_semantic_refs_empty_string_rejected_without_new_code(m32):
    # §32 Phase B requires non-empty strings; no dedicated code is named, so only fail-closed is asserted.
    with pytest.raises(m32.InvocationValidationError):
        m32.TypedCognitiveDatum(H.TEXT_V1, H.TEXT_T, "v", semantic_refs=("",))


def test_r11_binding_phase_c_and_draft_phase_d(m32):
    H.raises_code(m32, "INVALID_BINDING", m32.PrimitiveInputBinding, "", H.text(m32, "v"))
    H.raises_code(m32, "INVALID_BINDING", m32.PrimitiveInputBinding, "x", {"datum_type": H.TEXT_T})
    H.raises_code(m32, "INVALID_BINDING", m32.PrimitiveInvocationDraft, H.INVOCATION_SCHEMA, "test.echo", "v1",
                  ({"slot_name": "x"},), {})
    H.raises_code(m32, "INVALID_IMMUTABLE_CONFIG", m32.PrimitiveInvocationDraft, H.INVOCATION_SCHEMA, "test.echo",
                  "v1", (), ["not", "a", "mapping"])


def test_r11_phase_e_codes_and_run_not_called(m32):
    test_registry = H.build_test_registry(m32)
    reg = test_registry
    spy = H.Spy(lambda f, c: H.outcome(m32, "UNKNOWN"))
    reg.register_implementation(H.impl(m32, "test.echo", "impl.spy", spy))
    t = lambda v="v", s=H.TEXT_V1: H.text(m32, v, schema=s)  # noqa: E731
    cases = [
        ("DUPLICATE_INPUT_SLOT", [("x", t()), ("x", t())]),
        ("UNKNOWN_INPUT_SLOT", [("x", t()), ("y", t())]),
        ("DATUM_SCHEMA_MISMATCH", [("x", t(s=H.TEXT_V2))]),
    ]
    for code, bindings in cases:
        H.raises_code(m32, code, m32.finalize, H.draft(m32, "test.echo", bindings), reg)
    wrong_type = m32.TypedCognitiveDatum(H.TEXT_V1, "test.other", "v")
    H.raises_code(m32, "DATUM_TYPE_MISMATCH", m32.finalize, H.draft(m32, "test.echo", [("x", wrong_type)]), reg)
    H.raises_code(m32, "INVALID_IMMUTABLE_CONFIG", m32.finalize,
                  H.draft(m32, "test.echo", [("x", t())], {"undeclared": 1}), reg)
    H.raises_code(m32, "INVALID_SCHEMA_VERSION", m32.finalize,
                  m32.PrimitiveInvocationDraft("m32.invocation.v0", "test.echo", "v1",
                                               (m32.PrimitiveInputBinding("x", t()),), {}), reg)
    assert spy.calls == 0


def test_nfc_equivalent_slot_names_are_duplicates(m32):
    test_registry = H.build_test_registry(m32)
    reg = test_registry
    reg.register_type_spec(H.type_spec(m32, "test.accent", slots=(
        m32.InputSlotSpec(slot_name=unicodedata.normalize("NFC", "é"), datum_type=H.TEXT_T,
                          datum_schema_version=H.TEXT_V1, required=True),)))
    d = H.draft(m32, "test.accent", [(unicodedata.normalize("NFC", "é"), H.text(m32, "1")),
                                    (unicodedata.normalize("NFD", "é"), H.text(m32, "2"))])
    H.raises_code(m32, "DUPLICATE_INPUT_SLOT", m32.finalize, d, reg)


def test_inputs_canonically_sorted_by_nfc_slot(m32):
    test_registry = H.build_test_registry(m32)
    reg = test_registry
    reg.register_type_spec(H.type_spec(m32, "test.trio", slots=tuple(
        m32.InputSlotSpec(slot_name=n, datum_type=H.TEXT_T, datum_schema_version=H.TEXT_V1, required=True)
        for n in ("c", "a", "b"))))
    fin = H.finalize(m32, reg, "test.trio", [("b", H.text(m32, "2")), ("c", H.text(m32, "3")),
                                             ("a", H.text(m32, "1"))])
    assert [b.slot_name for b in fin.inputs] == ["a", "b", "c"]


def test_declared_slots_order_independent_and_nfc_unique(m32):
    def spec(order):
        return H.type_spec(m32, "test.order", slots=tuple(
            m32.InputSlotSpec(slot_name=n, datum_type=H.TEXT_T, datum_schema_version=H.TEXT_V1, required=True)
            for n in order))
    reg = m32.PrimitiveRegistry("TEST_REGISTRY")
    reg.register_type_spec(spec(("b", "a")))
    reg.register_type_spec(spec(("a", "b")))  # canonical-identical -> idempotent (§17 sorted slots, §27)
    dup = H.type_spec(m32, "test.dupdecl", slots=(
            m32.InputSlotSpec(slot_name=unicodedata.normalize("NFC", "é"), datum_type=H.TEXT_T,
                              datum_schema_version=H.TEXT_V1, required=True),
            m32.InputSlotSpec(slot_name=unicodedata.normalize("NFD", "é"), datum_type=H.TEXT_T,
                              datum_schema_version=H.TEXT_V1, required=True)))
    H.raises_code(m32, "INVALID_TYPE_SPEC", reg.register_type_spec, dup)  # §33: origin = registration


def test_caller_mutation_does_not_alter_identity(m32):
    test_registry = H.build_test_registry(m32)
    payload = {"k": ["a", "b"]}
    datum = m32.TypedCognitiveDatum(H.TEXT_V1, H.TEXT_T, payload)
    cfg = {"tag": "t"}
    fin = H.finalize(m32, test_registry, "test.echo", [("x", datum)], cfg)
    before = fin.invocation_id
    payload["k"].append("c")
    cfg["tag"] = "changed"
    assert datum.value == {"k": ["a", "b"]}
    assert H.finalize(m32, test_registry, "test.echo", [("x", m32.TypedCognitiveDatum(
        H.TEXT_V1, H.TEXT_T, {"k": ["a", "b"]}))], {"tag": "t"}).invocation_id == before
    with pytest.raises(Exception):
        fin.invocation_id = "0" * 64


def test_negative_zero_canonicalizes_to_zero(m32):
    test_registry = H.build_test_registry(m32)
    a = H.finalize(m32, test_registry, "test.echo", [("x", m32.TypedCognitiveDatum(H.TEXT_V1, H.TEXT_T, -0.0))])
    b = H.finalize(m32, test_registry, "test.echo", [("x", m32.TypedCognitiveDatum(H.TEXT_V1, H.TEXT_T, 0))])
    assert a.invocation_id == b.invocation_id


# Missing required slot -> finalized, id exists, INSUFFICIENT_INPUT, run not called.
def test_missing_required_slot_flow(m32):
    test_registry = H.build_test_registry(m32)
    reg = test_registry
    spy = H.Spy(lambda f, c: H.outcome(m32, "UNKNOWN"))
    reg.register_implementation(H.impl(m32, "test.echo", "impl.spy2", spy))
    fin = H.finalize(m32, reg, "test.echo", [])
    assert H.HEX64.match(fin.invocation_id)
    rec = m32.execute(fin, reg, "impl.spy2")
    assert rec.result.status is m32.PrimitiveResultStatus.INSUFFICIENT_INPUT
    assert rec.result.output is None and rec.result.invocation_id == fin.invocation_id
    assert spy.calls == 0


# Registry / versioning (§27/§28/§34).
def test_registry_idempotent_conflict_unknown(m32):
    test_registry = H.build_test_registry(m32)
    reg = m32.PrimitiveRegistry("TEST_REGISTRY")
    reg.register_type_spec(H.type_spec(m32, "test.r"))
    reg.register_type_spec(H.type_spec(m32, "test.r"))  # new object, same canonical bytes -> idempotent
    H.raises_code(m32, "REGISTRY_CONFLICT", reg.register_type_spec, H.type_spec(m32, "test.r", slot_schema=H.TEXT_V2))
    H.raises_code(m32, "UNKNOWN_PRIMITIVE_TYPE", m32.finalize, H.draft(m32, "test.nope", []), reg)
    H.raises_code(m32, "UNKNOWN_PRIMITIVE_VERSION", m32.finalize, H.draft(m32, "test.r", [], spec_version="v2"), reg)
    H.raises_code(m32, "UNKNOWN_PRIMITIVE_VERSION", m32.finalize, H.draft(m32, "test.r", [], spec_version="latest"), reg)


def test_v1_never_resolves_to_v2(m32):
    reg = m32.PrimitiveRegistry("TEST_REGISTRY")
    reg.register_type_spec(H.type_spec(m32, "test.ver", spec_version="v2"))
    H.raises_code(m32, "UNKNOWN_PRIMITIVE_VERSION", m32.finalize, H.draft(m32, "test.ver", [], spec_version="v1"), reg)


def test_implementation_registry_never_raises_type_codes(m32):
    reg = m32.PrimitiveRegistry("TEST_REGISTRY")
    H.raises_code(m32, "UNKNOWN_IMPLEMENTATION", reg.register_implementation,
                  H.impl(m32, "test.absent", "impl.a", lambda f, c: None))
    reg.register_type_spec(H.type_spec(m32, "test.r"))
    fin = H.finalize(m32, reg, "test.r", [("x", H.text(m32, "v"))])
    H.raises_code(m32, "UNKNOWN_IMPLEMENTATION", m32.execute, fin, reg, "impl.missing")


def test_invalid_execution_request_before_phase_h(m32):
    test_registry = H.build_test_registry(m32)
    spy = H.Spy(lambda f, c: H.outcome(m32, "UNKNOWN"))
    test_registry.register_implementation(H.impl(m32, "test.echo", "impl.spy3", spy))
    fin = H.finalize(m32, test_registry, "test.echo", [("x", H.text(m32, "v"))])
    H.raises_code(m32, "INVALID_EXECUTION_REQUEST", m32.execute, fin, test_registry, "impl.spy3",
                  derived_from_invocation_ids=("NOT-HEX",))
    assert spy.calls == 0


def test_run_returning_non_outcome_fails_closed(m32):
    test_registry = H.build_test_registry(m32)
    test_registry.register_implementation(H.impl(m32, "test.echo", "impl.junk", lambda f, c: "junk"))
    fin = H.finalize(m32, test_registry, "test.echo", [("x", H.text(m32, "v"))])
    with pytest.raises(m32.InvocationValidationError):
        m32.execute(fin, test_registry, "impl.junk")


# R12 — output retains required provenance.
def test_r12_provenance_retained(m32):
    test_registry = H.build_test_registry(m32)
    fin = H.finalize(m32, test_registry, "test.echo", [("x", H.text(m32, "v", refs=("r2", "r1", "r2")))])
    rec = m32.execute(fin, test_registry, "impl.a")
    p = rec.result.provenance
    assert p.implementation_id == "impl.a"
    assert isinstance(p.source_refs, tuple) and isinstance(p.derived_from_invocation_ids, tuple)
    assert p.source_refs == ("r1", "r2")
    assert rec.provenance == p


# R13 — compatible composition works; exact type+schema match only.
def test_r13_composition_linkage_and_schema_mismatch(m32):
    test_registry = H.build_test_registry(m32)
    reg = test_registry
    up = m32.execute(H.finalize(m32, reg, "test.echo", [("x", H.text(m32, "v"))]), reg, "impl.a")
    down_fin = H.finalize(m32, reg, "test.echo", [("x", up.result.output)])
    down = m32.execute(down_fin, reg, "impl.a", derived_from_invocation_ids=(up.invocation_id, up.invocation_id))
    assert down.provenance.derived_from_invocation_ids == (up.invocation_id,)
    H.raises_code(m32, "DATUM_SCHEMA_MISMATCH", m32.finalize, H.draft(m32, "test.echo2", [("x", up.result.output)]), reg)


def test_composition_no_fuzzy_type_match(m32):
    test_registry = H.build_test_registry(m32)
    similar = m32.TypedCognitiveDatum(H.TEXT_V1, "test.text.extended", "v")
    H.raises_code(m32, "DATUM_TYPE_MISMATCH", m32.finalize, H.draft(m32, "test.echo", [("x", similar)]), test_registry)


# R14 — domain adapter cannot grant authority; statuses pass through; reverse/invalid fail closed.
def _adapter(m32):
    spec = m32.DomainAdapterSpec(adapter_id="test.adapter", adapter_version="v1", source_domain_type="test.domain",
                                 target_datum_type=H.TEXT_T, target_datum_schema_version=H.TEXT_V1,
                                 reverse_supported=False)

    def to_core(v):
        if not isinstance(v, str):
            raise ValueError("invalid domain value")
        return m32.TypedCognitiveDatum(H.TEXT_V1, H.TEXT_T, v)

    return m32.DomainAdapter(spec, to_core)


def test_r14_adapter_boundary(m32):
    test_registry = H.build_test_registry(m32)
    ad = _adapter(m32)
    d = ad.to_core("domain-value")
    assert (d.datum_type, d.schema_version, d.value) == (H.TEXT_T, H.TEXT_V1, "domain-value")
    assert not hasattr(d, "authority") and not hasattr(d, "verified")
    assert getattr(d, "semantic_refs", None) in (None, ()) or "test.adapter" not in d.semantic_refs
    rec = m32.execute(H.finalize(m32, test_registry, "test.unknown", [("x", d)]), test_registry, "impl.a")
    assert rec.result.status is m32.PrimitiveResultStatus.UNKNOWN
    H.raises_code(m32, "ADAPTER_REVERSE_UNSUPPORTED", ad.from_core, d)
    H.raises_code(m32, "ADAPTER_INPUT_INVALID", ad.to_core, 12345)


def test_adapter_wrong_target_type_fails_closed(m32):
    spec = m32.DomainAdapterSpec(adapter_id="test.bad", adapter_version="v1", source_domain_type="test.domain",
                                 target_datum_type=H.TEXT_T, target_datum_schema_version=H.TEXT_V1,
                                 reverse_supported=False)
    ad = m32.DomainAdapter(spec, lambda v: m32.TypedCognitiveDatum(H.TEXT_V2, H.TEXT_T, v))  # silent schema switch
    # §25: to_core output must match the declared target; no dedicated code is named -> fail closed only.
    with pytest.raises(m32.InvocationValidationError):
        ad.to_core("v")
