"""M33 — ARM (Agent Reconstruction Méthodique) V1: bounded typed reconstruction.

Normative source: docs/architecture/M33_ARM_RECONSTRUCTION_SPEC_V1.md (certified), under
docs/architecture/M33_ARM_RECONSTRUCTION_DOCTRINE_V1.md and COGNITIVE_FOUNDATION_V1.
Advisory only: no memory write, no ACT, no B8/Binder/kernel/KX108 mutation, no external IO,
no durable state. M32 is the typed substrate (canonical JSON and datum contract are reused).
"""
import re as _re
import unicodedata as _unicodedata
from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum

import app.primitives.m32 as _m32

_REQUEST_SCHEMA = "m33.request.v1"
_ITEM_SCHEMA = "m33.item.v1"
_RELATION_SCHEMA = "m33.relation.v1"
_RESULT_SCHEMA = "m33.result.v1"
_KIND_RE = _re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")
_HEX64_RE = _re.compile(r"^[0-9a-f]{64}$")
_MAX_BOUND = 2 ** 53 - 1
_CONTRADICTS = "arm.contradicts"


class ReconstructionValidationError(Exception):
    """Fail-closed structural rejection (spec §8, §23). Never a status, never semantic FALSE."""

    def __init__(self, code, message="", field_path=None):
        super().__init__(f"{code}: {message}" if message else code)
        self.code, self.message, self.field_path = code, message, field_path


def _fail(code, message="", field_path=None):
    raise ReconstructionValidationError(code, message, field_path)


def _nfc(s):
    return _unicodedata.normalize("NFC", s)


def _is_opaque(v):
    return isinstance(v, str) and v != "" and v == v.strip()


def _is_kind(v):
    return isinstance(v, str) and _KIND_RE.match(_nfc(v)) is not None


def _is_hex(v):
    return isinstance(v, str) and _HEX64_RE.match(v) is not None


def _canon(obj):
    """M32 canonical JSON text (spec §19 reuses M32 §15)."""
    return _m32._serialize(_m32._freeze(obj, "NON_CANONICAL_VALUE"))


def _sha(obj):
    return _m32._sha256_hex(_m32._freeze(obj, "NON_CANONICAL_VALUE"))


def _set(obj, **fields):
    for k, v in fields.items():
        object.__setattr__(obj, k, v)


def _seq(v):
    return isinstance(v, (tuple, list))


# --------------------------------------------------------------------------- enums (values equal member names)
class ReconstructionSupportKind(_Enum):
    EVIDENCE = "EVIDENCE"
    INFERENCE = "INFERENCE"


class IntegrationStatus(_Enum):
    ALREADY_INTEGRATED = "ALREADY_INTEGRATED"
    EVOKED_NOT_LOCKED = "EVOKED_NOT_LOCKED"
    ABSENT_IN_SCOPE = "ABSENT_IN_SCOPE"
    UNDETERMINED = "UNDETERMINED"


class ContributionStatus(_Enum):
    COMPLETED = "COMPLETED"
    FAILED_RUNTIME = "FAILED_RUNTIME"


class ReconstructionIssueKind(_Enum):
    UNRESOLVED_REFERENCE = "UNRESOLVED_REFERENCE"
    CONTRADICTORY_SUPPORT = "CONTRADICTORY_SUPPORT"
    AMBIGUOUS_RECONSTRUCTION = "AMBIGUOUS_RECONSTRUCTION"
    INSUFFICIENT_MATERIAL = "INSUFFICIENT_MATERIAL"


class ReconstructionStatus(_Enum):
    RECONSTRUCTED = "RECONSTRUCTED"
    PARTIAL = "PARTIAL"
    INSUFFICIENT_MATERIAL = "INSUFFICIENT_MATERIAL"
    FAILED_RUNTIME = "FAILED_RUNTIME"


_PARTIAL_ISSUES = {ReconstructionIssueKind.UNRESOLVED_REFERENCE, ReconstructionIssueKind.AMBIGUOUS_RECONSTRUCTION,
                   ReconstructionIssueKind.INSUFFICIENT_MATERIAL}


