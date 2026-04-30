from pathlib import Path
import re

ROOT = Path(".")
aggregation = ROOT / "sigma" / "aggregation.py"
contracts = ROOT / "sigma" / "contracts.py"

# --- PATCH 1: aggregation.py ---
text = aggregation.read_text(encoding="utf-8")
pattern = re.compile(r"^(?P<indent>\s*)confidence\s*=\s*max\((?P<inside>[^\\\n]+?)\)\s*/\s*max\(1\.0,\s*sum\(scores\.values\(\)\)\)", re.MULTILINE)
matches = list(pattern.finditer(text))
if matches:
    def repl(m):
        indent = m.group("indent")
        inside = m.group("inside").strip()
        return f"{indent}confidence = round(min(0.98, max({inside}) if sum(scores.values()) > 0 else 0.5), 2)"
    text2 = pattern.sub(repl, text)
    aggregation.write_text(text2, encoding="utf-8")
    print(f"[OK] aggregation.py patched: {len(matches)} lines replaced")

# --- PATCH 2: contracts.py ---
lines = contracts.read_text(encoding="utf-8").splitlines(keepends=True)
start = None
for i, line in enumerate(lines):
    if re.match(r"^\s*if\s+self\.agent_votes\s*:\s*(#.*)?$", line):
        start = i
        break
if start is not None:
    indent = re.match(r"^(\s*)", lines[start]).group(1)
    end = start + 1
    while end < len(lines) and (len(re.match(r"^(\s*)", lines[end]).group(1)) > len(indent) or lines[end].strip() == ""):
        end += 1
    new_block = [
        f"{indent}if self.agent_votes:\n",
        f"{indent}    try:\n",
        f"{indent}        self.confidence = float(self.confidence)\n",
        f"{indent}    except Exception: self.confidence = 0.50\n",
        f"{indent}    if self.confidence < 0.0 or self.confidence > 1.0: self.confidence = 0.50\n",
        f"{indent}    verdict = str(getattr(self, \"market_verdict\", \"HOLD\")).upper()\n",
        f"{indent}    x108_gate = str(getattr(self, \"x108_gate\", \"\")).upper()\n",
        f"{indent}    if x108_gate == \"BLOCK\" or verdict in (\"BLOCK\", \"ABORT_TRAJECTORY\", \"REFUSE\", \"DENY\"):\n",
        f"{indent}        self.severity = Severity.S4\n",
        f"{indent}    elif verdict in (\"AUTHORIZE\", \"ALLOW\", \"ACT\", \"VALID\", \"PASS\", \"TRAJECTORY_VALID\", \"PAY\"):\n",
        f"{indent}        self.severity = Severity.S0\n",
        f"{indent}    else: self.severity = Severity.S2\n"
    ]
    contracts.write_text("".join(lines[:start] + new_block + lines[end:]), encoding="utf-8")
    print(f"[OK] contracts.py patched.")
