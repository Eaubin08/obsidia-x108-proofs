"""
tests/cli/test_family_wiring_v0.py
===============================================
Suite TERMINAL_FAMILY_WIRING_SELF_AUDIT_V0.

Prouve que obsidia_family_wiring.audit_family_wiring(...) :
  - resout la famille UNIQUEMENT via la registry (config, jamais de nom
    de famille en dur)
  - echoue ferme si la famille/l'etat canonique est absent ou malforme
  - applique la regle gelee resolution_status absent => OPEN
  - exclut les blockers SUPERSEDED du compte actif
  - RECALCULE independamment les compteurs plutot que de faire confiance
    aux valeurs persistees, et expose toute divergence (consistency_status)
  - ne mute jamais rien, ne cree aucun artefact
  - protege les chemins proteges (aucun acces hors du repo_root fourni)

Tout synthetique (tmp_path) pour les cas de schema/erreur -- la donnee
AGENTS reelle n'est utilisee que pour le test d'E2E de bout en bout via
le vrai CLI (marque explicitement comme tel).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import obsidia_family_wiring as FW  # noqa: E402



def _current_git_branch_for_family_wiring_test() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=Path(__file__).resolve().parents[2],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert result.returncode == 0, result.stderr
    branch = result.stdout.strip()
    assert branch
    return branch

def _write_state(tmp_path: Path, rel: str, data: dict) -> Path:
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def _blocker(**overrides) -> dict:
    base = {
        "blocker_id": "BLK-TEST-001",
        "wave": "WAVE_X",
        "path": "some/file.py",
        "blocker_category": "EXECUTION_BLOCKER",
        "blocker_type": "SYNTHETIC",
        "owner": "TEST",
        "reason": "synthetic",
        "next_action": "NONE",
        "source_artifact": "test.index.json",
        "is_file_blocker": True,
        "is_global_blocker": False,
    }
    base.update(overrides)
    return base


def _synthetic_registry(tmp_path: Path, family_id: str = "TESTFAM") -> dict:
    return {
        "families": {
            family_id: {
                "canonical_state": "state.json",
                "artifact_index": "index.json",
                "authority": "NON_SOVEREIGN",
                "write_capability": False,
            }
        }
    }


# ─── A. Registre resout la famille ───────────────────────────────────────────

class TestFamilyRegistration:
    def test_a_family_registry_resolves_registered_family(self, tmp_path):
        registry = _synthetic_registry(tmp_path)
        reg = FW.load_family_registration("TESTFAM", registry)
        assert reg is not None
        assert reg["canonical_state"] == "state.json"

    def test_unregistered_family_fails_closed(self, tmp_path):
        registry = _synthetic_registry(tmp_path)
        result = FW.audit_family_wiring("UNKNOWN_FAMILY", registry, repo_root=tmp_path)
        assert result["status"] == FW.STATUS_FAMILY_NOT_REGISTERED


# ─── B. Etat canonique se charge ────────────────────────────────────────────

class TestCanonicalStateLoads:
    def test_b_canonical_state_loads(self, tmp_path):
        registry = _synthetic_registry(tmp_path)
        _write_state(tmp_path, "state.json", {
            "global_manifest_complete": True,
            "global_relation_graph_complete": True,
            "testfam_family_reconciliation": {"family_status": "X", "testfam_family_fully_closed": False},
            "blocker_matrix_v1": {"blockers": []},
        })
        result = FW.audit_family_wiring("TESTFAM", registry, repo_root=tmp_path)
        assert result["status"] == FW.STATUS_OK


# ─── C-D. Regle de resolution_status ─────────────────────────────────────────

class TestResolutionSemantics:
    def test_c_missing_resolution_status_is_open(self, tmp_path):
        registry = _synthetic_registry(tmp_path)
        _write_state(tmp_path, "state.json", {
            "blocker_matrix_v1": {"blockers": [_blocker()]},
        })
        result = FW.audit_family_wiring("TESTFAM", registry, repo_root=tmp_path)
        assert result["active_blockers"][0]["resolution_status"] == "OPEN"
        assert result["recomputed_active_file_blockers"] == 1

    def test_d_superseded_excluded_from_active_count(self, tmp_path):
        registry = _synthetic_registry(tmp_path)
        _write_state(tmp_path, "state.json", {
            "blocker_matrix_v1": {"blockers": [
                _blocker(blocker_id="BLK-GLOBAL-A", is_file_blocker=False, is_global_blocker=True,
                         resolution_status="SUPERSEDED", resolution_reason="r", resolved_by_provider="p"),
            ]},
        })
        result = FW.audit_family_wiring("TESTFAM", registry, repo_root=tmp_path)
        assert result["recomputed_active_global_blockers"] == 0
        assert result["recomputed_historical_superseded"] == 1
        assert len(result["historical_superseded_blockers"]) == 1
        assert result["active_blockers"] == []


# ─── E-G. Derivation depuis l'etat reel AGENTS (synthetique ici, structure identique) ──

class TestDerivedCounts:
    def test_e_f_g_active_and_historical_counts_derived_not_hardcoded(self, tmp_path):
        registry = _synthetic_registry(tmp_path)
        blockers = [_blocker(blocker_id=f"BLK-FILE-{i}") for i in range(16)]
        blockers += [
            _blocker(blocker_id="BLK-GLOBAL-1", is_file_blocker=False, is_global_blocker=True,
                      resolution_status="SUPERSEDED", resolution_reason="r", resolved_by_provider="p"),
            _blocker(blocker_id="BLK-GLOBAL-2", is_file_blocker=False, is_global_blocker=True,
                      resolution_status="SUPERSEDED", resolution_reason="r", resolved_by_provider="p"),
            _blocker(blocker_id="BLK-GLOBAL-3", is_file_blocker=False, is_global_blocker=True,
                      resolution_status="SUPERSEDED", resolution_reason="r", resolved_by_provider="p"),
        ]
        _write_state(tmp_path, "state.json", {"blocker_matrix_v1": {"blockers": blockers}})
        result = FW.audit_family_wiring("TESTFAM", registry, repo_root=tmp_path)
        assert result["recomputed_active_file_blockers"] == 16
        assert result["recomputed_active_global_blockers"] == 0
        assert result["recomputed_historical_superseded"] == 3


# ─── H. Coherence persiste vs recalcule ─────────────────────────────────────

class TestConsistency:
    def test_h_persisted_and_recomputed_agree(self, tmp_path):
        registry = _synthetic_registry(tmp_path)
        _write_state(tmp_path, "state.json", {
            "testfam_family_reconciliation": {
                "testfam_family_file_blockers": 1,
                "testfam_family_global_blockers": 0,
                "testfam_family_historical_superseded_global_blockers": 0,
            },
            "blocker_matrix_v1": {"blockers": [_blocker()], "total_blockers": 1},
        })
        result = FW.audit_family_wiring("TESTFAM", registry, repo_root=tmp_path)
        assert result["consistency_status"] == FW.CONSISTENCY_PASS

    def test_h_disagreement_reported_not_normalized(self, tmp_path):
        registry = _synthetic_registry(tmp_path)
        _write_state(tmp_path, "state.json", {
            "testfam_family_reconciliation": {
                "testfam_family_file_blockers": 99,  # sciemment faux
            },
            "blocker_matrix_v1": {"blockers": [_blocker()], "total_blockers": 1},
        })
        result = FW.audit_family_wiring("TESTFAM", registry, repo_root=tmp_path)
        assert result["consistency_status"] == FW.CONSISTENCY_FAIL
        # jamais de correction silencieuse : la valeur persistee fausse reste visible telle quelle
        assert result["persisted_active_file_blockers"] == 99
        assert result["recomputed_active_file_blockers"] == 1


# ─── I. fully_closed ─────────────────────────────────────────────────────────

class TestFullyClosed:
    def test_i_fully_closed_false_when_declared(self, tmp_path):
        registry = _synthetic_registry(tmp_path)
        _write_state(tmp_path, "state.json", {
            "testfam_family_reconciliation": {"testfam_family_fully_closed": False},
            "blocker_matrix_v1": {"blockers": []},
        })
        result = FW.audit_family_wiring("TESTFAM", registry, repo_root=tmp_path)
        assert result["fully_closed"] is False


# ─── J. Provenance ────────────────────────────────────────────────────────────

class TestProvenance:
    def test_j_provenance_populated(self, tmp_path):
        registry = _synthetic_registry(tmp_path)
        _write_state(tmp_path, "state.json", {"blocker_matrix_v1": {"blockers": []}})
        result = FW.audit_family_wiring("TESTFAM", registry, repo_root=tmp_path)
        prov = result["provenance"]
        assert prov["state_source_sha256"] is not None
        assert prov["captured_at"] is not None
        assert prov["worktree_root"] == str(tmp_path)


# ─── K-L. Echecs fermes ───────────────────────────────────────────────────────

class TestFailClosed:
    def test_k_missing_family_fails_closed(self, tmp_path):
        registry = {"families": {}}
        result = FW.audit_family_wiring("NOPE", registry, repo_root=tmp_path)
        assert result["status"] == FW.STATUS_FAMILY_NOT_REGISTERED

    def test_k_missing_state_file_fails_closed(self, tmp_path):
        registry = _synthetic_registry(tmp_path)
        result = FW.audit_family_wiring("TESTFAM", registry, repo_root=tmp_path)
        assert result["status"] == FW.STATUS_STATE_FILE_MISSING

    def test_l_malformed_state_fails_closed(self, tmp_path):
        registry = _synthetic_registry(tmp_path)
        p = tmp_path / "state.json"
        p.write_text("{not valid json", encoding="utf-8")
        result = FW.audit_family_wiring("TESTFAM", registry, repo_root=tmp_path)
        assert result["status"] == FW.STATUS_STATE_FILE_MALFORMED

    def test_l_non_object_root_fails_closed(self, tmp_path):
        registry = _synthetic_registry(tmp_path)
        p = tmp_path / "state.json"
        p.write_text("[1, 2, 3]", encoding="utf-8")
        result = FW.audit_family_wiring("TESTFAM", registry, repo_root=tmp_path)
        assert result["status"] == FW.STATUS_STATE_FILE_MALFORMED


# ─── M-N. Aucune ecriture, chemins proteges intacts ─────────────────────────

class TestNoWrite:
    def test_m_no_write_occurs(self, tmp_path):
        registry = _synthetic_registry(tmp_path)
        _write_state(tmp_path, "state.json", {"blocker_matrix_v1": {"blockers": [_blocker()]}})
        before = {p: p.read_bytes() for p in tmp_path.rglob("*.json")}
        FW.audit_family_wiring("TESTFAM", registry, repo_root=tmp_path)
        after = {p: p.read_bytes() for p in tmp_path.rglob("*.json")}
        assert before == after
        assert set(before.keys()) == set(after.keys())  # aucun fichier cree/supprime

    def test_n_protected_paths_untouched(self, tmp_path):
        protected = tmp_path / "proofs" / "sealed.json"
        protected.parent.mkdir(parents=True)
        protected.write_text('{"sealed": true}', encoding="utf-8")
        registry = _synthetic_registry(tmp_path)
        _write_state(tmp_path, "state.json", {"blocker_matrix_v1": {"blockers": []}})
        before = protected.read_bytes()
        FW.audit_family_wiring("TESTFAM", registry, repo_root=tmp_path)
        assert protected.read_bytes() == before


# ─── Generique : aucun nom de famille en dur dans le lecteur ────────────────

class TestGenericNoHardcodedFamily:
    def test_reader_works_for_arbitrary_family_id(self, tmp_path):
        """Preuve que le lecteur ne connait pas 'AGENTS' -- fonctionne identiquement
        pour n'importe quel family_id fourni par la registry."""
        registry = {
            "families": {
                "ZORP": {
                    "canonical_state": "zorp_state.json",
                    "artifact_index": "zorp_index.json",
                    "authority": "NON_SOVEREIGN",
                }
            }
        }
        _write_state(tmp_path, "zorp_state.json", {
            "zorp_family_reconciliation": {"family_status": "ZORP_OK", "zorp_family_fully_closed": True},
            "blocker_matrix_v1": {"blockers": []},
        })
        result = FW.audit_family_wiring("ZORP", registry, repo_root=tmp_path)
        assert result["status"] == FW.STATUS_OK
        assert result["family_status"] == "ZORP_OK"
        assert result["fully_closed"] is True


