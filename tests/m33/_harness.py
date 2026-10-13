"""M33 RED harness (test code only — no M33 runtime behavior is implemented here).

Contents:
1. Runtime access: ``rt()`` imports ``app.reconstruction.m33``; when absent it raises an
   AssertionError("M33 runtime app/reconstruction/m33 is absent (certified RED)") so every
   runtime-dependent test FAILS individually (never a collection error, never a skip).
2. Independent reference ORACLES derived from the certified spec (M33 spec §19 identity
   preimages over M32 canonical JSON incl. RFC 8785 numbers; §21 status merge expectation;
   §24 status precedence expectation). REFERENCE_ORACLE != PRODUCTION_IMPLEMENTATION: these
   compute expected values only; they never produce M33 objects.
3. Static detectors (public-name collisions, forbidden imports, protected-path diff) reused
   from the certified M32 harness where the rule is the same (M32 spec §35 / M33 spec §33–§34).

Constructor calls use keyword arguments only (M33 spec defines field names, not positional order).
Enum members are referenced by name; in identity preimages an enum is serialized as its member
name (the spec lists enum values by name).
"""
from __future__ import annotations

import ast
import enum as enum_mod
import hashlib
import importlib
import json
import unicodedata
from pathlib import Path

from tests.m32 import _harness as M32H

RUNTIME_MODULE = "app.reconstruction.m33"
REPO = M32H.REPO
M33_RUNTIME_DIR = REPO / "app" / "reconstruction" / "m33"
M33_SPEC_BASE = "20bffb2442fac0057318596af79784fef32551b9"
SPEC_FILE = REPO / "docs" / "architecture" / "M33_ARM_RECONSTRUCTION_SPEC_V1.md"
ABSENT_MSG = "M33 runtime app/reconstruction/m33 is absent (certified RED)"

REQUEST_SCHEMA, ITEM_SCHEMA, RELATION_SCHEMA, RESULT_SCHEMA = (
    "m33.request.v1", "m33.item.v1", "m33.relation.v1", "m33.result.v1")
INTEGRATION_VALUES = ("ALREADY_INTEGRATED", "EVOKED_NOT_LOCKED", "ABSENT_IN_SCOPE", "UNDETERMINED")
SUPPORT_KINDS = ("EVIDENCE", "INFERENCE")
STATUS_VALUES = ("RECONSTRUCTED", "PARTIAL", "INSUFFICIENT_MATERIAL", "FAILED_RUNTIME")
ISSUE_KINDS = ("UNRESOLVED_REFERENCE", "CONTRADICTORY_SUPPORT", "AMBIGUOUS_RECONSTRUCTION", "INSUFFICIENT_MATERIAL")
EFFECT_FIELDS = ("memory_write", "emits_act", "b8_mutation", "binder_mutation", "kernel_mutation",
                 "kx108_mutation", "external_io", "durable_state_write")
ERROR_CODES = ("INVALID_MATERIAL", "INVALID_RECONSTRUCTION_REQUEST", "INVALID_DERIVATION",
               "INVALID_RECONSTRUCTION_ITEM", "INVALID_RECONSTRUCTION_RELATION", "INVALID_RECONSTRUCTION_ISSUE",
               "INVALID_CONTRIBUTION", "INVALID_EFFECTS_CONTRACT", "RECONSTRUCTION_BOUND_EXCEEDED",
               "INVALID_SUPPORT_REFERENCE", "DERIVATION_CYCLE", "INVALID_RELATION_REFERENCE",
               "INVALID_INTEGRATION_STATUS", "INVALID_RECONSTRUCTION_RESULT")
