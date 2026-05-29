from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(".").resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

OUT_JSON = ROOT / "docs" / "runtime" / f"OBSIDIA_F35_0_OPERATOR_DEMO_SURFACE_AUDIT_{TS}.json"
OUT_MD = ROOT / "docs" / "runtime" / f"OBSIDIA_F35_0_OPERATOR_DEMO_SURFACE_AUDIT_{TS}.md"

SCAN_PATTERNS = [
    "apps/**/*.py",
    "apps/**/*.html",
    "apps/**/*.tsx",
    "apps/**/*.ts",
    "apps/**/*.md",
    "periphery/**/*.py",
    "docs/runtime/*F34*.md",
    "docs/runtime/*F33*.md",
    "docs/runtime/*F32*.md",
    "tests/api/test_f3*.py",
]

TOKENS = [
    "operator",
    "Operator",
    "workbench",
    "Workbench",
    "demo",
    "Demo",
    "dashboard",
    "Dashboard",
    "panel",
    "runtime",
    "brody-runtime",
    "integration-packet",
    "workflow-governance",
    "monitor",
    "tree_signal",
    "domain_sigma",
    "KX108_ONLY",
    "readonly",
]

DANGER_TOKENS = [
    "emits_act=True",
    "can_emit_act=True",
    "runtime_execute=True",
    "kernel_mutation=True",
    "x108_mutation=True",
    "memory_write=True",
    "graphiti_write=True",
    "neo4j_write=True",
    "execute_write",
    "write_transaction",
    "os.system",
]


def run(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True, encoding="utf-8", errors="replace").strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def line_hits(text: str, tokens: list[str]) -> list[dict]:
    hits = []
    for idx, line in enumerate(text.splitlines(), start=1):
        for token in tokens:
            if token in line:
                hits.append({
                    "line": idx,
                    "token": token,
                    "text": line.strip()[:260],
                })
    return hits


def inspect(path: Path) -> dict:
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except Exception as exc:
        return {
            "path": rel,
            "read_ok": False,
            "error": repr(exc),
            "token_hits": [],
            "danger_hits": [],
        }

    return {
        "path": rel,
        "read_ok": True,
        "line_count": len(text.splitlines()),
        "token_hits": line_hits(text, TOKENS),
        "danger_hits": line_hits(text, DANGER_TOKENS),
    }


