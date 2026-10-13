"""M32 RED test harness (test code only — defines no production semantics).

Two kinds of content live here:

1. Independent ORACLES derived from the certified spec (reference canonical JSON, identity digest,
   protected-path discovery from the foundation seal/sentinel, AST public-name extraction). These are
   runtime-independent and are self-checked by test_m32_harness_selfcheck_red.py.

2. HARNESS BINDINGS: the spec names every type, field, code and operation (§§16–34), but does not fix
   the Python spelling of the registry object or the adapter wrapper. Those spellings are bound in ONE
   place below so a GREEN implementation can align with them (or the binding can be adjusted here
   without touching any test):
     - ``PrimitiveRegistry(scope)`` with scope ∈ {"TEST_REGISTRY", "PRODUCTION_REGISTRY"} (§30)
     - ``registry.register_type_spec(spec)`` (§27)
     - ``registry.register_implementation(impl_spec)`` (§34)
     - ``DomainAdapter(spec, to_core, from_core=None)`` exposing ``.to_core(v)`` / ``.from_core(d)`` (§25)
   Everything else uses the certified names verbatim: TypedCognitiveDatum, PrimitiveInputBinding,
   PrimitiveInvocationDraft, finalize, execute, PrimitiveTypeSpec, InputSlotSpec, DatumTypeRef,
   ConfigSchema, ConfigFieldSpec, CompositionContract, DomainAdapterPolicy, EffectsContract,
   PrimitiveImplementationSpec, PrimitiveImplementationOutcome, PrimitiveResultStatus, PrimitiveResult,
   PrimitiveProvenance, PrimitiveExecutionRecord, InvocationValidationError, DomainAdapterSpec.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
import unicodedata
from pathlib import Path

RUNTIME_MODULE = "app.primitives.m32"
REPO = Path(__file__).resolve().parents[2]
M32_BASE = "faf72a25fb912a27b4be9a71d1b1a07f0e8fca79"
M32_RUNTIME_DIR = REPO / "app" / "primitives" / "m32"
FORBIDDEN_RUNTIME_DIR = REPO / "app" / "cognition" / "m32"
SEAL_DOC = REPO / "docs" / "architecture" / "COGNITIVE_FOUNDATION_V1_SEAL.md"
SENTINEL = REPO / "scripts" / "foundation_sentinel.py"

INVOCATION_SCHEMA = "m32.invocation.v1"
RESULT_SCHEMA = "m32.result.v1"
TYPE_SPEC_SCHEMA = "m32.primitive_type_spec.v1"
TEXT_T, TEXT_V1, TEXT_V2 = "test.text", "v1", "v2"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
STATUS_NAMES = {"PRODUCED", "NOT_APPLICABLE", "INSUFFICIENT_INPUT", "UNKNOWN", "FAILED_RUNTIME"}


# ----------------------------------------------------------------------------- reference oracles
def _nfc(value):
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, list):
        return [_nfc(v) for v in value]
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            nk = _nfc(k)
            assert nk not in out, "NFC key collision"
            out[nk] = _nfc(v)
        return out
    return value


def ref_canonical_json(value) -> str:
    """§15 reference for the value classes used in the test vectors (strings, ints, bools, null,
    arrays, objects). Floats are deliberately not used in identity vectors."""
    v = _nfc(value)
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def ref_datum(datum_type, schema_version, value, semantic_refs=None) -> dict:
    d = {"datum_type": datum_type, "schema_version": schema_version, "value": value}
    if semantic_refs is not None:
        d["semantic_refs"] = list(semantic_refs)
    return d


def ref_invocation_id(primitive_type, spec_version, bindings, config) -> str:
    """§19: SHA-256 over canonical UTF-8 JSON of the five-key preimage; bindings sorted by NFC slot."""
    inputs = sorted(
        ({"datum": d, "slot_name": unicodedata.normalize("NFC", s)} for s, d in bindings),
        key=lambda b: b["slot_name"],
    )
    preimage = {
        "immutable_config": config,
        "inputs": inputs,
        "primitive_spec_version": spec_version,
        "primitive_type": primitive_type,
        "schema_version": INVOCATION_SCHEMA,
    }
    return hashlib.sha256(ref_canonical_json(preimage).encode("utf-8")).hexdigest()


# ----------------------------------------------------------------------------- seal / sentinel oracles
def protected_paths() -> list[str]:
    """§35: protected set = seal §4 PROTECTED_RUNTIME_CORE + sentinel file + sentinel test targets."""
    seal = SEAL_DOC.read_text(encoding="utf-8")
    core_line = next(l for l in seal.splitlines() if "PROTECTED_RUNTIME_CORE" in l)
    paths = re.findall(r"`([^`]+)`", core_line)
    paths.append("scripts/foundation_sentinel.py")
    sent = SENTINEL.read_text(encoding="utf-8")
    paths += re.findall(r'"(tests/[A-Za-z0-9_./*-]+)"', sent)
    out = []
    for p in paths:
        if "*" in p:
            out += [str(q.relative_to(REPO)).replace("\\", "/") for q in sorted(REPO.glob(p))]
        else:
            out.append(p.rstrip("/"))
    return sorted(set(out))


def git(*args) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, check=True).stdout


def protected_diff_since_base() -> list[str]:
    """Auditor-hardened §35 oracle: git diff M32_BASE..HEAD over PROTECTED_PATHS (any commit)."""
    out = git("diff", "--name-only", f"{M32_BASE}..HEAD", "--", *protected_paths())
    return [l for l in out.splitlines() if l.strip()]


def tracked_py(directory: str) -> list[Path]:
    out = git("ls-files", "--", directory)
    return [REPO / l for l in out.splitlines() if l.endswith(".py")]


def _top_level_bound(tree: ast.Module) -> set[str]:
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                for n in ast.walk(t):
                    if isinstance(n, ast.Name):
                        names.add(n.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


def public_names(layer_dir: str) -> set[str]:
    """§35 PUBLIC_NAMES(L): def/class/Assign/AnnAssign top-level in tracked .py recursively, plus
    names re-exported by L's __init__.py (imports there, or __all__). Underscore names excluded."""
    names: set[str] = set()
    for f in tracked_py(layer_dir):
        tree = ast.parse(f.read_text(encoding="utf-8"))
        names |= _top_level_bound(tree)
        if f.name == "__init__.py":
            for node in tree.body:
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    names |= {(a.asname or a.name).split(".")[0] for a in node.names}
                if isinstance(node, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets
                ):
                    try:
                        names |= set(ast.literal_eval(node.value))
                    except ValueError:
                        pass
    return {n for n in names if not n.startswith("_")}


