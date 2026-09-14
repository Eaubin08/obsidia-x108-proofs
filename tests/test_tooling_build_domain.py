"""
Tests du domaine tooling_build — KX108_TOOLING_BUILD_DOMAIN_ADAPTER_V0

Contrat canonique étendu (section 9 du mandat) :
  session_id, objective, base_sha, manifest_hash, diff_hash,
  approved_scope, actual_touched_files, new_files, deleted_files,
  protected_scope_status, human_approval_status, obsidure_status,
  worktree_isolated, branch_isolated,
  auto_commit_disabled, auto_push_disabled, auto_merge_disabled,
  tests_results, gates_results, first_failure,
  commit_status, push_status, merge_status,
  unknowns, contradictions, risk_flags, decision_authority

Groupes :
  A — contracts (Domain enum, ToolingBuildState)
  B — agents unitaires (ScopeIntegrityAgent, TestGateAgent, SessionIntegrityAgent, CommitGuardAgent)
  C — agrégation formelle (aggregate_tooling_build)
  D — pipeline complet (run_tooling_build_pipeline)
  E — run_pipeline.py CLI (validation + dispatch)
  F — invariants de gouvernance (DECISION_AUTHORITY=KX108_ONLY, emits_act=false)
  G — fixtures intégration (ACT / HOLD / BLOCK)
"""
from __future__ import annotations

import dataclasses
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sigma.contracts import (
    Domain,
    Layer,
    Severity,
    ToolingBuildState,
)
from sigma.domains.tooling_build_agents import (
    CommitGuardAgent,
    ScopeIntegrityAgent,
    SessionIntegrityAgent,
    TestGateAgent,
    build_tooling_build_agents,
)
from sigma.aggregation import aggregate_tooling_build
from sigma.protocols import run_tooling_build_pipeline
from sigma.run_pipeline import validate_tooling_build_payload


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_state(**overrides) -> ToolingBuildState:
    """Session propre — doit produire ACT (x108_gate=ALLOW)."""
    base = dict(
        session_id="35d45cb9",
        objective="TERMINAL_BUILD_BOUNDED_V1",
        base_sha="6a16d02abc",
        manifest_hash="deadbeef01234567",
        diff_hash="abc1234567890def",
        approved_scope=["sigma/contracts.py", "sigma/domains/tooling_build_agents.py"],
        actual_touched_files=["sigma/contracts.py", "sigma/domains/tooling_build_agents.py"],
        new_files=[],
        deleted_files=[],
        protected_scope_status="CLEAN",
        human_approval_status="APPROVED",
        obsidure_status="CLEAN",
        worktree_isolated=True,
        branch_isolated=True,
        auto_commit_disabled=True,
        auto_push_disabled=True,
        auto_merge_disabled=True,
        tests_results="PASS",
        gates_results="PASS",
        first_failure="",
        commit_status="NOT_COMMITTED",
        push_status="NOT_PUSHED",
        merge_status="NOT_MERGED",
        unknowns=[],
        contradictions=[],
        risk_flags=[],
        decision_authority="KX108_ONLY",
    )
    base.update(overrides)
    return ToolingBuildState(**base)


def _run_pipeline(state: ToolingBuildState) -> dict:
    return dataclasses.asdict(run_tooling_build_pipeline(state))


def _cli_payload(**overrides) -> dict:
    """Payload minimal valide pour le CLI (tous les champs requis)."""
    base = dict(
        session_id="35d45cb9",
        objective="TERMINAL_BUILD_BOUNDED_V1",
        base_sha="6a16d02",
        manifest_hash="deadbeef01234567",
        human_approval_status="APPROVED",
        worktree_isolated=True,
        branch_isolated=True,
        auto_commit_disabled=True,
        auto_push_disabled=True,
        auto_merge_disabled=True,
        tests_results="PASS",
        gates_results="PASS",
        commit_status="NOT_COMMITTED",
        push_status="NOT_PUSHED",
        merge_status="NOT_MERGED",
        decision_authority="KX108_ONLY",
    )
    base.update(overrides)
    return base


