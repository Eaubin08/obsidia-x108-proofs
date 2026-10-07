"""Security Boundary Sentinel V0 — detects material changes to a certified trust boundary.

Static, deterministic, AST-based (comments and docstrings are never code). Input: a snapshot
{posix relative path: source}. Output: typed findings with a severity from a frozen table, and the
boundary status (SAFE | REAUDIT_REQUIRED | SECURITY_HOLD | EMERGENCY_HOLD). The certified baseline is
read-only (app/security/b7_epoch1_baseline.py): a detected change never updates it and never bumps
the epoch -- only an explicit audited certification can establish a new epoch.

No provider, no network, no subprocess, no memory write, no act, no decision authority.
"""
from __future__ import annotations

import ast
import functools
import hashlib
import json
import pathlib
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Mapping

from app.security.b7_epoch1_baseline import BASELINE


class SecuritySeverity(Enum):
    LEVEL_1 = 1      # REAUDIT_REQUIRED: certified assumption changed, no demonstrated bypass
    LEVEL_2 = 2      # SECURITY_HOLD: dangerous trust-boundary condition reachable
    LEVEL_3 = 3      # EMERGENCY_HOLD: authority / integrity invariant breached


class SecurityBoundaryStatus(Enum):
    SAFE = "SAFE"
    REAUDIT_REQUIRED = "REAUDIT_REQUIRED"
    SECURITY_HOLD = "SECURITY_HOLD"
    EMERGENCY_HOLD = "EMERGENCY_HOLD"


_STATUS = {SecuritySeverity.LEVEL_1: SecurityBoundaryStatus.REAUDIT_REQUIRED,
           SecuritySeverity.LEVEL_2: SecurityBoundaryStatus.SECURITY_HOLD,
           SecuritySeverity.LEVEL_3: SecurityBoundaryStatus.EMERGENCY_HOLD}

L1, L2, L3 = SecuritySeverity.LEVEL_1, SecuritySeverity.LEVEL_2, SecuritySeverity.LEVEL_3
# frozen trigger table: trigger -> (severity, invariant, required action)
TRIGGERS: Mapping[str, tuple[SecuritySeverity, str, str]] = {
    "NEW_B7_IMPORTER": (L1, "no production importer of app.cognition outside B7", "re-audit B7 trust boundary"),
    "NEW_ISSUE_CALLER": (L1, "_issue / _is_issued used only by the B7 gate", "re-audit B7 issuance"),
    "NEW_TRUST_SINK_CALLER": (L1, "no production caller of B7 trust sinks", "re-audit B7 trust boundary"),
    "NEW_TRUST_SINK": (L1, "certified trust sinks = admit_trusted_context, register_derived", "re-audit B7 trust sinks"),
    "LIVE_PROVIDER_WIRING_ACTIVATED": (L1, "LIVE_PROVIDER_WIRING=NOT_IMPLEMENTED", "re-audit before activation"),
    "CERTIFIED_RUNTIME_CLOSURE_CHANGE": (L1, "B7 transitive runtime closure = certified module set", "re-audit closure"),
    "SECURITY_CONTRACT_CHANGED": (L1, "security-sensitive sources match the certified fingerprints", "re-audit change"),
    "UNGUARDED_TRUST_SINK": (L2, "every trust sink requires _is_issued + ACCEPT + StateEntry", "quarantine sink, re-audit"),
    "RAW_B6_TRUST_ADMISSION": (L2, "raw B6 ContextPacket is not proof of B7 validation", "quarantine admission, re-audit"),
    "SAME_PROCESS_UNTRUSTED_CODE": (L2, "no dynamic code execution in the B7 runtime", "quarantine; isolation boundary required"),
    "MEMORY_WRITE_ESCALATION": (L3, "MEMORY_WRITE=False", "emergency hold; governed recovery decision"),
    "ACT_ESCALATION": (L3, "EMITS_ACT=False", "emergency hold; governed recovery decision"),
    "KERNEL_MUTATION_ESCALATION": (L3, "KERNEL_MUTATION=False", "emergency hold; governed recovery decision"),
    "NON_KX108_AUTHORITY": (L3, "DECISION_AUTHORITY=KX108_ONLY", "emergency hold; governed recovery decision"),
}


@dataclass(frozen=True)
class SecurityFinding:
    finding_id: str
    boundary_id: str
    security_epoch: int
    severity: SecuritySeverity
    trigger: str
    invariant: str
    affected_surface: str
    symbol: str
    expected: str
    observed: str
    evidence_refs: tuple[str, ...]
    reason: str
    required_action: str


@dataclass(frozen=True)
class SentinelReport:
    boundary_id: str
    security_epoch: int
    status: SecurityBoundaryStatus
    findings: tuple[SecurityFinding, ...]

    @property
    def epoch_applicable(self) -> bool:
        """The certified epoch applies only to an unchanged boundary; never re-established here."""
        return self.status == SecurityBoundaryStatus.SAFE