def m32_defined_names(root: Path = M32_RUNTIME_DIR) -> set[str]:
    """§35 M32_DEFINED_NAMES: def/class/Assign/AnnAssign top-level under app/primitives/m32 (imports excluded)."""
    names: set[str] = set()
    for f in sorted(root.rglob("*.py")):
        names |= _top_level_bound(ast.parse(f.read_text(encoding="utf-8")))
    return {n for n in names if not n.startswith("_")}


def sealed_attribute_assignments(root: Path, sealed_prefixes: tuple[str, ...]) -> list[str]:
    """§35 rule 3: assignment/del/setattr on a module or member imported from a sealed layer."""
    hits = []
    for f in sorted(root.rglob("*.py")):
        tree = ast.parse(f.read_text(encoding="utf-8"))
        sealed_aliases = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    if a.name.startswith(sealed_prefixes):
                        sealed_aliases.add((a.asname or a.name).split(".")[0])
            elif isinstance(node, ast.ImportFrom) and (node.module or "").startswith(sealed_prefixes):
                sealed_aliases |= {a.asname or a.name for a in node.names}
        for node in ast.walk(tree):
            targets = []
            if isinstance(node, (ast.Assign, ast.AugAssign, ast.Delete)):
                targets = node.targets if hasattr(node, "targets") else [node.target]
            for t in targets:
                if isinstance(t, ast.Attribute):
                    base = t.value
                    while isinstance(base, ast.Attribute):
                        base = base.value
                    if isinstance(base, ast.Name) and base.id in sealed_aliases:
                        hits.append(f"{f}:{node.lineno}")
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id in {"setattr", "delattr"} and node.args
                    and isinstance(node.args[0], ast.Name) and node.args[0].id in sealed_aliases):
                hits.append(f"{f}:{node.lineno}")
    return hits


SEALED_LAYERS = {
    "B7": ("app/cognition/b7", "tests/b7", ("app.cognition.b7",)),
    "B8": ("app/knowledge/b8", "tests/b8", ("app.knowledge.b8",)),
    "B9": ("app/cognition/b9", "tests/b9", ("app.cognition.b9",)),
}


# ----------------------------------------------------------------------------- runtime fixture builders
def no_effects(m32, **overrides):
    flags = dict(memory_write=False, emits_act=False, b8_mutation=False,
                 binder_mutation=False, kernel_mutation=False, kx108_mutation=False)
    flags.update(overrides)
    return m32.EffectsContract(**flags)


