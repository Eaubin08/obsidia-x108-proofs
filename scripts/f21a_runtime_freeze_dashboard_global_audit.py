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
    "F21 audit readonly: expose l'état global runtime freeze F2 à F20, "
    "packets Brody, Graphiti, OS Trad, IR, Reverse OS, Thermo, Gencoin, "
    "terminal visibility, sans ACT, sans write, sans mutation X108."
)

REQUIRED_TOP_LEVEL = [
    "true_voice_snapshot",
    "true_response_structure_snapshot",
    "adaptive_response_policy",
    "sigma_packet",
    "anti_mismatch_packet",
    "thermodynamics_packet",
    "thermo_unified_packet",
    "gencoin_shadow_packet",
    "gencoin_cognitive_ledger_packet",
    "tree_signal_packet",
    "memory_promotion_guard_packet",
    "operator_view_packet",
    "translation_trace",
    "ir_candidate",
    "contracts",
    "permission_matrix",
    "machination_packet",
    "support_summary",
    "boundary_contract",
    "kernel_contract",
]

PHASES = [
    "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10",
    "F11", "F12", "F13", "F14", "F15", "F16", "F17", "F18", "F19", "F20"
]

def run_git(args: list[str]) -> str:
    try:
        r = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, timeout=30)
        return (r.stdout or r.stderr or "").strip()
    except Exception as e:
        return f"{type(e).__name__}: {e}"

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
                return {"ok": True, "status": r.status, "json": json.loads(raw), "raw_preview": raw[:1500]}
            except Exception:
                return {"ok": True, "status": r.status, "json": None, "raw_preview": raw[:1500]}
    except Exception as e:
        return {"ok": False, "status": 0, "error": f"{type(e).__name__}: {e}"}

def post_brody(port: int):
    return http_json(
        f"http://127.0.0.1:{port}/api/brody/chat",
        "POST",
        {
            "message": MESSAGE,
            "language": "fr",
            "session_id": f"f21a_runtime_freeze_dashboard_audit_{port}",
        },
    )

def payload_summary(port: int, res: dict[str, Any]):
    p = res.get("json")
    if not isinstance(p, dict):
        return {"port": port, "ok": False, "http_status": res.get("status"), "error": res.get("error")}

    present = {k: k in p and p.get(k) not in (None, {}, []) for k in REQUIRED_TOP_LEVEL}
    missing = [k for k, v in present.items() if not v]

    gencoin = p.get("gencoin_cognitive_ledger_packet") or {}
    thermo = p.get("thermo_unified_packet") or {}
    reverse = p.get("translation_trace") or {}
    ir = p.get("ir_candidate") or {}

    return {
        "port": port,
        "ok": True,
        "http_status": res.get("status"),
        "source": p.get("source"),
        "graphiti_status": p.get("graphiti_status"),
        "neo4j_status": p.get("neo4j_status"),
        "decision_authority": p.get("decision_authority"),
        "readonly": p.get("readonly"),
        "emits_act": p.get("emits_act"),
        "emits_verdict": p.get("emits_verdict"),
        "memory_write": p.get("memory_write"),
        "graphiti_write": p.get("graphiti_write"),
        "kernel_mutation": p.get("kernel_mutation"),
        "x108_mutation": p.get("x108_mutation"),
        "required_present": present,
        "missing_required_packets": missing,
        "packet_present_count": sum(1 for v in present.values() if v),
        "packet_total": len(REQUIRED_TOP_LEVEL),

        "reverse_os_source": reverse.get("source") if isinstance(reverse, dict) else None,
        "reverse_alphabet_units_count": reverse.get("alphabet_units_count") if isinstance(reverse, dict) else None,
        "ir_status": ir.get("status") if isinstance(ir, dict) else None,
        "ir_entities_count": len(ir.get("entities", [])) if isinstance(ir, dict) else None,
        "ir_constraints_count": len(ir.get("constraints", [])) if isinstance(ir, dict) else None,

        "thermo_status": thermo.get("status") if isinstance(thermo, dict) else None,
        "thermo_stability_state": thermo.get("stability_state") if isinstance(thermo, dict) else None,
        "thermo_composite_temperature": thermo.get("composite_temperature") if isinstance(thermo, dict) else None,
        "thermo_usable_for_gencoin": thermo.get("usable_for_gencoin") if isinstance(thermo, dict) else None,

        "gencoin_status": gencoin.get("status") if isinstance(gencoin, dict) else None,
        "gencoin_score": (
            (gencoin.get("entries") or [{}])[0].get("cognitive_ledger_score")
            if isinstance(gencoin, dict) else None
        ),
        "gencoin_score_status": (
            (gencoin.get("entries") or [{}])[0].get("score_status")
            if isinstance(gencoin, dict) else None
        ),
        "gencoin_projected_only": gencoin.get("projected_only") if isinstance(gencoin, dict) else None,
        "gencoin_mint_allowed": gencoin.get("mint_allowed") if isinstance(gencoin, dict) else None,
        "gencoin_wallet_enabled": gencoin.get("wallet_enabled") if isinstance(gencoin, dict) else None,
        "gencoin_blockchain_enabled": gencoin.get("blockchain_enabled") if isinstance(gencoin, dict) else None,
        "gencoin_is_real_token": gencoin.get("is_real_token") if isinstance(gencoin, dict) else None,
    }

