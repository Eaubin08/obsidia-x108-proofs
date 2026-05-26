import json, sys
from pathlib import Path

audit = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs\_local_audits\BRODY_CONNECTION_MAP_AUDIT_20260520")

# Validate JSON
json_path = audit / "BRODY_CONNECTION_MAP_AUDIT_REPORT.json"
try:
    raw = json_path.read_text(encoding="utf-8")
    data = json.loads(raw)
    print("JSON: VALID")
    print("  keys:", list(data.keys()))
    
    totals = data.get("totals", {})
    print("\nTOTALS (DeepSeek):")
    for k, v in totals.items():
        print(f"  {k}: {v}")
    
    live = data.get("live_api_audit", {})
    print("\nLIVE AUDIT:")
    print(f"  cases_passed: {live.get('cases_passed')}/{live.get('cases_tested')}")
    print(f"  memory_chain_pass: {live.get('memory_chain_pass')}")
    print(f"  tool_call: {live.get('tool_call_candidate_present')}")
    
    priorities = data.get("next_binding_priorities", [])
    print(f"\nPRIORITIES: {len(priorities)}")
    for p in priorities:
        print(f"  {p.get('priority')}: {p.get('label')}")
        
except json.JSONDecodeError as e:
    print(f"JSON: INVALID — {e}")
except Exception as e:
    print(f"ERROR: {e}")

# Check CSV lines
csv_path = audit / "BRODY_MODULE_INVENTORY.csv"
if csv_path.exists():
    lines = csv_path.read_text(encoding="utf-8").strip().splitlines()
    print(f"\nCSV lines: {len(lines)} (1 header + {len(lines)-1} modules)")

# Check all expected files
expected = [
    "BRODY_CONNECTION_MAP_AUDIT_REPORT.md",
    "BRODY_CONNECTION_MAP_AUDIT_REPORT.json",
    "BRODY_MODULE_INVENTORY.csv",
    "BRODY_FREEZE_LEDGER_SCAN.md",
    "BRODY_UNBOUND_MODULES.md",
    "BRODY_RUNTIME_BINDING_MATRIX.md",
    "BRODY_NEXT_BINDING_PRIORITY.md",
    "MANIFEST_SHA256.json",
]
print("\nFILE CHECK:")
for f in expected:
    p = audit / f
    exists = p.exists()
    size = p.stat().st_size if exists else 0
    print(f"  {f}: {'EXISTS' if exists else 'MISSING'} ({size} bytes)")
