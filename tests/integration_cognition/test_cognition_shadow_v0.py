"""COGNITION SHADOW V0 — RED contract tests for the first real SENS -> B6 -> B7 integration.

Future production (absent at RED, created only at GREEN):
- ``app/integration/cognition_shadow_v0.py`` exposing
  ``run_cognition_shadow(text: str) -> dict`` (JSON-serializable);
- ``scripts/obsidia_cognition_shadow_v0.py "<texte>"`` printing that dict as JSON on stdout.

Contract fixed by these tests (owner choice D3; D1 router deferred, D2 R12 separate, D4 no gateway log):
the shadow composes ONLY existing certified functions —
``sens_state_entries(text)`` -> ``WorkingStateRegistry.register`` -> ``assemble_context(text, registry)``
(B6 defaults) -> ``detect_unresolved(entry)`` for each entry — and returns::

    {"schema": "COGNITION_SHADOW_V0",
     "input_text": <text>,
     "state_entries": [StateEntry.to_dict(), ...],                 # exact, in SENS order
     "context_packet": ContextPacket.to_dict(),                     # exact
     "resolution_requests": [CognitiveResolutionRequest.to_dict(), ...],   # exact, entry order then B7 order
     "boundary": {"readonly": True, "decision_authority": "KX108_ONLY", "memory_write": False,
                  "emits_act": False, "kernel_mutation": False}}

No B7 ``propose``, no CognitiveResolutionCandidate, no B8/B10, no router, no Brody chat, no Obsidure,
no R12, no write, no network, no subprocess. Expected values are computed by calling the certified
functions directly, never through the shadow.
"""
from __future__ import annotations

import ast
import builtins
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
from app.harness.state_explicit.contracts import StateStatus, canonical_json  # noqa: E402
from app.harness.state_explicit.registry import WorkingStateRegistry  # noqa: E402
from app.harness.state_explicit.sens_adapter import sens_state_entries  # noqa: E402

MODULE = "app.integration.cognition_shadow_v0"
MODULE_PATH = ROOT / "app" / "integration" / "cognition_shadow_v0.py"
SCRIPT_PATH = ROOT / "scripts" / "obsidia_cognition_shadow_v0.py"
RED_MESSAGE = "COGNITION_SHADOW_V0 runtime is absent (certified RED)"
BASELINE_COMMIT = "a268ae460762144f1dae058858ddd5ad045000bc"

TEXTS = {
    "closed_action": "Supprime ce fichier.",
    "missing": "Il le lui a donné.",
    "coreference": "Qui a fait ça ?",
    "coordination": "La porte est ouverte et fermée.",
    "empty": "",
}
OVERSIZED = "mot " * 20000          # naturally exceeds the B6 payload bound -> SENS_FRAME_ERROR
EXPECTED_BOUNDARY = {"readonly": True, "decision_authority": "KX108_ONLY", "memory_write": False,
                     "emits_act": False, "kernel_mutation": False}


def shadow():
    try:
        return importlib.import_module(MODULE)
    except ModuleNotFoundError as exc:
        if (exc.name or "").startswith(("app.integration", MODULE)):
            pytest.fail(RED_MESSAGE)
        raise


def run(text):
    return shadow().run_cognition_shadow(text)


def canon(value):
    return json.loads(canonical_json(value))


def direct(text):
    """Independent expectation: the certified functions called directly, in the contract order."""
    entries = sens_state_entries(text)
    registry = WorkingStateRegistry()
    for entry in entries:
        registry.register(entry)
    packet = assemble_context(text, registry)
    requests = [request for entry in entries for request in detect_unresolved(entry)]
    return entries, packet, requests


