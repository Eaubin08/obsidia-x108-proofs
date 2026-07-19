import hashlib
import os
import json
from pathlib import Path
from datetime import datetime

def get_file_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def build_merkle_root(hashes):
    if not hashes: return None
    # Copie pour ne pas modifier la liste originale
    current_level = list(hashes)
    while len(current_level) > 1:
        if len(current_level) % 2 != 0:
            current_level.append(current_level[-1])
        new_level = []
        for i in range(0, len(current_level), 2):
            combined = current_level[i] + current_level[i+1]
            new_level.append(hashlib.sha256(combined.encode()).hexdigest())
        current_level = new_level
    return current_level[0]

def run_audit():
    # Chemin vers les preuves
    path = "./MonProjet/allData"
    if not os.path.exists(path):
        print(f"ERROR: Directory {path} not found.")
        return

    files = sorted([os.path.join(path, f) for f in os.listdir(path) if f.endswith('.json')])
    
    if not files:
        print("INFO: No JSON proofs found in allData.")
        return

    print(f"AUDIT: Processing {len(files)} proof files...")
    file_hashes = [get_file_hash(f) for f in files]
    
    root_hash = build_merkle_root(file_hashes)
    
    # Generation de la date actuelle (Format: 2026-04-27 15:30:00)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Generation du sceau final
    seal = {
        "status": "INTEGRITY_VERIFIED",
        "audit_date": now_str,
        "total_proofs_count": len(files),
        "merkle_root": root_hash,
        "first_proof": os.path.basename(files[0]),
        "last_proof": os.path.basename(files[-1])
    }
    
    with open("merkle_seal.json", "w") as f:
        json.dump(seal, f, indent=4)
    
    print("\n--- SEALING COMPLETE ---")
    print(f"ROOT HASH : {root_hash}")
    print(f"AUDIT DATE: {now_str}")
    print("Report saved to: merkle_seal.json")

if __name__ == "__main__":
    run_audit()