def _cli_run(payload: dict) -> dict:
    result = subprocess.run(
        [sys.executable, str(ROOT / "sigma" / "run_pipeline.py"), "tooling_build", json.dumps(payload)],
        capture_output=True, text=True,
    )
    return json.loads(result.stdout)


# ---------------------------------------------------------------------------
# Groupe A — contracts
# ---------------------------------------------------------------------------

class TestContracts:
    def test_domain_tooling_build_exists(self):
        assert Domain.TOOLING_BUILD == Domain.TOOLING_BUILD

    def test_domain_tooling_build_value(self):
        assert Domain.TOOLING_BUILD.value == "tooling_build"

    def test_tooling_build_state_defaults(self):
        s = ToolingBuildState()
        assert s.session_id == "UNKNOWN"
        assert s.human_approval_status == "UNKNOWN"
        assert s.auto_commit_disabled is True
        assert s.decision_authority == "KX108_ONLY"
        assert s.approved_scope == []

    def test_tooling_build_state_kwarg_init(self):
        s = _clean_state()
        assert s.session_id == "35d45cb9"
        assert s.human_approval_status == "APPROVED"
        assert s.tests_results == "PASS"
        assert s.branch_isolated is True

    def test_tooling_build_state_bool_coercion(self):
        s = ToolingBuildState(worktree_isolated=True, branch_isolated=True)
        assert isinstance(s.worktree_isolated, bool)
        assert isinstance(s.branch_isolated, bool)
        assert isinstance(s.auto_commit_disabled, bool)

    def test_tooling_build_state_list_fields(self):
        s = ToolingBuildState(
            approved_scope=["a.py", "b.py"],
            actual_touched_files=["a.py"],
            unknowns=["U1"],
            contradictions=["C1"],
            risk_flags=["R1"],
        )
        assert len(s.approved_scope) == 2
        assert len(s.actual_touched_files) == 1
        assert "U1" in s.unknowns
        assert "C1" in s.contradictions
        assert "R1" in s.risk_flags

    def test_tooling_build_state_all_fields_present(self):
        s = _clean_state()
        required = [
            "session_id", "objective", "base_sha", "manifest_hash", "diff_hash",
            "approved_scope", "actual_touched_files", "new_files", "deleted_files",
            "protected_scope_status", "human_approval_status", "obsidure_status",
            "worktree_isolated", "branch_isolated",
            "auto_commit_disabled", "auto_push_disabled", "auto_merge_disabled",
            "tests_results", "gates_results", "first_failure",
            "commit_status", "push_status", "merge_status",
            "unknowns", "contradictions", "risk_flags",
            "decision_authority",
        ]
        for f in required:
            assert hasattr(s, f), f"Champ manquant: {f}"

    def test_decision_authority_constant(self):
        s = _clean_state()
        assert s.decision_authority == "KX108_ONLY"


# ---------------------------------------------------------------------------
# Groupe B — agents unitaires
# ---------------------------------------------------------------------------

class TestScopeIntegrityAgent:
    def test_allow_on_clean_scope(self):
        agent = ScopeIntegrityAgent()
        vote = agent.evaluate(_clean_state())
        assert vote.proposed_verdict == "READY_FOR_COMMIT_REVIEW"
        assert vote.confidence >= 0.9
        assert vote.layer == Layer.OBSERVATION

    def test_hold_on_scope_drift(self):
        agent = ScopeIntegrityAgent()
        vote = agent.evaluate(_clean_state(
            approved_scope=["a.py"],
            actual_touched_files=["a.py", "extra.py"],
        ))
        assert vote.proposed_verdict == "BUILD_HOLD"
        assert "SCOPE_DRIFT" in vote.unknowns

    def test_block_on_protected_path(self):
        agent = ScopeIntegrityAgent()
        vote = agent.evaluate(_clean_state(protected_scope_status="VIOLATED"))
        assert vote.proposed_verdict == "BUILD_BLOCK"
        assert "PROTECTED_PATH_VIOLATION" in vote.contradictions
        assert vote.confidence < 0.2

    def test_domain_is_tooling_build(self):
        vote = ScopeIntegrityAgent().evaluate(_clean_state())
        assert vote.domain == Domain.TOOLING_BUILD

    def test_empty_approved_scope_no_drift(self):
        """Si approved_scope vide, pas de drift calculé."""
        vote = ScopeIntegrityAgent().evaluate(_clean_state(
            approved_scope=[],
            actual_touched_files=["any.py"],
        ))
        assert vote.proposed_verdict == "READY_FOR_COMMIT_REVIEW"


