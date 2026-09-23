"""F21B — Runtime Freeze Dashboard.

Readonly dashboard over F2→F20 runtime evidence:
- tags
- reports
- tests
- runtime packet expectations
- boundary invariants

No ACT. No write. No kernel/X108 mutation.
"""
from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter

from apps.obsidia_api.safe_response import safe_backend_response


router = APIRouter(prefix="/api/runtime", tags=["runtime-freeze-dashboard"])

ROOT = Path(__file__).resolve().parents[3]
DOCS_RUNTIME = ROOT / "docs" / "runtime"

PHASES = [
    "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10",
    "F11", "F12", "F13", "F14", "F15", "F16", "F17", "F18", "F19", "F20",
]

PHASE_LABELS = {
    "F2": "Transverse value stack / Sigma base",
    "F3": "Thermodynamics signal base",
    "F4": "Transverse value stack closure",
    "F5": "34 trees runtime signal",
    "F6": "Memory promotion guard",
    "F7": "Operator view packet",
    "F8": "RightPanel transverse UI",
    "F9": "Brody terminal chat view",
    "F10": "Existing command packet reconnect",
    "F11": "Live runtime /api/brody/chat repair",
    "F12": "Domain Raccord quality priority",
    "F13": "Live UI chat smoke",
    "F14": "Command copy button UI",
    "F15": "RightPanel live payload strict repair",
    "F16": "Real live source wiring",
    "F17": "Graphiti V20 frozen reconnect",
    "F18": "Existing Reverse OS / IR wiring",
    "F19": "Thermo / coherence / time unified packet",
    "F20": "Gencoin cognitive ledger visible",
}

REQUIRED_RUNTIME_PACKETS = [
    "true_voice_snapshot",
    "true_response_structure_snapshot",
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

BOUNDARY = {
    "decision_authority": "KX108_ONLY",
    "readonly": True,
    "advisory_only": True,
    "context_signal_only": True,
    "allowed_to_decide": False,
    "allowed_to_act": False,
    "emits_act": False,
    "emits_verdict": False,
    "memory_write": False,
    "graphiti_write": False,
    "neo4j_write": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "real_action": False,
    "execution_allowed": False,
}


def _git(args: list[str]) -> str:
    try:
        r = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=15,
        )
        return (r.stdout or r.stderr or "").strip()
    except Exception as e:
        return f"{type(e).__name__}: {e}"


def _all_runtime_files() -> list[Path]:
    if not DOCS_RUNTIME.exists():
        return []
    return [p for p in DOCS_RUNTIME.glob("*") if p.is_file()]


def _reports_by_phase() -> dict[str, list[str]]:
    files = _all_runtime_files()
    out: dict[str, list[str]] = {}
    for phase in PHASES:
        phase_upper = phase.upper()
        out[phase] = sorted(
            str(p.relative_to(ROOT))
            for p in files
            if phase_upper in p.name.upper()
        )
    return out


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


def _tags_by_phase() -> dict[str, list[str]]:
    tags = [x.strip() for x in _git(["tag", "--list", "BRODY_F*"]).splitlines() if x.strip()]
    out: dict[str, list[str]] = {}
    for phase in PHASES:
        out[phase] = [tag for tag in tags if _tag_matches_phase(tag, phase)]
    return out


def _test_inventory() -> list[str]:
    roots = [ROOT / "tests" / "api", ROOT / "tests" / "cli", ROOT / "tests" / "ui"]
    tests: list[str] = []
    for base in roots:
        if not base.exists():
            continue
        for p in base.rglob("test_*.py"):
            rel = str(p.relative_to(ROOT))
            low = rel.lower()
            if any(f"f{i}" in low for i in range(2, 21)):
                tests.append(rel)
    return sorted(tests)


def _phase_status(phase: str, reports: dict[str, list[str]], tags: dict[str, list[str]], tests: list[str]) -> dict[str, Any]:
    phase_lower = phase.lower()
    phase_tests = [t for t in tests if phase_lower in t.lower()]
    report_count = len(reports.get(phase, []))
    tag_count = len(tags.get(phase, []))

    # F3 is covered inside F2/F4/F19 evidence; not all early phases have explicit tags.
    explicit_tag_expected = phase in {
        "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13",
        "F14", "F15", "F16", "F17", "F18", "F19", "F20",
    }

    if report_count > 0 and (tag_count > 0 or not explicit_tag_expected):
        status = "FREEZE_EVIDENCE_PRESENT"
    elif report_count > 0:
        status = "REPORT_PRESENT_TAG_OPTIONAL_OR_MISSING"
    else:
        status = "NO_PHASE_EVIDENCE_FOUND"

    return {
        "phase": phase,
        "label": PHASE_LABELS.get(phase, phase),
        "status": status,
        "report_count": report_count,
        "tag_count": tag_count,
        "test_count": len(phase_tests),
        "tags": tags.get(phase, []),
        "reports_sample": reports.get(phase, [])[:8],
        "tests": phase_tests,
    }


