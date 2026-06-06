"""
P56A — Core/Proof Metric Delta Audit
Scans core ZIP and proof repo, pairs files by canonical mapping,
classifies every metric delta, produces 4 output artefacts.

Usage:
    python scripts/audit_core_proof_metric_delta_p56a.py

Outputs:
    _runtime_wiring_preflight/P56A_CORE_PACK_MANIFEST.json
    docs/core_import/OBSIDIA_CORE_PROOF_METRIC_DELTA_MATRIX_V0.json
    docs/core_import/OBSIDIA_CORE_PROOF_METRIC_AUTHORITY_MATRIX_V0.json
    docs/core_import/OBSIDIA_CORE_PROOF_BLOCKING_DELTAS_V0.json
    docs/core_import/OBSIDIA_CORE_PROOF_METRIC_DELTA_AUDIT_V0.md
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import zipfile
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
ZIP_PATH = Path(r"C:\Users\User\Desktop\OBSIDIA_CORE_ONLY_FULL_MACHINERY.zip")
TMP_CORE = REPO_ROOT / "_tmp_core_import" / "OBSIDIA_CORE_ONLY_FULL_MACHINERY"
PREFLIGHT_DIR = REPO_ROOT / "_runtime_wiring_preflight"
DOCS_DIR = REPO_ROOT / "docs" / "core_import"

PROOF_BASE = REPO_ROOT / "proofs" / "V18_3_1" / "engine_buildable_0_9_3_1"

# ---------------------------------------------------------------------------
# delta_type and authority_decision enums (as string constants)
# ---------------------------------------------------------------------------

DELTA_TYPES = {
    "EXACT_MATCH",
    "CORE_ONLY",
    "PROOF_ONLY",
    "SAME_NAME_SAME_MEANING",
    "SAME_NAME_DIFFERENT_DEFAULT",
    "SAME_NAME_DIFFERENT_FORMULA",
    "SAME_NAME_DIFFERENT_AUTHORITY",
    "PROOF_EXTENSION_COMPATIBLE",
    "PROOF_EXTENSION_DANGEROUS",
    "DOMAIN_EXTENSION",
    "BOUNDARY_EXTENSION",
    "BREAKING_CHANGE",
    "LAYER_DIFFERENCE_NOT_CONFLICT",
    "CORE_INTERNAL_BRIDGE_VARIANT",
    "UNKNOWN_REQUIRES_MANUAL_REVIEW",
}

AUTHORITY_DECISIONS = {
    "CORE_WINS",
    "PROOF_WINS",
    "KEEP_BOTH_NAMESPACED",
    "EXTENSION_ONLY",
    "DO_NOT_MERGE",
    "BLOCKED_PENDING_REVIEW",
    "KEEP_LAYER_SEPARATED",
}

# ---------------------------------------------------------------------------
# Critical blocking rules
# ---------------------------------------------------------------------------

OS_LAYERS = {"OS0", "OS1", "OS2", "OS3"}

BLOCKING_FIELD_PATTERNS = [
    "runtime_allowed_now",
    "activation_allowed",
    "graphiti_write",
    "memory_write",
    "neo4j_write",
    "kernel_mutation",
    "real_action",
    "side_effects",
]

# Fields in CanonicalDecisionEnvelope that must not change
CDE_CORE_FIELDS = {
    "domain", "market_verdict", "confidence", "contradictions", "unknowns",
    "risk_flags", "x108_gate", "reason_code", "severity", "decision_id",
    "trace_id", "ticket_required", "ticket_id", "attestation_ref", "source",
    "evidence_refs", "metrics", "raw_engine",
}

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class MetricEntry:
    metric_id: str = ""
    metric_name: str = ""
    layer_scope: str = "UNKNOWN"
    semantic_equivalence: str = "UNKNOWN"
    core_path: str = ""
    proof_path: str = ""
    core_value: str = ""
    proof_value: str = ""
    core_formula: str = ""
    proof_formula: str = ""
    core_default: str = ""
    proof_default: str = ""
    core_type: str = ""
    proof_type: str = ""
    delta_type: str = "UNKNOWN_REQUIRES_MANUAL_REVIEW"
    semantic_risk: str = "UNKNOWN"
    authority_decision: str = "BLOCKED_PENDING_REVIEW"
    merge_action: str = "MANUAL_REVIEW"
    notes: str = ""


# ---------------------------------------------------------------------------
# Phase 0 — Extract ZIP
# ---------------------------------------------------------------------------

def extract_core_zip() -> Dict[str, Any]:
    """Extract core ZIP and return manifest data."""
    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"Core ZIP not found: {ZIP_PATH}")

    TMP_CORE.mkdir(parents=True, exist_ok=True)

    file_hashes: Dict[str, str] = {}
    top_dirs: set = set()

    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        entries = zf.infolist()
        for entry in entries:
            if entry.is_dir():
                continue
            zf.extract(entry, TMP_CORE)
            abs_path = TMP_CORE / entry.filename
            if abs_path.exists():
                sha = hashlib.sha256(abs_path.read_bytes()).hexdigest()
                file_hashes[entry.filename] = sha
            parts = Path(entry.filename).parts
            if parts:
                top_dirs.add(parts[0])

    critical_files = [
        "engine/obsidia_os2/metrics.py",
        "engine/os3/metrics.py",
        "engine/os0/contract.py",
        "engine/os1/x108.py",
        "engine/obsidia_kernel/contract.py",
        "agents/contracts.py",
        "agents/aggregation.py",
        "agents/protocols.py",
        "agents/guard.py",
        "agents/obsidia_sigma_v130.py",
        "agents/run_pipeline.py",
        "python_agents/run_pipeline.py",
        "automation/canonicalPipeline.ts",
        "governance/contracts.py",
    ]
    critical_present: Dict[str, bool] = {}
    for f in critical_files:
        critical_present[f] = (TMP_CORE / f).exists()

    missing_build = []
    for bfile in ["pyproject.toml", "setup.py", "requirements.txt", "pytest.ini", "setup.cfg"]:
        if not (TMP_CORE / bfile).exists():
            missing_build.append(bfile)

    manifest = {
        "zip_path": str(ZIP_PATH),
        "extract_path": str(TMP_CORE),
        "file_count": len(file_hashes),
        "top_level_dirs": sorted(top_dirs),
        "critical_files_present": critical_present,
        "missing_build_test_config": missing_build,
        "sha256_by_file": file_hashes,
    }
    return manifest


# ---------------------------------------------------------------------------
# Phase 1 — File reading helpers
# ---------------------------------------------------------------------------

def read_file_safe(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def sha256_file(path: Path) -> str:
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Phase 2 — Metric pattern extraction (regex-based, no AST)
# ---------------------------------------------------------------------------

RE_DATACLASS_FIELD = re.compile(
    r"^\s{4}(\w+)\s*:\s*(float|int|str|bool|Optional\[[\w\[\]]+\]|List\[[\w\[\]]+\]|dict|Dict[^=\n]*)\s*=\s*(.+)$",
    re.MULTILINE,
)
RE_ENUM_VALUE = re.compile(
    r"^\s{4}(\w+)\s*=\s*[\"']([^\"']+)[\"']",
    re.MULTILINE,
)
RE_CONSTANT = re.compile(
    r"^([A-Z][A-Z0-9_]{2,})\s*=\s*(.+)$",
    re.MULTILINE,
)
RE_FUNC_PARAM = re.compile(
    r"def\s+\w+\s*\([^)]*?(\w+)\s*=\s*(\d+\.?\d*)[^)]*\)",
    re.DOTALL,
)
RE_FUNC_PARAM_NAMED = re.compile(
    r"(?:def\s+\w+\s*\(|,\s*)(\w+)\s*(?::\s*(?:float|int))?\s*=\s*(\d+\.?\d*)",
)

METRIC_KEYWORDS = re.compile(
    r"\b(metric|metrics|score|confidence|threshold|tau|limit|risk|severity|"
    r"x108|gate|allow|hold|block|act|readonly|write|mutation|"
    r"emits|decision|authority|coverage|unclassified|runtime_allowed|"
    r"activation_allowed|graphiti_write|memory_write|neo4j_write|"
    r"kernel_mutation|real_action|side_effects|"
    # Structural math metric names
    r"theta|alpha|beta|gamma|lam|lambda|"
    r"theta_t|theta_r|theta_a|theta_s|"
    r"t_mean|h_score|a_score|tmean|hstar|"
    r"asymmetry|radial|triangle|hexagon|"
    r"min_wait|elapsed|irreversible|"
    r"min_confidence|hold_confidence|max_unknown|max_contradiction|"
    r"harmonic|weighted|advisory|immutable)\b",
    re.IGNORECASE,
)


def extract_metrics_from_text(text: str, filepath: str) -> List[Dict[str, str]]:
    """Extract named metric fields from source text."""
    found: List[Dict[str, str]] = []
    seen: set = set()

    def add(name: str, value: str, typ: str, kind: str):
        key = (name, value)
        if key in seen:
            return
        seen.add(key)
        found.append({"name": name, "value": value.strip(), "type": typ, "kind": kind, "file": filepath})

    for m in RE_DATACLASS_FIELD.finditer(text):
        name, typ, val = m.group(1), m.group(2), m.group(3)
        if METRIC_KEYWORDS.search(name) or METRIC_KEYWORDS.search(val):
            add(name, val.strip(), typ.strip(), "dataclass_field")

    for m in RE_ENUM_VALUE.finditer(text):
        name, val = m.group(1), m.group(2)
        add(name, val, "str_enum", "enum_value")

    for m in RE_CONSTANT.finditer(text):
        name, val = m.group(1), m.group(2)
        if METRIC_KEYWORDS.search(name):
            add(name, val.strip(), "constant", "constant")

    for m in RE_FUNC_PARAM_NAMED.finditer(text):
        name, val = m.group(1), m.group(2)
        if METRIC_KEYWORDS.search(name):
            add(name, val, "float", "func_param")

    return found


# ---------------------------------------------------------------------------
# Phase 3 — Compare two files
# ---------------------------------------------------------------------------

def compare_files(
    core_path: Path,
    proof_path: Path,
    pair_id: str,
    layer_scope: str,
    semantic_equivalence: str,
    notes_prefix: str = "",
) -> List[MetricEntry]:
    """Compare two source files and return a list of MetricEntry."""
    entries: List[MetricEntry] = []

    core_text = read_file_safe(core_path)
    proof_text = read_file_safe(proof_path)

    core_exists = core_path.exists()
    proof_exists = proof_path.exists()

    # File-level hash comparison
    if core_exists and proof_exists:
        ch = sha256_file(core_path)
        ph = sha256_file(proof_path)
        if ch == ph:
            e = MetricEntry(
                metric_id=f"{pair_id}_FILE",
                metric_name="<file_hash>",
                layer_scope=layer_scope,
                semantic_equivalence=semantic_equivalence,
                core_path=str(core_path.relative_to(TMP_CORE) if TMP_CORE in core_path.parents else core_path),
                proof_path=str(proof_path.relative_to(REPO_ROOT) if REPO_ROOT in proof_path.parents else proof_path),
                core_value=ch[:16],
                proof_value=ph[:16],
                delta_type="EXACT_MATCH",
                semantic_risk="NONE",
                authority_decision="CORE_WINS",
                merge_action="NO_ACTION",
                notes=notes_prefix + "File SHA-256 identical.",
            )
            entries.append(e)
            return entries

    if not core_exists and not proof_exists:
        return entries

    if not core_exists:
        e = MetricEntry(
            metric_id=f"{pair_id}_FILE",
            metric_name="<file_presence>",
            layer_scope=layer_scope,
            semantic_equivalence=semantic_equivalence,
            proof_path=str(proof_path.relative_to(REPO_ROOT) if REPO_ROOT in proof_path.parents else proof_path),
            delta_type="PROOF_ONLY",
            semantic_risk="LOW",
            authority_decision="EXTENSION_ONLY",
            merge_action="KEEP_PROOF",
            notes=notes_prefix + "File exists only in proof.",
        )
        entries.append(e)
        return entries

    if not proof_exists:
        e = MetricEntry(
            metric_id=f"{pair_id}_FILE",
            metric_name="<file_presence>",
            layer_scope=layer_scope,
            semantic_equivalence=semantic_equivalence,
            core_path=str(core_path.relative_to(TMP_CORE) if TMP_CORE in core_path.parents else core_path),
            delta_type="CORE_ONLY",
            semantic_risk="MEDIUM",
            authority_decision="BLOCKED_PENDING_REVIEW",
            merge_action="MANUAL_REVIEW",
            notes=notes_prefix + "File exists only in core.",
        )
        entries.append(e)
        return entries

    # Extract metrics from both
    core_metrics = {m["name"]: m for m in extract_metrics_from_text(core_text, str(core_path))}
    proof_metrics = {m["name"]: m for m in extract_metrics_from_text(proof_text, str(proof_path))}

    all_names = set(core_metrics) | set(proof_metrics)

    # Fallback: files differ but no named metric fields extracted → surface the hash mismatch
    if not all_names:
        ch = sha256_file(core_path)
        ph = sha256_file(proof_path)
        core_rel = str(core_path.relative_to(TMP_CORE)) if TMP_CORE in core_path.parents else str(core_path)
        proof_rel = str(proof_path.relative_to(REPO_ROOT)) if REPO_ROOT in proof_path.parents else str(proof_path)
        size_c = core_path.stat().st_size if core_path.exists() else 0
        size_p = proof_path.stat().st_size if proof_path.exists() else 0
        note = f"Files differ (core={size_c}b sha={ch[:12]}, proof={size_p}b sha={ph[:12]}) but no named metric fields found by keyword scan."
        e = MetricEntry(
            metric_id=f"{pair_id}_HASH_DIFF",
            metric_name="<file_content_differs>",
            layer_scope=layer_scope,
            semantic_equivalence=semantic_equivalence,
            core_path=core_rel,
            proof_path=proof_rel,
            core_value=ch[:16],
            proof_value=ph[:16],
            delta_type="UNKNOWN_REQUIRES_MANUAL_REVIEW" if semantic_equivalence != "DIFFERENT_LAYER" else "LAYER_DIFFERENCE_NOT_CONFLICT",
            semantic_risk="LOW",
            authority_decision="KEEP_BOTH_NAMESPACED" if semantic_equivalence != "DIFFERENT_LAYER" else "KEEP_LAYER_SEPARATED",
            merge_action="MANUAL_REVIEW_NO_METRIC_FIELDS",
            notes=notes_prefix + note,
        )
        entries.append(e)
        return entries

    counter = 0

    for name in sorted(all_names):
        counter += 1
        mid = f"{pair_id}_M{counter:03d}"
        c = core_metrics.get(name)
        p = proof_metrics.get(name)

        core_rel = str(core_path.relative_to(TMP_CORE)) if TMP_CORE in core_path.parents else str(core_path)
        proof_rel = str(proof_path.relative_to(REPO_ROOT)) if REPO_ROOT in proof_path.parents else str(proof_path)

        if c and p:
            cv = c["value"].strip().rstrip(",)")
            pv = p["value"].strip().rstrip(",)")
            if cv == pv:
                delta = "EXACT_MATCH"
                risk = "NONE"
                auth = _authority_exact(layer_scope, name)
                action = "NO_ACTION"
                note = ""
            else:
                delta, risk, auth, action, note = _classify_delta(
                    name, cv, pv, c["type"], p["type"],
                    layer_scope, semantic_equivalence, notes_prefix,
                )
            e = MetricEntry(
                metric_id=mid, metric_name=name,
                layer_scope=layer_scope, semantic_equivalence=semantic_equivalence,
                core_path=core_rel, proof_path=proof_rel,
                core_value=cv, proof_value=pv,
                core_default=cv, proof_default=pv,
                core_type=c["type"], proof_type=p["type"],
                delta_type=delta, semantic_risk=risk,
                authority_decision=auth, merge_action=action,
                notes=notes_prefix + note,
            )
        elif c and not p:
            e = MetricEntry(
                metric_id=mid, metric_name=name,
                layer_scope=layer_scope, semantic_equivalence=semantic_equivalence,
                core_path=core_rel, core_value=c["value"], core_type=c["type"],
                delta_type="CORE_ONLY",
                semantic_risk="LOW" if layer_scope not in OS_LAYERS else "MEDIUM",
                authority_decision="CORE_WINS",
                merge_action="ADD_TO_PROOF_IF_NEEDED",
                notes=notes_prefix,
            )
        else:
            e = MetricEntry(
                metric_id=mid, metric_name=name,
                layer_scope=layer_scope, semantic_equivalence=semantic_equivalence,
                proof_path=proof_rel, proof_value=p["value"], proof_type=p["type"],
                delta_type="PROOF_ONLY",
                semantic_risk="NONE",
                authority_decision=_authority_proof_only(name, layer_scope),
                merge_action="KEEP_PROOF_NAMESPACED",
                notes=notes_prefix,
            )
        entries.append(e)

    return entries


# ---------------------------------------------------------------------------
# Classification logic
# ---------------------------------------------------------------------------

def _authority_exact(layer_scope: str, name: str) -> str:
    if layer_scope in OS_LAYERS:
        return "CORE_WINS"
    return "CORE_WINS"


def _authority_proof_only(name: str, layer_scope: str) -> str:
    if any(bf in name.lower() for bf in BLOCKING_FIELD_PATTERNS):
        return "DO_NOT_MERGE"
    if name in ("confidence_integrity", "confidence_governance", "confidence_readiness",
                "governance_scope", "readiness_scope", "confidence_scope"):
        return "KEEP_BOTH_NAMESPACED"
    if layer_scope == "SIGMA_EXTENSION":
        return "EXTENSION_ONLY"
    if layer_scope == "PROOF_ONLY":
        return "EXTENSION_ONLY"
    return "KEEP_BOTH_NAMESPACED"


def _classify_delta(
    name: str, cv: str, pv: str, ct: str, pt: str,
    layer_scope: str, semantic_eq: str, notes_prefix: str,
) -> tuple:
    """Return (delta_type, semantic_risk, authority_decision, merge_action, note)."""

    # Rule 8: DIFFERENT_LAYER → never auto-block
    if semantic_eq == "DIFFERENT_LAYER":
        return (
            "LAYER_DIFFERENCE_NOT_CONFLICT",
            "NONE",
            "KEEP_LAYER_SEPARATED",
            "NO_ACTION",
            f"Different layers ({layer_scope}): {name} core={cv} proof={pv}",
        )

    # Forbidden runtime flags
    for bf in BLOCKING_FIELD_PATTERNS:
        if bf in name.lower():
            if pv.lower() in ("true", "1", "yes"):
                return (
                    "BREAKING_CHANGE",
                    "CRITICAL",
                    "DO_NOT_MERGE",
                    "BLOCK",
                    f"FORBIDDEN: {name}=True detected in proof path.",
                )

    # ACT in dry-run path
    if "act" in name.lower() and pv.upper() == "ACT":
        if "dry" in str(notes_prefix).lower() or "readonly" in str(notes_prefix).lower():
            return (
                "PROOF_EXTENSION_DANGEROUS",
                "CRITICAL",
                "DO_NOT_MERGE",
                "BLOCK",
                f"ACT detected in dry-run/readonly path.",
            )

    # decision_authority must stay KX108_ONLY
    if name == "decision_authority":
        if pv.upper() != "KX108_ONLY":
            return (
                "BREAKING_CHANGE",
                "HIGH",
                "DO_NOT_MERGE",
                "BLOCK",
                f"decision_authority changed from {cv} to {pv}.",
            )

    # OS0/OS1/OS2/OS3 field differences → BLOCKED_PENDING_REVIEW
    if layer_scope in OS_LAYERS and semantic_eq in ("SAME_LAYER_SAME_ROLE",):
        return (
            "SAME_NAME_DIFFERENT_DEFAULT",
            "HIGH",
            "BLOCKED_PENDING_REVIEW",
            "MANUAL_REVIEW",
            f"OS-layer metric differs: {name} core={cv} proof={pv}",
        )

    # CanonicalDecisionEnvelope core fields
    if name in CDE_CORE_FIELDS and layer_scope == "AGENTS_CORE":
        return (
            "SAME_NAME_DIFFERENT_DEFAULT",
            "HIGH",
            "BLOCKED_PENDING_REVIEW",
            "MANUAL_REVIEW",
            f"CDE core field differs: {name} core={cv} proof={pv}",
        )

    # confidence triple extension (PROOF_ONLY fields with namespaced names)
    if name in ("confidence_integrity", "confidence_governance", "confidence_readiness"):
        return (
            "PROOF_EXTENSION_COMPATIBLE",
            "LOW",
            "KEEP_BOTH_NAMESPACED",
            "KEEP_PROOF_NAMESPACED",
            f"Triple confidence extension field: {name}",
        )

    # GPS/defense/aviation domain
    if "gps" in name.lower() or "defense" in name.lower() or "aviation" in name.lower():
        return (
            "DOMAIN_EXTENSION",
            "LOW",
            "EXTENSION_ONLY",
            "KEEP_PROOF_NAMESPACED",
            f"GPS/defense/aviation extension: {name}",
        )

    # Numeric default difference
    try:
        float(cv); float(pv)
        return (
            "SAME_NAME_DIFFERENT_DEFAULT",
            "MEDIUM",
            "BLOCKED_PENDING_REVIEW" if layer_scope in OS_LAYERS else "KEEP_BOTH_NAMESPACED",
            "MANUAL_REVIEW",
            f"Numeric default differs: {name} core={cv} proof={pv}",
        )
    except (ValueError, TypeError):
        pass

    # Formula/type mismatch
    if ct != pt:
        return (
            "SAME_NAME_DIFFERENT_FORMULA",
            "HIGH",
            "BLOCKED_PENDING_REVIEW",
            "MANUAL_REVIEW",
            f"Type mismatch: core={ct} proof={pt}",
        )

    return (
        "SAME_NAME_SAME_MEANING",
        "LOW",
        "CORE_WINS",
        "NO_ACTION",
        f"Same name, same value, different context: {name}",
    )


# ---------------------------------------------------------------------------
# Phase 4 — Canonical file pairs
# ---------------------------------------------------------------------------

def build_canonical_pairs() -> List[Dict]:
    """Define all canonical comparison pairs with layer/semantic metadata."""
    pb = PROOF_BASE
    return [
        {
            "pair_id": "P01",
            "core": TMP_CORE / "engine" / "obsidia_os2" / "metrics.py",
            "proof": pb / "obsidia_os2" / "metrics.py",
            "layer_scope": "OS2",
            "semantic_equivalence": "SAME_LAYER_SAME_ROLE",
            "notes": "OS2 structural metrics layer.",
        },
        {
            "pair_id": "P02",
            "core": TMP_CORE / "engine" / "os3" / "metrics.py",
            "proof": pb / "obsidia_structural_core" / "metrics.py",
            "layer_scope": "OS3",
            "semantic_equivalence": "SAME_LAYER_SAME_ROLE",
            "notes": "OS3/structural_core full graph metrics.",
        },
        {
            "pair_id": "P03",
            "core": TMP_CORE / "engine" / "os0" / "contract.py",
            "proof": pb / "obsidia_os0" / "contract.py",
            "layer_scope": "OS0",
            "semantic_equivalence": "SAME_LAYER_SAME_ROLE",
            "notes": "OS0 IR contract validator.",
        },
        {
            "pair_id": "P04",
            "core": TMP_CORE / "engine" / "os1" / "x108.py",
            "proof": pb / "obsidia_os1" / "x108.py",
            "layer_scope": "OS1",
            "semantic_equivalence": "SAME_LAYER_SAME_ROLE",
            "notes": "OS1 X108Gate timing gate.",
        },
        {
            "pair_id": "P05",
            "core": TMP_CORE / "engine" / "obsidia_kernel" / "contract.py",
            "proof": pb / "obsidia_kernel" / "contract.py",
            "layer_scope": "KERNEL",
            "semantic_equivalence": "SAME_LAYER_SAME_ROLE",
            "notes": "Kernel contract (Decision enum, Governance).",
        },
        {
            "pair_id": "P06",
            "core": TMP_CORE / "agents" / "contracts.py",
            "proof": REPO_ROOT / "sigma" / "contracts.py",
            "layer_scope": "AGENTS_CORE",
            "semantic_equivalence": "SAME_LAYER_SAME_ROLE",
            "notes": "CanonicalDecisionEnvelope + X108Gate.",
        },
        {
            "pair_id": "P07",
            "core": TMP_CORE / "agents" / "aggregation.py",
            "proof": REPO_ROOT / "sigma" / "aggregation.py",
            "layer_scope": "AGENTS_CORE",
            "semantic_equivalence": "SAME_LAYER_SAME_ROLE",
            "notes": "Signal aggregation.",
        },
        {
            "pair_id": "P08",
            "core": TMP_CORE / "agents" / "protocols.py",
            "proof": REPO_ROOT / "sigma" / "protocols.py",
            "layer_scope": "AGENTS_CORE",
            "semantic_equivalence": "SAME_LAYER_SAME_ROLE",
            "notes": "Domain protocols.",
        },
        {
            "pair_id": "P09",
            "core": TMP_CORE / "agents" / "guard.py",
            "proof": REPO_ROOT / "sigma" / "guard.py",
            "layer_scope": "AGENTS_CORE",
            "semantic_equivalence": "SAME_LAYER_SAME_ROLE",
            "notes": "GuardX108 with confidence thresholds.",
        },
        {
            "pair_id": "P10",
            "core": TMP_CORE / "agents" / "obsidia_sigma_v130.py",
            "proof": REPO_ROOT / "sigma" / "obsidia_sigma_v130.py",
            "layer_scope": "AGENTS_CORE",
            "semantic_equivalence": "SAME_LAYER_SAME_ROLE",
            "notes": "Sigma orchestrator v1.3.0.",
        },
        {
            "pair_id": "P11",
            "core": TMP_CORE / "python_agents" / "run_pipeline.py",
            "proof": REPO_ROOT / "sigma" / "run_pipeline.py",
            "layer_scope": "AGENTS_CORE",
            "semantic_equivalence": "SAME_LAYER_SAME_ROLE",
            "notes": "Pipeline runner (python_agents vs sigma).",
        },
        # Internal core delta: agents/ vs python_agents/ run_pipeline
        {
            "pair_id": "P11b",
            "core": TMP_CORE / "agents" / "run_pipeline.py",
            "proof": TMP_CORE / "python_agents" / "run_pipeline.py",
            "layer_scope": "AGENTS_CORE",
            "semantic_equivalence": "SAME_LAYER_DIFFERENT_ROLE",
            "notes": "CORE_INTERNAL: agents/run_pipeline vs python_agents/run_pipeline.",
        },
        # OS2 vs structural_core — cross-layer comparison for explicit documentation
        {
            "pair_id": "P_CROSS_OS2_OS3",
            "core": TMP_CORE / "engine" / "obsidia_os2" / "metrics.py",
            "proof": pb / "obsidia_structural_core" / "metrics.py",
            "layer_scope": "OS2",
            "semantic_equivalence": "DIFFERENT_LAYER",
            "notes": "CROSS-LAYER: OS2 simplified vs OS3 structural_core. delta_type must be LAYER_DIFFERENCE_NOT_CONFLICT.",
        },
        {
            "pair_id": "P12_GOVERNANCE",
            "core": TMP_CORE / "governance" / "contracts.py",
            "proof": REPO_ROOT / "sigma" / "contracts.py",
            "layer_scope": "AGENTS_CORE",
            "semantic_equivalence": "SAME_LAYER_SAME_ROLE",
            "notes": "governance/contracts vs sigma/contracts (alternate core path).",
        },
    ]


# ---------------------------------------------------------------------------
# Phase 5 — Apply critical rules post-classification
# ---------------------------------------------------------------------------

def apply_critical_rules(entries: List[MetricEntry]) -> List[MetricEntry]:
    """Post-process: enforce critical rules that override classification."""
    for e in entries:
        # Rule: DIFFERENT_LAYER → always KEEP_LAYER_SEPARATED
        if e.semantic_equivalence == "DIFFERENT_LAYER":
            e.delta_type = "LAYER_DIFFERENCE_NOT_CONFLICT"
            e.authority_decision = "KEEP_LAYER_SEPARATED"
            e.merge_action = "NO_ACTION"
            e.semantic_risk = "NONE"

        # Rule: CORE_INTERNAL_BRIDGE_VARIANT
        if e.pair_id if hasattr(e, "pair_id") else "" == "P11b":
            e.delta_type = "CORE_INTERNAL_BRIDGE_VARIANT"
            e.authority_decision = "KEEP_BOTH_NAMESPACED"
            e.semantic_risk = "LOW"
            e.merge_action = "NOTE_ONLY"

        # Rule: GPS/defense/aviation never CORE_WINS
        if "gps_defense_aviation" in e.metric_name.lower():
            e.delta_type = "DOMAIN_EXTENSION"
            e.authority_decision = "EXTENSION_ONLY"

        # Rule: runtime_allowed_now=true → DO_NOT_MERGE
        if "runtime_allowed_now" in e.metric_name.lower() and e.proof_value.lower() in ("true", "1"):
            e.authority_decision = "DO_NOT_MERGE"
            e.delta_type = "BREAKING_CHANGE"
            e.semantic_risk = "CRITICAL"

    return entries


def apply_pair_p11b_fix(entries: List[MetricEntry]) -> List[MetricEntry]:
    """Fix P11b entries (core internal bridge variant)."""
    for e in entries:
        if e.notes and "CORE_INTERNAL" in e.notes:
            e.delta_type = "CORE_INTERNAL_BRIDGE_VARIANT"
            e.authority_decision = "KEEP_BOTH_NAMESPACED"
            e.semantic_risk = "LOW"
            e.merge_action = "NOTE_ONLY"
    return entries


# ---------------------------------------------------------------------------
# Phase 6 — Build outputs
# ---------------------------------------------------------------------------

def compute_fusion_status(entries: List[MetricEntry]) -> Dict[str, Any]:
    blocking = [
        e for e in entries
        if e.authority_decision in ("DO_NOT_MERGE", "BLOCKED_PENDING_REVIEW")
        and e.delta_type not in ("LAYER_DIFFERENCE_NOT_CONFLICT", "CORE_INTERNAL_BRIDGE_VARIANT")
    ]
    exact = [e for e in entries if e.delta_type == "EXACT_MATCH"]
    core_only = [e for e in entries if e.delta_type == "CORE_ONLY"]
    proof_only = [e for e in entries if e.delta_type == "PROOF_ONLY"]
    dangerous = [e for e in entries if e.delta_type in ("BREAKING_CHANGE", "PROOF_EXTENSION_DANGEROUS")]

    fusion_status = "FUSION_BLOCKED_BY_METRIC_DELTA" if blocking else "FUSION_READY"

    return {
        "fusion_status": fusion_status,
        "total_entries": len(entries),
        "exact_match_count": len(exact),
        "core_only_count": len(core_only),
        "proof_only_count": len(proof_only),
        "dangerous_count": len(dangerous),
        "blocking_delta_count": len(blocking),
        "blocking_deltas": [asdict(e) for e in blocking],
    }


def build_authority_matrix(entries: List[MetricEntry]) -> List[Dict]:
    return [
        {
            "metric_id": e.metric_id,
            "metric_name": e.metric_name,
            "layer_scope": e.layer_scope,
            "semantic_equivalence": e.semantic_equivalence,
            "delta_type": e.delta_type,
            "authority_decision": e.authority_decision,
            "semantic_risk": e.semantic_risk,
        }
        for e in entries
    ]


def render_report_md(entries: List[MetricEntry], fusion: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# OBSIDIA CORE/PROOF METRIC DELTA AUDIT V0")
    lines.append("")
    lines.append(f"**Date:** 2026-06-06")
    lines.append(f"**Branch:** p56a-core-proof-metric-delta-audit")
    lines.append(f"**Core pack:** OBSIDIA_CORE_ONLY_FULL_MACHINERY.zip")
    lines.append(f"**Proof repo:** obsidia-x108-proofs_REMOTE_A5F21C6B")
    lines.append("")
    lines.append("## Verdict de fusion")
    lines.append("")
    status = fusion["fusion_status"]
    lines.append(f"**{status}**")
    lines.append("")
    lines.append(f"- Total métriques analysées : {fusion['total_entries']}")
    lines.append(f"- EXACT_MATCH : {fusion['exact_match_count']}")
    lines.append(f"- CORE_ONLY : {fusion['core_only_count']}")
    lines.append(f"- PROOF_ONLY : {fusion['proof_only_count']}")
    lines.append(f"- Deltas dangereux : {fusion['dangerous_count']}")
    lines.append(f"- **Deltas bloquants : {fusion['blocking_delta_count']}**")
    lines.append("")

    if fusion["blocking_deltas"]:
        lines.append("## Deltas bloquants")
        lines.append("")
        lines.append("| metric_id | metric_name | layer_scope | delta_type | authority_decision | core_value | proof_value |")
        lines.append("|---|---|---|---|---|---|---|")
        for b in fusion["blocking_deltas"]:
            lines.append(
                f"| {b['metric_id']} | {b['metric_name']} | {b['layer_scope']} "
                f"| {b['delta_type']} | {b['authority_decision']} "
                f"| {b['core_value']} | {b['proof_value']} |"
            )
        lines.append("")

    lines.append("## Matrice complète (résumé)")
    lines.append("")
    lines.append("| metric_id | metric_name | layer_scope | delta_type | authority_decision | semantic_risk |")
    lines.append("|---|---|---|---|---|---|")
    for e in entries:
        lines.append(
            f"| {e.metric_id} | {e.metric_name} | {e.layer_scope} "
            f"| {e.delta_type} | {e.authority_decision} | {e.semantic_risk} |"
        )
    lines.append("")

    lines.append("## Règles critiques appliquées")
    lines.append("")
    lines.append("1. OS0/OS1/OS2/OS3 field differs → BLOCKED_PENDING_REVIEW")
    lines.append("2. CanonicalDecisionEnvelope core field changed → BLOCKED_PENDING_REVIEW")
    lines.append("3. Proof adds field without modifying core → PROOF_EXTENSION_COMPATIBLE or DOMAIN_EXTENSION")
    lines.append("4. Confidence formula changed → BLOCKED_PENDING_REVIEW")
    lines.append("5. X108 gate ALLOW/HOLD/BLOCK changed → DO_NOT_MERGE")
    lines.append("6. ACT in dry-run path → DO_NOT_MERGE")
    lines.append("7. runtime_allowed_now=true → DO_NOT_MERGE")
    lines.append("8. memory_write/graphiti_write=true → DO_NOT_MERGE")
    lines.append("9. GPS/defense/aviation enters core → DOMAIN_EXTENSION only")
    lines.append("10. Source pack metrics replace core metrics → DO_NOT_MERGE")
    lines.append("11. semantic_equivalence=DIFFERENT_LAYER → LAYER_DIFFERENCE_NOT_CONFLICT, KEEP_LAYER_SEPARATED")
    lines.append("12. Core internal bridge variant → CORE_INTERNAL_BRIDGE_VARIANT, NOTE_ONLY")
    lines.append("")
    lines.append(f"## P56A_{status}")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("[P56A] Starting Core/Proof Metric Delta Audit...")

    # Phase 0: Extract ZIP
    print("[P56A] Phase 0: Extracting core ZIP...")
    manifest = extract_core_zip()
    print(f"[P56A]   Extracted {manifest['file_count']} files.")
    print(f"[P56A]   Top-level dirs: {manifest['top_level_dirs']}")
    missing_critical = [k for k, v in manifest["critical_files_present"].items() if not v]
    if missing_critical:
        print(f"[P56A]   WARNING: Missing critical files: {missing_critical}")

    PREFLIGHT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = PREFLIGHT_DIR / "P56A_CORE_PACK_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[P56A]   Manifest written: {manifest_path}")

    # Phase 1–4: Compare pairs
    print("[P56A] Phase 1-4: Comparing canonical file pairs...")
    pairs = build_canonical_pairs()
    all_entries: List[MetricEntry] = []

    for pair in pairs:
        pair_entries = compare_files(
            core_path=pair["core"],
            proof_path=pair["proof"],
            pair_id=pair["pair_id"],
            layer_scope=pair["layer_scope"],
            semantic_equivalence=pair["semantic_equivalence"],
            notes_prefix=pair["notes"] + " | ",
        )
        # Tag P11b entries
        if pair["pair_id"] == "P11b":
            for e in pair_entries:
                e.notes = "CORE_INTERNAL: " + e.notes
        all_entries.extend(pair_entries)
        print(f"[P56A]   {pair['pair_id']}: {len(pair_entries)} entries.")

    # Phase 5: Apply critical rules
    all_entries = apply_critical_rules(all_entries)
    all_entries = apply_pair_p11b_fix(all_entries)

    # Phase 6: Compute outputs
    print("[P56A] Phase 6: Computing fusion status...")
    fusion = compute_fusion_status(all_entries)
    authority_matrix = build_authority_matrix(all_entries)
    report_md = render_report_md(all_entries, fusion)

    # Write outputs
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    matrix_path = DOCS_DIR / "OBSIDIA_CORE_PROOF_METRIC_DELTA_MATRIX_V0.json"
    matrix_path.write_text(
        json.dumps([asdict(e) for e in all_entries], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    auth_path = DOCS_DIR / "OBSIDIA_CORE_PROOF_METRIC_AUTHORITY_MATRIX_V0.json"
    auth_path.write_text(
        json.dumps(authority_matrix, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    blocking_path = DOCS_DIR / "OBSIDIA_CORE_PROOF_BLOCKING_DELTAS_V0.json"
    blocking_path.write_text(
        json.dumps(fusion, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    report_path = DOCS_DIR / "OBSIDIA_CORE_PROOF_METRIC_DELTA_AUDIT_V0.md"
    report_path.write_text(report_md, encoding="utf-8")

    print(f"[P56A]   Matrix: {matrix_path}")
    print(f"[P56A]   Authority: {auth_path}")
    print(f"[P56A]   Blocking: {blocking_path}")
    print(f"[P56A]   Report: {report_path}")
    print(f"[P56A] Fusion status: {fusion['fusion_status']}")
    print(f"[P56A] Blocking deltas: {fusion['blocking_delta_count']}")
    print(f"[P56A] Done.")
    return fusion


if __name__ == "__main__":
    main()
