"""E11 COGNITION SHADOW MEMORY V0 — RED contract tests: an already-computed native memory retrieval snapshot -> B6.

Future production (absent at RED, created only at GREEN):
``app/integration/cognition_shadow_memory_v0.py`` exposing
``run_cognition_shadow_with_memory(text: str, memory_snapshot: Mapping) -> dict`` (JSON-serializable).

Owner decisions: D1=RETRIEVAL_SNAPSHOT_V1_ONLY, D2=B7_ON_SENS_ENTRIES_ONLY, D3=COGNITION_SHADOW_MEMORY_V0.
The consumer composes ONLY existing certified functions —
``sens_state_entries(text)`` -> ``WorkingStateRegistry.register`` ->
``native_memory_state_entries(snapshot)`` -> ``assemble_context(text, registry, memory_entries=...)`` (B6 defaults)
-> ``detect_unresolved(entry)`` for each SENS entry only — and returns::

    {"schema": "COGNITION_SHADOW_MEMORY_V0",
     "input_text": <text>,
     "memory_snapshot_ref": {"schema_version", "status", "query", "selected_items_count"},   # copied, never fixed
     "state_entries": [SENS StateEntry.to_dict(), ...],
     "memory_entries": [native memory StateEntry.to_dict(), ...],
     "context_packet": ContextPacket.to_dict(),                     # B6 packet, never ContextPacketV2
     "resolution_requests": [CognitiveResolutionRequest.to_dict(), ...],
     "boundary": {"readonly": True, "decision_authority": "KX108_ONLY", "memory_write": False,
                  "emits_act": False, "kernel_mutation": False}}

Input contract (D1): ``memory_snapshot`` must be a Mapping with
``schema_version == "OBSIDIA_NATIVE_MEMORY_RETRIEVAL_V1"``, a non-empty string ``status``, a list
``selected_items``, and no truthy ``memory_write`` / ``emits_act`` / ``kernel_mutation``; anything else
(other schema, Brody response envelope, malformed input) is rejected with ``TypeError`` or ``ValueError``.
An item without ``id`` is NOT rejected: the certified adapter turns it into an explicit ERROR entry.

No second retrieval, no response engine, no generation, no B7 propose, no B8/B10/R12/router/periphery,
no write, no network, no subprocess. Expected values come from direct calls to certified functions.
"""
from __future__ import annotations

import ast
import builtins
import copy
import hashlib
import importlib
import io
import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.cognition.b7.detector import detect_unresolved  # noqa: E402
from app.harness.state_explicit.context_assembly import assemble_context  # noqa: E402
from app.harness.state_explicit.contracts import ContextBoundError, StateStatus, canonical_json  # noqa: E402
from app.harness.state_explicit.memory_adapter import native_memory_state_entries  # noqa: E402
from app.harness.state_explicit.registry import DuplicateStateError, WorkingStateRegistry  # noqa: E402
from app.harness.state_explicit.sens_adapter import sens_state_entries  # noqa: E402

MODULE = "app.integration.cognition_shadow_memory_v0"
MODULE_PATH = ROOT / "app" / "integration" / "cognition_shadow_memory_v0.py"
RED_MESSAGE = "COGNITION_SHADOW_MEMORY_V0 runtime is absent (certified RED)"
BASELINE_COMMIT = "c3b5befe90f05aad33b57f2e383b14f2e88444e0"
SCHEMA = "OBSIDIA_NATIVE_MEMORY_RETRIEVAL_V1"
MEM_PROVENANCE = "apps.obsidia_api.brody_obsidia_native_memory"
OVERSIZED = "mot " * 20000
EXPECTED_BOUNDARY = {"readonly": True, "decision_authority": "KX108_ONLY", "memory_write": False,
                     "emits_act": False, "kernel_mutation": False}
TOP_KEYS = {"schema", "input_text", "memory_snapshot_ref", "state_entries", "memory_entries", "context_packet",
            "resolution_requests", "boundary"}
SNAPSHOT_BOUNDARY = {"readonly": True, "memory_authority": False, "memory_write": False, "canonical_write": False,
                     "auto_promotion": False, "kernel_mutation": False, "x108_mutation": False, "emits_act": False,
                     "emits_verdict": False, "allowed_to_decide": False, "allowed_to_act": False,
                     "decision_authority": "KX108_ONLY"}

