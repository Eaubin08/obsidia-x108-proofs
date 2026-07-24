"""
generate_manifest_sha256_patched.py
──────────────────────────────────────────────────────────────────────────────
PATCH V1 — 2026-06-22
Faille corrigée (P0) : "apps" était dans EXCLUDE_DIRS, excluant toute l'API
                       de la preuve d'intégrité cryptographique.
Correction : "apps" retiré de EXCLUDE_DIRS. Les routes API (main.py, pipelines,
             middleware) sont désormais incluses dans le manifest SHA256.

PATCH V2 — 2026-07-07 (OLD-9B1)
Failles corrigées :
  - Artefacts locaux gitignorés (.local_audits/, .local_exports/, etc.)
    étaient inclus dans le manifest — ces chemins ne sont jamais poussés
    sur le dépôt public et ne doivent pas figurer dans la preuve d'intégrité.
  - MANIFEST_SHA256.json lui-même et ses variantes (NEW, RECURSIVE) étaient
    inclus, créant une auto-référence instable à chaque régénération.
  - cic_readonly_binding_v0.yaml (directive COMMIT/FREEZE/PUSH: NO) était inclus.
Correction : ajout de EXCLUDE_DIRS_LOCAL et EXCLUDE_FILES.
──────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import hashlib
import json
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("obsidia.manifest.sha256")


# ── Dossiers exclus du hash ────────────────────────────────────────────────
#
# PATCH P0 : "apps" retiré intentionnellement.
# Les routes API, pipelines et middlewares sous apps/ sont désormais
# soumis à la preuve d'intégrité cryptographique.
# Toute modification non autorisée de apps/ sera détectable.
#
EXCLUDE_DIRS: frozenset[str] = frozenset({
    # Outils / cache standards
    ".git",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
    # "apps" retiré — inclus dans la preuve cryptographique
    # PATCH V2 — artefacts locaux gitignorés (jamais poussés sur le dépôt public)
    ".local_audits",
    ".local_exports",
    ".local_freezes",
    ".local_reports",
    ".local_test_runs",
    ".local_verify",
    ".local_obsidia",
    ".runtime_freezes",
    "_PATCH_PROPOSALS",
    "_freezes",
    "_tmp_core_import",
    "_EPHEMERAL_CODE_SANDBOX",
    "SOURCE_PACKS_DEEP_DIFF_AUDIT",
    "LOCAL_AUDIT",
    "LOCAL_READ",
    "LOCAL_ONLY",
    "AUDIT_ALL",
    "OBSIDIA_COMPONENT_",
})

# ── Fichiers exclus nominalement ───────────────────────────────────────────
#
# PATCH V2 : exclusions par nom de fichier exact (indépendantes du répertoire).
# - MANIFEST_SHA256*.json : auto-référence instable à chaque régénération.
# - cic_readonly_binding_v0.yaml : directive COMMIT/FREEZE/PUSH: NO.
#
EXCLUDE_FILES: frozenset[str] = frozenset({
    "MANIFEST_SHA256.json",
    "MANIFEST_SHA256_NEW.json",
    "MANIFEST_SHA256_RECURSIVE.json",
    "cic_readonly_binding_v0.yaml",
})

# Extensions couvertes par le manifest
INCLUDE_EXTENSIONS: frozenset[str] = frozenset({
    ".py",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".md",
    ".lean",
    ".tla",
})


def should_hash_file(path: Path) -> bool:
    """
    Détermine si un fichier doit être inclus dans le manifest SHA256.

    Critères :
      - Le nom du fichier n'est pas dans EXCLUDE_FILES.
      - Le chemin ne traverse pas un dossier exclu (exact ou par préfixe).
      - L'extension est dans INCLUDE_EXTENSIONS.
    """
    # Exclusion par nom de fichier exact (PATCH V2)
    if path.name in EXCLUDE_FILES:
        return False
    # Exclusion par répertoire (exact ou préfixe pour les variantes générées)
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return False
        # Préfixes : _EPHEMERAL_CODE_SANDBOX_*, AUDIT_ALL_*, OBSIDIA_COMPONENT_*, etc.
        for prefix in (
            "_EPHEMERAL_CODE_SANDBOX",
            "AUDIT_ALL",
            "OBSIDIA_COMPONENT_",
            "SOURCE_PACKS_DEEP_DIFF_AUDIT",
            "LOCAL_AUDIT_",
            "LOCAL_READ_",
            "LOCAL_ONLY_",
        ):
            if part.startswith(prefix):
                return False
    return path.suffix in INCLUDE_EXTENSIONS


def compute_file_sha256(path: Path) -> str:
    """Calcule le SHA256 d'un fichier."""
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


