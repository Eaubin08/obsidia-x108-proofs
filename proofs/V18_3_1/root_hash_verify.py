# OBSIDIA V18.3 — ROOT HASH VERIFIER
# Usage: python root_hash_verify.py
import os, hashlib, json, sys

ROOT_FILE="ROOT_HASH_V18_3.txt"
META_FILE="SEAL_META_V18_3.json"
MANIFEST="MASTER_MANIFEST_V18_3.json"

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def compute_root():
    entries=[]
    for root,_,files in os.walk("."):
        for fn in files:
            rel=os.path.relpath(os.path.join(root,fn), ".").replace("\\","/")
            if rel in (ROOT_FILE, META_FILE):
                continue
            entries.append(rel)
    entries=sorted(entries)
    lines=[]
    for rel in entries:
        lines.append(f"{sha256_file(rel)}  {rel}")
    root=hashlib.sha256(("\n".join(lines)+"\n").encode("utf-8")).hexdigest()
    return root

def parse_declared_root():
    if not os.path.exists(ROOT_FILE):
        return None
    for line in open(ROOT_FILE,"r",encoding="utf-8",errors="ignore"):
        if line.startswith("RootHash:"):
            return line.split(":",1)[1].strip()
    return None

def main():
    declared=parse_declared_root()
    if not declared:
        print("FAIL: declared root not found")
        sys.exit(2)
    got=compute_root()
    if got!=declared:
        print("FAIL: root hash mismatch")
        print(" got:", got)
        print(" exp:", declared)
        sys.exit(1)
    if os.path.exists(META_FILE):
        meta=json.load(open(META_FILE,"r",encoding="utf-8"))
        mh=sha256_file(MANIFEST) if os.path.exists(MANIFEST) else None
        rh=sha256_file(ROOT_FILE)
        if mh and meta["sha256"]["MASTER_MANIFEST_V18_3.json"]!=mh:
            print("FAIL: manifest sha mismatch")
            sys.exit(1)
        if meta["sha256"]["ROOT_HASH_V18_3.txt"]!=rh:
            print("FAIL: root file sha mismatch")
            sys.exit(1)
        g=hashlib.sha256((mh+"\n"+rh+"\n").encode("utf-8")).hexdigest() if mh else None
        if g and meta["sha256"]["GLOBAL_SEAL_HASH"]!=g:
            print("FAIL: global seal mismatch")
            sys.exit(1)
    print("PASS")
    sys.exit(0)

if __name__=="__main__":
    main()