def type_spec(m32, primitive_type, *, spec_version="v1", slot_schema=TEXT_V1, slots=None,
              config_fields=(), effects=None):
    if slots is None:
        slots = (m32.InputSlotSpec(slot_name="x", datum_type=TEXT_T,
                                   datum_schema_version=slot_schema, required=True),)
    return m32.PrimitiveTypeSpec(
        schema_version=TYPE_SPEC_SCHEMA,
        primitive_type=primitive_type,
        spec_version=spec_version,
        input_slots=tuple(slots),
        output_type=m32.DatumTypeRef(datum_type=TEXT_T, datum_schema_version=TEXT_V1),
        immutable_config_schema=m32.ConfigSchema(fields=tuple(config_fields)),
        composition_contract=m32.CompositionContract(direct_composition_rule="EXACT_TYPE_AND_SCHEMA_MATCH"),
        domain_adapter_policy=m32.DomainAdapterPolicy(admitted_adapter_ids=()),
        effects_contract=effects if effects is not None else no_effects(m32),
    )


def outcome(m32, status_name, output=None, diagnostics=()):
    return m32.PrimitiveImplementationOutcome(
        status=getattr(m32.PrimitiveResultStatus, status_name), output=output, diagnostics=tuple(diagnostics))


class Spy:
    """Counts calls to a run callable."""

    def __init__(self, fn):
        self.fn, self.calls = fn, 0

    def __call__(self, finalized, immutable_config):
        self.calls += 1
        return self.fn(finalized, immutable_config)


class ControlledFailure(RuntimeError):
    pass


def _x_value(finalized):
    return next(b.datum.value for b in finalized.inputs if b.slot_name == "x")


def impl(m32, primitive_type, implementation_id, run, *, provider_id=None, env=None):
    kwargs = dict(primitive_type=primitive_type, spec_version="v1", implementation_id=implementation_id, run=run)
    if provider_id is not None:
        kwargs["provider_id"] = provider_id
    if env is not None:
        kwargs["execution_environment_ref"] = env
    return m32.PrimitiveImplementationSpec(**kwargs)


def build_test_registry(m32):
    """§36 fixtures: test.echo (impl.a, impl.b), test.na, test.unknown, test.failure, test.echo2."""
    reg = m32.PrimitiveRegistry("TEST_REGISTRY")
    tag = m32.ConfigFieldSpec(name="tag", value_kind="string", required=False)
    reg.register_type_spec(type_spec(m32, "test.echo", config_fields=(tag,)))
    for t in ("test.na", "test.unknown", "test.failure"):
        reg.register_type_spec(type_spec(m32, t))
    reg.register_type_spec(type_spec(m32, "test.echo2", slot_schema=TEXT_V2))

    def echo(fin, cfg):
        return outcome(m32, "PRODUCED", m32.TypedCognitiveDatum(TEXT_V1, TEXT_T, _x_value(fin)))

    def echo_bang(fin, cfg):
        return outcome(m32, "PRODUCED", m32.TypedCognitiveDatum(TEXT_V1, TEXT_T, _x_value(fin) + "!"))

    def raise_(fin, cfg):
        raise ControlledFailure("controlled")

    reg.register_implementation(impl(m32, "test.echo", "impl.a", echo))
    reg.register_implementation(impl(m32, "test.echo", "impl.b", echo_bang, provider_id="prov.b"))
    reg.register_implementation(impl(m32, "test.na", "impl.a", lambda f, c: outcome(m32, "NOT_APPLICABLE")))
    reg.register_implementation(impl(m32, "test.unknown", "impl.a", lambda f, c: outcome(m32, "UNKNOWN")))
    reg.register_implementation(impl(m32, "test.failure", "impl.a", raise_))
    reg.register_implementation(impl(m32, "test.echo2", "impl.a", echo))
    return reg


def text(m32, value, schema=TEXT_V1, refs=None):
    if refs is None:
        return m32.TypedCognitiveDatum(schema, TEXT_T, value)
    return m32.TypedCognitiveDatum(schema, TEXT_T, value, semantic_refs=tuple(refs))


def draft(m32, primitive_type, bindings, config=None, spec_version="v1"):
    return m32.PrimitiveInvocationDraft(
        INVOCATION_SCHEMA, primitive_type, spec_version,
        tuple(m32.PrimitiveInputBinding(s, d) for s, d in bindings), dict(config or {}))


def finalize(m32, reg, primitive_type, bindings, config=None, spec_version="v1"):
    return m32.finalize(draft(m32, primitive_type, bindings, config, spec_version), reg)


def raises_code(m32, code, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except m32.InvocationValidationError as exc:
        assert exc.code == code, f"expected {code}, got {exc.code}"
        return exc
    raise AssertionError(f"expected InvocationValidationError({code}), nothing raised")