# --------------------------------------------------------------------------- effects (§16)
_EFFECT_FIELDS = ("memory_write", "emits_act", "b8_mutation", "binder_mutation", "kernel_mutation",
                  "kx108_mutation", "external_io", "durable_state_write")


@_dataclass(frozen=True, init=False)
class ReconstructionEffectsContract:
    memory_write: bool
    emits_act: bool
    b8_mutation: bool
    binder_mutation: bool
    kernel_mutation: bool
    kx108_mutation: bool
    external_io: bool
    durable_state_write: bool

    def __init__(self, memory_write=False, emits_act=False, b8_mutation=False, binder_mutation=False,
                 kernel_mutation=False, kx108_mutation=False, external_io=False, durable_state_write=False):
        values = dict(memory_write=memory_write, emits_act=emits_act, b8_mutation=b8_mutation,
                      binder_mutation=binder_mutation, kernel_mutation=kernel_mutation, kx108_mutation=kx108_mutation,
                      external_io=external_io, durable_state_write=durable_state_write)
        for k, v in values.items():
            if v is not False:
                _fail("INVALID_EFFECTS_CONTRACT", f"{k} must be False in M33 V1", k)
        _set(self, **values)


RECONSTRUCTION_EFFECTS = ReconstructionEffectsContract()


# --------------------------------------------------------------------------- material / bounds / request (§9–§11)
@_dataclass(frozen=True, init=False)
class ReconstructionMaterial:
    material_id: str
    datum: object
    source_refs: tuple
    context_origin: object = None

    def __init__(self, material_id, datum, source_refs=(), context_origin=None):
        if not _is_opaque(material_id):
            _fail("INVALID_MATERIAL", "material_id must be an opaque non-empty string", "material_id")
        if not isinstance(datum, _m32.TypedCognitiveDatum):
            _fail("INVALID_MATERIAL", "datum must be an M32 TypedCognitiveDatum", "datum")
        if not _seq(source_refs) or not all(_is_opaque(r) for r in source_refs):
            _fail("INVALID_MATERIAL", "source_refs must be opaque strings", "source_refs")
        if context_origin is not None and not _is_opaque(context_origin):
            _fail("INVALID_MATERIAL", "context_origin must be an opaque string", "context_origin")
        _set(self, material_id=_nfc(material_id), datum=datum,
             source_refs=tuple(sorted({_nfc(r) for r in source_refs})),
             context_origin=None if context_origin is None else _nfc(context_origin))

    def _canonical(self):
        return {"datum": self.datum._canonical(), "material_id": self.material_id, "source_refs": list(self.source_refs)}


@_dataclass(frozen=True, init=False)
class ReconstructionBounds:
    max_items: int
    max_relations: int
    max_supports_per_unit: int
    max_derivation_depth: int

    def __init__(self, max_items, max_relations, max_supports_per_unit, max_derivation_depth):
        values = dict(max_items=max_items, max_relations=max_relations, max_supports_per_unit=max_supports_per_unit,
                      max_derivation_depth=max_derivation_depth)
        for k, v in values.items():
            if type(v) is not int or not 1 <= v <= _MAX_BOUND:
                _fail("INVALID_RECONSTRUCTION_REQUEST", f"{k} must be an int in [1, 2^53-1]", k)
        _set(self, **values)

    def _canonical(self):
        return {"max_derivation_depth": self.max_derivation_depth, "max_items": self.max_items,
                "max_relations": self.max_relations, "max_supports_per_unit": self.max_supports_per_unit}


