from __future__ import annotations

import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()
OUT = ROOT / "docs" / "runtime"
OUT.mkdir(parents=True, exist_ok=True)

TS = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

TERMS = [
    "thermo", "thermodynamic", "thermodynamics", "energy",
    "coherence", "cohérence", "timeverse", "temporal", "time",
    "sigma", "mismatch", "anti_mismatch",
    "value_layer_scores", "hard_risks", "soft_risks",
    "stability_state", "usable_for_gencoin", "usable_for_value_layer",
]

ROUTE_TERMS = [
    "thermo", "energy", "coherence", "timeverse", "temporal",
    "sigma", "mismatch", "gencoin", "value", "brody"
]

SOURCE_ROOTS = [
    ROOT / "apps",
    ROOT / "periphery",
    ROOT / "tests",
    ROOT / "scripts",
]

IGNORE_PARTS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__",
    "dist", "build", ".pytest_cache"
}

EXTS = {".py", ".ts", ".tsx", ".json", ".md", ".txt", ".lean", ".yml", ".yaml"}

RUNTIME_MESSAGE = (
    "F19A2 readonly probe: expose thermodynamics, coherence, temporal/timeverse, "
    "sigma and anti-mismatch scoring without ACT, without write, without X108 mutation."
)

POST_PAYLOAD = {
    "message": RUNTIME_MESSAGE,
    "query": RUNTIME_MESSAGE,
    "text": RUNTIME_MESSAGE,
    "language": "fr",
    "session_id": "f19a2_route_probe",
    "readonly": True,
    "decision_authority": "KX108_ONLY",
    "memory_write": False,
    "graphiti_write": False,
    "kernel_mutation": False,
    "x108_mutation": False,
}

def http_json(url: str, method: str = "GET", payload: dict[str, Any] | None = None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode("utf-8", errors="replace")
            try:
                return {
                    "ok": True,
                    "status": r.status,
                    "json": json.loads(raw),
                    "raw_preview": raw[:1000],
                }
            except Exception:
                return {
                    "ok": True,
                    "status": r.status,
                    "json": None,
                    "raw_preview": raw[:2000],
                }
    except Exception as e:
        return {
            "ok": False,
            "status": 0,
            "error": f"{type(e).__name__}: {e}",
        }

def key_summary(obj: Any):
    if isinstance(obj, dict):
        return {
            "type": "dict",
            "keys": sorted(list(obj.keys()))[:80],
            "boundary": {
                "decision_authority": obj.get("decision_authority"),
                "readonly": obj.get("readonly"),
                "emits_act": obj.get("emits_act"),
                "emits_verdict": obj.get("emits_verdict"),
                "memory_write": obj.get("memory_write"),
                "graphiti_write": obj.get("graphiti_write"),
                "kernel_mutation": obj.get("kernel_mutation"),
                "x108_mutation": obj.get("x108_mutation"),
            },
        }
    if isinstance(obj, list):
        return {"type": "list", "count": len(obj)}
    return {"type": type(obj).__name__, "preview": str(obj)[:500]}

def numeric_count(obj: Any) -> int:
    if isinstance(obj, bool):
        return 0
    if isinstance(obj, (int, float)):
        return 1
    if isinstance(obj, dict):
        return sum(numeric_count(v) for v in obj.values())
    if isinstance(obj, list):
        return sum(numeric_count(v) for v in obj)
    return 0

def collect_term_paths(obj: Any, prefix: str = ""):
    out = []
    terms_l = [t.lower() for t in TERMS]

    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else str(k)
            if any(t in str(k).lower() for t in terms_l):
                preview = v
                if isinstance(v, (dict, list)):
                    preview = f"{type(v).__name__}[{len(v)}]"
                out.append({"path": path, "preview": preview})
            out.extend(collect_term_paths(v, path))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:60]):
            out.extend(collect_term_paths(v, f"{prefix}[{i}]"))

    return out[:300]

