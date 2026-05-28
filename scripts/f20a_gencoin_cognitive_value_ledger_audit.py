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

MESSAGE = (
    "F20 audit readonly: expose gencoin_shadow_packet, value_layer, "
    "thermo_unified_packet, ledger status, cognitive value, proof value, reuse value, "
    "sans mint, sans wallet, sans blockchain, sans ACT, sans mutation X108."
)

POST = {
    "message": MESSAGE,
    "language": "fr",
    "session_id": "f20a_gencoin_value_ledger_audit",
}

TERMS = [
    "gencoin", "GENCOIN", "shadow_value", "gencoin_shadow_packet",
    "value_layer", "cognitive_value", "proof_value", "reuse_value",
    "memory_value", "attention_cost", "energy_cost", "stability_value",
    "economic_projection", "ledger", "mint", "wallet", "token",
    "blockchain", "usable_shadow_value", "usable_for_gencoin",
    "final_scoring_enabled", "economic_scoring_enabled",
]

SOURCE_ROOTS = [
    ROOT / "apps",
    ROOT / "periphery",
    ROOT / "tests",
    ROOT / "scripts",
]

EXTS = {".py", ".ts", ".tsx", ".json", ".md", ".txt", ".lean", ".yml", ".yaml"}
IGNORE = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".pytest_cache"}

def http_json(url: str, method: str = "GET", payload: dict[str, Any] | None = None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode("utf-8", errors="replace")
            try:
                return {"ok": True, "status": r.status, "json": json.loads(raw), "raw": raw[:2000]}
            except Exception:
                return {"ok": True, "status": r.status, "json": None, "raw": raw[:2000]}
    except Exception as e:
        return {"ok": False, "status": 0, "error": f"{type(e).__name__}: {e}"}

def post_brody(port: int):
    body = dict(POST)
    body["session_id"] = f"f20a_gencoin_value_ledger_audit_{port}"
    return http_json(f"http://127.0.0.1:{port}/api/brody/chat", "POST", body)

def collect_paths(obj: Any, terms: list[str], prefix: str = ""):
    out = []
    terms_l = [t.lower() for t in terms]
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else str(k)
            if any(t in str(k).lower() for t in terms_l):
                preview = v
                if isinstance(v, (dict, list)):
                    preview = f"{type(v).__name__}[{len(v)}]"
                out.append({"path": path, "preview": preview})
            out.extend(collect_paths(v, terms, path))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:80]):
            out.extend(collect_paths(v, terms, f"{prefix}[{i}]"))
    return out[:500]

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

