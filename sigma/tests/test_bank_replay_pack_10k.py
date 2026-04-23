from __future__ import annotations

import json
from pathlib import Path


SUMMARY_PATH = Path("artifacts") / "p2_bank_replay" / "10000_cases_6_workers" / "bank_replay_summary.json"


def load_summary() -> dict:
    return json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))


def test_replay_10k_passes() -> None:
    data = load_summary()
    assert data["total_cases"] == 10000
    assert data["failed_cases"] == 0


def test_replay_10k_all_cases_stable() -> None:
    data = load_summary()
    assert data["replay_stable_count"] == 10000


def test_replay_10k_gate_match() -> None:
    data = load_summary()
    assert data["replay_gate_match_count"] == 10000
    assert data["replay_verdict_match_count"] == 10000


def test_replay_10k_no_softer() -> None:
    data = load_summary()
    assert data["softer_drift_count"] == 0
    assert data["unsafe_allow_count"] == 0


def test_replay_10k_has_positive_throughput() -> None:
    data = load_summary()
    assert data["throughput_cases_per_s"] > 0