PUBLIC_SURFACE = ("ReconstructionMaterial", "ReconstructionBounds", "ReconstructionRequest",
                  "ReconstructionSupportKind", "ReconstructionSupportRef", "ReconstructionSupport",
                  "IntegrationStatus", "ReconstructionItem", "ReconstructionEndpoint", "ReconstructionRelation",
                  "ReconstructionContributor", "ContributionStatus", "ReconstructionContribution",
                  "ReconstructionIssueKind", "ReconstructionIssue", "ReconstructionStatus",
                  "ReconstructionProvenance", "ReconstructionResult", "ReconstructionEffectsContract",
                  "ReconstructionValidationError", "reconstruct", "RECONSTRUCTION_EFFECTS")
SEALED_LAYERS = {"B6": "app/harness/state_explicit", "B7": "app/cognition/b7", "B8": "app/knowledge/b8",
                 "B9": "app/cognition/b9", "M32": "app/primitives/m32"}


# --------------------------------------------------------------------------- runtime access
def rt():
    try:
        return importlib.import_module(RUNTIME_MODULE)
    except ModuleNotFoundError as exc:
        if exc.name and (exc.name == RUNTIME_MODULE or RUNTIME_MODULE.startswith(exc.name)):
            raise AssertionError(ABSENT_MSG) from None
        raise


def m32():
    return importlib.import_module("app.primitives.m32")


def require_runtime_dir():
    assert M33_RUNTIME_DIR.is_dir(), ABSENT_MSG


# --------------------------------------------------------------------------- canonical reference (independent)
def es_number(x) -> str:
    """ECMAScript Number::toString (RFC 8785) from Python's shortest round-trip digits."""
    if isinstance(x, bool):
        raise TypeError
    if isinstance(x, int):
        return str(x)
    if x == 0:
        return "0"
    sign = "-" if x < 0 else ""
    mant, _, exp = repr(abs(x)).partition("e")
    whole, _, frac = mant.partition(".")
    digits = whole + frac
    n = len(whole) + (int(exp) if exp else 0)
    stripped = digits.lstrip("0")
    n -= len(digits) - len(stripped)
    digits = stripped.rstrip("0")
    k = len(digits)
    if k <= n <= 21:
        body = digits + "0" * (n - k)
    elif 0 < n <= 21:
        body = digits[:n] + "." + digits[n:]
    elif -6 < n <= 0:
        body = "0." + "0" * (-n) + digits
    else:
        e = n - 1
        body = (digits if k == 1 else digits[0] + "." + digits[1:]) + "e" + ("+" if e >= 0 else "-") + str(abs(e))
    return sign + body


def plain(v):
    """Convert frozen/immutable equivalents (mappingproxy, tuple, enum) to plain JSON-like values."""
    if isinstance(v, enum_mod.Enum):
        return v.name
    if isinstance(v, str):
        return unicodedata.normalize("NFC", v)
    if isinstance(v, (list, tuple)):
        return [plain(x) for x in v]
    if hasattr(v, "keys") and hasattr(v, "__getitem__"):
        return {unicodedata.normalize("NFC", k): plain(v[k]) for k in v.keys()}
    return v