@_dataclass(frozen=True, init=False)
class ReconstructionRequest:
    schema_version: str
    reconstruction_kind: str
    materials: tuple
    bounds: ReconstructionBounds
    inspection_scope_ref: object
    request_id: str

    def __init__(self, schema_version, reconstruction_kind, materials, bounds, inspection_scope_ref=None):
        if schema_version != _REQUEST_SCHEMA:
            _fail("INVALID_RECONSTRUCTION_REQUEST", "schema_version must be m33.request.v1", "schema_version")
        if not _is_kind(reconstruction_kind):
            _fail("INVALID_RECONSTRUCTION_REQUEST", "reconstruction_kind must be namespaced", "reconstruction_kind")
        if not _seq(materials) or not all(isinstance(x, ReconstructionMaterial) for x in materials):
            _fail("INVALID_RECONSTRUCTION_REQUEST", "materials must be ReconstructionMaterial", "materials")
        ids = [x.material_id for x in materials]
        if len(set(ids)) != len(ids):
            _fail("INVALID_RECONSTRUCTION_REQUEST", "material_id values must be unique", "materials")
        if not isinstance(bounds, ReconstructionBounds):
            _fail("INVALID_RECONSTRUCTION_REQUEST", "bounds must be ReconstructionBounds", "bounds")
        if inspection_scope_ref is not None and not _is_opaque(inspection_scope_ref):
            _fail("INVALID_RECONSTRUCTION_REQUEST", "inspection_scope_ref must be opaque", "inspection_scope_ref")
        mats = tuple(sorted(materials, key=lambda x: x.material_id))
        ref = None if inspection_scope_ref is None else _nfc(inspection_scope_ref)
        pre = {"bounds": bounds._canonical(), "materials": [x._canonical() for x in mats],
               "reconstruction_kind": _nfc(reconstruction_kind), "schema_version": _REQUEST_SCHEMA}
        if ref is not None:
            pre["inspection_scope_ref"] = ref
        _set(self, schema_version=_REQUEST_SCHEMA, reconstruction_kind=_nfc(reconstruction_kind), materials=mats,
             bounds=bounds, inspection_scope_ref=ref, request_id=_sha(pre))


# --------------------------------------------------------------------------- support (§13)
_SUPPORT_REF_KINDS = ("MATERIAL", "SOURCE", "ITEM")


@_dataclass(frozen=True, init=False)
class ReconstructionSupportRef:
    ref_kind: str
    ref_id: str

    def __init__(self, ref_kind, ref_id):
        if ref_kind not in _SUPPORT_REF_KINDS:
            _fail("INVALID_DERIVATION", "ref_kind must be MATERIAL, SOURCE or ITEM", "ref_kind")
        if (ref_kind == "ITEM" and not _is_hex(ref_id)) or (ref_kind != "ITEM" and not _is_opaque(ref_id)):
            _fail("INVALID_DERIVATION", "invalid ref_id for ref_kind", "ref_id")
        _set(self, ref_kind=ref_kind, ref_id=_nfc(ref_id))


@_dataclass(frozen=True, init=False)
class ReconstructionSupport:
    kind: ReconstructionSupportKind
    refs: tuple
    derivation: object = None

    def __init__(self, kind, refs, derivation=None):
        if not isinstance(kind, ReconstructionSupportKind):
            _fail("INVALID_DERIVATION", "kind must be ReconstructionSupportKind", "kind")
        if not _seq(refs) or not refs or not all(isinstance(r, ReconstructionSupportRef) for r in refs):
            _fail("INVALID_DERIVATION", "refs must be a non-empty sequence of ReconstructionSupportRef", "refs")
        allowed = {"MATERIAL", "SOURCE"} if kind is ReconstructionSupportKind.EVIDENCE else {"MATERIAL", "ITEM"}
        if any(r.ref_kind not in allowed for r in refs):
            _fail("INVALID_DERIVATION", f"{kind.name} support cannot reference these ref kinds", "refs")
        if derivation is not None and not _is_kind(derivation):
            _fail("INVALID_DERIVATION", "derivation must be a namespaced label", "derivation")
        uniq = {(r.ref_kind, r.ref_id): r for r in refs}
        _set(self, kind=kind, refs=tuple(uniq[k] for k in sorted(uniq)),
             derivation=None if derivation is None else _nfc(derivation))

    def _canonical(self):
        o = {"kind": self.kind.name, "refs": [{"ref_id": r.ref_id, "ref_kind": r.ref_kind} for r in self.refs]}
        if self.derivation is not None:
            o["derivation"] = self.derivation
        return o


