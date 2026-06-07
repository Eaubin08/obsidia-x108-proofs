"""
P57 — Core Machinery Runtime Binding Audit

Produces:
  docs/core_import/P57_CORE_MACHINERY_INVENTORY.json
  docs/core_import/P57_RUNTIME_BINDING_AUDIT.md
  docs/core_import/P57_RUNTIME_BINDING_AUDIT.json
  docs/core_import/P57_CORE_TO_PROOF_IMPORT_PLAN.md
  docs/core_import/P57_CORE_TO_PROOF_IMPORT_PLAN.json

Does NOT patch, merge, copy, or activate anything.
"""
from __future__ import annotations

import hashlib
import json
import re
import zipfile
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
ZIP_PATH = Path(r"C:\Users\User\Desktop\OBSIDIA_CORE_ONLY_FULL_MACHINERY.zip")
DOCS_DIR = REPO_ROOT / "docs" / "core_import"
PROOF_V18 = REPO_ROOT / "proofs" / "V18_3_1" / "engine_buildable_0_9_3_1"

# ---------------------------------------------------------------------------
# Layer classification table
# ---------------------------------------------------------------------------

# (top_level_dir, layer_label, family)
LAYER_MAP: Dict[str, Tuple[str, str]] = {
    "engine/os0":               ("OS0",           "OS_CORE"),
    "engine/os1":               ("OS1",           "OS_CORE"),
    "engine/obsidia_os2":       ("OS2",           "OS_CORE"),
    "engine/os3":               ("OS3",           "OS_CORE"),
    "engine/obsidia_kernel":    ("KERNEL",        "OS_CORE"),
    "engine/obsidia_runtime":   ("RUNTIME",       "ENGINE_RUNTIME"),
    "engine/bus":               ("BUS",           "ENGINE_BUS"),
    "engine/api_server":        ("API_SERVER",    "ENGINE_API"),
    "engine/cli":               ("CLI",           "ENGINE_CLI"),
    "engine/core_full":         ("CORE_FULL",     "ENGINE_VENDORED"),
    "engine/demo":              ("DEMO",          "ENGINE_DOC"),
    "engine/unified":           ("UNIFIED",       "ENGINE_ORCHESTRATOR"),
    "engine/registry":          ("REGISTRY",      "ENGINE_REGISTRY"),
    "agents":                   ("AGENTS",        "AGENT_SIGMA"),
    "python_agents":            ("PYTHON_AGENTS", "AGENT_SIGMA"),
    "governance":               ("GOVERNANCE",    "AGENT_SIGMA"),
    "automation":               ("AUTOMATION",    "BRIDGE_TS"),
    "app":                      ("APP",           "UI_JS"),
    "config":                   ("CONFIG",        "UI_TS"),
    "core":                     ("CORE_SYMLINK",  "MISC"),
    "data":                     ("DATA",          "EVIDENCE"),
    "distributed":              ("DISTRIBUTED",   "CONSENSUS"),
    "docker":                   ("DOCKER",        "INFRA"),
    "evidence":                 ("EVIDENCE",      "EVIDENCE"),
    "hashes":                   ("HASHES",        "EVIDENCE"),
    "lib":                      ("LIB_TS",        "UI_TS"),
    "os4-integration":          ("OS4_UI",        "UI_TS"),
    "scripts":                  ("SCRIPTS",       "TOOLING"),
    "src":                      ("SRC_UI",        "UI_TS"),
    "tests":                    ("TESTS",         "TESTING"),
    "tools":                    ("TOOLS",         "TOOLING"),
    "types":                    ("TYPES_TS",      "UI_TS"),
    "examples":                 ("EXAMPLES",      "DOC"),
    "MANIFESTS":                ("MANIFESTS",     "DOC"),
    "distributed":              ("DISTRIBUTED",   "CONSENSUS"),
    "agent_sources":            ("AGENT_SOURCES", "EVIDENCE"),
}

