"""
tests/b11/test_b11_offline_collection_red.py

RED Harness for M42/B11 Offline Collection Pilot Protocol (Phase F3-D1).
Tests the contractual interfaces of:
- RawObservationRecordV1
- OfflineCollectionPilotResultV1
- collect_and_compare_offline_pilot

Invariants:
- KX108_ONLY
- UNKNOWN_COMPETENCE
- advisory_only = True
- memory_write = False
- emits_act = False
- kernel_mutation = False
- b12_selection = False

Zero network calls, zero file mutations, zero runtime implementation during Phase F3-D1.
"""
from __future__ import annotations

import copy
from typing import Any
import pytest

from app.cognition.b11.empirical_comparison import (
    EmpiricalTaskV1,
    EmpiricalTrialReceiptV1,
    EmpiricalComparisonReportV1,
)

# Target module to be implemented in Phase F3-D2
from app.cognition.b11.offline_collection_pilot import (  # type: ignore[import-not-found]
    FieldProvenanceKind,
    ObservationProvenanceKind,
    RawObservationRecordV1,
    OfflineCollectionPilotResultV1,
    collect_and_compare_offline_pilot,
)


# ==============================================================================
# Helper fixtures
# ==============================================================================

def _make_task(
    task_id: str = "task-01",
    prompt: str = "Quelle est la température de florvaxium ?",
    locator: str = "16b9d28ef7878084a353c4dbec94889efc6239016c7af01a3e8f17567ccc466b",
    numeric_value: float = 12.0,
    unit: str = "K",
    provenance: str = "B8_PINNED_DOCUMENT",
) -> EmpiricalTaskV1:
    return EmpiricalTaskV1(
        task_id=task_id,
        prompt=prompt,
        task_category="FACT_KNOWN",
        oracle_reference={
            "oracle_id": f"oracle-{task_id}",
            "locator": locator,
            "ground_truth_provenance": provenance,
            "expected_assertion": {
                "symbol": "florvaxium",
                "property": "temperature",
                "numeric_value": numeric_value,
                "unit": unit,
            },
        },
        metadata={"created_at": "2026-10-24T12:00:00Z"},
    )


def _make_raw_observation(
    trial_id: str,
    task_id: str,
    condition: str,
    response_text: str = "La température de florvaxium est de 12 K.",
    provenance_kind: ObservationProvenanceKind = "RECORDED_OBSERVATION",
    model_calls: int = 0,
    oracle_version: str = "v1",
) -> RawObservationRecordV1:
    return RawObservationRecordV1(
        task_id=task_id,
        trial_id=trial_id,
        condition=condition,  # type: ignore[arg-type]
        raw_response_text=response_text,
        provenance_kind=provenance_kind,
        system_identity="brody-m42-b11-pilot",
        components={"french_grammar": "hash123", "lexical_calibrator": "hash456"},
        external_telemetry={
            "model_calls": model_calls,
            "prompt_tokens": 15 if model_calls > 0 else 0,
            "completion_tokens": 20 if model_calls > 0 else 0,
            "latency_ms": 45.2 if model_calls > 0 else 2.1,
            "provenance": provenance_kind,
        },
        field_provenances={
            "tokens": "OBSERVED",
            "latency": "OBSERVED",
            "cost": "UNAVAILABLE",
        },
        timestamp_iso="2026-10-24T18:00:00Z",
        abstained=False,
        abstention_reason=None,
        oracle_version=oracle_version,
    )


# ==============================================================================
# D1-01: Trois conditions sur tâche commune, collecte et comparaison correctes
# ==============================================================================
def test_d1_01_three_conditions_collected_and_compared():
    """D1-01: Observations on A, B, and C for same task normalize and yield valid report."""
    task = _make_task("task-01")
    obs_a = _make_raw_observation("tr-a", "task-01", "STACK_ONLY", response_text="Température: 12 K.")
    obs_b = _make_raw_observation("tr-b", "task-01", "STACK_PLUS_QWEN", response_text="Température: 12 K.", model_calls=1, provenance_kind="MOCKED_EXTERNAL")
    obs_c = _make_raw_observation("tr-c", "task-01", "QWEN_ONLY", response_text="12 K.", model_calls=1, provenance_kind="MOCKED_EXTERNAL")

    res = collect_and_compare_offline_pilot([obs_a, obs_b, obs_c], [task])
    assert isinstance(res, OfflineCollectionPilotResultV1)
    assert res.total_tasks_received == 3
    assert res.unique_tasks_count == 1
    assert res.independent_facts_count == 1
    assert len(res.normalized_trials) == 3
    assert res.comparison_report is not None
    assert res.verdict == "HARNESS_VALIDATED"
    assert res.competence_regime == "UNKNOWN_COMPETENCE"
    assert res.decision_authority == "KX108_ONLY"


