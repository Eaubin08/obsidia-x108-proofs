from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / "docs" / "runtime"
OUT.mkdir(parents=True, exist_ok=True)

TS = datetime.now().strftime("%Y%m%d_%H%M%S")

TARGETS = [
    "sigma/contracts.py",
    "sigma/aggregation.py",
]

TEST_DIRS = [
    "tests",
    "tests/sigma",
]

KEYWORDS = [
    "AgentVote",
    "ReadinessPacket",
    "compute_governance_confidence",
    "compute_readiness_confidence",
    "normalize_confidence",
    "readiness_scope",
    "harmonic_integrity_governance",
    "calculate_immutable_vote",
    "immutable_vote",
    "harmonic",
    "HOLD",
    "ALLOW",
    "BLOCK",
    "confidence",
    "x108_gate",
]

FORBIDDEN_F25B_RUNTIME_TOUCH = [
    "apps/obsidia_api/routes/brody.py",
    "apps/obsidia_api/main.py",
    "apps/obsidia_api/routes/",
    "periphery/",
    "Obsidia/",
]

def sh(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, cwd=ROOT, text=True, encoding="utf-8", errors="replace").strip()
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"

def read(path: str) -> str:
    p = ROOT / path
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="replace")

def scan_lines(path: str, keywords: list[str]) -> list[dict]:
    txt = read(path)
    hits = []
    for i, line in enumerate(txt.splitlines(), 1):
        low = line.lower()
        for kw in keywords:
            if kw.lower() in low:
                hits.append({"line": i, "keyword": kw, "text": line[:500]})
                break
    return hits

def find_all(pattern: str) -> str:
    return sh([
        "powershell",
        "-NoProfile",
        "-Command",
        f"Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue | "
        f"Where-Object {{ $_.FullName -notmatch '\\\\.git\\\\|node_modules|\\\\.venv\\\\|__pycache__|dist|build' }} | "
        f"Select-String -Pattern '{pattern}' -SimpleMatch | "
        f"Select-Object Path,LineNumber,Line | ConvertTo-Json -Depth 4"
    ])

head = sh(["git", "rev-parse", "--short", "HEAD"])
tag = sh(["git", "tag", "--points-at", "HEAD"])
status = sh(["git", "status", "-sb"])

target_hits = {path: scan_lines(path, KEYWORDS) for path in TARGETS}
calculate_scan = find_all("calculate_immutable_vote")
sigma_imports = find_all("from sigma")
agentvote_scan = find_all("AgentVote")

contracts_text = read("sigma/contracts.py")
aggregation_text = read("sigma/aggregation.py")

readiness_structure_present = (
    "readiness_scope" in contracts_text
    and "confidence_readiness" in contracts_text
    and "x108_gate" in contracts_text
    and "def compute_readiness_confidence" in contracts_text
)

findings = {
    "agent_vote_present": "class AgentVote" in contracts_text,
    "readiness_packet_class_present": "class ReadinessPacket" in contracts_text,
    "readiness_structure_present": readiness_structure_present,
    "compute_governance_confidence_present": "def compute_governance_confidence" in contracts_text,
    "compute_readiness_confidence_present": "def compute_readiness_confidence" in contracts_text,
    "calculate_immutable_vote_present": "calculate_immutable_vote" in contracts_text,
    "sigma_aggregation_present": "def aggregate_" in aggregation_text,
}

gap_confirmed = (
    findings["agent_vote_present"]
    and findings["readiness_structure_present"]
    and findings["compute_governance_confidence_present"]
    and findings["compute_readiness_confidence_present"]
    and not findings["calculate_immutable_vote_present"]
)

patch_boundary = {
    "allowed_patch_file_f25b": "sigma/contracts.py",
    "allowed_test_file_f25b": "tests/sigma/test_f25b_immutable_vote_minimal.py",
    "forbidden_runtime_touch": FORBIDDEN_F25B_RUNTIME_TOUCH,
    "f25b_must_be_additive_only": True,
    "runtime_wiring_allowed": False,
    "dependency_install_allowed": False,
}

recommended_f25b_contract = {
    "function": "calculate_immutable_vote",
    "type": "pure_advisory_function",
    "side_effects": False,
    "decision_authority": "KX108_ONLY",
    "readonly": True,
    "emits_act": False,
    "emits_verdict": False,
    "memory_write": False,
    "graphiti_write": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "score_range": "[-1.0, 1.0]",
    "x108_gate_preserved": True,
    "advisory_verdict_never_runtime_decision": True,
}