def iter_tracked_files(root_dir: Path) -> list[Path]:
    """
    Retourne la liste des fichiers trackés par Git sous root_dir.

    PATCH V3 — Remplace rglob("*") par git ls-files pour garantir
    que le manifest ne contient que des fichiers commités/trackés.
    Git est la seule source d'autorité : les dossiers locaux, gitignorés
    ou non-trackés sont exclus automatiquement.
    """
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root_dir,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    paths: list[Path] = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        rel = raw.decode("utf-8", errors="strict")
        paths.append(root_dir / rel)
    return paths


def generate_manifest(root_dir: Path) -> dict[str, Any]:
    """
    Génère le manifest SHA256 de tous les fichiers couverts sous root_dir.

    Returns:
        Dict structuré avec la liste des fichiers hashés et le hash global.
    """
    file_hashes: dict[str, str] = {}
    skipped: list[str] = []

    for path in sorted(iter_tracked_files(root_dir)):
        if not path.is_file():
            continue
        relative = path.relative_to(root_dir)
        if should_hash_file(relative):
            try:
                file_hashes[str(relative)] = compute_file_sha256(path)
            except OSError as exc:
                logger.warning("MANIFEST_SKIP: %s — %s", relative, exc)
                skipped.append(str(relative))
        else:
            skipped.append(str(relative))

    # Hash global du manifest (hash des hashes)
    global_hash = hashlib.sha256(
        json.dumps(file_hashes, sort_keys=True).encode()
    ).hexdigest()

    manifest: dict[str, Any] = {
        "manifest_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root_dir": str(root_dir),
        "global_sha256": global_hash,
        "file_count": len(file_hashes),
        "skipped_count": len(skipped),
        "exclude_dirs": sorted(EXCLUDE_DIRS),
        "include_extensions": sorted(INCLUDE_EXTENSIONS),
        # PATCH : apps/ est maintenant dans files (plus dans skipped)
        "apps_included_in_manifest": True,
        "files": file_hashes,
    }

    logger.info(
        "MANIFEST_GENERATED: %d files hashed, %d skipped, global=%s",
        len(file_hashes),
        len(skipped),
        global_hash[:16] + "...",
    )
    return manifest


def verify_manifest(
    manifest_path: Path,
    root_dir: Path,
) -> dict[str, Any]:
    """
    Vérifie l'intégrité du repo en comparant les hashes actuels au manifest.

    Returns:
        Dict avec status (OK/TAMPERED), liste des fichiers modifiés.
    """
    with open(manifest_path, encoding="utf-8") as f:
        saved_manifest: dict[str, Any] = json.load(f)

    current = generate_manifest(root_dir)
    saved_files: dict[str, str] = saved_manifest.get("files", {})
    current_files: dict[str, str] = current.get("files", {})

    tampered: list[str] = []
    added: list[str] = []
    removed: list[str] = []

    for path, saved_hash in saved_files.items():
        current_hash = current_files.get(path)
        if current_hash is None:
            removed.append(path)
        elif current_hash != saved_hash:
            tampered.append(path)

    for path in current_files:
        if path not in saved_files:
            added.append(path)

    status = "OK" if not (tampered or added or removed) else "TAMPERED"

    if status == "TAMPERED":
        logger.warning(
            "MANIFEST_TAMPERED: modified=%d added=%d removed=%d",
            len(tampered), len(added), len(removed),
        )

    return {
        "status": status,
        "tampered_files": tampered,
        "added_files": added,
        "removed_files": removed,
        "saved_global_sha256": saved_manifest.get("global_sha256"),
        "current_global_sha256": current.get("global_sha256"),
    }


if __name__ == "__main__":
    import sys

    repo_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    manifest = generate_manifest(repo_root)
    output_path = repo_root / "manifest_sha256.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"Manifest généré : {output_path}")
    print(f"Fichiers hashés : {manifest['file_count']}")
    print(f"Global SHA256   : {manifest['global_sha256']}")
    print(f"apps/ inclus    : {manifest['apps_included_in_manifest']}")