def canonical_json(v) -> str:
    v = plain(v)
    if v is None:
        return "null"
    if v is True:
        return "true"
    if v is False:
        return "false"
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, (int, float)):
        return es_number(v)
    if isinstance(v, list):
        return "[" + ",".join(canonical_json(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ",".join(json.dumps(k, ensure_ascii=False) + ":" + canonical_json(v[k]) for k in sorted(v)) + "}"
    raise TypeError(type(v).__name__)


def sha(preimage) -> str:
    return hashlib.sha256(canonical_json(preimage).encode("utf-8")).hexdigest()


def datum_obj(d) -> dict:
    """M32 §16 canonical datum object built from an M32 TypedCognitiveDatum's public fields."""
    o = {"datum_type": d.datum_type, "schema_version": d.schema_version, "value": plain(d.value)}
    if getattr(d, "semantic_refs", None) is not None:
        o["semantic_refs"] = list(d.semantic_refs)
    return o


def ref_item_id(item_kind, d) -> str:
    return sha({"content": datum_obj(d), "item_kind": item_kind, "schema_version": ITEM_SCHEMA})


def ref_relation_id(kind, src, tgt) -> str:
    return sha({"relation_kind": kind, "schema_version": RELATION_SCHEMA,
                "source": {"kind": src[0], "ref_id": src[1]}, "target": {"kind": tgt[0], "ref_id": tgt[1]}})


def ref_request_id(kind, materials, bounds, scope_ref=None) -> str:
    """materials: list of (material_id, datum, source_refs)."""
    pre = {"bounds": dict(bounds), "materials": sorted(
        ({"datum": datum_obj(d), "material_id": mid, "source_refs": sorted(set(refs))} for mid, d, refs in materials),
        key=lambda o: o["material_id"]), "reconstruction_kind": kind, "schema_version": REQUEST_SCHEMA}
    if scope_ref is not None:
        pre["inspection_scope_ref"] = scope_ref
    return sha(pre)


def support_obj(kind, refs, derivation=None) -> dict:
    o = {"kind": kind, "refs": sorted(({"ref_id": i, "ref_kind": k} for k, i in set(refs)),
                                      key=lambda r: (r["ref_kind"], r["ref_id"]))}
    if derivation is not None:
        o["derivation"] = derivation
    return o


def issue_obj(kind, subject_ids, detail=None) -> dict:
    o = {"issue_kind": kind, "subject_ids": sorted(set(subject_ids))}
    if detail is not None:
        o["detail"] = detail
    return o


def ref_result_id(request_id, status, items, relations, issues) -> str:
    """items: list of (item_id, integration_status_name, [support_obj]); relations: (relation_id, [support_obj])."""
    def srt(objs):
        return sorted(objs, key=canonical_json)
    return sha({
        "issues": srt(issues),
        "items": sorted(({"integration_status": s, "item_id": i, "supports": srt(sup)} for i, s, sup in items),
                        key=lambda o: o["item_id"]),
        "relations": sorted(({"relation_id": r, "supports": srt(sup)} for r, sup in relations),
                            key=lambda o: o["relation_id"]),
        "request_id": request_id, "schema_version": RESULT_SCHEMA, "status": status})


# --------------------------------------------------------------------------- reference expectations (spec §21, §24)
def expected_merged_status(statuses):
    """§21: equal statuses kept; any difference → UNDETERMINED (+ AMBIGUOUS_RECONSTRUCTION)."""
    s = set(statuses)
    return (next(iter(s)), False) if len(s) == 1 else ("UNDETERMINED", True)


def expected_top_status(any_failed: bool, n_items: int, issue_kinds) -> str:
    """§24, evaluated only after structural validation succeeded."""
    if any_failed:
        return "FAILED_RUNTIME"
    if n_items == 0:
        return "INSUFFICIENT_MATERIAL"
    if set(issue_kinds) & {"UNRESOLVED_REFERENCE", "AMBIGUOUS_RECONSTRUCTION", "INSUFFICIENT_MATERIAL"}:
        return "PARTIAL"
    return "RECONSTRUCTED"


# --------------------------------------------------------------------------- static detectors
def defined_names(root: Path) -> set[str]:
    return M32H.m32_defined_names(root)


def candidate_names(names) -> set[str]:
    return {n for n in names if "Candidate" in n}


def imported_modules(root: Path) -> set[str]:
    mods = set()
    for f in sorted(root.rglob("*.py")):
        tree = ast.parse(f.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                mods |= {a.name for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                mods.add(node.module)
    return mods


# B6 context assembly (§25/R15), B8 (§27/R17), Shazam/periphery (§30), and IO/persistence (§29/R19).
FORBIDDEN_IMPORT_PREFIXES = ("app.harness.state_explicit", "app.knowledge.b8", "periphery", "sqlite3", "socket",
                             "requests", "urllib", "http", "subprocess", "graphiti", "shelve", "pickle")


def forbidden_imports(root: Path) -> set[str]:
    return {m for m in imported_modules(root) if m.startswith(FORBIDDEN_IMPORT_PREFIXES)}


def protected_diff_since_m33_base() -> list[str]:
    out = M32H.git("diff", "--name-only", f"{M33_SPEC_BASE}..HEAD", "--", *M32H.protected_paths())
    return [l for l in out.splitlines() if l.strip()]


# --------------------------------------------------------------------------- object builders (runtime, kwargs only)
def datum(value, datum_type="arm.text", schema="v1", refs=None):
    if refs is None:
        return m32().TypedCognitiveDatum(schema, datum_type, value)
    return m32().TypedCognitiveDatum(schema, datum_type, value, semantic_refs=tuple(refs))


def enum(m, cls, name):
    return getattr(getattr(m, cls), name)


def bounds(m, max_items=50, max_relations=50, max_supports_per_unit=8, max_derivation_depth=4):
    return m.ReconstructionBounds(max_items=max_items, max_relations=max_relations,
                                  max_supports_per_unit=max_supports_per_unit, max_derivation_depth=max_derivation_depth)


def material(m, material_id="mat-1", value="text", source_refs=("src:a",)):
    return m.ReconstructionMaterial(material_id=material_id, datum=datum(value), source_refs=tuple(source_refs))


def request(m, materials, scope_ref="scope:test", kind="arm.reconstruction", b=None):
    kwargs = dict(schema_version=REQUEST_SCHEMA, reconstruction_kind=kind, materials=tuple(materials),
                  bounds=b if b is not None else bounds(m))
    if scope_ref is not None:
        kwargs["inspection_scope_ref"] = scope_ref
    return m.ReconstructionRequest(**kwargs)


def sref(m, ref_kind, ref_id):
    return m.ReconstructionSupportRef(ref_kind=ref_kind, ref_id=ref_id)


def support(m, kind, refs, derivation=None):
    kw = dict(kind=enum(m, "ReconstructionSupportKind", kind), refs=tuple(sref(m, k, i) for k, i in refs))
    if derivation is not None:
        kw["derivation"] = derivation
    return m.ReconstructionSupport(**kw)


def evidence(m, material_id="mat-1"):
    return support(m, "EVIDENCE", [("MATERIAL", material_id)])


def item(m, value="concept A", kind="arm.concept", supports=None, status="EVOKED_NOT_LOCKED"):
    return m.ReconstructionItem(item_kind=kind, content=datum(value), supports=tuple(supports or (evidence(m),)),
                                integration_status=enum(m, "IntegrationStatus", status))


def endpoint(m, kind, ref_id):
    return m.ReconstructionEndpoint(kind=kind, ref_id=ref_id)


def relation(m, src, tgt, kind="arm.related_to", supports=None):
    return m.ReconstructionRelation(relation_kind=kind, source=endpoint(m, *src), target=endpoint(m, *tgt),
                                    supports=tuple(supports or (evidence(m),)))


def issue(m, kind, subject_ids=(), detail=None):
    kw = dict(issue_kind=enum(m, "ReconstructionIssueKind", kind), subject_ids=tuple(subject_ids))
    if detail is not None:
        kw["detail"] = detail
    return m.ReconstructionIssue(**kw)


def contributor(m, **kw):
    kw = kw or {"implementation_id": "impl.a"}
    return m.ReconstructionContributor(**kw)


def contribution(m, cid="c1", items=(), relations=(), issues=(), status="COMPLETED", who=None, diagnostics=()):
    return m.ReconstructionContribution(contribution_id=cid, contributor=who or contributor(m),
                                        status=enum(m, "ContributionStatus", status), items=tuple(items),
                                        relations=tuple(relations), issues=tuple(issues),
                                        diagnostics=tuple(diagnostics))


def raises_code(m, code, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except m.ReconstructionValidationError as exc:
        assert exc.code == code, f"expected {code}, got {exc.code}"
        return exc
    raise AssertionError(f"expected ReconstructionValidationError({code}); nothing raised")