def _sorted_supports(supports):
    uniq = {_canon(s._canonical()): s for s in supports}
    return tuple(uniq[k] for k in sorted(uniq))


# --------------------------------------------------------------------------- item / relation (§14)
@_dataclass(frozen=True, init=False)
class ReconstructionItem:
    item_kind: str
    content: object
    supports: tuple
    integration_status: IntegrationStatus
    item_id: str

    def __init__(self, item_kind, content, supports, integration_status):
        if not _is_kind(item_kind):
            _fail("INVALID_RECONSTRUCTION_ITEM", "item_kind must be namespaced", "item_kind")
        if not isinstance(content, _m32.TypedCognitiveDatum):
            _fail("INVALID_RECONSTRUCTION_ITEM", "content must be an M32 TypedCognitiveDatum", "content")
        if not _seq(supports) or not supports or not all(isinstance(s, ReconstructionSupport) for s in supports):
            _fail("INVALID_RECONSTRUCTION_ITEM", "supports must be a non-empty sequence of ReconstructionSupport", "supports")
        if not isinstance(integration_status, IntegrationStatus):
            _fail("INVALID_RECONSTRUCTION_ITEM", "integration_status must be IntegrationStatus", "integration_status")
        kind = _nfc(item_kind)
        _set(self, item_kind=kind, content=content, supports=_sorted_supports(supports),
             integration_status=integration_status,
             item_id=_sha({"content": content._canonical(), "item_kind": kind, "schema_version": _ITEM_SCHEMA}))


_ENDPOINT_KINDS = ("MATERIAL", "ITEM")


@_dataclass(frozen=True, init=False)
class ReconstructionEndpoint:
    kind: str
    ref_id: str

    def __init__(self, kind, ref_id):
        if kind not in _ENDPOINT_KINDS:
            _fail("INVALID_RECONSTRUCTION_RELATION", "endpoint kind must be MATERIAL or ITEM", "kind")
        if (kind == "ITEM" and not _is_hex(ref_id)) or (kind == "MATERIAL" and not _is_opaque(ref_id)):
            _fail("INVALID_RECONSTRUCTION_RELATION", "invalid endpoint ref_id", "ref_id")
        _set(self, kind=kind, ref_id=_nfc(ref_id))


@_dataclass(frozen=True, init=False)
class ReconstructionRelation:
    relation_kind: str
    source: ReconstructionEndpoint
    target: ReconstructionEndpoint
    supports: tuple
    relation_id: str

    def __init__(self, relation_kind, source, target, supports):
        if not _is_kind(relation_kind):
            _fail("INVALID_RECONSTRUCTION_RELATION", "relation_kind must be namespaced", "relation_kind")
        if not isinstance(source, ReconstructionEndpoint) or not isinstance(target, ReconstructionEndpoint):
            _fail("INVALID_RECONSTRUCTION_RELATION", "source/target must be ReconstructionEndpoint")
        if (source.kind, source.ref_id) == (target.kind, target.ref_id):
            _fail("INVALID_RECONSTRUCTION_RELATION", "source and target must differ")
        if not _seq(supports) or not supports or not all(isinstance(s, ReconstructionSupport) for s in supports):
            _fail("INVALID_RECONSTRUCTION_RELATION", "supports must be non-empty", "supports")
        kind = _nfc(relation_kind)
        pre = {"relation_kind": kind, "schema_version": _RELATION_SCHEMA,
               "source": {"kind": source.kind, "ref_id": source.ref_id},
               "target": {"kind": target.kind, "ref_id": target.ref_id}}
        _set(self, relation_kind=kind, source=source, target=target, supports=_sorted_supports(supports),
             relation_id=_sha(pre))


