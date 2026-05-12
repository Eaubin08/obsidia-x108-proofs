import argparse
import csv
import hashlib
import json
import re
from datetime import datetime
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
    "scope": "BRODY_GRAPHITI_READY_EXPORT_PERIPHERY_ONLY",
}

HOT_TAG_PATTERNS = {
    "x108": [
        r"\bx-?108\b",
        r"\bkx108\b",
        r"\btemporal\s+gate\b",
        r"\bhold\s*[-→>]*\s*act\b",
    ],
    "kernel": [
        r"\bkernel\b",
        r"\bnoyau\b",
        r"\bos0\b",
        r"\binvariant\b",
        r"\binvariants\b",
    ],
    "proof": [
        r"\bproof\b",
        r"\bpreuve\b",
        r"\bpreuves\b",
        r"\blean\b",
        r"\btla\+?\b",
        r"\btheorem\b",
        r"\bth[eé]or[eè]me\b",
        r"\bformal\b",
    ],
    "audit": [
        r"\baudit\b",
        r"\btrace\b",
        r"\bledger\b",
        r"\bhash\b",
        r"\bsha256\b",
        r"\bmerkle\b",
        r"\bimmutabilit[eé]\b",
    ],
    "graphiti": [
        r"\bgraphiti\b",
    ],
    "session": [
        r"\bsession\b",
        r"\bconversation\b",
        r"\bdialogue\b",
        r"\bjournal\b",
    ],
    "34_arbres": [
        r"\b34\s+arbres?\b",
        r"\barbres?_34\b",
        r"\b34[_ -]arbres?\b",
        r"\bmatrice\s+des\s+34\s+arbres\b",
        r"\b34\s+trees?\b",
        r"\bshazam\b",
        r"\bhexaflux\b",
        r"\bcartographe\b",
        r"\batlas\b",
    ],
    "canon": [
        r"\bcanon\b",
        r"\bcanonical\b",
        r"\bregistre\b",
        r"\bregistry\b",
    ],
    "world_intake": [
        r"\bworld\s+intake\b",
        r"\bsource\s+intake\b",
    ],
}


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="replace")).hexdigest().upper()

def read_text_safe(path: Path, limit: int = 12000) -> str:
    try:
        txt = path.read_text(encoding="utf-8-sig", errors="replace")
        return txt[:limit]
    except Exception as e:
        return f"[READ_ERROR] {type(e).__name__}: {e}"

def parse_pointer(path: Path) -> dict:
    out = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out

def tags_for(blob: str):
    low = blob.lower()
    tags = []
    for tag, patterns in HOT_TAG_PATTERNS.items():
        if any(re.search(pattern, low, flags=re.IGNORECASE) for pattern in patterns):
            tags.append(tag)
    return sorted(set(tags))