def discover_routes():
    openapi = http_json("http://127.0.0.1:8000/openapi.json")
    routes = []
    obj = openapi.get("json")
    if not isinstance(obj, dict):
        return {"openapi": openapi, "routes": routes}

    paths = obj.get("paths") or {}
    for route, methods in sorted(paths.items()):
        low = route.lower()
        if not any(t in low for t in ROUTE_TERMS):
            continue
        method_names = sorted([m.upper() for m in methods.keys() if isinstance(methods, dict)])
        routes.append({
            "route": route,
            "methods": method_names,
            "openapi_keys": sorted(list(methods.keys())) if isinstance(methods, dict) else [],
        })
    return {"openapi_status": openapi.get("status"), "routes": routes}

def probe_routes(routes):
    results = []
    for r in routes:
        route = r["route"]
        methods = r.get("methods") or []
        for method in methods:
            if method not in {"GET", "POST"}:
                continue
            url = "http://127.0.0.1:8000" + route
            payload = POST_PAYLOAD if method == "POST" else None
            res = http_json(url, method=method, payload=payload)
            entry = {
                "route": route,
                "method": method,
                "ok": res.get("ok"),
                "status": res.get("status"),
                "error": res.get("error"),
                "summary": key_summary(res.get("json")),
                "term_paths": collect_term_paths(res.get("json")) if res.get("json") is not None else [],
                "numeric_count": numeric_count(res.get("json")),
                "raw_preview": res.get("raw_preview", "")[:1000],
            }
            results.append(entry)
    return results

def post_brody(port: int):
    res = http_json(
        f"http://127.0.0.1:{port}/api/brody/chat",
        method="POST",
        payload=POST_PAYLOAD | {"session_id": f"f19a2_brody_payload_{port}"},
    )
    return res

def scan_sources():
    rx = re.compile("|".join(re.escape(t) for t in TERMS), re.IGNORECASE)
    results = []

    for root in SOURCE_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in IGNORE_PARTS for part in path.parts):
                continue
            if path.suffix.lower() not in EXTS:
                continue

            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                results.append({
                    "path": str(path.relative_to(ROOT)),
                    "read_error": f"{type(e).__name__}: {e}",
                })
                continue

            hits = []
            for i, line in enumerate(text.splitlines(), 1):
                if rx.search(line):
                    hits.append({"line": i, "text": line[:500]})
                    if len(hits) >= 20:
                        break

            if hits or rx.search(str(path)):
                results.append({
                    "path": str(path.relative_to(ROOT)),
                    "size": path.stat().st_size,
                    "hits": hits,
                })

            if len(results) >= 500:
                return results

    return results

def classify_sources(scan):
    counts = {}
    for item in scan:
        text = json.dumps(item, ensure_ascii=False).lower()
        if "thermo" in text or "energy" in text:
            c = "THERMO_ENERGY"
        elif "coherence" in text:
            c = "COHERENCE"
        elif "timeverse" in text or "temporal" in text:
            c = "TIME_TEMPORAL"
        elif "sigma" in text:
            c = "SIGMA"
        elif "mismatch" in text:
            c = "ANTI_MISMATCH"
        elif "gencoin" in text or "value_layer" in text:
            c = "VALUE_GENCOIN"
        else:
            c = "RELATED"
        counts[c] = counts.get(c, 0) + 1
    return counts