# --------------------------------------------------------------------------- issues (§17)
@_dataclass(frozen=True, init=False)
class ReconstructionIssue:
    issue_kind: ReconstructionIssueKind
    subject_ids: tuple
    detail: object = None

    def __init__(self, issue_kind, subject_ids=(), detail=None):
        if not isinstance(issue_kind, ReconstructionIssueKind):
            _fail("INVALID_RECONSTRUCTION_ISSUE", "issue_kind must be ReconstructionIssueKind", "issue_kind")
        if not _seq(subject_ids) or not all(_is_opaque(s) for s in subject_ids):
            _fail("INVALID_RECONSTRUCTION_ISSUE", "subject_ids must be opaque strings", "subject_ids")
        if detail is not None and not _is_kind(detail):
            _fail("INVALID_RECONSTRUCTION_ISSUE", "detail must be a namespaced label", "detail")
        _set(self, issue_kind=issue_kind, subject_ids=tuple(sorted({_nfc(s) for s in subject_ids})),
             detail=None if detail is None else _nfc(detail))

    def _canonical(self):
        o = {"issue_kind": self.issue_kind.name, "subject_ids": list(self.subject_ids)}
        if self.detail is not None:
            o["detail"] = self.detail
        return o


def _sorted_issues(issues):
    uniq = {_canon(i._canonical()): i for i in issues}
    return tuple(uniq[k] for k in sorted(uniq))


# --------------------------------------------------------------------------- contributions (§15)
_CONTRIBUTOR_FIELDS = ("role_ref", "implementation_id", "provider_id", "model_id", "primitive_invocation_id")


@_dataclass(frozen=True, init=False)
class ReconstructionContributor:
    role_ref: object = None
    implementation_id: object = None
    provider_id: object = None
    model_id: object = None
    primitive_invocation_id: object = None

    def __init__(self, role_ref=None, implementation_id=None, provider_id=None, model_id=None,
                 primitive_invocation_id=None):
        values = dict(role_ref=role_ref, implementation_id=implementation_id, provider_id=provider_id,
                      model_id=model_id, primitive_invocation_id=primitive_invocation_id)
        if all(v is None for v in values.values()):
            _fail("INVALID_CONTRIBUTION", "a contributor needs at least one identifying field")
        for k, v in values.items():
            if v is None:
                continue
            ok = _is_hex(v) if k == "primitive_invocation_id" else _is_opaque(v)
            if not ok:
                _fail("INVALID_CONTRIBUTION", f"invalid {k}", k)
        _set(self, **{k: (None if v is None else _nfc(v)) for k, v in values.items()})

    def _canonical(self):
        return {k: getattr(self, k) for k in _CONTRIBUTOR_FIELDS if getattr(self, k) is not None}


@_dataclass(frozen=True, init=False)
class ReconstructionContribution:
    contribution_id: str
    contributor: ReconstructionContributor
    status: ContributionStatus
    items: tuple
    relations: tuple
    issues: tuple
    diagnostics: tuple

    def __init__(self, contribution_id, contributor, status, items=(), relations=(), issues=(), diagnostics=()):
        if not _is_opaque(contribution_id):
            _fail("INVALID_CONTRIBUTION", "contribution_id must be opaque", "contribution_id")
        if not isinstance(contributor, ReconstructionContributor):
            _fail("INVALID_CONTRIBUTION", "contributor must be ReconstructionContributor", "contributor")
        if not isinstance(status, ContributionStatus):
            _fail("INVALID_CONTRIBUTION", "status must be ContributionStatus", "status")
        for name, seq, cls in (("items", items, ReconstructionItem), ("relations", relations, ReconstructionRelation),
                               ("issues", issues, ReconstructionIssue)):
            if not _seq(seq) or not all(isinstance(x, cls) for x in seq):
                _fail("INVALID_CONTRIBUTION", f"{name} must contain {cls.__name__}", name)
        if not _seq(diagnostics) or not all(isinstance(d, str) for d in diagnostics):
            _fail("INVALID_CONTRIBUTION", "diagnostics must be strings", "diagnostics")
        if status is ContributionStatus.FAILED_RUNTIME and (items or relations):
            _fail("INVALID_CONTRIBUTION", "a FAILED_RUNTIME contribution carries no items or relations")
        _set(self, contribution_id=_nfc(contribution_id), contributor=contributor, status=status,
             items=tuple(items), relations=tuple(relations), issues=tuple(issues), diagnostics=tuple(diagnostics))


