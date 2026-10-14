"""M41 World Model V1 — minimal, transient, non-sovereign world hypothesis representation.

Contract: docs/architecture/M41_WORLD_MODEL_SPEC_V1.md (certified). Three immutable types:
WorldMaterialRef, WorldStateHypothesis, WorldHypothesisSet, plus the read-only M41_EFFECTS mapping.

Pure representation: no I/O, no memory or B10 write, no B8 promotion, no action, no reference
resolution, no identity resolution, no selection. Identifiers reuse M32 canonical JSON (RFC 8785
numbers) and SHA-256; they are technical identities of canonical bytes, never world identity.
"""
from __future__ import annotations

import math as _math
import re as _re
import unicodedata as _unicodedata
from types import MappingProxyType as _MappingProxyType

import app.primitives.m32 as _m32
from app.primitives.m32 import TypedCognitiveDatum as _TypedCognitiveDatum

__all__ = ["WorldMaterialRef", "WorldStateHypothesis", "WorldHypothesisSet", "M41_EFFECTS"]

_STATE = "STATE_OF_PRESUMED_REFERENT"
_IDENTITY = "REFERENT_IDENTITY"
_KINDS = (_STATE, _IDENTITY)
_TOKEN = _re.compile(r"[a-z][a-z0-9_]*(\.[a-z0-9_]+)+")
_HYPOTHESIS_SCHEMA = "m41.world_state_hypothesis.v1"
_SET_SCHEMA = "m41.world_hypothesis_set.v1"

M41_EFFECTS = _MappingProxyType({
    "memory_write": False,
    "emits_act": False,
    "b8": False,
    "binder": False,
    "kernel": False,
    "kx108": False,
    "external_io": False,
    "durable_state_write": False,
})


def _fail(code, message):
    raise ValueError(f"{code}: {message}")


def _is_token(value):
    return isinstance(value, str) and _TOKEN.fullmatch(value) is not None


def _is_opaque(value):
    return (isinstance(value, str) and "\x00" not in value
            and _unicodedata.normalize("NFC", value).strip() != "")


def _nfc(value):
    return _unicodedata.normalize("NFC", value)


def _canonical_json(obj):
    return _m32._serialize(_m32._freeze(obj, "M41_NON_CANONICAL"))


def _sha256_id(obj):
    return _m32._sha256_hex(_m32._freeze(obj, "M41_NON_CANONICAL"))


def _as_sequence(value, field):
    if not isinstance(value, (list, tuple)):
        _fail("M41_INVALID_COLLECTION", f"{field} must be a list or tuple")
    return tuple(value)


class _Immutable:
    __slots__ = ()

    def __setattr__(self, name, value):
        raise AttributeError(f"{type(self).__name__} is immutable")

    def __delattr__(self, name):
        raise AttributeError(f"{type(self).__name__} is immutable")


class WorldMaterialRef(_Immutable):
    """Unresolved, declared reference to external world material. Proves no existence, reliability,
    identity or provenance; source_label is declared, never verified."""

    __slots__ = ("ref_kind", "ref_id", "source_label")

    def __init__(self, ref_kind, ref_id, source_label=None):
        if not _is_token(ref_kind):
            _fail("M41_INVALID_REF", "ref_kind must be a namespaced token")
        if not _is_opaque(ref_id):
            _fail("M41_INVALID_REF", "ref_id must be a non-blank string without NUL")
        if source_label is not None and not _is_opaque(source_label):
            _fail("M41_INVALID_REF", "source_label must be a non-blank string without NUL")
        object.__setattr__(self, "ref_kind", ref_kind)
        object.__setattr__(self, "ref_id", _nfc(ref_id))
        object.__setattr__(self, "source_label", None if source_label is None else _nfc(source_label))

    def _canonical(self):
        obj = {"ref_id": self.ref_id, "ref_kind": self.ref_kind}
        if self.source_label is not None:
            obj["source_label"] = self.source_label
        return obj

    def __eq__(self, other):
        if not isinstance(other, WorldMaterialRef):
            return NotImplemented
        return (self.ref_kind, self.ref_id, self.source_label) == \
            (other.ref_kind, other.ref_id, other.source_label)

    def __hash__(self):
        return hash((self.ref_kind, self.ref_id, self.source_label))

    def __repr__(self):
        return f"WorldMaterialRef(ref_kind={self.ref_kind!r}, ref_id={self.ref_id!r}, source_label={self.source_label!r})"


def _ref_collection(value, field, required):
    items = _as_sequence(value, field)
    if required and not items:
        _fail("M41_MISSING_MATERIAL", f"{field} must contain at least one reference")
    for item in items:
        if not isinstance(item, WorldMaterialRef):
            _fail("M41_INVALID_COLLECTION", f"{field} must contain only WorldMaterialRef")
    keyed = [(_canonical_json(item._canonical()), item) for item in items]
    if len({key for key, _ in keyed}) != len(keyed):
        _fail("M41_DUPLICATE_ENTRY", f"duplicate entry in {field}")
    return tuple(item for _, item in sorted(keyed, key=lambda pair: pair[0]))