def extract_brody_summary(port, res):
    p = res.get("json")
    if not isinstance(p, dict):
        return {"port": port, "error": "not_json", "status": res.get("status")}

    thermo = p.get("thermodynamics_packet") or {}
    sigma = p.get("sigma_packet") or {}
    anti = p.get("anti_mismatch_packet") or p.get("anti_mismatch_snapshot") or {}
    gencoin = p.get("gencoin_shadow_packet") or {}
    temporal = p.get("temporal_context") or p.get("time_context") or {}

    return {
        "port": port,
        "status": res.get("status"),
        "source": p.get("source"),
        "decision_authority": p.get("decision_authority"),
        "readonly": p.get("readonly"),
        "emits_act": p.get("emits_act"),
        "memory_write": p.get("memory_write"),
        "graphiti_write": p.get("graphiti_write"),
        "kernel_mutation": p.get("kernel_mutation"),
        "x108_mutation": p.get("x108_mutation"),
        "thermo_keys": sorted(thermo.keys()) if isinstance(thermo, dict) else [],
        "thermo_scores": thermo.get("scores") if isinstance(thermo, dict) else None,
        "thermo_inputs": thermo.get("inputs") if isinstance(thermo, dict) else None,
        "thermo_stability_state": thermo.get("stability_state") if isinstance(thermo, dict) else None,
        "thermo_usable_for_gencoin": thermo.get("usable_for_gencoin") if isinstance(thermo, dict) else None,
        "thermo_usable_for_value_layer": thermo.get("usable_for_value_layer") if isinstance(thermo, dict) else None,
        "sigma_keys": sorted(sigma.keys()) if isinstance(sigma, dict) else [],
        "anti_keys": sorted(anti.keys()) if isinstance(anti, dict) else [],
        "gencoin_keys": sorted(gencoin.keys()) if isinstance(gencoin, dict) else [],
        "temporal_keys": sorted(temporal.keys()) if isinstance(temporal, dict) else [],
        "term_paths": collect_term_paths(p)[:120],
        "numeric_count": numeric_count(thermo) + numeric_count(sigma) + numeric_count(anti) + numeric_count(gencoin) + numeric_count(temporal),
    }