class SecurityHoldError(RuntimeError):
    """Fail-closed signal: the certified boundary no longer holds (V0: raised, never auto-recovered)."""


# ── snapshot ──────────────────────────────────────────────────────────────────────────────────
_SKIP_DIRS = {".git", ".claude", "__pycache__", "node_modules", ".venv", "venv"}


def _is_test_path(path: str) -> bool:
    parts = path.split("/")
    return any(p in ("tests", "test") for p in parts[:-1]) or parts[-1].startswith("test_") or parts[-1] == "conftest.py"


def repository_snapshot(root: pathlib.Path | str) -> dict[str, str]:
    """All app/ sources, plus every other production file that mentions app.cognition (import candidates)."""
    root = pathlib.Path(root)
    files: dict[str, str] = {}
    for p in sorted(root.rglob("*.py")):
        rel = p.relative_to(root).as_posix()
        if set(rel.split("/")) & _SKIP_DIRS:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if rel.startswith("app/") or "cognition" in text:
            files[rel] = text
    return files


# ── AST helpers ───────────────────────────────────────────────────────────────────────────────
@functools.lru_cache(maxsize=4096)
def _parse(src: str) -> ast.AST | None:
    """Pure function of the source text (trees are never mutated), cached for repeated scans."""
    try:
        return ast.parse(src)
    except SyntaxError:
        return None


def _module_name(path: str) -> str | None:
    if not path.endswith(".py"):
        return None
    mod = path[:-3].replace("/", ".")
    return mod[: -len(".__init__")] if mod.endswith(".__init__") else mod


