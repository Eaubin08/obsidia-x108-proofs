"""
audit_event_bus_connectability.py
-----------------------------------
Validates that periphery/event_bus.py is importable and has no forbidden
dependencies (bus must not import from sigma/, kernel/, brody/ directly).

Produces: event_bus_connectability_report.json + .md

Run: python scripts/audit_event_bus_connectability.py
Exit 0 = PASS, Exit 1 = FAIL
"""
from __future__ import annotations
import ast, importlib, json, re, sys, traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

FORBIDDEN_DEPS = [
    "sigma",
    "proofs.lean",
    "formal.tla",
    "kernel",
    "brody_local",
    "neo4j",
    "graphiti",
]

EVENT_BUS_MODULE = "periphery.event_bus"
REQUIRED_CLASSES = ["UniversalEventBus", "EventEnvelope", "BrodyEventConsumer",
                    "SigmaEventObserver", "AuditEventWriter", "EventType"]
REQUIRED_FUNCTIONS = ["get_bus", "build_standard_bus"]


def _check_importable() -> tuple[bool, str]:
    try:
        mod = importlib.import_module(EVENT_BUS_MODULE)
        return True, f"OK (module id: {id(mod)})"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def _check_api(mod) -> list[str]:
    missing = []
    for name in REQUIRED_CLASSES + REQUIRED_FUNCTIONS:
        if not hasattr(mod, name):
            missing.append(name)
    return missing


def _check_forbidden_imports(src: str) -> list[str]:
    hits = []
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return ["SYNTAX_ERROR"]
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.ImportFrom) and node.module:
                mod_name = node.module
            elif isinstance(node, ast.Import):
                mod_name = ".".join(a.name for a in node.names)
            else:
                continue
            for forbidden in FORBIDDEN_DEPS:
                if mod_name.startswith(forbidden):
                    hits.append(f"{mod_name} (matches '{forbidden}')")
    return hits


def _scan_all_files() -> dict[str, list[str]]:
    """Scan all periphery Python files for imports of the bus."""
    connected: list[str] = []
    excluded = {".venv", "__pycache__", ".git", "archives", "demos", "Demo-obsidia-x108-proof"}
    for f in ROOT.rglob("*.py"):
        if any(x in f.parts for x in excluded):
            continue
        try:
            src = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "event_bus" in src or "EventEnvelope" in src or "UniversalEventBus" in src:
            connected.append(f.relative_to(ROOT).as_posix())
    return {"connected_files": connected}


def main() -> None:
    warnings: list[str] = []
    errors: list[str] = []

    # 1. Importability
    ok, msg = _check_importable()
    if not ok:
        errors.append(f"IMPORT_FAIL: {msg}")

    # 2. API surface
    missing_api: list[str] = []
    if ok:
        import periphery.event_bus as eb_mod
        missing_api = _check_api(eb_mod)
        if missing_api:
            errors.append(f"MISSING_API: {missing_api}")

    # 3. Forbidden deps in bus source
    bus_src_path = ROOT / "periphery" / "event_bus.py"
    forbidden_hits: list[str] = []
    if bus_src_path.exists():
        forbidden_hits = _check_forbidden_imports(bus_src_path.read_text(encoding="utf-8"))
        if forbidden_hits:
            errors.append(f"FORBIDDEN_DEPS: {forbidden_hits}")
    else:
        errors.append("BUS_FILE_NOT_FOUND")

    # 4. Connectivity scan
    scan = _scan_all_files()
    if len(scan["connected_files"]) == 0:
        warnings.append("NO_FILES_REFERENCE_BUS_YET — bus exists but not wired to any module")

    result = "PASS" if not errors else "FAIL"
    report = {
        "result": result,
        "bus_module": EVENT_BUS_MODULE,
        "importable": ok,
        "import_message": msg if ok else errors[0] if errors else "",
        "missing_api": missing_api,
        "forbidden_dependency_count": len(forbidden_hits),
        "forbidden_deps": forbidden_hits,
        "module_errors_count": len(errors),
        "errors": errors,
        "warnings": warnings,
        "connected_files": scan["connected_files"],
        "scanned_files": "all periphery/**/*.py",
        "decision_authority": "KX108_ONLY",
        "readonly": True,
        "emits_act": False,
    }

    json_out = ROOT / "event_bus_connectability_report.json"
    md_out = ROOT / "event_bus_connectability_report.md"

    json_out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# Event Bus Connectability Report",
        f"**Result:** {result}",
        f"**Bus module:** `{EVENT_BUS_MODULE}`",
        f"**Importable:** {ok}",
        f"**Missing API:** {missing_api or 'none'}",
        f"**Forbidden deps:** {len(forbidden_hits)}",
        f"**Errors:** {len(errors)}",
        f"**Warnings:** {len(warnings)}",
        f"**decision_authority:** KX108_ONLY",
        "",
        "## Files referencing bus",
    ]
    for f in scan["connected_files"]:
        lines.append(f"- `{f}`")
    if not scan["connected_files"]:
        lines.append("_None yet._")
    md_out.write_text("\n".join(lines), encoding="utf-8")

    tag = "EVENT_BUS_CONNECTABILITY_AUDIT_PASS" if result == "PASS" else "EVENT_BUS_CONNECTABILITY_AUDIT_FAIL"
    print(f"{tag}: importable={ok}, forbidden={len(forbidden_hits)}, errors={len(errors)}, warnings={len(warnings)}")
    for e in errors:
        print(f"  ERROR: {e}")
    for w in warnings:
        print(f"  WARN:  {w}")

    sys.exit(0 if result == "PASS" else 1)


if __name__ == "__main__":
    main()
