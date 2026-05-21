from pathlib import Path

x108 = Path("/mnt/c/Users/User/Desktop/obsidia-engine-proof-core/obsidia-x108-proofs")
audit = x108 / "_local_audits/EXTERNAL_BENCHMARKS"
out = audit / "reports/BRODY_ENTRYPOINT_DISCOVERY.txt"
out.parent.mkdir(parents=True, exist_ok=True)

keywords = [
    "brody",
    "llmobsidien",
    "readonly",
    "chat",
    "dialogue",
    "context_packet",
    "memory",
]

skip_parts = {
    ".git",
    ".venv",
    "node_modules",
    "_external_benchmarks",
    "__pycache__",
}

def allowed(path: Path) -> bool:
    return not bool(set(path.parts) & skip_parts)

def has_keyword(path: Path) -> bool:
    s = str(path).lower()
    return any(k in s for k in keywords)

all_files = []
py_files = []
main_hits = []

for p in x108.rglob("*"):
    if not p.is_file():
        continue
    if not allowed(p):
        continue

    rel = p.relative_to(x108)

    if has_keyword(p):
        all_files.append(str(rel))

    if p.suffix == ".py" and has_keyword(p):
        py_files.append(str(rel))

    if p.suffix == ".py" and has_keyword(p):
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for i, line in enumerate(txt.splitlines(), start=1):
            if any(pattern in line for pattern in [
                "if __name__",
                "argparse",
                "typer",
                "click",
                "def main",
                "input(",
                "print(",
            ]):
                main_hits.append(f"{rel}:{i}: {line[:220]}")

report = []
report.append("=== BRODY FILE DISCOVERY ===")
report.extend(all_files[:300])
report.append("")
report.append("=== PYTHON CANDIDATES ===")
report.extend(py_files[:200])
report.append("")
report.append("=== MAIN / CLI PATTERNS ===")
report.extend(main_hits[:300])
report.append("")
report.append("BRODY_ENTRYPOINT_DISCOVERY_DONE")

out.write_text("\n".join(report), encoding="utf-8")

print(out.read_text(encoding="utf-8")[-12000:])
print("BRODY_ENTRYPOINT_DISCOVERY_SAVED_TO=", out)
