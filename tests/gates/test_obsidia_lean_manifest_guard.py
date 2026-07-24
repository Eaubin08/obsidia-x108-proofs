"""test_obsidia_lean_manifest_guard — Build Gates V0 (deferred A).

Scope : APPLY_DEFERRED_GATE_LEAN_MANIFEST_V0
Fixtures JSON ecrites uniquement dans tmp_path.
Aucune dependance au manifest reel ni au repo dirty.
"""

from __future__ import annotations

import copy
import json
import py_compile
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_GATES_DIR = _REPO_ROOT / "scripts" / "gates"
sys.path.insert(0, str(_GATES_DIR))

import obsidia_lean_manifest_guard as gate  # noqa: E402


# ── Fixture minimale ───────────────────────────────────────────────────────────

def _make_entry(proof_id: str = "LEAN_TEST_P1", lean_file: str = "Test.lean") -> dict:
    return {
        "proof_id": proof_id,
        "item_id": proof_id,
        "lean_file": f"proofs/lean/Obsidia/{lean_file}",
        "sha256": "abc123def456abc123def456abc123def456abc123def456abc123def456abc1",
        "lean_ok": True,
        "forbidden_ok": True,
        "decision_authority": "KX108_ONLY",
        "runtime_bound": False,
        "category": "TEST",
    }


def _make_manifest(
    *,
    layer_a_count: int = 2,
    layer_b_count: int = 1,
    **overrides,
) -> dict:
    entries_a = [_make_entry(f"LEAN_TEST_A{i}", f"A{i}.lean") for i in range(layer_a_count)]
    entries_b = [_make_entry(f"LEAN_TEST_B{i}", f"B{i}.lean") for i in range(layer_b_count)]
    manifest = {
        "manifest_id": "LEAN_TEST_V1_FIXTURE",
        "generated_at": "2026-07-03T00:00:00+00:00",
        "proof_surface_version": "1.0.0",
        "total_entries": layer_a_count + layer_b_count,
        "decision_authority": "KX108_ONLY",
        "lean_decides": False,
        "runtime_bound": False,
        "attestation_only": True,
        "lean_ok": True,
        "forbidden_ok": True,
        "layers": {
            "LayerA": {"count": layer_a_count, "aggregator": None, "entries": entries_a},
            "LayerB": {"count": layer_b_count, "aggregator": None, "entries": entries_b},
        },
    }
    manifest.update(overrides)
    return manifest


def _write(tmp_path: Path, data: dict) -> Path:
    p = tmp_path / "manifest.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def _run(tmp_path: Path, data: dict) -> int:
    p = _write(tmp_path, data)
    return gate.main(["--file", str(p)])


# ── Tests ──────────────────────────────────────────────────────────────────────

def test_py_compile() -> None:
    py_compile.compile(str(_GATES_DIR / "obsidia_lean_manifest_guard.py"), doraise=True)


def test_valid_manifest_passes(tmp_path, capsys) -> None:
    rc = _run(tmp_path, _make_manifest())
    assert rc == 0
    assert "LEAN_MANIFEST_GUARD_PASS" in capsys.readouterr().out


def test_missing_file_fails(tmp_path, capsys) -> None:
    rc = gate.main(["--file", str(tmp_path / "absent.json")])
    assert rc == 1
    assert "LEAN_MANIFEST_GUARD_FAIL" in capsys.readouterr().out


def test_invalid_json_fails(tmp_path, capsys) -> None:
    p = tmp_path / "bad.json"
    p.write_text("{not valid json", encoding="utf-8")
    rc = gate.main(["--file", str(p)])
    assert rc == 1
    assert "INVALID_JSON" in capsys.readouterr().out


def test_missing_manifest_id_fails(tmp_path, capsys) -> None:
    data = _make_manifest()
    del data["manifest_id"]
    rc = _run(tmp_path, data)
    assert rc == 1
    assert "MISSING_ROOT_FIELD" in capsys.readouterr().out


