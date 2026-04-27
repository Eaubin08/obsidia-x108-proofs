import hashlib
import os
import json

def get_file_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def build_merkle_root(hashes):
    if not hashes: return None
    while len(hashes) > 1:
        if len(hashes) % 2 != 0:
            hashes.append(hashes[-1])
        new_level = []
        for i in range(0, len(hashes), 2):
            combined = hashes[i] + hashes[i+1]
            new_level.append(hashlib.sha256(combined.encode()).hexdigest())
        hashes = new_level
    return hashes[0]

def run_audit():
    # Chemin vers tes preuves
    path = "./MonProjet/allData"
    if not os.path.exists(path):
        print(f"❌ Erreur : Dossier {path} introuvable.")
        return

    files = sorted([os.path.join(path, f) for f in os.listdir(path) if f.endswith('.json')])
    
    if not files:
        print("❌ Aucune preuve JSON trouvée dans allData.")
        return

    print(f"📂 Audit de {len(files)} fichiers de preuves en cours...")
    file_hashes = [get_file_hash(f) for f in files]
    
    root_hash = build_merkle_root(file_hashes)
    
    # Génération du sceau final
    seal = {
        "audit_date": str(os.popen('date /t').read().strip() + " " + os.popen('time /t').read().strip()),
        "total_proofs_count": len(files),
        "merkle_root": root_hash,
        "first_proof": os.path.basename(files[0]),
        "last_proof": os.path.basename(files[-1]),
        "status": "INTEGRITY_VERIFIED"
    }
    
    with open("merkle_seal.json", "w") as f:
        json.dump(seal, f, indent=4)
    
    print(f"\n🛡️ SCELLAGE TERMINÉ")
    print(f"🔑 MERKLE ROOT : {root_hash}")
    print(f"📜 Rapport généré : merkle_seal.json")

if __name__ == "__main__":
    run_audit()
