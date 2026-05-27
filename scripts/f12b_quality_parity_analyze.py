from pathlib import Path
import re
import json

root = sorted(Path("docs/runtime").glob("f12b_quality_parity_*"))[-1]
files = sorted(root.glob("p*_port_*_terminal.txt"))

def read_any(p: Path) -> str:
    raw = p.read_bytes()
    for enc in ("utf-8", "utf-16", "cp1252", "cp850"):
        try:
            return raw.decode(enc)
        except Exception:
            pass
    return raw.decode("utf-8", errors="replace")

rows = []
for p in files:
    txt = read_any(p)
    rows.append({
        "file": str(p),
        "has_brody": "BRODY" in txt,
        "runtime_graphiti_live": "REAL_BRODY_GRAPHITI_LIVE" in txt,
        "runtime_no_graphiti": "REAL_BRODY_RUNTIME_NO_GRAPHITI" in txt,
        "graphiti_pass": "GRAPHITI_LIVE_READONLY_PASS" in txt,
        "graphiti_blocked": "GRAPHITI_LIVE_BLOCKED" in txt,
        "domain_raccord": "DOMAIN RACCORD / STRUCTURE-FIRST" in txt,
        "true_voice": "TRUE VOICE / LLM OBSIDIEN" in txt,
        "code_debug": "DOMAIN_RACCORD_CODE_DEBUG" in txt,
        "structural": "DOMAIN_RACCORD_STRUCTURAL" in txt,
        "architecture": "DOMAIN_RACCORD_ARCHITECTURE" in txt,
        "write_boundary": "DOMAIN_RACCORD_WRITE_BOUNDARY" in txt,
        "boundary": "BOUNDARY" in txt,
        "mojibake": any(x in txt for x in ["Ô", "├", "Ç"]),
    })

print(json.dumps(rows, indent=2, ensure_ascii=False))

(root / "F12B_PARITY_ANALYSIS.json").write_text(
    json.dumps(rows, indent=2, ensure_ascii=False),
    encoding="utf-8",
)

print("F12B_PARITY_ANALYSIS_WRITTEN=", root / "F12B_PARITY_ANALYSIS.json")