def audit_snapshot():
    out = {}
    for path in sorted((ROOT / "audit").glob("*")):
        if path.is_file():
            out[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return out


# ---------------------------------------------------------------------------
# Output shape
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("key", sorted(TEXTS))
def test_output_is_json_serializable_with_exact_top_level_keys(key):
    out = run(TEXTS[key])
    assert set(out) == {"schema", "input_text", "state_entries", "context_packet", "resolution_requests",
                        "boundary"}
    assert out["schema"] == "COGNITION_SHADOW_V0"
    assert out["input_text"] == TEXTS[key]
    json.dumps(out, ensure_ascii=False)


# ---------------------------------------------------------------------------
# R1 — direct B6 equivalence
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("key", sorted(TEXTS))
def test_r1_state_entries_equal_direct_sens_adapter(key):
    entries, _, _ = direct(TEXTS[key])
    assert canon(run(TEXTS[key])["state_entries"]) == canon([e.to_dict() for e in entries])


@pytest.mark.parametrize("key", sorted(TEXTS))
def test_r1_context_packet_equals_direct_b6_assembly(key):
    _, packet, _ = direct(TEXTS[key])
    out = run(TEXTS[key])["context_packet"]
    assert canon(out) == canon(packet.to_dict())
    assert out["packet_id"] == packet.packet_id
    assert out["schema"] == "B6_STATE_EXPLICIT_CONTEXT_PACKET_V1"


# ---------------------------------------------------------------------------
# R2 — B7 equivalence (canonical contents, not counts)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("key", sorted(TEXTS))
def test_r2_resolution_requests_equal_direct_detect_unresolved(key):
    _, _, requests = direct(TEXTS[key])
    out = run(TEXTS[key])["resolution_requests"]
    assert canon(out) == canon([r.to_dict() for r in requests])
    assert [r["request_id"] for r in out] == [r.request_id for r in requests]


def test_r2_coreference_request_kind_preserved():
    kinds = [r["unresolved_kind"] for r in run(TEXTS["coreference"])["resolution_requests"]]
    assert "COREFERENCE" in kinds


def test_r2_closed_frame_produces_no_request():
    out = run(TEXTS["closed_action"])
    assert out["state_entries"][0]["status"] == StateStatus.KNOWN.value
    assert out["resolution_requests"] == []


# ---------------------------------------------------------------------------
# R3 — open meaning preserved
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("key", ["missing", "coreference", "coordination", "empty"])
def test_r3_open_items_kept_in_entries_unknowns_and_requests(key):
    entries, packet, _ = direct(TEXTS[key])
    out = run(TEXTS[key])
    entry = out["state_entries"][0]
    payload = entry["payload"]
    assert entry["status"] == "OPEN"
    for field in ("missing", "ambiguities", "unresolved_references", "contradictions"):
        assert payload[field] == entries[0].payload[field]
    assert payload["semantic_closure"]["closed"] is False or payload["frame_closure"] is False
    assert canon(out["context_packet"]["unknowns"]) == canon(packet.to_dict()["unknowns"])
    assert any(u["state_id"] == entry["state_id"] and u["status"] == "OPEN"
               for u in out["context_packet"]["unknowns"])
    assert out["resolution_requests"], "open meaning must yield at least one unresolved request"


def test_r3_requested_action_never_marked_authorized():
    payload = run(TEXTS["closed_action"])["state_entries"][0]["payload"]
    assert payload["requested_is_authorized"] is False


def test_r3_omission_limits_follow_b6():
    _, packet, _ = direct(TEXTS["missing"])
    out = run(TEXTS["missing"])["context_packet"]
    assert canon(out["omitted"]) == canon(packet.to_dict()["omitted"])
    assert canon(out["projection"]) == canon(packet.to_dict()["projection"])


# ---------------------------------------------------------------------------
# R4 — error propagation; empty input follows certified SENS/B6 behavior
# ---------------------------------------------------------------------------

def _inject_sens_parse_failure(monkeypatch):
    """Fault injection upstream of the tested path: the certified SENS adapter turns a parser exception into
    an explicit SENS_FRAME_ERROR entry (sens_adapter.py). Natural ERROR inputs (oversized or lone-surrogate
    text) also make the certified B6 assembly raise, so they cannot exercise a retained ERROR entry."""
    import app.harness.state_explicit.sens_adapter as sens_adapter

    def failing_parse(_text):
        raise RuntimeError("injected SENS parse failure")

    monkeypatch.setattr(sens_adapter, "parse_utterance", failing_parse)


def test_r4_sens_error_entry_retained(monkeypatch):
    _inject_sens_parse_failure(monkeypatch)
    text = TEXTS["missing"]
    entries, packet, _ = direct(text)
    assert entries[0].status == StateStatus.ERROR            # precondition from certified B6
    out = run(text)
    assert out["state_entries"][0]["status"] == "ERROR"
    assert out["state_entries"][0]["state_type"] == "SENS_FRAME_ERROR"
    assert canon(out["context_packet"]) == canon(packet.to_dict())
    assert any(u["status"] == "ERROR" for u in out["context_packet"]["unknowns"])
    assert out["resolution_requests"] == []                   # B7: operational failure, not a cognitive problem


def test_r4_b6_bound_error_propagates_not_fabricated():
    # Certified B6 behavior: assemble_context raises ContextBoundError for a query over its bound.
    from app.harness.state_explicit.contracts import ContextBoundError

    with pytest.raises(ContextBoundError):
        direct(OVERSIZED)                                     # precondition from certified B6
    with pytest.raises(ContextBoundError):
        run(OVERSIZED)                                        # the shadow never fabricates a packet


def test_r4_empty_input_is_not_rejected():
    out = run("")
    assert out["state_entries"][0]["status"] == sens_state_entries("")[0].status.value
    assert out["context_packet"]["packet_id"].startswith("b6ctx_")


# ---------------------------------------------------------------------------
# R5 — determinism
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("key", sorted(TEXTS))
def test_r5_identical_input_identical_output(key):
    a, b = run(TEXTS[key]), run(TEXTS[key])
    assert canonical_json(a) == canonical_json(b)
    assert a["context_packet"]["packet_id"] == b["context_packet"]["packet_id"]


def test_r5_different_inputs_different_packets():
    assert run(TEXTS["missing"])["context_packet"]["packet_id"] != \
        run(TEXTS["coreference"])["context_packet"]["packet_id"]


# ---------------------------------------------------------------------------
# R6 — no forbidden authority (static + dynamic guard on B7 propose)
# ---------------------------------------------------------------------------

FORBIDDEN_PREFIXES = ("app.knowledge", "app.cognition.b7.translator", "app.cognition.b7.router", "app.cognition.b9",
                      "app.router", "app.ir", "app.gates", "app.world_model", "app.reconstruction",
                      "app.primitives", "periphery", "apps", "scripts", "obsidia_cli", "subprocess", "socket",
                      "requests", "urllib", "http", "sqlite3", "shutil", "importlib", "multiprocessing",
                      "threading", "asyncio")
FORBIDDEN_SUBSTRINGS = ("obsidure", "binder", "kx108", "brody", "r12", "mission", "graphiti", "neo4j", "openjarvis")
FORBIDDEN_NAMES = {"propose", "CognitiveResolutionCandidate", "eval", "exec", "__import__", "open"}


def _imports_and_names(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
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
    return modules, names


@pytest.mark.parametrize("which", ["module", "script"])
def test_r6_static_no_forbidden_imports_or_calls(which):
    shadow()                                   # RED attribution when the runtime is absent
    path = {"module": MODULE_PATH, "script": SCRIPT_PATH}[which]
    assert path.is_file(), RED_MESSAGE
    modules, names = _imports_and_names(path)
    bad = [m for m in modules if m.startswith(".")
           or any(m == p or m.startswith(p + ".") for p in FORBIDDEN_PREFIXES)
           or any(s in m.lower() for s in FORBIDDEN_SUBSTRINGS)]
    assert not bad, bad
    assert not (names & FORBIDDEN_NAMES), sorted(names & FORBIDDEN_NAMES)


def test_r6_b7_propose_never_called(monkeypatch):
    import app.cognition.b7.translator as translator

    def forbidden(*_a, **_k):
        raise AssertionError("B7 propose must never be called by the shadow")

    monkeypatch.setattr(translator, "propose", forbidden)
    out = run(TEXTS["coreference"])
    assert all("candidate_id" not in r for r in out["resolution_requests"])


# ---------------------------------------------------------------------------
# R7 — no external side effects (bounded guards; reads allowed)
# ---------------------------------------------------------------------------

def test_r7_no_write_network_or_subprocess_in_process(monkeypatch):
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
    for name in ("remove", "unlink", "rename", "replace", "mkdir", "makedirs", "write"):
        monkeypatch.setattr(os, name, forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    before = audit_snapshot()
    for text in TEXTS.values():
        mod.run_cognition_shadow(text)
    assert audit_snapshot() == before


# ---------------------------------------------------------------------------
# R8 — real CLI entrypoint (bounded subprocess, no shell, independent of OBSIDIA_ROUTER_ROOT)
# ---------------------------------------------------------------------------

def _run_cli(text, tmp_path):
    shadow()                                   # RED attribution when the runtime is absent
    assert SCRIPT_PATH.is_file(), RED_MESSAGE
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "OBSIDIA_ROUTER_ROOT")}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run([sys.executable, "-B", str(SCRIPT_PATH), text], cwd=str(tmp_path), env=env,
                          capture_output=True, timeout=120, check=False, shell=False)


@pytest.mark.parametrize("key", ["coreference", "closed_action", "empty"])
def test_r8_cli_prints_contract_json(key, tmp_path):
    before = audit_snapshot()
    proc = _run_cli(TEXTS[key], tmp_path)
    assert proc.returncode == 0, proc.stderr.decode("utf-8", "replace")
    out = json.loads(proc.stdout.decode("utf-8"))
    assert canon(out) == canon(run(TEXTS[key]))
    assert audit_snapshot() == before
    assert list(tmp_path.iterdir()) == []


def test_r8_cli_ignores_obsidia_router_root(tmp_path):
    shadow()
    assert SCRIPT_PATH.is_file(), RED_MESSAGE
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8",
               OBSIDIA_ROUTER_ROOT=str(tmp_path / "nonexistent_router"))
    proc = subprocess.run([sys.executable, "-B", str(SCRIPT_PATH), TEXTS["missing"]], cwd=str(tmp_path), env=env,
                          capture_output=True, timeout=120, check=False, shell=False)
    assert proc.returncode == 0, proc.stderr.decode("utf-8", "replace")
    assert canon(json.loads(proc.stdout.decode("utf-8"))) == canon(run(TEXTS["missing"]))


