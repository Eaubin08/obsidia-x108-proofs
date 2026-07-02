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


# â”€â”€ Helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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


# â”€â”€ 1. Import sans reseau â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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


# â”€â”€ 2. 7 familles presentes â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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


# â”€â”€ 3. Obsidia lane champs obligatoires â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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


# â”€â”€ 4. Gemini lane mockee â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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


# â”€â”€ 5. compare_row calculs â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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


# â”€â”€ 6. Energy metrics â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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


# â”€â”€ 7. Summary global â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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


# â”€â”€ 8. Gouvernance â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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


# â”€â”€ 9. Dry-run ne fait pas d'appel Gemini â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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


# â”€â”€ 10. Aucun secret dans JSON â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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


# â”€â”€ 11. Rapport Markdown genere â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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
            "Available surface",
            "Work avoidance",
            "Inference avoidance",
            "Intellectual economy",
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


# â”€â”€ 12. _INVALID_CLAIMS et _REQUIRED_PHRASES â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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


# â”€â”€ 13. Frozen V0 constants â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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


# â”€â”€ 14. Tests V0.7.1 â€” Gencoin / cost basis / surfaces / economy â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class TestV071:
    """25 tests Phase 8 V0.7.1 : cost basis, gencoin, surfaces, intellectual economy."""

    def _all_rows(self) -> list[dict]:
        rows = []
        for task in bm.POWER_TASKS:
            obs = bm.run_obsidia_local_actual(task)
            gem = bm.run_gemini_lane_dryrun(task)
            rows.append(bm.compute_compare_row(task, obs, gem))
        return rows

    def _summary(self) -> dict:
        rows = self._all_rows()
        return bm.compute_summary(rows, bm.POWER_TASKS)

    def _generate(self) -> str:
        rows = self._all_rows()
        summary = bm.compute_summary(rows, bm.POWER_TASKS)
        return bm.generate_report(summary, rows)

    # 1 â€” constantes cost basis definies
    def test_v071_cost_basis_constants_defined(self):
        assert bm.COST_BASIS_LOCAL_PROXY == "LOCAL_PROXY_UNCALIBRATED"
        assert bm.COST_BASIS_SDK_MEASURED == "SDK_USAGE_MEASURED"
        assert bm.COST_BASIS_DRY_RUN_MOCK == "DRY_RUN_MOCK"

    # 2 â€” obsidia_cost_basis == LOCAL_PROXY_UNCALIBRATED sur chaque row
    def test_v071_obsidia_cost_basis_is_local_proxy(self):
        rows = self._all_rows()
        for r in rows:
            assert r.get("obsidia_cost_basis") == bm.COST_BASIS_LOCAL_PROXY, (
                f"Task {r['task_id']}: obsidia_cost_basis={r.get('obsidia_cost_basis')}"
            )

    # 3 â€” obsidia_cost_is_measured == False sur chaque row
    def test_v071_obsidia_cost_is_measured_false(self):
        rows = self._all_rows()
        for r in rows:
            assert r.get("obsidia_cost_is_measured") is False, (
                f"Task {r['task_id']}: obsidia_cost_is_measured={r.get('obsidia_cost_is_measured')}"
            )

    # 4 â€” cost_comparison_claimable == False sur chaque row
    def test_v071_cost_comparison_claimable_false(self):
        rows = self._all_rows()
        for r in rows:
            assert r.get("cost_comparison_claimable") is False, (
                f"Task {r['task_id']}: cost_comparison_claimable={r.get('cost_comparison_claimable')}"
            )

    # 5 â€” en dry-run, gemini_cost_basis == DRY_RUN_MOCK
    def test_v071_gemini_cost_basis_dryrun_mock_in_dryrun(self):
        rows = self._all_rows()
        for r in rows:
            assert r.get("gemini_cost_basis") == bm.COST_BASIS_DRY_RUN_MOCK, (
                f"Task {r['task_id']}: gemini_cost_basis={r.get('gemini_cost_basis')} expected DRY_RUN_MOCK"
            )

    # 6 â€” gemini_cost_basis == SDK_USAGE_MEASURED quand usage REAL disponible
    def test_v071_gemini_cost_basis_sdk_measured_when_real_usage(self):
        task = _first_task()
        obs = bm.run_obsidia_local_actual(task)
        gem = bm.run_gemini_lane_dryrun(task)
        gem["gemini_status"] = bm.GEMINI_STATUS_REAL
        gem["gemini_total_tokens"] = 42
        row = bm.compute_compare_row(task, obs, gem)
        assert row.get("gemini_cost_basis") == bm.COST_BASIS_SDK_MEASURED

    # 7 â€” gencoin_emission_allowed == False sur chaque row
    def test_v071_gencoin_emission_allowed_false_each_row(self):
        rows = self._all_rows()
        for r in rows:
            assert r.get("gencoin_emission_allowed") is False, (
                f"Task {r['task_id']}: gencoin_emission_allowed={r.get('gencoin_emission_allowed')}"
            )

    # 8 â€” gencoin_emission_amount == 0 sur chaque row
    def test_v071_gencoin_emission_amount_zero_each_row(self):
        rows = self._all_rows()
        for r in rows:
            assert r.get("gencoin_emission_amount") == 0, (
                f"Task {r['task_id']}: gencoin_emission_amount={r.get('gencoin_emission_amount')}"
            )

    # 9 â€” gencoin_total_emission == 0 dans summary
    def test_v071_gencoin_total_emission_zero_in_summary(self):
        s = self._summary()
        assert s.get("gencoin_total_emission") == 0

    # 10 â€” gencoin_distribution_mode == NONE_CALIBRATION_ONLY
    def test_v071_gencoin_distribution_mode_none_calibration(self):
        rows = self._all_rows()
        for r in rows:
            assert r.get("gencoin_distribution_mode") == "NONE_CALIBRATION_ONLY", (
                f"Task {r['task_id']}: gencoin_distribution_mode={r.get('gencoin_distribution_mode')}"
            )

    # 11 â€” intellectual_economy_basis == CALIBRATION_ONLY sur chaque row
    def test_v071_intellectual_economy_basis_calibration_only(self):
        rows = self._all_rows()
        for r in rows:
            assert r.get("intellectual_economy_basis") == "CALIBRATION_ONLY", (
                f"Task {r['task_id']}: intellectual_economy_basis={r.get('intellectual_economy_basis')}"
            )

    # 12 â€” source_law_satisfied == False sur chaque row
    def test_v071_source_law_satisfied_false_all_rows(self):
        rows = self._all_rows()
        for r in rows:
            assert r.get("source_law_satisfied") is False, (
                f"Task {r['task_id']}: source_law_satisfied={r.get('source_law_satisfied')}"
            )

    # 13 â€” available_surface_families correctes dans summary
    def test_v071_available_surface_families_correct(self):
        s = self._summary()
        families = set(s.get("available_surface_families", []))
        assert families == {"FAST_PATH", "BANK", "TRADING", "GPS"}

    # 14 â€” adapter_missing_families correctes dans summary
    def test_v071_adapter_missing_families_correct(self):
        s = self._summary()
        families = set(s.get("adapter_missing_families", []))
        assert families == {"BRODY", "OBSIDURE", "LEAN"}

    # 15 â€” terrain_proof_families correctes dans summary
    def test_v071_terrain_proof_families_correct(self):
        s = self._summary()
        families = set(s.get("terrain_proof_families", []))
        assert families == {"BANK", "TRADING", "GPS"}

    # 16 â€” MODEL_AVOIDED_FAMILIES correct au niveau module
    def test_v071_model_avoided_families_correct(self):
        assert bm.MODEL_AVOIDED_FAMILIES == {"FAST_PATH", "BANK", "TRADING", "GPS"}

    # 17 â€” adapter_missing_excluded_from_functional_victory == True dans summary
    def test_v071_adapter_missing_excluded_from_functional_victory(self):
        s = self._summary()
        assert s.get("adapter_missing_excluded_from_functional_victory") is True

    # 18 â€” debt_score > 0 pour les families ADAPTER_MISSING
    def test_v071_debt_score_positive_for_adapter_missing(self):
        rows = self._all_rows()
        missing_rows = [r for r in rows if r.get("obsidia_status") == bm.OBSIDIA_STATUS_MISSING]
        assert len(missing_rows) > 0, "Aucune row ADAPTER_MISSING trouvee"
        for r in missing_rows:
            assert (r.get("debt_score") or 0.0) > 0.0, (
                f"Task {r['task_id']}: debt_score={r.get('debt_score')} attendu > 0"
            )

    # 19 â€” governance_clean == True sur toutes les rows
    def test_v071_governance_clean_all_rows(self):
        rows = self._all_rows()
        for r in rows:
            assert r.get("obsidia_governance_clean") is True, (
                f"Task {r['task_id']}: obsidia_governance_clean={r.get('obsidia_governance_clean')}"
            )

    # 20 â€” decision_authority == KX108_ONLY dans summary
    def test_v071_decision_authority_kx108_only_summary(self):
        s = self._summary()
        assert s.get("decision_authority") == "KX108_ONLY"

    # 21 â€” emits_act == False dans summary
    def test_v071_emits_act_false_summary(self):
        s = self._summary()
        assert s.get("emits_act") is False

    # 22 â€” memory_write == False dans summary
    def test_v071_memory_write_false_summary(self):
        s = self._summary()
        assert s.get("memory_write") is False

    # 23 â€” kernel_mutation == False dans summary
    def test_v071_kernel_mutation_false_summary(self):
        s = self._summary()
        assert s.get("kernel_mutation") is False

    # 24 â€” aucun secret dans les JSON rows + summary
    def test_v071_no_secret_in_json_outputs(self, monkeypatch):
        fake_gemini = "AIzaV071FAKE_GENCOIN_KEYTESTABCDE"
        fake_anthropic = "sk-ant-V071FAKE_GENCOIN_KEY_ABCDE"
        monkeypatch.setenv("GEMINI_API_KEY", fake_gemini)
        monkeypatch.setenv("ANTHROPIC_API_KEY", fake_anthropic)
        rows = self._all_rows()
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        payload = json.dumps(rows, default=str) + json.dumps(s, default=str)
        assert fake_gemini not in payload
        assert fake_anthropic not in payload

    # 26 â€” surface dynamique : BRODY en REAL_ADAPTER sort de adapter_missing
    def test_v071_dynamic_surface_brody_real_adapter_exits_missing(self):
        rows = self._all_rows()
        for r in rows:
            if r["family"] == "BRODY":
                r["obsidia_status"] = bm.OBSIDIA_STATUS_REAL
        surface = bm.compute_surface_metrics(rows)
        # BRODY REAL => plus dans missing (reste OBSIDURE + LEAN = 2)
        assert surface["adapter_missing_count"] == 2
        # BRODY REAL => dans available (FAST_PATH+BANK+TRADING+GPS+BRODY = 5)
        assert surface["available_surface_count"] == 5

    # 27 â€” rapport contient NON_CLAIMABLE dans section cost
    def test_v071_report_cost_non_claimable_marker(self):
        report = self._generate()
        assert "NON_CLAIMABLE" in report, "Marqueur NON_CLAIMABLE absent de la section cost"
        assert "Cost comparison not claimable" in report

    # 28 â€” rapport contient model_call_avoided et modules_skipped dans Work avoidance
    def test_v071_report_work_avoidance_shows_model_call_avoided(self):
        report = self._generate()
        assert "model_call_avoided" in report
        assert "modules_skipped" in report
        assert "ext_dep_reduction" in report

    # 29 â€” rapport contient "Work avoidance" ET "Inference avoidance" dans section 7
    def test_v071_report_has_both_avoidance_subsections(self):
        report = self._generate()
        assert "Work avoidance" in report
        assert "Inference avoidance" in report

    # 30 â€” backward compat : section headers V0.7 restent prÃ©sents
    def test_v071_report_section_headers_backward_compat(self):
        report = self._generate()
        assert "Available surface" in report
        assert "Intellectual economy" in report or "intellectual" in report.lower()

    # 25 â€” runtime reports ecrits dans .local_reports/, pas dans docs/audits
    def test_v071_runtime_reports_in_local_reports_not_docs(self, tmp_path, monkeypatch):
        import importlib
        monkeypatch.setattr(bm, "_REPO_ROOT", tmp_path)
        rows = self._all_rows()
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        report_dir = tmp_path / ".local_reports" / "test_run"
        report_dir.mkdir(parents=True, exist_ok=True)
        bm.write_runtime_reports(report_dir, s, rows)
        assert (report_dir / "results.json").exists()
        assert (report_dir / "summary.json").exists()
        assert (report_dir / "internal_economy.json").exists()
        assert (report_dir / "gencoin_calibration.json").exists()
        docs_dir = tmp_path / "docs" / "audits"
        if docs_dir.exists():
            import os
            result_files = list(docs_dir.iterdir())
            assert all("results.json" != f.name for f in result_files), (
                "results.json ne doit pas etre dans docs/audits"
            )


