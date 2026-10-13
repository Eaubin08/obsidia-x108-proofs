"""M32 — common cognitive primitive substrate (V1, SUBSTRATE_ONLY, CORE_PRIMITIVE_COUNT=0).

Normative source: docs/architecture/M32_COMMON_COGNITIVE_PRIMITIVES_SPEC_V1.md (§§14–36).
Lives outside the sealed foundation (§14). No memory write, no ACT, no kernel/Binder/KX108/B8
mutation, no authority: DECISION_AUTHORITY=KX108_ONLY.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from dataclasses import dataclass, field, fields
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Mapping, Optional

INVOCATION_SCHEMA = "m32.invocation.v1"
RESULT_SCHEMA = "m32.result.v1"
TYPE_SPEC_SCHEMA = "m32.primitive_type_spec.v1"
_MAX_SAFE_INT = 2 ** 53 - 1
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_SCOPES = ("TEST_REGISTRY", "PRODUCTION_REGISTRY")
_EFFECT_FLAGS = ("memory_write", "emits_act", "b8_mutation", "binder_mutation", "kernel_mutation", "kx108_mutation")


class InvocationValidationError(Exception):
    """Fail-closed rejection (§21-A, §33). A code never means semantic FALSE."""

    def __init__(self, code: str, message: str = "", field_path: Optional[str] = None):
        super().__init__(f"{code}: {message}" if message else code)
        self.code, self.message, self.field_path = code, message, field_path


def _fail(code: str, message: str = "", field_path: Optional[str] = None):
    raise InvocationValidationError(code, message, field_path)


def _nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def _is_nonempty_str(v) -> bool:
    return isinstance(v, str) and v != ""


# ---------------------------------------------------------------- canonical values (§15)
def _freeze(value, code: str, path: str = "$"):
    """Validate a CanonicalValue and return an immutable, NFC-normalized deep copy."""
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, str):
        return _nfc(value)
    if isinstance(value, int):
        if abs(value) > _MAX_SAFE_INT:
            _fail(code, "integer outside ±(2^53−1)", path)
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            _fail(code, "non-finite number", path)
        return 0.0 if value == 0 else value
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(v, code, f"{path}[{i}]") for i, v in enumerate(value))
    if isinstance(value, Mapping):
        out = {}
        for k, v in value.items():
            if not isinstance(k, str):
                _fail(code, "non-string object key", path)
            nk = _nfc(k)
            if nk in out:
                _fail(code, "object keys collide after NFC", path)
            out[nk] = _freeze(v, code, f"{path}.{nk}")
        return MappingProxyType(dict(sorted(out.items())))
    _fail(code, f"non-canonical value of type {type(value).__name__}", path)


def _number_text(n) -> str:
    if isinstance(n, int):
        return str(n)
    if n == 0:
        return "0"
    if n.is_integer() and abs(n) < 1e21:
        return str(int(n))
    return repr(n)


def _jsonable(value):
    if isinstance(value, Mapping):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [_jsonable(v) for v in value]
    return value


def _serialize(value) -> str:
    """§15 canonical JSON text (input already frozen / NFC)."""
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, (int, float)):
        return _number_text(value)
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(_serialize(v) for v in value) + "]"
    if isinstance(value, Mapping):
        return "{" + ",".join(json.dumps(k, ensure_ascii=False) + ":" + _serialize(value[k])
                              for k in sorted(value)) + "}"
    raise TypeError(type(value).__name__)


def _sha256_hex(value) -> str:
    return hashlib.sha256(_serialize(value).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- datum & bindings (§16, §18, §32 B–C)
_ABSENT = None


@dataclass(frozen=True, init=False)
class TypedCognitiveDatum:
    schema_version: str
    datum_type: str
    value: Any
    semantic_refs: Optional[tuple] = None

    def __init__(self, schema_version, datum_type, value, semantic_refs=_ABSENT):
        if not _is_nonempty_str(schema_version):
            _fail("INVALID_DATUM_SCHEMA", "schema_version must be a non-empty string")
        if not _is_nonempty_str(datum_type):
            _fail("INVALID_DATUM_TYPE", "datum_type must be a non-empty string")
        frozen = _freeze(value, "NON_CANONICAL_VALUE")
        refs = _ABSENT
        if semantic_refs is not _ABSENT:
            if isinstance(semantic_refs, (str, bytes)) or not isinstance(semantic_refs, (list, tuple)):
                _fail("NON_CANONICAL_VALUE", "semantic_refs must be a sequence of strings")
            if not all(_is_nonempty_str(r) for r in semantic_refs):
                _fail("NON_CANONICAL_VALUE", "semantic_refs entries must be non-empty strings")
            refs = tuple(_nfc(r) for r in semantic_refs)
        object.__setattr__(self, "schema_version", _nfc(schema_version))
        object.__setattr__(self, "datum_type", _nfc(datum_type))
        object.__setattr__(self, "value", frozen)
        object.__setattr__(self, "semantic_refs", refs)

    def _canonical(self):
        d = {"datum_type": self.datum_type, "schema_version": self.schema_version, "value": self.value}
        if self.semantic_refs is not _ABSENT:
            d["semantic_refs"] = self.semantic_refs
        return d


@dataclass(frozen=True, init=False)
class PrimitiveInputBinding:
    slot_name: str
    datum: TypedCognitiveDatum

    def __init__(self, slot_name, datum):
        if not _is_nonempty_str(slot_name):
            _fail("INVALID_BINDING", "slot_name must be a non-empty string")
        if not isinstance(datum, TypedCognitiveDatum):
            _fail("INVALID_BINDING", "datum must be a TypedCognitiveDatum")
        object.__setattr__(self, "slot_name", _nfc(slot_name))
        object.__setattr__(self, "datum", datum)

    def _canonical(self):
        return {"datum": self.datum._canonical(), "slot_name": self.slot_name}


# ---------------------------------------------------------------- type spec parts (§17)
@dataclass(frozen=True)
class InputSlotSpec:
    slot_name: str
    datum_type: str
    datum_schema_version: str
    required: bool


@dataclass(frozen=True)
class DatumTypeRef:
    datum_type: str
    datum_schema_version: str


@dataclass(frozen=True)
class ConfigFieldSpec:
    name: str
    value_kind: str
    required: bool


@dataclass(frozen=True)
class ConfigSchema:
    fields: tuple = ()


@dataclass(frozen=True)
class CompositionContract:
    direct_composition_rule: str = "EXACT_TYPE_AND_SCHEMA_MATCH"


@dataclass(frozen=True)
class DomainAdapterPolicy:
    admitted_adapter_ids: tuple = ()


@dataclass(frozen=True)
class EffectsContract:
    memory_write: bool = False
    emits_act: bool = False
    b8_mutation: bool = False
    binder_mutation: bool = False
    kernel_mutation: bool = False
    kx108_mutation: bool = False


@dataclass(frozen=True)
class PrimitiveTypeSpec:
    schema_version: str
    primitive_type: str
    spec_version: str
    input_slots: tuple
    output_type: DatumTypeRef
    immutable_config_schema: ConfigSchema
    composition_contract: CompositionContract
    domain_adapter_policy: DomainAdapterPolicy
    effects_contract: EffectsContract

    def _slots(self):
        return tuple(sorted(self.input_slots, key=lambda s: _nfc(s.slot_name)))

    def _canonical(self):
        def obj(x):
            return {f.name: getattr(x, f.name) for f in fields(x)}
        return {
            "composition_contract": obj(self.composition_contract),
            "domain_adapter_policy": {"admitted_adapter_ids": tuple(sorted(self.domain_adapter_policy.admitted_adapter_ids))},
            "effects_contract": obj(self.effects_contract),
            "immutable_config_schema": {"fields": tuple(obj(f) for f in sorted(
                self.immutable_config_schema.fields, key=lambda f: _nfc(f.name)))},
            "input_slots": tuple(dict(obj(s), slot_name=_nfc(s.slot_name)) for s in self._slots()),
            "output_type": obj(self.output_type),
            "primitive_type": self.primitive_type,
            "schema_version": self.schema_version,
            "spec_version": self.spec_version,
        }


# ---------------------------------------------------------------- invocation (§18, §19, §32 D–G)
@dataclass(frozen=True, init=False)
class PrimitiveInvocationDraft:
    schema_version: Any
    primitive_type: Any
    primitive_spec_version: Any
    inputs: tuple
    immutable_config: Any

    def __init__(self, schema_version, primitive_type, primitive_spec_version, inputs, immutable_config):
        if isinstance(inputs, (str, bytes, Mapping)) or not isinstance(inputs, (list, tuple)):
            _fail("INVALID_BINDING", "inputs must be a sequence of PrimitiveInputBinding")
        if not all(isinstance(b, PrimitiveInputBinding) for b in inputs):
            _fail("INVALID_BINDING", "inputs must contain only PrimitiveInputBinding")
        if not isinstance(immutable_config, Mapping):
            _fail("INVALID_IMMUTABLE_CONFIG", "immutable_config must be a mapping")
        try:
            cfg = _freeze(immutable_config, "INVALID_IMMUTABLE_CONFIG")
        except InvocationValidationError:
            cfg = _Unfrozen(dict(immutable_config))  # canonical check is §20 step 9
        object.__setattr__(self, "schema_version", schema_version)
        object.__setattr__(self, "primitive_type", primitive_type)
        object.__setattr__(self, "primitive_spec_version", primitive_spec_version)
        object.__setattr__(self, "inputs", tuple(inputs))
        object.__setattr__(self, "immutable_config", cfg)


class _Unfrozen:
    def __init__(self, raw):
        self.raw = raw


@dataclass(frozen=True)
class FinalizedPrimitiveInvocation:
    schema_version: str
    primitive_type: str
    primitive_spec_version: str
    inputs: tuple
    immutable_config: Any
    invocation_id: str


_KIND_CHECK = {
    "null": lambda v: v is None,
    "boolean": lambda v: isinstance(v, bool),
    "string": lambda v: isinstance(v, str),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "array": lambda v: isinstance(v, tuple),
    "object": lambda v: isinstance(v, Mapping),
}


def finalize(draft: PrimitiveInvocationDraft, registry: "PrimitiveRegistry") -> FinalizedPrimitiveInvocation:
    """Phases E–G (§20 steps 1–13). The registry is always explicit."""
    ptype, pver = draft.primitive_type, draft.primitive_spec_version
    if not _is_nonempty_str(ptype):
        _fail("UNKNOWN_PRIMITIVE_TYPE", "primitive_type must be a non-empty string")
    if not _is_nonempty_str(pver):
        _fail("UNKNOWN_PRIMITIVE_VERSION", "primitive_spec_version must be a non-empty string")
    spec = registry._resolve_type(ptype, pver)
    if draft.schema_version != INVOCATION_SCHEMA:
        _fail("INVALID_SCHEMA_VERSION", f"expected {INVOCATION_SCHEMA}")
    declared = {_nfc(s.slot_name): s for s in spec.input_slots}
    seen = set()
    for b in draft.inputs:
        if b.slot_name in seen:
            _fail("DUPLICATE_INPUT_SLOT", b.slot_name, b.slot_name)
        seen.add(b.slot_name)
    for b in draft.inputs:
        if b.slot_name not in declared:
            _fail("UNKNOWN_INPUT_SLOT", b.slot_name, b.slot_name)
    for b in sorted(draft.inputs, key=lambda x: x.slot_name):
        slot = declared[b.slot_name]
        if b.datum.datum_type != slot.datum_type:
            _fail("DATUM_TYPE_MISMATCH", b.slot_name, b.slot_name)
        if b.datum.schema_version != slot.datum_schema_version:
            _fail("DATUM_SCHEMA_MISMATCH", b.slot_name, b.slot_name)
    cfg = draft.immutable_config
    if isinstance(cfg, _Unfrozen):
        _fail("INVALID_IMMUTABLE_CONFIG", "immutable_config is not canonical")
    schema = {_nfc(f.name): f for f in spec.immutable_config_schema.fields}
    for key in cfg:
        if key not in schema:
            _fail("INVALID_IMMUTABLE_CONFIG", f"undeclared config key {key}", key)
    for name, f in schema.items():
        if name not in cfg:
            if f.required:
                _fail("INVALID_IMMUTABLE_CONFIG", f"missing config key {name}", name)
        elif not _KIND_CHECK.get(f.value_kind, lambda v: False)(cfg[name]):
            _fail("INVALID_IMMUTABLE_CONFIG", f"wrong kind for {name}", name)
    inputs = tuple(sorted(draft.inputs, key=lambda x: x.slot_name))
    preimage = {
        "immutable_config": cfg,
        "inputs": tuple(b._canonical() for b in inputs),
        "primitive_spec_version": pver,
        "primitive_type": ptype,
        "schema_version": INVOCATION_SCHEMA,
    }
    return FinalizedPrimitiveInvocation(INVOCATION_SCHEMA, ptype, pver, inputs, cfg, _sha256_hex(preimage))


# ---------------------------------------------------------------- results & provenance (§22, §23, §34)
class PrimitiveResultStatus(Enum):
    PRODUCED = "PRODUCED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    INSUFFICIENT_INPUT = "INSUFFICIENT_INPUT"
    UNKNOWN = "UNKNOWN"
    FAILED_RUNTIME = "FAILED_RUNTIME"


@dataclass(frozen=True)
class PrimitiveProvenance:
    implementation_id: str
    source_refs: tuple
    derived_from_invocation_ids: tuple
    implementation_version: Optional[str] = None
    provider_id: Optional[str] = None
    model_id: Optional[str] = None
    execution_environment_ref: Optional[str] = None


@dataclass(frozen=True, init=False)
class PrimitiveResult:
    schema_version: str
    invocation_id: str
    status: PrimitiveResultStatus
    output: Optional[TypedCognitiveDatum]
    provenance: PrimitiveProvenance
    diagnostics: tuple

    def __init__(self, schema_version, invocation_id, status, output, provenance, diagnostics, **extra):
        if extra:
            _fail("INVALID_RESULT", f"unknown result fields {sorted(extra)}")
        if schema_version != RESULT_SCHEMA:
            _fail("INVALID_RESULT", "wrong result schema_version")
        if not isinstance(invocation_id, str) or not _HEX64.match(invocation_id):
            _fail("INVALID_RESULT", "invocation_id must be 64 lowercase hex")
        if not isinstance(status, PrimitiveResultStatus):
            _fail("INVALID_RESULT", "unknown status")
        if status is PrimitiveResultStatus.PRODUCED:
            if not isinstance(output, TypedCognitiveDatum):
                _fail("INVALID_RESULT", "PRODUCED requires an output datum")
        elif output is not None:
            _fail("INVALID_RESULT", f"{status.value} must not carry an output")
        if not isinstance(provenance, PrimitiveProvenance):
            _fail("INVALID_RESULT", "provenance must be a PrimitiveProvenance")
        if isinstance(diagnostics, (str, bytes)) or not all(isinstance(d, str) for d in diagnostics):
            _fail("INVALID_RESULT", "diagnostics must be a tuple of strings")
        for name, val in (("schema_version", schema_version), ("invocation_id", invocation_id), ("status", status),
                          ("output", output), ("provenance", provenance), ("diagnostics", tuple(diagnostics))):
            object.__setattr__(self, name, val)


@dataclass(frozen=True)
class PrimitiveImplementationOutcome:
    status: PrimitiveResultStatus
    output: Optional[TypedCognitiveDatum] = None
    diagnostics: tuple = ()


@dataclass(frozen=True)
class PrimitiveImplementationSpec:
    primitive_type: str
    spec_version: str
    implementation_id: str
    run: Callable = field(compare=False)
    implementation_version: Optional[str] = None
    provider_id: Optional[str] = None
    model_id: Optional[str] = None
    execution_environment_ref: Optional[str] = None

    def _canonical(self):
        d = {"implementation_id": self.implementation_id, "primitive_type": self.primitive_type,
             "spec_version": self.spec_version}
        for k in ("execution_environment_ref", "implementation_version", "model_id", "provider_id"):
            if getattr(self, k) is not None:
                d[k] = getattr(self, k)
        return _freeze(d, "INVALID_TYPE_SPEC")


@dataclass(frozen=True)
class PrimitiveExecutionRecord:
    invocation_id: str
    implementation_id: str
    result: PrimitiveResult
    provenance: PrimitiveProvenance
    implementation_version: Optional[str] = None
    provider_id: Optional[str] = None
    model_id: Optional[str] = None
    execution_environment_ref: Optional[str] = None


# ---------------------------------------------------------------- registry (§27, §30, §34)
class PrimitiveRegistry:
    """Explicit registry scope: TEST_REGISTRY or PRODUCTION_REGISTRY (§30). Grants no authority."""

    def __init__(self, scope: str):
        if scope not in _SCOPES:
            raise ValueError(f"scope must be one of {_SCOPES}")
        self.scope = scope
        self._types: dict = {}
        self._impls: dict = {}

    def _reject_test_namespace(self, primitive_type):
        if self.scope == "PRODUCTION_REGISTRY" and str(primitive_type).startswith("test."):
            _fail("TEST_PRIMITIVE_IN_PRODUCTION", primitive_type)

    def register_type_spec(self, spec: PrimitiveTypeSpec) -> None:
        if not isinstance(spec, PrimitiveTypeSpec):
            _fail("INVALID_TYPE_SPEC", "not a PrimitiveTypeSpec")
        self._reject_test_namespace(spec.primitive_type)
        if spec.schema_version != TYPE_SPEC_SCHEMA:
            _fail("INVALID_TYPE_SPEC", "wrong type-spec schema_version")
        if not (_is_nonempty_str(spec.primitive_type) and _is_nonempty_str(spec.spec_version)):
            _fail("INVALID_TYPE_SPEC", "primitive_type and spec_version must be non-empty")
        if any(getattr(spec.effects_contract, f) is not False for f in _EFFECT_FLAGS):
            _fail("INVALID_TYPE_SPEC", "M32 V1 effects must all be false")
        names = [_nfc(s.slot_name) if _is_nonempty_str(s.slot_name) else None for s in spec.input_slots]
        if None in names or len(set(names)) != len(names):
            _fail("INVALID_TYPE_SPEC", "input slot names must be non-empty and unique after NFC")
        if spec.composition_contract.direct_composition_rule != "EXACT_TYPE_AND_SCHEMA_MATCH":
            _fail("INVALID_TYPE_SPEC", "unsupported composition rule")
        try:
            canonical = _serialize(_freeze(spec._canonical(), "INVALID_TYPE_SPEC"))
        except InvocationValidationError:
            raise
        key = (spec.primitive_type, spec.spec_version)
        existing = self._types.get(key)
        if existing is not None:
            if existing[0] != canonical:
                _fail("REGISTRY_CONFLICT", f"{key} already registered with a different spec")
            return
        self._types[key] = (canonical, spec)

    def _resolve_type(self, primitive_type, spec_version) -> PrimitiveTypeSpec:
        if not any(t == primitive_type for t, _ in self._types):
            _fail("UNKNOWN_PRIMITIVE_TYPE", primitive_type)
        entry = self._types.get((primitive_type, spec_version))
        if entry is None:
            _fail("UNKNOWN_PRIMITIVE_VERSION", f"{primitive_type}@{spec_version}")
        return entry[1]

    def register_implementation(self, impl: PrimitiveImplementationSpec) -> None:
        self._reject_test_namespace(impl.primitive_type)
        if (impl.primitive_type, impl.spec_version) not in self._types:
            _fail("UNKNOWN_IMPLEMENTATION", "target type spec is not registered in this scope")
        if not _is_nonempty_str(impl.implementation_id) or not callable(impl.run):
            _fail("UNKNOWN_IMPLEMENTATION", "implementation_id must be non-empty and run callable")
        key = (impl.primitive_type, impl.spec_version, _nfc(impl.implementation_id))
        canonical = _serialize(impl._canonical())
        existing = self._impls.get(key)
        if existing is not None:
            if existing[0] != canonical or existing[1].run is not impl.run:
                _fail("REGISTRY_CONFLICT", f"implementation {key} already registered differently")
            return
        self._impls[key] = (canonical, impl)

    def _resolve_impl(self, primitive_type, spec_version, implementation_id) -> PrimitiveImplementationSpec:
        entry = self._impls.get((primitive_type, spec_version, _nfc(str(implementation_id))))
        if entry is None:
            _fail("UNKNOWN_IMPLEMENTATION", str(implementation_id))
        return entry[1]


# ---------------------------------------------------------------- execution (§34, §32 H–J)
def _opt_nfc(v):
    return _nfc(v) if isinstance(v, str) else v


def execute(finalized: FinalizedPrimitiveInvocation, registry: PrimitiveRegistry, implementation_id: str,
            derived_from_invocation_ids=()) -> PrimitiveExecutionRecord:
    impl = registry._resolve_impl(finalized.primitive_type, finalized.primitive_spec_version, implementation_id)
    if isinstance(derived_from_invocation_ids, (str, bytes)) or not all(
            isinstance(i, str) and _HEX64.match(i) for i in derived_from_invocation_ids):
        _fail("INVALID_EXECUTION_REQUEST", "derived_from_invocation_ids must be 64 lowercase hex strings")
    derived = tuple(sorted(set(derived_from_invocation_ids)))
    refs = set()
    for b in finalized.inputs:
        refs.update(b.datum.semantic_refs or ())
    provenance = PrimitiveProvenance(
        implementation_id=_nfc(impl.implementation_id),
        source_refs=tuple(sorted(_nfc(r) for r in refs)),
        derived_from_invocation_ids=derived,
        implementation_version=_opt_nfc(impl.implementation_version),
        provider_id=_opt_nfc(impl.provider_id),
        model_id=_opt_nfc(impl.model_id),
        execution_environment_ref=_opt_nfc(impl.execution_environment_ref),
    )
    spec = registry._resolve_type(finalized.primitive_type, finalized.primitive_spec_version)
    supplied = {b.slot_name for b in finalized.inputs}
    missing = [s for s in spec.input_slots if s.required and _nfc(s.slot_name) not in supplied]
    if missing:
        status, output, diagnostics = PrimitiveResultStatus.INSUFFICIENT_INPUT, None, ()
    else:
        try:
            candidate = impl.run(finalized, finalized.immutable_config)
        except Exception as exc:  # captured, never raised (§32 I)
            candidate = PrimitiveImplementationOutcome(PrimitiveResultStatus.FAILED_RUNTIME, None,
                                                       (type(exc).__name__,))
        if type(candidate) is not PrimitiveImplementationOutcome:
            _fail("INVALID_RESULT", "implementation must return exactly a PrimitiveImplementationOutcome")
        status, output, diagnostics = candidate.status, candidate.output, candidate.diagnostics
        if status is PrimitiveResultStatus.PRODUCED and isinstance(output, TypedCognitiveDatum) and (
                output.datum_type, output.schema_version) != (spec.output_type.datum_type,
                                                              spec.output_type.datum_schema_version):
            _fail("INVALID_RESULT", "PRODUCED output does not match the declared output_type")
    result = PrimitiveResult(RESULT_SCHEMA, finalized.invocation_id, status, output, provenance, tuple(diagnostics))
    return PrimitiveExecutionRecord(
        invocation_id=finalized.invocation_id, implementation_id=provenance.implementation_id, result=result,
        provenance=provenance, implementation_version=provenance.implementation_version,
        provider_id=provenance.provider_id, model_id=provenance.model_id,
        execution_environment_ref=provenance.execution_environment_ref)


# ---------------------------------------------------------------- domain adapters (§25)
@dataclass(frozen=True)
class DomainAdapterSpec:
    adapter_id: str
    adapter_version: str
    source_domain_type: str
    target_datum_type: str
    target_datum_schema_version: str
    reverse_supported: bool


class DomainAdapter:
    """Wraps caller translation functions; enforces the declared target and reverse support.
    Adapters cannot touch result statuses, authority, memory or primitive versions."""

    __slots__ = ("spec", "_to", "_from")

    def __init__(self, spec: DomainAdapterSpec, to_core: Callable, from_core: Optional[Callable] = None):
        object.__setattr__(self, "spec", spec)
        object.__setattr__(self, "_to", to_core)
        object.__setattr__(self, "_from", from_core)

    def __setattr__(self, name, value):
        raise AttributeError("DomainAdapter is immutable")

    def to_core(self, domain_value) -> TypedCognitiveDatum:
        try:
            datum = self._to(domain_value)
        except InvocationValidationError:
            raise
        except Exception as exc:
            raise InvocationValidationError("ADAPTER_INPUT_INVALID", type(exc).__name__) from None
        if not isinstance(datum, TypedCognitiveDatum) or (datum.datum_type, datum.schema_version) != (
                self.spec.target_datum_type, self.spec.target_datum_schema_version):
            _fail("ADAPTER_INPUT_INVALID", "adapter output does not match its declared target datum type/schema")
        return datum

    def from_core(self, datum: TypedCognitiveDatum):
        if not self.spec.reverse_supported or self._from is None:
            _fail("ADAPTER_REVERSE_UNSUPPORTED", self.spec.adapter_id)
        if not isinstance(datum, TypedCognitiveDatum) or (datum.datum_type, datum.schema_version) != (
                self.spec.target_datum_type, self.spec.target_datum_schema_version):
            _fail("ADAPTER_INPUT_INVALID", "datum does not match the adapter's declared target")
        try:
            return self._from(datum)
        except Exception as exc:
            raise InvocationValidationError("ADAPTER_INPUT_INVALID", type(exc).__name__) from None
