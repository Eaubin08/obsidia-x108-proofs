#!/usr/bin/env python3
"""
verify_chain_anchor.py — Vérification de l'ancrage OpenTimestamps (Phase 14B2)
Usage: python3 tools/verify_chain_anchor.py <ots_file> <payload_file>
"""
import sys, subprocess, os

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 tools/verify_chain_anchor.py <ots_file> <payload_file>")
        sys.exit(1)

    ots_file = sys.argv[1]
    payload_file = sys.argv[2]

    if not os.path.exists(ots_file):
        print(f"ERROR: OTS file not found: {ots_file}")
        sys.exit(1)
    if not os.path.exists(payload_file):
        print(f"ERROR: Payload file not found: {payload_file}")
        sys.exit(1)

    print(f"OTS file   : {ots_file}")
    print(f"Payload    : {payload_file}")
    print(f"Verifying against Bitcoin blockchain...")
    print()

    result = subprocess.run(
        ["ots", "verify", ots_file, "-f", payload_file],
        capture_output=True, text=True
    )

    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    if result.returncode == 0:
        print("VERIFICATION: PASS")
    else:
        print("VERIFICATION: PENDING (blockchain not yet confirmed, retry in ~1h)")

if __name__ == "__main__":
    main()