# ---------------------------------------------------------------------------
# R9 — non-sovereignty
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("key", sorted(TEXTS))
def test_r9_boundary_exact(key):
    out = run(TEXTS[key])
    assert out["boundary"] == EXPECTED_BOUNDARY
    assert out["context_packet"]["boundary"]["decision_authority"] == "KX108_ONLY"
    assert out["context_packet"]["boundary"]["memory_write"] is False
    assert out["context_packet"]["boundary"]["emits_act"] is False
    for entry in out["state_entries"]:
        assert entry["readonly"] is True


# ---------------------------------------------------------------------------
# R10 — regression isolation (sealed B6/B7/SENS and M41 untouched since the baseline)
# ---------------------------------------------------------------------------

def test_r10_sealed_and_m41_sources_unchanged():
    shadow()
    paths = ["app/harness/state_explicit", "app/cognition", "app/semantic", "app/knowledge", "app/world_model",
             "app/primitives", "app/reconstruction", "scripts/obsidia_cli.py", "app/router"]
    proc = subprocess.run(["git", "diff", "--quiet", BASELINE_COMMIT, "--", *paths], cwd=str(ROOT),
                          capture_output=True, timeout=60, check=False, shell=False)
    assert proc.returncode == 0, proc.stdout.decode("utf-8", "replace")