def extract_summary(port: int, res: dict[str, Any]):
    p = res.get("json")
    if not isinstance(p, dict):
        return {"port": port, "error": "not_json", "status": res.get("status")}

    g = p.get("gencoin_shadow_packet") or {}
    vl = p.get("value_layer") or {}
    tu = p.get("thermo_unified_packet") or {}
    thermo = p.get("thermodynamics_packet") or {}
    sigma = p.get("sigma_packet") or {}
    anti = p.get("anti_mismatch_packet") or {}
    guard = p.get("memory_promotion_guard_packet") or {}

    shadow_scores = g.get("shadow_scores") if isinstance(g, dict) else None
    value_scores = vl.get("scores") if isinstance(vl, dict) else None

    classification = "UNKNOWN"
    if isinstance(g, dict) and g.get("version") == "GENCOIN_SHADOW_VALUE_PACKET_V1":
        if g.get("usable_shadow_value") is True and isinstance(shadow_scores, dict):
            classification = "SHADOW_VALUE_REAL_PRESENT_LEDGER_NOT_FINAL"
        elif isinstance(shadow_scores, dict):
            classification = "SHADOW_VALUE_PACKET_PRESENT_BUT_NOT_USABLE"
        else:
            classification = "GENCOIN_PACKET_PRESENT_NO_SCORES"
    else:
        classification = "GENCOIN_RUNTIME_PACKET_ABSENT"

    if isinstance(vl, dict) and value_scores in (None, {}, []) and isinstance(g, dict) and g.get("usable_shadow_value") is True:
        classification = "SHADOW_VALUE_REAL_VALUE_LAYER_NULL"

    return {
        "port": port,
        "http_status": res.get("status"),
        "source": p.get("source"),
        "graphiti_status": p.get("graphiti_status"),
        "decision_authority": p.get("decision_authority"),
        "readonly": p.get("readonly"),
        "emits_act": p.get("emits_act"),
        "emits_verdict": p.get("emits_verdict"),
        "memory_write": p.get("memory_write"),
        "graphiti_write": p.get("graphiti_write"),
        "kernel_mutation": p.get("kernel_mutation"),
        "x108_mutation": p.get("x108_mutation"),

        "gencoin_present": bool(g),
        "gencoin_version": g.get("version") if isinstance(g, dict) else None,
        "gencoin_mode": g.get("mode") if isinstance(g, dict) else None,
        "usable_shadow_value": g.get("usable_shadow_value") if isinstance(g, dict) else None,
        "final_scoring_enabled": g.get("final_scoring_enabled") if isinstance(g, dict) else None,
        "economic_scoring_enabled": g.get("economic_scoring_enabled") if isinstance(g, dict) else None,
        "blockchain_enabled": g.get("blockchain_enabled") if isinstance(g, dict) else None,
        "memory_promotion_enabled": g.get("memory_promotion_enabled") if isinstance(g, dict) else None,
        "shadow_scores": shadow_scores,
        "shadow_scores_numeric_count": numeric_count(shadow_scores),
        "gencoin_reason": g.get("reason") if isinstance(g, dict) else None,

        "value_layer_present": bool(vl),
        "value_layer_keys": sorted(vl.keys()) if isinstance(vl, dict) else [],
        "value_layer_scores": value_scores,
        "value_layer_scores_numeric_count": numeric_count(value_scores),

        "thermo_unified_present": bool(tu),
        "thermo_unified_status": tu.get("status") if isinstance(tu, dict) else None,
        "thermo_unified_usable_for_gencoin": tu.get("usable_for_gencoin") if isinstance(tu, dict) else None,
        "thermo_unified_composite_temperature": tu.get("composite_temperature") if isinstance(tu, dict) else None,

        "thermodynamics_usable_for_gencoin": thermo.get("usable_for_gencoin") if isinstance(thermo, dict) else None,
        "sigma_usable_for_gencoin": sigma.get("usable_for_gencoin") if isinstance(sigma, dict) else None,
        "anti_mismatch_risk_level": anti.get("risk_level") if isinstance(anti, dict) else None,

        "memory_guard_status": guard.get("status") if isinstance(guard, dict) else None,
        "memory_guard_allows_promotion": guard.get("allows_promotion") if isinstance(guard, dict) else None,

        "term_paths": collect_paths(p, TERMS),
        "classification": classification,
    }

def discover_routes():
    openapi = http_json("http://127.0.0.1:8000/openapi.json")
    routes = []
    obj = openapi.get("json")
    if isinstance(obj, dict):
        for route, methods in sorted((obj.get("paths") or {}).items()):
            low = route.lower()
            if any(t in low for t in ["gencoin", "ledger", "token", "wallet", "blockchain", "value"]):
                routes.append({
                    "route": route,
                    "methods": sorted([m.upper() for m in methods.keys()]) if isinstance(methods, dict) else [],
                })
    return routes

def probe_routes(routes):
    out = []
    for r in routes:
        for method in r.get("methods") or []:
            if method not in {"GET", "POST"}:
                continue
            url = "http://127.0.0.1:8000" + r["route"]
            payload = {
                "action_id": "F20A_READONLY_AUDIT",
                "utility": 0.5,
                "coherence": 0.8,
                "stability": 0.8,
                "cost": 0.1,
                "risk": 0.1,
            } if method == "POST" else None
            res = http_json(url, method, payload)
            j = res.get("json")
            out.append({
                "route": r["route"],
                "method": method,
                "ok": res.get("ok"),
                "status": res.get("status"),
                "error": res.get("error"),
                "keys": sorted(j.keys()) if isinstance(j, dict) else [],
                "summary": {
                    "decision_authority": j.get("decision_authority") if isinstance(j, dict) else None,
                    "readonly": j.get("readonly") if isinstance(j, dict) else None,
                    "emits_act": j.get("emits_act") if isinstance(j, dict) else None,
                    "source": j.get("source") if isinstance(j, dict) else None,
                    "status": j.get("status") if isinstance(j, dict) else None,
                    "total": j.get("total") if isinstance(j, dict) else None,
                    "count": j.get("count") if isinstance(j, dict) else None,
                    "reason": j.get("reason") if isinstance(j, dict) else None,
                    "no_wallet": j.get("no_wallet") if isinstance(j, dict) else None,
                    "no_mint": j.get("no_mint") if isinstance(j, dict) else None,
                    "is_real_token": j.get("is_real_token") if isinstance(j, dict) else None,
                },
                "term_paths": collect_paths(j, TERMS) if isinstance(j, dict) else [],
                "numeric_count": numeric_count(j),
            })
    return out

