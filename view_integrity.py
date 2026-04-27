import json
import os
from pathlib import Path

def show_dashboard():
    root = Path(__file__).resolve().parent
    seal_path = root / "merkle_seal.json"
    data_dir = root / "MonProjet" / "allData"

    print("\n" + "="*40)
    print("      OBSIDIA INTEGRITY MONITOR")
    print("="*40)

    # 1. Analyse du stock de preuves
    if data_dir.exists():
        files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
        count = len(files)
        print(f"Total Proofs Collected : {count}")
    else:
        print("Total Proofs Collected : 0 (Directory not found)")

    # 2. Lecture du Sceau de Gouvernance
    if seal_path.exists():
        with open(seal_path, "r") as f:
            seal = json.load(f)
            print(f"Last Seal Date       : {seal.get('audit_date', 'N/A')}")
            # Extraction propre du hash
            m_root = seal.get('merkle_root', 'UNKNOWN')
            print(f"Merkle Root          : {m_root[:16]}...")
            print(f"Status               : {seal.get('status')}")
            
            if seal.get('status') == "INTEGRITY_VERIFIED":
                print(f"Integrity Score      : 100% [SAFE]")
    else:
        print("Status               : NO SEAL DETECTED")
        print("Integrity Score      : 0% [UNSECURED]")

    print("="*40 + "\n")

if __name__ == "__main__":
    show_dashboard()
