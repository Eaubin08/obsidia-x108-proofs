from pathlib import Path
import re

latest = sorted(
    Path("docs/runtime").glob("OBSIDIA_F21A_RUNTIME_FREEZE_DASHBOARD_GLOBAL_AUDIT_*.txt"),
    key=lambda p: p.stat().st_mtime,
    reverse=True,
)[0]

txt = latest.read_text(encoding="utf-8", errors="replace")

f2 = re.search(r"^F2: (.+)$", txt, re.MULTILINE)
f20 = re.search(r"^F20: (.+)$", txt, re.MULTILINE)

assert f2, "F2_TAG_LINE_MISSING"
assert f20, "F20_TAG_LINE_MISSING"

assert "BRODY_F20_GENCOIN_COGNITIVE_LEDGER_VISIBLE_20260528" not in f2.group(1), f2.group(1)
assert "BRODY_F20_GENCOIN_COGNITIVE_LEDGER_VISIBLE_20260528" in f20.group(1), f20.group(1)
assert "packet_present_count=20/20" in txt
assert "missing_required_packets=[]" in txt
assert "classification=F21_DASHBOARD_READY_FOR_PATCH" in txt

print("F21A_CLEAN_TAG_ASSERT_PASS")
print("LATEST=" + str(latest))
print("F2_LINE=" + f2.group(1))
print("F20_LINE=" + f20.group(1))