class TestTestGateAgent:
    def test_allow_when_all_pass(self):
        vote = TestGateAgent().evaluate(_clean_state())
        assert vote.proposed_verdict == "READY_FOR_COMMIT_REVIEW"
        assert vote.confidence >= 0.9

    def test_hold_when_only_tests_fail(self):
        vote = TestGateAgent().evaluate(_clean_state(tests_results="FAIL", gates_results="PASS"))
        assert vote.proposed_verdict == "BUILD_HOLD"
        assert "TEST_GATE_INCOMPLETE" in vote.unknowns

    def test_hold_when_only_gates_fail(self):
        vote = TestGateAgent().evaluate(_clean_state(tests_results="PASS", gates_results="FAIL"))
        assert vote.proposed_verdict == "BUILD_HOLD"

    def test_block_when_both_fail(self):
        vote = TestGateAgent().evaluate(_clean_state(tests_results="FAIL", gates_results="FAIL"))
        assert vote.proposed_verdict == "BUILD_BLOCK"
        assert "GATE_FAILURE" in vote.contradictions

    def test_hold_on_partial(self):
        vote = TestGateAgent().evaluate(_clean_state(tests_results="PARTIAL"))
        assert vote.proposed_verdict == "BUILD_HOLD"

    def test_first_failure_in_risk_flags(self):
        vote = TestGateAgent().evaluate(_clean_state(tests_results="FAIL", first_failure="test_x::fail"))
        assert any("test_x::fail" in rf for rf in vote.risk_flags)

    def test_layer_is_interpretation(self):
        vote = TestGateAgent().evaluate(_clean_state())
        assert vote.layer == Layer.INTERPRETATION

    def test_unknown_results_pass(self):
        """UNKNOWN n'est pas FAIL — ne doit pas bloquer."""
        vote = TestGateAgent().evaluate(_clean_state(tests_results="UNKNOWN", gates_results="UNKNOWN"))
        assert vote.proposed_verdict == "READY_FOR_COMMIT_REVIEW"


class TestSessionIntegrityAgent:
    def test_allow_on_full_integrity(self):
        vote = SessionIntegrityAgent().evaluate(_clean_state())
        assert vote.proposed_verdict == "READY_FOR_COMMIT_REVIEW"
        assert vote.confidence >= 0.9

    def test_block_on_no_human_approval(self):
        vote = SessionIntegrityAgent().evaluate(_clean_state(human_approval_status="MISSING"))
        assert vote.proposed_verdict == "BUILD_BLOCK"
        assert "HUMAN_APPROVAL_MISSING" in vote.contradictions

    def test_hold_on_pending_approval(self):
        vote = SessionIntegrityAgent().evaluate(_clean_state(human_approval_status="PENDING"))
        assert vote.proposed_verdict in ("BUILD_HOLD",)
        assert "HUMAN_APPROVAL_PENDING" in vote.unknowns

    def test_block_on_no_worktree_isolation(self):
        vote = SessionIntegrityAgent().evaluate(_clean_state(worktree_isolated=False))
        assert vote.proposed_verdict == "BUILD_BLOCK"
        assert "WORKTREE_NOT_ISOLATED" in vote.contradictions

    def test_block_on_no_branch_isolation(self):
        vote = SessionIntegrityAgent().evaluate(_clean_state(branch_isolated=False))
        assert vote.proposed_verdict == "BUILD_BLOCK"
        assert "BRANCH_NOT_ISOLATED" in vote.contradictions

    def test_hold_on_missing_base_sha(self):
        vote = SessionIntegrityAgent().evaluate(_clean_state(base_sha=""))
        assert vote.proposed_verdict in ("BUILD_HOLD",)
        assert "BASE_SHA_MISSING" in vote.unknowns

    def test_block_on_wrong_decision_authority(self):
        vote = SessionIntegrityAgent().evaluate(_clean_state(decision_authority="HUMAN"))
        assert vote.proposed_verdict == "BUILD_BLOCK"
        assert "DECISION_AUTHORITY_VIOLATION" in vote.contradictions

    def test_layer_is_contradiction(self):
        vote = SessionIntegrityAgent().evaluate(_clean_state())
        assert vote.layer == Layer.CONTRADICTION

    def test_caller_contradictions_propagated(self):
        vote = SessionIntegrityAgent().evaluate(_clean_state(contradictions=["PRE_EXISTING_ISSUE"]))
        assert "PRE_EXISTING_ISSUE" in vote.contradictions


