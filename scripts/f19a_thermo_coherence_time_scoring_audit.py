from __future__ import annotations

import json
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()
OUT = ROOT / "docs" / "runtime"
OUT.mkdir(parents=True, exist_ok=True)

TS = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

MESSAGE = (
    "F19 audit readonly: analyse thermodynamics, coherence, time scoring, "
    "THERMO_HOT, value_layer_scores, sigma pressure, temporal context, "
    "sans écrire mémoire, sans ACT, sans mutation X108."
)

PATTERN = (
    "thermo|thermodynamic|thermodynamics|THERMO_HOT|THERMO_COLD|"
    "coherence|cohérence|coherence_score|temporal|time_score|time|"
    "value_layer_scores|value_layer_scores_null|hard_risks|soft_risks|"
    "sigma_packet|sigma_pressure|anti_mismatch|mismatch|"
    "gencoin_shadow_packet|shadow_value|F3|F19"
)

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
                return r.status, json.loads(raw)
            except Exception:
                return r.status, {"raw": raw[:3000]}
    except Exception as e:
        return 0, {"error": f"{type(e).__name__}: {e}"}

def post_brody(port: int):
    return http_json(
        f"http://127.0.0.1:{port}/api/brody/chat",
        "POST",
        {
            "message": MESSAGE,
            "language": "fr",
            "session_id": f"f19a_thermo_coherence_time_{port}",
        },
    )

def find_deep(obj: Any, terms: list[str], prefix: str = "") -> list[dict[str, Any]]:
    hits = []
    terms_l = [t.lower() for t in terms]

    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else str(k)
            key_l = str(k).lower()
            if any(t in key_l for t in terms_l):
                preview = v
                if isinstance(v, (dict, list)):
                    preview = f"{type(v).__name__}[{len(v)}]"
                hits.append({"path": path, "preview": preview})
            hits.extend(find_deep(v, terms, path))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:50]):
            hits.extend(find_deep(v, terms, f"{prefix}[{i}]"))

    return hits[:300]

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

def analyse(port: int, status: int, payload: Any):
    if not isinstance(payload, dict):
        return {"port": port, "http_status": status, "error": "payload_not_dict"}

    thermo = payload.get("thermodynamics_packet") or payload.get("thermo_packet") or {}
    sigma = payload.get("sigma_packet") or {}
    anti = payload.get("anti_mismatch_packet") or payload.get("anti_mismatch_snapshot") or {}
    gencoin = payload.get("gencoin_shadow_packet") or {}
    temporal = payload.get("temporal_context") or payload.get("time_context") or {}

    all_hits = find_deep(
        payload,
        [
            "thermo", "coherence", "time", "temporal", "value_layer",
            "hard_risks", "soft_risks", "sigma", "mismatch", "gencoin"
        ],
    )

    hard_risks = []
    for source in [thermo, sigma, anti, gencoin, payload]:
        if isinstance(source, dict):
            hr = source.get("hard_risks")
            if isinstance(hr, list):
                hard_risks.extend([str(x) for x in hr])

    value_layer_scores = None
    value_layer_scores_null = None
    if isinstance(thermo, dict):
        value_layer_scores = thermo.get("value_layer_scores")
        value_layer_scores_null = thermo.get("value_layer_scores_null")
    if value_layer_scores is None and isinstance(gencoin, dict):
        value_layer_scores = gencoin.get("value_layer_scores")
        value_layer_scores_null = gencoin.get("value_layer_scores_null")

    score_numeric_count = (
        numeric_count(thermo)
        + numeric_count(sigma)
        + numeric_count(anti)
        + numeric_count(gencoin)
        + numeric_count(temporal)
    )

    has_thermo = bool(thermo)
    has_sigma = bool(sigma)
    has_anti = bool(anti)
    has_time = bool(temporal) or any("time" in h["path"].lower() or "temporal" in h["path"].lower() for h in all_hits)

    if has_thermo and score_numeric_count >= 3 and value_layer_scores not in (None, {}, []):
        classification = "REAL_SCORING_PRESENT_NEEDS_VALIDATION"
    elif has_thermo or has_sigma or has_anti or has_time:
        classification = "PARTIAL_SIGNAL_ONLY_NEEDS_WIRING"
    else:
        classification = "ABSENT_NEEDS_READONLY_SCORING_ADAPTER"

    if "THERMO_HOT" in hard_risks or value_layer_scores_null is True:
        classification = "PARTIAL_SIGNAL_WITH_THERMO_HOT_OR_NULL_VALUE_SCORES"

    return {
        "port": port,
        "http_status": status,
        "source": payload.get("source"),
        "graphiti_status": payload.get("graphiti_status"),
        "decision_authority": payload.get("decision_authority"),
        "readonly": payload.get("readonly"),
        "emits_act": payload.get("emits_act"),
        "memory_write": payload.get("memory_write"),
        "graphiti_write": payload.get("graphiti_write"),
        "kernel_mutation": payload.get("kernel_mutation"),
        "x108_mutation": payload.get("x108_mutation"),

        "thermodynamics_packet_present": has_thermo,
        "thermodynamics_keys": sorted(thermo.keys()) if isinstance(thermo, dict) else [],
        "sigma_packet_present": has_sigma,
        "sigma_keys": sorted(sigma.keys()) if isinstance(sigma, dict) else [],
        "anti_mismatch_present": has_anti,
        "anti_mismatch_keys": sorted(anti.keys()) if isinstance(anti, dict) else [],
        "gencoin_shadow_present": bool(gencoin),
        "gencoin_shadow_keys": sorted(gencoin.keys()) if isinstance(gencoin, dict) else [],
        "temporal_context_present": bool(temporal),
        "temporal_context_keys": sorted(temporal.keys()) if isinstance(temporal, dict) else [],

        "hard_risks": sorted(set(hard_risks)),
        "value_layer_scores": value_layer_scores,
        "value_layer_scores_null": value_layer_scores_null,
        "score_numeric_count": score_numeric_count,
        "deep_hits_sample": all_hits[:120],
        "classification": classification,
    }