# --------------------------------------------------------------------------- provenance / result (§18, §19, §24)
@_dataclass(frozen=True)
class ReconstructionProvenance:
    request_id: str
    contribution_ids: tuple
    contributors: tuple
    source_refs: tuple
    derived_from_material_ids: tuple
    derived_from_item_ids: tuple
    diagnostics: tuple


@_dataclass(frozen=True, init=False)
class ReconstructionResult:
    schema_version: str
    reconstruction_id: str
    request_id: str
    status: ReconstructionStatus
    items: tuple
    relations: tuple
    issues: tuple
    provenance: ReconstructionProvenance
    effects: ReconstructionEffectsContract

    def __init__(self, schema_version, request_id, status, items, relations, issues, provenance,
                 effects=RECONSTRUCTION_EFFECTS):
        bad = "INVALID_RECONSTRUCTION_RESULT"
        if schema_version != _RESULT_SCHEMA:
            _fail(bad, "schema_version must be m33.result.v1", "schema_version")
        if not _is_hex(request_id):
            _fail(bad, "request_id must be 64 lowercase hex", "request_id")
        if not isinstance(status, ReconstructionStatus):
            _fail(bad, "status must be ReconstructionStatus", "status")
        for name, seq, cls in (("items", items, ReconstructionItem), ("relations", relations, ReconstructionRelation),
                               ("issues", issues, ReconstructionIssue)):
            if not _seq(seq) or not all(isinstance(x, cls) for x in seq):
                _fail(bad, f"{name} must contain {cls.__name__}", name)
        if not isinstance(provenance, ReconstructionProvenance):
            _fail(bad, "provenance must be ReconstructionProvenance", "provenance")
        if not isinstance(effects, ReconstructionEffectsContract):
            _fail(bad, "effects must be ReconstructionEffectsContract", "effects")
        kinds = {i.issue_kind for i in issues}
        if status is ReconstructionStatus.FAILED_RUNTIME and (items or relations or issues):
            _fail(bad, "FAILED_RUNTIME carries no items, relations or issues", "status")
        if status is ReconstructionStatus.INSUFFICIENT_MATERIAL and items:
            _fail(bad, "INSUFFICIENT_MATERIAL carries no items", "status")
        if status in (ReconstructionStatus.RECONSTRUCTED, ReconstructionStatus.PARTIAL) and not items:
            _fail(bad, f"{status.name} requires at least one item", "status")
        if status is ReconstructionStatus.PARTIAL and not kinds & _PARTIAL_ISSUES:
            _fail(bad, "PARTIAL requires an unresolved, ambiguous or insufficient-material issue", "status")
        if status is ReconstructionStatus.RECONSTRUCTED and kinds & _PARTIAL_ISSUES:
            _fail(bad, "RECONSTRUCTED cannot carry partial issues", "status")
        items = tuple(sorted(items, key=lambda i: i.item_id))
        relations = tuple(sorted(relations, key=lambda r: r.relation_id))
        issues = _sorted_issues(issues)
        pre = {
            "issues": [i._canonical() for i in issues],
            "items": [{"integration_status": i.integration_status.name, "item_id": i.item_id,
                       "supports": [s._canonical() for s in i.supports]} for i in items],
            "relations": [{"relation_id": r.relation_id, "supports": [s._canonical() for s in r.supports]}
                          for r in relations],
            "request_id": request_id, "schema_version": _RESULT_SCHEMA, "status": status.name}
        _set(self, schema_version=_RESULT_SCHEMA, reconstruction_id=_sha(pre), request_id=request_id, status=status,
             items=items, relations=relations, issues=issues, provenance=provenance, effects=effects)