def test_total_entries_mismatch_fails(tmp_path, capsys) -> None:
    data = _make_manifest()
    data["total_entries"] = 999
    rc = _run(tmp_path, data)
    assert rc == 1
    out = capsys.readouterr().out
    assert "LEAN_MANIFEST_GUARD_FAIL" in out
    assert "MISMATCH" in out


def test_layer_count_mismatch_fails(tmp_path, capsys) -> None:
    data = _make_manifest()
    data["layers"]["LayerA"]["count"] = 99
    rc = _run(tmp_path, data)
    assert rc == 1
    assert "LAYER_COUNT_MISMATCH" in capsys.readouterr().out


def test_root_authority_not_kx108_fails(tmp_path, capsys) -> None:
    data = _make_manifest()
    data["decision_authority"] = "SIGMA_ONLY"
    rc = _run(tmp_path, data)
    assert rc == 1
    assert "ROOT_AUTHORITY_VIOLATION" in capsys.readouterr().out


def test_root_runtime_bound_true_fails(tmp_path, capsys) -> None:
    data = _make_manifest()
    data["runtime_bound"] = True
    rc = _run(tmp_path, data)
    assert rc == 1
    assert "ROOT_RUNTIME_BOUND_VIOLATION" in capsys.readouterr().out


def test_root_lean_decides_true_fails(tmp_path, capsys) -> None:
    data = _make_manifest()
    data["lean_decides"] = True
    rc = _run(tmp_path, data)
    assert rc == 1
    assert "ROOT_LEAN_DECIDES_VIOLATION" in capsys.readouterr().out


def test_entry_missing_required_field_fails(tmp_path, capsys) -> None:
    data = _make_manifest()
    del data["layers"]["LayerA"]["entries"][0]["sha256"]
    rc = _run(tmp_path, data)
    assert rc == 1
    assert "ENTRY_MISSING_FIELD" in capsys.readouterr().out


def test_entry_lean_ok_false_fails(tmp_path, capsys) -> None:
    data = _make_manifest()
    data["layers"]["LayerA"]["entries"][0]["lean_ok"] = False
    rc = _run(tmp_path, data)
    assert rc == 1
    assert "ENTRY_LEAN_OK_FALSE" in capsys.readouterr().out


def test_entry_forbidden_ok_false_fails(tmp_path, capsys) -> None:
    data = _make_manifest()
    data["layers"]["LayerB"]["entries"][0]["forbidden_ok"] = False
    rc = _run(tmp_path, data)
    assert rc == 1
    assert "ENTRY_FORBIDDEN_OK_FALSE" in capsys.readouterr().out


def test_entry_runtime_bound_true_fails(tmp_path, capsys) -> None:
    data = _make_manifest()
    data["layers"]["LayerA"]["entries"][1]["runtime_bound"] = True
    rc = _run(tmp_path, data)
    assert rc == 1
    assert "ENTRY_RUNTIME_BOUND_VIOLATION" in capsys.readouterr().out


def test_entry_authority_not_kx108_fails(tmp_path, capsys) -> None:
    data = _make_manifest()
    data["layers"]["LayerB"]["entries"][0]["decision_authority"] = "BRODY"
    rc = _run(tmp_path, data)
    assert rc == 1
    assert "ENTRY_AUTHORITY_VIOLATION" in capsys.readouterr().out


def test_empty_sha256_fails(tmp_path, capsys) -> None:
    data = _make_manifest()
    data["layers"]["LayerA"]["entries"][0]["sha256"] = ""
    rc = _run(tmp_path, data)
    assert rc == 1
    assert "ENTRY_SHA256_EMPTY" in capsys.readouterr().out


def test_no_mutation_of_gate_file() -> None:
    target = _GATES_DIR / "obsidia_lean_manifest_guard.py"
    before = target.stat().st_mtime_ns
    gate.main(["--file", str(_REPO_ROOT / "proofs" / "LEAN_PROOF_SURFACE_MANIFEST.json")])
    assert target.stat().st_mtime_ns == before