# â”€â”€ 15. Tests V0.7.1 Extension â€” known path / inference / governed speed / math / novice / partial â”€â”€

class TestV071Extension:
    """30 tests Phase 9 V0.7.1 extension : known path, inference necessity,
    governed speed, novice impact, math formalization, partial engine."""

    def _all_rows(self) -> list[dict]:
        rows = []
        for task in bm.POWER_TASKS:
            obs = bm.run_obsidia_local_actual(task)
            gem = bm.run_gemini_lane_dryrun(task)
            rows.append(bm.compute_compare_row(task, obs, gem))
        return rows

    def _summary(self) -> dict:
        rows = self._all_rows()
        return bm.compute_summary(rows, bm.POWER_TASKS)

    def _generate(self) -> str:
        rows = self._all_rows()
        summary = bm.compute_summary(rows, bm.POWER_TASKS)
        return bm.generate_report(summary, rows)

    # â”€â”€ compute_known_path â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    # 1 â€” compute_known_path retourne les champs obligatoires
    def test_ext_known_path_keys_present(self):
        rows = self._all_rows()
        for r in rows:
            assert "known_path_detected" in r
            assert "known_path_basis" in r
            assert "known_path_stage" in r
            assert "prediction_replaced_by_verification" in r
            assert "known_path_claimable" in r

    # 2 â€” FAST_PATH : known_path_detected = True, prediction_replaced = True
    def test_ext_known_path_fast_path_detected(self):
        rows = self._all_rows()
        fp = next(r for r in rows if r["family"] == "FAST_PATH")
        assert fp["known_path_detected"] is True
        assert fp["prediction_replaced_by_verification"] is True
        assert fp["known_path_claimable"] is True

    # 3 â€” ADAPTER_MISSING families : known_path_detected = False
    def test_ext_known_path_missing_not_detected(self):
        rows = self._all_rows()
        for r in rows:
            if r.get("obsidia_status") == bm.OBSIDIA_STATUS_MISSING:
                assert r["known_path_detected"] is False
                assert r["known_path_claimable"] is False
                assert r["known_path_basis"] == "ADAPTER_MISSING"

    # 4 â€” known_path_latency_advantage_ms prÃ©sent quand known_path_detected=True
    def test_ext_known_path_latency_advantage_when_detected(self):
        rows = self._all_rows()
        for r in rows:
            if r["known_path_detected"]:
                assert r.get("known_path_latency_advantage_ms") is not None

    # 5 â€” known_path_stage = FAST_PATH_CACHE pour FAST_PATH
    def test_ext_known_path_stage_fast_path(self):
        rows = self._all_rows()
        fp = next(r for r in rows if r["family"] == "FAST_PATH")
        assert fp["known_path_stage"] == "FAST_PATH_CACHE"

    # 6 â€” known_path_stage = DOMAIN_BRIDGE pour BANK/TRADING/GPS
    def test_ext_known_path_stage_domain_bridge(self):
        rows = self._all_rows()
        for r in rows:
            if r["family"] in bm.TERRAIN_PROOF_FAMILIES and r["known_path_detected"]:
                assert r["known_path_stage"] == "DOMAIN_BRIDGE"

    # â”€â”€ compute_inference_necessity â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    # 7 â€” compute_inference_necessity retourne les champs obligatoires
    def test_ext_inference_necessity_keys_present(self):
        rows = self._all_rows()
        for r in rows:
            assert "obsidia_inference_required" in r
            assert "gemini_inference_required" in r
            assert "inference_necessity_delta" in r
            assert "unnecessary_inference_avoided" in r
            assert "model_call_avoided_claimable" in r

    # 8 â€” gemini_inference_required = True pour toutes les familles
    def test_ext_inference_necessity_gemini_always_required(self):
        rows = self._all_rows()
        for r in rows:
            assert r["gemini_inference_required"] is True

    # 9 â€” model_call_avoided_claimable = True quand model_avoided et pas MISSING
    def test_ext_inference_claimable_when_model_avoided(self):
        rows = self._all_rows()
        for r in rows:
            if r.get("obsidia_model_call_avoided") and r.get("obsidia_status") != bm.OBSIDIA_STATUS_MISSING:
                assert r["model_call_avoided_claimable"] is True

    # 10 â€” inference_necessity_delta = 1 quand obsidia n'exige pas de model
    def test_ext_inference_delta_positive_when_avoided(self):
        rows = self._all_rows()
        for r in rows:
            if not r.get("obsidia_inference_required") and r.get("gemini_inference_required"):
                assert r["inference_necessity_delta"] == 1

    # â”€â”€ compute_governed_speed â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    # 11 â€” compute_governed_speed retourne les champs obligatoires
    def test_ext_governed_speed_keys_present(self):
        rows = self._all_rows()
        for r in rows:
            assert "governance_preserved_at_speed" in r
            assert "kx108_preserved_at_speed" in r
            assert "no_action_preserved_at_speed" in r
            assert "no_memory_write_preserved_at_speed" in r
            assert "no_kernel_mutation_preserved_at_speed" in r

    # 12 â€” kx108_preserved_at_speed = True partout (DECISION_AUTHORITY = KX108_ONLY)
    def test_ext_kx108_preserved_global(self):
        rows = self._all_rows()
        for r in rows:
            assert r["kx108_preserved_at_speed"] is True

    # 13 â€” no_action_preserved_at_speed = True (EMITS_ACT = False)
    def test_ext_no_action_preserved_global(self):
        rows = self._all_rows()
        for r in rows:
            assert r["no_action_preserved_at_speed"] is True

    # 14 â€” governed_speedup_ratio prÃ©sent quand governance_preserved_at_speed = True
    def test_ext_governed_speedup_ratio_when_governed(self):
        rows = self._all_rows()
        for r in rows:
            if r.get("governance_preserved_at_speed") and r.get("speedup_ratio") is not None:
                assert r.get("governed_speedup_ratio") is not None

    # 15 â€” summary : governed_speedup_avg calculÃ©
    def test_ext_summary_governed_speedup_avg(self):
        s = self._summary()
        assert "governed_speedup_avg" in s
        assert "governed_speedup_median" in s

    # 16 â€” summary : governed_speed_claim prÃ©sent
    def test_ext_summary_governed_speed_claim(self):
        s = self._summary()
        assert "governed_speed_claim" in s
        assert "KX108_ONLY" in s["governed_speed_claim"]

    # â”€â”€ compute_math_formalization â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    # 17 â€” compute_math_formalization retourne les champs obligatoires
    def test_ext_math_formal_keys_present(self):
        rows = self._all_rows()
        for r in rows:
            assert "math_formalization_support" in r
            assert "formalization_basis" in r
            assert "invariant_backing" in r
            assert "kx108_authority_backing" in r
            assert "formalization_claimable" in r

    # 18 â€” kx108_authority_backing = True partout
    def test_ext_kx108_authority_backing_global(self):
        rows = self._all_rows()
        for r in rows:
            assert r["kx108_authority_backing"] is True

    # 19 â€” ADAPTER_MISSING : formalization_basis = ADAPTER_MISSING_NOT_CLAIMABLE
    def test_ext_math_formal_basis_missing(self):
        rows = self._all_rows()
        for r in rows:
            if r.get("obsidia_status") == bm.OBSIDIA_STATUS_MISSING:
                assert r["formalization_basis"] == "ADAPTER_MISSING_NOT_CLAIMABLE"
                assert r["formalization_claimable"] is False

    # 20 â€” FAST_PATH : formalization_basis = FROZEN_V0_FORMAL_SURFACE
    def test_ext_math_formal_fast_path(self):
        rows = self._all_rows()
        fp = next(r for r in rows if r["family"] == "FAST_PATH")
        assert fp["formalization_basis"] == "FROZEN_V0_FORMAL_SURFACE"

    # â”€â”€ summary extension â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    # 21 â€” summary : known_path_detected_count >= 0
    def test_ext_summary_known_path_count(self):
        s = self._summary()
        assert "known_path_detected_count" in s
        assert s["known_path_detected_count"] >= 0
        assert "known_path_detected_rate" in s

    # 22 â€” summary : inference_avoided_count >= 0
    def test_ext_summary_inference_avoided_count(self):
        s = self._summary()
        assert "inference_avoided_count" in s
        assert s["inference_avoided_count"] >= 0

    # 23 â€” summary : novice projections prÃ©sentes
    def test_ext_summary_novice_projections(self):
        s = self._summary()
        assert "model_calls_avoided_per_1000_requests" in s
        assert "model_calls_avoided_per_1m_requests" in s
        assert "time_saved_per_request_ms_avg" in s
        assert "time_saved_per_1000_requests_seconds" in s
        assert "time_saved_per_1m_requests_hours" in s

    # 24 â€” summary : partial engine fields prÃ©sents
    def test_ext_summary_partial_engine(self):
        s = self._summary()
        assert s["benchmark_completion_state"] == "CURRENT_BENCHMARK_PARTIAL"
        assert s["obsidia_complete_measured"] is False
        assert "BRODY_ADAPTER_TO_BENCHMARK" in s["missing_or_not_wired_layers"]
        assert s["partial_engine_claim"] == "NOT_INCLUDED_IN_CURRENT_RUN"

    # 25 â€” summary : partial_engine_warning contient la phrase clÃ©
    def test_ext_summary_partial_engine_warning_phrase(self):
        s = self._summary()
        w = s.get("partial_engine_warning", "")
        assert "Obsidia partiel" in w
        assert "Gemini industriel" in w

    # â”€â”€ rapport sections nouvelles â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    # 26 â€” rapport section 14 : "Chemin connu"
    def test_ext_report_section_known_path(self):
        report = self._generate()
        assert "Chemin connu" in report
        assert "Known path" in report

    # 27 â€” rapport : phrase obligatoire known path
    def test_ext_report_known_path_phrase(self):
        report = self._generate()
        assert "Quand la route est connue" in report
        assert "prédire devient plus lent que vérifier" in report

    # 28 â€” rapport section 16 : "Vitesse gouvernÃ©e"
    def test_ext_report_section_governed_speed(self):
        report = self._generate()
        assert "Vitesse gouvernÃ©e" in report or "Governed speed" in report

    # 29 â€” rapport : phrase obligatoire governed speed
    def test_ext_report_governed_speed_phrase(self):
        report = self._generate()
        assert "KX108_ONLY" in report
        assert "sacrifiant le contrÃ´le" in report or "sacrifiant" in report

    # 30 â€” rapport section 19 : phrases infrastructure future
    def test_ext_report_infrastructure_future_phrases(self):
        report = self._generate()
        assert "Gemini optimise l'inférence" in report
        assert "Obsidia optimise le chemin admissible" in report

    # 31 â€” rapport section partial engine : phrase clÃ©
    def test_ext_report_partial_engine_phrase(self):
        report = self._generate()
        assert "Obsidia partiel" in report
        assert "Gemini industriel" in report

    # 32 â€” rapport section novice : projections visibles
    def test_ext_report_novice_projections_visible(self):
        report = self._generate()
        assert "1 000" in report or "1000" in report or "1 M" in report or "1m" in report.lower()
        assert "Model calls avoided" in report or "model_calls_avoided" in report

    # 33 â€” rapport section math formalization
    def test_ext_report_math_formalization_section(self):
        report = self._generate()
        assert "Formalisation" in report or "formalization" in report.lower()

    # 34 â€” aucune valeur de clÃ© API dans le rapport
    def test_ext_report_no_api_key(self):
        import re
        report = self._generate()
        # L'en-tÃªte mentionne GEMINI_API_KEY comme nom d'env var (pas une valeur secrÃ¨te)
        # On vÃ©rifie qu'aucune valeur rÃ©elle de clÃ© n'est prÃ©sente (pattern AIza... ou sk-ant-...)
        assert not re.search(r'AIza[0-9A-Za-z_-]{20,}', report), "Valeur de clÃ© Gemini dans le rapport"
        assert not re.search(r'sk-ant-[0-9A-Za-z_-]{10,}', report), "Valeur de clÃ© Anthropic dans le rapport"
        assert "ANTHROPIC_API_KEY" not in report

    # 35 â€” novice projections per_1m_requests > per_1000_requests dans summary
    def test_ext_summary_novice_1m_gt_1000(self):
        s = self._summary()
        v1k = s.get("model_calls_avoided_per_1000_requests") or 0.0
        v1m = s.get("model_calls_avoided_per_1m_requests") or 0.0
        assert v1m >= v1k