# --------------------------------------------------------------------------- reconstruct (§22, §24)
def _derivation_depth_check(items_by_id, max_depth):
    edges = {iid: sorted({r.ref_id for s in it.supports if s.kind is ReconstructionSupportKind.INFERENCE
                          for r in s.refs if r.ref_kind == "ITEM"}) for iid, it in items_by_id.items()}
    state, depth = {}, {}

    def visit(node):
        if state.get(node) == 1:
            _fail("DERIVATION_CYCLE", "derivation dependency cycle", node)
        if state.get(node) == 2:
            return depth[node]
        state[node] = 1
        d = 0
        for nxt in edges.get(node, ()):
            d = max(d, 1 + visit(nxt))
        state[node] = 2
        depth[node] = d
        return d

    for node in sorted(edges):
        visit(node)
    if depth and max(depth.values()) > max_depth:
        _fail("RECONSTRUCTION_BOUND_EXCEEDED", "derivation depth exceeds max_derivation_depth")


def _validate_and_merge(request, contributions):
    # Steps 1–8 (structural validation; raise only).
    if not isinstance(request, ReconstructionRequest):
        _fail("INVALID_RECONSTRUCTION_REQUEST", "request must be a ReconstructionRequest")
    if not _seq(contributions) or not all(isinstance(c, ReconstructionContribution) for c in contributions):
        _fail("INVALID_CONTRIBUTION", "contributions must be ReconstructionContribution instances")
    ids = [c.contribution_id for c in contributions]
    if len(set(ids)) != len(ids):
        _fail("INVALID_CONTRIBUTION", "contribution_id values must be unique")
    if request.inspection_scope_ref is None:
        for c in contributions:
            for it in c.items:
                if it.integration_status is IntegrationStatus.ABSENT_IN_SCOPE:
                    _fail("INVALID_INTEGRATION_STATUS", "ABSENT_IN_SCOPE requires inspection_scope_ref", it.item_id)
    items, statuses, relations, issues = {}, {}, {}, []
    for c in sorted(contributions, key=lambda x: x.contribution_id):
        if c.status is not ContributionStatus.COMPLETED:
            continue
        for it in c.items:
            prev = items.get(it.item_id)
            items[it.item_id] = it if prev is None else ReconstructionItem(
                item_kind=it.item_kind, content=it.content, supports=prev.supports + it.supports,
                integration_status=prev.integration_status)
            statuses.setdefault(it.item_id, set()).add(it.integration_status)
        for rel in c.relations:
            prev = relations.get(rel.relation_id)
            relations[rel.relation_id] = rel if prev is None else ReconstructionRelation(
                relation_kind=rel.relation_kind, source=rel.source, target=rel.target,
                supports=prev.supports + rel.supports)
        issues.extend(c.issues)
    b = request.bounds
    if len(items) > b.max_items or len(relations) > b.max_relations:
        _fail("RECONSTRUCTION_BOUND_EXCEEDED", "too many items or relations")
    if any(len(u.supports) > b.max_supports_per_unit for u in list(items.values()) + list(relations.values())):
        _fail("RECONSTRUCTION_BOUND_EXCEEDED", "too many supports on a merged unit")
    material_ids = {m.material_id for m in request.materials}
    source_refs = {s for m in request.materials for s in m.source_refs}
    targets = {"MATERIAL": material_ids, "SOURCE": source_refs, "ITEM": set(items)}
    for unit in list(items.values()) + list(relations.values()):
        for s in unit.supports:
            for r in s.refs:
                if r.ref_id not in targets[r.ref_kind]:
                    _fail("INVALID_SUPPORT_REFERENCE", f"unresolved {r.ref_kind} reference", r.ref_id)
    _derivation_depth_check(items, b.max_derivation_depth)
    for rel in relations.values():
        for ep in (rel.source, rel.target):
            if ep.ref_id not in (material_ids if ep.kind == "MATERIAL" else set(items)):
                _fail("INVALID_RELATION_REFERENCE", f"unresolved {ep.kind} endpoint", ep.ref_id)
    return items, statuses, relations, issues, material_ids, source_refs