def main():
    paths = []
    for pattern in SCAN_PATTERNS:
        paths.extend(ROOT.glob(pattern))

    paths = sorted(
        {p for p in paths if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts},
        key=lambda p: str(p).lower(),
    )

    records = [inspect(p) for p in paths]
    active = [r for r in records if r.get("token_hits")]
    danger = [r for r in records if r.get("danger_hits")]

    # Local server snapshot through PowerShell because Windows environment is active.
    live_probe = run([
        "powershell",
        "-NoProfile",
        "-Command",
        r"""
$ErrorActionPreference='Stop'
$root = Invoke-WebRequest 'http://127.0.0.1:8000/' -UseBasicParsing -TimeoutSec 10
$openapi = Invoke-WebRequest 'http://127.0.0.1:8000/openapi.json' -UseBasicParsing -TimeoutSec 10
$oa = $openapi.Content | ConvertFrom-Json
$paths = $oa.paths | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name
$f33 = $paths | Where-Object { $_ -eq '/api/periphery/brody-runtime/f33/integration-packet' }
$workflow = $paths | Where-Object { $_ -eq '/api/periphery/workflow-governance/packet' }
$monitor = $paths | Where-Object { $_ -like '*monitor*' }
[pscustomobject]@{
  root_status=$root.StatusCode
  total_routes=$paths.Count
  f33_route_found=[bool]$f33
  workflow_route_found=[bool]$workflow
  monitor_route_count=($monitor | Measure-Object).Count
} | ConvertTo-Json -Compress
"""
    ])

    report = {
        "report_id": f"OBSIDIA_F35_0_OPERATOR_DEMO_SURFACE_AUDIT_{TS}",
        "phase": "F35.0",
        "mode": "AUDIT_ONLY_NO_PATCH",
        "commit": False,
        "tag": False,
        "push": False,
        "head": run(["git", "rev-parse", "--short", "HEAD"]),
        "tag_context": run(["git", "tag", "--points-at", "HEAD"]),
        "git_status": run(["git", "status", "-sb"]),
        "live_8000_probe": live_probe,
        "scanned_files": len(records),
        "active_records": len(active),
        "danger_records": len(danger),
        "active_records_sample": active[:80],
        "danger_records": danger,
        "candidate_surfaces": [
            {
                "id": "F35_C01",
                "name": "Operator Live Runtime Panel",
                "purpose": "Afficher la réponse F33/F34B live sur 8000 avec 7 surfaces READY et boundary KX108_ONLY.",
                "route_needed": "GET /api/operator/runtime-panel or static HTML",
                "risk": "LOW if readonly only",
            },
            {
                "id": "F35_C02",
                "name": "Investor Demo Packet",
                "purpose": "Transformer la preuve runtime en endpoint/report lisible investisseur.",
                "route_needed": "GET /api/demo/runtime-readiness",
                "risk": "LOW if report-only",
            },
            {
                "id": "F35_C03",
                "name": "Workbench Connector Surface",
                "purpose": "Brancher une surface opérateur sur F33 + workflow governance + monitor.",
                "route_needed": "HTML/JSON readonly",
                "risk": "MEDIUM if UI starts mixing runtime/context layers",
            },
        ],
        "recommendation": {
            "next_best_palier": "F35.1_OPERATOR_LIVE_RUNTIME_PANEL_READONLY",
            "why": "F34B already proves live backend readiness. Next useful layer is an operator-readable surface, not another backend gate.",
            "patch_scope": [
                "readonly route or static panel only",
                "consume existing F33 endpoint",
                "display boundary + surfaces + proof links",
                "no ACT",
                "no runtime execution",
                "no memory/Graphiti/Neo4j write",
            ],
        },
        "boundary_expected": {
            "decision_authority": "KX108_ONLY",
            "readonly": True,
            "advisory_only": True,
            "context_signal_only": True,
            "emits_act": False,
            "runtime_execute": False,
            "kernel_mutation": False,
            "x108_mutation": False,
            "memory_write": False,
            "graphiti_write": False,
            "neo4j_write": False,
        },
        "next_recommended": "F35.1_OPERATOR_LIVE_RUNTIME_PANEL_READONLY",
        "status": "F35_0_OPERATOR_DEMO_SURFACE_AUDIT_DONE",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# OBSIDIA F35.0 — OPERATOR / DEMO SURFACE AUDIT")
    lines.append("")
    lines.append("Mode: AUDIT_ONLY_NO_PATCH")
    lines.append("Commit: NO")
    lines.append("Tag: NO")
    lines.append("Push: NO")
    lines.append("")
    lines.append(f"HEAD: `{report['head']}`")
    lines.append(f"Tags on HEAD: `{report['tag_context'] or 'NONE'}`")
    lines.append("")
    lines.append("## Live 8000 probe")
    lines.append("")
    lines.append("```json")
    lines.append(live_probe)
    lines.append("```")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Scanned files: {len(records)}")
    lines.append(f"- Active operator/demo records: {len(active)}")
    lines.append(f"- Danger records: {len(danger)}")
    lines.append("")
    lines.append("## Candidate surfaces")
    lines.append("")
    for c in report["candidate_surfaces"]:
        lines.append(f"- `{c['id']}` — {c['name']}")
        lines.append(f"  - purpose: {c['purpose']}")
        lines.append(f"  - route_needed: `{c['route_needed']}`")
        lines.append(f"  - risk: {c['risk']}")
    lines.append("")
    lines.append("## Recommendation")
    lines.append("")
    lines.append("```text")
    lines.append("NEXT_BEST_PALIER=F35.1_OPERATOR_LIVE_RUNTIME_PANEL_READONLY")
    lines.append("WHY=F34B proves live backend readiness; next useful layer is an operator-readable readonly surface.")
    lines.append("```")
    lines.append("")
    lines.append("## Danger records")
    lines.append("")
    if danger:
        for r in danger[:30]:
            lines.append(f"- `{r['path']}`")
            for h in r["danger_hits"][:8]:
                lines.append(f"  - L{h['line']} `{h['token']}` — {h['text']}")
    else:
        lines.append("- None.")
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append("```text")
    lines.append("DECISION_AUTHORITY=KX108_ONLY")
    lines.append("readonly=true")
    lines.append("advisory_only=true")
    lines.append("context_signal_only=true")
    lines.append("emits_act=false")
    lines.append("runtime_execute=false")
    lines.append("kernel_mutation=false")
    lines.append("x108_mutation=false")
    lines.append("memory_write=false")
    lines.append("graphiti_write=false")
    lines.append("neo4j_write=false")
    lines.append("```")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("F35_0_OPERATOR_DEMO_SURFACE_AUDIT_DONE")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("F35_0_OPERATOR_DEMO_SURFACE_AUDIT_DONE")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    print(f"SCANNED={len(records)}")
    print(f"ACTIVE={len(active)}")
    print(f"DANGER={len(danger)}")
    print("NEXT=F35.1_OPERATOR_LIVE_RUNTIME_PANEL_READONLY")


if __name__ == "__main__":
    main()