# ─── E2E reel via le vrai CLI (donnee AGENTS reelle, explicitement marque) ──

class TestRealCliE2E:
    def test_real_terminal_e2e_wiring_status_agents(self):
        """E2E OBLIGATOIRE : invoque le vrai binaire CLI, pas des fonctions
        Python importees directement. Utilise l'etat AGENTS reel importe dans
        le depot Terminal canonique (BOUNDED_CANONICAL_STATE_BUNDLE_IMPORT,
        source_checkpoint=4005f3ee47acbce7f6d7252939d99c9be022f313 sur
        campaign/obsidia-4353-family-compilation-v1) ; ce test verifie
        seulement que le CHEMIN TERMINAL les redecouvre correctement et que
        consistency_status=PASS."""
        proc = subprocess.run(
            [sys.executable, "scripts/obsidia_cli.py", "wiring", "status", "AGENTS", "--json"],
            cwd=str(_REPO_ROOT), capture_output=True, text=True, timeout=30,
        )
        assert proc.returncode == 0, proc.stderr
        data = json.loads(proc.stdout)
        assert data["status"] == "OK"
        assert data["family"] == "AGENTS"
        assert data["consistency_status"] == "PASS"
        assert data["fully_closed"] is False
        assert data["recomputed_active_global_blockers"] == 0
        assert data["recomputed_historical_superseded"] == 3
        assert isinstance(data["recomputed_active_file_blockers"], int)
        assert data["provenance"]["git_branch"] == _current_git_branch_for_family_wiring_test()

    def test_real_terminal_e2e_unregistered_family_fails_closed(self):
        proc = subprocess.run(
            [sys.executable, "scripts/obsidia_cli.py", "wiring", "status", "NOT_A_REAL_FAMILY", "--json"],
            cwd=str(_REPO_ROOT), capture_output=True, text=True, timeout=30,
        )
        assert proc.returncode == 0
        data = json.loads(proc.stdout)
        assert data["status"] == "FAMILY_NOT_REGISTERED"