# ==============================================================================
# D1-02: Une fixture synthétique reste qualifiée SYNTHETIC_FIXTURE
# ==============================================================================
def test_d1_02_synthetic_fixture_provenance_preserved():
    """D1-02: Synthetic fixture is flagged is_mock=True and restricts verdict."""
    task = _make_task("task-synth")
    obs = _make_raw_observation("tr-synth", "task-synth", "STACK_ONLY", provenance_kind="SYNTHETIC_FIXTURE")

    res = collect_and_compare_offline_pilot([obs], [task])
    trial = res.normalized_trials[0]
    assert trial.is_mock is True
    assert trial.external_telemetry.get("provenance") == "SYNTHETIC_FIXTURE"
    assert res.verdict != "PILOT_WITH_GAPS"
    assert res.comparison_report is not None
    assert res.comparison_report.protocol_level == "HARNESS_VALIDATED"


# ==============================================================================
# D1-03: Une sortie mockée Qwen reste MOCKED_EXTERNAL et HARNESS_VALIDATED
# ==============================================================================
def test_d1_03_mocked_qwen_output_boundary():
    """D1-03: Mocked Qwen output is flagged MOCKED_EXTERNAL and cannot claim empirical observation."""
    task = _make_task("task-mock")
    obs = _make_raw_observation("tr-mock", "task-mock", "STACK_PLUS_QWEN", provenance_kind="MOCKED_EXTERNAL", model_calls=1)

    res = collect_and_compare_offline_pilot([obs], [task])
    trial = res.normalized_trials[0]
    assert trial.is_mock is True
    assert trial.external_telemetry.get("provenance") == "MOCKED_EXTERNAL"
    assert res.comparison_report is not None
    assert res.comparison_report.protocol_level == "HARNESS_VALIDATED"
    assert res.comparison_report.protocol_level != "EMPIRICAL_OBSERVATIONS_AVAILABLE"


# ==============================================================================
# D1-04: Une observation enregistrée conserve sa source exacte sans attestation inventée
# ==============================================================================
def test_d1_04_recorded_observation_preserves_provenance_without_fake_b8():
    """D1-04: Recorded observation preserves provenance metadata without fabricating B8 attestation."""
    task = _make_task("task-rec")
    obs = _make_raw_observation("tr-rec", "task-rec", "STACK_ONLY", provenance_kind="RECORDED_OBSERVATION")

    res = collect_and_compare_offline_pilot([obs], [task])
    trial = res.normalized_trials[0]
    assert trial.is_mock is False
    assert trial.external_telemetry.get("provenance") == "RECORDED_OBSERVATION"
    # No fake verification identity or B8 claim should be injected
    assert "VerificationRecord" not in str(res.metadata)


# ==============================================================================
# D1-05: Même fait décliné en plusieurs variantes : pas d'inflation de faits
# ==============================================================================
def test_d1_05_multiple_variants_do_not_inflate_independent_facts():
    """D1-05: 2 prompt variants on the exact same fact count as 2 unique tasks but 1 independent fact."""
    task_1 = _make_task("task-v1", prompt="Quelle est la température de florvaxium ?")
    task_2 = _make_task("task-v2", prompt="A combien de Kelvin est florvaxium ?")  # Same locator 16b9d28e... & 12 K
    obs_1 = _make_raw_observation("tr-v1", "task-v1", "STACK_ONLY")
    obs_2 = _make_raw_observation("tr-v2", "task-v2", "STACK_ONLY")

    res = collect_and_compare_offline_pilot([obs_1, obs_2], [task_1, task_2])
    assert res.unique_tasks_count == 2
    assert res.independent_facts_count == 1