class TestCommitGuardAgent:
    def test_allow_when_nothing_committed(self):
        vote = CommitGuardAgent().evaluate(_clean_state())
        assert vote.proposed_verdict == "READY_FOR_COMMIT_REVIEW"
        assert vote.confidence >= 0.95

    def test_block_on_unauthorized_commit(self):
        vote = CommitGuardAgent().evaluate(_clean_state(commit_status="COMMITTED"))
        assert vote.proposed_verdict == "BUILD_BLOCK"
        assert "UNAUTHORIZED_COMMIT" in vote.contradictions

    def test_block_on_push(self):
        vote = CommitGuardAgent().evaluate(_clean_state(push_status="PUSHED"))
        assert "UNAUTHORIZED_PUSH" in vote.contradictions

    def test_block_on_merge(self):
        vote = CommitGuardAgent().evaluate(_clean_state(merge_status="MERGED"))
        assert "UNAUTHORIZED_MERGE" in vote.contradictions

    def test_block_when_auto_commit_enabled(self):
        vote = CommitGuardAgent().evaluate(_clean_state(auto_commit_disabled=False))
        assert vote.proposed_verdict == "BUILD_BLOCK"
        assert "AUTO_COMMIT_NOT_DISABLED" in vote.contradictions

    def test_block_when_auto_push_enabled(self):
        vote = CommitGuardAgent().evaluate(_clean_state(auto_push_disabled=False))
        assert "AUTO_PUSH_NOT_DISABLED" in vote.contradictions

    def test_block_when_auto_merge_enabled(self):
        vote = CommitGuardAgent().evaluate(_clean_state(auto_merge_disabled=False))
        assert "AUTO_MERGE_NOT_DISABLED" in vote.contradictions

    def test_layer_is_kernel(self):
        vote = CommitGuardAgent().evaluate(_clean_state())
        assert vote.layer == Layer.KERNEL

    def test_unknown_status_is_tolerated(self):
        vote = CommitGuardAgent().evaluate(_clean_state(
            commit_status="UNKNOWN", push_status="UNKNOWN", merge_status="UNKNOWN"
        ))
        assert vote.proposed_verdict == "READY_FOR_COMMIT_REVIEW"


# ---------------------------------------------------------------------------
# Groupe C — agrégation
# ---------------------------------------------------------------------------

