from __future__ import annotations

import importlib.util
import json
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B")
BASE = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core")
OUT = ROOT / "docs" / "runtime"
OUT.mkdir(parents=True, exist_ok=True)

TS = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

MMONDE = BASE / "obsidia-engine-candidate" / "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_FREEZE_CANDIDATE" / "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1"

CANDIDATES = {
    "repo_periphery_reverse_os": ROOT / "periphery" / "reverse_os.py",
    "repo_periphery_test_reverse_os": ROOT / "periphery" / "test_reverse_os_non_decision.py",
    "zip2_bridge_reverse_os_adapter": BASE / "obsidia-engine-candidate" / "bridge" / "zip2_reverse_os_real_adapter.py",
    "mmonde_reverse_os": MMONDE / "06_REVERSE_OS_SSR_JARVIS" / "reverse_os.py",
    "mmonde_semantic_mapper": MMONDE / "06_REVERSE_OS_SSR_JARVIS" / "semantic_mapper.py",
    "mmonde_jarvis_projection": MMONDE / "06_REVERSE_OS_SSR_JARVIS" / "jarvis_projection.py",
    "mmonde_active_cognitive_reduction": MMONDE / "06_REVERSE_OS_SSR_JARVIS" / "active_cognitive_reduction.py",
    "mmonde_common_types": MMONDE / "common_types.py",
    "mmonde_obsidia_ir": MMONDE / "09_MCP_BRIDGE_OBSIDIA_IR" / "obsidia_ir.py",
    "mmonde_demo_full_pipeline": MMONDE / "20_DEMO_MINIMALE" / "demo_full_pipeline.py",
    "mmonde_test_reverse_os_non_decision": MMONDE / "17_TESTS" / "test_reverse_os_non_decision.py",
}

FLOW = {
    "agent_name": "F18A4_AUDIT_AGENT",
    "reason_code": "RC_X108_REQUIRED",
    "merkle_root": "F18A4_READONLY_MERKLE_PLACEHOLDER",
    "verdict": "NO_KERNEL_DECISION",
    "tree_vector": [0.0, 0.12, 0.01, 0.4, 0.2, 0.0, 0.7] + [0.0] * 27,
    "non_decision": True,
    "decision_authority": "KX108_ONLY",
}

PACKET = {
    "packet_id": "F18A4_READONLY_PACKET",
    "query": "write Graphiti memory + canon -> DOMAIN_RACCORD_WRITE_BOUNDARY",
    "activated_trees": [
        "TREE_CODE_IR_PROJECTION",
        "TREE_MEMORY_GRAPH",
        "TREE_CANON_BOUNDARY",
    ],
    "requires_x108": True,
    "non_decision": True,
    "decision_authority": "KX108_ONLY",
    "readonly": True,
    "memory_write": False,
    "graphiti_write": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "emits_act": False,
}

def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def safe_call(label: str, fn, *args, **kwargs) -> dict[str, Any]:
    try:
        out = fn(*args, **kwargs)
        return {
            "label": label,
            "ok": True,
            "output": out,
            "output_type": type(out).__name__,
        }
    except Exception as e:
        return {
            "label": label,
            "ok": False,
            "error": f"{type(e).__name__}: {e}",
            "traceback": traceback.format_exc()[-3000:],
        }

def inspect_module(label: str, path: Path) -> dict[str, Any]:
    item: dict[str, Any] = {
        "label": label,
        "path": str(path),
        "exists": path.exists(),
        "size": path.stat().st_size if path.exists() else None,
        "load_ok": False,
        "functions": [],
        "classes": [],
        "calls": [],
    }
    if not path.exists():
        return item

    try:
        mod = load_module(f"f18a4_{label}", path)
        item["load_ok"] = True
        item["functions"] = sorted([x for x in dir(mod) if callable(getattr(mod, x, None)) and not x.startswith("_")])
        item["classes"] = sorted([x for x in dir(mod) if isinstance(getattr(mod, x, None), type)])
    except Exception as e:
        item["load_error"] = f"{type(e).__name__}: {e}"
        item["load_traceback"] = traceback.format_exc()[-3000:]
        return item

    # Known safe calls only. No demo_full_pipeline.main because it writes files.
    if hasattr(mod, "project"):
        item["calls"].append(safe_call(f"{label}.project", mod.project, FLOW))

    if hasattr(mod, "map_reason_code"):
        item["calls"].append(safe_call(f"{label}.map_reason_code", mod.map_reason_code, "RC_X108_REQUIRED"))

    if hasattr(mod, "project_to_ui"):
        item["calls"].append(safe_call(f"{label}.project_to_ui", mod.project_to_ui, {"text": "projection readonly", "non_decision": True}))

    if hasattr(mod, "reduce"):
        item["calls"].append(safe_call(f"{label}.reduce", mod.reduce, FLOW["tree_vector"], top_n=3))

    if hasattr(mod, "build_reverse_flow"):
        item["calls"].append(safe_call(f"{label}.build_reverse_flow", mod.build_reverse_flow, PACKET))

    if hasattr(mod, "enrich_reverse_os"):
        item["calls"].append(safe_call(f"{label}.enrich_reverse_os", mod.enrich_reverse_os, PACKET))

    return item

