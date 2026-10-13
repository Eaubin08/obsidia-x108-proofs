"""M32 RED — R1..R5 (spec §36), plus lifecycle (§32) and identity (§19) reds."""
from __future__ import annotations

import time
import unicodedata

import pytest

from tests.m32 import _harness as H


# R1 — same type + canonical inputs/config -> same identity.
# PRECONDITION test.echo registered | OPERATION finalize two drafts, bindings in different order
# EXPECTED equal ids, ^[0-9a-f]{64}$, draft has no invocation_id | FAILURE ids differ / wrong format / draft id
def test_r1_same_canonical_invocation_same_id(m32):
    test_registry = H.build_test_registry(m32)
    reg = test_registry
    spec2 = H.type_spec(m32, "test.pair", slots=(
        m32.InputSlotSpec(slot_name="a", datum_type=H.TEXT_T, datum_schema_version=H.TEXT_V1, required=True),
        m32.InputSlotSpec(slot_name="b", datum_type=H.TEXT_T, datum_schema_version=H.TEXT_V1, required=True)))
    reg.register_type_spec(spec2)
    d1 = H.draft(m32, "test.pair", [("a", H.text(m32, "1")), ("b", H.text(m32, "2"))])
    d2 = H.draft(m32, "test.pair", [("b", H.text(m32, "2")), ("a", H.text(m32, "1"))])
    assert not hasattr(d1, "invocation_id")
    f1, f2 = m32.finalize(d1, reg), m32.finalize(d2, reg)
    assert f1.invocation_id == f2.invocation_id
    assert H.HEX64.match(f1.invocation_id)


def test_r1_id_matches_reference_preimage(m32):
    test_registry = H.build_test_registry(m32)
    fin = H.finalize(m32, test_registry, "test.echo", [("x", H.text(m32, "hello"))], {"tag": "t"})
    expected = H.ref_invocation_id("test.echo", "v1", [("x", H.ref_datum(H.TEXT_T, H.TEXT_V1, "hello"))], {"tag": "t"})
    assert fin.invocation_id == expected


# R2 — different type -> different identity.
def test_r2_different_type_different_id(m32):
    test_registry = H.build_test_registry(m32)
    a = H.finalize(m32, test_registry, "test.echo", [("x", H.text(m32, "v"))])
    b = H.finalize(m32, test_registry, "test.na", [("x", H.text(m32, "v"))])
    assert a.invocation_id != b.invocation_id


# R3 — different relevant input or config -> different identity.
def test_r3_input_and_config_change_id(m32):
    test_registry = H.build_test_registry(m32)
    base = H.finalize(m32, test_registry, "test.echo", [("x", H.text(m32, "v"))], {"tag": "t1"})
    val = H.finalize(m32, test_registry, "test.echo", [("x", H.text(m32, "w"))], {"tag": "t1"})
    cfg = H.finalize(m32, test_registry, "test.echo", [("x", H.text(m32, "v"))], {"tag": "t2"})
    assert len({base.invocation_id, val.invocation_id, cfg.invocation_id}) == 3


# R4 — wall clock / host do not alter identity; id equals recomputed five-key digest.
def test_r4_wall_clock_and_host_excluded(m32, monkeypatch):
    test_registry = H.build_test_registry(m32)
    a = H.finalize(m32, test_registry, "test.echo", [("x", H.text(m32, "v"))])
    monkeypatch.setattr(time, "time", lambda: 4_102_444_800.0)
    monkeypatch.setattr(time, "time_ns", lambda: 4_102_444_800_000_000_000)
    b = H.finalize(m32, test_registry, "test.echo", [("x", H.text(m32, "v"))])
    assert a.invocation_id == b.invocation_id
    assert a.invocation_id == H.ref_invocation_id("test.echo", "v1", [("x", H.ref_datum(H.TEXT_T, H.TEXT_V1, "v"))], {})


