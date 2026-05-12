import argparse
import json
import subprocess
import sys
from pathlib import Path

BOUNDARY = {
    "readonly": True,
    "memory_authority": False,
    "memory_decision": False,
    "allowed_to_decide": False,
    "emits_act": False,
    "kernel_binding": False,
    "x108_merge": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "decision_authority": "KX108_ONLY",
    "scope": "BRODY_WORLD_SOURCE_INTAKE_PERIPHERY_ONLY"
}

def read_kv(path: Path) -> dict:
    out = {}
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out

def bad_score(s: str) -> int:
    markers = ["â", "Ã", "Â", "�"]
    return sum(s.count(m) for m in markers)

def fix_mojibake(s: str) -> str:
    if not s:
        return s

    replacements = {
        "â€”": "—",
        "â€“": "–",
        "â†’": "→",
        "â€˜": "‘",
        "â€™": "’",
        "â€œ": "“",
        "â€�": "”",
        "â€¦": "…",
        "Â ": " ",
        "Â": "",
        "Ã©": "é",
        "Ãè": "è",
        "Ã¨": "è",
        "Ãª": "ê",
        "Ã ": "à",
        "Ã¢": "â",
        "Ã§": "ç",
        "Ã®": "î",
        "Ã´": "ô",
        "Ã»": "û",
        "Ã‰": "É",
    }

    fixed = s
    for a, b in replacements.items():
        fixed = fixed.replace(a, b)

    try:
        candidate = fixed.encode("cp1252", errors="strict").decode("utf-8", errors="strict")
        if bad_score(candidate) < bad_score(fixed):
            fixed = candidate
    except Exception:
        pass

    return fixed

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))

def write_json(path: Path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--out-root", required=True)
    ap.add_argument("--label", default="SOURCE")
    ap.add_argument("--v161-py", required=True)
    args = ap.parse_args()

    v161 = Path(args.v161_py)
    out_root = Path(args.out_root)

    cmd = [
        sys.executable,
        str(v161),
        "--source",
        args.source,
        "--out-root",
        str(out_root),
        "--label",
        args.label,
    ]

    subprocess.run(cmd, check=True)

    ptr = out_root / "CURRENT_BRODY_WORLD_SOURCE_INTAKE_READONLY.txt"
    kv = read_kv(ptr)
    manifest_path = Path(kv["MANIFEST"])
    manifest = load_json(manifest_path)

    cleaned_files = 0
    before_bad = 0
    after_bad = 0

    for rec in manifest.get("files", []):
        md_path = Path(rec.get("path", ""))
        if not md_path.exists():
            continue

        raw = md_path.read_text(encoding="utf-8-sig", errors="replace")
        before_bad += bad_score(raw)
        fixed = fix_mojibake(raw)
        after_bad += bad_score(fixed)

        if fixed != raw:
            md_path.write_text(fixed, encoding="utf-8")
            cleaned_files += 1

        if rec.get("snippet"):
            rec["snippet"] = fix_mojibake(rec["snippet"])

        rec["text_normalization"] = "MOJIBAKE_BASIC_CLEANUP_V1_6_2"
        rec["mojibake_bad_score_before"] = bad_score(raw)
        rec["mojibake_bad_score_after"] = bad_score(fixed)

    manifest["status"] = "BRODY_WORLD_SOURCE_INTAKE_READONLY_PASS"
    manifest["text_normalization"] = "MOJIBAKE_BASIC_CLEANUP_V1_6_2"
    manifest["cleaned_files_count"] = cleaned_files
    manifest["mojibake_bad_score_before"] = before_bad
    manifest["mojibake_bad_score_after"] = after_bad
    manifest.update(BOUNDARY)

    write_json(manifest_path, manifest)

    result = {
        "status": "BRODY_WORLD_SOURCE_INTAKE_V1_6_2_MOJIBAKE_CLEAN_PASS",
        "manifest": str(manifest_path),
        "files_count": manifest.get("files_count"),
        "usable_files_count": manifest.get("usable_files_count"),
        "cleaned_files_count": cleaned_files,
        "mojibake_bad_score_before": before_bad,
        "mojibake_bad_score_after": after_bad,
        **BOUNDARY
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