def git_grep():
    try:
        r = subprocess.run(
            ["git", "grep", "-n", "-E", PATTERN, "--", "apps", "periphery", "tests", "docs/runtime", "scripts"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=40,
        )
        lines = (r.stdout or "").splitlines()
    except Exception as e:
        return [{"error": f"{type(e).__name__}: {e}"}]

    out = []
    for line in lines[:800]:
        parts = line.split(":", 2)
        if len(parts) == 3:
            out.append({"path": parts[0], "line": parts[1], "text": parts[2][:500]})
    return out

def classify_sources(scan: list[dict[str, Any]]):
    counts = {}
    for h in scan:
        text = json.dumps(h, ensure_ascii=False).lower()
        if "thermodynamics_operational" in text or "thermodynamics" in text:
            c = "THERMODYNAMICS_SOURCE"
        elif "sigma" in text:
            c = "SIGMA_SOURCE"
        elif "anti_mismatch" in text or "mismatch" in text:
            c = "ANTI_MISMATCH_SOURCE"
        elif "temporal" in text or "time" in text:
            c = "TIME_TEMPORAL_SOURCE"
        elif "gencoin" in text or "value_layer" in text:
            c = "GENCOIN_VALUE_SOURCE"
        else:
            c = "RELATED"
        counts[c] = counts.get(c, 0) + 1
    return counts

def main():
    status8000, payload8000 = post_brody(8000)
    status8012, payload8012 = post_brody(8012)
    status_openapi, openapi = http_json("http://127.0.0.1:8000/openapi.json")

    routes = []
    if isinstance(openapi, dict):
        for route in sorted((openapi.get("paths") or {}).keys()):
            low = route.lower()
            if any(x in low for x in ["thermo", "coherence", "time", "sigma", "gencoin", "value", "brody"]):
                routes.append(route)

    scan = git_grep()
    source_counts = classify_sources(scan)

    a8000 = analyse(8000, status8000, payload8000)
    a8012 = analyse(8012, status8012, payload8012)

    payload8000_path = OUT / f"F19A_THERMO_COHERENCE_TIME_PAYLOAD_8000_{TS}.json"
    payload8012_path = OUT / f"F19A_THERMO_COHERENCE_TIME_PAYLOAD_8012_{TS}.json"
    routes_path = OUT / f"F19A_OPENAPI_ROUTES_8000_{TS}.json"
    scan_path = OUT / f"F19A_SOURCE_SCAN_{TS}.json"
    report_json_path = OUT / f"OBSIDIA_F19A_THERMO_COHERENCE_TIME_SCORING_AUDIT_{TS}.json"
    report_txt_path = OUT / f"OBSIDIA_F19A_THERMO_COHERENCE_TIME_SCORING_AUDIT_{TS}.txt"

    payload8000_path.write_text(json.dumps(payload8000, ensure_ascii=False, indent=2), encoding="utf-8")
    payload8012_path.write_text(json.dumps(payload8012, ensure_ascii=False, indent=2), encoding="utf-8")
    routes_path.write_text(json.dumps({"http_status": status_openapi, "routes": routes}, ensure_ascii=False, indent=2), encoding="utf-8")
    scan_path.write_text(json.dumps(scan, ensure_ascii=False, indent=2), encoding="utf-8")

    report = {
        "checkpoint": "F19A_THERMO_COHERENCE_TIME_SCORING_AUDIT",
        "mode": "READ_ONLY",
        "timestamp": TS,
        "files_created": {
            "payload_8000": str(payload8000_path),
            "payload_8012": str(payload8012_path),
            "routes": str(routes_path),
            "source_scan": str(scan_path),
            "report_json": str(report_json_path),
            "report_txt": str(report_txt_path),
        },
        "runtime_summary_8000": a8000,
        "runtime_summary_8012": a8012,
        "routes_candidates": routes,
        "source_scan_counts": source_counts,
        "source_scan_sample": scan[:120],
        "preliminary_classification": {
            "8000": a8000.get("classification"),
            "8012": a8012.get("classification"),
        },
        "boundary_check": {
            "decision_authority": a8000.get("decision_authority"),
            "readonly": a8000.get("readonly"),
            "emits_act": a8000.get("emits_act"),
            "memory_write": a8000.get("memory_write"),
            "graphiti_write": a8000.get("graphiti_write"),
            "kernel_mutation": a8000.get("kernel_mutation"),
            "x108_mutation": a8000.get("x108_mutation"),
        },
        "next_step": "F19B should reuse existing thermo/sigma/time modules if present; otherwise create readonly scoring adapter with honest null/partial status.",
    }

    report_json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "OBSIDIA F19A THERMO / COHERENCE / TIME SCORING AUDIT",
        f"timestamp={TS}",
        "mode=READ_ONLY",
        "",
        f"CLASSIFICATION_8000={a8000.get('classification')}",
        f"CLASSIFICATION_8012={a8012.get('classification')}",
        "",
        "8000:",
        f"thermodynamics_packet_present={a8000.get('thermodynamics_packet_present')}",
        f"thermodynamics_keys={a8000.get('thermodynamics_keys')}",
        f"sigma_packet_present={a8000.get('sigma_packet_present')}",
        f"anti_mismatch_present={a8000.get('anti_mismatch_present')}",
        f"temporal_context_present={a8000.get('temporal_context_present')}",
        f"gencoin_shadow_present={a8000.get('gencoin_shadow_present')}",
        f"hard_risks={a8000.get('hard_risks')}",
        f"value_layer_scores_null={a8000.get('value_layer_scores_null')}",
        f"score_numeric_count={a8000.get('score_numeric_count')}",
        "",
        "8012:",
        f"thermodynamics_packet_present={a8012.get('thermodynamics_packet_present')}",
        f"hard_risks={a8012.get('hard_risks')}",
        f"value_layer_scores_null={a8012.get('value_layer_scores_null')}",
        f"score_numeric_count={a8012.get('score_numeric_count')}",
        "",
        "SOURCE_SCAN_COUNTS:",
    ]

    for k, v in sorted(source_counts.items()):
        lines.append(f"{k}={v}")

    lines.extend([
        "",
        "ROUTES:",
        *routes,
        "",
        "BOUNDARY:",
        f"decision_authority={a8000.get('decision_authority')}",
        f"readonly={a8000.get('readonly')}",
        f"emits_act={a8000.get('emits_act')}",
        f"memory_write={a8000.get('memory_write')}",
        f"graphiti_write={a8000.get('graphiti_write')}",
        f"kernel_mutation={a8000.get('kernel_mutation')}",
        f"x108_mutation={a8000.get('x108_mutation')}",
        "",
        "FILES:",
        str(payload8000_path),
        str(payload8012_path),
        str(routes_path),
        str(scan_path),
        str(report_json_path),
        str(report_txt_path),
    ])

    report_txt_path.write_text("\n".join(lines), encoding="utf-8")

    print("F19A_THERMO_COHERENCE_TIME_SCORING_AUDIT_DONE")
    print("REPORT_JSON=" + str(report_json_path))
    print("REPORT_TXT=" + str(report_txt_path))
    print("CLASSIFICATION_8000=" + str(a8000.get("classification")))
    print("CLASSIFICATION_8012=" + str(a8012.get("classification")))
    print("THERMO_PRESENT_8000=" + str(a8000.get("thermodynamics_packet_present")))
    print("HARD_RISKS_8000=" + str(a8000.get("hard_risks")))
    print("VALUE_LAYER_SCORES_NULL_8000=" + str(a8000.get("value_layer_scores_null")))
    print("SCORE_NUMERIC_COUNT_8000=" + str(a8000.get("score_numeric_count")))
    print("SOURCE_SCAN_COUNTS=" + json.dumps(source_counts, ensure_ascii=False))

if __name__ == "__main__":
    main()