def main():
    discovered = discover_routes()
    route_probes = probe_routes(discovered["routes"])

    brody_8000 = post_brody(8000)
    brody_8012 = post_brody(8012)
    summary_8000 = extract_brody_summary(8000, brody_8000)
    summary_8012 = extract_brody_summary(8012, brody_8012)

    source_scan = scan_sources()
    source_counts = classify_sources(source_scan)

    working_routes = [
        p for p in route_probes
        if p.get("ok") and p.get("status") and int(p["status"]) < 400
    ]

    if working_routes and summary_8000.get("thermo_scores"):
        classification = "EXISTING_ROUTES_AND_THERMO_PACKET_NEED_UNIFICATION"
    elif summary_8000.get("thermo_scores"):
        classification = "THERMO_PACKET_PRESENT_BUT_ROUTE_PARITY_UNKNOWN"
    else:
        classification = "PARTIAL_SIGNAL_ONLY_NEEDS_SCORING_ADAPTER"

    report = {
        "checkpoint": "F19A2_TARGETED_THERMO_COHERENCE_TIME_ROUTE_SOURCE_AUDIT",
        "mode": "READ_ONLY",
        "timestamp": TS,
        "classification": classification,
        "discovered_routes": discovered["routes"],
        "route_probes": route_probes,
        "working_routes": working_routes,
        "brody_summary_8000": summary_8000,
        "brody_summary_8012": summary_8012,
        "source_scan_counts": source_counts,
        "source_scan_sample": source_scan[:120],
        "boundary": {
            "decision_authority": summary_8000.get("decision_authority"),
            "readonly": summary_8000.get("readonly"),
            "emits_act": summary_8000.get("emits_act"),
            "memory_write": summary_8000.get("memory_write"),
            "graphiti_write": summary_8000.get("graphiti_write"),
            "kernel_mutation": summary_8000.get("kernel_mutation"),
            "x108_mutation": summary_8000.get("x108_mutation"),
        },
        "next": "F19B should unify Brody thermodynamics_packet with working energy/coherence/time routes, preserving readonly KX108_ONLY.",
    }

    out_json = OUT / f"OBSIDIA_F19A2_TARGETED_THERMO_COHERENCE_TIME_AUDIT_{TS}.json"
    out_txt = OUT / f"OBSIDIA_F19A2_TARGETED_THERMO_COHERENCE_TIME_AUDIT_{TS}.txt"
    brody_8000_path = OUT / f"F19A2_BRODY_PAYLOAD_8000_{TS}.json"
    brody_8012_path = OUT / f"F19A2_BRODY_PAYLOAD_8012_{TS}.json"
    routes_path = OUT / f"F19A2_ROUTE_PROBES_{TS}.json"
    scan_path = OUT / f"F19A2_SOURCE_SCAN_{TS}.json"

    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    brody_8000_path.write_text(json.dumps(brody_8000, ensure_ascii=False, indent=2), encoding="utf-8")
    brody_8012_path.write_text(json.dumps(brody_8012, ensure_ascii=False, indent=2), encoding="utf-8")
    routes_path.write_text(json.dumps(route_probes, ensure_ascii=False, indent=2), encoding="utf-8")
    scan_path.write_text(json.dumps(source_scan, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "OBSIDIA F19A2 TARGETED THERMO / COHERENCE / TIME AUDIT",
        f"timestamp={TS}",
        "mode=READ_ONLY",
        f"classification={classification}",
        "",
        "BRODY_8000:",
        f"thermo_scores={summary_8000.get('thermo_scores')}",
        f"thermo_inputs={summary_8000.get('thermo_inputs')}",
        f"thermo_stability_state={summary_8000.get('thermo_stability_state')}",
        f"thermo_usable_for_gencoin={summary_8000.get('thermo_usable_for_gencoin')}",
        f"thermo_usable_for_value_layer={summary_8000.get('thermo_usable_for_value_layer')}",
        f"numeric_count={summary_8000.get('numeric_count')}",
        "",
        "WORKING_ROUTES:",
    ]

    for p in working_routes:
        lines.append(f"{p.get('method')} {p.get('route')} status={p.get('status')} numeric_count={p.get('numeric_count')} keys={p.get('summary', {}).get('keys')}")

    lines.extend([
        "",
        "SOURCE_SCAN_COUNTS:",
    ])
    for k, v in sorted(source_counts.items()):
        lines.append(f"{k}={v}")

    lines.extend([
        "",
        "BOUNDARY:",
        f"decision_authority={summary_8000.get('decision_authority')}",
        f"readonly={summary_8000.get('readonly')}",
        f"emits_act={summary_8000.get('emits_act')}",
        f"memory_write={summary_8000.get('memory_write')}",
        f"graphiti_write={summary_8000.get('graphiti_write')}",
        f"kernel_mutation={summary_8000.get('kernel_mutation')}",
        f"x108_mutation={summary_8000.get('x108_mutation')}",
        "",
        "FILES:",
        str(out_json),
        str(out_txt),
        str(brody_8000_path),
        str(brody_8012_path),
        str(routes_path),
        str(scan_path),
    ])

    out_txt.write_text("\n".join(lines), encoding="utf-8")

    print("F19A2_TARGETED_THERMO_COHERENCE_TIME_AUDIT_DONE")
    print("REPORT_JSON=" + str(out_json))
    print("REPORT_TXT=" + str(out_txt))
    print("CLASSIFICATION=" + classification)
    print("WORKING_ROUTES_COUNT=" + str(len(working_routes)))
    for p in working_routes[:20]:
        print(f"WORKING_ROUTE={p.get('method')} {p.get('route')} status={p.get('status')} numeric_count={p.get('numeric_count')}")
    print("THERMO_SCORES_8000=" + json.dumps(summary_8000.get("thermo_scores"), ensure_ascii=False))
    print("THERMO_INPUTS_8000=" + json.dumps(summary_8000.get("thermo_inputs"), ensure_ascii=False))
    print("SOURCE_SCAN_COUNTS=" + json.dumps(source_counts, ensure_ascii=False))

if __name__ == "__main__":
    main()