def scan_sources():
    rx = re.compile("|".join(re.escape(t) for t in TERMS), re.IGNORECASE)
    results = []

    for root in SOURCE_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in IGNORE for part in path.parts):
                continue
            if path.suffix.lower() not in EXTS:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                results.append({"path": str(path.relative_to(ROOT)), "read_error": str(e)})
                continue

            hits = []
            for i, line in enumerate(text.splitlines(), 1):
                if rx.search(line):
                    hits.append({"line": i, "text": line[:500]})
                    if len(hits) >= 25:
                        break
            if hits or rx.search(str(path)):
                results.append({
                    "path": str(path.relative_to(ROOT)),
                    "size": path.stat().st_size,
                    "hits": hits,
                })
            if len(results) >= 700:
                return results

    return results

def classify_sources(scan):
    counts = {}
    for item in scan:
        text = json.dumps(item, ensure_ascii=False).lower()
        if "brody_gencoin_shadow_value" in text:
            c = "BRODY_GENCOIN_SHADOW_VALUE"
        elif "gencoin_transverse" in text:
            c = "GENCOIN_TRANSVERSE_INTERFACE"
        elif "routes/gencoin" in text or "/api/gencoin" in text:
            c = "GENCOIN_LEDGER_ROUTE"
        elif "gencoin_sandbox" in text:
            c = "GENCOIN_SANDBOX"
        elif "ledger" in text:
            c = "LEDGER_SOURCE"
        elif "blockchain" in text or "wallet" in text or "mint" in text:
            c = "BLOCKCHAIN_TOKEN_BOUNDARY"
        elif "value_layer" in text or "cognitive_value" in text:
            c = "VALUE_LAYER_SOURCE"
        else:
            c = "RELATED"
        counts[c] = counts.get(c, 0) + 1
    return counts

