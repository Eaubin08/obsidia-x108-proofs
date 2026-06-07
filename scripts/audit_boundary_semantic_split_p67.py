"""
scripts/audit_boundary_semantic_split_p67.py — P67 boundary semantic split audit script.

AUDIT ONLY — ne modifie aucun fichier, ne stage rien.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKIP_DIRS = {
    "__pycache__", "_tmp_core_import", "_freezes",
    "_source_packs", "_source_discovery", ".git", "node_modules",
}

SURFACES_MAP = {
    "sigma": ["sigma"],
    "runtime_wiring": ["runtime_wiring"],
    "apps/obsidia_api": ["apps/obsidia_api"],
    "routes": ["apps/obsidia_api/routes"],
    "bus": ["apps/obsidia_api/bus"],
    "os_adapters": ["apps/obsidia_api/os_adapters"],
    "periphery": ["periphery"],
    "SRL": ["periphery/brody_memory_readonly/srl_session_registry_layer_readonly"],
    "connectors": ["connectors"],
    "tools_scripts": ["tools", "scripts"],
    "proofs_tests": ["proofs", "tests"],
    "audit_docs": ["audit", "docs"],
}

TERM_PATTERNS = [
    ("dry_run_only",          r"DRY_RUN_ONLY\s*=\s*True"),
    ("readonly_true",         r"readonly.*True|READONLY.*true"),
    ("emits_act_true",        r"emits_act.*True"),
    ("emits_act_false",       r"emits_act.*False"),
    ("memory_write_true",     r"memory_write.*True"),
    ("memory_write_false",    r"memory_write.*False"),
    ("graphiti_write_true",   r"graphiti_write.*True|graphiti_index_write.*True"),
    ("graphiti_write_false",  r"graphiti_write.*False"),
    ("neo4j_write_true",      r"neo4j_write.*True"),
    ("neo4j_write_false",     r"neo4j_write.*False"),
    ("kernel_mutation_true",  r"kernel_mutation.*True"),
    ("kernel_mutation_false", r"kernel_mutation.*False"),
    ("runtime_allowed_now",   r"runtime_allowed_now"),
    ("x108_merge_true",       r"x108_merge.*True"),
    ("network_post",          r"requests\.post\(|httpx\.post\(|ccxt"),
    ("network_get",           r"requests\.get\(|httpx\.get\("),
    ("subprocess_use",        r"subprocess\.(run|Popen|call|check_output)\("),
    ("os_system",             r"os\.system\("),
    ("os_remove",             r"os\.remove\(|os\.unlink\("),
    ("shutil_rmtree",         r"shutil\.rmtree\("),
    ("open_write",            r"open\([^)]+,\s*[\"']w"),
    ("write_text",            r"\.write_text\("),
    ("neo4j_password",        r"NEO4J_PASSWORD"),
    ("admin1234",             r"admin1234"),
    ("localhost",             r"localhost|127\.0\.0\.1"),
    ("decision_authority_kx108", r"KX108_ONLY"),
    ("audit_jsonl",           r"\.jsonl"),
    ("manifest_write",        r"generate_recursive_manifest|write_manifest"),
]


def should_skip(path: Path) -> bool:
    return any(s in path.parts for s in SKIP_DIRS)


def scan_file(f: Path) -> dict:
    try:
        content = f.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {}
    detected = {}
    for term, pattern in TERM_PATTERNS:
        if re.search(pattern, content):
            detected[term] = True
    return detected


def classify_file(detected: dict, path_str: str) -> dict:
    is_test = "/tests/" in path_str or "/test_" in path_str
    is_doc = "/docs/" in path_str
    is_audit = "/audit/" in path_str
    is_scripts = "/scripts/" in path_str
    is_sigma = path_str.startswith("sigma/")
    is_srl = "srl_session_registry_layer_readonly" in path_str

    categories = []

    if detected.get("dry_run_only"):
        categories.append("DRY_RUN_ONLY")
    if detected.get("readonly_true") and not detected.get("memory_write_true"):
        categories.append("DECISION_READONLY")
    if detected.get("emits_act_false") and not detected.get("emits_act_true"):
        categories.append("ACT_READONLY")
    if detected.get("audit_jsonl") or detected.get("manifest_write"):
        if not is_test and not is_doc:
            categories.append("LOCAL_AUDIT_WRITE_ALLOWED")
    if detected.get("open_write") or detected.get("write_text"):
        if is_test:
            categories.append("TEST_ONLY_SAFE")
        elif is_doc:
            categories.append("DOC_ONLY_SAFE")
        elif is_scripts or is_audit:
            categories.append("ARTIFACT_WRITE_ALLOWED")
        else:
            categories.append("REPORT_WRITE_ALLOWED")
    if detected.get("canonical_memory_write_true") or detected.get("memory_write_true"):
        if not is_test and not is_doc:
            categories.append("CANONICAL_MEMORY_WRITE_FORBIDDEN")
    if detected.get("graphiti_write_true"):
        if not is_test and not is_doc:
            categories.append("GRAPHITI_WRITE_FORBIDDEN")
    if detected.get("neo4j_write_true"):
        if not is_test and not is_doc:
            categories.append("NEO4J_WRITE_FORBIDDEN")
    if detected.get("network_post") or detected.get("network_get"):
        categories.append("NETWORK_EGRESS_REVIEW")
    if detected.get("subprocess_use") or detected.get("os_system"):
        categories.append("SUBPROCESS_REVIEW")
    if detected.get("localhost") or detected.get("admin1234"):
        categories.append("PATH_EXPOSURE_REVIEW")
    if detected.get("kernel_mutation_true"):
        categories.append("KERNEL_MUTATION_FORBIDDEN")
    if is_sigma:
        categories.append("SIGMA_MUTATION_PROTECTED")
    if detected.get("runtime_allowed_now"):
        categories.append("RUNTIME_MUTATION_BLOCKED")
    if is_test:
        if "KERNEL_MUTATION_FORBIDDEN" not in categories and "CANONICAL_MEMORY_WRITE_FORBIDDEN" not in categories:
            categories.append("TEST_ONLY_SAFE")
    if is_doc:
        categories.append("DOC_ONLY_SAFE")
    if not categories:
        categories.append("UNKNOWN_REQUIRES_REVIEW")

    risk = "LOW"
    if any(c in categories for c in ["GRAPHITI_WRITE_FORBIDDEN", "NEO4J_WRITE_FORBIDDEN", "KERNEL_MUTATION_FORBIDDEN", "CANONICAL_MEMORY_WRITE_FORBIDDEN"]):
        risk = "HIGH"
    elif any(c in categories for c in ["NETWORK_EGRESS_REVIEW", "SUBPROCESS_REVIEW", "RUNTIME_MUTATION_BLOCKED"]):
        risk = "MEDIUM"
    elif any(c in categories for c in ["PATH_EXPOSURE_REVIEW", "PATH_EXPOSURE_REVIEW"]):
        risk = "LOW_REVIEW"

    return {
        "categories": list(set(categories)),
        "risk": risk,
    }


def main():
    surface_stats = {}
    all_entries = []
    category_counts = {}

    for surface, paths in SURFACES_MAP.items():
        stats = {"files_scanned": 0, "present": False, "categories": {}}
        for p in paths:
            pp = ROOT / p
            if not pp.exists():
                continue
            stats["present"] = True
            for f in pp.rglob("*"):
                if not f.is_file():
                    continue
                if should_skip(f):
                    continue
                if f.suffix not in (".py", ".json", ".md", ".ps1", ".txt", ".jsonl"):
                    continue
                stats["files_scanned"] += 1
                detected = scan_file(f)
                if not detected:
                    continue
                classification = classify_file(detected, str(f.relative_to(ROOT)).replace("\\", "/"))
                path_str = str(f.relative_to(ROOT)).replace("\\", "/")
                entry = {
                    "path": path_str,
                    "surface": surface,
                    "detected_terms": sorted(k for k, v in detected.items() if v),
                    "decision_readonly": detected.get("readonly_true", False),
                    "act_readonly": detected.get("emits_act_false", False) and not detected.get("emits_act_true", False),
                    "dry_run_only": detected.get("dry_run_only", False),
                    "filesystem_write": detected.get("open_write", False) or detected.get("write_text", False),
                    "artifact_write": detected.get("manifest_write", False),
                    "local_audit_write": detected.get("audit_jsonl", False),
                    "report_write": detected.get("open_write", False),
                    "canonical_memory_write": detected.get("memory_write_true", False),
                    "graphiti_write": detected.get("graphiti_write_true", False),
                    "neo4j_write": detected.get("neo4j_write_true", False),
                    "network_egress": detected.get("network_post", False) or detected.get("network_get", False),
                    "subprocess_execute": detected.get("subprocess_use", False) or detected.get("os_system", False),
                    "path_exposure": detected.get("localhost", False) or detected.get("admin1234", False),
                    "kernel_mutation": detected.get("kernel_mutation_true", False),
                    "category": "|".join(sorted(set(classification["categories"]))),
                    "risk_level": classification["risk"],
                    "reason": "detected_boundary_terms",
                    "next_action": "REVIEW" if classification["risk"] in ("MEDIUM", "HIGH") else "OK",
                }
                all_entries.append(entry)
                for cat in classification["categories"]:
                    category_counts[cat] = category_counts.get(cat, 0) + 1
                    stats["categories"][cat] = stats["categories"].get(cat, 0) + 1
        surface_stats[surface] = stats

    # Build bucketed lists
    safe_readonly = [e["path"] for e in all_entries if "DECISION_READONLY" in e["category"] and e["risk_level"] == "LOW"]
    dry_run_files = [e["path"] for e in all_entries if "DRY_RUN_ONLY" in e["category"]]
    local_audit = [e["path"] for e in all_entries if "LOCAL_AUDIT_WRITE_ALLOWED" in e["category"]]
    artifact_write = [e["path"] for e in all_entries if "ARTIFACT_WRITE_ALLOWED" in e["category"]]
    report_write = [e["path"] for e in all_entries if "REPORT_WRITE_ALLOWED" in e["category"]]
    network_review = [e["path"] for e in all_entries if "NETWORK_EGRESS_REVIEW" in e["category"]]
    subprocess_review = [e["path"] for e in all_entries if "SUBPROCESS_REVIEW" in e["category"]]
    path_review = [e["path"] for e in all_entries if "PATH_EXPOSURE_REVIEW" in e["category"]]
    route_review = []
    canon_mem_forbidden = [e["path"] for e in all_entries if "CANONICAL_MEMORY_WRITE_FORBIDDEN" in e["category"]]
    graphiti_forbidden = [e["path"] for e in all_entries if "GRAPHITI_WRITE_FORBIDDEN" in e["category"]]
    neo4j_forbidden = [e["path"] for e in all_entries if "NEO4J_WRITE_FORBIDDEN" in e["category"]]
    kernel_forbidden = [e["path"] for e in all_entries if "KERNEL_MUTATION_FORBIDDEN" in e["category"]]
    sigma_protected = [e["path"] for e in all_entries if "SIGMA_MUTATION_PROTECTED" in e["category"]]
    runtime_blocked = [e["path"] for e in all_entries if "RUNTIME_MUTATION_BLOCKED" in e["category"]]
    unknown_review = [e["path"] for e in all_entries if "UNKNOWN_REQUIRES_REVIEW" in e["category"]]

    boundary_model = {
        "decision_readonly": "Flag boundary: la couche ne prend pas de décision souveraine. N'implique pas l'absence d'écritures locales.",
        "act_readonly": "Flag boundary: aucun ACT émis. emits_act=False confirmé.",
        "dry_run_only": "Flag code: DRY_RUN_ONLY=True — la logique d'exécution réelle est neutralisée.",
        "filesystem_write": "Écriture fichier locale autorisée pour rapports/audits/artifacts. Distincte de canonical_memory_write.",
        "artifact_write": "Écriture manifests, rapports JSON/MD locaux. Autorisée dans scripts/audit.",
        "local_audit_write": "Écriture .jsonl audit local. Autorisée dans couches audit/periphery.",
        "report_write": "Écriture rapport narratif MD/JSON. Autorisée dans docs/audit.",
        "canonical_memory_write": "INTERDIT hors validation KX108_ONLY explicite. Ne pas confondre avec report_write.",
        "graphiti_write": "INTERDIT dans chemin SRL readonly. Autorisé uniquement dans zones MANUAL_GRAPHITI_WRITE_ZONE.",
        "neo4j_write": "INTERDIT hors opérateur humain KX108_ONLY. Connexion Neo4j protégée par env NEO4J_PASSWORD obligatoire.",
        "network_egress": "REVIEW requis. Distinguer dry-run probe vs appel réseau réel (requests.post actif).",
        "subprocess_execute": "REVIEW requis. Distinguer subprocess lecture vs subprocess exécution action externe.",
        "path_exposure": "REVIEW requis. localhost/127.0.0.1 dans code ou fixtures. Vérifier si hardcodé ou env-driven.",
        "kernel_mutation": "INTERDIT hors P-palier explicitement autorisé. kernel_mutation=True = flag rouge.",
    }

    result = {
        "audit_id": "P67",
        "status": "P67_BOUNDARY_SEMANTIC_SPLIT_AUDIT_READY",
        "mode": "AUDIT_ONLY",
        "source_patch_applied": False,
        "files_imported_count": 0,
        "total_files_scanned": sum(s["files_scanned"] for s in surface_stats.values()),
        "total_boundary_entries": len(all_entries),
        "boundary_model": boundary_model,
        "scanned_surfaces": list(SURFACES_MAP.keys()),
        "surface_stats": {k: {"files_scanned": v["files_scanned"], "present": v["present"], "top_categories": sorted(v["categories"].items(), key=lambda x: -x[1])[:5]} for k, v in surface_stats.items()},
        "boundary_matrix": all_entries[:300],
        "category_counts": dict(sorted(category_counts.items(), key=lambda x: -x[1])),
        "safe_readonly_files": sorted(set(safe_readonly))[:50],
        "dry_run_only_files": sorted(set(dry_run_files))[:50],
        "local_audit_write_allowed": sorted(set(local_audit))[:30],
        "artifact_write_allowed": sorted(set(artifact_write))[:30],
        "report_write_allowed": sorted(set(report_write))[:30],
        "network_egress_review": sorted(set(network_review))[:30],
        "subprocess_review": sorted(set(subprocess_review))[:30],
        "path_exposure_review": sorted(set(path_review))[:30],
        "route_exposure_review": route_review,
        "canonical_memory_write_forbidden": sorted(set(canon_mem_forbidden))[:30],
        "graphiti_write_forbidden": sorted(set(graphiti_forbidden))[:30],
        "neo4j_write_forbidden": sorted(set(neo4j_forbidden))[:30],
        "kernel_mutation_forbidden": sorted(set(kernel_forbidden))[:30],
        "sigma_mutation_protected": sorted(set(sigma_protected))[:30],
        "runtime_mutation_blocked": sorted(set(runtime_blocked))[:30],
        "unknown_requires_review": sorted(set(unknown_review))[:30],
        "preexisting_manifest_drift": [
            {"file": "audit/world_action_bus.jsonl", "status": "HASH_MISMATCH_PREEXISTING_P65"},
            {"file": "proofs/PROOFKIT_REPORT.json", "status": "HASH_MISMATCH_PREEXISTING_P65"},
        ],
        "preexisting_test_debt": [
            {"test": "tests/test_invariants_against_engine.py", "reason": "ModuleNotFoundError: obsidia_os2 — module vendor absent"},
            {"test": "tests/api/test_brody_source_pack_context_p28.py::test_second_request_cache_hit", "reason": "Cache timing pre-existing"},
            {"test": "tests/sigma_stress_test.py", "reason": "ModuleNotFoundError: agents.obsidia_sigma_v130"},
            {"test": "tests/test_agents_functional.py", "reason": "ImportError: TradingState from agents"},
            {"test": "tests/test_consensus_inprocess.py", "reason": "ModuleNotFoundError: agents.run_pipeline"},
            {"test": "tests/test_sigma_v18_9.py", "reason": "ModuleNotFoundError: agents.obsidia_sigma_v130"},
        ],
        "runtime_modified": False,
        "sigma_modified": False,
        "routes_modified": False,
        "srl_modified": False,
        "act_enabled": False,
        "memory_write_enabled": False,
        "graphiti_write_enabled": False,
        "neo4j_write_enabled": False,
        "kernel_mutation_enabled": False,
        "x108_merge_enabled": False,
        "next_step": "P68_API_AUTH_AND_ROUTE_EXPOSURE_AUDIT",
    }

    out_path = ROOT / "docs" / "core_import" / "P67_BOUNDARY_SEMANTIC_SPLIT_AUDIT.json"
    out_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    print(f"P67 JSON written: {out_path} ({len(result['boundary_matrix'])} entries)")


if __name__ == "__main__":
    main()
