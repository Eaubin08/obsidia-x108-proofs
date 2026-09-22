from __future__ import annotations

import ast
import csv
import hashlib
import json
import os
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / "architecture_v3"

SKIP_PREFIXES = (
    ".git/",
    "architecture_v3/",
)

TEXT_EXTENSIONS = {
    ".py", ".ps1", ".sh", ".js", ".ts", ".tsx", ".jsx",
    ".json", ".yaml", ".yml", ".md", ".lean", ".tla",
    ".toml", ".txt", ".csv", ".cjs", ".mjs"
}


def git_files():
    raw = subprocess.check_output(
        ["git", "ls-files", "-z"],
        cwd=ROOT
    )
    return [
        Path(p.decode("utf-8", errors="replace"))
        for p in raw.split(b"\0")
        if p
    ]


def sha256(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def classify_layer(path: str):
    p = path.lower()

    rules = [
        ("00_SCOPE_DISCIPLINE",
         ["scope", "claim_scope", "production_blocker", "reproducib"]),

        ("01_FOUNDATIONS_PHILOSOPHY",
         ["philosoph", "doctrine", "alignment"]),

        ("02_ONTOLOGY_SEMANTICS",
         ["ontology", "ontologie", "semantic", "symbolic"]),

        ("03_COSMOS_MMONDE_WORLD",
         ["cosmos", "mmonde", "world_protocol", "world_model", "continuum"]),

        ("04_NARRATIVE_PROVENANCE_NPL",
         ["narrative_provenance", "/npl", "human_logic", "cultural_matrix",
          "archive_gap", "hidden_transcript"]),

        ("05_MATHEMATICS",
         ["math", "tensor", "topolog", "geometr", "dimension"]),

        ("06_ENTROPY_THERMODYNAMICS_POG",
         ["entropy", "entrop", "lyapunov", "thermodynamic", "semantic_heat",
          "proof_of_governance"]),

        ("07_BALANCE_BUV_GEOMETRIES",
         ["buv", "balance_", "balance/", "geometries"]),

        ("08_CONSTITUTION_STRUCTURAL_LAWS",
         ["constitution", "structural_law", "high_law", "who_can_read",
          "action_lifecycle", "object_status_lifecycle"]),

        ("09_AGI_TREE34_FLUX",
         ["tree34", "trees_34", "34arbres", "34_arbres", "cognitive_tree",
          "tree_registry", "tree_activation"]),

        ("10_COGNITIVE_SYSTEM",
         ["brody", "obsidure", "sigma", "/agents/", "meta_agent",
          "reflex", "cognition"]),

        ("11_HIGH_PERIPHERY_MACHINERY",
         ["shazam", "hexaflux", "hexaflow", "/bdf/", "double_brain",
          "reverse_os", "ltcu", "consciousness_regime", "point_cloud"]),

        ("12_LANGUAGE_OS_TRAD_IR",
         ["os_trad", "translation", "interlanguage", "ir_alphabet",
          "language_router"]),

        ("13_MCP_TOOLS_CONNECTORS",
         ["mcp", "connector", "tool_call", "pretool"]),

        ("14_CONTEXT_MEMORY_EDUCATION",
         ["memory", "graphiti", "neo4j", "context_packet", "education"]),

        ("15_ATLAS_EXTERNAL_SIGNALS",
         ["atlas", "timeverse", "external_signal"]),

        ("16_X108_AUTHORITY_KERNEL",
         ["kx108", "guardx108", "guard_x108", "decision_ticket",
          "canonicaldecision", "canonical_decision", "x108_authority",
          "/kernel/", "sigma/guard.py"]),

        ("17_BOUNDARIES_ACTION_INGRESS",
         ["x108_ingress", "reality_gate", "action_boundary",
          "world_action", "worldcall"]),

        ("18_RUNTIME_CAPABILITIES_API",
         ["runtime_wiring", "source_runtime", "capability_", "apps/obsidia_api"]),

        ("19_INTERFACE_WORKBENCH_VISUALIZATION",
         ["workbench", "/interface/", "os_map", "visualization",
          "decision_card"]),

        ("20_DOMAINS_CRITICAL_WORLDS",
         ["domains/", "gps", "aviation", "defense", "bank", "trading",
          "ecommerce", "domain_packet"]),

        ("21_VALUE_GENCOIN_JCOIN",
         ["gencoin", "jcoin", "productive_value", "machine_work"]),

        ("22_BLOCKCHAIN_SECURITY",
         ["blockchain", "wallet", "smart_contract", "onchain", "defi",
          "oracle_freshness", "bridge_risk"]),

        ("23_SECURITY_COMPLIANCE",
         ["rssi", "rgpd", "compliance", "security/", "threat_model",
          "data_governance"]),

        ("24_FORMAL_METHODS",
         ["proofs/lean", "formal/", ".lean", ".tla", "theorem"]),

        ("25_OS3_PROOF_REPLAY_ATTESTATION",
         ["os3", "replay", "merkle", "rfc3161", "attestation",
          "trace_persistence"]),

        ("26_TEST_QA_REPRODUCIBILITY",
         ["tests/", "test_", "qa/", "pytest"]),

        ("27_AUDIT_EVIDENCE_ARTIFACTS",
         ["audit/", "audits/", "artifact", "receipt", "evidence",
          "report", "manifest_sha"]),

        ("28_FREEZE_CANON_REGISTRIES",
         ["freeze", "registry", "canonical_registry", "_runtime_freezes"]),

        ("29_RESEARCH_PEPITES_EVOLUTION",
         ["research", "pepites", "hypoth", "experiment"]),

        ("30_DEV_TOOLING_CI_STAGING",
         ["scripts/", "tools/", ".github/", "staging/", ".claude/",
          ".codex/", ".agents/"]),

        ("99_ARCHIVE_PROVENANCE",
         ["archive", "legacy", "_source_discovery", "_source_packs"]),
    ]

    # Priority cases
    if p.startswith("tests/") or "/tests/" in p or Path(p).name.startswith("test_"):
        return "26_TEST_QA_REPRODUCIBILITY"

    if p.startswith("proofs/lean/") or p.startswith("formal/") or p.endswith(".lean") or p.endswith(".tla"):
        return "24_FORMAL_METHODS"

    for layer, keys in rules:
        if any(k in p for k in keys):
            return layer

    return "UNCLASSIFIED"


def parse_python(path: Path):
    funcs = []
    classes = []
    imports = []

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(text)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                funcs.append(node.name)

            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)

            elif isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

    except Exception:
        pass

    return sorted(set(funcs)), sorted(set(classes)), sorted(set(imports))


