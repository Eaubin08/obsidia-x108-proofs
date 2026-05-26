import json
from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs")
REPORT = ROOT / "artifacts" / "p2_bank_security_fuzz_extended" / "bank_security_fuzz_extended_report.json"
OUT_MD = ROOT / "docs" / "P2_BANK_SECURITY_FUZZ_EXTENDED_FAILURES.md"

rows = json.loads(REPORT.read_text(encoding="utf-8"))
fails = [r for r in rows if not r.get("ok")]

print("FAIL_COUNT =", len(fails))
print()

for i, r in enumerate(fails, 1):
    print(f"--- FAIL {i} ---")
    print("case_id:", r.get("case_id"))
    print("category:", r.get("category"))
    print("expectation:", r.get("expectation"))
    print("safety_outcome:", r.get("safety_outcome"))
    print("gate:", r.get("x108_gate_observed"))
    print("reason_code:", r.get("reason_code"))
    print("severity:", r.get("severity"))
    print("stderr:", r.get("stderr"))
    print()

lines = []
lines.append("# P2 Bank — Security Fuzz Extended Failures")
lines.append("")
lines.append(f"Total failing cases: {len(fails)}")
lines.append("")

for i, r in enumerate(fails, 1):
    lines.append(f"## {i}. {r.get('case_id')}")
    lines.append("")
    lines.append(f"- category: `{r.get('category')}`")
    lines.append(f"- expectation: `{r.get('expectation')}`")
    lines.append(f"- safety_outcome: `{r.get('safety_outcome')}`")
    lines.append(f"- x108_gate_observed: `{r.get('x108_gate_observed')}`")
    lines.append(f"- reason_code: `{r.get('reason_code')}`")
    lines.append(f"- severity: `{r.get('severity')}`")
    lines.append(f"- stderr: `{r.get('stderr')}`")
    lines.append("")

OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("MARKDOWN =", str(OUT_MD))