TEXTS = {"closed_action": "Supprime ce fichier.", "coreference": "Qui a fait ça ?", "empty": "",
         "memory_relevant": "Que dit le kernel b6 ?"}      # tag match: native items are projected by B6


def item(native_id, rank=1, title=None, excerpt="extrait readonly", tags=("b6", "kernel")):
    out = {"rank": rank, "title": title or f"Titre {native_id}", "source": "OBSIDIA_NATIVE_MEMORY_V1",
           "path": f"docs/{native_id}.md", "tags": list(tags), "score": 10 - rank, "excerpt": excerpt,
           "source_ref": f"native:{native_id}", "readonly": True, "memory_write": False, "emits_act": False,
           "decision_authority": "KX108_ONLY"}
    if native_id is not None:
        out["id"] = native_id
    return out


def snapshot(status="MEMORY_USABLE", items=(), query="kernel b6", **extra):
    items = [dict(i) for i in items]
    snap = {"schema_version": SCHEMA, "source_type": "OBSIDIA_NATIVE_MEMORY_V1", "query": query,
            "query_normalized": query.lower(), "memory_required": status != "MEMORY_NOT_REQUIRED",
            "selected_items_count": len(items), "selected_items": items, "index_record_count": 12,
            **SNAPSHOT_BOUNDARY, "status": status,
            "material_quality": "USABLE_MATERIAL" if items else "NO_MATERIAL"}
    snap.update(extra)
    return snap


USABLE = snapshot(items=[item("nm-1", 1), item("nm-2", 2, excerpt="second extrait")])
FAIL_STATUSES = ["MEMORY_REQUIRED_EMPTY", "MEMORY_REQUIRED_NO_NATIVE_SOURCE",
                 "MEMORY_REQUIRED_INVALID_NATIVE_SOURCE", "MEMORY_REQUIRED_EMPTY_QUERY"]
SNAPSHOTS = {"usable": USABLE, "not_required": snapshot("MEMORY_NOT_REQUIRED"),
             "empty": snapshot("MEMORY_REQUIRED_EMPTY")}


def shadow():
    try:
        return importlib.import_module(MODULE)
    except ModuleNotFoundError as exc:
        if (exc.name or "").startswith(("app.integration", MODULE)):
            pytest.fail(RED_MESSAGE)
        raise


def run(text, snap):
    return shadow().run_cognition_shadow_with_memory(text, snap)


def canon(value):
    return json.loads(canonical_json(value))


def direct(text, snap):
    """Independent expectation: certified functions called directly, in contract order (D2: B7 on SENS only)."""
    entries = sens_state_entries(text)
    registry = WorkingStateRegistry()
    for entry in entries:
        registry.register(entry)
    mem = native_memory_state_entries(snap)
    packet = assemble_context(text, registry, memory_entries=mem)
    requests = [r for entry in entries for r in detect_unresolved(entry)]
    return entries, mem, packet, requests


def audit_snapshot():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / "audit").glob("*")) if p.is_file()}


CASES = [(t, s) for t in sorted(TEXTS) for s in sorted(SNAPSHOTS)]


# M1 — output shape --------------------------------------------------------------------------------

@pytest.mark.parametrize("tkey,skey", CASES)
def test_m1_json_serializable_exact_keys(tkey, skey):
    snap = SNAPSHOTS[skey]
    out = run(TEXTS[tkey], snap)
    assert set(out) == TOP_KEYS
    assert out["schema"] == "COGNITION_SHADOW_MEMORY_V0"
    assert out["input_text"] == TEXTS[tkey]
    assert out["memory_snapshot_ref"] == {"schema_version": SCHEMA, "status": snap["status"],
                                          "query": snap["query"],
                                          "selected_items_count": snap["selected_items_count"]}
    json.dumps(out, ensure_ascii=False)


# M2 — B6 equivalence; B6 packet, never ContextPacketV2 -------------------------------------------

