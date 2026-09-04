"""Check for forbidden content ? excludes known policy/docs false positives."""
import os
import sys

FORBIDDEN = [".venv", "node_modules", "__pycache__", ".pytest_cache"]
SECRET_PATTERNS = ["private_key", "seed_phrase", "api_key", "secret_key", "mnemonic", "keystore"]

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".graph-memory",
    ".claude",
    "_local_audits",
    ".local_audits",
    "_freezes",
    "_backups",
    "_source_packs",
}

ALLOWED_EXACT_PATHS = {
    "apps/obsidia_api/brody_secret_scrubber.py",
}

ALLOWED_FILES = {
    ".env.example",
}

ALLOWED_PATH_FRAGMENTS = [
    "docs/blockchain/",
    "specs/10_VALUE_GENCOIN_JCOIN/",
    "periphery/blockchain/",
    "periphery/world_calls/secret_boundary",
    "04_SECURITE_PAREFEU/SECRET_GUARD.md",
    "tests/",
    "docs/security/",
    ".github/workflows/",
    "docs/core_import/POST_P80_SECRET_ROTATION",
]

def norm(path: str) -> str:
    return path.replace("\\", "/")

violations = []

for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

    for f in files:
        path = norm(os.path.join(root, f))
        fname = f.lower()

        if f in ALLOWED_FILES:
            continue

        repo_rel = path[2:] if path.startswith("./") else path
        if repo_rel in ALLOWED_EXACT_PATHS:
            continue

        if any(fragment in path for fragment in ALLOWED_PATH_FRAGMENTS):
            continue

        if any(b in path for b in FORBIDDEN):
            violations.append(f"FORBIDDEN_DIR:{path}")

        if any(s in fname for s in ["private_key", "secret", "credential", "token", "api_key"]):
            violations.append(f"SUSPICIOUS_FILE:{path}")

if violations:
    for v in violations:
        print(v)
    sys.exit(1)

print("FORBIDDEN_CONTENT_PASS")
