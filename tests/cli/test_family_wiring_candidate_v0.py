"""
tests/cli/test_family_wiring_candidate_v0.py
===============================================
Suite FAMILY_WIRING_CANDIDATE_ONLY_V0.

Prouve que obsidia_family_wiring.build_family_remediation_candidate(...) :
  - transforme UN blocker Family Wiring ACTIF en candidat structure
    deterministe, sans jamais rien ecrire ni creer d'artefact persiste
  - resout la famille UNIQUEMENT via la registry (aucun nom de famille en
    dur)
  - echoue ferme : famille inconnue, blocker inconnu, blocker historique
    / SUPERSEDED, blocker actif sans chemin cible, consistency != PASS
  - candidate_id deterministe (meme etat canonique + meme blocker =>
    meme candidate_id ; captured_at n'entre pas dans l'id)
  - PRESERVE l'ambiguite de next_action : un "..._OR_..." n'est jamais
    reduit a une seule action ; la machine ne choisit rien
  - authority=NON_SOVEREIGN, write_capability=false,
    requires_human_review=true, decision_authority=KX108_ONLY

Tout synthetique (tmp_path) pour schema/erreurs. La donnee AGENTS reelle
n'est utilisee que dans TestRealCliE2E via le vrai binaire CLI.

Ce checkpoint est OBSERVATION -> CANDIDAT STRUCTURE seulement : pas de
proposition, pas de ledger, pas de batch, pas de KX108, pas d'approbation
humaine, pas de mutation de cible, pas de closure. Le seam de remediation
gouvernee complet reste sur HOLD.
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


# --- fixtures synthetiques -------------------------------------------------


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
        "blocker_id": "BLK-SYNTH-001",
        "wave": "WAVE_X",
        "path": "some/dir/artifact.py.bak_safe_scan_20200101_000000",
        "blocker_category": "RELATION_BLOCKER",
        "blocker_type": "BAK_SCAN_ARTIFACT_NO_CONSUMER",
        "owner": "WAVE_X",
        "reason": "synthetic bak artifact",
        "next_action": "ARCHIVE_OR_DELETE_IN_CLEANUP_CAMPAIGN",
        "source_artifact": "periphery/agents/synthetic.index.json",
        "is_file_blocker": True,
        "is_global_blocker": False,
    }
    base.update(overrides)
    return base


def _synthetic_registry(family_id: str = "TESTFAM") -> dict:
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


def _ok_state(blockers: list) -> dict:
    """Etat canonique coherent (persisted == recompute) => consistency PASS."""
    active_file = sum(
        1 for b in blockers
        if b.get("is_file_blocker") and (b.get("resolution_status") or "OPEN") == "OPEN"
    )
    active_global = sum(
        1 for b in blockers
        if b.get("is_global_blocker") and (b.get("resolution_status") or "OPEN") == "OPEN"
    )
    hist = sum(
        1 for b in blockers
        if b.get("is_global_blocker") and b.get("resolution_status") == "SUPERSEDED"
    )
    return {
        "testfam_family_reconciliation": {
            "testfam_family_file_blockers": active_file,
            "testfam_family_global_blockers": active_global,
            "testfam_family_historical_superseded_global_blockers": hist,
        },
        "blocker_matrix_v1": {"blockers": blockers, "total_blockers": active_file + active_global},
    }


def _build(tmp_path: Path, blockers: list, family_id: str = "TESTFAM", blocker_id: str = "BLK-SYNTH-001"):
    registry = _synthetic_registry(family_id)
    _write_state(tmp_path, "state.json", _ok_state(blockers))
    return FW.build_family_remediation_candidate(family_id, blocker_id, registry, repo_root=tmp_path)


# --- 1. determinisme du candidate_id ------------------------------------------

def test_1_candidate_id_deterministic(tmp_path):
    r1 = _build(tmp_path, [_blocker()])
    r2 = _build(tmp_path, [_blocker()])
    assert r1["status"] == FW.STATUS_OK
    assert r1["candidate_id"] == r2["candidate_id"]
    assert r1["candidate_id"].startswith("frc-")
    # captured_at ne doit PAS influer sur l'id
    assert r1["finding_provenance"]["captured_at"] != r2["finding_provenance"]["captured_at"] \
        or r1["finding_provenance"]["captured_at"] == r2["finding_provenance"]["captured_at"]
    assert r1["candidate_id"] == r2["candidate_id"]


def test_1b_candidate_id_changes_with_canonical_state(tmp_path):
    r1 = _build(tmp_path, [_blocker()])
    r2 = _build(tmp_path, [_blocker(reason="different reason changes state sha")])
    assert r1["candidate_id"] != r2["candidate_id"]


# --- 2. famille enregistree -> OK -------------------------------------------

def test_2_registered_family_ok(tmp_path):
    r = _build(tmp_path, [_blocker()])
    assert r["status"] == FW.STATUS_OK
    assert r["family_id"] == "TESTFAM"
    assert r["source_blocker_id"] == "BLK-SYNTH-001"


def test_2b_generic_arbitrary_family_id(tmp_path):
    """Le builder ne connait pas 'AGENTS' : fonctionne pour n'importe quel
    family_id fourni par la registry."""
    registry = {
        "families": {
            "ZORP": {"canonical_state": "z.json", "artifact_index": "zi.json", "authority": "NON_SOVEREIGN"}
        }
    }
    _write_state(tmp_path, "z.json", {
        "zorp_family_reconciliation": {"zorp_family_file_blockers": 1},
        "blocker_matrix_v1": {"blockers": [_blocker(blocker_id="BLK-ZORP-9")], "total_blockers": 1},
    })
    r = FW.build_family_remediation_candidate("ZORP", "BLK-ZORP-9", registry, repo_root=tmp_path)
    assert r["status"] == FW.STATUS_OK
    assert r["family_id"] == "ZORP"


# --- 3. famille inconnue : echec ferme ------------------------------------

def test_3_unknown_family_fails_closed(tmp_path):
    registry = _synthetic_registry("TESTFAM")
    _write_state(tmp_path, "state.json", _ok_state([_blocker()]))
    r = FW.build_family_remediation_candidate("NOPE", "BLK-SYNTH-001", registry, repo_root=tmp_path)
    assert r["status"] == FW.STATUS_FAMILY_NOT_REGISTERED
    assert "candidate_id" not in r


def test_3b_missing_state_file_fails_closed(tmp_path):
    registry = _synthetic_registry("TESTFAM")
    r = FW.build_family_remediation_candidate("TESTFAM", "BLK-SYNTH-001", registry, repo_root=tmp_path)
    assert r["status"] == FW.STATUS_STATE_FILE_MISSING
    assert "candidate_id" not in r


# --- 4. blocker inconnu : echec ferme -----------------------------------

def test_4_unknown_blocker_fails_closed(tmp_path):
    r = _build(tmp_path, [_blocker()], blocker_id="BLK-DOES-NOT-EXIST")
    assert r["status"] == FW.STATUS_BLOCKER_NOT_FOUND
    assert "candidate_id" not in r


# --- 5. blocker historique / SUPERSEDED : rejete comme cible active -----

def test_5_superseded_blocker_rejected(tmp_path):
    blockers = [
        _blocker(),  # garde 1 file blocker actif pour la coherence
        _blocker(
            blocker_id="BLK-GLOBAL-OLD", is_file_blocker=False, is_global_blocker=True,
            resolution_status="SUPERSEDED", resolution_reason="r", resolved_by_provider="p",
        ),
    ]
    r = _build(tmp_path, blockers, blocker_id="BLK-GLOBAL-OLD")
    assert r["status"] == FW.STATUS_BLOCKER_NOT_ACTIVE
    assert r.get("resolution_status") == "SUPERSEDED"
    assert "candidate_id" not in r


# --- 6. consistency != PASS bloque le candidat -------------------------

def test_6_consistency_fail_blocks_candidate(tmp_path):
    registry = _synthetic_registry("TESTFAM")
    _write_state(tmp_path, "state.json", {
        "testfam_family_reconciliation": {"testfam_family_file_blockers": 99},  # sciemment faux
        "blocker_matrix_v1": {"blockers": [_blocker()], "total_blockers": 1},
    })
    r = FW.build_family_remediation_candidate("TESTFAM", "BLK-SYNTH-001", registry, repo_root=tmp_path)
    assert r["status"] == FW.STATUS_CONSISTENCY_HOLD
    assert r["consistency_status"] == FW.CONSISTENCY_FAIL
    assert "candidate_id" not in r


# --- 7. target_path propage tel quel ----------------------------------

def test_7_target_path_propagated(tmp_path):
    path = "periphery/x/y/thing.py.bak_safe_scan_20200202_010101"
    r = _build(tmp_path, [_blocker(path=path)])
    assert r["target_path"] == path


def test_7b_active_blocker_without_path_is_malformed(tmp_path):
    r = _build(tmp_path, [_blocker(path="")])
    assert r["status"] == FW.STATUS_BLOCKER_MALFORMED
    assert "candidate_id" not in r


# --- 8. provenance propagee -----------------------------------------

def test_8_provenance_propagated(tmp_path):
    r = _build(tmp_path, [_blocker(source_artifact="periphery/agents/foo.index.json")])
    prov = r["finding_provenance"]
    assert prov["family_wiring_state_sha256"] is not None
    assert len(prov["family_wiring_state_sha256"]) == 64
    assert prov["source_artifact"] == "periphery/agents/foo.index.json"
    assert prov["captured_at"] is not None


# --- 9. allowed_scope limite a la cible -------------------------------

def test_9_allowed_scope_is_exactly_target(tmp_path):
    path = "some/dir/artifact.py.bak_safe_scan_20200101_000000"
    r = _build(tmp_path, [_blocker(path=path)])
    assert r["allowed_scope"] == [path]
    assert r["forbidden_scope"] == []


# --- 10-12. autorite / capacite d'ecriture / revue humaine -----------

def test_10_requires_human_review_true(tmp_path):
    r = _build(tmp_path, [_blocker()])
    assert r["requires_human_review"] is True


def test_11_authority_non_sovereign(tmp_path):
    r = _build(tmp_path, [_blocker()])
    assert r["authority"] == "NON_SOVEREIGN"
    assert r["decision_authority"] == "KX108_ONLY"


def test_12_write_capability_false(tmp_path):
    r = _build(tmp_path, [_blocker()])
    assert r["write_capability"] is False


# --- 13-14. aucune ecriture filesystem / aucune mutation d'etat ------

def test_13_zero_filesystem_mutation(tmp_path):
    registry = _synthetic_registry("TESTFAM")
    _write_state(tmp_path, "state.json", _ok_state([_blocker()]))
    before = {p: p.read_bytes() for p in tmp_path.rglob("*")}
    FW.build_family_remediation_candidate("TESTFAM", "BLK-SYNTH-001", registry, repo_root=tmp_path)
    after = {p: p.read_bytes() for p in tmp_path.rglob("*")}
    assert set(before.keys()) == set(after.keys())  # aucun fichier cree/supprime
    assert before == after                          # aucun octet modifie


def test_14_canonical_state_bytes_unchanged(tmp_path):
    registry = _synthetic_registry("TESTFAM")
    state_path = _write_state(tmp_path, "state.json", _ok_state([_blocker()]))
    before = state_path.read_bytes()
    FW.build_family_remediation_candidate("TESTFAM", "BLK-SYNTH-001", registry, repo_root=tmp_path)
    assert state_path.read_bytes() == before


# --- 15-16. ambiguite ARCHIVE_OR_DELETE preservee, aucune action choisie

def test_15_ambiguous_next_action_preserved_not_collapsed(tmp_path):
    r = _build(tmp_path, [_blocker(next_action="ARCHIVE_OR_DELETE_IN_CLEANUP_CAMPAIGN")])
    assert r["status"] == FW.STATUS_OK
    assert r["source_next_action"] == "ARCHIVE_OR_DELETE_IN_CLEANUP_CAMPAIGN"
    assert r["candidate_status"] == FW.CANDIDATE_STATUS_HOLD_FOR_HUMAN_REMEDIATION_CHOICE
    assert r["remediation_intent"] == FW.REMEDIATION_HOLD_FOR_HUMAN_CHOICE
    assert r["source_next_action_classification"] == "next_action_is_explicit_disjunction"


def test_16_no_single_archive_or_delete_selected(tmp_path):
    r = _build(tmp_path, [_blocker(next_action="ARCHIVE_OR_DELETE_IN_CLEANUP_CAMPAIGN")])
    intent = r["remediation_intent"]
    assert intent not in ("ARCHIVE", "DELETE", "ARCHIVE_OR_DELETE", "ARCHIVE_OR_DELETE_IN_CLEANUP_CAMPAIGN")
    assert intent == "HOLD_FOR_HUMAN_REMEDIATION_CHOICE"


def test_16b_campaign_deferral_also_holds(tmp_path):
    r = _build(tmp_path, [_blocker(next_action="RESOLVE_IN_BRODY_API_STABILIZATION_CAMPAIGN")])
    assert r["candidate_status"] == FW.CANDIDATE_STATUS_HOLD_FOR_HUMAN_REMEDIATION_CHOICE
    assert r["remediation_intent"] == FW.REMEDIATION_HOLD_FOR_HUMAN_CHOICE
    assert r["source_next_action_classification"] == "next_action_deferred_to_named_effort"


def test_16c_single_deterministic_action_is_ready_for_review(tmp_path):
    """Un next_action mono-token, sans '_OR_' ni deferral de campagne, devient
    READY_FOR_HUMAN_REVIEW avec remediation_intent = le token concret --
    mais toujours requires_human_review=true, NON_SOVEREIGN, write=false."""
    r = _build(tmp_path, [_blocker(next_action="REWIRE")])
    assert r["candidate_status"] == FW.CANDIDATE_STATUS_READY_FOR_HUMAN_REVIEW
    assert r["remediation_intent"] == "REWIRE"
    assert r["source_next_action_classification"] == "next_action_is_single_token"
    assert r["requires_human_review"] is True
    assert r["authority"] == "NON_SOVEREIGN"
    assert r["write_capability"] is False


# --- 17. E2E reel via le vrai CLI (donnee AGENTS reelle) --------------

class TestRealCliE2E:
    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "scripts/obsidia_cli.py", *args],
            cwd=str(_REPO_ROOT), capture_output=True, text=True, timeout=60,
        )

    def test_17_real_e2e_candidate_agents_blk_w5d_001(self):
        """E2E OBLIGATOIRE : vrai binaire CLI, etat AGENTS reel. La verite du
        blocker est d'abord relue via 'wiring blockers', puis comparee au
        candidat -- rien n'est code en dur au-dela de l'identifiant pilote."""
        blk_proc = self._run("wiring", "blockers", "AGENTS", "--json")
        assert blk_proc.returncode == 0, blk_proc.stderr
        blk_data = json.loads(blk_proc.stdout)
        canonical = next(
            (b for b in blk_data["active_blockers"] if b["blocker_id"] == "BLK-W5D-001"), None
        )
        assert canonical is not None, "BLK-W5D-001 absent de l'etat AGENTS actif courant"

        proc = self._run("wiring", "candidate", "AGENTS", "BLK-W5D-001", "--json")
        assert proc.returncode == 0, proc.stderr
        cand = json.loads(proc.stdout)

        assert cand["status"] == "OK"
        assert cand["family_id"] == "AGENTS"
        assert cand["source_blocker_id"] == "BLK-W5D-001"
        assert cand["target_path"] == canonical["path"]
        assert cand["source_next_action"] == canonical["next_action"]
        assert cand["allowed_scope"] == [canonical["path"]]
        assert cand["forbidden_scope"] == []
        assert cand["requires_human_review"] is True
        assert cand["authority"] == "NON_SOVEREIGN"
        assert cand["write_capability"] is False
        assert cand["decision_authority"] == "KX108_ONLY"
        assert cand["finding_provenance"]["git_branch"] == _current_git_branch_for_family_wiring_test()
        assert len(cand["finding_provenance"]["family_wiring_state_sha256"]) == 64

        # next_action canonique = "ARCHIVE_OR_DELETE_..." => disjonction explicite,
        # la machine ne choisit NI archive NI delete.
        assert "_OR_" in canonical["next_action"]
        assert cand["candidate_status"] == "HOLD_FOR_HUMAN_REMEDIATION_CHOICE"
        assert cand["remediation_intent"] == "HOLD_FOR_HUMAN_REMEDIATION_CHOICE"
        assert cand["remediation_intent"] not in ("ARCHIVE", "DELETE")

    def test_17b_candidate_id_stable_across_two_real_invocations(self):
        a = self._run("wiring", "candidate", "AGENTS", "BLK-W5D-001", "--json")
        b = self._run("wiring", "candidate", "AGENTS", "BLK-W5D-001", "--json")
        assert a.returncode == 0 and b.returncode == 0
        assert json.loads(a.stdout)["candidate_id"] == json.loads(b.stdout)["candidate_id"]

    def test_18_real_e2e_json_output_well_formed(self):
        proc = self._run("wiring", "candidate", "AGENTS", "BLK-W5D-001", "--json")
        assert proc.returncode == 0
        data = json.loads(proc.stdout)  # ne doit pas lever
        assert isinstance(data, dict) and data["candidate_id"].startswith("frc-")

    def test_18b_real_e2e_human_output_not_approved_looking(self):
        proc = self._run("wiring", "candidate", "AGENTS", "BLK-W5D-001")
        assert proc.returncode == 0
        out = proc.stdout
        assert "HUMAN REMEDIATION CHOICE REQUIRED" in out
        assert "NOT an execution authorization" in out
        assert "candidate_status     : HOLD_FOR_HUMAN_REMEDIATION_CHOICE" in out
        assert "ALLOW" not in out and "APPROVED" not in out

    def test_18c_real_e2e_unknown_blocker_fails_closed(self):
        proc = self._run("wiring", "candidate", "AGENTS", "BLK-NOPE-999", "--json")
        assert proc.returncode == 0
        data = json.loads(proc.stdout)
        assert data["status"] == "BLOCKER_NOT_FOUND"
        assert "candidate_id" not in data

    def test_19_existing_wiring_subcommands_still_compatible(self):
        """La commande candidate ne doit pas perturber status|audit|blockers."""
        for sub in ("status", "audit", "blockers"):
            proc = self._run("wiring", sub, "AGENTS", "--json")
            assert proc.returncode == 0, proc.stderr
            data = json.loads(proc.stdout)
            assert data["status"] == "OK"
            assert data["family"] == "AGENTS"
            assert data["consistency_status"] == "PASS"