files = git_files()

file_rows = []
function_rows = []
registry = []

for rel in files:
    rel_s = rel.as_posix()

    if rel_s.startswith(SKIP_PREFIXES):
        continue

    path = ROOT / rel

    if not path.is_file():
        continue

    layer = classify_layer(rel_s)
    ext = path.suffix.lower()

    funcs = []
    classes = []
    imports = []

    if ext == ".py":
        funcs, classes, imports = parse_python(path)

    size = path.stat().st_size

    entry = {
        "id": rel_s.upper()
            .replace("/", "__")
            .replace("\\", "__")
            .replace(".", "_")
            .replace("-", "_"),
        "source": rel_s,
        "extension": ext,
        "size_bytes": size,
        "sha256": sha256(path),
        "candidate_layer": layer,
        "canonical_layer": None if layer == "UNCLASSIFIED" else layer,
        "runtime_status": "TO_CLASSIFY",
        "authority": "TO_CLASSIFY",
        "functionality": "TO_CLASSIFY",
        "canonical_owner": "TO_CLASSIFY",
        "target_path": "TO_CLASSIFY",
        "migration_action": "KEEP_UNTIL_AUDITED",
        "tests": [],
        "proofs": [],
        "routes": [],
        "dependencies": imports,
        "functions": funcs,
        "classes": classes,
    }

    registry.append(entry)

    file_rows.append({
        "source": rel_s,
        "extension": ext,
        "size_bytes": size,
        "sha256": entry["sha256"],
        "candidate_layer": layer,
        "functionality": "TO_CLASSIFY",
        "runtime_status": "TO_CLASSIFY",
        "authority": "TO_CLASSIFY",
        "target_path": "TO_CLASSIFY",
        "migration_action": "KEEP_UNTIL_AUDITED",
    })

    for name in funcs:
        function_rows.append({
            "source": rel_s,
            "symbol_type": "FUNCTION",
            "symbol": name,
            "candidate_layer": layer,
            "functionality": "TO_CLASSIFY",
        })

    for name in classes:
        function_rows.append({
            "source": rel_s,
            "symbol_type": "CLASS",
            "symbol": name,
            "candidate_layer": layer,
            "functionality": "TO_CLASSIFY",
        })


