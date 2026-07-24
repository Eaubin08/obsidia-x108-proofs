#!/usr/bin/env python3
"""
SRL Session Registry Layer Audit V0

Readonly audit for Brody peripheral memory components.

Scope:
- Scan periphery/brody_memory_readonly
- Verify foundation components exist:
  - ledger
  - presave buffer
  - auto triage
- Verify no mutation capability is exposed:
  - memory_write=True forbidden
  - graphiti_write=True forbidden
  - neo4j_write=True forbidden
  - emits_act=True forbidden
  - allowed_to_act=True forbidden
  - allowed_to_decide=True forbidden
  - decision_authority must remain KX108_ONLY when declared

This script is readonly:
- no writes to memory
- no writes to Graphiti
- no writes to Neo4j
- no kernel mutation
- no ACT
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MEMORY_ROOT = ROOT / "periphery" / "brody_memory_readonly"

FOUNDATION_PATTERNS = {
    "ledger": [
        "ledger",
        "cognitive_ledger",
        "gencoin",
        "receipt",
        "replay",
    ],
    "presave_buffer": [
        "presave",
        "pre_save",
        "candidate_memory",
        "memory_candidate",
        "buffer",
    ],
    "auto_triage": [
        "auto_triage",
        "triage",
        "post_human_review",
        "human_validation",
    ],
}

FORBIDDEN_TRUE_PATTERNS = {
    "memory_write_true": re.compile(r"\bmemory_write\s*[:=]\s*True\b|\bmemory_write\s*[:=]\s*true\b", re.I),
    "graphiti_write_true": re.compile(r"\bgraphiti_write\s*[:=]\s*True\b|\bgraphiti_write\s*[:=]\s*true\b", re.I),
    "neo4j_write_true": re.compile(r"\bneo4j_write\s*[:=]\s*True\b|\bneo4j_write\s*[:=]\s*true\b", re.I),
    "emits_act_true": re.compile(r"\bemits_act\s*[:=]\s*True\b|\bemits_act\s*[:=]\s*true\b", re.I),
    "allowed_to_act_true": re.compile(r"\ballowed_to_act\s*[:=]\s*True\b|\ballowed_to_act\s*[:=]\s*true\b", re.I),
    "allowed_to_decide_true": re.compile(r"\ballowed_to_decide\s*[:=]\s*True\b|\ballowed_to_decide\s*[:=]\s*true\b", re.I),
    "decision_authority_not_kx108": re.compile(
        r"\bdecision_authority\s*[:=]\s*[\"'](?!KX108_ONLY\b)[^\"']+[\"']",
        re.I,
    ),
    "kernel_mutation_true": re.compile(r"\bkernel_mutation\s*[:=]\s*True\b|\bkernel_mutation\s*[:=]\s*true\b", re.I),
    "x108_mutation_true": re.compile(r"\bx108_mutation\s*[:=]\s*True\b|\bx108_mutation\s*[:=]\s*true\b", re.I),
}

READABLE_SUFFIXES = {".py", ".ps1", ".md", ".json", ".yaml", ".yml", ".txt"}


@dataclass
class Finding:
    severity: str
    code: str
    file: str
    detail: str


def read_text_safe(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "cp1252"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="ignore")


def list_source_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return [
        p for p in root.rglob("*")
        if p.is_file()
        and p.suffix.lower() in READABLE_SUFFIXES
        and ".git" not in p.parts
        and "__pycache__" not in p.parts
    ]


def scan_foundations(files: list[Path]) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}

    searchable = []
    for path in files:
        rel = str(path.relative_to(ROOT))
        text = read_text_safe(path)
        lines = text.splitlines()
        searchable.append((rel, text.lower()))

    for family, patterns in FOUNDATION_PATTERNS.items():
        hits = []
        for rel, low in searchable:
            if any(pattern.lower() in rel.lower() or pattern.lower() in low for pattern in patterns):
                hits.append(rel)
        results[family] = {
            "present": bool(hits),
            "hits": sorted(set(hits))[:50],
            "hit_count": len(set(hits)),
        }

    return results


def scan_forbidden(files: list[Path]) -> list[Finding]:
    findings: list[Finding] = []

    for path in files:
        rel = str(path.relative_to(ROOT))
        text = read_text_safe(path)
        lines = text.splitlines()

        for code, rx in FORBIDDEN_TRUE_PATTERNS.items():
            for match in rx.finditer(text):
                line_no = text.count("\n", 0, match.start())
                line_txt = lines[line_no] if line_no < len(lines) else ""
                if "violations.append" in line_txt or line_txt.strip().startswith(("'", '"', "#")):
                    continue
                line_no = text.count("\n", 0, match.start()) + 1
                findings.append(
                    Finding(
                        severity="BLOCKER",
                        code=code,
                        file=rel,
                        detail=f"Forbidden pattern at line {line_no}: {match.group(0)}",
                    )
                )

    return findings


def build_report() -> dict[str, Any]:
    files = list_source_files(MEMORY_ROOT)
    foundations = scan_foundations(files)
    forbidden = scan_forbidden(files)

    missing_foundations = [
        name for name, result in foundations.items()
        if not result["present"]
    ]

    status = "PASS"
    if missing_foundations:
        status = "WARN"
    if forbidden:
        status = "FAIL"

    return {
        "audit_id": "SRL_SESSION_REGISTRY_LAYER_AUDIT_V0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(ROOT),
        "memory_root": str(MEMORY_ROOT),
        "readonly": True,
        "advisory_only": True,
        "decision_authority": "KX108_ONLY",
        "emits_act": False,
        "memory_write": False,
        "graphiti_write": False,
        "neo4j_write": False,
        "kernel_mutation": False,
        "x108_mutation": False,
        "files_scanned": len(files),
        "foundation_components": foundations,
        "missing_foundations": missing_foundations,
        "forbidden_findings": [asdict(f) for f in forbidden],
        "status": status,
        "notes": [
            "Readonly audit only.",
            "No memory, graphiti, neo4j, kernel or x108 mutation performed.",
            "WARN means foundation component naming may differ or is absent.",
            "FAIL means a forbidden mutation/authority pattern was detected.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Print full JSON report.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero on WARN or FAIL.")
    args = parser.parse_args()

    report = build_report()

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"SRL audit status: {report['status']}")
        print(f"Files scanned: {report['files_scanned']}")
        print(f"Missing foundations: {report['missing_foundations']}")
        print(f"Forbidden findings: {len(report['forbidden_findings'])}")

    if report["status"] == "FAIL":
        return 2
    if args.strict and report["status"] == "WARN":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