@pytest.mark.parametrize("tkey,skey", CASES)
def test_m2_entries_and_packet_equal_direct_b6(tkey, skey):
    entries, mem, packet, _ = direct(TEXTS[tkey], SNAPSHOTS[skey])
    out = run(TEXTS[tkey], SNAPSHOTS[skey])
    assert canon(out["state_entries"]) == canon([e.to_dict() for e in entries])
    assert canon(out["memory_entries"]) == canon([e.to_dict() for e in mem])
    assert canon(out["context_packet"]) == canon(packet.to_dict())
    assert out["context_packet"]["packet_id"] == packet.packet_id
    assert out["context_packet"]["schema"] == "B6_STATE_EXPLICIT_CONTEXT_PACKET_V1"
    assert "context_items" not in out["context_packet"]          # ContextPacketV2 field


# M3 — B7 on SENS entries only (D2) ---------------------------------------------------------------

@pytest.mark.parametrize("tkey,skey", CASES)
def test_m3_requests_equal_direct_b7_on_sens_only(tkey, skey):
    _, mem, _, requests = direct(TEXTS[tkey], SNAPSHOTS[skey])
    out = run(TEXTS[tkey], SNAPSHOTS[skey])
    assert canon(out["resolution_requests"]) == canon([r.to_dict() for r in requests])
    mem_ids = {e.state_id for e in mem}
    assert not any(r.get("origin_state_id") in mem_ids for r in out["resolution_requests"])


# M4 — MEMORY_NOT_REQUIRED adds nothing -----------------------------------------------------------

@pytest.mark.parametrize("tkey", sorted(TEXTS))
def test_m4_not_required_matches_closed_shadow_v0(tkey):
    from app.integration.cognition_shadow_v0 import run_cognition_shadow
    out = run(TEXTS[tkey], SNAPSHOTS["not_required"])
    v0 = run_cognition_shadow(TEXTS[tkey])
    assert out["memory_entries"] == []
    assert canon(out["context_packet"]) == canon(v0["context_packet"])
    assert canon(out["state_entries"]) == canon(v0["state_entries"])
    assert canon(out["resolution_requests"]) == canon(v0["resolution_requests"])


# M5 — unusable retrieval stays explicit UNKNOWN ---------------------------------------------------

@pytest.mark.parametrize("status", FAIL_STATUSES)
def test_m5_unusable_status_is_unknown_entry(status):
    out = run(TEXTS["closed_action"], snapshot(status))
    (mem,) = out["memory_entries"]
    assert mem["status"] == "UNKNOWN" and mem["state_type"] == "NATIVE_MEMORY_STATUS"
    assert mem["payload"] == {"status": status}
    assert f"native_memory_status:{status}" in mem["uncertainty"]
    assert any(u["state_id"] == mem["state_id"] and u["status"] == "UNKNOWN"
               for u in out["context_packet"]["unknowns"])


# M6 — item without id stays explicit ERROR --------------------------------------------------------

def test_m6_item_without_id_is_error_entry_not_rejected():
    snap = snapshot(items=[item(None, 1), item("nm-2", 2)])
    out = run(TEXTS["closed_action"], snap)
    statuses = {e["state_type"]: e["status"] for e in out["memory_entries"]}
    assert statuses["NATIVE_MEMORY_ITEM_ERROR"] == "ERROR"
    assert statuses["NATIVE_MEMORY_ITEM"] == "KNOWN"
    assert any(u["status"] == "ERROR" for u in out["context_packet"]["unknowns"])


# M7 — provenance and identity --------------------------------------------------------------------

def test_m7_identity_and_provenance_preserved():
    out = run(TEXTS["memory_relevant"], USABLE)
    by_id = {e["state_id"]: e for e in out["memory_entries"]}
    for native_id in ("nm-1", "nm-2"):
        entry = by_id[f"native_memory:{native_id}"]
        assert entry["source_ref"] == f"native:{native_id}"
        assert MEM_PROVENANCE in entry["provenance"]
        assert entry["payload"]["id"] == native_id
    refs = set(out["context_packet"]["provenance_refs"])
    assert MEM_PROVENANCE in refs
    included = {i["state_id"] for i in out["context_packet"]["projection"]["included"]}
    assert {"native_memory:nm-1", "native_memory:nm-2"} <= included   # precondition: B6 projects both
    assert {"native:nm-1", "native:nm-2"} <= refs


