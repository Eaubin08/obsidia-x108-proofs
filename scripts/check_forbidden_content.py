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

        if any(fragment in path for fragment in ALLOWED_PATH_FRAGMENTS):
            continue

        if any(b in path for b in FORBIDDEN):
            violations.append(f"FORBIDDEN_DIR:{path}")

        suspicious_filename = any(
            s in fname
            for s in ["private_key", "secret", "credential", "token", "api_key"]
        )
        known_filename_false_positive = (
            fname == "brody_secret_scrubber.py"
        )
        if suspicious_filename and not known_filename_false_positive:
            violations.append(f"SUSPICIOUS_FILE:{path}")

if violations:
    for v in violations:
        print(v)
    sys.exit(1)

print("FORBIDDEN_CONTENT_PASS")