def boundary_eval(results: list[dict[str, Any]]) -> dict[str, Any]:
    text = json.dumps(results, ensure_ascii=False)

    return {
        "contains_non_decision_true": '"non_decision": true' in text.lower(),
        "contains_kx108_only": "KX108_ONLY" in text,
        "contains_forbidden_decision_field": '"decision"' in text.lower(),
        "contains_act_string": "ACT" in text,
        "contains_kernel_mutation_true": '"kernel_mutation": true' in text.lower(),
        "contains_memory_write_true": '"memory_write": true' in text.lower(),
        "contains_graphiti_write_true": '"graphiti_write": true' in text.lower(),
    }

def main():
    results = []
    for label, path in CANDIDATES.items():
        results.append(inspect_module(label, path))

    boundary = boundary_eval(results)

    recommended = {
        "reuse_strategy": "ADAPT_EXISTING_REAL_BRIDGE_NOT_NAIVE_NEW_ADAPTER",
        "primary_candidate": "obsidia-engine-candidate/bridge/zip2_reverse_os_real_adapter.py",
        "support_candidates": [
            "periphery/reverse_os.py",
            "MMONDE/06_REVERSE_OS_SSR_JARVIS/reverse_os.py",
            "MMONDE/06_REVERSE_OS_SSR_JARVIS/semantic_mapper.py",
            "MMONDE/06_REVERSE_OS_SSR_JARVIS/jarvis_projection.py",
            "MMONDE/06_REVERSE_OS_SSR_JARVIS/active_cognitive_reduction.py",
            "MMONDE/common_types.py",
            "MMONDE/09_MCP_BRIDGE_OBSIDIA_IR/obsidia_ir.py",
            "MMONDE/17_TESTS/test_reverse_os_non_decision.py",
        ],
        "note": "Do not call demo_full_pipeline.main directly in runtime because it writes demo outputs. Use it as architecture reference only.",
    }

    report = {
        "checkpoint": "F18A4_EXISTING_CANDIDATE_EXECUTION_AUDIT",
        "mode": "READ_ONLY",
        "timestamp": TS,
        "results": results,
        "boundary_eval": boundary,
        "recommended": recommended,
    }

    out_json = OUT / f"OBSIDIA_F18A4_EXISTING_CANDIDATE_EXECUTION_AUDIT_{TS}.json"
    out_txt = OUT / f"OBSIDIA_F18A4_EXISTING_CANDIDATE_EXECUTION_AUDIT_{TS}.txt"

    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "OBSIDIA F18A4 EXISTING CANDIDATE EXECUTION AUDIT",
        f"timestamp={TS}",
        "mode=READ_ONLY",
        "",
        "BOUNDARY_EVAL:",
    ]
    for k, v in boundary.items():
        lines.append(f"{k}={v}")

    lines.extend([
        "",
        "MODULE RESULTS:",
    ])

    for r in results:
        lines.append("--------------------------------------------------")
        lines.append(f"label={r['label']}")
        lines.append(f"path={r['path']}")
        lines.append(f"exists={r['exists']}")
        lines.append(f"load_ok={r.get('load_ok')}")
        if r.get("load_error"):
            lines.append(f"load_error={r.get('load_error')}")
        lines.append("functions=" + ", ".join(r.get("functions", [])[:20]))
        for c in r.get("calls", []):
            lines.append(f"CALL={c.get('label')} ok={c.get('ok')}")
            if c.get("ok"):
                preview = json.dumps(c.get("output"), ensure_ascii=False)[:1000]
                lines.append(f"OUTPUT={preview}")
            else:
                lines.append(f"ERROR={c.get('error')}")

    lines.extend([
        "",
        "RECOMMENDED:",
        json.dumps(recommended, ensure_ascii=False, indent=2),
    ])

    out_txt.write_text("\n".join(lines), encoding="utf-8")

    print("F18A4_EXISTING_CANDIDATE_EXECUTION_AUDIT_DONE")
    print("REPORT_JSON=" + str(out_json))
    print("REPORT_TXT=" + str(out_txt))
    print("BOUNDARY_EVAL=" + json.dumps(boundary, ensure_ascii=False))
    print("PRIMARY_CANDIDATE=" + recommended["primary_candidate"])
    for r in results:
        print(f"{r['label']} exists={r['exists']} load_ok={r.get('load_ok')} calls={len(r.get('calls', []))}")

if __name__ == "__main__":
    main()