def test_r4_provider_and_environment_only_in_provenance(m32):
    test_registry = H.build_test_registry(m32)
    reg = test_registry
    reg.register_implementation(H.impl(m32, "test.echo", "impl.env1", lambda f, c: H.outcome(m32, "UNKNOWN"),
                                       env="host-A:/srv/one"))
    reg.register_implementation(H.impl(m32, "test.echo", "impl.env2", lambda f, c: H.outcome(m32, "UNKNOWN"),
                                       env="host-B:C:\\two"))
    fin = H.finalize(m32, reg, "test.echo", [("x", H.text(m32, "v"))])
    r1 = m32.execute(fin, reg, "impl.env1")
    r2 = m32.execute(fin, reg, "impl.env2")
    assert r1.invocation_id == r2.invocation_id == fin.invocation_id
    assert r1.provenance.execution_environment_ref != r2.provenance.execution_environment_ref


def test_r4_provider_declared_in_config_changes_id(m32):
    test_registry = H.build_test_registry(m32)
    reg = test_registry
    prov = m32.ConfigFieldSpec(name="provider", value_kind="string", required=False)
    reg.register_type_spec(H.type_spec(m32, "test.semprov", config_fields=(prov,)))
    a = H.finalize(m32, reg, "test.semprov", [("x", H.text(m32, "v"))], {"provider": "p1"})
    b = H.finalize(m32, reg, "test.semprov", [("x", H.text(m32, "v"))], {"provider": "p2"})
    assert a.invocation_id != b.invocation_id


def test_identity_nfc_equivalent_values_same_id(m32):
    test_registry = H.build_test_registry(m32)
    composed = unicodedata.normalize("NFC", "é")
    decomposed = unicodedata.normalize("NFD", "é")
    assert composed != decomposed
    a = H.finalize(m32, test_registry, "test.echo", [("x", H.text(m32, composed))])
    b = H.finalize(m32, test_registry, "test.echo", [("x", H.text(m32, decomposed))])
    assert a.invocation_id == b.invocation_id


# R5 — primitive cannot ACT.
# (a) registration of emits_act=true -> INVALID_TYPE_SPEC; (b) run RETURNS an outcome carrying extra field
# `act` -> INVALID_RESULT at Phase J (candidate is returned from run, not built inside it).
def test_r5a_emits_act_true_unregistrable(m32):
    reg = m32.PrimitiveRegistry("TEST_REGISTRY")
    spec = H.type_spec(m32, "test.act", effects=H.no_effects(m32, emits_act=True))
    H.raises_code(m32, "INVALID_TYPE_SPEC", reg.register_type_spec, spec)


class _OutcomeWithExtra:
    """Hostile candidate outcome: the closed §34 shape plus one forbidden effect field."""

    def __init__(self, status, extra_name):
        self.status, self.output, self.diagnostics = status, None, ()
        setattr(self, extra_name, True)


@pytest.mark.parametrize("extra", ["act"])
def test_r5b_outcome_with_act_field_rejected(m32, extra):
    test_registry = H.build_test_registry(m32)
    reg = test_registry
    reg.register_implementation(H.impl(
        m32, "test.unknown", "impl.hostile",
        lambda f, c: _OutcomeWithExtra(m32.PrimitiveResultStatus.UNKNOWN, extra)))
    fin = H.finalize(m32, reg, "test.unknown", [("x", H.text(m32, "v"))])
    H.raises_code(m32, "INVALID_RESULT", m32.execute, fin, reg, "impl.hostile")


def test_r5_registered_specs_declare_no_act(m32):
    test_registry = H.build_test_registry(m32)
    spec = H.type_spec(m32, "test.probe")
    assert spec.effects_contract.emits_act is False


# Lifecycle (§32): draft has no id; malformed material fails at its certified phase.
def test_lifecycle_draft_has_no_invocation_id_and_final_does(m32):
    test_registry = H.build_test_registry(m32)
    d = H.draft(m32, "test.echo", [("x", H.text(m32, "v"))])
    assert not hasattr(d, "invocation_id")
    fin = m32.finalize(d, test_registry)
    assert H.HEX64.match(fin.invocation_id)


def test_lifecycle_finalize_requires_explicit_registry(m32):
    d = H.draft(m32, "test.echo", [("x", H.text(m32, "v"))])
    with pytest.raises(TypeError):
        m32.finalize(d)  # registry is an explicit argument, never a global default (§32)