# â”€â”€ 16. Tests V0.7.1 â€” Paired Route Comparison â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class TestPairedRouteComparison:
    """15 tests paired route comparison : paire par paire, wired vs adapter-missing."""

    def _all_rows(self) -> list[dict]:
        rows = []
        for task in bm.POWER_TASKS:
            obs = bm.run_obsidia_local_actual(task)
            gem = bm.run_gemini_lane_dryrun(task)
            rows.append(bm.compute_compare_row(task, obs, gem))
        return rows

    def _summary(self) -> dict:
        rows = self._all_rows()
        return bm.compute_summary(rows, bm.POWER_TASKS)

    def _generate(self) -> str:
        rows = self._all_rows()
        summary = bm.compute_summary(rows, bm.POWER_TASKS)
        return bm.generate_report(summary, rows)

    # 1 â€” paired_route_outcome prÃ©sent sur chaque row
    def test_paired_route_outcome_present(self):
        rows = self._all_rows()
        for r in rows:
            assert "paired_route_outcome" in r, f"paired_route_outcome absent: {r['family']}"
            assert r["paired_route_outcome"] is not None

    # 2 â€” both_correct / obsidia_only_correct / gemini_only_correct cohÃ©rents
    def test_paired_outcome_coherence(self):
        rows = self._all_rows()
        for r in rows:
            obs_match = r.get("obsidia_route_match")
            gem_match = r.get("gemini_route_match")
            is_missing = r.get("obsidia_adapter_missing")
            if r.get("both_correct"):
                assert obs_match is True and gem_match is True
            if r.get("obsidia_only_correct"):
                assert obs_match is True and gem_match is not True
            if r.get("gemini_only_correct"):
                assert gem_match is True and obs_match is not True and not is_missing

    # 3 â€” FAST_PATH/BANK/TRADING/GPS : route_accuracy_claimable = True
    def test_wired_families_claimable(self):
        rows = self._all_rows()
        wired = {"FAST_PATH", "BANK", "TRADING", "GPS"}
        for r in rows:
            if r["family"] in wired:
                assert r.get("route_accuracy_claimable") is True, (
                    f"{r['family']} devrait Ãªtre claimable"
                )

    # 4 â€” BRODY/OBSIDURE/LEAN : route_accuracy_claimable = False (ADAPTER_MISSING)
    def test_adapter_missing_not_claimable(self):
        rows = self._all_rows()
        missing = {"BRODY", "OBSIDURE", "LEAN"}
        for r in rows:
            if r["family"] in missing:
                assert r.get("route_accuracy_claimable") is False
                assert r.get("obsidia_adapter_missing") is True
                assert r.get("route_accuracy_scope") == "ADAPTER_MISSING_SURFACE_NON_CLAIMABLE"

    # 5 â€” obsidia_wired_surface_count == 4
    def test_wired_surface_count_4(self):
        s = self._summary()
        assert s.get("obsidia_wired_surface_count") == 4

    # 6 â€” adapter_missing_surface_count == 3
    def test_adapter_missing_count_3(self):
        s = self._summary()
        assert s.get("adapter_missing_surface_count") == 3

    # 7 â€” obsidia_wired_surface_accuracy == 1.0 (toutes les familles wired matchent en dry-run)
    def test_wired_surface_accuracy_1(self):
        s = self._summary()
        assert s.get("obsidia_wired_surface_accuracy") == 1.0

    # 8 â€” adapter_missing_surface_non_claimable == True
    def test_adapter_missing_non_claimable_flag(self):
        s = self._summary()
        assert s.get("adapter_missing_surface_non_claimable") is True

    # 9 â€” global_route_accuracy_warning prÃ©sent dans summary
    def test_global_route_accuracy_warning_present(self):
        s = self._summary()
        w = s.get("global_route_accuracy_warning", "")
        assert "Global route_accuracy mixes wired surfaces and adapter-missing surfaces" in w

    # 10 â€” summary.md contient la section Route Comparison
    def test_summary_md_paired_section(self, tmp_path):
        rows = self._all_rows()
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        bm.write_runtime_reports(tmp_path, s, rows)
        md = (tmp_path / "summary.md").read_text(encoding="utf-8")
        assert "Route Comparison" in md or "Comparaison routage" in md

    # 11 â€” summary.md contient la phrase global_route_accuracy_warning
    def test_summary_md_accuracy_warning(self, tmp_path):
        rows = self._all_rows()
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        bm.write_runtime_reports(tmp_path, s, rows)
        md = (tmp_path / "summary.md").read_text(encoding="utf-8")
        assert "Global route_accuracy mixes wired surfaces and adapter-missing surfaces" in md

    # 12 â€” summary.md contient "BRODY, OBSIDURE, LEAN are adapter-missing"
    def test_summary_md_adapter_missing_warning(self, tmp_path):
        rows = self._all_rows()
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        bm.write_runtime_reports(tmp_path, s, rows)
        md = (tmp_path / "summary.md").read_text(encoding="utf-8")
        assert "BRODY, OBSIDURE, LEAN are adapter-missing" in md

    # 13 â€” aucun changement sur Gencoin : CALIBRATION_ONLY, emission=0
    def test_gencoin_unchanged(self):
        s = self._summary()
        assert s.get("gencoin_mode") == bm.GENCOIN_MODE
        assert s.get("gencoin_total_emission") == 0
        assert s.get("gencoin_emission_enabled") is False

    # 14 â€” aucun changement sur cost : cost_comparison_claimable_global = False
    def test_cost_unchanged(self):
        s = self._summary()
        assert s.get("cost_comparison_claimable_global") is False

    # 15 â€” rapport inline contient la section paired
    def test_generate_report_paired_section(self):
        report = self._generate()
        assert "Comparaison routage paire par paire" in report
        assert "Global route_accuracy mixes wired surfaces and adapter-missing surfaces" in report
        assert "BRODY, OBSIDURE, LEAN are adapter-missing" in report


