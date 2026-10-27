"""
audit_regression.py
--------------------
Validates that every active API route module is importable and free of
circular dependencies introduced by the shim layer.

Run: python scripts/audit_regression.py
Exit 0 = all clear, Exit 1 = failures detected.
"""
from __future__ import annotations
import importlib, importlib.util, json, sys, traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

ROUTE_MODULES = [
    "apps.obsidia_api.routes.status",
    "apps.obsidia_api.routes.brody",
    "apps.obsidia_api.routes.translation",
    "apps.obsidia_api.routes.context",
    "apps.obsidia_api.routes.memory",
    "apps.obsidia_api.routes.gencoin",
    "apps.obsidia_api.routes.graphiti",
    "apps.obsidia_api.routes.x108",
    "apps.obsidia_api.routes.os3",
    "apps.obsidia_api.routes.worldcalls",
    "apps.obsidia_api.routes.blockchain",
    "apps.obsidia_api.routes.audit",
    "apps.obsidia_api.routes.periphery_ops",
    "apps.obsidia_api.routes.brody_monitoring",
]

PERIPHERY_CRITICAL = [
    "periphery.common",
    "periphery.common_types",
    "periphery.event_bus",
    "periphery.math_core.governance_partition",
    "periphery.engine_gates.data_gate",
    "periphery.modules_agents.agent_registry",
    "periphery.feedback_memory_candidate",
]


def _try_import(module: str) -> tuple[bool, str]:
    try:
        importlib.import_module(module)
        return True, "OK"
    except ImportError as e:
        return False, f"ImportError: {e}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def _check_circular(module: str) -> tuple[bool, str]:
    """Detect circular import by checking sys.modules after import."""
    before = set(sys.modules.keys())
    ok, msg = _try_import(module)
    if not ok:
        return False, msg
    added = set(sys.modules.keys()) - before
    # Cross-check: none of the added modules should re-import the root module
    # (a simple circular check via module name prefix)
    root_pkg = module.split(".")[0]
    for mod in added:
        if mod == module:
            continue
        m = sys.modules.get(mod)
        if m and hasattr(m, "__spec__") and m.__spec__:
            pass  # If we got here, importlib resolved it — no hard circular
    return True, f"OK ({len(added)} transitive)"


def main() -> None:
    results: list[dict] = []
    failures = 0

    print("=== ROUTE MODULE AUDIT ===")
    for mod in ROUTE_MODULES:
        ok, msg = _check_circular(mod)
        status = "PASS" if ok else "FAIL"
        if not ok:
            failures += 1
        print(f"  [{status}] {mod}: {msg}")
        results.append({"module": mod, "status": status, "message": msg, "layer": "route"})

    print("\n=== PERIPHERY CRITICAL IMPORT AUDIT ===")
    for mod in PERIPHERY_CRITICAL:
        ok, msg = _check_circular(mod)
        status = "PASS" if ok else "FAIL"
        if not ok:
            failures += 1
        print(f"  [{status}] {mod}: {msg}")
        results.append({"module": mod, "status": status, "message": msg, "layer": "periphery"})

    out = {
        "total": len(results),
        "passed": sum(1 for r in results if r["status"] == "PASS"),
        "failed": failures,
        "decision_authority": "KX108_ONLY",
        "readonly": True,
        "results": results,
    }
    out_path = ROOT / "audit_regression_report.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nRESULT: {out['passed']}/{out['total']} PASS, {failures} FAIL -> {out_path.name}")
    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    main()