class TestAggregateToolingBuild:
    def _votes_clean(self):
        return [a.evaluate(_clean_state()) for a in build_tooling_build_agents()]

    def test_aggregate_produces_domain_aggregate(self):
        from sigma.contracts import DomainAggregate
        agg = aggregate_tooling_build(self._votes_clean())
        assert isinstance(agg, DomainAggregate)

    def test_aggregate_clean_verdict(self):
        agg = aggregate_tooling_build(self._votes_clean())
        assert agg.market_verdict == "READY_FOR_COMMIT_REVIEW"

    def test_aggregate_clean_no_contradictions(self):
        agg = aggregate_tooling_build(self._votes_clean())
        assert agg.contradictions == []

    def test_aggregate_clean_confidence_high(self):
        agg = aggregate_tooling_build(self._votes_clean())
        assert agg.confidence >= 0.90

    def test_aggregate_block_on_contradictions(self):
        votes = [a.evaluate(_clean_state(protected_scope_status="VIOLATED")) for a in build_tooling_build_agents()]
        agg = aggregate_tooling_build(votes)
        assert agg.market_verdict == "BUILD_BLOCK"
        assert len(agg.contradictions) >= 1

    def test_aggregate_hold_on_scope_drift(self):
        votes = [a.evaluate(_clean_state(
            approved_scope=["a.py"],
            actual_touched_files=["a.py", "b.py"],
        )) for a in build_tooling_build_agents()]
        agg = aggregate_tooling_build(votes)
        assert agg.market_verdict in ("BUILD_HOLD", "BUILD_BLOCK")

    def test_aggregate_extra_metrics_decision_authority(self):
        agg = aggregate_tooling_build(self._votes_clean())
        assert agg.extra_metrics.get("decision_authority") == "KX108_ONLY"

    def test_aggregate_extra_metrics_emits_act_false(self):
        agg = aggregate_tooling_build(self._votes_clean())
        assert agg.extra_metrics.get("emits_act") is False

    def test_aggregate_four_votes(self):
        agg = aggregate_tooling_build(self._votes_clean())
        assert agg.extra_metrics.get("vote_count") == 4


# ---------------------------------------------------------------------------
# Groupe D — pipeline complet
# ---------------------------------------------------------------------------

class TestPipeline:
    def test_clean_state_gives_act(self):
        r = _run_pipeline(_clean_state())
        assert r["x108_gate"] == "ALLOW"

    def test_clean_domain_is_tooling_build(self):
        r = _run_pipeline(_clean_state())
        assert r["domain"] == "tooling_build"

    def test_protected_scope_gives_block(self):
        r = _run_pipeline(_clean_state(protected_scope_status="VIOLATED"))
        assert r["x108_gate"] == "BLOCK"

    def test_scope_drift_gives_hold_or_block(self):
        r = _run_pipeline(_clean_state(
            approved_scope=["a.py"],
            actual_touched_files=["a.py", "extra.py"],
        ))
        assert r["x108_gate"] in ("HOLD", "BLOCK")

    def test_no_human_approval_gives_block(self):
        r = _run_pipeline(_clean_state(human_approval_status="MISSING"))
        assert r["x108_gate"] == "BLOCK"

    def test_tests_failed_gives_hold_or_block(self):
        r = _run_pipeline(_clean_state(tests_results="FAIL", gates_results="PASS"))
        assert r["x108_gate"] in ("HOLD", "BLOCK")

    def test_unauthorized_commit_gives_block(self):
        r = _run_pipeline(_clean_state(commit_status="COMMITTED"))
        assert r["x108_gate"] == "BLOCK"

    def test_branch_not_isolated_gives_block(self):
        r = _run_pipeline(_clean_state(branch_isolated=False))
        assert r["x108_gate"] == "BLOCK"

    def test_auto_commit_enabled_gives_block(self):
        r = _run_pipeline(_clean_state(auto_commit_disabled=False))
        assert r["x108_gate"] == "BLOCK"

    def test_result_has_canonical_envelope_fields(self):
        r = _run_pipeline(_clean_state())
        assert "x108_gate" in r
        assert "market_verdict" in r
        assert "confidence" in r


# ---------------------------------------------------------------------------
# Groupe E — CLI run_pipeline.py
# ---------------------------------------------------------------------------

