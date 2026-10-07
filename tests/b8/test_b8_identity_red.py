"""RED tranche 1 — local canonical serialization, B6 conformance, full SHA-256 identities, slot
canonicalization and the object bound (spec §3, §5).

§3 states identities are computed over strict canonical JSON as defined by
`app.harness.state_explicit.contracts.canonical_json`; B8 owns a local implementation (no production
import of B6), whose output must therefore be byte-identical to B6 on the shared JSON subset. The B6
import below is test-only compatibility evidence, never a B8 production dependency.
"""
from __future__ import annotations

import hashlib
import math
import re
import unicodedata

import pytest

from app.harness.state_explicit.contracts import canonical_json as b6_canonical_json

SAMPLES = [
    {"b": 1, "a": [3, 2, 1], "c": {"z": None, "y": True, "x": False}},
    {"é": "café", "日本": ["語", "é"], "nested": {"k": [{"b": 2, "a": 1}]}},
    [1, -7, 0, "x", None, True, False, [], {}],
    "plain string with \"quotes\" and \\ backslash",
    12345678901234567890,
]


@pytest.mark.parametrize("value", SAMPLES, ids=range(len(SAMPLES)))
def test_local_canonical_json_matches_b6_on_shared_subset(b8, value):
    assert b8.canonical_json(value) == b6_canonical_json(value)


def test_canonical_json_ignores_mapping_insertion_order(b8):
    a = {"x": 1, "y": {"p": [1, 2], "q": "v"}}
    b = {"y": {"q": "v", "p": [1, 2]}, "x": 1}
    assert b8.canonical_json(a) == b8.canonical_json(b)


@pytest.mark.parametrize("bad", [math.nan, math.inf, {1: "x"}, {"s": {1, 2}}, object()])
def test_canonical_json_is_strict(b8, bad):
    with pytest.raises(ValueError):
        b8.canonical_json(bad)


def test_b8_production_does_not_import_b6_serialization():
    from tests.b8.test_b8_authority_boundary_red import production_imports
    assert not any(m.startswith("app.harness") for m in production_imports())


def _sha(value):
    return hashlib.sha256(b6_canonical_json(value).encode("utf-8")).hexdigest()


def test_full_identity_is_prefix_plus_64_hex_sha256(b8):
    value = {"k": "v", "n": 1}
    ident = b8.full_identity("b8treq_", value)
    assert ident == "b8treq_" + _sha(value)
    assert re.fullmatch(r"b8treq_[0-9a-f]{64}", ident)
    assert b8.full_identity("b8treq_", {"n": 1, "k": "v"}) == ident
    assert b8.full_identity("b8treq_", {"k": "w", "n": 1}) != ident


def _expected_slot(claim_class, domain, subjects, contexts, predicate):
    norm = lambda s: unicodedata.normalize("NFC", s)  # noqa: E731  (spec §5: NFC, no other normalization)
    payload = [claim_class, norm(domain), sorted(set(map(norm, subjects))), sorted(set(map(norm, contexts))), norm(predicate)]
    return "b8slot_" + _sha(payload)


def test_knowledge_slot_identity_follows_spec_formula(b8):
    got = b8.knowledge_slot_id("DOMAIN_CLAIM", "domain:x", ["subj:B", "subj:A"], ["ctx:1"], "pred:temp")
    assert got == _expected_slot("DOMAIN_CLAIM", "domain:x", ["subj:A", "subj:B"], ["ctx:1"], "pred:temp")
    assert re.fullmatch(r"b8slot_[0-9a-f]{64}", got)


def test_knowledge_slot_order_duplicates_and_unicode_forms_do_not_change_identity(b8):
    base = b8.knowledge_slot_id("DOMAIN_CLAIM", "d", ["é", "b"], [], "p")
    assert b8.knowledge_slot_id("DOMAIN_CLAIM", "d", ["b", "é", "b"], [], "p") == base
    assert b8.knowledge_slot_id("DOMAIN_CLAIM", "d", ["é", "b"], [], "p") == base
    assert b8.knowledge_slot_id("DOMAIN_CLAIM", "d", ["É", "b"], [], "p") != base       # no case folding


def test_knowledge_slot_context_may_be_empty_but_differs_from_non_empty(b8):
    assert b8.knowledge_slot_id("DOMAIN_CLAIM", "d", ["s"], [], "p") != b8.knowledge_slot_id("DOMAIN_CLAIM", "d", ["s"], ["c"], "p")


@pytest.mark.parametrize("subjects,contexts,domain,predicate", [
    ([], [], "d", "p"),                 # EMPTY_SUBJECT_REFS=REJECT
    ([""], [], "d", "p"),
    (["  "], [], "d", "p"),
    ([3], [], "d", "p"),
    (["s"], [" "], "d", "p"),
    (["s"], [], "", "p"),
    (["s"], [], "d", "   "),
])
def test_malformed_slot_components_are_rejected_with_malformed_slot(b8, subjects, contexts, domain, predicate):
    with pytest.raises(b8.MalformedSlot) as exc:
        b8.knowledge_slot_id("DOMAIN_CLAIM", domain, subjects, contexts, predicate)
    assert exc.value.reason is b8.ReasonCode.malformed_slot


def test_object_total_bound_is_the_spec_value(b8, spec_text):
    assert "OBJECT_TOTAL_BOUND=MAX_CANDIDATE_CHARS=32768" in spec_text
    assert b8.OBJECT_TOTAL_BOUND == 32768
