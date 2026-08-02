"""
Readonly configuration registry for the 52 OBSIDIA AI agent configurations.

Source: periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/
        10_AGENTS_52/agents_52.registry.json

ARCHITECTURE: JSON_FIRST_READONLY_CONFIGURATION_REGISTRY
AUTHORITY:    NON_SOVEREIGN — KX108_ONLY decision authority.

All entries are non-decision and readonly. No agent is invoked, no model is
called, no memory is written. Semantic validation requires a separate
human-approved step (NEEDS_HUMAN_VALIDATION preserved for all 52 entries).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

_REGISTRY_REL_PARTS = (
    "periphery",
    "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1",
    "10_AGENTS_52",
    "agents_52.registry.json",
)

# Batch 001 — explicit mapping from ART118.
# Source: 118_AGENTS52_FIRST_HUMAN_VALIDATION_BATCH_PROPOSAL_REV2D.csv
# Never derive ROW_IDs from JSON position, ordinal, name order, or list index.
_BATCH001_TAG = "AGENTS52_BATCH001"
_BATCH001_STATUS = "DOCUMENTED_AGENT_CONFIG_REGISTERED_READONLY"
_OTHER_STATUS = "DOCUMENTED_SOURCE_ONLY"

# ART118 explicit mapping: source_row_id → agent name ("name" field in JSON)
_BATCH001_ROW_MAP: dict[str, str] = {
    "1811": "SECURITY_FIREWALL_ARCHITECT",
    "1812": "POLICY_FIREWALL_AGENT",
    "1813": "RUNTIME_ATTESTATION_AGENT",
    "1814": "SUPPLY_CHAIN_GUARD",
    "1815": "SECRET_GUARD",
}
_BATCH001_AGENT_TO_ROW: dict[str, str] = {v: k for k, v in _BATCH001_ROW_MAP.items()}

# Batch 002 — explicit mapping from ART150.
# Source: 150_AGENTS52_BATCH002_HUMAN_VALIDATION_PROPOSAL_REV2D.csv
# Family: Frise / Arbres / Monde humain
_BATCH002_TAG = "AGENTS52_BATCH002"
_BATCH002_STATUS = "DOCUMENTED_AGENT_CONFIG_REGISTERED_READONLY"

_BATCH002_ROW_MAP: dict[str, str] = {
    "1821": "FRISE_HUMAINE",
    "1822": "CARTOGRAPHE_34_ARBRES",
    "1823": "HUMAN_HISTORY_MAPPER",
    "1824": "CALIBRATION_PROCEDURALE",
    "1825": "NUAGE_POINTS",
}
_BATCH002_AGENT_TO_ROW: dict[str, str] = {v: k for k, v in _BATCH002_ROW_MAP.items()}

# Batch 003 — explicit mapping from ART181 (campaign selection).
# Source: 181_AGENTS52_BATCH003_SELECTION_REV2D.json
# Family: Atlas Obsidia
# Note: row 1829 (CARTOGRAPHE_LOIS_PROTOCOLES) carries BRODY provenance — included per Batch 002 precedent.
_BATCH003_TAG = "AGENTS52_BATCH003"
_BATCH003_STATUS = "DOCUMENTED_AGENT_CONFIG_REGISTERED_READONLY"

_BATCH003_ROW_MAP: dict[str, str] = {
    "1826": "GRAND_CARTOGRAPHE_OBSIDIA",
    "1827": "ONTOLOGUE_OBSIDIA",
    "1828": "CARTOGRAPHE_COUCHES",
    "1829": "CARTOGRAPHE_LOIS_PROTOCOLES",
    "1830": "CARTOGRAPHE_FORMULES",
    "1831": "CARTOGRAPHE_DOMAINES_TERRAIN",
    "1832": "CARTOGRAPHE_AGI_VISION_HAUTE",
    "1833": "COLLISION_DETECTOR",
}
_BATCH003_AGENT_TO_ROW: dict[str, str] = {v: k for k, v in _BATCH003_ROW_MAP.items()}


@dataclass(frozen=True)
class AgentConfigEntry:
    """Immutable configuration entry for an OBSIDIA AI agent. Never executable."""

    # Core identity
    agent_id: str
    name: str
    family: str
    role: str
    input_contract: str
    output_contract: str
    non_decision: bool
    boundary: str
    deployment: str
    validation_status: str

    # Provenance — relative paths only; no absolute machine paths exposed
    source_path: str
    source_reference: str
    source_registry_sha256: str
    source_row_id: str | None

    # Compilation
    compilation_batch: str | None
    compilation_status: str

    # Authority — always hardcoded; never sourced from JSON input
    authority: str = "NON_SOVEREIGN"
    readonly: bool = True
    can_decide: bool = False
    can_act: bool = False
    emits_act: bool = False
    memory_write: bool = False
    graphiti_write: bool = False
    neo4j_write: bool = False


def _repo_root() -> Path:
    # __file__ = periphery/agents_obsidia_config_registry.py
    # .parent   = periphery/
    # .parent   = repo root
    return Path(__file__).resolve().parent.parent


def _registry_path() -> Path:
    return _repo_root().joinpath(*_REGISTRY_REL_PARTS)


def _rel_path() -> str:
    return "/".join(_REGISTRY_REL_PARTS)


# Module-level cache — loaded once, never mutated after construction.
_CACHE: tuple[AgentConfigEntry, ...] | None = None
_CACHE_SHA: str = ""


def _build_entry(raw: dict, sha256: str) -> AgentConfigEntry:
    name: str = str(raw.get("name") or raw.get("nom") or "")
    entry_id: str = str(raw.get("id", ""))
    rel = _rel_path()

    # Authority violation check.
    # If JSON asserts decision or action capability, classify AUTHORITY_REVIEW_REQUIRED.
    # Do not silently normalise a conflicting entry.
    authority_violation = (
        bool(raw.get("can_decide", False))
        or bool(raw.get("can_act", False))
        or bool(raw.get("emits_act", False))
        or bool(raw.get("memory_write", False))
        or not bool(raw.get("non_decision", True))
    )

    if authority_violation:
        c_batch: str | None = None
        row_id: str | None = None
        c_status = "AUTHORITY_REVIEW_REQUIRED"
    elif name in _BATCH001_AGENT_TO_ROW:
        row_id = _BATCH001_AGENT_TO_ROW[name]
        c_batch = _BATCH001_TAG
        c_status = _BATCH001_STATUS
    elif name in _BATCH002_AGENT_TO_ROW:
        row_id = _BATCH002_AGENT_TO_ROW[name]
        c_batch = _BATCH002_TAG
        c_status = _BATCH002_STATUS
    elif name in _BATCH003_AGENT_TO_ROW:
        row_id = _BATCH003_AGENT_TO_ROW[name]
        c_batch = _BATCH003_TAG
        c_status = _BATCH003_STATUS
    else:
        row_id = None
        c_batch = None
        c_status = _OTHER_STATUS

    return AgentConfigEntry(
        agent_id=name,
        name=name,
        family=str(raw.get("family") or raw.get("famille") or ""),
        role=str(raw.get("role") or ""),
        input_contract=str(raw.get("input") or ""),
        output_contract=str(raw.get("output") or raw.get("sortie_principale") or ""),
        non_decision=True,  # hardcoded; JSON confirmed True for all 52 entries
        boundary=str(raw.get("boundary") or ""),
        deployment=str(raw.get("deployment") or raw.get("deploiement") or ""),
        validation_status=str(raw.get("status") or "NEEDS_HUMAN_VALIDATION"),
        source_path=rel,
        source_reference=f"{rel}#id={entry_id}",
        source_registry_sha256=sha256,
        source_row_id=row_id,
        compilation_batch=c_batch,
        compilation_status=c_status,
        # Authority — always hardcoded regardless of JSON content
        authority="NON_SOVEREIGN",
        readonly=True,
        can_decide=False,
        can_act=False,
        emits_act=False,
        memory_write=False,
        graphiti_write=False,
        neo4j_write=False,
    )


def load_registry() -> tuple[AgentConfigEntry, ...]:
    """Load agents_52.registry.json; return immutable tuple. Cached after first call."""
    global _CACHE, _CACHE_SHA
    if _CACHE is not None:
        return _CACHE
    path = _registry_path()
    raw_bytes = path.read_bytes()
    sha256 = hashlib.sha256(raw_bytes).hexdigest()
    raw_list: list[dict] = json.loads(raw_bytes)
    _CACHE_SHA = sha256
    _CACHE = tuple(_build_entry(e, sha256) for e in raw_list)
    return _CACHE


def validate_registry() -> dict:
    """Validate registry integrity; return diagnostic summary."""
    entries = load_registry()
    batch1 = [e for e in entries if e.compilation_batch == _BATCH001_TAG]
    batch2 = [e for e in entries if e.compilation_batch == _BATCH002_TAG]
    batch3 = [e for e in entries if e.compilation_batch == _BATCH003_TAG]
    technically_compiled = batch1 + batch2 + batch3
    return {
        "entry_count": len(entries),
        "unique_ids": len({e.agent_id for e in entries}),
        "all_non_decision": all(e.non_decision for e in entries),
        "all_readonly": all(e.readonly for e in entries),
        "all_no_act": all(not e.can_act for e in entries),
        "all_no_decide": all(not e.can_decide for e in entries),
        "all_no_emits_act": all(not e.emits_act for e in entries),
        "all_no_memory_write": all(not e.memory_write for e in entries),
        "all_no_graphiti_write": all(not e.graphiti_write for e in entries),
        "all_no_neo4j_write": all(not e.neo4j_write for e in entries),
        "batch001_count": len(batch1),
        "batch002_count": len(batch2),
        "batch003_count": len(batch3),
        "technically_compiled_readonly_count": len(technically_compiled),
        "documented_source_only_count": len(entries) - len(technically_compiled),
        "other_count": len(entries) - len(batch1),
        "validation_status_uniform": all(
            e.validation_status == "NEEDS_HUMAN_VALIDATION" for e in entries
        ),
        "authority_uniform": all(e.authority == "NON_SOVEREIGN" for e in entries),
        "source_sha256": _CACHE_SHA,
    }


def get_agent_config(agent_id: str) -> AgentConfigEntry:
    """Return AgentConfigEntry for agent_id. Raises KeyError if unknown."""
    for e in load_registry():
        if e.agent_id == agent_id:
            return e
    raise KeyError(f"UNKNOWN_AGENT_CONFIG:{agent_id}")


def list_agent_configs() -> list[str]:
    """Return sorted list of all agent_id strings."""
    return sorted(e.agent_id for e in load_registry())


def list_agents_by_family(family: str) -> list[AgentConfigEntry]:
    """Return entries matching family, sorted by agent_id."""
    return sorted(
        (e for e in load_registry() if e.family == family),
        key=lambda e: e.agent_id,
    )


def get_registry_provenance() -> dict:
    """Return provenance metadata: relative source path, SHA256, counts, batch info."""
    load_registry()
    entries = _CACHE or ()
    batch1 = [e for e in entries if e.compilation_batch == _BATCH001_TAG]
    batch2 = [e for e in entries if e.compilation_batch == _BATCH002_TAG]
    batch3 = [e for e in entries if e.compilation_batch == _BATCH003_TAG]
    return {
        "source_path": _rel_path(),
        "source_sha256": _CACHE_SHA,
        "entry_count": len(entries),
        "readonly": True,
        "authority": "NON_SOVEREIGN",
        "can_decide": False,
        "can_act": False,
        "emits_act": False,
        "memory_write": False,
        "batch_compiled": _BATCH001_TAG,
        "batch_compiled_count": len(batch1),
        "batch_compiled_agent_ids": sorted(e.agent_id for e in batch1),
        "batch002_compiled": _BATCH002_TAG,
        "batch002_compiled_count": len(batch2),
        "batch002_compiled_agent_ids": sorted(e.agent_id for e in batch2),
        "batch003_compiled": _BATCH003_TAG,
        "batch003_compiled_count": len(batch3),
        "batch003_compiled_agent_ids": sorted(e.agent_id for e in batch3),
        "technically_compiled_readonly_count": len(batch1) + len(batch2) + len(batch3),
    }
