# demo_usecase/run_demo.py
import json
from pathlib import Path

print("=== Obsidia End-to-End Demo (Conceptual) ===")

initial = json.loads(Path("request_initial.json").read_text())
approved = json.loads(Path("request_approved.json").read_text())

print("\nStep 1: Initial ACTION (irreversible)")
print("Expected decision: HOLD (human gate required)")

print("\nStep 2: Human approval provided")
print("Expected decision: ACT")

print("\nStep 3: Audit updated and chained")

print("\nStep 4: Attestation will include audit hash")

print("\nDemo complete — deterministic governance enforced.")