def normalize_path(p: str, base: Path) -> Path:
    if not p:
        return Path("")
    path = Path(p)
    if path.is_absolute():
        return path
    return (base / path).resolve()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--world-pointer", required=True)
    ap.add_argument("--graphiti-pointer", required=False, default="")
    ap.add_argument("--out-root", required=True)
    ap.add_argument("--label", required=True)
    args = ap.parse_args()

    root = Path(args.root).resolve()
    world_pointer = Path(args.world_pointer).resolve()
    graphiti_pointer = Path(args.graphiti_pointer).resolve() if args.graphiti_pointer else None
    out_root = Path(args.out_root).resolve()

    world_ptr = parse_pointer(world_pointer)
    graphiti_ptr = parse_pointer(graphiti_pointer) if graphiti_pointer else {}

    manifest_path = Path(world_ptr.get("MANIFEST", ""))
    if not manifest_path.exists():
        raise SystemExit(f"WORLD_MANIFEST_NOT_FOUND={manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig", errors="replace"))

    run_dir = out_root / f"BRODY_GRAPHITI_READY_EXPORT_{args.label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir.mkdir(parents=True, exist_ok=True)

    records_path = run_dir / "graphiti_ready_records.jsonl"
    index_path = run_dir / "graphiti_ready_index.json"
    metrics_path = run_dir / "graphiti_ready_metrics.json"
    hits34_path = run_dir / "graphiti_ready_34_arbres_hits.csv"
    status_json = run_dir / "GRAPHITI_READY_EXPORT_STATUS.json"
    status_txt = run_dir / "GRAPHITI_READY_EXPORT_STATUS.txt"

    records = []
    hits34 = []

    files = manifest.get("files", [])
    for i, f in enumerate(files):
        source_original_path = str(f.get("source_original_path", ""))
        md_path = normalize_path(str(f.get("path", "")), root)

        extracted_text = read_text_safe(md_path)
        title = Path(source_original_path).name or Path(str(f.get("path", ""))).name

        # Taxonomy must classify semantic content, not timestamps, root paths, or generated intake paths.
        # Path metadata is kept in the record, but excluded from tag matching to avoid false universal tags.
        tag_blob = " ".join([
            title,
            extracted_text[:3000],
        ])

        rec_tags = tags_for(tag_blob)

        rec = {
            "id": f"BRODY_GRAPHITI_READY_{i:06d}",
            "title": title,
            "source_original_path": source_original_path,
            "normalized_md_path": str(md_path),
            "original_extension": f.get("original_extension"),
            "extraction_status": f.get("extraction_status"),
            "extractor": f.get("extractor"),
            "content_usable": bool(f.get("content_usable")),
            "source_original_sha256": f.get("source_original_sha256") or f.get("sha256"),
            "text_sha256": sha256_text(extracted_text),
            "text_excerpt": extracted_text[:3000],
            "tags": rec_tags,
            **BOUNDARY,
        }
        records.append(rec)

        if "34_arbres" in rec_tags:
            hits34.append({
                "id": rec["id"],
                "title": title,
                "source_original_path": source_original_path,
                "original_extension": rec["original_extension"],
                "extraction_status": rec["extraction_status"],
                "content_usable": rec["content_usable"],
                "sha256": rec["source_original_sha256"],
            })

    with records_path.open("w", encoding="utf-8", newline="\n") as w:
        for r in records:
            w.write(json.dumps(r, ensure_ascii=False) + "\n")

    tag_counts = {}
    for r in records:
        for t in r["tags"]:
            tag_counts[t] = tag_counts.get(t, 0) + 1

    metrics = {
        "status": "BRODY_GRAPHITI_READY_EXPORT_READONLY_PASS",
        "label": args.label,
        "records_count": len(records),
        "usable_records_count": sum(1 for r in records if r["content_usable"]),
        "tag_counts": tag_counts,
        "hits_34_arbres_count": len(hits34),
        "world_manifest": str(manifest_path),
        "world_pointer": str(world_pointer),
        "graphiti_pointer": str(graphiti_pointer) if graphiti_pointer else None,
        "graphiti_current": graphiti_ptr,
        **BOUNDARY,
    }

    index = {
        "status": "BRODY_GRAPHITI_READY_INDEX_BUILT",
        "records_path": str(records_path),
        "metrics_path": str(metrics_path),
        "hits34_path": str(hits34_path),
        "records_count": len(records),
        "tags": tag_counts,
        **BOUNDARY,
    }

    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    status_json.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    with hits34_path.open("w", encoding="utf-8", newline="") as w:
        fieldnames = ["id", "title", "source_original_path", "original_extension", "extraction_status", "content_usable", "sha256"]
        writer = csv.DictWriter(w, fieldnames=fieldnames)
        writer.writeheader()
        for row in hits34:
            writer.writerow(row)

    status_txt.write_text(
        "\n".join([
            f"CURRENT_BRODY_GRAPHITI_READY_EXPORT_READONLY={run_dir}",
            f"RECORDS={records_path}",
            f"INDEX={index_path}",
            f"METRICS={metrics_path}",
            f"HITS_34_ARBRES={hits34_path}",
            f"STATUS=BRODY_GRAPHITI_READY_EXPORT_READONLY_PASS",
            f"RECORDS_COUNT={len(records)}",
            f"USABLE_RECORDS_COUNT={metrics['usable_records_count']}",
            f"HITS_34_ARBRES_COUNT={len(hits34)}",
            "MEMORY_DECISION=false",
            "DECISION_AUTHORITY=KX108_ONLY",
            "KERNEL_MUTATION=false",
            "X108_MERGE=false",
            "NEXT=BUILD_OR_REFRESH_GRAPHITI_READONLY_INDEX",
            "",
        ]),
        encoding="utf-8",
    )

    current = root / "CURRENT_BRODY_GRAPHITI_READY_EXPORT_READONLY.txt"
    current.write_text(status_txt.read_text(encoding="utf-8"), encoding="utf-8")

    print(json.dumps(metrics, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