def collect_reports():
    reports = {}
    all_files = list((ROOT / "docs" / "runtime").glob("*"))
    for phase in PHASES:
        phase_files = [
            str(p.relative_to(ROOT))
            for p in all_files
            if phase.upper() in p.name.upper()
        ]
        reports[phase] = sorted(phase_files)
    return reports

def _tag_matches_phase(tag: str, phase: str) -> bool:
    """Strict phase matcher.

    Prevents F20 from being counted as F2, F19 as F1, etc.
    Accepts:
    - BRODY_F20_...
    - ..._F20_...
    - ..._F20B_...
    - ..._F20C_...
    """
    import re

    return re.search(rf"(^|_)BRODY_{phase}([A-Z]?)(_|$)", tag) is not None or re.search(
        rf"(^|_){phase}([A-Z]?)(_|$)", tag
    ) is not None


def collect_tags():
    tag_text = run_git(["tag", "--list", "BRODY_F*"])
    tags = [x.strip() for x in tag_text.splitlines() if x.strip()]
    out = {}
    for phase in PHASES:
        out[phase] = [t for t in tags if _tag_matches_phase(t, phase)]
    return {"all": tags, "by_phase": out}

def collect_test_inventory():
    tests = []
    for base in [ROOT / "tests" / "api", ROOT / "tests" / "cli", ROOT / "tests" / "ui"]:
        if not base.exists():
            continue
        for p in base.rglob("test_*.py"):
            name = str(p.relative_to(ROOT))
            if any(phase.lower() in name.lower() for phase in [f"f{i}" for i in range(2, 21)]):
                tests.append(name)
    return sorted(tests)

def classify(summary8000: dict[str, Any], summary8012: dict[str, Any], reports: dict[str, list[str]], tags: dict[str, Any]):
    boundary_ok = all([
        summary8000.get("decision_authority") == "KX108_ONLY",
        summary8000.get("readonly") is True,
        summary8000.get("emits_act") is False,
        summary8000.get("memory_write") is False,
        summary8000.get("graphiti_write") is False,
        summary8000.get("kernel_mutation") is False,
        summary8000.get("x108_mutation") is False,
    ])

    runtime_ok = (
        summary8000.get("ok") is True
        and summary8012.get("ok") is True
        and summary8000.get("packet_present_count", 0) >= 16
        and summary8012.get("packet_present_count", 0) >= 16
    )

    late_phases = ["F16", "F17", "F18", "F19", "F20"]
    late_reports_ok = all(len(reports.get(p, [])) > 0 for p in late_phases)
    late_tags_ok = all(len(tags["by_phase"].get(p, [])) > 0 for p in ["F17", "F18", "F19", "F20"])

    if boundary_ok and runtime_ok and late_reports_ok and late_tags_ok:
        return "F21_DASHBOARD_READY_FOR_PATCH"
    if boundary_ok and runtime_ok:
        return "RUNTIME_READY_REPORT_OR_TAG_GAPS"
    return "F21_DASHBOARD_NOT_READY"