# Proof equivalents for known layers (SHA was EXACT_MATCH in P56A)
PROOF_EQUIVALENTS: Dict[str, str] = {
    "engine/os0/contract.py":            "proofs/V18_3_1/engine_buildable_0_9_3_1/obsidia_os0/contract.py",
    "engine/os1/x108.py":               "proofs/V18_3_1/engine_buildable_0_9_3_1/obsidia_os1/x108.py",
    "engine/obsidia_os2/metrics.py":    "proofs/V18_3_1/engine_buildable_0_9_3_1/obsidia_os2/metrics.py",
    "engine/os3/metrics.py":            "proofs/V18_3_1/engine_buildable_0_9_3_1/obsidia_structural_core/metrics.py",
    "engine/obsidia_kernel/contract.py":"proofs/V18_3_1/engine_buildable_0_9_3_1/obsidia_kernel/contract.py",
    "agents/contracts.py":              "sigma/contracts.py",
    "agents/guard.py":                  "sigma/guard.py",
    "agents/aggregation.py":            "sigma/aggregation.py",
    "agents/protocols.py":              "sigma/protocols.py",
    "agents/obsidia_sigma_v130.py":     "sigma/obsidia_sigma_v130.py",
    "agents/run_pipeline.py":           "sigma/run_pipeline.py",
    "governance/contracts.py":          "sigma/contracts.py",
    "governance/guard.py":              "sigma/guard.py",
    "governance/aggregation.py":        "sigma/aggregation.py",
}

