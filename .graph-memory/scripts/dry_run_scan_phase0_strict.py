from pathlib import Path
import subprocess
import fnmatch
from datetime import datetime, timezone

ROOT = Path.cwd()
REPORTS = ROOT / ".graph-memory" / "reports"

ALLOW_PATTERNS = [
    "agents/registry.md",
    "agents/registry.json",
    "agents/prompts/*.md",
    "agents/bootstrap/*.md",
    "agents/routing/*.md",
    "CLAUDE.md",
    "MANIFEST.md",
    ".claude/context/*.md",
    ".claude/skills/*/SKILL.md",
]

CONDITIONAL_ALLOW = [
    "sigma/*.py",
    "sigma/tests/*.py",
    "connectors/**/*.py",
    "qa/**/*.py",
    ".github/workflows/*.yml",
]

DENY_PATTERNS = [
    "proofs/V18_*/**",
    "proofs/lean/**",
    "proofs/tla/**",
    "formal/tla/**",
    "proofs/merkle_root.json",
    "proofs/merkle_seal.json",
    "merkle_root.json",
    "merkle_seal.json",
    "proofs/rfc3161_anchor.json",
    "server.kernel.sealed.cjs",
    "*root*",
    "*seal*",
    "*hash*",
    "*anchor*",
    "*freeze*",
    ".env",
    ".env.*",
    "secrets/**",
    "*.pem",
    "audit/local/**",
    "archive/diagnostics/local_diag/**",
    "RECUPE_SCORING/aggregation_stable.py",
    "RECUPE_SCORING/contracts_stable.py",
    "sigma/contracts.broken-ragnarok.py",
    "vendor/wheels/**",
    "System.*/**",
    "Google.Protobuf.*/**",
    "node_modules/**",
    ".git/**",
    "__pycache__/**",
    ".pytest_cache/**",
    "artifacts/**",
    "archive/**",
    "staging/runtime_candidates/**",
]

def git_files():
    out = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True, encoding="utf-8", errors="replace")
    return [x.strip().replace("\\", "/") for x in out.splitlines() if x.strip()]

def match_any(path, patterns):
    p = path.replace("\\", "/")
    low = p.lower()
    for pat in patterns:
        pat_low = pat.lower()
        if fnmatch.fnmatch(low, pat_low):
            return pat
    return None

def file_stats(path):
    full = ROOT / path
    try:
        size = full.stat().st_size
    except FileNotFoundError:
        size = 0
    estimated_tokens = max(1, round(size / 4))
    return size, estimated_tokens

def write_report(name, content):
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / name).write_text(content.rstrip() + "\n", encoding="utf-8")

def main():
    files = git_files()

    allowed = []
    conditional = []
    denied = []
    ignored = []

    for f in files:
        deny_pat = match_any(f, DENY_PATTERNS)
        allow_pat = match_any(f, ALLOW_PATTERNS)
        conditional_pat = match_any(f, CONDITIONAL_ALLOW)

        if deny_pat:
            denied.append((f, deny_pat))
        elif allow_pat:
            size, toks = file_stats(f)
            allowed.append((f, allow_pat, size, toks))
        elif conditional_pat:
            size, toks = file_stats(f)
            conditional.append((f, conditional_pat, size, toks))
        else:
            ignored.append(f)

    now = datetime.now(timezone.utc).isoformat()

    allowed_total_bytes = sum(x[2] for x in allowed)
    allowed_total_tokens = sum(x[3] for x in allowed)

    dry = [
        "# Graph Memory Dry Run Candidates",
        "",
        f"Generated: {now}",
        "",
        "## Allowed candidates",
        "",
        "| File | Matched rule | Bytes | Est. tokens |",
        "|---|---|---:|---:|",
    ]
    for f, pat, size, toks in allowed:
        dry.append(f"| `{f}` | `{pat}` | {size} | {toks} |")

    dry += [
        "",
        "## Summary",
        "",
        f"- allowed files: {len(allowed)}",
        f"- total bytes: {allowed_total_bytes}",
        f"- estimated tokens: {allowed_total_tokens}",
    ]

    deny = [
        "# Graph Memory Denylist Hits",
        "",
        f"Generated: {now}",
        "",
        "| File | Matched deny rule |",
        "|---|---|",
    ]
    for f, pat in denied:
        deny.append(f"| `{f}` | `{pat}` |")

    cond = [
        "# Graph Memory Conditional Candidates",
        "",
        f"Generated: {now}",
        "",
        "These files are not indexed in Phase 0. They require explicit approval.",
        "",
        "| File | Matched conditional rule | Bytes | Est. tokens |",
        "|---|---|---:|---:|",
    ]
    for f, pat, size, toks in conditional:
        cond.append(f"| `{f}` | `{pat}` | {size} | {toks} |")

    budget = [
        "# Graph Memory Token Budget Estimate",
        "",
        f"Generated: {now}",
        "",
        "## Phase 0",
        "",
        f"- allowed files: {len(allowed)}",
        f"- estimated tokens: {allowed_total_tokens}",
        "",
        "## Conditional phase",
        "",
        f"- conditional files: {len(conditional)}",
        f"- estimated conditional tokens: {sum(x[3] for x in conditional)}",
        "",
        "## Ignored",
        "",
        f"- ignored files: {len(ignored)}",
        "",
        "## Denied",
        "",
        f"- denied files: {len(denied)}",
    ]

    write_report("dry_run_candidates.md", "\n".join(dry))
    write_report("denylist_hits.md", "\n".join(deny))
    write_report("conditional_candidates.md", "\n".join(cond))
    write_report("token_budget_estimate.md", "\n".join(budget))

    print("DRY_RUN_DONE")
    print(f"allowed_files={len(allowed)}")
    print(f"allowed_estimated_tokens={allowed_total_tokens}")
    print(f"conditional_files={len(conditional)}")
    print(f"denied_files={len(denied)}")
    print(f"ignored_files={len(ignored)}")

if __name__ == "__main__":
    main()
