# OBSIDIA V18.3 – ROOT HASH VERIFIER (PATCHED – ANTI-NOISE & AUTO-SEAL)
# Usage: python root_hash_verify.py [--update]
import os, hashlib, json, sys

ROOT_FILE = "ROOT_HASH_V18_3.txt"
META_FILE = "SEAL_META_V18_3.json"
MANIFEST = "MASTER_MANIFEST_V18_3.json"

def canonical_bytes(path):
    data = open(path, "rb").read()
    if b"\x00" in data:
        return data
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")

def sha256_file(path):
    h = hashlib.sha256()
    h.update(canonical_bytes(path))
    return h.hexdigest()

def compute_root():
    entries = []
    for root, dirs, files in os.walk("."):
        # Élimination systématique des répertoires de cache pour éviter le drift NTFS/Windows
        if "__pycache__" in root or ".git" in root or "_local_audits" in root:
            continue
        for fn in files:
            # Ignorer les résidus d'exécution, fichiers temporaires et système
            if fn.endswith(".pyc") or fn.startswith(".") or fn.endswith(".tmp") or fn == "desktop.ini":
                continue
            rel = os.path.relpath(os.path.join(root, fn), ".").replace("\\", "/")
            if rel in (ROOT_FILE, META_FILE):
                continue
            entries.append(rel)

    entries = sorted(entries)
    lines = []
    for rel in entries:
        lines.append(f"{sha256_file(rel)}  {rel}")

    return hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()

def parse_declared_root():
    if not os.path.exists(ROOT_FILE):
        return None
    content = open(ROOT_FILE, "r", encoding="utf-8").read().strip()
    return content.split()[0] if content else None

def main():
    update_mode = "--update" in sys.argv

    if update_mode:
        print("[SYSTEM] Mode réalignement automatique activé.")
    
    declared = parse_declared_root()
    got = compute_root()

    if update_mode:
        # Écriture déterministe du nouveau Hash Racine validé sur le disque
        with open(ROOT_FILE, "w", encoding="utf-8", newline="\n") as f:
            f.write(f"{got}\n")
        print(f"[SUCCESS] Nouveau hash racine scellé : {got}")
        declared = got

    if not declared:
        print("FAIL: declared root not found")
        sys.exit(2)

    if got != declared:
        print("FAIL: root hash mismatch")
        print(" got:", got)
        print(" exp:", declared)
        sys.exit(1)

    if os.path.exists(META_FILE):
        meta = json.load(open(META_FILE, "r", encoding="utf-8"))
        mh = sha256_file(MANIFEST) if os.path.exists(MANIFEST) else None
        rh = sha256_file(ROOT_FILE)

        if mh and meta["sha256"]["MASTER_MANIFEST_V18_3.json"] != mh:
            if update_mode:
                meta["sha256"]["MASTER_MANIFEST_V18_3.json"] = mh
            else:
                print("FAIL: manifest sha mismatch")
                sys.exit(1)

        if meta["sha256"]["ROOT_HASH_V18_3.txt"] != rh:
            if update_mode:
                meta["sha256"]["ROOT_HASH_V18_3.txt"] = rh
            else:
                print("FAIL: root file sha mismatch")
                sys.exit(1)

        g = hashlib.sha256((mh + "\n" + rh + "\n").encode("utf-8")).hexdigest() if mh else None
        if g and meta["sha256"]["GLOBAL_SEAL_HASH"] != g:
            if update_mode:
                meta["sha256"]["GLOBAL_SEAL_HASH"] = g
            else:
                print("FAIL: global seal mismatch")
                sys.exit(1)
                
        if update_mode:
            with open(META_FILE, "w", encoding="utf-8", newline="\n") as f:
                json.dump(meta, f, indent=4)
            print("[SUCCESS] Métadonnées de scellage (SEAL_META) recalculées et synchronisées.")

    print("PASS")
    sys.exit(0)

if __name__ == "__main__":
    main()
