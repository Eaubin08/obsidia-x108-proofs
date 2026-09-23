from pathlib import Path
from datetime import datetime, timezone
import json
import re

ROOT = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B")
BASE = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core")
OUT = ROOT / "docs" / "runtime"
OUT.mkdir(parents=True, exist_ok=True)

TS = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

CANDIDATES = [
    ROOT / "periphery" / "reverse_os.py",
    ROOT / "periphery" / "test_reverse_os_non_decision.py",

    BASE / "obsidia-engine-candidate" / "bridge" / "zip2_reverse_os_real_adapter.py",

    BASE / "obsidia-engine-candidate" / "reports" / "RAPPORT_BRANCHEMENT_ZIP2_REVERSE_OS_TO_ZIP1_X108.md",
    BASE / "obsidia-engine-candidate" / "reports" / "RAPPORT_BRANCHEMENT_ZIP2_REVERSE_OS_TO_ZIP1_X108_REPAIR.md",
    BASE / "obsidia-engine-candidate" / "reports" / "RAPPORT_BRANCHEMENT_ZIP2_DEEP_OBSIDIA_IR_TO_ZIP1_X108.md",
    BASE / "obsidia-engine-candidate" / "reports" / "RAPPORT_BRANCHEMENT_ZIP2_34_TREES_IR_SHAZAM_TO_ZIP1_X108.md",

    BASE / "obsidia-engine-candidate" / "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_FREEZE_CANDIDATE" / "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1" / "06_REVERSE_OS_SSR_JARVIS" / "reverse_os.py",
    BASE / "obsidia-engine-candidate" / "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_FREEZE_CANDIDATE" / "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1" / "06_REVERSE_OS_SSR_JARVIS" / "jarvis_projection.py",
    BASE / "obsidia-engine-candidate" / "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_FREEZE_CANDIDATE" / "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1" / "06_REVERSE_OS_SSR_JARVIS" / "semantic_mapper.py",
    BASE / "obsidia-engine-candidate" / "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_FREEZE_CANDIDATE" / "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1" / "06_REVERSE_OS_SSR_JARVIS" / "active_cognitive_reduction.py",
    BASE / "obsidia-engine-candidate" / "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_FREEZE_CANDIDATE" / "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1" / "17_TESTS" / "test_reverse_os_non_decision.py",
    BASE / "obsidia-engine-candidate" / "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_FREEZE_CANDIDATE" / "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1" / "20_DEMO_MINIMALE" / "demo_full_pipeline.py",
    BASE / "obsidia-engine-candidate" / "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_FREEZE_CANDIDATE" / "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1" / "common_types.py",
    BASE / "obsidia-engine-candidate" / "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_FREEZE_CANDIDATE" / "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1" / "09_MCP_BRIDGE_OBSIDIA_IR" / "obsidia_ir.py",
]

PATTERNS = [
    "def ", "class ", "non_decision", "decision", "verdict", "ObsidiaIR",
    "SSRProjection", "ContextPacket", "MCPRequest", "reverse", "projection",
    "KX108", "readonly", "ACT", "mutation", "ContextPacket"
]

def read_text(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"__READ_ERROR__ {type(e).__name__}: {e}"

def inspect(path):
    exists = path.exists()
    item = {
        "path": str(path),
        "exists": exists,
        "size": path.stat().st_size if exists else None,
        "functions": [],
        "classes": [],
        "boundary_hits": [],
        "preview": "",
    }
    if not exists:
        return item

    text = read_text(path)
    item["preview"] = text[:2000]

    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("def "):
            item["functions"].append({"line": i, "text": stripped})
        if stripped.startswith("class "):
            item["classes"].append({"line": i, "text": stripped})
        if any(p.lower() in stripped.lower() for p in PATTERNS):
            item["boundary_hits"].append({"line": i, "text": stripped[:500]})
        if len(item["boundary_hits"]) > 80:
            break

    return item

results = [inspect(p) for p in CANDIDATES]

report = {
    "checkpoint": "F18A3_TARGETED_OS_TRAD_IR_REVERSE_CANDIDATE_INSPECTION",
    "mode": "READ_ONLY",
    "timestamp": TS,
    "results": results,
    "decision_hint": {
        "do_not_patch_yet": True,
        "likely_reuse_targets": [
            "periphery/reverse_os.py",
            "obsidia-engine-candidate/bridge/zip2_reverse_os_real_adapter.py",
            "MMONDE/common_types.py",
            "MMONDE/09_MCP_BRIDGE_OBSIDIA_IR/obsidia_ir.py",
            "MMONDE/20_DEMO_MINIMALE/demo_full_pipeline.py",
            "MMONDE/17_TESTS/test_reverse_os_non_decision.py"
        ],
        "next": "Choose F18B reuse strategy after human review."
    }
}

out_json = OUT / f"OBSIDIA_F18A3_TARGETED_CANDIDATE_INSPECTION_{TS}.json"
out_txt = OUT / f"OBSIDIA_F18A3_TARGETED_CANDIDATE_INSPECTION_{TS}.txt"

out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

lines = [
    "OBSIDIA F18A3 TARGETED OS TRAD / IR / REVERSE OS CANDIDATE INSPECTION",
    f"timestamp={TS}",
    "mode=READ_ONLY",
    "",
]

for r in results:
    lines.append("--------------------------------------------------")
    lines.append(f"PATH={r['path']}")
    lines.append(f"EXISTS={r['exists']}")
    lines.append(f"SIZE={r['size']}")
    lines.append("FUNCTIONS:")
    for f in r["functions"][:20]:
        lines.append(f"  L{f['line']}: {f['text']}")
    lines.append("CLASSES:")
    for c in r["classes"][:20]:
        lines.append(f"  L{c['line']}: {c['text']}")
    lines.append("BOUNDARY HITS:")
    for h in r["boundary_hits"][:25]:
        lines.append(f"  L{h['line']}: {h['text']}")

out_txt.write_text("\n".join(lines), encoding="utf-8")

print("F18A3_TARGETED_CANDIDATE_INSPECTION_DONE")
print("REPORT_JSON=" + str(out_json))
print("REPORT_TXT=" + str(out_txt))
print("EXISTING_FILES=" + str(sum(1 for r in results if r["exists"])))
for r in results:
    if r["exists"]:
        print("- " + r["path"])
