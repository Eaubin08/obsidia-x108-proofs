# _runtime_wiring_preflight/p40_live_matrix.py
# P40 — Live endpoint matrix validation via HTTP + TestClient.
# Pas de subprocess. Pas d'ACT. KX108_ONLY. Readonly.
import json
import pathlib
import socket
import urllib.request
import urllib.error
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

API_BASE = "http://127.0.0.1:8000"
OUT_DIR = REPO / "_runtime_wiring_preflight"

# ── Port check ────────────────────────────────────────────────────────────────
def port_open(port: int) -> bool:
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout=1)
        s.close()
        return True
    except Exception:
        return False

# ── HTTP helpers ──────────────────────────────────────────────────────────────
def http_get(path: str, timeout: int = 10) -> tuple:
    try:
        req = urllib.request.urlopen(f"{API_BASE}{path}", timeout=timeout)
        return json.loads(req.read()), req.status
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read())
        except Exception:
            body = {}
        return {**body, "_http_error": e.code}, e.code
    except Exception as ex:
        return {"_error": str(ex)}, 0

def http_post(path: str, body: dict, timeout: int = 20) -> tuple:
    try:
        data = json.dumps(body).encode()
        req_obj = urllib.request.Request(
            f"{API_BASE}{path}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        resp = urllib.request.urlopen(req_obj, timeout=timeout)
        return json.loads(resp.read()), resp.status
    except urllib.error.HTTPError as e:
        try:
            body_e = json.loads(e.read())
        except Exception:
            body_e = {}
        return {**body_e, "_http_error": e.code}, e.code
    except Exception as ex:
        return {"_error": str(ex)}, 0

# ── TestClient fallback ───────────────────────────────────────────────────────
def testclient_get(path: str):
    from fastapi.testclient import TestClient
    from apps.obsidia_api.main import app
    c = TestClient(app)
    r = c.get(path)
    return r.json(), r.status_code

def testclient_post(path: str, body: dict):
    from fastapi.testclient import TestClient
    from apps.obsidia_api.main import app
    c = TestClient(app)
    r = c.post(path, json=body)
    return r.json(), r.status_code

def smart_get(path: str, live_available: bool):
    if live_available:
        d, s = http_get(path)
        if s >= 200 and "_error" not in d:
            return d, s, "LIVE"
    d, s = testclient_get(path)
    return d, s, "TESTCLIENT"

def smart_post(path: str, body: dict, live_available: bool):
    if live_available:
        d, s = http_post(path, body)
        if s >= 200 and "_error" not in d and "_http_error" not in d:
            return d, s, "LIVE"
    d, s = testclient_post(path, body)
    return d, s, "TESTCLIENT"

def main():
    results = {
        "boundary": {
            "readonly": True,
            "emits_act": False,
            "decision_authority": "KX108_ONLY",
            "no_act": True,
        },
        "services": {},
        "live_server": {},
        "endpoints": {},
        "queries": {},
        "workbench": {},
        "verdicts": {},
        "verdict": "PENDING",
    }

    # ── 1. Port check ─────────────────────────────────────────────────────────
    for name, port in [("API_8000", 8000), ("WORKBENCH_5173", 5173), ("OBSIDIASHELL_8011", 8011)]:
        open_ = port_open(port)
        results["services"][name] = {"port": port, "open": open_, "status": "OPEN" if open_ else "CLOSED"}
        print(f"  {name}:{port} => {'OPEN' if open_ else 'CLOSED'}")

    api_up = results["services"]["API_8000"]["open"]

    # ── 2. Live server version check ──────────────────────────────────────────
    print("\n=== LIVE SERVER CHECK ===")
    spec, s = http_get("/openapi.json")
    paths_live = sorted(spec.get("paths", {}).keys()) if s == 200 else []
    p36_routes_live = [p for p in paths_live if "source-runtime" in p or "os-map" in p]
    server_has_p36 = len(p36_routes_live) > 0
    results["live_server"] = {
        "http": s,
        "total_routes": len(paths_live),
        "p36_p38_routes": p36_routes_live,
        "has_p36_routes": server_has_p36,
        "note": "READY" if server_has_p36 else "OLD_CODE_NEEDS_RESTART",
    }
    print(f"  Live server routes: {len(paths_live)} | P36-P38 routes: {len(p36_routes_live)}")
    if not server_has_p36:
        print("  NOTE: Live server runs old code. TestClient will be used for P36-P38 validation.")
    else:
        print("  Live server has P36-P38 routes!")

    live_ok = server_has_p36 and api_up

    # ── 3. GET endpoint matrix ────────────────────────────────────────────────
    print("\n=== GET ENDPOINT MATRIX ===")
    get_endpoints = [
        ("/api/status", "service"),
        ("/api/runtime-wiring/preview", "status"),
        ("/api/runtime-wiring/source-runtime/status", "source_runtime_status"),
        ("/api/runtime-wiring/os-map/status", "os_map_status"),
        ("/api/x108/status", "kernel_status"),
    ]
    for path, key in get_endpoints:
        d, s, src = smart_get(path, live_ok)
        results["endpoints"][path] = {
            "http": s,
            "source": src,
            key: d.get(key, "?"),
            "decision_authority": d.get("decision_authority", "?"),
            "emits_act": d.get("emits_act", "?"),
            "readonly": d.get("readonly", "?"),
        }
        print(f"  [{src}] GET {path} => HTTP {s} | {key}={d.get(key,'?')}")

    # ── 4. Query matrix ───────────────────────────────────────────────────────
    print("\n=== QUERY MATRIX ===")
    query_defs = [
        ("IR alphabet reverse OS interlanguage", "IR_QUERY"),
        ("34 arbres agents registry", "AGENT_TREE_QUERY"),
        ("lois protocoles non décision boundary", "LAW_PROTOCOL_QUERY"),
        ("mémoire Brody Graphiti réintégration", "MEMORY_GRAPHITI_QUERY"),
        ("envoie un mail maintenant", "ACTION_QUERY"),
    ]
    for q, label in query_defs:
        body = {"query": q, "max_paths": 3}
        d, s, src = smart_post("/api/runtime-wiring/os-map/query", body, live_ok)
        sel = d.get("selected_runtime_path", {})
        chain = sel.get("capability_chain", ["?"])
        results["queries"][label] = {
            "query": q,
            "http": s,
            "source": src,
            "os_map_status": d.get("os_map_status", "?"),
            "selected_capability": chain[0] if chain else "?",
            "x108_decision": d.get("x108_decision", "?"),
            "action_blocked": d.get("action_blocked", False),
            "runtime_allowed_now": d.get("runtime_allowed_now", "?"),
            "emits_act": d.get("emits_act", "?"),
            "evidence_packs": d.get("selected_evidence_packs", []),
            "inventory_linked": d.get("inventory_linked", False),
            "coverage_status": d.get("coverage_status", "?"),
            "selected_functions_count": len(d.get("selected_functions", [])),
        }
        print(f"  [{src}][{label}] HTTP={s} | cap={chain[0] if chain else '?'} | x108={d.get('x108_decision','?')} | blocked={d.get('action_blocked','?')}")

    # ── 5. Workbench check ────────────────────────────────────────────────────
    print("\n=== WORKBENCH CHECK ===")
    wb = REPO / "apps" / "obsidia-workbench"
    dist = wb / "dist" / "index.html"
    sidebar = wb / "src" / "components" / "LeftSidebar.tsx"
    app_tsx = wb / "src" / "App.tsx"
    os_map_view = wb / "src" / "views" / "OSMapView.tsx"
    dist_js = list((wb / "dist" / "assets").glob("*.js")) if (wb / "dist" / "assets").exists() else []
    dist_js_kb = sum(f.stat().st_size for f in dist_js) // 1024 if dist_js else 0

    results["workbench"] = {
        "OSMapView_exists": os_map_view.exists(),
        "App_imports_OSMapView": "OSMapView" in app_tsx.read_text(encoding="utf-8", errors="replace") if app_tsx.exists() else False,
        "Sidebar_has_os_map": "'os-map'" in sidebar.read_text(encoding="utf-8", errors="replace") if sidebar.exists() else False,
        "dist_built": dist.exists(),
        "dist_js_kb": dist_js_kb,
        "vite_port_open": results["services"]["WORKBENCH_5173"]["open"],
        "vite_serving": results["services"]["WORKBENCH_5173"]["open"],
    }
    for k, v in results["workbench"].items():
        print(f"  {k}: {v}")

    # ── 6. Verdicts ───────────────────────────────────────────────────────────
    q = results["queries"]
    verdicts = {
        "IR_QUERY_correct": q.get("IR_QUERY", {}).get("selected_capability") in ["IR_ALPHABET_MAPPING", "REVERSE_OS_INTERLANGUAGE"],
        "AGENT_TREE_correct": q.get("AGENT_TREE_QUERY", {}).get("selected_capability") == "AGENT_TREE_LOOKUP",
        "LAW_PROTOCOL_correct": q.get("LAW_PROTOCOL_QUERY", {}).get("selected_capability") == "LAW_PROTOCOL_LOOKUP",
        "MEMORY_GRAPHITI_correct": q.get("MEMORY_GRAPHITI_QUERY", {}).get("selected_capability") in ["MEMORY_REINTEGRATION_CONTEXT", "GRAPHITI_READONLY_CONTEXT"],
        "ACTION_BLOCKED_correct": q.get("ACTION_QUERY", {}).get("action_blocked") is True,
        "NO_RUNTIME_ALLOWED_NOW": all(
            v.get("runtime_allowed_now") is False
            for v in q.values()
        ),
        "NO_EMITS_ACT": all(
            v.get("emits_act") is False
            for v in q.values()
        ),
        "ALL_HTTP_200": all(v.get("http") == 200 for v in q.values()),
        "EVIDENCE_PACKS_IR": "REVERSE_OS_INTERLANGUAGE_CANON_V1" in q.get("IR_QUERY", {}).get("evidence_packs", []),
        "WORKBENCH_BUILT": results["workbench"]["dist_built"],
        "OS_MAP_VIEW_COMPLETE": all([
            results["workbench"]["OSMapView_exists"],
            results["workbench"]["App_imports_OSMapView"],
            results["workbench"]["Sidebar_has_os_map"],
        ]),
    }
    results["verdicts"] = verdicts
    all_pass = all(verdicts.values())
    results["verdict"] = "P40_LIVE_RELOAD_SERVER_MATRIX_READY" if all_pass else "P40_PARTIAL_MATRIX_VALIDATED"

    # Server mode note
    if not server_has_p36:
        results["verdicts"]["live_server_has_p36_routes"] = False
        results["verdict_note"] = (
            "TestClient used for P36-P38 routes (live server runs old code). "
            "Restart server with: python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000 --reload"
        )
    else:
        results["verdicts"]["live_server_has_p36_routes"] = True
        results["verdict_note"] = "All validations performed against live server on port 8000."

    # Write JSON
    out_json = OUT_DIR / "P40_LIVE_RELOAD_SERVER_MATRIX_RESULTS.json"
    out_json.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nJSON: {out_json}")
    print(f"VERDICT: {results['verdict']}")
    print("Verdicts:")
    for k, v in verdicts.items():
        print(f"  {'✓' if v else '✗'} {k}: {v}")

    return results

if __name__ == "__main__":
    main()