class TestCLI:
    def test_cli_clean_returns_allow(self):
        r = _cli_run(_cli_payload())
        assert r.get("x108_gate") == "ALLOW"

    def test_cli_missing_field_raises_error(self):
        p = _cli_payload()
        del p["session_id"]
        result = subprocess.run(
            [sys.executable, str(ROOT / "sigma" / "run_pipeline.py"), "tooling_build", json.dumps(p)],
            capture_output=True, text=True,
        )
        assert result.returncode != 0
        err = json.loads(result.stderr or result.stdout)
        assert "error" in err

    def test_cli_unknown_field_raises_error(self):
        p = _cli_payload()
        p["unknown_field_xyz"] = "oops"
        result = subprocess.run(
            [sys.executable, str(ROOT / "sigma" / "run_pipeline.py"), "tooling_build", json.dumps(p)],
            capture_output=True, text=True,
        )
        assert result.returncode != 0

    def test_validate_tooling_build_payload_ok(self):
        validate_tooling_build_payload(_cli_payload())

    def test_validate_missing_field(self):
        p = _cli_payload()
        del p["manifest_hash"]
        with pytest.raises(ValueError, match="manifest_hash"):
            validate_tooling_build_payload(p)

    def test_validate_missing_decision_authority(self):
        p = _cli_payload()
        del p["decision_authority"]
        with pytest.raises(ValueError, match="decision_authority"):
            validate_tooling_build_payload(p)

    def test_validate_wrong_decision_authority(self):
        p = _cli_payload()
        p["decision_authority"] = "HUMAN"
        with pytest.raises(ValueError, match="KX108_ONLY"):
            validate_tooling_build_payload(p)

    def test_validate_wrong_type_bool(self):
        p = _cli_payload()
        p["worktree_isolated"] = "yes"
        with pytest.raises(ValueError, match="boolean"):
            validate_tooling_build_payload(p)

    def test_validate_wrong_type_list(self):
        p = _cli_payload()
        p["approved_scope"] = "not-a-list"
        with pytest.raises(ValueError, match="list"):
            validate_tooling_build_payload(p)

    def test_validate_missing_branch_isolated(self):
        p = _cli_payload()
        del p["branch_isolated"]
        with pytest.raises(ValueError, match="branch_isolated"):
            validate_tooling_build_payload(p)


# ---------------------------------------------------------------------------
# Groupe F — invariants de gouvernance
# ---------------------------------------------------------------------------

class TestGovernanceInvariants:
    def test_decision_authority_kx108_only_in_aggregate(self):
        votes = [a.evaluate(_clean_state()) for a in build_tooling_build_agents()]
        agg = aggregate_tooling_build(votes)
        assert agg.extra_metrics["decision_authority"] == "KX108_ONLY"

    def test_emits_act_false_in_aggregate(self):
        votes = [a.evaluate(_clean_state()) for a in build_tooling_build_agents()]
        agg = aggregate_tooling_build(votes)
        assert agg.extra_metrics["emits_act"] is False

    def test_clean_session_verdict_is_ready_for_commit_review_not_commit(self):
        r = _run_pipeline(_clean_state())
        assert "COMMIT" not in r.get("x108_gate", "")
        assert r.get("market_verdict") == "READY_FOR_COMMIT_REVIEW"

    def test_kernel_agent_has_highest_layer(self):
        agents = build_tooling_build_agents()
        layers = [int(a.evaluate(_clean_state()).layer) for a in agents]
        assert max(layers) == int(Layer.KERNEL)

    def test_no_auto_commit_field_in_result(self):
        r = _run_pipeline(_clean_state())
        forbidden = {"auto_commit", "auto_push", "auto_merge"}
        assert not forbidden.intersection(r.keys())

    def test_agents_do_not_emit_act(self):
        for agent in build_tooling_build_agents():
            vote = agent.evaluate(_clean_state())
            assert vote.proposed_verdict != "ACT", f"{agent.agent_id} ne doit pas émettre ACT"

    def test_pipeline_decision_authority_kx108_only(self):
        r = _run_pipeline(_clean_state())
        metrics = r.get("metrics", {})
        assert metrics.get("decision_authority") == "KX108_ONLY"

    def test_pipeline_emits_act_false(self):
        r = _run_pipeline(_clean_state())
        metrics = r.get("metrics", {})
        assert metrics.get("emits_act") is False