def test_m7_irrelevant_items_are_recorded_omissions_not_silent_drops():
    out = run(TEXTS["coreference"], USABLE)
    assert {e["state_id"] for e in out["memory_entries"]} == {"native_memory:nm-1", "native_memory:nm-2"}
    omitted = {(o["state_id"], o["reason"]) for o in out["context_packet"]["omitted"]}
    assert {("native_memory:nm-1", "irrelevant_to_query"), ("native_memory:nm-2", "irrelevant_to_query")} <= omitted


# M8 / M9 — certified errors propagate, no fabricated packet ---------------------------------------

def test_m8_duplicate_native_id_raises():
    snap = snapshot(items=[item("nm-1", 1), item("nm-1", 2)])
    with pytest.raises(DuplicateStateError):
        direct(TEXTS["closed_action"], snap)                     # precondition from certified B6
    with pytest.raises(DuplicateStateError):
        run(TEXTS["closed_action"], snap)


def test_m9_query_bound_error_propagates():
    with pytest.raises(ContextBoundError):
        direct(OVERSIZED, USABLE)                                # precondition from certified B6
    with pytest.raises(ContextBoundError):
        run(OVERSIZED, USABLE)


# M10 — D1: only the retrieval snapshot V1 is accepted ---------------------------------------------

def _response_envelope():
    env = {k: v for k, v in USABLE.items() if k != "schema_version"}
    env.update(retrieval_status="MEMORY_USABLE", status="NATIVE_MEMORY_RESPONSE_PARTIAL",
               local_response_engine_used=False, attempted_queries=[], query_results_count=2)
    return env


REJECTED = {
    "foreign_schema": lambda: snapshot(items=[item("nm-1")], schema_version="OBSIDIA_NATIVE_MEMORY_RETRIEVAL_V2"),
    "missing_schema": lambda: {k: v for k, v in USABLE.items() if k != "schema_version"},
    "response_envelope": _response_envelope,
    "response_envelope_with_schema": lambda: {**_response_envelope(), "schema_version": SCHEMA},
    "missing_status": lambda: {k: v for k, v in USABLE.items() if k != "status"},
    "empty_status": lambda: snapshot(status=""),
    "items_not_list": lambda: snapshot(selected_items="nm-1"),
    "memory_write_true": lambda: snapshot(items=[item("nm-1")], memory_write=True),
    "emits_act_true": lambda: snapshot(items=[item("nm-1")], emits_act=True),
    "kernel_mutation_true": lambda: snapshot(items=[item("nm-1")], kernel_mutation=True),
    "not_a_mapping": lambda: [USABLE],
    "none": lambda: None,
}


@pytest.mark.parametrize("key", sorted(REJECTED))
def test_m10_non_v1_snapshots_rejected_explicitly(key):
    mod = shadow()
    with pytest.raises((TypeError, ValueError)):
        mod.run_cognition_shadow_with_memory(TEXTS["closed_action"], REJECTED[key]())


# M11 — no second retrieval, no response engine ---------------------------------------------------

def test_m11_no_second_retrieval_or_response_engine(monkeypatch):
    import apps.obsidia_api.brody_native_memory_response_adapter as resp
    import apps.obsidia_api.brody_obsidia_native_memory as native

    def trap(*_a, **_k):
        raise AssertionError("retrieval / response engine must never run inside the shadow")

    for name in ("build_native_memory_retrieval_snapshot", "load_native_memory_index", "query_native_memory"):
        monkeypatch.setattr(native, name, trap)
    for name in ("build_native_memory_response", "_load_local_response_engine"):
        monkeypatch.setattr(resp, name, trap)
    for skey in sorted(SNAPSHOTS):
        run(TEXTS["coreference"], SNAPSHOTS[skey])


# M12 — static guard ------------------------------------------------------------------------------

FORBIDDEN_PREFIXES = ("app.knowledge", "app.cognition.b7.translator", "app.cognition.b7.router", "app.cognition.b9",
                      "app.integration.cognition_shadow_v0", "app.router", "app.ir", "app.gates",
                      "app.world_model", "app.reconstruction", "app.primitives", "apps", "periphery", "scripts",
                      "obsidia_cli", "subprocess", "socket", "requests", "urllib", "http", "sqlite3", "shutil",
                      "importlib", "multiprocessing", "threading", "asyncio")