def write_csv(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


write_csv(
    OUT / "FILE_TO_FUNCTIONALITY.csv",
    file_rows,
    [
        "source",
        "extension",
        "size_bytes",
        "sha256",
        "candidate_layer",
        "functionality",
        "runtime_status",
        "authority",
        "target_path",
        "migration_action",
    ]
)

write_csv(
    OUT / "FUNCTION_TO_FUNCTIONALITY.csv",
    function_rows,
    [
        "source",
        "symbol_type",
        "symbol",
        "candidate_layer",
        "functionality",
    ]
)

with (OUT / "FUNCTIONALITY_REGISTRY.yaml").open("w", encoding="utf-8") as f:
    # JSON is valid YAML 1.2
    json.dump(
        {
            "schema_version": "1.0",
            "status": "RAW_MECHANICAL_INVENTORY",
            "authority_default": "KX108_ONLY",
            "entries": registry,
        },
        f,
        indent=2,
        ensure_ascii=False,
    )

counts = Counter(row["candidate_layer"] for row in file_rows)

unclassified_files = [
    row["source"]
    for row in file_rows
    if row["candidate_layer"] == "UNCLASSIFIED"
]

with (OUT / "STATUS_MATRIX.md").open("w", encoding="utf-8") as f:
    f.write("# Architecture V3 — Status Matrix\n\n")
    f.write(f"Tracked files scanned: **{len(file_rows)}**\n\n")
    f.write(f"Python functions/classes scanned: **{len(function_rows)}**\n\n")
    f.write(f"FILES_UNCLASSIFIED: **{len(unclassified_files)}**\n\n")
    f.write("## Candidate layer distribution\n\n")
    f.write("| Layer | Files |\n|---|---:|\n")
    for layer, count in sorted(counts.items()):
        f.write(f"| {layer} | {count} |\n")

with (OUT / "ORPHAN_GAP_REPORT.md").open("w", encoding="utf-8") as f:
    f.write("# Orphan / Gap Report\n\n")
    f.write("Mechanical first pass only.\n\n")
    f.write(f"## FILES_UNCLASSIFIED = {len(unclassified_files)}\n\n")

    if unclassified_files:
        for p in unclassified_files:
            f.write(f"- `{p}`\n")
    else:
        f.write("No mechanically unclassified tracked files.\n")

    f.write("\n## Still requiring semantic classification\n\n")
    f.write("- functionality ownership\n")
    f.write("- runtime status\n")
    f.write("- authority\n")
    f.write("- source → test links\n")
    f.write("- source → proof links\n")
    f.write("- duplicate/canonical resolution\n")
    f.write("- target migration path\n")

for name, title in [
    ("FUNCTIONALITY_TO_RUNTIME.csv", "functionality,runtime,status\n"),
    ("FUNCTIONALITY_TO_TEST.csv", "functionality,test,status\n"),
    ("FUNCTIONALITY_TO_PROOF.csv", "functionality,proof,status\n"),
    ("CANONICAL_TARGET_MAP.csv", "source,functionality,current_layer,target_layer,target_path,action\n"),
]:
    p = OUT / name
    if not p.exists():
        p.write_text(title, encoding="utf-8")

(OUT / "FUNCTIONALITY_DEPENDENCY_GRAPH.json").write_text(
    json.dumps(
        {
            "status": "TO_BUILD_FROM_REGISTRY",
            "nodes": [],
            "edges": [],
        },
        indent=2,
    ),
    encoding="utf-8",
)

(OUT / "DUPLICATION_COLLISION_REPORT.md").write_text(
    "# Duplication / Collision Report\n\nStatus: TO_ANALYZE\n",
    encoding="utf-8",
)

(OUT / "MIGRATION_PLAN_V1.md").write_text(
    """# Migration Plan V1

Status: NOT_AUTHORIZED_YET

No move/delete/rename is allowed before semantic registry validation.

Required before migration:

- FILES_UNCLASSIFIED = 0
- MODULES_UNCLASSIFIED = 0
- FUNCTIONS_UNCLASSIFIED = 0
- FUNCTIONALITIES_WITHOUT_OWNER = 0
- ACTIVE_SOURCE_WITHOUT_TARGET = 0
- UNKNOWN_RUNTIME_STATUS = 0
- UNKNOWN_AUTHORITY = 0

Then validate vertical slices:

1. X108
2. Brody
3. GPS

Only after that create the physical migration branch.
""",
    encoding="utf-8",
)

print()
print("==========================================")
print("OBSIDIA ARCHITECTURE V3 INVENTORY COMPLETE")
print("==========================================")
print(f"Tracked files          : {len(file_rows)}")
print(f"Functions/classes      : {len(function_rows)}")
print(f"FILES_UNCLASSIFIED     : {len(unclassified_files)}")
print(f"Output                 : {OUT}")
print("==========================================")
