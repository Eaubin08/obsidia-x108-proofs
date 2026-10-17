"""
scripts/download_linguistic_corpora.py

Downloads and verifies official, legal French and English lexical datasets
according to data/linguistic_corpus/DOWNLOAD_MANIFEST.json.

Datasets:
- Morphalou 3.1 (LGPL-LR, ATILF CNRS / ORTOLANG)
- UniMorph French (CC-BY-SA 4.0, UniMorph Consortium)
- UniMorph English (CC-BY-SA 4.0, UniMorph Consortium)
- Open English WordNet 2025 (CC-BY 4.0, Global WordNet Association)
- French Thesaurus (MPL 2.0 / LGPL 3.0 / GPL 3.0, Dicollecte / LibreOffice)
- Princeton WordNet Morphological Exceptions (BSD-style, Princeton / NLTK)
- XMLittré (CC-BY-SA 3.0 / Public Domain, François Gannaz / Littre.org)
- FreeDict French-English Dictionary (GPL v2+, FreeDict Project)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW_DIR = ROOT / "_external_sources" / "lexicon" / "raw"
DEFAULT_MANIFEST = ROOT / "data" / "linguistic_corpus" / "DOWNLOAD_MANIFEST.json"


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def download_file(url: str, dest_path: Path) -> tuple[int, str]:
    print(f"Downloading {url} -> {dest_path.name}...")
    start = time.perf_counter()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ObsidiaLexiconIngestor/1.0"}
    req = urllib.request.Request(url, headers=headers)

    sha256 = hashlib.sha256()
    bytes_downloaded = 0

    temp_path = dest_path.with_suffix(dest_path.suffix + ".tmp")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp, open(temp_path, "wb") as f:
            while True:
                chunk = resp.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)
                sha256.update(chunk)
                bytes_downloaded += len(chunk)
                print(f"  {bytes_downloaded / (1024 * 1024):.1f} MB downloaded...", end="\r", flush=True)

        if temp_path.exists():
            if dest_path.exists():
                dest_path.unlink()
            temp_path.rename(dest_path)
    finally:
        if temp_path.exists():
            temp_path.unlink()

    elapsed = time.perf_counter() - start
    digest = sha256.hexdigest()
    print(f"\n  Done: {bytes_downloaded:,} bytes in {elapsed:.2f}s (SHA256: {digest[:16]}...)")
    return bytes_downloaded, digest


def main():
    parser = argparse.ArgumentParser(description="Download and verify linguistic corpora for Obsidia/Brody.")
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR, help="Destination directory for raw archives.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Path to DOWNLOAD_MANIFEST.json.")
    parser.add_argument("--force", action="store_true", help="Force redownload even if files exist.")
    args = parser.parse_args()

    raw_dir: Path = args.raw_dir
    manifest_path: Path = args.manifest
    force: bool = args.force

    if not manifest_path.exists():
        print(f"ERROR: Manifest not found at {manifest_path}", file=sys.stderr)
        sys.exit(1)

    with open(manifest_path, "r", encoding="utf-8") as f:
        datasets = json.load(f)

    raw_dir.mkdir(parents=True, exist_ok=True)
    print(f"=== Obsidia Linguistic Corpora Download & Verification ===")
    print(f"Destination: {raw_dir}")
    print(f"Datasets: {len(datasets)}")

    results = []
    failures = []

    for item in datasets:
        filename = item["filename"]
        expected_sha = item["sha256"]
        dest_file = raw_dir / filename

        print(f"\nProcessing [{item['id']}] {item['name']}...")
        if dest_file.exists() and not force:
            print(f"  Found existing file ({dest_file.stat().st_size:,} bytes). Verifying SHA256...")
            current_sha = compute_sha256(dest_file)
            if current_sha.lower() == expected_sha.lower():
                print(f"  SHA256 OK: {current_sha}")
                results.append({
                    **item,
                    "bytes_downloaded": dest_file.stat().st_size,
                    "sha256": current_sha,
                    "local_path": str(dest_file),
                })
                continue
            else:
                print(f"  SHA256 mismatch (expected {expected_sha}, got {current_sha}). Re-downloading...")

        try:
            b_count, d_sha = download_file(item["url"], dest_file)
            if d_sha.lower() != expected_sha.lower():
                print(f"ERROR: SHA256 verification failed for {filename}!", file=sys.stderr)
                print(f"  Expected: {expected_sha}", file=sys.stderr)
                print(f"  Got:      {d_sha}", file=sys.stderr)
                failures.append(filename)
            else:
                print(f"  Verified SHA256 matches pinned hash.")
                results.append({
                    **item,
                    "bytes_downloaded": b_count,
                    "sha256": d_sha,
                    "local_path": str(dest_file),
                })
        except Exception as exc:
            print(f"ERROR: Failed to download {item['url']}: {exc}", file=sys.stderr)
            failures.append(filename)

    # Write download_manifest.json in raw_dir.parent for backward compatibility
    try:
        manifest_out = raw_dir.parent / "download_manifest.json"
        with open(manifest_out, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nManifest recorded at {manifest_out}")
    except Exception as exc:
        print(f"Notice: Could not write secondary manifest: {exc}")

    if failures:
        print(f"\nFAILURE: {len(failures)} dataset(s) failed download or verification: {failures}", file=sys.stderr)
        sys.exit(1)

    print("\nALL DATASETS VERIFIED SUCCESSFULLY.")


if __name__ == "__main__":
    main()
