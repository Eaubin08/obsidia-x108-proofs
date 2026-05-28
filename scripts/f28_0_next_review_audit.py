from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(".").resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

OUT_JSON = ROOT / "docs" / "runtime" / f"OBSIDIA_F28_0_NEXT_REVIEW_AUDIT_{TS}.json"
OUT_MD = ROOT / "docs" / "runtime" / f"OBSIDIA_F28_0_NEXT_REVIEW_AUDIT_{TS}.md"

PALIER_TAG_PREFIXES = [
    "BRODY_F23A4",
    "BRODY_F23A5",
    "BRODY_F23A6",
    "BRODY_F27",
]

NEXT_CANDIDATES = [
    {
        "id": "F28_GOVERNED_OPERATOR_RUNTIME",
        "title": "Brody Operator Runtime unified view",
        "reason": "Sigma envelope + TreeSignalPacket now exist; next useful layer is an operator-facing runtime packet that exposes both together.",
        "risk": "LOW_MEDIUM",
        "patch_scope": [
            "apps/obsidia_api/brody_operator_view_packet.py",
            "apps/obsidia_api/brody_runtime_context_adapter.py",
            "apps/obsidia_api/routes/periphery_ops.py",
        ],
        "recommended": True,
    },
    {
        "id": "F29_MEMORY_GRAPHITI_RECONCILIATION",
        "title": "Graphiti / memory sidecar reconciliation",
        "reason": "There are still memory/audit leftovers and known Graphiti/Brody material gaps; useful but touches sidecar semantics.",
        "risk": "MEDIUM",
        "patch_scope": [
            "periphery/brody_memory_readonly",
            "periphery/graphiti",
            "apps/obsidia_api/routes/brody_monitoring.py",
        ],
        "recommended": False,
    },
    {
        "id": "F30_WORKFLOW_SOP_ENGINE",
        "title": "Workflow/SOP pseudo-deterministic engine",
        "reason": "Connects to the enterprise workflows idea: work as SOP graph, but must stay under KX108 and no-ACT boundaries.",
        "risk": "MEDIUM",
        "patch_scope": [
            "periphery/workflows",
            "apps/obsidia_api/routes/periphery_ops.py",
            "tests/api",
        ],
        "recommended": False,
    },
    {
        "id": "F31_CLEAN_UNTRACKED_RUNTIME_DEBT",
        "title": "Clean untracked F23 audit debris",
        "reason": "Repo working tree remains noisy with old untracked F23A4/F23 meta/night audit files.",
        "risk": "LOW",
        "patch_scope": [
            "docs/runtime",
            "scripts",
            "sigma/*.bak_*",
        ],
        "recommended": False,
    },
]


def git(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True, encoding="utf-8", errors="replace").strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def git_lines(cmd: list[str]) -> list[str]:
    out = git(cmd)
    if out.startswith("ERROR:"):
        return [out]
    return [line for line in out.splitlines() if line.strip()]