def build_runtime_freeze_dashboard() -> dict[str, Any]:
    reports = _reports_by_phase()
    tags = _tags_by_phase()
    tests = _test_inventory()

    phase_rows = [
        _phase_status(phase, reports, tags, tests)
        for phase in PHASES
    ]

    late_phases = {"F16", "F17", "F18", "F19", "F20"}
    late_ok = all(
        row["status"] == "FREEZE_EVIDENCE_PRESENT"
        for row in phase_rows
        if row["phase"] in late_phases
    )

    report_total = sum(row["report_count"] for row in phase_rows)
    tag_total = sum(row["tag_count"] for row in phase_rows)
    covered_phases = sum(1 for row in phase_rows if row["report_count"] > 0)

    dashboard_status = (
        "F2_F20_RUNTIME_FREEZE_DASHBOARD_READY"
        if late_ok and covered_phases >= 18
        else "F2_F20_RUNTIME_FREEZE_DASHBOARD_PARTIAL"
    )

    return {
        "version": "RUNTIME_FREEZE_DASHBOARD_F21B_V1",
        "status": dashboard_status,
        "source": "BRODY_F21B_RUNTIME_FREEZE_DASHBOARD",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "head": _git(["--no-pager", "log", "-1", "--oneline"]),
        "git_status": _git(["status", "-sb"]),
        "diff_check": _git(["diff", "--check"]) or "OK",
        "phase_count": len(PHASES),
        "covered_phase_count": covered_phases,
        "report_total": report_total,
        "tag_total": tag_total,
        "test_inventory_count": len(tests),
        "runtime_packet_expectations": {
            "required_top_level_packets": REQUIRED_RUNTIME_PACKETS,
            "required_top_level_packet_count": len(REQUIRED_RUNTIME_PACKETS),
            "known_aliases": {
                "adaptive_response_policy": "true_voice_snapshot.adaptive_response_policy",
            },
            "latest_confirmed_runtime_audit": "F21A_RUNTIME_FREEZE_DASHBOARD_GLOBAL_AUDIT",
            "latest_confirmed_runtime_packets": "19/20 plus known nested adaptive_response_policy alias",
        },
        "late_phase_gate": {
            "required": sorted(late_phases),
            "pass": late_ok,
        },
        "phases": phase_rows,
        "boundary": dict(BOUNDARY),
        **BOUNDARY,
    }


@router.get("/freeze-dashboard")
async def runtime_freeze_dashboard():
    return safe_backend_response(
        {
            "runtime_freeze_dashboard": build_runtime_freeze_dashboard(),
            **BOUNDARY,
        },
        source="BRODY_F21B_RUNTIME_FREEZE_DASHBOARD",
    )

@router.get("/freeze-dashboard/summary")
async def runtime_freeze_dashboard_summary():
    d = build_runtime_freeze_dashboard()
    return safe_backend_response(
        {
            "status": d["status"],
            "version": d["version"],
            "head": d["head"],
            "phase_count": d["phase_count"],
            "covered_phase_count": d["covered_phase_count"],
            "report_total": d["report_total"],
            "tag_total": d["tag_total"],
            "test_inventory_count": d["test_inventory_count"],
            "late_phase_gate": d["late_phase_gate"],
            "boundary": d["boundary"],

            # F21B strict top-level boundary invariants.
            # Do not rely only on nested boundary or safe_backend_response defaults.
            "decision_authority": "KX108_ONLY",
            "readonly": True,
            "advisory_only": True,
            "context_signal_only": True,
            "allowed_to_decide": False,
            "allowed_to_act": False,
            "emits_act": False,
            "emits_verdict": False,
            "memory_write": False,
            "graphiti_write": False,
            "neo4j_write": False,
            "kernel_mutation": False,
            "x108_mutation": False,
            "real_action": False,
            "execution_allowed": False,
        },
        source="BRODY_F21B_RUNTIME_FREEZE_DASHBOARD",
    )