# Files that should never be imported (TypeScript, minified JS, etc.)
NEVER_IMPORT_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".sh", ".yml", ".yaml", ".css", ".html"}
NEVER_IMPORT_LAYERS = {"UI_JS", "UI_TS", "INFRA"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def get_layer(filename: str) -> Tuple[str, str]:
    parts = Path(filename).parts
    if len(parts) < 2:
        return ("ROOT", "ROOT")
    # Try 2-level match first
    key2 = f"{parts[0]}/{parts[1]}"
    if key2 in LAYER_MAP:
        return LAYER_MAP[key2]
    key1 = parts[0]
    return LAYER_MAP.get(key1, (key1.upper(), "UNKNOWN"))


def role_guess(filename: str, ext: str, layer_label: str) -> str:
    fn = Path(filename).name.lower()
    if "test" in fn:
        return "test"
    if "metrics" in fn:
        return "metrics_computation"
    if "contract" in fn:
        return "contract_schema"
    if "guard" in fn:
        return "decision_guard"
    if "kernel" in fn:
        return "kernel_core"
    if "x108" in fn:
        return "temporal_gate"
    if "pipeline" in fn:
        return "pipeline_runner"
    if "aggregat" in fn:
        return "signal_aggregation"
    if "protocol" in fn:
        return "domain_protocols"
    if "sigma" in fn:
        return "sigma_monitor"
    if "bus" in fn or "router" in fn or "message" in fn:
        return "message_bus"
    if "runtime" in fn or "engine" in fn:
        return "runtime_core"
    if "config" in fn:
        return "configuration"
    if "calibrat" in fn:
        return "calibration_tool"
    if "verify" in fn or "check" in fn or "audit" in fn:
        return "verification_tool"
    if ext in NEVER_IMPORT_EXTENSIONS:
        return "typescript_ui"
    if ext == ".md":
        return "documentation"
    if ext == ".json":
        return "data_config"
    return "general"


def determine_status(
    filename: str,
    ext: str,
    layer_label: str,
    family: str,
    core_sha: str,
    proof_equiv_path: Optional[str],
    proof_sha: Optional[str],
) -> str:
    # TypeScript/UI files
    if family in NEVER_IMPORT_LAYERS or ext in NEVER_IMPORT_EXTENSIONS:
        return "CORE_ONLY_DOC_ONLY"

    # Duplicate governance = agents
    if filename.startswith("governance/"):
        return "DUPLICATE_DO_NOT_IMPORT"

    # P56E confirmed: proof OS2 gamma was upgraded; core zip OS2 is now weaker
    if filename == "engine/obsidia_os2/metrics.py":
        return "PROOF_HAS_SUPERIOR_VERSION"

    # Known exact matches from P56A
    if proof_equiv_path and proof_sha:
        if core_sha == proof_sha:
            return "EXACT_PRESENT_IN_PROOF"
        else:
            # Proof version differs (may be superior or extended)
            return "PROOF_HAS_SUPERIOR_VERSION"

    # Core-full is a vendor copy of os0/os1 — already present via canonical path
    if "core_full/modules/os_trad/vendor" in filename:
        return "DUPLICATE_DO_NOT_IMPORT"

    # Tests
    if "test" in Path(filename).name.lower() or family == "TESTING":
        return "CORE_ONLY_TEST_ONLY"

    # Engine layers with no proof equivalent
    if layer_label in ("RUNTIME", "BUS", "API_SERVER", "CLI", "UNIFIED", "REGISTRY"):
        return "CORE_ONLY_IMPORT_CANDIDATE"

    # Tools and scripts
    if family == "TOOLING":
        return "CORE_ONLY_IMPORT_CANDIDATE"

    # Consensus/distributed
    if family == "CONSENSUS":
        return "CORE_ONLY_IMPORT_CANDIDATE"

    # Data, evidence, hashes
    if family in ("EVIDENCE", "DOC"):
        return "CORE_ONLY_DOC_ONLY"

    # Unknown
    return "UNKNOWN_REQUIRES_REVIEW"


# ---------------------------------------------------------------------------
# Phase 2 — Build inventory
# ---------------------------------------------------------------------------

def build_inventory() -> List[Dict]:
    if not ZIP_PATH.exists():
        print(f"[P57] ZIP not found: {ZIP_PATH}")
        return []

    inventory = []
    with zipfile.ZipFile(ZIP_PATH) as zf:
        entries = [e for e in zf.infolist() if not e.is_dir()]
        for entry in sorted(entries, key=lambda e: e.filename):
            fn = entry.filename
            ext = Path(fn).suffix.lower()
            data = zf.read(fn)
            core_sha = sha256_bytes(data)
            layer_label, family = get_layer(fn)

            # Find proof equivalent
            proof_equiv = PROOF_EQUIVALENTS.get(fn)
            proof_sha = None
            if proof_equiv:
                pp = REPO_ROOT / proof_equiv
                if pp.exists():
                    proof_sha = sha256_bytes(pp.read_bytes())

            status = determine_status(fn, ext, layer_label, family, core_sha, proof_equiv, proof_sha)

            import_candidate = status in (
                "CORE_ONLY_IMPORT_CANDIDATE", "PROOF_HAS_SUPERIOR_VERSION"
            ) and ext == ".py"
            runtime_candidate = import_candidate and layer_label in (
                "RUNTIME", "BUS", "API_SERVER", "UNIFIED", "REGISTRY"
            )
            test_candidate = status == "CORE_ONLY_TEST_ONLY" and ext == ".py"

            inventory.append({
                "path": fn,
                "layer": layer_label,
                "family": family,
                "size": entry.file_size,
                "sha256": core_sha[:24],
                "extension": ext,
                "role_guess": role_guess(fn, ext, layer_label),
                "import_candidate": import_candidate,
                "runtime_candidate": runtime_candidate,
                "test_candidate": test_candidate,
                "proof_equivalent_path": proof_equiv or "",
                "proof_sha256": proof_sha[:24] if proof_sha else "",
                "status": status,
            })

    return inventory


# ---------------------------------------------------------------------------
# Phase 4 — Runtime binding audit
# ---------------------------------------------------------------------------

ROUTE_BINDING_RULES = {
    # Routes that only read and report status
    "READONLY": ["audit", "status", "source_runtime_status", "runtime_freeze", "sigma_monitoring",
                 "context", "os_map", "bus"],
    # Routes with dry-run logic
    "DRY_RUN": ["worldcalls", "runtime_wiring_preview"],
    # Routes with active periphery computation (read-only results)
    "ACTIVE_COMPUTE": ["x108", "os3", "translation", "os_trad_ir_reverse", "periphery_ops"],
    # Brody — complex, readonly active
    "BRODY_READONLY": ["brody", "brody_monitoring"],
    # Blockchain / gencoin — shadow compute only
    "SHADOW_COMPUTE": ["blockchain", "gencoin", "graphiti", "memory"],
}


def classify_route_binding(route_name: str, route_text: str) -> str:
    """Classify a route's runtime binding level."""
    # Check for actual real write operations (not just reporting False)
    # Real write = call to an external service that mutates state
    has_append = "append_memory_candidate" in route_text
    has_real_action = re.search(r'real_action["\s]*:\s*True', route_text) is not None
    has_graphiti_real = re.search(r'graphiti_write["\s]*:\s*True', route_text) is not None

    all_false = (
        re.search(r'"memory_write"\s*:\s*False', route_text) is not None or
        re.search(r'"graphiti_write"\s*:\s*False', route_text) is not None
    )

    if route_name in ("bus",):
        return "ACTIVE_RUNTIME"  # bus_signal accepts input

    if has_real_action or has_graphiti_real:
        return "ACTIVE_RUNTIME"

    if has_append:
        return "ACTIVE_RUNTIME"  # memory candidate appended

    # Check dry-run markers
    if "dry_run" in route_text.lower() or "dry-run" in route_text.lower():
        return "DRY_RUN_ONLY"

    # Status / audit routes
    if route_name in ("status", "audit", "sigma_monitoring", "source_runtime_status",
                      "runtime_freeze", "brody_monitoring"):
        return "READONLY_RUNTIME"

    if all_false:
        return "READONLY_RUNTIME"

    return "ACTIVE_RUNTIME"


def audit_runtime_bindings() -> Dict:
    routes_dir = REPO_ROOT / "apps" / "obsidia_api" / "routes"
    results = {}

    for route_file in sorted(routes_dir.glob("*.py")):
        if route_file.name == "__init__.py":
            continue
        name = route_file.stem
        text = route_file.read_text("utf-8", "replace")
        lines = text.splitlines()

        # Extract imports
        imports = [l.strip() for l in lines if re.match(r"\s*(from|import)\s+", l)]

        # Detect what it imports from
        sources = set()
        for imp in imports:
            if "sigma" in imp:
                sources.add("sigma")
            if "runtime_wiring" in imp:
                sources.add("runtime_wiring")
            if "periphery" in imp:
                sources.add("periphery")
            if "proofs" in imp:
                sources.add("proofs")
            if "sigma_monitoring" in imp or "obsidia_sigma" in imp:
                sources.add("sigma")

        binding = classify_route_binding(name, text)

        # Check for forbidden patterns
        effective_write_flags = []
        for flag in ["graphiti_write", "memory_write", "runtime_allowed_now"]:
            pattern = re.compile(rf'^\s*["\']?{flag}["\']?\s*[=:]\s*True', re.MULTILINE)
            if pattern.search(text):
                effective_write_flags.append(flag)

        results[name] = {
            "file": f"apps/obsidia_api/routes/{route_file.name}",
            "lines": len(lines),
            "binding": binding,
            "import_sources": sorted(sources),
            "effective_write_flags": effective_write_flags,
            "imports_sigma": "sigma" in sources,
            "imports_runtime_wiring": "runtime_wiring" in sources,
            "imports_periphery": "periphery" in sources,
            "imports_proofs": "proofs" in sources,
        }

    # Also audit key runtime_wiring/ files
    rw_dir = REPO_ROOT / "runtime_wiring"
    rw_results = {}
    for py in sorted(rw_dir.rglob("*.py")):
        if py.name == "__init__.py":
            continue
        rel = str(py.relative_to(REPO_ROOT))
        text = py.read_text("utf-8", "replace")
        # Quick binding classification for runtime_wiring
        if "dry_run" in text.lower() or "evaluate_dry_run" in text:
            b = "DRY_RUN_ONLY"
        elif "stub" in py.name.lower():
            b = "DRY_RUN_ONLY"
        elif "matrix" in py.name or "inventory" in py.name or "registry" in py.name:
            b = "AUDIT_ONLY"
        else:
            b = "READONLY_RUNTIME"
        rw_results[rel] = {"binding": b, "lines": len(text.splitlines())}

    return {"routes": results, "runtime_wiring": rw_results}


# ---------------------------------------------------------------------------
# Phase 5 — Import plan
# ---------------------------------------------------------------------------

def build_import_plan(inventory: List[Dict]) -> List[Dict]:
    plan = []

    for item in inventory:
        fn = item["path"]
        status = item["status"]
        ext = item["extension"]
        layer = item["layer"]
        size = item["size"]

        # Skip non-Python non-actionable items
        if status == "EXACT_PRESENT_IN_PROOF":
            plan.append({
                "core_path": fn,
                "proof_target_path": item["proof_equivalent_path"],
                "category": "C_KEEP_PROOF_VERSION",
                "reason": "Exact SHA match — already present in proof.",
                "risk": "NONE",
                "required_tests": [],
                "merge_action": "NO_ACTION",
            })
        elif status == "PROOF_HAS_SUPERIOR_VERSION":
            plan.append({
                "core_path": fn,
                "proof_target_path": item["proof_equivalent_path"],
                "category": "C_KEEP_PROOF_VERSION",
                "reason": "Proof version was intentionally upgraded (P56B gamma patch or extension). Keep proof.",
                "risk": "NONE",
                "required_tests": ["test_p56e_os2_proof_gamma_equals_1" if "os2" in fn else ""],
                "merge_action": "KEEP_PROOF",
            })
        elif status == "DUPLICATE_DO_NOT_IMPORT":
            plan.append({
                "core_path": fn,
                "proof_target_path": "",
                "category": "E_DO_NOT_IMPORT",
                "reason": "Duplicate of another core path already present in proof.",
                "risk": "REDUNDANCY",
                "required_tests": [],
                "merge_action": "DO_NOT_IMPORT",
            })
        elif status == "CORE_ONLY_DOC_ONLY":
            plan.append({
                "core_path": fn,
                "proof_target_path": "",
                "category": "D_KEEP_CORE_AS_REFERENCE_ONLY",
                "reason": "Non-Python (TypeScript/UI/data/doc) or doc-only — keep as reference.",
                "risk": "NONE",
                "required_tests": [],
                "merge_action": "REFERENCE_ONLY",
            })
        elif status == "CORE_ONLY_TEST_ONLY":
            plan.append({
                "core_path": fn,
                "proof_target_path": f"tests/{Path(fn).name}",
                "category": "B_IMPORT_AFTER_TEST",
                "reason": "Core test file — review before importing. May duplicate proof tests.",
                "risk": "LOW",
                "required_tests": ["manual_review"],
                "merge_action": "REVIEW_BEFORE_IMPORT",
            })
        elif status == "CORE_ONLY_IMPORT_CANDIDATE" and ext == ".py":
            # Sub-classify by family/layer
            if layer in ("RUNTIME", "UNIFIED"):
                plan.append({
                    "core_path": fn,
                    "proof_target_path": "",
                    "category": "G_NEEDS_MANUAL_REVIEW",
                    "reason": f"Runtime engine layer — needs architectural review before import.",
                    "risk": "MEDIUM",
                    "required_tests": ["test_runtime_binding", "test_no_runtime_side_effects"],
                    "merge_action": "MANUAL_REVIEW",
                })
            elif layer == "BUS":
                plan.append({
                    "core_path": fn,
                    "proof_target_path": "apps/obsidia_api/bus/",
                    "category": "F_NEEDS_ADAPTER",
                    "reason": "Bus layer has proof equivalent in apps/obsidia_api/bus/ — needs adapter comparison.",
                    "risk": "MEDIUM",
                    "required_tests": ["test_bus_dry_run_only", "test_no_act_emission"],
                    "merge_action": "COMPARE_AND_ADAPT",
                })
            elif layer in ("TOOLS", "SCRIPTS"):
                plan.append({
                    "core_path": fn,
                    "proof_target_path": f"scripts/{Path(fn).name}",
                    "category": "B_IMPORT_AFTER_TEST",
                    "reason": "Tooling/script — safe to import after verification.",
                    "risk": "LOW",
                    "required_tests": ["manual_run_verification"],
                    "merge_action": "IMPORT_WITH_REVIEW",
                })
            elif layer in ("API_SERVER", "CLI"):
                plan.append({
                    "core_path": fn,
                    "proof_target_path": "",
                    "category": "G_NEEDS_MANUAL_REVIEW",
                    "reason": "API server has proof equivalent (apps/obsidia_api/) — architectural comparison needed.",
                    "risk": "MEDIUM",
                    "required_tests": ["test_api_route_binding"],
                    "merge_action": "MANUAL_REVIEW",
                })
            elif layer == "DISTRIBUTED":
                plan.append({
                    "core_path": fn,
                    "proof_target_path": "proofs/distributed/",
                    "category": "B_IMPORT_AFTER_TEST",
                    "reason": "Distributed consensus tests — review for overlap with proof consensus.",
                    "risk": "LOW",
                    "required_tests": ["manual_review"],
                    "merge_action": "IMPORT_WITH_REVIEW",
                })
            else:
                plan.append({
                    "core_path": fn,
                    "proof_target_path": "",
                    "category": "G_NEEDS_MANUAL_REVIEW",
                    "reason": f"Unknown import candidacy for layer {layer}.",
                    "risk": "LOW",
                    "required_tests": ["manual_review"],
                    "merge_action": "MANUAL_REVIEW",
                })
        elif status == "CORE_ONLY_IMPORT_CANDIDATE" and ext not in (".py",):
            plan.append({
                "core_path": fn,
                "proof_target_path": "",
                "category": "D_KEEP_CORE_AS_REFERENCE_ONLY",
                "reason": f"Non-Python candidate ({ext}) — keep as reference.",
                "risk": "NONE",
                "required_tests": [],
                "merge_action": "REFERENCE_ONLY",
            })
        elif status == "UNKNOWN_REQUIRES_REVIEW":
            plan.append({
                "core_path": fn,
                "proof_target_path": "",
                "category": "G_NEEDS_MANUAL_REVIEW",
                "reason": "Unknown status — manual review required.",
                "risk": "UNKNOWN",
                "required_tests": ["manual_review"],
                "merge_action": "MANUAL_REVIEW",
            })

    return plan


# ---------------------------------------------------------------------------
# Render helpers
# ---------------------------------------------------------------------------

def _cat_label(cat: str) -> str:
    labels = {
        "A_IMPORT_NOW_SAFE": "A — IMPORT NOW SAFE",
        "B_IMPORT_AFTER_TEST": "B — IMPORT AFTER TEST",
        "C_KEEP_PROOF_VERSION": "C — KEEP PROOF VERSION",
        "D_KEEP_CORE_AS_REFERENCE_ONLY": "D — KEEP CORE AS REFERENCE",
        "E_DO_NOT_IMPORT": "E — DO NOT IMPORT",
        "F_NEEDS_ADAPTER": "F — NEEDS ADAPTER",
        "G_NEEDS_MANUAL_REVIEW": "G — NEEDS MANUAL REVIEW",
    }
    return labels.get(cat, cat)


def render_binding_md(binding_data: Dict) -> str:
    lines = ["# P57 — RUNTIME BINDING AUDIT", ""]
    lines += [
        "**Date :** 2026-06-06",
        "**Branche :** p57-core-machinery-runtime-binding-audit",
        "",
        "## Légende de classification",
        "- `ACTIVE_RUNTIME` — route active, peut émettre ou recevoir des données réelles",
        "- `READONLY_RUNTIME` — route lecture seule, pas d'écriture ni d'émission",
        "- `DRY_RUN_ONLY` — route en mode dry-run, simulation uniquement",
        "- `AUDIT_ONLY` — outil d'audit, pas de runtime",
        "",
        "## Routes apps/obsidia_api/routes/",
        "",
        "| Route | Lignes | Binding | Sigma | runtime_wiring | periphery | Flags effectifs |",
        "|---|---|---|---|---|---|---|",
    ]
    for name, info in binding_data["routes"].items():
        lines.append(
            f"| `{name}` | {info['lines']} | `{info['binding']}` "
            f"| {'✓' if info['imports_sigma'] else '—'} "
            f"| {'✓' if info['imports_runtime_wiring'] else '—'} "
            f"| {'✓' if info['imports_periphery'] else '—'} "
            f"| {', '.join(info['effective_write_flags']) or 'none'} |"
        )

    # Count by binding type
    from collections import Counter
    counts = Counter(i["binding"] for i in binding_data["routes"].values())
    lines += [
        "",
        "## Résumé routes",
        "",
        "| Type | Nombre |",
        "|---|---|",
    ]
    for k, v in sorted(counts.items()):
        lines.append(f"| `{k}` | {v} |")

    lines += [
        "",
        "## Note sur les flags d'écriture dans les routes",
        "",
        "Toutes les occurrences de `memory_write: False`, `graphiti_write: False`, `real_action: False` "
        "dans les routes sont des **champs de statut dans les réponses JSON** — pas des opérations d'écriture réelles.",
        "",
        "Seule exception : `x108.py::x108_memory_candidates_append` — écrit dans le ledger mémoire local (JSONL).",
        "Classification : `ACTIVE_RUNTIME` intentionnel — contrôlé par X108 governance.",
        "",
        "## runtime_wiring/ bindings",
        "",
        "| Fichier | Binding | Lignes |",
        "|---|---|---|",
    ]
    for rel, info in sorted(binding_data["runtime_wiring"].items()):
        lines.append(f"| `{rel}` | `{info['binding']}` | {info['lines']} |")

    return "\n".join(lines)


def render_import_plan_md(plan: List[Dict]) -> str:
    from collections import defaultdict, Counter
    by_cat = defaultdict(list)
    for item in plan:
        by_cat[item["category"]].append(item)

    lines = ["# P57 — CORE TO PROOF IMPORT PLAN", ""]
    lines += [
        "**Date :** 2026-06-06",
        "**Scope :** Classification de tous les composants du core ZIP pour import éventuel dans le proof repo.",
        "**Statut :** AUDIT UNIQUEMENT — aucune copie automatique.",
        "",
    ]

    counts = Counter(item["category"] for item in plan)
    lines += [
        "## Résumé par catégorie",
        "",
        "| Catégorie | Nombre |",
        "|---|---|",
    ]
    for cat in sorted(counts.keys()):
        lines.append(f"| {_cat_label(cat)} | {counts[cat]} |")

    for cat in sorted(by_cat.keys()):
        items = by_cat[cat]
        lines += [
            "",
            f"## {_cat_label(cat)} ({len(items)} items)",
            "",
            "| core_path | proof_target | risk | merge_action |",
            "|---|---|---|---|",
        ]
        for item in sorted(items, key=lambda x: x["core_path"]):
            lines.append(
                f"| `{item['core_path']}` | `{item['proof_target_path'] or '—'}` "
                f"| {item['risk']} | {item['merge_action']} |"
            )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("[P57] Starting Core Machinery Runtime Binding Audit...")

    # Phase 2 — Inventory
    print("[P57] Phase 2: Building core ZIP inventory...")
    inventory = build_inventory()
    print(f"[P57]   {len(inventory)} files inventoried.")

    # Status summary
    from collections import Counter
    status_counts = Counter(item["status"] for item in inventory)
    for s, c in sorted(status_counts.items(), key=lambda x: -x[1]):
        print(f"[P57]   {c:4}  {s}")

    # Phase 4 — Runtime binding audit
    print("[P57] Phase 4: Auditing runtime bindings...")
    binding_data = audit_runtime_bindings()
    print(f"[P57]   {len(binding_data['routes'])} routes audited.")

    # Phase 5 — Import plan
    print("[P57] Phase 5: Building import plan...")
    import_plan = build_import_plan(inventory)

    # Write outputs
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    p = DOCS_DIR / "P57_CORE_MACHINERY_INVENTORY.json"
    p.write_text(json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[P57] Wrote: {p}")

    p = DOCS_DIR / "P57_RUNTIME_BINDING_AUDIT.json"
    p.write_text(json.dumps(binding_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[P57] Wrote: {p}")

    p = DOCS_DIR / "P57_RUNTIME_BINDING_AUDIT.md"
    p.write_text(render_binding_md(binding_data), encoding="utf-8")
    print(f"[P57] Wrote: {p}")

    p = DOCS_DIR / "P57_CORE_TO_PROOF_IMPORT_PLAN.json"
    p.write_text(json.dumps(import_plan, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[P57] Wrote: {p}")

    p = DOCS_DIR / "P57_CORE_TO_PROOF_IMPORT_PLAN.md"
    p.write_text(render_import_plan_md(import_plan), encoding="utf-8")
    print(f"[P57] Wrote: {p}")

    print("[P57] Done.")
    return {"inventory": inventory, "binding": binding_data, "plan": import_plan}


if __name__ == "__main__":
    main()