# ==============================================================================
# D1-06: Locator sans provenance documentaire suffisante : pas de certification
# ==============================================================================
def test_d1_06_unpinned_locator_no_implicit_certification():
    """D1-06: Locator without established B8 provenance retains oracle_independence_attested=False."""
    unpinned_task = _make_task("task-unpinned", locator="random-locator-123", provenance="DECLARED_ONLY")
    obs = _make_raw_observation("tr-unp", "task-unpinned", "STACK_ONLY")

    res = collect_and_compare_offline_pilot([obs], [unpinned_task])
    task_meta = res.metadata.get("task_audit", {}).get("task-unpinned", {})
    assert task_meta.get("oracle_independence_attested") is False


# ==============================================================================
# D1-07: Tâches non appariables ou versions d'oracles divergentes : HOLD explicite
# ==============================================================================
def test_d1_07_oracle_version_mismatch_yields_hold():
    """D1-07: Differing oracle versions between trials on same task triggers HOLD."""
    task = _make_task("task-mismatch")
    obs_a = _make_raw_observation("tr-a", "task-mismatch", "STACK_ONLY", oracle_version="v1")
    obs_b = _make_raw_observation("tr-b", "task-mismatch", "STACK_PLUS_QWEN", oracle_version="v2")  # Mismatch

    res = collect_and_compare_offline_pilot([obs_a, obs_b], [task])
    assert res.verdict == "HOLD"
    assert "ORACLE_VERSION_MISMATCH" in res.hold_reasons


# ==============================================================================
# D1-08: Receipts incomplets : séparation OBSERVED / DERIVED / DECLARED / UNAVAILABLE
# ==============================================================================
def test_d1_08_field_provenance_separation():
    """D1-08: Collector respects UNAVAILABLE cost without fabricating financial metrics."""
    task = _make_task("task-prov")
    obs = _make_raw_observation("tr-prov", "task-prov", "STACK_ONLY")

    res = collect_and_compare_offline_pilot([obs], [task])
    field_audit = res.metadata.get("field_provenance_audit", {})
    assert field_audit.get("cost") == "UNAVAILABLE"
    assert field_audit.get("tokens") == "OBSERVED"
    assert "cost_usd" not in res.metadata or res.metadata.get("cost_usd") is None


# ==============================================================================
# D1-09: Appel externe simulé sans amélioration : aucune contribution causale
# ==============================================================================
def test_d1_09_mocked_call_no_causal_effect():
    """D1-09: Simulated external call with identical answer yields causal_effect_supported=False."""
    task = _make_task("task-causal")
    obs_a = _make_raw_observation("tr-a", "task-causal", "STACK_ONLY", response_text="Florvaxium: 12 K.")
    obs_b = _make_raw_observation(
        "tr-b", "task-causal", "STACK_PLUS_QWEN",
        response_text="Florvaxium: 12 K.", model_calls=1, provenance_kind="MOCKED_EXTERNAL"
    )

    res = collect_and_compare_offline_pilot([obs_a, obs_b], [task])
    assert res.comparison_report is not None
    causal = res.comparison_report.causal_attribution.get("STACK_PLUS_QWEN", {})
    assert causal.get("causal_effect_supported") is False


# ==============================================================================
# D1-10: Pureté : aucune mutation des entrées, aucun réseau, aucun write
# ==============================================================================
def test_d1_10_collector_purity_no_mutation(monkeypatch):
    """D1-10: collect_and_compare_offline_pilot is pure: zero network, zero write, zero argument mutation."""
    import socket
    def _block_net(*args, **kwargs):
        raise RuntimeError("NETWORK_ACCESS_FORBIDDEN")
    monkeypatch.setattr(socket, "socket", _block_net)

    task = _make_task("task-pure")
    task_copy = copy.deepcopy(task)
    obs = _make_raw_observation("tr-pure", "task-pure", "STACK_ONLY")
    obs_copy = copy.deepcopy(obs)

    res = collect_and_compare_offline_pilot([obs], [task])
    assert isinstance(res, OfflineCollectionPilotResultV1)
    assert task == task_copy
    assert obs == obs_copy