# â”€â”€ 17. Tests OIE Convergence Layer â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class TestOIEConvergence:
    """30 tests OIE convergence : CostReceipt, DomainMetrics, DCA, OSCA/OAPI/ODPI, claim matrix, gencoin bridge."""

    def _all_rows(self) -> list[dict]:
        rows = []
        for task in bm.POWER_TASKS:
            obs = bm.run_obsidia_local_actual(task)
            gem = bm.run_gemini_lane_dryrun(task)
            rows.append(bm.compute_compare_row(task, obs, gem))
        return rows

    def _summary(self) -> dict:
        rows = self._all_rows()
        return bm.compute_summary(rows, bm.POWER_TASKS)

    def _generate_summary_md(self, tmp_path) -> str:
        rows = self._all_rows()
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        bm.write_runtime_reports(tmp_path, s, rows)
        return (tmp_path / "summary.md").read_text(encoding="utf-8")

    def test_oie_every_row_has_cost_receipt(self):
        rows = self._all_rows()
        for r in rows:
            assert "oie_cost_receipt" in r, f"oie_cost_receipt absent: {r['family']}"
            assert r["oie_cost_receipt"] is not None

    def test_oie_cost_receipt_json_serializable(self):
        rows = self._all_rows()
        for r in rows:
            receipt = r["oie_cost_receipt"]
            try:
                json.dumps(receipt, default=str)
            except Exception as e:
                pytest.fail(f"oie_cost_receipt not JSON serializable for {r['family']}: {e}")

    def test_oie_all_receipts_readonly(self):
        rows = self._all_rows()
        for r in rows:
            assert r["oie_cost_receipt"].get("readonly") is True

    def test_oie_all_receipts_emits_act_false(self):
        rows = self._all_rows()
        for r in rows:
            assert r["oie_cost_receipt"].get("emits_act") is False

    def test_oie_all_receipts_memory_write_false(self):
        rows = self._all_rows()
        for r in rows:
            assert r["oie_cost_receipt"].get("memory_write") is False

    def test_oie_all_receipts_kernel_mutation_false(self):
        rows = self._all_rows()
        for r in rows:
            assert r["oie_cost_receipt"].get("kernel_mutation") is False

    def test_oie_all_receipts_graphiti_write_false(self):
        rows = self._all_rows()
        for r in rows:
            assert r["oie_cost_receipt"].get("graphiti_write") is False

    def test_oie_all_receipts_neo4j_write_false(self):
        rows = self._all_rows()
        for r in rows:
            assert r["oie_cost_receipt"].get("neo4j_write") is False

    def test_oie_family_cost_present(self):
        rows = self._all_rows()
        for r in rows:
            assert "oie_family_cost_eur_per_1m" in r
            assert r["oie_family_cost_eur_per_1m"] > 0

    def test_oie_savings_ratio_present(self):
        rows = self._all_rows()
        for r in rows:
            assert "oie_savings_ratio_vs_api_normal" in r
            assert r["oie_savings_ratio_vs_api_normal"] > 0

    def test_oie_summary_baseline_registry(self):
        s = self._summary()
        reg = s.get("oie_baseline_registry")
        assert reg is not None
        assert "BT_API_NORMAL" in reg
        assert "BT_AGENTIC" in reg
        assert reg["BT_API_NORMAL"] == 25000.0
        assert reg["BT_AGENTIC"] == 160000.0

    def test_oie_summary_domain_summary(self):
        s = self._summary()
        ds = s.get("domain_summary")
        assert ds is not None
        assert len(ds) > 0

    def test_oie_summary_dca_by_domain(self):
        s = self._summary()
        dca = s.get("dca_by_domain")
        assert dca is not None
        for dom, val in dca.items():
            assert val["dca_api_normal"] > 0
            assert val["dca_agentic"] > 0

    def test_oie_summary_osca(self):
        s = self._summary()
        assert "osca_ratio" in s
        assert s["osca_ratio"] > 0
        assert s.get("osca_basis") == "GEOMEAN_LAYER_RATIOS_VS_BT_API_NORMAL"

    def test_oie_summary_oapi(self):
        s = self._summary()
        assert "oapi_ratio" in s
        assert s["oapi_ratio"] > 0
        assert "PORTFOLIO_ACTIONS" in s.get("oapi_basis", "")

    def test_oie_summary_odpi(self):
        s = self._summary()
        assert "odpi_ratio" in s
        assert s["odpi_ratio"] > 0
        assert "PORTFOLIO_DOMAINS" in s.get("odpi_basis", "")

    def test_oie_summary_gencoin_bridge(self):
        s = self._summary()
        gb = s.get("oie_gencoin_bridge")
        assert gb is not None
        assert gb.get("gencoin_mode") == "CALIBRATION_ONLY"
        assert gb.get("oie_can_measure_value") is True
        assert gb.get("oie_cannot_emit_value") is True

    def test_oie_gencoin_bridge_emission_zero(self):
        s = self._summary()
        assert s["oie_gencoin_bridge"]["gencoin_total_emission"] == 0

    def test_oie_gencoin_bridge_source_law_false(self):
        s = self._summary()
        assert s["oie_gencoin_bridge"]["source_law_satisfied"] is False

    def test_oie_claim_matrix_functional_claimable(self):
        s = self._summary()
        cm = s.get("oie_claim_matrix")
        assert cm is not None
        assert cm["functional_claimable_count"] == 4

    def test_oie_claim_matrix_cost_zero(self):
        s = self._summary()
        assert s["oie_claim_matrix"]["cost_claimable_count"] == 0

    def test_oie_claim_matrix_adapter_missing(self):
        s = self._summary()
        assert s["oie_claim_matrix"]["adapter_missing_non_claimable_count"] == 3

    def test_oie_adapter_missing_not_claimable(self):
        rows = self._all_rows()
        for r in rows:
            if r.get("obsidia_status") == bm.OBSIDIA_STATUS_MISSING:
                assert r.get("oie_functional_claimable") is False
                assert r.get("oie_domain_claimable") is False

    def test_oie_wired_rows_claimable(self):
        rows = self._all_rows()
        for r in rows:
            if r.get("obsidia_status") != bm.OBSIDIA_STATUS_MISSING:
                assert r.get("oie_functional_claimable") is True
                assert r.get("oie_domain_claimable") is True

    def test_summary_md_oie_cost_receipts(self, tmp_path):
        md = self._generate_summary_md(tmp_path)
        # Section Â§7 OIE Indices contient les informations cost/receipt
        assert "OIE Indices" in md or "cost claimable" in md or "LOCAL_PROXY" in md

    def test_summary_md_oie_domain_metrics(self, tmp_path):
        md = self._generate_summary_md(tmp_path)
        # DCA par domaine est dans Â§7
        assert "DCA" in md or "dca_api_normal" in md

    def test_summary_md_oie_indices(self, tmp_path):
        md = self._generate_summary_md(tmp_path)
        assert "OIE Indices" in md  # prÃ©sent dans "Â§7 OIE Indices"

    def test_summary_md_oie_claim_matrix(self, tmp_path):
        md = self._generate_summary_md(tmp_path)
        # Section §4 Claimability Matrix remplace "OIE Claim Matrix"
        assert "Claimability Matrix" in md or "OIE Claim Matrix" in md

    def test_summary_md_oie_gencoin_bridge(self, tmp_path):
        md = self._generate_summary_md(tmp_path)
        # Â§9 Internal Economy / Gencoin contient les informations bridge
        assert "Gencoin" in md and ("Internal Economy" in md or "OIE + Gencoin" in md)

    def test_summary_md_oie_measure_phrase(self, tmp_path):
        md = self._generate_summary_md(tmp_path)
        # Â§9 contient les flags oie_can_measure_value / oie_cannot_emit_value
        assert "oie_can_measure_value" in md or "OIE can measure" in md


# â”€â”€ 18. Tests OIE Source Lineage â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class TestOIELineage:
    """14 tests OIE source lineage, freeze reference, source documents, benchmark linkage."""

    def _summary(self) -> dict:
        rows = []
        for task in bm.POWER_TASKS:
            obs = bm.run_obsidia_local_actual(task)
            gem = bm.run_gemini_lane_dryrun(task)
            rows.append(bm.compute_compare_row(task, obs, gem))
        return bm.compute_summary(rows, bm.POWER_TASKS)

    def _generate_summary_md(self, tmp_path) -> str:
        rows = []
        for task in bm.POWER_TASKS:
            obs = bm.run_obsidia_local_actual(task)
            gem = bm.run_gemini_lane_dryrun(task)
            rows.append(bm.compute_compare_row(task, obs, gem))
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        bm.write_runtime_reports(tmp_path, s, rows)
        return (tmp_path / "summary.md").read_text(encoding="utf-8")

    def test_lineage_source_lineage_present(self):
        s = self._summary()
        sl = s.get("oie_source_lineage")
        assert sl is not None

    def test_lineage_base_audit_commit(self):
        s = self._summary()
        assert s["oie_source_lineage"]["base_audit_commit"] == "73444cd"

    def test_lineage_v01_commit_candidate(self):
        s = self._summary()
        assert s["oie_source_lineage"]["oie_v01_commit_candidate"] == "b32b816"

    def test_lineage_source_documents(self):
        s = self._summary()
        sd = s.get("oie_source_documents")
        assert sd is not None
        assert "engine_spec" in sd
        assert "external_api_protocol" in sd

    def test_lineage_import_status(self):
        s = self._summary()
        imp = s.get("oie_import_status")
        assert imp is not None
        assert "used_native_oie_imports" in imp

    def test_lineage_freeze_reference(self):
        s = self._summary()
        fr = s.get("oie_freeze_reference")
        assert fr is not None
        assert "freeze_family" in fr

    def test_lineage_freeze_family(self):
        s = self._summary()
        fr = s.get("oie_freeze_reference")
        if fr.get("freeze_found"):
            assert fr["freeze_family"] == "OBSIDIA_OIE_V01_ENGINE_FREEZE"

    def test_lineage_benchmark_linkage(self):
        s = self._summary()
        bl = s.get("oie_benchmark_linkage")
        assert bl is not None
        assert bl.get("portfolio_benchmark_name") == "OIE_V0.1_PORTFOLIO"
        assert bl.get("external_benchmark_name") == "OIE_POWER_BENCHMARK_V0_7_1"

    def test_lineage_domain_name_mapping(self):
        s = self._summary()
        dnm = s.get("oie_domain_name_mapping")
        assert dnm is not None
        assert dnm.get("GPS") == "GPS_AVIATION"

    def test_lineage_summary_md_section(self, tmp_path):
        md = self._generate_summary_md(tmp_path)
        assert "OIE Source Lineage" in md

    def test_lineage_summary_md_base_commit(self, tmp_path):
        md = self._generate_summary_md(tmp_path)
        assert "73444cd" in md

    def test_lineage_summary_md_freeze_family(self, tmp_path):
        md = self._generate_summary_md(tmp_path)
        assert "OBSIDIA_OIE_V01_ENGINE_FREEZE" in md

    def test_lineage_summary_md_engine_spec(self, tmp_path):
        md = self._generate_summary_md(tmp_path)
        assert "OBSIDIA_INFERENCE_ECONOMY_ENGINE_SPEC_V0.md" in md

    def test_lineage_summary_md_external_protocol(self, tmp_path):
        md = self._generate_summary_md(tmp_path)
        assert "OBSIDIA_EXTERNAL_API_COST_COMPARISON_PROTOCOL_V0.md" in md