FORBIDDEN_SUBSTRINGS = ("obsidure", "binder", "kx108", "brody", "r12", "mission", "graphiti", "neo4j",
                        "openjarvis", "b8", "b10", "m42", "retrieval", "response_adapter")
FORBIDDEN_NAMES = {"propose", "CognitiveResolutionCandidate", "ContextPacketV2", "eval", "exec", "__import__",
                   "open", "build_native_memory_retrieval_snapshot", "build_native_memory_response",
                   "load_native_memory_index", "query_native_memory"}


def test_m12_static_no_forbidden_imports_or_names():
    shadow()
    assert MODULE_PATH.is_file(), RED_MESSAGE
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    modules, names = [], set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            modules.append(("." * node.level) + (node.module or ""))
            names |= {a.name for a in node.names}
        elif isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
    bad = [m for m in modules if m.startswith(".")
           or any(m == p or m.startswith(p + ".") for p in FORBIDDEN_PREFIXES)
           or any(s in m.lower() for s in FORBIDDEN_SUBSTRINGS)]
    assert not bad, bad
    assert not (names & FORBIDDEN_NAMES), sorted(names & FORBIDDEN_NAMES)


# M13 — no write / network / subprocess (bounded guards) ------------------------------------------

def test_m13_no_write_network_or_subprocess(monkeypatch):
    mod = shadow()
    real_open = builtins.open

    def guarded_open(file, mode="r", *args, **kwargs):
        if any(flag in str(mode) for flag in ("w", "a", "x", "+")):
            raise AssertionError(f"write attempted: {file!r} mode={mode!r}")
        return real_open(file, mode, *args, **kwargs)

    def forbidden(*_a, **_k):
        raise AssertionError("forbidden external effect")

    monkeypatch.setattr(builtins, "open", guarded_open)
    monkeypatch.setattr(io, "open", guarded_open)
    for name in ("open", "remove", "unlink", "rename", "replace", "mkdir", "makedirs", "write"):
        monkeypatch.setattr(os, name, forbidden)
    monkeypatch.setattr(Path, "write_text", forbidden)
    monkeypatch.setattr(Path, "write_bytes", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    before = audit_snapshot()
    for tkey, skey in CASES:
        mod.run_cognition_shadow_with_memory(TEXTS[tkey], SNAPSHOTS[skey])
    assert audit_snapshot() == before


# M14 — determinism; packet_id reflects projected material, not B6-ignored fields ------------------

@pytest.mark.parametrize("tkey,skey", CASES)
def test_m14_identical_input_identical_output(tkey, skey):
    a, b = run(TEXTS[tkey], SNAPSHOTS[skey]), run(TEXTS[tkey], SNAPSHOTS[skey])
    assert canonical_json(a) == canonical_json(b)


def test_m14_projected_material_change_changes_packet_id():
    other = snapshot(items=[item("nm-1", 1, excerpt="extrait different"), item("nm-2", 2, excerpt="second extrait")])
    t = TEXTS["memory_relevant"]
    a = run(t, USABLE)["context_packet"]
    b = run(t, other)["context_packet"]
    assert direct(t, USABLE)[2].packet_id != direct(t, other)[2].packet_id          # precondition from B6
    assert a["packet_id"] != b["packet_id"]


def test_m14_omitted_material_change_does_not_fabricate_packet_change():
    # B6 omits irrelevant items (recorded); their content is not projected, so packet_id must not move
    other = snapshot(items=[item("nm-1", 1, excerpt="extrait different"), item("nm-2", 2, excerpt="second extrait")])
    t = TEXTS["coreference"]
    assert direct(t, USABLE)[2].packet_id == direct(t, other)[2].packet_id          # precondition from B6
    assert run(t, USABLE)["context_packet"]["packet_id"] == run(t, other)["context_packet"]["packet_id"]
    assert run(t, USABLE)["memory_entries"] != run(t, other)["memory_entries"]   # entries still differ


def test_m14_b6_ignored_fields_do_not_fabricate_packet_change():
    ignored = copy.deepcopy(USABLE)
    ignored.update(index_record_count=999, material_quality="USABLE_MATERIAL", query_normalized="autre")
    for it in ignored["selected_items"]:
        it["rank"] += 10
        it["source"] = "OTHER_SOURCE_LABEL"
    t = TEXTS["memory_relevant"]
    a = run(t, USABLE)["context_packet"]
    b = run(t, ignored)["context_packet"]
    assert direct(t, ignored)[2].packet_id == direct(t, USABLE)[2].packet_id
    assert a["packet_id"] == b["packet_id"]


def test_m14_input_mutation_after_call_does_not_change_output():
    snap = copy.deepcopy(USABLE)
    out = run(TEXTS["coreference"], snap)
    frozen = canonical_json(out)
    snap["selected_items"][0]["excerpt"] = "mutated"
    snap["selected_items"].append(item("nm-9", 9))
    snap["status"] = "MEMORY_REQUIRED_EMPTY"
    assert canonical_json(out) == frozen


def test_m14_input_snapshot_not_mutated_by_call():
    snap = copy.deepcopy(USABLE)
    before = canonical_json(snap)
    run(TEXTS["coreference"], snap)
    assert canonical_json(snap) == before


# M15 — boundary, no authority fields -------------------------------------------------------------

FORBIDDEN_FIELDS = {"decision", "approval", "action", "resolved_truth", "promoted_knowledge", "selected_hypothesis",
                    "verdict", "candidate_id"}


def _keys(value):
    if isinstance(value, dict):
        for k, v in value.items():
            yield k
            yield from _keys(v)
    elif isinstance(value, list):
        for v in value:
            yield from _keys(v)


@pytest.mark.parametrize("tkey,skey", CASES)
def test_m15_boundary_exact_and_no_authority_fields(tkey, skey):
    out = run(TEXTS[tkey], SNAPSHOTS[skey])
    assert out["boundary"] == EXPECTED_BOUNDARY
    assert out["context_packet"]["boundary"]["decision_authority"] == "KX108_ONLY"
    assert out["context_packet"]["boundary"]["memory_write"] is False
    assert not (set(_keys(out)) & FORBIDDEN_FIELDS)
    for entry in out["state_entries"] + out["memory_entries"]:
        assert entry["readonly"] is True


# M16 — KNOWN memory item is a retrieved reference, not truth --------------------------------------

def test_m16_known_item_is_reference_not_truth():
    out = run(TEXTS["closed_action"], USABLE)
    for entry in out["memory_entries"]:
        assert entry["status"] == StateStatus.KNOWN.value
        assert entry["state_type"] == "NATIVE_MEMORY_ITEM"
        assert entry["payload"]["memory_write"] is False and entry["payload"]["readonly"] is True
        assert not ({"truth", "verified", "validated", "promoted", "canonical"} & set(entry["payload"]))
    assert all(r.get("origin_state_id", "").startswith("sens:") or "origin_state_id" not in r
               for r in out["resolution_requests"])


# M17 — closed Shadow V0, sealed layers and Brody untouched since baseline --------------------------

def test_m17_closed_shadow_and_sealed_sources_unchanged():
    shadow()
    paths = ["app/integration/cognition_shadow_v0.py", "app/integration/__init__.py",
             "scripts/obsidia_cognition_shadow_v0.py", "tests/integration_cognition/test_cognition_shadow_v0.py",
             "app/harness/state_explicit", "app/cognition", "app/semantic", "app/knowledge", "app/world_model",
             "app/primitives", "app/reconstruction", "app/router", "scripts/obsidia_cli.py",
             "apps/obsidia_api/brody_obsidia_native_memory.py",
             "apps/obsidia_api/brody_native_memory_response_adapter.py", "apps/obsidia_api/routes/brody.py",
             "apps/obsidia_api/brody_real_cognitive_join.py", "periphery/context"]
    proc = subprocess.run(["git", "diff", "--quiet", BASELINE_COMMIT, "--", *paths], cwd=str(ROOT),
                          capture_output=True, timeout=60, check=False, shell=False)
    assert proc.returncode == 0, proc.stdout.decode("utf-8", "replace")