# ---------------------------------------------------------------------------
# Groupe G — fixtures intégration (ACT / HOLD / BLOCK)
# ---------------------------------------------------------------------------

class TestIntegrationFixtures:
    def test_fixture_act_clean_session_35d45cb9(self):
        """Fixture ACT : session 35d45cb9 avec tous les flags propres."""
        state = _clean_state(session_id="35d45cb9", base_sha="6a16d02")
        r = _run_pipeline(state)
        assert r["x108_gate"] == "ALLOW", f"Attendu ALLOW, obtenu: {r['x108_gate']}"
        assert r["market_verdict"] == "READY_FOR_COMMIT_REVIEW"
        assert r["domain"] == "tooling_build"

    def test_fixture_hold_scope_drift(self):
        """Fixture HOLD : scope non exact, aucune contradiction critique."""
        state = _clean_state(
            approved_scope=["sigma/contracts.py"],
            actual_touched_files=["sigma/contracts.py", "sigma/extra.py"],
            protected_scope_status="CLEAN",
            human_approval_status="APPROVED",
            worktree_isolated=True,
            branch_isolated=True,
            tests_results="PASS",
            gates_results="PASS",
            commit_status="NOT_COMMITTED",
            push_status="NOT_PUSHED",
            merge_status="NOT_MERGED",
        )
        r = _run_pipeline(state)
        assert r["x108_gate"] in ("HOLD", "BLOCK")

    def test_fixture_block_protected_scope(self):
        """Fixture BLOCK : chemin protégé touché → BLOCK absolu."""
        state = _clean_state(protected_scope_status="VIOLATED")
        r = _run_pipeline(state)
        assert r["x108_gate"] == "BLOCK"

    def test_fixture_block_no_approval(self):
        """Fixture BLOCK : approbation humaine manquante."""
        state = _clean_state(human_approval_status="MISSING")
        r = _run_pipeline(state)
        assert r["x108_gate"] == "BLOCK"

    def test_fixture_block_unauthorized_push(self):
        """Fixture BLOCK : push non autorisé détecté par CommitGuardAgent (Layer KERNEL)."""
        state = _clean_state(push_status="PUSHED")
        r = _run_pipeline(state)
        assert r["x108_gate"] == "BLOCK"

    def test_fixture_block_auto_commit_enabled(self):
        """Fixture BLOCK : garde-fou auto_commit désactivé."""
        state = _clean_state(auto_commit_disabled=False)
        r = _run_pipeline(state)
        assert r["x108_gate"] == "BLOCK"

    def test_fixture_block_branch_not_isolated(self):
        """Fixture BLOCK : branche non isolée."""
        state = _clean_state(branch_isolated=False)
        r = _run_pipeline(state)
        assert r["x108_gate"] == "BLOCK"

    def test_fixture_hold_tests_partial(self):
        """Fixture HOLD : tests partiels."""
        state = _clean_state(tests_results="PARTIAL")
        r = _run_pipeline(state)
        assert r["x108_gate"] in ("HOLD", "BLOCK")

    def test_fixture_cli_act_clean(self):
        """Fixture CLI ACT : payload complet via CLI."""
        r = _cli_run(_cli_payload())
        assert r.get("x108_gate") == "ALLOW"

    def test_fixture_cli_block_missing_approval(self):
        """Fixture CLI BLOCK : approbation manquante."""
        r = _cli_run(_cli_payload(human_approval_status="MISSING"))
        assert r.get("x108_gate") == "BLOCK"

    def test_fixture_cli_hold_pending_approval(self):
        """Fixture CLI HOLD : approbation en attente."""
        r = _cli_run(_cli_payload(human_approval_status="PENDING"))
        assert r.get("x108_gate") in ("HOLD", "BLOCK")