def main():
    p8000 = post_brody(8000)
    p8012 = post_brody(8012)

    s8000 = extract_summary(8000, p8000)
    s8012 = extract_summary(8012, p8012)

    routes = discover_routes()
    route_probes = probe_routes(routes)
    source_scan = scan_sources()
    source_counts = classify_sources(source_scan)

    ledger_probe = http_json("http://127.0.0.1:8000/api/gencoin", "GET")
    ledger_json = ledger_probe.get("json") if isinstance(ledger_probe.get("json"), dict) else {}

    if s8000.get("classification") == "SHADOW_VALUE_REAL_VALUE_LAYER_NULL" and ledger_json.get("status") == "LIVE_EMPTY_REGISTRY":
        classification = "SHADOW_VALUE_REAL_LEDGER_EMPTY_NEEDS_READONLY_COGNITIVE_LEDGER"
    elif s8000.get("classification") == "SHADOW_VALUE_REAL_PRESENT_LEDGER_NOT_FINAL":
        classification = "SHADOW_VALUE_REAL_LEDGER_PARITY_NEEDS_VALIDATION"
    elif s8000.get("gencoin_present"):
        classification = "GENCOIN_PRESENT_PARTIAL"
    else:
        classification = "GENCOIN_RUNTIME_ABSENT"

    report = {
        "checkpoint": "F20A_GENCOIN_COGNITIVE_VALUE_LEDGER_AUDIT",
        "mode": "READ_ONLY",
        "timestamp": TS,
        "classification": classification,
        "brody_summary_8000": s8000,
        "brody_summary_8012": s8012,
        "routes": routes,
        "route_probes": route_probes,
        "ledger_probe": ledger_json,
        "source_scan_counts": source_counts,
        "source_scan_sample": source_scan[:160],
        "boundary": {
            "decision_authority": s8000.get("decision_authority"),
            "readonly": s8000.get("readonly"),
            "emits_act": s8000.get("emits_act"),
            "emits_verdict": s8000.get("emits_verdict"),
            "memory_write": s8000.get("memory_write"),
            "graphiti_write": s8000.get("graphiti_write"),
            "kernel_mutation": s8000.get("kernel_mutation"),
            "x108_mutation": s8000.get("x108_mutation"),
        },
        "next": "F20B should likely create readonly cognitive value ledger projection over existing gencoin_shadow_packet and /api/gencoin LIVE_EMPTY_REGISTRY; no mint, no wallet, no blockchain.",
    }

    out_json = OUT / f"OBSIDIA_F20A_GENCOIN_COGNITIVE_VALUE_LEDGER_AUDIT_{TS}.json"
    out_txt = OUT / f"OBSIDIA_F20A_GENCOIN_COGNITIVE_VALUE_LEDGER_AUDIT_{TS}.txt"
    p8000_path = OUT / f"F20A_BRODY_PAYLOAD_8000_{TS}.json"
    p8012_path = OUT / f"F20A_BRODY_PAYLOAD_8012_{TS}.json"
    routes_path = OUT / f"F20A_ROUTE_PROBES_{TS}.json"
    scan_path = OUT / f"F20A_SOURCE_SCAN_{TS}.json"

    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    p8000_path.write_text(json.dumps(p8000, ensure_ascii=False, indent=2), encoding="utf-8")
    p8012_path.write_text(json.dumps(p8012, ensure_ascii=False, indent=2), encoding="utf-8")
    routes_path.write_text(json.dumps(route_probes, ensure_ascii=False, indent=2), encoding="utf-8")
    scan_path.write_text(json.dumps(source_scan, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "OBSIDIA F20A GENCOIN COGNITIVE VALUE / LEDGER AUDIT",
        f"timestamp={TS}",
        "mode=READ_ONLY",
        f"classification={classification}",
        "",
        "BRODY_8000:",
        f"gencoin_version={s8000.get('gencoin_version')}",
        f"gencoin_mode={s8000.get('gencoin_mode')}",
        f"usable_shadow_value={s8000.get('usable_shadow_value')}",
        f"shadow_scores_numeric_count={s8000.get('shadow_scores_numeric_count')}",
        f"shadow_scores={s8000.get('shadow_scores')}",
        f"value_layer_scores={s8000.get('value_layer_scores')}",
        f"thermo_unified_usable_for_gencoin={s8000.get('thermo_unified_usable_for_gencoin')}",
        f"final_scoring_enabled={s8000.get('final_scoring_enabled')}",
        f"economic_scoring_enabled={s8000.get('economic_scoring_enabled')}",
        f"blockchain_enabled={s8000.get('blockchain_enabled')}",
        f"memory_promotion_enabled={s8000.get('memory_promotion_enabled')}",
        "",
        "LEDGER_PROBE:",
        f"status={ledger_json.get('status')}",
        f"source={ledger_json.get('source')}",
        f"total={ledger_json.get('total')}",
        f"reason={ledger_json.get('reason')}",
        f"no_wallet={ledger_json.get('no_wallet')}",
        f"no_mint={ledger_json.get('no_mint')}",
        f"is_real_token={ledger_json.get('is_real_token')}",
        "",
        "ROUTE_PROBES:",
    ]

    for p in route_probes:
        lines.append(f"{p.get('method')} {p.get('route')} ok={p.get('ok')} status={p.get('status')} summary={p.get('summary')}")

    lines.extend(["", "SOURCE_SCAN_COUNTS:"])
    for k, v in sorted(source_counts.items()):
        lines.append(f"{k}={v}")

    lines.extend([
        "",
        "BOUNDARY:",
        f"decision_authority={s8000.get('decision_authority')}",
        f"readonly={s8000.get('readonly')}",
        f"emits_act={s8000.get('emits_act')}",
        f"emits_verdict={s8000.get('emits_verdict')}",
        f"memory_write={s8000.get('memory_write')}",
        f"graphiti_write={s8000.get('graphiti_write')}",
        f"kernel_mutation={s8000.get('kernel_mutation')}",
        f"x108_mutation={s8000.get('x108_mutation')}",
        "",
        "FILES:",
        str(out_json),
        str(out_txt),
        str(p8000_path),
        str(p8012_path),
        str(routes_path),
        str(scan_path),
    ])

    out_txt.write_text("\n".join(lines), encoding="utf-8")

    print("F20A_GENCOIN_COGNITIVE_VALUE_LEDGER_AUDIT_DONE")
    print("REPORT_JSON=" + str(out_json))
    print("REPORT_TXT=" + str(out_txt))
    print("CLASSIFICATION=" + classification)
    print("GENCOIN_VERSION_8000=" + str(s8000.get("gencoin_version")))
    print("USABLE_SHADOW_VALUE_8000=" + str(s8000.get("usable_shadow_value")))
    print("SHADOW_SCORES_NUMERIC_COUNT_8000=" + str(s8000.get("shadow_scores_numeric_count")))
    print("VALUE_LAYER_SCORES_8000=" + json.dumps(s8000.get("value_layer_scores"), ensure_ascii=False))
    print("THERMO_UNIFIED_USABLE_FOR_GENCOIN_8000=" + str(s8000.get("thermo_unified_usable_for_gencoin")))
    print("LEDGER_STATUS=" + str(ledger_json.get("status")))
    print("LEDGER_REASON=" + str(ledger_json.get("reason")))
    print("SOURCE_SCAN_COUNTS=" + json.dumps(source_counts, ensure_ascii=False))

if __name__ == "__main__":
    main()