def _unknowns(value):
    items = _as_sequence(value, "unknowns")
    for item in items:
        if not isinstance(item, str):
            _fail("M41_INVALID_COLLECTION", "unknowns must contain only strings")
        if not _is_opaque(item):
            _fail("M41_INVALID_COLLECTION", "unknowns entries must be non-blank strings without NUL")
    normalized = tuple(_nfc(item) for item in items)
    if len(set(normalized)) != len(normalized):
        _fail("M41_DUPLICATE_ENTRY", "duplicate entry in unknowns")
    return tuple(sorted(normalized))


def _check_rank(rank):
    if rank is not None and (type(rank) is not int or rank < 0):
        _fail("M41_INVALID_SCALAR", "rank must be a non-negative int")


def _check_confidence(confidence):
    if confidence is None:
        return
    if type(confidence) not in (int, float) or not _math.isfinite(confidence) or not 0 <= confidence <= 1:
        _fail("M41_INVALID_SCALAR", "confidence must be a finite number in [0, 1]")


class WorldStateHypothesis(_Immutable):
    """One non-sovereign hypothesis about a presumed referent. Never a world state, a truth,
    an identity decision or a selection; rank and confidence carry no authority."""

    __slots__ = ("hypothesis_kind", "presumed_referent_ref", "content", "material_refs", "modality_label",
                 "contradiction_refs", "unknowns", "rank", "confidence", "hypothesis_id")

    def __init__(self, hypothesis_kind, presumed_referent_ref, material_refs, modality_label, content=None,
                 contradiction_refs=(), unknowns=(), rank=None, confidence=None):
        if not isinstance(hypothesis_kind, str) or hypothesis_kind not in _KINDS:
            _fail("M41_INVALID_KIND", "hypothesis_kind must be STATE_OF_PRESUMED_REFERENT or REFERENT_IDENTITY")
        if not isinstance(presumed_referent_ref, WorldMaterialRef):
            _fail("M41_INVALID_REF", "presumed_referent_ref must be a WorldMaterialRef")
        if content is not None and not isinstance(content, _TypedCognitiveDatum):
            _fail("M41_INVALID_CONTENT", "content must be a TypedCognitiveDatum")
        materials = _ref_collection(material_refs, "material_refs", required=True)
        if not _is_token(modality_label):
            _fail("M41_INVALID_MODALITY", "modality_label must be a namespaced token")
        contradictions = _ref_collection(contradiction_refs, "contradiction_refs", required=False)
        unknown_entries = _unknowns(unknowns)
        _check_rank(rank)
        _check_confidence(confidence)

        preimage = {
            "schema_version": _HYPOTHESIS_SCHEMA,
            "hypothesis_kind": hypothesis_kind,
            "presumed_referent": presumed_referent_ref._canonical(),
            "material_refs": [r._canonical() for r in materials],
            "modality_label": modality_label,
            "contradiction_refs": [r._canonical() for r in contradictions],
            "unknowns": list(unknown_entries),
        }
        if content is not None:
            preimage["content"] = content._canonical()

        object.__setattr__(self, "hypothesis_kind", hypothesis_kind)
        object.__setattr__(self, "presumed_referent_ref", presumed_referent_ref)
        object.__setattr__(self, "content", content)
        object.__setattr__(self, "material_refs", materials)
        object.__setattr__(self, "modality_label", modality_label)
        object.__setattr__(self, "contradiction_refs", contradictions)
        object.__setattr__(self, "unknowns", unknown_entries)
        object.__setattr__(self, "rank", rank)
        object.__setattr__(self, "confidence", confidence)
        object.__setattr__(self, "hypothesis_id", _sha256_id(preimage))

    def __repr__(self):
        return f"WorldStateHypothesis(hypothesis_id={self.hypothesis_id!r}, kind={self.hypothesis_kind!r})"


class WorldHypothesisSet(_Immutable):
    """At least two coexisting hypotheses about one presumed subject. No fusion, selection, ranking,
    supersession, identity resolution or truth; members are ordered by hypothesis_id only."""

    __slots__ = ("subject_ref", "members", "set_id")

    def __init__(self, subject_ref, members):
        if not isinstance(subject_ref, WorldMaterialRef):
            _fail("M41_INVALID_REF", "subject_ref must be a WorldMaterialRef")
        items = _as_sequence(members, "members")
        for item in items:
            if not isinstance(item, WorldStateHypothesis):
                _fail("M41_INVALID_COLLECTION", "members must contain only WorldStateHypothesis")
        if len(items) < 2:
            _fail("M41_INSUFFICIENT_MEMBERS", "a set requires at least two members")
        if len({item.hypothesis_id for item in items}) != len(items):
            _fail("M41_DUPLICATE_MEMBER", "two members have the same hypothesis_id")
        ordered = tuple(sorted(items, key=lambda item: item.hypothesis_id))
        object.__setattr__(self, "subject_ref", subject_ref)
        object.__setattr__(self, "members", ordered)
        object.__setattr__(self, "set_id", _sha256_id({
            "schema_version": _SET_SCHEMA,
            "subject": subject_ref._canonical(),
            "member_ids": [item.hypothesis_id for item in ordered],
        }))

    def __repr__(self):
        return f"WorldHypothesisSet(set_id={self.set_id!r}, members={len(self.members)})"