def _provenance(request, contributions, items, relations, failed):
    mats, derived_items = set(), set()
    if not failed:
        for unit in list(items) + list(relations):
            for s in unit.supports:
                for r in s.refs:
                    if r.ref_kind == "MATERIAL":
                        mats.add(r.ref_id)
                    elif r.ref_kind == "ITEM":
                        derived_items.add(r.ref_id)
        for rel in relations:
            for ep in (rel.source, rel.target):
                if ep.kind == "MATERIAL":
                    mats.add(ep.ref_id)
    contributors = tuple(sorted((c.contributor for c in contributions), key=lambda x: _canon(x._canonical())))
    diagnostics = tuple(d for c in sorted(contributions, key=lambda x: x.contribution_id) for d in c.diagnostics)
    return ReconstructionProvenance(
        request_id=request.request_id, contribution_ids=tuple(sorted(c.contribution_id for c in contributions)),
        contributors=contributors, source_refs=tuple(sorted({s for m in request.materials for s in m.source_refs})),
        derived_from_material_ids=tuple(sorted(mats)), derived_from_item_ids=tuple(sorted(derived_items)),
        diagnostics=diagnostics)


def reconstruct(request, contributions):
    """Bounded typed reconstruction (§22). Validation (steps 1–8) always precedes runtime status (step 9)."""
    contributions = tuple(contributions) if isinstance(contributions, list) else contributions
    items, statuses, relations, issues, _mats, _srcs = _validate_and_merge(request, contributions)
    failed = any(c.status is ContributionStatus.FAILED_RUNTIME for c in contributions)
    if not failed:
        try:
            final_items, final_issues = [], list(issues)
            for iid in sorted(items):
                it, sts = items[iid], statuses[iid]
                status = next(iter(sts)) if len(sts) == 1 else IntegrationStatus.UNDETERMINED
                if len(sts) > 1:
                    final_issues.append(ReconstructionIssue(
                        issue_kind=ReconstructionIssueKind.AMBIGUOUS_RECONSTRUCTION, subject_ids=(iid,)))
                final_items.append(it if status is it.integration_status else ReconstructionItem(
                    item_kind=it.item_kind, content=it.content, supports=it.supports, integration_status=status))
            final_relations = [relations[r] for r in sorted(relations)]
            for rel in final_relations:
                if rel.relation_kind == _CONTRADICTS:
                    final_issues.append(ReconstructionIssue(
                        issue_kind=ReconstructionIssueKind.CONTRADICTORY_SUPPORT,
                        subject_ids=(rel.source.ref_id, rel.target.ref_id)))
            kinds = {i.issue_kind for i in final_issues}
            if not final_items:
                top = ReconstructionStatus.INSUFFICIENT_MATERIAL
            elif kinds & _PARTIAL_ISSUES:
                top = ReconstructionStatus.PARTIAL
            else:
                top = ReconstructionStatus.RECONSTRUCTED
            prov = _provenance(request, contributions, final_items, final_relations, False)
            return ReconstructionResult(schema_version=_RESULT_SCHEMA, request_id=request.request_id, status=top,
                                        items=tuple(final_items), relations=tuple(final_relations),
                                        issues=tuple(final_issues), provenance=prov)
        except ReconstructionValidationError:
            raise
        except Exception:  # unexpected internal failure after validation (§22 steps 9–11)
            pass
    prov = _provenance(request, contributions, (), (), True)
    return ReconstructionResult(schema_version=_RESULT_SCHEMA, request_id=request.request_id,
                                status=ReconstructionStatus.FAILED_RUNTIME, items=(), relations=(), issues=(),
                                provenance=prov)