def main():
    git_status = run_git(["status", "-sb"])
    head = run_git(["--no-pager", "log", "-1", "--oneline"])
    diff_check = run_git(["diff", "--check"])

    p8000 = post_brody(8000)
    p8012 = post_brody(8012)
    s8000 = payload_summary(8000, p8000)
    s8012 = payload_summary(8012, p8012)

    reports = collect_reports()
    tags = collect_tags()
    tests = collect_test_inventory()

    classification = classify(s8000, s8012, reports, tags)

    report = {
        "checkpoint": "F21A_RUNTIME_FREEZE_DASHBOARD_GLOBAL_AUDIT",
        "mode": "READ_ONLY",
        "timestamp": TS,
        "classification": classification,
        "git": {
            "status": git_status,
            "head": head,
            "diff_check": diff_check,
        },
        "runtime_8000": s8000,
        "runtime_8012": s8012,
        "reports_by_phase": reports,
        "tags": tags,
        "test_inventory": tests,
        "next": "F21B should create a readonly dashboard endpoint and/or terminal/dashboard surface summarizing F2→F20 runtime packets, tags, reports, tests, and boundary state.",
    }

    out_json = OUT / f"OBSIDIA_F21A_RUNTIME_FREEZE_DASHBOARD_GLOBAL_AUDIT_{TS}.json"
    out_txt = OUT / f"OBSIDIA_F21A_RUNTIME_FREEZE_DASHBOARD_GLOBAL_AUDIT_{TS}.txt"
    p8000_path = OUT / f"F21A_BRODY_PAYLOAD_8000_{TS}.json"
    p8012_path = OUT / f"F21A_BRODY_PAYLOAD_8012_{TS}.json"

    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    p8000_path.write_text(json.dumps(p8000, ensure_ascii=False, indent=2), encoding="utf-8")
    p8012_path.write_text(json.dumps(p8012, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "OBSIDIA F21A RUNTIME FREEZE DASHBOARD GLOBAL AUDIT",
        f"timestamp={TS}",
        "mode=READ_ONLY",
        f"classification={classification}",
        "",
        "GIT:",
        f"status={git_status}",
        f"head={head}",
        f"diff_check={diff_check or 'OK'}",
        "",
        "RUNTIME 8000:",
        f"source={s8000.get('source')}",
        f"graphiti_status={s8000.get('graphiti_status')}",
        f"packet_present_count={s8000.get('packet_present_count')}/{s8000.get('packet_total')}",
        f"missing_required_packets={s8000.get('missing_required_packets')}",
        f"reverse_os_source={s8000.get('reverse_os_source')}",
        f"ir_status={s8000.get('ir_status')}",
        f"thermo_status={s8000.get('thermo_status')}",
        f"gencoin_status={s8000.get('gencoin_status')}",
        f"gencoin_score={s8000.get('gencoin_score')}",
        f"gencoin_score_status={s8000.get('gencoin_score_status')}",
        "",
        "RUNTIME 8012:",
        f"source={s8012.get('source')}",
        f"graphiti_status={s8012.get('graphiti_status')}",
        f"packet_present_count={s8012.get('packet_present_count')}/{s8012.get('packet_total')}",
        f"missing_required_packets={s8012.get('missing_required_packets')}",
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
        "TAGS BY PHASE:",
    ]

    for phase in PHASES:
        lines.append(f"{phase}: {tags['by_phase'].get(phase, [])}")

    lines.extend(["", "REPORT COUNTS BY PHASE:"])
    for phase in PHASES:
        lines.append(f"{phase}: {len(reports.get(phase, []))}")

    lines.extend([
        "",
        "TEST INVENTORY COUNT:",
        str(len(tests)),
        "",
        "FILES:",
        str(out_json),
        str(out_txt),
        str(p8000_path),
        str(p8012_path),
    ])

    out_txt.write_text("\n".join(lines), encoding="utf-8")

    print("F21A_RUNTIME_FREEZE_DASHBOARD_GLOBAL_AUDIT_DONE")
    print("REPORT_JSON=" + str(out_json))
    print("REPORT_TXT=" + str(out_txt))
    print("CLASSIFICATION=" + classification)
    print("HEAD=" + head)
    print("GIT_STATUS=" + git_status.replace("\n", " | "))
    print("PACKETS_8000=" + str(s8000.get("packet_present_count")) + "/" + str(s8000.get("packet_total")))
    print("MISSING_8000=" + json.dumps(s8000.get("missing_required_packets"), ensure_ascii=False))
    print("GRAPHITI_8000=" + str(s8000.get("graphiti_status")))
    print("GENCOIN_STATUS_8000=" + str(s8000.get("gencoin_status")))
    print("GENCOIN_SCORE_8000=" + str(s8000.get("gencoin_score")))
    print("REPORT_COUNTS_F16_F20=" + json.dumps({p: len(reports.get(p, [])) for p in ['F16','F17','F18','F19','F20']}, ensure_ascii=False))
    print("TAG_COUNTS_F17_F20=" + json.dumps({p: len(tags['by_phase'].get(p, [])) for p in ['F17','F18','F19','F20']}, ensure_ascii=False))

if __name__ == "__main__":
    main()