def latest_docs(pattern: str) -> list[str]:
    docs = sorted(
        (ROOT / "docs" / "runtime").glob(pattern),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return [str(p).replace("\\", "/") for p in docs[:5]]


def main():
    head = git(["git", "rev-parse", "--short", "HEAD"])
    status = git_lines(["git", "status", "-sb"])
    tags = git_lines(["git", "tag", "--list", "BRODY_F*"])

    palier_tags = [
        tag for tag in tags
        if any(tag.startswith(prefix) for prefix in PALIER_TAG_PREFIXES)
    ]

    untracked = [line for line in status if line.startswith("?? ")]
    modified = [line for line in status if line.startswith(" M ") or line.startswith("M ")]

    selected = next(c for c in NEXT_CANDIDATES if c["recommended"])

    report = {
        "report_id": f"OBSIDIA_F28_0_NEXT_REVIEW_AUDIT_{TS}",
        "phase": "F28.0",
        "mode": "NEXT_REVIEW_AUDIT_NO_PATCH",
        "commit": False,
        "tag": False,
        "freeze": False,
        "head": head,
        "status": status,
        "palier_tags": palier_tags,
        "untracked_count": len(untracked),
        "modified_count": len(modified),
        "latest_docs": {
            "f23a4": latest_docs("OBSIDIA_F23A4*.md"),
            "f23a5": latest_docs("OBSIDIA_F23A5*.md"),
            "f23a6": latest_docs("OBSIDIA_F23A6*.md"),
            "f27": latest_docs("OBSIDIA_F27*.md"),
        },
        "f27_runtime_smoke_confirmed": {
            "status": True,
            "route": "/api/periphery/cognitive/tree-signal",
            "version": "TREE_SIGNAL_PACKET_V1",
            "decision_authority": "KX108_ONLY",
            "emits_act": False,
        },
        "next_candidates": NEXT_CANDIDATES,
        "selected_next": selected,
        "locked_decisions": [
            "F28.0 is audit-only.",
            "No runtime patch in F28.0.",
            "Do not clean untracked files blindly.",
            "Do not merge Graphiti/memory sidecar before a dedicated review.",
            "Next recommended palier should bind Sigma + TreeSignal into an operator runtime view, still readonly.",
            "Decision authority remains KX108_ONLY.",
        ],
        "next_recommended": "F28.1_GOVERNED_OPERATOR_RUNTIME_AUDIT",
        "final_status": "F28_0_NEXT_REVIEW_AUDIT_DONE",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# OBSIDIA F28.0 — NEXT REVIEW AUDIT")
    lines.append("")
    lines.append("Mode: NEXT_REVIEW_AUDIT_NO_PATCH")
    lines.append("Commit: NO")
    lines.append("Tag: NO")
    lines.append("Freeze: NO")
    lines.append("")
    lines.append(f"HEAD: `{head}`")
    lines.append("")
    lines.append("## Palier chain")
    lines.append("")
    for tag in palier_tags:
        lines.append(f"- `{tag}`")
    lines.append("")
    lines.append("## Working tree")
    lines.append("")
    lines.append(f"- Modified tracked files: {len(modified)}")
    lines.append(f"- Untracked files: {len(untracked)}")
    lines.append("")
    lines.append("## F27 runtime smoke")
    lines.append("")
    lines.append("```text")
    lines.append("route=/api/periphery/cognitive/tree-signal")
    lines.append("version=TREE_SIGNAL_PACKET_V1")
    lines.append("decision_authority=KX108_ONLY")
    lines.append("emits_act=false")
    lines.append("runtime_smoke=PASS")
    lines.append("```")
    lines.append("")
    lines.append("## Next candidates")
    lines.append("")
    for c in NEXT_CANDIDATES:
        mark = "SELECTED" if c["recommended"] else "DEFERRED"
        lines.append(f"### {c['id']} — {mark}")
        lines.append(f"- Title: {c['title']}")
        lines.append(f"- Reason: {c['reason']}")
        lines.append(f"- Risk: {c['risk']}")
        lines.append(f"- Patch scope: {', '.join(c['patch_scope'])}")
        lines.append("")
    lines.append("## Selected next")
    lines.append("")
    lines.append("```text")
    lines.append("F28.1_GOVERNED_OPERATOR_RUNTIME_AUDIT")
    lines.append("```")
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append("```text")
    lines.append("DECISION_AUTHORITY=KX108_ONLY")
    lines.append("readonly=true")
    lines.append("emits_act=false")
    lines.append("kernel_mutation=false")
    lines.append("x108_mutation=false")
    lines.append("```")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("F28_0_NEXT_REVIEW_AUDIT_DONE")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("F28_0_NEXT_REVIEW_AUDIT_DONE")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    print(f"HEAD={head}")
    print(f"PALIER_TAGS={len(palier_tags)}")
    print(f"MODIFIED={len(modified)}")
    print(f"UNTRACKED={len(untracked)}")
    print(f"SELECTED_NEXT={report['next_recommended']}")


if __name__ == "__main__":
    main()
