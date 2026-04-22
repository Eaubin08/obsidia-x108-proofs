# OBSIDIA V18.3 FINAL — SEAL VERIFIER
# Usage: python seal_verify.py
import hashlib, json, os, sys

MANIFEST="MASTER_MANIFEST_V18_3.json"

def sha256_file(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    if not os.path.exists(MANIFEST):
        print("FAIL: manifest not found:", MANIFEST)
        sys.exit(2)
    m=json.load(open(MANIFEST,"r",encoding="utf-8"))
    bad=[]
    for rel, expected in m["sha256"].items():
        p=os.path.join(os.path.dirname(MANIFEST), rel)
        if expected is None: 
            continue
        if not os.path.exists(p):
            bad.append((rel,"missing",expected))
            continue
        got=sha256_file(p)
        if got!=expected:
            bad.append((rel,got,expected))
    if bad:
        print("FAIL")
        for rel,got,exp in bad:
            print(" -", rel, "got", got, "expected", exp)
        sys.exit(1)
    print("PASS")
    sys.exit(0)

if __name__=="__main__":
    main()
