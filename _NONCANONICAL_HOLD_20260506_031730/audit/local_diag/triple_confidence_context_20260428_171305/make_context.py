from pathlib import Path
import json
import subprocess
from datetime import datetime

ROOT = Path(".")
OUT = Path(r".\\audit\\local_diag\\triple_confidence_context_20260428_171305\\TRIPLE_CONFIDENCE_CONTEXT.txt")

FILES = [
    "sigma/contracts.py",
    "sigma/guard.py",
    "sigma/aggregation.py",
    "sigma/protocols.py",
    "sigma/run_pipeline.py",
]

def write(s=""):
    with OUT.open("a", encoding="utf-8", newline="\n") as f:
        f.write(str(s) + "\n")

def dump_file(path_str):
    p = ROOT / path_str
    write("\n" + "=" * 100)
    write(f"FILE: {path_str}")
    write("=" * 100)

    if not p.exists():
        write("[MISSING]")
        return

    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    for i, line in enumerate(lines, 1):
        write(f"{i:04d}: {line}")

def dump_git_status():
    write("\n" + "=" * 100)
    write("GIT STATUS")
    write("=" * 100)
    try:
        r = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        write(r.stdout)
        if r.stderr:
            write("STDERR:")
            write(r.stderr)
    except Exception as e:
        write(f"[git status failed] {e}")

def dump_git_diff():
    write("\n" + "=" * 100)
    write("GIT DIFF TARGET FILES")
    write("=" * 100)
    try:
        r = subprocess.run(
            ["git", "diff", "--", *FILES],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        write(r.stdout)
        if r.stderr:
            write("STDERR:")
            write(r.stderr)
    except Exception as e:
        write(f"[git diff failed] {e}")

def dump_newest_decisions():
    write("\n" + "=" * 100)
    write("NEWEST decision_*.json SUMMARY")
    write("=" * 100)

    files = sorted(ROOT.rglob("decision_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:12]

    for p in files:
        write("\n" + "-" * 80)
        write(f"JSON: {p}")
        write(f"mtime: {datetime.fromtimestamp(p.stat().st_mtime).isoformat()}")

        try:
            data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
        except Exception as e:
            write(f"[JSON READ ERROR] {e}")
            continue

        keys = [
            "domain",
            "market_verdict",
            "x108_gate",
            "confidence",
            "confidence_integrity",
            "confidence_governance",
            "confidence_readiness",
            "confidence_scope",
            "governance_scope",
            "readiness_scope",
            "severity",
            "reason_code",
            "unknowns",
            "risk_flags",
            "contradictions",
            "metrics",
            "raw_engine",
        ]

        for k in keys:
            write(f"{k}: {json.dumps(data.get(k, None), ensure_ascii=False)}")

OUT.write_text("", encoding="utf-8", newline="\n")

write("TRIPLE CONFIDENCE CONTEXT")
write(f"generated_at: {datetime.now().isoformat()}")

dump_git_status()
dump_git_diff()

for f in FILES:
    dump_file(f)

dump_newest_decisions()

print(str(OUT))