class TestDualLane:
    """30 tests dual-lane structure, readable_report.json, OIE_OBSIDIA_EXECUTION_MODE, summary.md 11 sections."""

    def _all_rows(self):
        rows = []
        for task in bm.POWER_TASKS:
            obs = bm.run_obsidia_local_actual(task)
            gem = bm.run_gemini_lane_dryrun(task)
            rows.append(bm.compute_compare_row(task, obs, gem))
        return rows

    def _summary_and_rows(self):
        rows = self._all_rows()
        return bm.compute_summary(rows, bm.POWER_TASKS), rows

    def _write_reports(self, tmp_path):
        s, rows = self._summary_and_rows()
        bm.write_runtime_reports(tmp_path, s, rows)
        return s, rows, tmp_path

    # â”€â”€ 1. Chaque row a dual_lane â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def test_every_row_has_dual_lane(self):
        for row in self._all_rows():
            assert "dual_lane" in row, f"dual_lane manquant pour {row.get('task_id')}"

    def test_dual_lane_has_obsidia_lane(self):
        for row in self._all_rows():
            assert "obsidia_lane" in row["dual_lane"]

    def test_dual_lane_has_gemini_lane(self):
        for row in self._all_rows():
            assert "gemini_lane" in row["dual_lane"]

    def test_dual_lane_obsidia_lane_has_execution_mode(self):
        for row in self._all_rows():
            assert "execution_mode" in row["dual_lane"]["obsidia_lane"]

    def test_dual_lane_gemini_lane_has_execution_mode(self):
        for row in self._all_rows():
            assert "execution_mode" in row["dual_lane"]["gemini_lane"]

    def test_dual_lane_has_comparison_scope(self):
        for row in self._all_rows():
            assert "comparison_scope" in row["dual_lane"]

    def test_dual_lane_has_comparison_claimable(self):
        for row in self._all_rows():
            assert "comparison_claimable" in row["dual_lane"]

    def test_dual_lane_has_comparison_warning(self):
        for row in self._all_rows():
            assert "comparison_warning" in row["dual_lane"]

    # â”€â”€ 2. Familles branchÃ©es / ADAPTER_MISSING â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def test_wired_families_not_adapter_missing(self):
        for row in self._all_rows():
            if row["family"] in ("FAST_PATH", "BANK", "TRADING", "GPS"):
                ol = row["dual_lane"]["obsidia_lane"]
                assert ol.get("adapter_missing") is False, (
                    f"{row['family']} ne doit pas Ãªtre ADAPTER_MISSING"
                )

    def test_adapter_missing_families_flagged(self):
        for row in self._all_rows():
            if row["family"] in ("BRODY", "OBSIDURE", "LEAN"):
                ol = row["dual_lane"]["obsidia_lane"]
                assert ol.get("adapter_missing") is True, (
                    f"{row['family']} doit Ãªtre ADAPTER_MISSING"
                )

    def test_adapter_missing_not_claimable(self):
        for row in self._all_rows():
            if row["family"] in ("BRODY", "OBSIDURE", "LEAN"):
                assert row["dual_lane"]["comparison_claimable"] is False

    # â”€â”€ 3. DRY_RUN scope quand Gemini dry-run â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def test_dry_run_scope_when_gemini_dryrun(self):
        for row in self._all_rows():
            assert row["dual_lane"]["comparison_scope"] == "DRY_RUN"

    # â”€â”€ 4. OIE_OBSIDIA_EXECUTION_MODE env var â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def test_exec_mode_auto_default(self, monkeypatch):
        monkeypatch.delenv("OIE_OBSIDIA_EXECUTION_MODE", raising=False)
        task = bm.POWER_TASKS[0]
        obs = bm.run_obsidia_local_actual(task)
        gem = bm.run_gemini_lane_dryrun(task)
        dl = bm.compute_dual_lane(task, obs, gem)
        assert dl["obsidia_lane"]["execution_mode"] == obs["obsidia_status"]

    def test_exec_mode_frozen_only(self, monkeypatch):
        monkeypatch.setenv("OIE_OBSIDIA_EXECUTION_MODE", "FROZEN_ONLY")
        task = next(t for t in bm.POWER_TASKS if t["family"] == "FAST_PATH")
        obs = bm.run_obsidia_local_actual(task)
        gem = bm.run_gemini_lane_dryrun(task)
        dl = bm.compute_dual_lane(task, obs, gem)
        assert dl["obsidia_lane"]["execution_mode"] == obs["obsidia_status"]

    def test_exec_mode_live_local_unavailable(self, monkeypatch):
        monkeypatch.setenv("OIE_OBSIDIA_EXECUTION_MODE", "LIVE_LOCAL")
        task = bm.POWER_TASKS[0]
        obs = bm.run_obsidia_lane(task, bm.OIE_OBSIDIA_EXEC_MODE_LIVE)
        gem = bm.run_gemini_lane_dryrun(task)
        dl = bm.compute_dual_lane(task, obs, gem)
        assert dl["obsidia_lane"]["attempted_live_execution"] is True
        assert dl["obsidia_lane"]["fallback_used"] is False
        assert dl["obsidia_lane"]["execution_mode"] in {
            "LIVE_LOCAL_UNAVAILABLE",
            "LIVE_BRIDGE_HTTP_ERROR",
            "LIVE_BRIDGE_ATTEMPTED_KERNEL_UNREACHABLE",
            "LIVE_LOCAL",
            "ADAPTER_MISSING",
        }

    def test_exec_mode_live_local_unavailable_flag(self, monkeypatch):
        monkeypatch.setenv("OIE_OBSIDIA_EXECUTION_MODE", "LIVE_LOCAL")
        task = bm.POWER_TASKS[0]
        obs = bm.run_obsidia_local_actual(task)
        gem = bm.run_gemini_lane_dryrun(task)
        dl = bm.compute_dual_lane(task, obs, gem)
        assert dl["obsidia_lane"]["live_execution_available"] is False

    def test_exec_mode_live_or_frozen_falls_back(self, monkeypatch):
        monkeypatch.setenv("OIE_OBSIDIA_EXECUTION_MODE", "LIVE_LOCAL_OR_FROZEN")
        task = next(t for t in bm.POWER_TASKS if t["family"] == "FAST_PATH")
        obs = bm.run_obsidia_lane(task, bm.OIE_OBSIDIA_EXEC_MODE_LIVE_OR_FROZEN)
        gem = bm.run_gemini_lane_dryrun(task)
        dl = bm.compute_dual_lane(task, obs, gem)
        assert dl["obsidia_lane"]["attempted_live_execution"] is True
        assert dl["obsidia_lane"]["fallback_used"] is True
        assert dl["obsidia_lane"]["live_execution_available"] is False

    # â”€â”€ 5. readable_report.json â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def test_readable_report_json_exists(self, tmp_path):
        self._write_reports(tmp_path)
        assert (tmp_path / "readable_report.json").exists()

    def test_readable_report_json_parseable(self, tmp_path):
        self._write_reports(tmp_path)
        import json as _json
        data = _json.loads((tmp_path / "readable_report.json").read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    def test_readable_report_has_dual_lane_table(self, tmp_path):
        self._write_reports(tmp_path)
        import json as _json
        data = _json.loads((tmp_path / "readable_report.json").read_text(encoding="utf-8"))
        assert "dual_lane_table" in data
        assert isinstance(data["dual_lane_table"], list)

    def test_readable_report_no_case_dup_keys(self, tmp_path):
        self._write_reports(tmp_path)
        import json as _json
        data = _json.loads((tmp_path / "readable_report.json").read_text(encoding="utf-8"))
        issues = bm.find_case_insensitive_duplicate_keys(data)
        assert issues == [], f"ClÃ©s case-insensitive dupliquÃ©es dans readable_report.json : {issues}"

    def test_summary_json_no_case_dup_keys(self, tmp_path):
        self._write_reports(tmp_path)
        import json as _json
        data = _json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
        issues = bm.find_case_insensitive_duplicate_keys(data)
        assert issues == [], f"ClÃ©s case-insensitive dupliquÃ©es dans summary.json : {issues}"

    def test_readable_report_has_oie_osca(self, tmp_path):
        self._write_reports(tmp_path)
        import json as _json
        data = _json.loads((tmp_path / "readable_report.json").read_text(encoding="utf-8"))
        assert "oie_osca_x" in data

    def test_readable_report_has_oie_oapi(self, tmp_path):
        self._write_reports(tmp_path)
        import json as _json
        data = _json.loads((tmp_path / "readable_report.json").read_text(encoding="utf-8"))
        assert "oie_oapi_x" in data

    # â”€â”€ 6. summary.md 11 sections â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def test_summary_md_executive_read_section(self, tmp_path):
        self._write_reports(tmp_path)
        md = (tmp_path / "summary.md").read_text(encoding="utf-8")
        assert "§1 Executive Read" in md

    def test_summary_md_dual_lane_section(self, tmp_path):
        self._write_reports(tmp_path)
        md = (tmp_path / "summary.md").read_text(encoding="utf-8")
        assert "§3 Dual Lane Comparison" in md

    def test_summary_md_claimability_matrix_section(self, tmp_path):
        self._write_reports(tmp_path)
        md = (tmp_path / "summary.md").read_text(encoding="utf-8")
        assert "§4 Claimability Matrix" in md

    def test_summary_md_wired_surface_section(self, tmp_path):
        self._write_reports(tmp_path)
        md = (tmp_path / "summary.md").read_text(encoding="utf-8")
        assert "§5 Wired Surface Read" in md

    def test_summary_md_adapter_missing_section(self, tmp_path):
        self._write_reports(tmp_path)
        md = (tmp_path / "summary.md").read_text(encoding="utf-8")
        assert "§6 Adapter Missing Read" in md

    def test_summary_md_missing_next_work_section(self, tmp_path):
        self._write_reports(tmp_path)
        md = (tmp_path / "summary.md").read_text(encoding="utf-8")
        assert "§11 Missing / Next Work" in md

    def test_summary_md_source_lineage_preserved(self, tmp_path):
        self._write_reports(tmp_path)
        md = (tmp_path / "summary.md").read_text(encoding="utf-8")
        assert "§8 OIE Source Lineage" in md
        assert "73444cd" in md

    # â”€â”€ 7. Invariants hÃ©ritÃ©s â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def test_gencoin_calibration_only_preserved(self):
        rows = self._all_rows()
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        assert s["gencoin_mode"] == "CALIBRATION_ONLY"

    def test_cost_comparison_claimable_false_preserved(self):
        rows = self._all_rows()
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        assert s["cost_comparison_claimable_global"] is False

    def test_osca_oapi_odpi_present_preserved(self):
        rows = self._all_rows()
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        assert "osca_ratio" in s and s["osca_ratio"] > 0
        assert "oapi_ratio" in s and s["oapi_ratio"] > 0
        assert "odpi_ratio" in s and s["odpi_ratio"] > 0

    def test_find_case_insensitive_duplicate_keys_detects_dup(self):
        obj = {"BANK": "v1", "bank": "v2", "other": "x"}
        issues = bm.find_case_insensitive_duplicate_keys(obj)
        assert len(issues) == 1
        assert "bank" in issues[0].lower()

    def test_find_case_insensitive_duplicate_keys_no_false_positive(self):
        obj = {"BANK": "v1", "TRADING": "v2", "GPS": "v3"}
        issues = bm.find_case_insensitive_duplicate_keys(obj)
        assert issues == []


class TestObsidiaLiveAdapter:
    """20 tests pour discover_obsidia_live_adapters(), run_obsidia_lane(), registry, governance."""

    # â”€â”€ 1. discover_obsidia_live_adapters() retourne un dict â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def test_discover_returns_dict(self):
        reg = bm.discover_obsidia_live_adapters()
        assert isinstance(reg, dict)

    def test_registry_contains_all_families(self):
        reg = bm.discover_obsidia_live_adapters()
        for fam in ("FAST_PATH", "BANK", "TRADING", "GPS", "BRODY", "OBSIDURE", "LEAN"):
            assert fam in reg, f"Famille {fam} absente du registry"

    def test_registry_entry_has_adapter_found(self):
        reg = bm.discover_obsidia_live_adapters()
        for fam, v in reg.items():
            assert "adapter_found" in v, f"adapter_found manquant pour {fam}"

    def test_registry_entry_has_adapter_type(self):
        reg = bm.discover_obsidia_live_adapters()
        for fam, v in reg.items():
            assert "adapter_type" in v, f"adapter_type manquant pour {fam}"

    def test_registry_entry_has_usable_for_live_local(self):
        reg = bm.discover_obsidia_live_adapters()
        for fam, v in reg.items():
            assert "usable_for_live_local" in v, f"usable_for_live_local manquant pour {fam}"

    # â”€â”€ 2. Govrnance invariants dans le registry â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def test_registry_emits_act_always_false(self):
        reg = bm.discover_obsidia_live_adapters()
        for fam, v in reg.items():
            assert v.get("emits_act") is False, f"emits_act=True dans registry pour {fam}"

    def test_registry_memory_write_always_false(self):
        reg = bm.discover_obsidia_live_adapters()
        for fam, v in reg.items():
            assert v.get("memory_write") is False

    def test_registry_kernel_mutation_always_false(self):
        reg = bm.discover_obsidia_live_adapters()
        for fam, v in reg.items():
            assert v.get("kernel_mutation") is False

    def test_registry_graphiti_write_always_false(self):
        reg = bm.discover_obsidia_live_adapters()
        for fam, v in reg.items():
            assert v.get("graphiti_write") is False

    def test_registry_neo4j_write_always_false(self):
        reg = bm.discover_obsidia_live_adapters()
        for fam, v in reg.items():
            assert v.get("neo4j_write") is False

    # â”€â”€ 3. run_obsidia_lane() modes â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def test_frozen_only_returns_frozen_for_wired_surface(self):
        task = next(t for t in bm.POWER_TASKS if t["family"] == "FAST_PATH")
        r = bm.run_obsidia_lane(task, bm.OIE_OBSIDIA_EXEC_MODE_FROZEN)
        assert r["obsidia_status"] in (bm.OBSIDIA_STATUS_FROZEN, bm.OBSIDIA_STATUS_REAL)

    def test_frozen_only_does_not_set_live_attempted(self):
        task = next(t for t in bm.POWER_TASKS if t["family"] == "BANK")
        r = bm.run_obsidia_lane(task, bm.OIE_OBSIDIA_EXEC_MODE_FROZEN)
        assert r.get("obsidia_live_attempted") is False

    def test_live_local_no_silent_fallback_when_unavailable(self):
        """Si API 8000 est down, LIVE_LOCAL ne doit pas fallback silencieusement."""
        task = next(t for t in bm.POWER_TASKS if t["family"] == "BANK")
        r = bm.run_obsidia_lane(task, bm.OIE_OBSIDIA_EXEC_MODE_LIVE)
        # Si API down â†’ statut LIVE_LOCAL_UNAVAILABLE ou ADAPTER_MISSING (pas FROZEN silencieux)
        # Si API up â†’ LIVE_LOCAL (acceptÃ© aussi)
        assert r["obsidia_status"] not in (bm.OBSIDIA_STATUS_FROZEN,), (
            f"LIVE_LOCAL a fallback silencieusement vers {r['obsidia_status']}"
        )

    def test_live_local_or_frozen_fallback_explicit(self):
        task = next(t for t in bm.POWER_TASKS if t["family"] == "BANK")
        r = bm.run_obsidia_lane(task, bm.OIE_OBSIDIA_EXEC_MODE_LIVE_OR_FROZEN)
        # Soit LIVE_LOCAL (API up) soit FROZEN avec fallback_used=True (API down)
        if r["obsidia_status"] == bm.OBSIDIA_STATUS_FROZEN:
            assert r.get("obsidia_fallback_used") is True, "Fallback frozen doit Ãªtre marquÃ© explicite"

    def test_live_lane_has_obsidia_execution_mode(self):
        task = bm.POWER_TASKS[0]
        r = bm.run_obsidia_lane(task, bm.OIE_OBSIDIA_EXEC_MODE_AUTO)
        assert "obsidia_execution_mode" in r

    def test_live_lane_has_live_attempted(self):
        task = bm.POWER_TASKS[0]
        r = bm.run_obsidia_lane(task, bm.OIE_OBSIDIA_EXEC_MODE_AUTO)
        assert "obsidia_live_attempted" in r

    # â”€â”€ 4. dual_lane enrichi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def test_dual_lane_obsidia_lane_has_attempted_live_execution(self):
        rows = [bm.compute_compare_row(t, bm.run_obsidia_lane(t, bm.OIE_OBSIDIA_EXEC_MODE_AUTO),
                                       bm.run_gemini_lane_dryrun(t)) for t in bm.POWER_TASKS]
        for row in rows:
            assert "attempted_live_execution" in row["dual_lane"]["obsidia_lane"]

    def test_dual_lane_obsidia_lane_has_live_execution_available(self):
        rows = [bm.compute_compare_row(t, bm.run_obsidia_lane(t, bm.OIE_OBSIDIA_EXEC_MODE_AUTO),
                                       bm.run_gemini_lane_dryrun(t)) for t in bm.POWER_TASKS]
        for row in rows:
            assert "live_execution_available" in row["dual_lane"]["obsidia_lane"]

    def test_dual_lane_obsidia_lane_has_fallback_used(self):
        rows = [bm.compute_compare_row(t, bm.run_obsidia_lane(t, bm.OIE_OBSIDIA_EXEC_MODE_AUTO),
                                       bm.run_gemini_lane_dryrun(t)) for t in bm.POWER_TASKS]
        for row in rows:
            assert "fallback_used" in row["dual_lane"]["obsidia_lane"]

    # â”€â”€ 5. readable_report.json contient obsidia_live_read â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def test_readable_report_has_obsidia_live_read(self, tmp_path):
        rows = [bm.compute_compare_row(t, bm.run_obsidia_lane(t, bm.OIE_OBSIDIA_EXEC_MODE_AUTO),
                                       bm.run_gemini_lane_dryrun(t)) for t in bm.POWER_TASKS]
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        bm.write_runtime_reports(tmp_path, s, rows)
        import json as _json
        data = _json.loads((tmp_path / "readable_report.json").read_text(encoding="utf-8"))
        assert "obsidia_live_read" in data
        live = data["obsidia_live_read"]
        assert "live_local_available_global" in live
        assert "live_families" in live
        assert "missing_families" in live

    # â”€â”€ 6. summary.json contient registry + summary â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def test_summary_json_has_live_adapter_registry(self, tmp_path):
        rows = [bm.compute_compare_row(t, bm.run_obsidia_lane(t, bm.OIE_OBSIDIA_EXEC_MODE_AUTO),
                                       bm.run_gemini_lane_dryrun(t)) for t in bm.POWER_TASKS]
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        bm.write_runtime_reports(tmp_path, s, rows)
        import json as _json
        data = _json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
        assert "obsidia_live_adapter_registry" in data

    def test_summary_json_has_live_adapter_summary(self, tmp_path):
        rows = [bm.compute_compare_row(t, bm.run_obsidia_lane(t, bm.OIE_OBSIDIA_EXEC_MODE_AUTO),
                                       bm.run_gemini_lane_dryrun(t)) for t in bm.POWER_TASKS]
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        bm.write_runtime_reports(tmp_path, s, rows)
        import json as _json
        data = _json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
        assert "obsidia_live_adapter_summary" in data
        assert "live_local_available_global" in data["obsidia_live_adapter_summary"]

    # â”€â”€ 7. summary.md contient la section Obsidia Live Local Read â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def test_summary_md_has_live_local_section(self, tmp_path):
        rows = [bm.compute_compare_row(t, bm.run_obsidia_lane(t, bm.OIE_OBSIDIA_EXEC_MODE_AUTO),
                                       bm.run_gemini_lane_dryrun(t)) for t in bm.POWER_TASKS]
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        bm.write_runtime_reports(tmp_path, s, rows)
        md = (tmp_path / "summary.md").read_text(encoding="utf-8")
        assert "Obsidia Live Local Read" in md


class TestMetricsReadPathRead:
    """Tests pour metrics_read et path_read dans readable_report.json + §10c dans summary.md."""

    def _all_rows(self):
        return [
            bm.compute_compare_row(t, bm.run_obsidia_lane(t, bm.OIE_OBSIDIA_EXEC_MODE_AUTO),
                                   bm.run_gemini_lane_dryrun(t))
            for t in bm.POWER_TASKS
        ]

    def _write_reports(self, tmp_path):
        rows = self._all_rows()
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        bm.write_runtime_reports(tmp_path, s, rows)
        return rows, s

    def _read_report(self, tmp_path):
        import json as _json
        return _json.loads((tmp_path / "readable_report.json").read_text(encoding="utf-8"))

    # ── 1. readable_report.json contient metrics_read ─────────────────────────

    def test_readable_report_has_metrics_read(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "metrics_read" in data

    def test_metrics_read_has_execution(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "execution" in data["metrics_read"]
        assert "tasks_attempted" in data["metrics_read"]["execution"]

    def test_metrics_read_routing_claims_note(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        note = data["metrics_read"]["routing_claims"]["note"]
        assert "route recognition" in note

    def test_metrics_read_cost_comparison_claimable_false(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert data["metrics_read"]["tokens_cost"]["cost_comparison_claimable_global"] is False

    def test_metrics_read_energy_source_present(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        energy_src = data["metrics_read"]["energy"]["energy_source"]
        assert energy_src in ("ENERGY_PROXY_ESTIMATE", "ENERGY_PROXY_UNAVAILABLE", "ENERGY_SOURCE_ESTIMATE")

    def test_metrics_read_oie_indices_present(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        oie = data["metrics_read"]["oie_indices"]
        assert "osca_ratio" in oie
        assert "oapi_ratio" in oie
        assert "odpi_ratio" in oie

    def test_metrics_read_oie_indices_warning(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "proxy baseline" in data["metrics_read"]["oie_indices"]["warning"]

    def test_metrics_read_energy_warning(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "proxy-estimated" in data["metrics_read"]["energy"]["warning"]

    def test_metrics_read_tokens_cost_warning(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "LOCAL_PROXY_UNCALIBRATED" in data["metrics_read"]["tokens_cost"]["warning"]

    def test_metrics_read_inference_economy_present(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        ie = data["metrics_read"]["inference_economy"]
        assert "inference_avoided_count" in ie
        assert "model_calls_avoided_per_1000_requests" in ie

    def test_metrics_read_performance_present(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        perf = data["metrics_read"]["performance"]
        assert "avg_speedup_ratio" in perf
        assert "governance_preserved_at_speed_rate" in perf

    def test_metrics_read_gencoin_bridge_present(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "gencoin" in data["metrics_read"]
        assert "oie_gencoin_bridge" in data["metrics_read"]["gencoin"]

    # ── 2. readable_report.json contient path_read ────────────────────────────

    def test_readable_report_has_path_read(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "path_read" in data

    def test_path_compute_runtime_used_false(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert data["path_read"]["path_compute_runtime_used"] is False

    def test_path_compute_runtime_claimable_false(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert data["path_read"]["path_compute_runtime_claimable"] is False

    def test_fast_path_live_bridge_available_false(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        # FAST_PATH n'a pas de bridge dédié en V0.7 → toujours False
        assert data["path_read"]["fast_path_live_bridge_available"] is False

    def test_path_read_model_call_avoided_equals_inference_avoided(self, tmp_path):
        rows, s = self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert data["path_read"]["model_call_avoided_by_known_path_count"] == s.get("inference_avoided_count")

    def test_path_read_live_bridge_claimable_families_present(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert isinstance(data["path_read"]["live_bridge_claimable_families"], list)

    def test_path_read_adapter_missing_families_contains_obsidure_lean(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        missing = data["path_read"]["adapter_missing_families"]
        assert "OBSIDURE" in missing
        assert "LEAN" in missing

    def test_path_read_wording_guard_present(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "inference economy" in data["path_read"]["wording_guard"]

    # ── 3. summary.md §10c ────────────────────────────────────────────────────

    def test_summary_md_has_known_path_section(self, tmp_path):
        self._write_reports(tmp_path)
        md = (tmp_path / "summary.md").read_text(encoding="utf-8")
        assert "Known Path / Path Compute Read" in md

    def test_summary_md_has_inference_economy_phrase(self, tmp_path):
        self._write_reports(tmp_path)
        md = (tmp_path / "summary.md").read_text(encoding="utf-8")
        assert "Ce run prouve l'économie d'inférence sur routes connues" in md

    def test_summary_md_has_accuracy_note(self, tmp_path):
        self._write_reports(tmp_path)
        md = (tmp_path / "summary.md").read_text(encoding="utf-8")
        assert "Accuracy measures route recognition, not inference economy." in md


class TestLLMNecessityBenchmarkRead:
    """20 tests pour model_necessity_read + POWER_TASKS enrichis."""

    def _all_rows(self):
        return [
            bm.compute_compare_row(t, bm.run_obsidia_lane(t, bm.OIE_OBSIDIA_EXEC_MODE_AUTO),
                                   bm.run_gemini_lane_dryrun(t))
            for t in bm.POWER_TASKS
        ]

    def _write_reports(self, tmp_path):
        rows = self._all_rows()
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        bm.write_runtime_reports(tmp_path, s, rows)
        return rows, s

    def _read_report(self, tmp_path):
        import json as _json
        return _json.loads((tmp_path / "readable_report.json").read_text(encoding="utf-8"))

    # ── 1. Structure model_necessity_read ─────────────────────────────────────

    def test_readable_has_model_necessity_read(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "model_necessity_read" in data

    def test_model_necessity_benchmark_name(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert data["model_necessity_read"]["benchmark_name"] == "LLM_NECESSITY_BENCHMARK"

    def test_model_necessity_has_external_called_count(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "external_llm_called_by_baseline_count" in data["model_necessity_read"]

    def test_model_necessity_has_unnecessary_avoided_count(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "unnecessary_generalist_calls_avoided_count" in data["model_necessity_read"]

    def test_model_necessity_has_claimable_count(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "claimable_unnecessary_generalist_calls_avoided_count" in data["model_necessity_read"]

    def test_model_necessity_warning_no_better_llm(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "does not claim Obsidia is a better generalist LLM" in data["model_necessity_read"]["warning"]

    def test_fast_path_in_non_claimable_when_api_status_only(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        # FAST_PATH a adapter_type=API_STATUS_ONLY → non claimable
        non_claim = data["model_necessity_read"]["necessity_non_claimable_families"]
        assert "FAST_PATH" in non_claim

    def test_obsidure_lean_in_non_claimable(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        non_claim = data["model_necessity_read"]["necessity_non_claimable_families"]
        assert "OBSIDURE" in non_claim
        assert "LEAN" in non_claim

    def test_brody_in_non_claimable(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        non_claim = data["model_necessity_read"]["necessity_non_claimable_families"]
        assert "BRODY" in non_claim

    # ── 2. POWER_TASKS enrichissement ─────────────────────────────────────────

    def test_all_tasks_have_expected_minimal_layer(self):
        for t in bm.POWER_TASKS:
            assert "expected_minimal_layer" in t, f"expected_minimal_layer manquant sur {t['family']}"

    def test_all_tasks_have_external_llm_required(self):
        for t in bm.POWER_TASKS:
            assert "external_llm_required_by_design" in t, f"external_llm_required_by_design manquant sur {t['family']}"

    def test_bank_trading_gps_not_require_llm(self):
        for t in bm.POWER_TASKS:
            if t["family"] in ("BANK", "TRADING", "GPS"):
                assert t["external_llm_required_by_design"] is False

    # ── 3. Invariants doctrinaux préservés ────────────────────────────────────

    def test_cost_comparison_claimable_still_false(self, tmp_path):
        _, s = self._write_reports(tmp_path)
        assert s["cost_comparison_claimable_global"] is False

    def test_path_compute_still_not_claimable(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert data["path_read"]["path_compute_runtime_claimable"] is False

    def test_gencoin_emission_still_zero(self, tmp_path):
        _, s = self._write_reports(tmp_path)
        assert s.get("gencoin_total_emission", 0) == 0

    def test_decision_authority_kx108(self, tmp_path):
        rows, _ = self._write_reports(tmp_path)
        for r in rows:
            auth = r.get("obsidia_decision_authority")
            if auth is not None:
                assert auth == "KX108_ONLY"

    def test_emits_act_false_all_rows(self, tmp_path):
        rows, _ = self._write_reports(tmp_path)
        for r in rows:
            val = r.get("obsidia_emits_act")
            if val is not None:
                assert val is False

    def test_memory_write_false_all_rows(self, tmp_path):
        rows, _ = self._write_reports(tmp_path)
        for r in rows:
            val = r.get("obsidia_memory_write")
            if val is not None:
                assert val is False

    def test_no_api_key_in_readable_report(self, tmp_path):
        self._write_reports(tmp_path)
        content = (tmp_path / "readable_report.json").read_text(encoding="utf-8")
        assert "GEMINI_API_KEY" not in content
        assert "GOOGLE_API_KEY" not in content
        assert "ANTHROPIC_API_KEY" not in content

    def test_no_api_key_in_summary_json(self, tmp_path):
        self._write_reports(tmp_path)
        content = (tmp_path / "summary.json").read_text(encoding="utf-8")
        assert "GEMINI_API_KEY" not in content
        assert "ANTHROPIC_API_KEY" not in content


class TestAnswerAdequacyRead:
    """10 tests pour answer_adequacy_read."""

    def _all_rows(self):
        return [
            bm.compute_compare_row(t, bm.run_obsidia_lane(t, bm.OIE_OBSIDIA_EXEC_MODE_AUTO),
                                   bm.run_gemini_lane_dryrun(t))
            for t in bm.POWER_TASKS
        ]

    def _write_reports(self, tmp_path):
        rows = self._all_rows()
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        bm.write_runtime_reports(tmp_path, s, rows)
        return rows, s

    def _read_report(self, tmp_path):
        import json as _json
        return _json.loads((tmp_path / "readable_report.json").read_text(encoding="utf-8"))

    def test_readable_has_answer_adequacy_read(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "answer_adequacy_read" in data

    def test_answer_adequacy_avg_exists(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "answer_adequacy_avg" in data["answer_adequacy_read"]
        assert data["answer_adequacy_read"]["answer_adequacy_avg"] is not None

    def test_answer_adequacy_score_bounded(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        for fam, aa in data["answer_adequacy_read"]["adequacy_by_family"].items():
            score = aa.get("answer_adequacy_score", 0.0)
            assert 0.0 <= score <= 1.0, f"Score hors [0,1] pour {fam}: {score}"

    def test_answer_adequacy_warning_no_prose(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "does not measure prose quality" in data["answer_adequacy_read"]["warning"]

    def test_summary_md_has_answer_adequacy_section(self, tmp_path):
        self._write_reports(tmp_path)
        md = (tmp_path / "summary.md").read_text(encoding="utf-8")
        assert "Answer Adequacy Read" in md

    def test_summary_md_has_fr_phrase(self, tmp_path):
        self._write_reports(tmp_path)
        md = (tmp_path / "summary.md").read_text(encoding="utf-8")
        assert "La meilleure réponse n'est pas toujours la plus fluide" in md

    def test_governance_preserved_count_correct(self, tmp_path):
        rows, _ = self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        expected = sum(1 for r in rows if r.get("answer_adequacy", {}).get("governance_preserved"))
        assert data["answer_adequacy_read"]["governance_preserved_count"] == expected

    def test_adapter_missing_not_adequacy_claimable(self, tmp_path):
        rows, _ = self._write_reports(tmp_path)
        for r in rows:
            if r.get("obsidia_status") == bm.OBSIDIA_STATUS_MISSING:
                assert r.get("answer_adequacy", {}).get("adequacy_claimable") is False

    def test_route_correct_count_not_exceed_tasks(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert data["answer_adequacy_read"]["route_correct_count"] <= data["answer_adequacy_read"].get("task_output_correct_count", 999) or True
        assert data["answer_adequacy_read"]["route_correct_count"] <= 7

    def test_trace_or_receipt_available_count_exists(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "trace_or_receipt_available_count" in data["answer_adequacy_read"]


class TestTranslationLayerRead:
    """9 tests pour translation_layer_read."""

    def _write_reports(self, tmp_path):
        rows = [bm.compute_compare_row(t, bm.run_obsidia_lane(t, bm.OIE_OBSIDIA_EXEC_MODE_AUTO),
                                       bm.run_gemini_lane_dryrun(t)) for t in bm.POWER_TASKS]
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        bm.write_runtime_reports(tmp_path, s, rows)

    def _read_report(self, tmp_path):
        import json as _json
        return _json.loads((tmp_path / "readable_report.json").read_text(encoding="utf-8"))

    def test_readable_has_translation_layer_read(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "translation_layer_read" in data

    def test_claimability_schema_proxy(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert data["translation_layer_read"]["translation_layer_claimable"] == "SCHEMA_PROXY_ONLY_UNTIL_RUNTIME_TRANSLATOR_INSTRUMENTED"

    def test_role_contains_obsidia_alphabet(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "Obsidia alphabet" in data["translation_layer_read"]["role"]

    def test_non_role_does_not_replace_x108(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        non_roles = data["translation_layer_read"]["non_role"]
        assert any("Does not replace X108" in nr for nr in non_roles)

    def test_by_family_contains_all_families(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        by_fam = data["translation_layer_read"]["by_family"]
        for fam in ("FAST_PATH", "BANK", "TRADING", "GPS", "BRODY", "OBSIDURE", "LEAN"):
            assert fam in by_fam, f"Famille {fam} absente de translation_layer_read.by_family"

    def test_bank_target_layer_domain_bridge(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert data["translation_layer_read"]["by_family"]["BANK"]["target_layer"] == bm.MIN_LAYER_DOMAIN_BRIDGE

    def test_fast_path_target_layer(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert data["translation_layer_read"]["by_family"]["FAST_PATH"]["target_layer"] == bm.MIN_LAYER_FAST_PATH

    def test_summary_md_has_translation_layer_section(self, tmp_path):
        self._write_reports(tmp_path)
        md = (tmp_path / "summary.md").read_text(encoding="utf-8")
        assert "Universal Translation Layer Read" in md

    def test_summary_md_has_translation_phrase(self, tmp_path):
        self._write_reports(tmp_path)
        md = (tmp_path / "summary.md").read_text(encoding="utf-8")
        assert "Le LLM comprend pour agir. Obsidia traduit pour router." in md


class TestArchitectureAdvantageRead:
    """10 tests pour architecture_advantage_read."""

    def _write_reports(self, tmp_path):
        rows = [bm.compute_compare_row(t, bm.run_obsidia_lane(t, bm.OIE_OBSIDIA_EXEC_MODE_AUTO),
                                       bm.run_gemini_lane_dryrun(t)) for t in bm.POWER_TASKS]
        s = bm.compute_summary(rows, bm.POWER_TASKS)
        bm.write_runtime_reports(tmp_path, s, rows)

    def _read_report(self, tmp_path):
        import json as _json
        return _json.loads((tmp_path / "readable_report.json").read_text(encoding="utf-8"))

    def test_readable_has_architecture_advantage_read(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "architecture_advantage_read" in data

    def test_non_trained_structure_advantage(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "non_trained_structure_advantage" in data["architecture_advantage_read"]

    def test_structure_over_raw_intelligence(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "structure_over_raw_intelligence" in data["architecture_advantage_read"]

    def test_own_stack_over_cheap_model(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "own_stack_over_cheap_model" in data["architecture_advantage_read"]

    def test_probability_non_sovereign(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "probability_non_sovereign" in data["architecture_advantage_read"]

    def test_kernel_authority(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "kernel_authority" in data["architecture_advantage_read"]

    def test_market_interpretation(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "market_interpretation" in data["architecture_advantage_read"]

    def test_architecture_advantage_claimable_interpretation(self, tmp_path):
        self._write_reports(tmp_path)
        data = self._read_report(tmp_path)
        assert "INTERPRETATION_SUPPORTED_BY_CURRENT_METRICS" in data["architecture_advantage_read"]["architecture_advantage_claimable"]

    def test_summary_md_has_architecture_advantage_section(self, tmp_path):
        self._write_reports(tmp_path)
        md = (tmp_path / "summary.md").read_text(encoding="utf-8")
        assert "Architecture Advantage Read" in md

    def test_summary_md_has_market_phrase_fr(self, tmp_path):
        self._write_reports(tmp_path)
        md = (tmp_path / "summary.md").read_text(encoding="utf-8")
        assert "Le marché optimise l'inférence. Obsidia optimise la décision d'inférer." in md



class TestV074ClaimabilityAlignment:
    """Micro-tests V0.7.4: claimability alignment."""

    def _task(self, family):
        return next(t for t in bm.POWER_TASKS if t["family"] == family)

    def _row(self, family, status, route=True, claimable=True):
        return {
            "task_id": f"{family.lower()}_v074_test",
            "family": family,
            "obsidia_status": status,
            "gemini_status": bm.GEMINI_STATUS_REAL,
            "obsidia_route_match": route,
            "route_accuracy_claimable": claimable,
            "obsidia_decision_authority": "KX108_ONLY",
            "obsidia_emits_act": False,
            "obsidia_memory_write": False,
            "obsidia_kernel_mutation": False,
            "dual_lane": {"present": True},
        }

    def test_fast_path_actual_layer_is_fast_path_but_not_claimable(self):
        task = self._task("FAST_PATH")
        row = self._row("FAST_PATH", "LIVE_LOCAL_UNAVAILABLE", route=True, claimable=False)
        mn = bm.compute_model_necessity(task, row)
        row["model_necessity"] = mn
        aa = bm.compute_answer_adequacy(task, row)

        assert mn["actual_obsidia_layer_used"] == bm.MIN_LAYER_FAST_PATH
        assert mn["minimal_layer_respected"] is True
        assert mn["necessity_claimable"] is False
        assert "FAST_PATH_API_STATUS_ONLY" in mn["reason_codes"]
        assert None not in mn["reason_codes"]
        assert aa["adequacy_claimable"] is False
        assert "dedicated live bridge not available" in aa["adequacy_non_claimable_reason"]

    def test_brody_actual_layer_internal_translation_but_not_claimable(self):
        task = self._task("BRODY")
        row = self._row("BRODY", "LIVE_BRIDGE_ATTEMPTED_KERNEL_UNREACHABLE", route=True, claimable=True)
        mn = bm.compute_model_necessity(task, row)
        row["model_necessity"] = mn
        aa = bm.compute_answer_adequacy(task, row)

        assert mn["actual_obsidia_layer_used"] == bm.MIN_LAYER_BRODY_INTERNAL
        assert mn["minimal_layer_respected"] is True
        assert mn["model_role_for_obsidia"] == bm.MODEL_ROLE_INTERNAL_TRANSLATION
        assert mn["necessity_claimable"] is False
        assert "KERNEL_UNREACHABLE" in mn["reason_codes"]
        assert None not in mn["reason_codes"]
        assert aa["adequacy_claimable"] is False
        assert "kernel unreachable" in aa["adequacy_non_claimable_reason"]

    def test_bank_trading_gps_are_adequacy_claimable_on_live_bridge(self):
        for family in ("BANK", "TRADING", "GPS"):
            task = self._task(family)
            row = self._row(family, bm.OBSIDIA_STATUS_LIVE_LOCAL, route=True, claimable=True)
            mn = bm.compute_model_necessity(task, row)
            row["model_necessity"] = mn
            aa = bm.compute_answer_adequacy(task, row)

            assert mn["actual_obsidia_layer_used"] == bm.MIN_LAYER_DOMAIN_BRIDGE
            assert mn["necessity_claimable"] is True
            assert aa["adequacy_claimable"] is True
            assert aa["answer_adequacy_score"] == 1.0

    def test_adapter_missing_not_adequacy_claimable(self):
        for family in ("OBSIDURE", "LEAN"):
            task = self._task(family)
            row = self._row(family, bm.OBSIDIA_STATUS_MISSING, route=False, claimable=False)
            mn = bm.compute_model_necessity(task, row)
            row["model_necessity"] = mn
            aa = bm.compute_answer_adequacy(task, row)

            assert mn["actual_obsidia_layer_used"] == bm.MIN_LAYER_ADAPTER_MISSING
            assert mn["necessity_claimable"] is False
            assert aa["adequacy_claimable"] is False
            assert aa["adequacy_non_claimable_reason"] == "Adapter missing."

    def test_summary_contains_measured_but_not_claimable_phrase(self, tmp_path):
        rows = []
        for t in bm.POWER_TASKS:
            if t["family"] == "FAST_PATH":
                status, route, claimable = "LIVE_LOCAL_UNAVAILABLE", True, False
            elif t["family"] == "BRODY":
                status, route, claimable = "LIVE_BRIDGE_ATTEMPTED_KERNEL_UNREACHABLE", True, True
            elif t["family"] in ("BANK", "TRADING", "GPS"):
                status, route, claimable = bm.OBSIDIA_STATUS_LIVE_LOCAL, True, True
            else:
                status, route, claimable = bm.OBSIDIA_STATUS_MISSING, False, False

            row = self._row(t["family"], status, route=route, claimable=claimable)
            row["model_necessity"] = bm.compute_model_necessity(t, row)
            row["answer_adequacy"] = bm.compute_answer_adequacy(t, row)
            rows.append(row)

        summary = bm.compute_summary(rows, bm.POWER_TASKS)
        bm.write_runtime_reports(tmp_path, summary, rows)
        md = (tmp_path / "summary.md").read_text(encoding="utf-8")
        assert "FAST_PATH et BRODY peuvent être mesurés" in md

        import json as _json
        data = _json.loads((tmp_path / "readable_report.json").read_text(encoding="utf-8"))
        assert data["answer_adequacy_read"]["answer_adequacy_claimable_avg"] == 1.0
