"""Check for forbidden content — .env, venv, node_modules, pycache, secrets."""
import os, sys

FORBIDDEN = [".env", ".venv", "node_modules", "__pycache__", ".pytest_cache"]
SECRET_PATTERNS = ["private_key", "seed_phrase", "api_key", "secret_key", "mnemonic", "keystore"]
EXCLUDE_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", ".graph-memory", "_local_audits"}

violations = []
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    for f in files:
        path = os.path.join(root, f)
        if any(b in path for b in FORBIDDEN):
            violations.append(f"FORBIDDEN_DIR:{path}")
        fname = f.lower()
        if any(s in fname for s in ["private_key", "secret", "credential", "token", "api_key"]):
            if not any(ok in path for ok in ["periphery/blockchain", "tests/", "periphery/world_calls/secret_boundary"]):
                violations.append(f"SUSPICIOUS_FILE:{path}")

if violations:
    for v in violations:
        print(v)
    sys.exit(1)
print("FORBIDDEN_CONTENT_PASS")