recommended_tests = [
    "test_all_allow_votes_positive_score",
    "test_all_block_votes_negative_score",
    "test_all_hold_votes_neutral_score",
    "test_mixed_votes_weighted",
    "test_empty_votes_returns_hold",
    "test_output_is_readonly",
    "test_decision_authority_kx108_only",
    "test_emits_act_false",
    "test_emits_verdict_false",
    "test_immutable_flag",
    "test_x108_gate_preserved",
    "test_advisory_does_not_override_x108_block",
    "test_confidence_clamped",
    "test_score_clamped_to_minus_one_one",
]

report = {
    "checkpoint": "F25A_HARMONIC_VOTE_SOURCE_AUDIT",
    "timestamp": TS,
    "mode": "READ_ONLY_AUDIT",
    "patch": "NO",
    "commit": "NO",
    "head": head,
    "tag": tag,
    "git_status": status,
    "findings": findings,
    "gap_confirmed": gap_confirmed,
    "audit_note": "F25A1 uses readiness_structure_present instead of requiring exact class ReadinessPacket.",
    "target_hits": target_hits,
    "calculate_immutable_vote_scan": calculate_scan,
    "sigma_imports_scan": sigma_imports,
    "agentvote_scan": agentvote_scan,
    "patch_boundary": patch_boundary,
    "recommended_f25b_contract": recommended_f25b_contract,
    "recommended_tests": recommended_tests,
    "next": "F25B_IMMUTABLE_VOTE_MINIMAL_PATCH" if gap_confirmed else "STOP_REVIEW_REQUIRED",
}

json_path = OUT / f"OBSIDIA_F25A_HARMONIC_VOTE_SOURCE_AUDIT_{TS}.json"
md_path = OUT / f"OBSIDIA_F25A_HARMONIC_VOTE_SOURCE_AUDIT_{TS}.md"

json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

lines = []
lines.append("# OBSIDIA F25A — HARMONIC VOTE SOURCE AUDIT")
lines.append("")
lines.append(f"Date: {TS}")
lines.append("Mode: READ_ONLY_AUDIT")
lines.append("Patch: NO")
lines.append("Commit: NO")
lines.append("")
lines.append("## Git")
lines.append("")
lines.append(f"- HEAD: {head}")
lines.append(f"- TAG: {tag}")
lines.append("```text")
lines.append(status)
lines.append("```")
lines.append("")
lines.append("## Findings")
lines.append("")
for k, v in findings.items():
    lines.append(f"- {k}: {v}")
lines.append("")
lines.append(f"## Gap confirmed: {gap_confirmed}")
lines.append("")
if gap_confirmed:
    lines.append("`calculate_immutable_vote()` is missing while AgentVote / ReadinessPacket / governance confidence functions exist.")
    lines.append("")
lines.append("## Allowed F25B patch boundary")
lines.append("")
lines.append("- allowed patch file: `sigma/contracts.py`")
lines.append("- allowed test file: `tests/sigma/test_f25b_immutable_vote_minimal.py`")
lines.append("- no Brody route wiring")
lines.append("- no runtime restart")
lines.append("- no dependency install")
lines.append("- no Graphiti / Neo4j / memory / kernel mutation")
lines.append("")
lines.append("## Required F25B invariants")
lines.append("")
for k, v in recommended_f25b_contract.items():
    lines.append(f"- {k}: {v}")
lines.append("")
lines.append("## Required tests")
lines.append("")
for t in recommended_tests:
    lines.append(f"- {t}")
lines.append("")
lines.append("## Target snippets")
lines.append("")
for path, hits in target_hits.items():
    lines.append(f"### {path}")
    for h in hits[:60]:
        lines.append(f"- L{h['line']} [{h['keyword']}] {h['text']}")
    lines.append("")
lines.append("## Status")
lines.append("")
if gap_confirmed:
    lines.append("F25A_HARMONIC_VOTE_SOURCE_AUDIT_PASS")
    lines.append("NEXT=F25B_IMMUTABLE_VOTE_MINIMAL_PATCH")
else:
    lines.append("F25A_HARMONIC_VOTE_SOURCE_AUDIT_NEEDS_REVIEW")
    lines.append("NEXT=STOP_REVIEW_REQUIRED")

md_path.write_text("\n".join(lines), encoding="utf-8")

print("F25A_HARMONIC_VOTE_SOURCE_AUDIT_DONE")
print(f"HEAD={head}")
print(f"TAG={tag}")
print(f"GAP_CONFIRMED={gap_confirmed}")
print(f"REPORT_MD={md_path}")
print(f"REPORT_JSON={json_path}")
print("PATCH=NO")
print("COMMIT=NO")
print(report["next"])