def _imports(tree: ast.AST, module: str, is_pkg: bool) -> list[tuple[str, tuple[str, ...]]]:
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out += [(a.name, ()) for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                pkg = module.split(".") if is_pkg else module.split(".")[:-1]
                pkg = pkg[: len(pkg) - (node.level - 1)]
                base = ".".join(pkg + ([base] if base else []))
            out.append((base, tuple(a.name for a in node.names)))
    return out


def _with_parents(mod: str) -> list[str]:
    parts = mod.split(".")
    return [".".join(parts[:i]) for i in range(1, len(parts) + 1)]


def runtime_closure(files: Mapping[str, str], root_module: str = "app.cognition.b7") -> frozenset[str]:
    """Transitive app.* modules executed by importing root_module (parent packages included)."""
    by_mod = {}
    for path in files:
        mod = _module_name(path)
        if mod and mod.startswith("app"):
            by_mod[mod] = path
    seen: set[str] = set()
    todo = [m for m in _with_parents(root_module) if m in by_mod]
    while todo:
        mod = todo.pop()
        if mod in seen:
            continue
        seen.add(mod)
        tree = _parse(files[by_mod[mod]])
        if tree is None:
            continue
        for base, names in _imports(tree, mod, by_mod[mod].endswith("__init__.py")):
            targets = [base] + [f"{base}.{n}" for n in names]
            for t in targets:
                for m in _with_parents(t):
                    if m in by_mod and m not in seen:
                        todo.append(m)
    return frozenset(seen)


_EXEC_NAMES = {"eval", "exec", "compile", "__import__", "execfile"}
_EXEC_ATTRS = {("runpy", None), ("importlib", "import_module"), ("importlib", "reload"), (None, "exec_module"),
               (None, "spec_from_file_location"), (None, "module_from_spec"), ("pickle", "load"), ("pickle", "loads"),
               ("marshal", "loads"), ("dill", None), ("cloudpickle", None), ("shelve", "open"), ("code", None)}


def _exec_sites(tree: ast.AST) -> list[str]:
    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        if isinstance(f, ast.Name) and f.id in _EXEC_NAMES:
            hits.append(f.id)           # bare compile() only: re.compile(...) is an attribute call
        elif isinstance(f, ast.Attribute):
            base = f.value.id if isinstance(f.value, ast.Name) else None
            for b, a in _EXEC_ATTRS:
                if (b is None or b == base) and (a is None or a == f.attr):
                    hits.append(f"{base}.{f.attr}")
                    break
    return hits


_FLAG_TRIGGER = {"memory_write": "MEMORY_WRITE_ESCALATION", "emits_act": "ACT_ESCALATION",
                 "allowed_to_act": "ACT_ESCALATION", "kernel_mutation": "KERNEL_MUTATION_ESCALATION",
                 "allowed_to_decide": "NON_KX108_AUTHORITY"}


def _authority_sites(tree: ast.AST) -> list[tuple[str, str]]:
    def judge(key: Any, value: ast.AST) -> tuple[str, str] | None:
        if not isinstance(value, ast.Constant):
            return None
        if key in _FLAG_TRIGGER and value.value is True:
            return _FLAG_TRIGGER[key], f"{key}=True"
        if key == "decision_authority" and isinstance(value.value, str) and value.value != "KX108_ONLY":
            return "NON_KX108_AUTHORITY", f"decision_authority={value.value!r}"
        return None
    out = []
    for node in ast.walk(tree):
        pairs: list[tuple[Any, ast.AST]] = []
        if isinstance(node, ast.Dict):
            pairs = [(k.value, v) for k, v in zip(node.keys, node.values) if isinstance(k, ast.Constant)]
        elif isinstance(node, ast.Call):
            pairs = [(k.arg, k.value) for k in node.keywords if k.arg]
        for key, value in pairs:
            hit = judge(key, value)
            if hit:
                out.append(hit)
    return out


def _names(node: ast.AST) -> set[str]:
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            out.add(n.id)
        elif isinstance(n, ast.Attribute):
            out.add(n.attr)
        elif isinstance(n, ast.alias):
            out.add(n.asname or n.name.split(".")[-1])
            out.add(n.name.split(".")[-1])
    return out


def _guarded(fn: ast.AST) -> bool:
    calls = {n.func.id for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    return "_is_issued" in calls and "ACCEPT_AS_STRUCTURED_CONTEXT" in _names(fn) and "StateEntry" in _names(fn)


def _functions(tree: ast.AST) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def _reads_derived_state(fn: ast.AST) -> bool:
    return any(isinstance(n, ast.Attribute) and n.attr == "derived_state" and isinstance(n.ctx, ast.Load)
               for n in ast.walk(fn))


def _fingerprint(src: str) -> str:
    return hashlib.sha256(src.replace("\r\n", "\n").encode("utf-8")).hexdigest()


# ── scan ──────────────────────────────────────────────────────────────────────────────────────
_GATE_INTERNAL = {"_derive", "validate_candidate", "validate_candidates", "_issue", "_is_issued"}
_WIRING_NAMES = {"propose", "translate", "validate_candidate", "validate_candidates"}


def scan(files: Mapping[str, str], *, boundary: Mapping[str, Any] | None = None,
         baseline: Mapping[str, Any] = BASELINE) -> SentinelReport:
    bid, epoch = baseline["boundary_id"], baseline["security_epoch"]
    raw: list[tuple[str, str, str, str, str]] = []      # (trigger, surface, symbol, expected, observed)

    def hit(trigger, surface, symbol, expected, observed):
        raw.append((trigger, surface, symbol, expected, observed))

    pkg = baseline["package_prefix"]
    trees = {p: _parse(s) for p, s in files.items() if p.endswith(".py")}
    production = {p for p in trees if not _is_test_path(p)}

    # A/B/D + external sinks: production code outside the B7 package touching app.cognition
    for path in sorted(production):
        tree = trees[path]
        if tree is None or path.startswith(pkg):
            continue
        mod = _module_name(path) or path
        imports = [(b, n) for b, n in _imports(tree, mod, path.endswith("__init__.py")) if b.startswith("app.cognition")]
        if not imports:
            continue
        hit("NEW_B7_IMPORTER", path, ",".join(sorted({b for b, _ in imports})), "certified importers: none",
            "imports " + ",".join(sorted({b for b, _ in imports})))
        used = _names(tree)
        if used & {"_issue", "_is_issued"}:
            hit("NEW_ISSUE_CALLER", path, ",".join(sorted(used & {"_issue", "_is_issued"})), "0 external callers",
                "references issuance helpers")
        if used & set(baseline["trust_sinks"]):
            hit("NEW_TRUST_SINK_CALLER", path, ",".join(sorted(used & set(baseline["trust_sinks"]))), "0 callers",
                "calls certified trust sink")
        if used & _WIRING_NAMES:
            hit("LIVE_PROVIDER_WIRING_ACTIVATED", path, ",".join(sorted(used & _WIRING_NAMES)),
                "LIVE_PROVIDER_WIRING=NOT_IMPLEMENTED", "production code drives B7 proposal/validation")
        for fn in _functions(tree):
            if _reads_derived_state(fn) and not (_names(fn) & set(baseline["trust_sinks"])):
                hit("UNGUARDED_TRUST_SINK", path, fn.name, "derived_state only via issued-result sinks",
                    "reads derived_state directly")
        for mech in _exec_sites(tree):
            hit("SAME_PROCESS_UNTRUSTED_CODE", path, mech, "no dynamic execution where B7 is loaded", f"calls {mech}")

    # trust sinks, issuance, raw B6 admission inside the B7 package
    for path in sorted(p for p in production if p.startswith(pkg)):
        tree = trees[path]
        if tree is None:
            continue
        if "ContextPacket" in _names(tree):
            hit("RAW_B6_TRUST_ADMISSION", path, "ContextPacket", "B7 never admits raw B6 packets",
                "B7 package references ContextPacket")
        for fn in _functions(tree):
            calls = {n.func.id for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
            if "_issue" in calls and fn.name not in baseline["issue_call_sites"]:
                hit("NEW_ISSUE_CALLER", path, fn.name, "issuance only in " + ",".join(baseline["issue_call_sites"]),
                    f"{fn.name} calls _issue")
            if fn.name in _GATE_INTERNAL or not _reads_derived_state(fn):
                continue
            if not _guarded(fn):
                hit("UNGUARDED_TRUST_SINK", path, fn.name, "_is_issued + ACCEPT + StateEntry", "guard missing")
            elif fn.name not in baseline["trust_sinks"]:
                hit("NEW_TRUST_SINK", path, fn.name, "certified sinks only", "new guarded sink")

    # F + same-process execution + authority literals in the certified runtime closure
    closure = runtime_closure(files, baseline["root_module"])
    certified = set(baseline["runtime_closure"])
    for mod in sorted(closure ^ certified):
        hit("CERTIFIED_RUNTIME_CLOSURE_CHANGE", mod, mod, "certified closure",
            "added to closure" if mod in closure else "removed from closure")
    by_mod = {_module_name(p): p for p in trees}
    for mod in sorted(closure):
        path = by_mod.get(mod)
        tree = trees.get(path) if path else None
        if tree is None:
            continue
        for mech in _exec_sites(tree):
            hit("SAME_PROCESS_UNTRUSTED_CODE", path, mech, "no dynamic execution in the B7 runtime", f"calls {mech}")
        for trigger, observed in _authority_sites(tree):
            hit(trigger, path, observed.split("=")[0], TRIGGERS[trigger][1], observed)

    # E: security-sensitive source fingerprints
    for path, digest in sorted(baseline["fingerprints"].items()):
        observed = _fingerprint(files[path]) if path in files else "missing"
        if observed != digest:
            hit("SECURITY_CONTRACT_CHANGED", path, path, digest, observed)
    for path in sorted(p for p in production if p.startswith(pkg) and p not in baseline["fingerprints"]):
        hit("SECURITY_CONTRACT_CHANGED", path, path, "not certified", "new file in B7 package")

    # runtime authority invariants
    if boundary is None:
        from app.harness.state_explicit.contracts import BOUNDARY as boundary
    for key, trigger in (("memory_write", "MEMORY_WRITE_ESCALATION"), ("emits_act", "ACT_ESCALATION"),
                         ("allowed_to_act", "ACT_ESCALATION"), ("kernel_mutation", "KERNEL_MUTATION_ESCALATION"),
                         ("allowed_to_decide", "NON_KX108_AUTHORITY")):
        if boundary.get(key) is not False:
            hit(trigger, "app.harness.state_explicit.contracts.BOUNDARY", key, "False", repr(boundary.get(key)))
    if boundary.get("decision_authority") != "KX108_ONLY":
        hit("NON_KX108_AUTHORITY", "app.harness.state_explicit.contracts.BOUNDARY", "decision_authority",
            "KX108_ONLY", repr(boundary.get("decision_authority")))

    findings = []
    for trigger, surface, symbol, expected, observed in sorted(set(raw)):
        severity, invariant, action = TRIGGERS[trigger]
        fid = "secf_" + hashlib.sha256(json.dumps([bid, epoch, trigger, surface, symbol, observed],
                                                  ensure_ascii=False).encode("utf-8")).hexdigest()
        findings.append(SecurityFinding(
            finding_id=fid, boundary_id=bid, security_epoch=epoch, severity=severity, trigger=trigger,
            invariant=invariant, affected_surface=surface, symbol=symbol, expected=expected, observed=observed,
            evidence_refs=(f"{surface}:{symbol}", baseline["certified_by"]),
            reason=f"{trigger}: expected {expected}; observed {observed}", required_action=action))
    worst = max((f.severity for f in findings), key=lambda s: s.value, default=None)
    status = _STATUS[worst] if worst else SecurityBoundaryStatus.SAFE
    return SentinelReport(bid, epoch, status, tuple(findings))


def assert_boundary_safe(files: Mapping[str, str], **kw: Any) -> SentinelReport:
    """Fail closed for certification / CI: any finding raises SecurityHoldError."""
    report = scan(files, **kw)
    if report.status != SecurityBoundaryStatus.SAFE:
        raise SecurityHoldError(f"{report.boundary_id} epoch {report.security_epoch}: {report.status.value} "
                                f"({', '.join(sorted({f.trigger for f in report.findings}))})")
    return report


__all__ = ["SecuritySeverity", "SecurityBoundaryStatus", "SecurityFinding", "SentinelReport", "SecurityHoldError",
           "TRIGGERS", "repository_snapshot", "runtime_closure", "scan", "assert_boundary_safe"]
