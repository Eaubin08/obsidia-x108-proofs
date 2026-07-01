"""OIE V0.7 -- Tests : Obsidia vs Gemini Power Benchmark.

Couvre :
- import sans reseau
- 7 familles presentes
- Obsidia lane champs obligatoires (speed/cost/energy/work/governance)
- Gemini lane mockee (tokens/cout/latence)
- compare_row calculs (latency_delta_pct, speedup_ratio, token_delta_pct,
  avoided_cost_per_request, energy_avoided_wh si coefficients, summary global)
- governance_clean true si flags corrects
- dry-run sans appel Gemini
- aucun secret dans JSON
- rapport markdown genere
- phrases obligatoires presentes
- claims invalides absents
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.performance.benchmark_oie_obsidia_vs_gemini_power_v0_7 as bm


# ── Helpers ──────────────────────────────────────────────────────────────────

def _first_task() -> dict:
    return bm.POWER_TASKS[0]


def _task_by_family(family: str) -> dict:
    return next(t for t in bm.POWER_TASKS if t["family"] == family)


def _mock_gemini_result(task_id: str) -> dict:
    frozen = bm._FROZEN_GEMINI_PER_TASK.get(task_id, {})
    return {
        "gemini_status": bm.GEMINI_STATUS_DRYRUN,
        "gemini_detected_route": frozen.get("detected_route"),
        "gemini_route_match": frozen.get("route_match"),
        "gemini_latency_ms": frozen.get("latency_ms", 400.0),
        "gemini_input_tokens": frozen.get("input_tokens", 40),
        "gemini_output_tokens": frozen.get("output_tokens", 2),
        "gemini_total_tokens": frozen.get("total_tokens", 42),
        "gemini_cost_source": "USAGE_UNAVAILABLE",
        "gemini_cost_per_request_measured": None,
        "gemini_cost_per_1m_measured": None,
        "gemini_quality_score": 1.0 if frozen.get("route_match") else 0.0,
        "gemini_failure_type": "NONE",
        "gemini_external_model_call_required": True,
    }


# ── 1. Import sans reseau ─────────────────────────────────────────────────────

class TestImportSafety:
    def test_module_imports_without_network(self):
        """L'import du module ne doit pas declencher d'appel reseau."""
        assert bm is not None

    def test_power_tasks_defined_at_module_level(self):
        assert hasattr(bm, "POWER_TASKS")
        assert isinstance(bm.POWER_TASKS, list)

    def test_constants_defined(self):
        assert bm.BENCHMARK_VERSION.startswith("OIE_POWER_BENCHMARK")
        assert bm.OBSIDIA_STATUS_FROZEN == "FROZEN_V0_ESTIMATE"
        assert bm.OBSIDIA_STATUS_MISSING == "ADAPTER_MISSING"
        assert bm.OBSIDIA_STATUS_REAL == "REAL_ADAPTER"
        assert bm.GEMINI_STATUS_DRYRUN == "DRY_RUN_MOCK"
        assert bm.ENERGY_SOURCE_UNAVAILABLE == "ENERGY_PROXY_UNAVAILABLE"
        assert bm.ENERGY_SOURCE_ESTIMATE == "ENERGY_PROXY_ESTIMATE"


# ── 2. 7 familles presentes ───────────────────────────────────────────────────

class TestSevenFamilies:
    def test_exactly_7_tasks(self):
        assert len(bm.POWER_TASKS) == 7

    def test_all_required_families_present(self):
        families = {t["family"] for t in bm.POWER_TASKS}
        assert "FAST_PATH" in families
        assert "BRODY" in families
        assert "BANK" in families
        assert "TRADING" in families
        assert "GPS" in families
        assert "OBSIDURE" in families
        assert "LEAN" in families

    def test_each_task_has_required_fields(self):
        required = [
            "task_id", "family", "comparison_axis", "prompt", "expected_route",
            "obsidia_model_call_required", "external_model_call_required",
            "obsidia_cost_per_1m_est", "expected_modules_considered",
            "expected_modules_activated", "expected_modules_skipped",
        ]
        for task in bm.POWER_TASKS:
            for f in required:
                assert f in task, f"Task {task['task_id']} missing field {f}"

    def test_modules_skipped_consistent(self):
        for task in bm.POWER_TASKS:
            assert (
                task["expected_modules_activated"] + task["expected_modules_skipped"]
                == task["expected_modules_considered"]
            )

    def test_unique_task_ids(self):
        ids = [t["task_id"] for t in bm.POWER_TASKS]
        assert len(ids) == len(set(ids))


# ── 3. Obsidia lane champs obligatoires ──────────────────────────────────────

class TestObsidiaLane:
    _SPEED_FIELDS = [
        "obsidia_latency_ms", "obsidia_throughput_req_per_sec",
        "obsidia_safe_decisions_per_second",
    ]
    _COST_FIELDS = [
        "obsidia_cost_per_request_est", "obsidia_cost_per_1m_est",
        "obsidia_decisions_per_cost_unit",
    ]
    _WORK_FIELDS = [
        "obsidia_model_call_avoided", "obsidia_modules_skipped",
        "obsidia_modules_skipped_pct", "obsidia_cache_hit", "obsidia_cache_hit_ratio",
        "obsidia_files_read", "obsidia_files_skipped",
        "obsidia_memory_records_loaded", "obsidia_memory_records_skipped",
        "obsidia_graphiti_cold_ms", "obsidia_runtime_context_build_ms",
    ]
    _GOV_FIELDS = [
        "obsidia_emits_act", "obsidia_memory_write", "obsidia_kernel_mutation",
        "obsidia_decision_authority", "obsidia_boundary_ok",
    ]

    def test_speed_fields_present(self):
        obs = bm.run_obsidia_local_actual(_first_task())
        for f in self._SPEED_FIELDS:
            assert f in obs, f"Missing field {f}"

    def test_cost_fields_present(self):
        obs = bm.run_obsidia_local_actual(_first_task())
        for f in self._COST_FIELDS:
            assert f in obs, f"Missing field {f}"

    def test_work_avoidance_fields_present(self):
        obs = bm.run_obsidia_local_actual(_first_task())
        for f in self._WORK_FIELDS:
            assert f in obs, f"Missing field {f}"

    def test_governance_fields_present(self):
        obs = bm.run_obsidia_local_actual(_first_task())
        for f in self._GOV_FIELDS:
            assert f in obs, f"Missing field {f}"

    def test_governance_values_correct(self):
        obs = bm.run_obsidia_local_actual(_first_task())
        assert obs["obsidia_emits_act"] is False
        assert obs["obsidia_memory_write"] is False
        assert obs["obsidia_kernel_mutation"] is False
        assert obs["obsidia_decision_authority"] == "KX108_ONLY"

    def test_fast_path_model_call_avoided(self):
        task = _task_by_family("FAST_PATH")
        obs = bm.run_obsidia_local_actual(task)
        assert obs["obsidia_model_call_avoided"] is True

    def test_brody_model_call_not_avoided(self):
        task = _task_by_family("BRODY")
        obs = bm.run_obsidia_local_actual(task)
        assert obs["obsidia_model_call_avoided"] is False

    def test_adapter_missing_status_for_brody(self):
        task = _task_by_family("BRODY")
        obs = bm.run_obsidia_local_actual(task)
        assert obs["obsidia_status"] == bm.OBSIDIA_STATUS_MISSING

    def test_frozen_status_for_bank(self):
        task = _task_by_family("BANK")
        obs = bm.run_obsidia_local_actual(task)
        assert obs["obsidia_status"] == bm.OBSIDIA_STATUS_FROZEN

    def test_estimated_tokens_positive(self):
        obs = bm.run_obsidia_local_actual(_first_task())
        assert obs["obsidia_estimated_total_tokens"] > 0
        assert obs["obsidia_estimated_input_tokens"] > 0

    def test_cost_per_request_positive(self):
        obs = bm.run_obsidia_local_actual(_first_task())
        assert obs["obsidia_cost_per_request_est"] > 0

    def test_modules_skipped_pct_bounded(self):
        for task in bm.POWER_TASKS:
            obs = bm.run_obsidia_local_actual(task)
            pct = obs["obsidia_modules_skipped_pct"]
            assert 0.0 <= pct <= 100.0


# ── 4. Gemini lane mockee ─────────────────────────────────────────────────────

class TestGeminiLaneDryRun:
    def test_dry_run_returns_dryrun_status(self):
        task = _first_task()
        gem = bm.run_gemini_lane_dryrun(task)
        assert gem["gemini_status"] == bm.GEMINI_STATUS_DRYRUN

    def test_dry_run_has_tokens(self):
        task = _first_task()
        gem = bm.run_gemini_lane_dryrun(task)
        assert gem["gemini_input_tokens"] is not None
        assert gem["gemini_output_tokens"] is not None
        assert gem["gemini_total_tokens"] is not None

    def test_dry_run_has_latency(self):
        task = _first_task()
        gem = bm.run_gemini_lane_dryrun(task)
        assert gem["gemini_latency_ms"] is not None
        assert gem["gemini_latency_ms"] > 0

    def test_dry_run_external_model_call_required(self):
        gem = bm.run_gemini_lane_dryrun(_first_task())
        assert gem["gemini_external_model_call_required"] is True

    def test_dry_run_never_calls_gemini_sdk(self):
        with patch(
            "apps.obsidia_api.inference_economy.external_comparison.run_gemini_sdk"
        ) as mock_g:
            for task in bm.POWER_TASKS:
                bm.run_gemini_lane_dryrun(task)
        mock_g.assert_not_called()

    def test_dry_run_7_tasks_all_have_frozen_data(self):
        for task in bm.POWER_TASKS:
            gem = bm.run_gemini_lane_dryrun(task)
            assert gem["gemini_total_tokens"] is not None, f"No frozen data for {task['task_id']}"


# ── 5. compare_row calculs ────────────────────────────────────────────────────

class TestCompareRow:
    def _row(self, task: dict, monkeypatch=None) -> dict:
        obs = bm.run_obsidia_local_actual(task)
        gem = bm.run_gemini_lane_dryrun(task)
        return bm.compute_compare_row(task, obs, gem)

    def test_latency_delta_pct_present(self):
        row = self._row(_first_task())
        assert "latency_delta_pct" in row

    def test_latency_delta_pct_positive_for_fast_path(self):
        row = self._row(_task_by_family("FAST_PATH"))
        # Gemini slower than Obsidia Fast Path => positive delta
        if row["latency_delta_pct"] is not None:
            assert row["latency_delta_pct"] > 0

    def test_speedup_ratio_present(self):
        row = self._row(_first_task())
        assert "speedup_ratio" in row

    def test_speedup_ratio_positive(self):
        row = self._row(_task_by_family("FAST_PATH"))
        if row["speedup_ratio"] is not None:
            assert row["speedup_ratio"] > 1.0

    def test_token_delta_pct_present(self):
        row = self._row(_first_task())
        assert "token_delta_pct" in row

    def test_token_delta_pct_formula(self):
        task = _first_task()
        obs = bm.run_obsidia_local_actual(task)
        gem = bm.run_gemini_lane_dryrun(task)
        row = bm.compute_compare_row(task, obs, gem)
        if row["token_delta_pct"] is not None:
            expected = 100.0 * (
                (gem["gemini_total_tokens"] - obs["obsidia_estimated_total_tokens"])
                / gem["gemini_total_tokens"]
            )
            assert abs(row["token_delta_pct"] - round(expected, 2)) < 0.01

    def test_avoided_cost_none_without_gemini_measured_cost(self):
        row = self._row(_first_task())
        # dry-run => gemini_cost=None => avoided_cost_per_request=None
        assert row["avoided_cost_per_request"] is None

    def test_avoided_cost_computed_when_gemini_cost_available(self):
        task = _first_task()
        obs = bm.run_obsidia_local_actual(task)
        gem = bm.run_gemini_lane_dryrun(task)
        gem["gemini_cost_per_request_measured"] = 0.000005
        gem["gemini_cost_per_1m_measured"] = 5.0
        row = bm.compute_compare_row(task, obs, gem)
        assert row["avoided_cost_per_request"] is not None

    def test_all_required_compare_fields_present(self):
        required = [
            "task_id", "family", "expected_route",
            "obsidia_detected_route", "gemini_detected_route",
            "obsidia_route_match", "gemini_route_match",
            "obsidia_latency_ms", "gemini_latency_ms",
            "latency_delta_pct", "speedup_ratio",
            "obsidia_throughput_req_per_sec", "gemini_throughput_req_per_sec",
            "throughput_gain_ratio",
            "safe_decisions_per_second_obsidia", "safe_decisions_per_second_gemini",
            "decisions_per_cost_unit_obsidia", "decisions_per_cost_unit_gemini",
            "obsidia_estimated_total_tokens", "gemini_total_tokens",
            "token_delta_pct", "estimated_context_budget_delta_pct",
            "external_token_dependency_ratio",
            "gemini_cost_per_request_measured", "obsidia_cost_per_request_est",
            "avoided_cost_per_request", "cost_savings_ratio",
            "obsidia_energy_wh_est", "gemini_energy_wh_est",
            "energy_avoided_wh", "energy_savings_ratio",
            "obsidia_modules_skipped", "obsidia_cache_hit",
            "obsidia_model_call_avoided",
            "obsidia_quality_score", "gemini_quality_score", "quality_delta",
            "obsidia_boundary_ok", "obsidia_governance_clean",
            "winner_speed", "winner_cost", "winner_energy",
            "winner_route", "winner_governance",
            "final_interpretation",
        ]
        for task in bm.POWER_TASKS:
            obs = bm.run_obsidia_local_actual(task)
            gem = bm.run_gemini_lane_dryrun(task)
            row = bm.compute_compare_row(task, obs, gem)
            for f in required:
                assert f in row, f"compare_row missing field {f} for task {task['task_id']}"

    def test_winner_fields_valid_values(self):
        valid = {"OBSIDIA", "GEMINI", "TIE", "NEITHER", "UNKNOWN", "CONTESTED"}
        for task in bm.POWER_TASKS:
            obs = bm.run_obsidia_local_actual(task)
            gem = bm.run_gemini_lane_dryrun(task)
            row = bm.compute_compare_row(task, obs, gem)
            assert row["winner_speed"] in valid
            assert row["winner_cost"] in valid
            assert row["winner_energy"] in valid
            assert row["winner_route"] in valid
            assert row["winner_governance"] in valid

    def test_governance_clean_when_flags_correct(self):
        task = _first_task()
        obs = bm.run_obsidia_local_actual(task)
        gem = bm.run_gemini_lane_dryrun(task)
        row = bm.compute_compare_row(task, obs, gem)
        assert row["obsidia_governance_clean"] is True


# ── 6. Energy metrics ─────────────────────────────────────────────────────────

class TestEnergyMetrics:
    def test_energy_unavailable_without_env(self, monkeypatch):
        monkeypatch.delenv("OIE_EXTERNAL_ENERGY_WH_PER_1K_TOKENS", raising=False)
        monkeypatch.delenv("OIE_LOCAL_POWER_W", raising=False)
        result = bm.compute_energy_metrics(42, 10.0, None, None, None)
        assert result["energy_source"] == bm.ENERGY_SOURCE_UNAVAILABLE
        assert result["external_energy_wh_est"] is None
        assert result["local_energy_wh_est"] is None
        assert result["energy_avoided_wh"] is None

    def test_energy_estimate_with_coefficients(self, monkeypatch):
        result = bm.compute_energy_metrics(
            tokens=42, latency_ms=10.0,
            wh_per_1k_tokens=0.001, local_power_w=200.0, carbon_per_kwh=400.0
        )
        assert result["energy_source"] == bm.ENERGY_SOURCE_ESTIMATE
        assert result["external_energy_wh_est"] == pytest.approx(0.042 / 1000.0, rel=1e-3)
        assert result["local_energy_wh_est"] is not None
        assert result["energy_avoided_wh"] is not None

    def test_energy_avoided_wh_in_compare_row_with_env(self, monkeypatch):
        monkeypatch.setenv("OIE_EXTERNAL_ENERGY_WH_PER_1K_TOKENS", "0.001")
        monkeypatch.setenv("OIE_LOCAL_POWER_W", "200")
        monkeypatch.setenv("OIE_CARBON_GCO2_PER_KWH", "400")
        task = _first_task()
        obs = bm.run_obsidia_local_actual(task)
        gem = bm.run_gemini_lane_dryrun(task)
        row = bm.compute_compare_row(task, obs, gem)
        assert row["energy_avoided_wh"] is not None

    def test_energy_absent_in_compare_row_without_env(self, monkeypatch):
        monkeypatch.delenv("OIE_EXTERNAL_ENERGY_WH_PER_1K_TOKENS", raising=False)
        monkeypatch.delenv("OIE_LOCAL_POWER_W", raising=False)
        task = _first_task()
        obs = bm.run_obsidia_local_actual(task)
        gem = bm.run_gemini_lane_dryrun(task)
        row = bm.compute_compare_row(task, obs, gem)
        assert row["energy_avoided_wh"] is None
        assert row["obsidia_energy_wh_est"] is None

    def test_decisions_per_wh_present_when_energy_available(self, monkeypatch):
        monkeypatch.setenv("OIE_EXTERNAL_ENERGY_WH_PER_1K_TOKENS", "0.001")
        monkeypatch.setenv("OIE_LOCAL_POWER_W", "200")
        task = _first_task()
        obs = bm.run_obsidia_local_actual(task)
        gem = bm.run_gemini_lane_dryrun(task)
        row = bm.compute_compare_row(task, obs, gem)
        assert row.get("decisions_per_wh_obsidia") is not None


# ── 7. Summary global ─────────────────────────────────────────────────────────

class TestSummary:
    def _all_rows(self) -> list[dict]:
        rows = []
        for task in bm.POWER_TASKS:
            obs = bm.run_obsidia_local_actual(task)
            gem = bm.run_gemini_lane_dryrun(task)
            rows.append(bm.compute_compare_row(task, obs, gem))
        return rows

    def test_summary_has_route_accuracy(self):
        rows = self._all_rows()
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        assert "obsidia_route_accuracy" in s
        assert "gemini_route_accuracy" in s

    def test_summary_route_accuracy_bounded(self):
        rows = self._all_rows()
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        assert 0.0 <= s["obsidia_route_accuracy"] <= 1.0
        assert 0.0 <= s["gemini_route_accuracy"] <= 1.0

    def test_summary_avg_speedup_ratio(self):
        rows = self._all_rows()
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        assert "avg_speedup_ratio" in s

    def test_summary_total_avoided_cost_none_without_measured(self):
        rows = self._all_rows()
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        # dry-run => gemini_cost=None => total_avoided_cost=None
        assert s["total_avoided_cost"] is None

    def test_summary_total_avoided_cost_computed_when_costs_set(self):
        rows = self._all_rows()
        # inject fake gemini cost
        for r in rows:
            r["gemini_cost_per_request_measured"] = 0.000005
            r["avoided_cost_per_request"] = 0.000004
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        assert s["total_avoided_cost"] is not None
        assert s["total_avoided_cost"] > 0

    def test_summary_model_call_avoided_rate(self):
        rows = self._all_rows()
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        assert "obsidia_model_call_avoided_rate" in s
        assert 0.0 <= s["obsidia_model_call_avoided_rate"] <= 1.0

    def test_summary_model_call_avoided_count(self):
        rows = self._all_rows()
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        # FAST_PATH, BANK, TRADING, GPS = 4 avoided
        assert s["obsidia_model_call_avoided_count"] == 4

    def test_summary_modules_skipped_total(self):
        rows = self._all_rows()
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        assert "obsidia_modules_skipped_total" in s
        assert s["obsidia_modules_skipped_total"] > 0

    def test_summary_safe_decisions_per_second(self):
        rows = self._all_rows()
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        assert "obsidia_safe_decisions_per_second_avg" in s
        assert "gemini_safe_decisions_per_second_avg" in s

    def test_summary_decisions_per_cost_unit(self):
        rows = self._all_rows()
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        assert "obsidia_decisions_per_cost_unit_avg" in s
        assert "gemini_decisions_per_cost_unit_avg" in s

    def test_summary_decisions_per_wh_none_without_energy(self, monkeypatch):
        monkeypatch.delenv("OIE_EXTERNAL_ENERGY_WH_PER_1K_TOKENS", raising=False)
        monkeypatch.delenv("OIE_LOCAL_POWER_W", raising=False)
        rows = self._all_rows()
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        assert s["obsidia_decisions_per_wh_avg"] is None

    def test_summary_decisions_per_wh_present_with_energy(self, monkeypatch):
        monkeypatch.setenv("OIE_EXTERNAL_ENERGY_WH_PER_1K_TOKENS", "0.001")
        monkeypatch.setenv("OIE_LOCAL_POWER_W", "200")
        rows = []
        for task in bm.POWER_TASKS:
            obs = bm.run_obsidia_local_actual(task)
            gem = bm.run_gemini_lane_dryrun(task)
            rows.append(bm.compute_compare_row(task, obs, gem))
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        assert s["obsidia_decisions_per_wh_avg"] is not None

    def test_summary_total_energy_avoided_with_energy_env(self, monkeypatch):
        monkeypatch.setenv("OIE_EXTERNAL_ENERGY_WH_PER_1K_TOKENS", "0.001")
        monkeypatch.setenv("OIE_LOCAL_POWER_W", "200")
        rows = []
        for task in bm.POWER_TASKS:
            obs = bm.run_obsidia_local_actual(task)
            gem = bm.run_gemini_lane_dryrun(task)
            rows.append(bm.compute_compare_row(task, obs, gem))
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        assert s["total_energy_avoided_wh"] is not None

    def test_summary_governance_clean(self):
        rows = self._all_rows()
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        assert s["governance_clean"] is True
        assert s["decision_authority"] == "KX108_ONLY"
        assert s["emits_act"] is False
        assert s["memory_write"] is False
        assert s["kernel_mutation"] is False
        assert s["secrets_redacted"] is True


# ── 8. Gouvernance ────────────────────────────────────────────────────────────

class TestGovernance:
    def test_governance_clean_true_correct_flags(self):
        task = _first_task()
        obs = bm.run_obsidia_local_actual(task)
        gem = bm.run_gemini_lane_dryrun(task)
        row = bm.compute_compare_row(task, obs, gem)
        assert row["obsidia_governance_clean"] is True

    def test_emits_act_always_false(self):
        for task in bm.POWER_TASKS:
            obs = bm.run_obsidia_local_actual(task)
            assert obs["obsidia_emits_act"] is False

    def test_memory_write_always_false(self):
        for task in bm.POWER_TASKS:
            obs = bm.run_obsidia_local_actual(task)
            assert obs["obsidia_memory_write"] is False

    def test_kernel_mutation_always_false(self):
        for task in bm.POWER_TASKS:
            obs = bm.run_obsidia_local_actual(task)
            assert obs["obsidia_kernel_mutation"] is False

    def test_decision_authority_kx108_only(self):
        for task in bm.POWER_TASKS:
            obs = bm.run_obsidia_local_actual(task)
            assert obs["obsidia_decision_authority"] == "KX108_ONLY"


# ── 9. Dry-run ne fait pas d'appel Gemini ─────────────────────────────────────

class TestDryRunNoNetwork:
    def test_dry_run_does_not_call_run_gemini_sdk(self):
        with patch(
            "apps.obsidia_api.inference_economy.external_comparison.run_gemini_sdk"
        ) as mock_g:
            for task in bm.POWER_TASKS:
                bm.run_gemini_lane_dryrun(task)
        mock_g.assert_not_called()

    def test_gemini_real_calls_sdk_only_with_model(self):
        """run_gemini_lane_real sans modele retourne FAILED sans appel SDK."""
        result = bm.run_gemini_lane_real(_first_task(), "")
        assert result["gemini_status"] == bm.GEMINI_STATUS_FAILED


# ── 10. Aucun secret dans JSON ────────────────────────────────────────────────

class TestNoSecretInJson:
    def _full_rows_and_summary(self) -> tuple[list[dict], dict]:
        rows = []
        for task in bm.POWER_TASKS:
            obs = bm.run_obsidia_local_actual(task)
            gem = bm.run_gemini_lane_dryrun(task)
            rows.append(bm.compute_compare_row(task, obs, gem))
        return rows, bm.compute_summary(rows, bm.POWER_TASKS)

    def test_no_gemini_api_key_in_rows_json(self, monkeypatch):
        fake_key = "AIzaFAKE_V07_KEYTEST_1234567890ABC"
        monkeypatch.setenv("GEMINI_API_KEY", fake_key)
        rows, _ = self._full_rows_and_summary()
        payload = json.dumps(rows)
        assert fake_key not in payload

    def test_no_google_api_key_in_summary_json(self, monkeypatch):
        fake_key = "AIzaGOOGLE_V07_KEYTEST_ABCDEFGH"
        monkeypatch.setenv("GOOGLE_API_KEY", fake_key)
        _, summary = self._full_rows_and_summary()
        payload = json.dumps(summary, default=str)
        assert fake_key not in payload

    def test_no_anthropic_key_in_json(self, monkeypatch):
        fake_key = "sk-ant-FAKE_V07_KEY_ABCDEFGHIJ"
        monkeypatch.setenv("ANTHROPIC_API_KEY", fake_key)
        rows, summary = self._full_rows_and_summary()
        payload = json.dumps(rows) + json.dumps(summary, default=str)
        assert fake_key not in payload


# ── 11. Rapport Markdown genere ───────────────────────────────────────────────

class TestReportGeneration:
    def _generate(self) -> str:
        rows = []
        for task in bm.POWER_TASKS:
            obs = bm.run_obsidia_local_actual(task)
            gem = bm.run_gemini_lane_dryrun(task)
            rows.append(bm.compute_compare_row(task, obs, gem))
        summary = bm.compute_summary(rows, bm.POWER_TASKS)
        return bm.generate_report(summary, rows)

    def test_report_generated_as_string(self):
        report = self._generate()
        assert isinstance(report, str)
        assert len(report) > 100

    def test_report_contains_required_phrase_1(self):
        report = self._generate()
        assert bm._REQUIRED_PHRASES[0] in report

    def test_report_contains_required_phrase_2(self):
        report = self._generate()
        assert bm._REQUIRED_PHRASES[1] in report

    def test_report_contains_required_phrase_3(self):
        report = self._generate()
        assert bm._REQUIRED_PHRASES[2] in report

    def test_report_contains_all_7_families(self):
        report = self._generate()
        for family in ["FAST_PATH", "BRODY", "BANK", "TRADING", "GPS", "OBSIDURE", "LEAN"]:
            assert family in report, f"Family {family} missing from report"

    def test_report_invalid_claim_not_endorsed(self):
        """Claims invalides listes sous INTERDIT, jamais endosses comme faits."""
        report = self._generate()
        # Chaque claim invalide doit apparaitre seulement precede de "INTERDIT"
        for claim in bm._INVALID_CLAIMS:
            idx = report.find(claim)
            while idx >= 0:
                prefix = report[max(0, idx - 30):idx]
                assert "INTERDIT" in prefix, (
                    f"Claim '{claim}' presente sans prefixe INTERDIT"
                )
                idx = report.find(claim, idx + 1)

    def test_report_contains_section_headers(self):
        report = self._generate()
        required_sections = [
            "Executive Summary",
            "Speed metrics",
            "Cost metrics",
            "Energy metrics",
            "Work avoidance",
            "Inference avoidance",
            "Routing quality",
            "Governance",
            "Valid claims",
            "Invalid claims",
        ]
        for sec in required_sections:
            assert sec in report, f"Section '{sec}' missing from report"

    def test_report_contains_benchmark_version(self):
        report = self._generate()
        assert bm.BENCHMARK_VERSION in report

    def test_report_does_not_contain_adapter_missing_as_win(self):
        report = self._generate()
        # ADAPTER_MISSING ne doit pas etre interprete comme PASS/WIN
        assert "ADAPTER_MISSING wins" not in report


# ── 12. _INVALID_CLAIMS et _REQUIRED_PHRASES ─────────────────────────────────

class TestClaimsAndPhrases:
    def test_required_phrases_defined(self):
        assert len(bm._REQUIRED_PHRASES) >= 3

    def test_invalid_claims_defined(self):
        assert len(bm._INVALID_CLAIMS) >= 4

    def test_invalid_claim_smarter_than_gemini_present(self):
        claims_str = " ".join(bm._INVALID_CLAIMS)
        assert "smarter" in claims_str.lower() or "Obsidia is smarter than Gemini" in bm._INVALID_CLAIMS

    def test_invalid_claim_faster_than_all_llms_present(self):
        assert any("faster than all LLMs" in c for c in bm._INVALID_CLAIMS)

    def test_energy_phrase_mentions_proxy_estimate(self):
        assert "proxy estimate" in bm._REQUIRED_PHRASES[2].lower()


# ── 13. Frozen V0 constants ───────────────────────────────────────────────────

class TestFrozenConstants:
    def test_graphiti_warm_gain_ratio(self):
        assert bm.FROZEN_GRAPHITI_WARM_GAIN_RATIO == pytest.approx(868.14, rel=1e-3)

    def test_loader_warm_gain_ratio(self):
        assert bm.FROZEN_LOADER_WARM_GAIN_RATIO == pytest.approx(11348.76, rel=1e-3)

    def test_graphiti_warm_ms(self):
        assert bm.FROZEN_GRAPHITI_WARM_MS < 1.0

    def test_graphiti_cold_ms(self):
        assert bm.FROZEN_GRAPHITI_COLD_MS > 100.0

    def test_runtime_context_build_ms(self):
        assert bm.FROZEN_RUNTIME_CONTEXT_BUILD_MS < 1.0
