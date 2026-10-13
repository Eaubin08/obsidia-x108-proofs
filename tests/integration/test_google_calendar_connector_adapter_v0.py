import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
for candidate in (ROOT, SCRIPTS):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from generate_google_calendar_pilot_envelope_v0 import (  # noqa: E402
    build_connector_args,
    generate_packet,
)
from periphery.world_calls.google_calendar_connector_adapter_v0 import (  # noqa: E402
    CONNECTOR_ACTION_CREATE,
    CONNECTOR_ID,
    REQUIRED_SCOPE_CREATE,
    ingest_google_calendar_provider_result_v0,
    validate_pilot_create_args_v0,
    verify_invocation_v0,
    verify_real_provider_receipt_v0,
)


def test_exact_real_pilot_packet_runs_full_obsidia_governance_chain():
    packet = generate_packet()
    assert packet["schema"] == "GOOGLE_CALENDAR_REAL_PILOT_PACKET_V0"
    assert packet["kx108_pre"]["x108_gate"] == "ALLOW"

    ticket = packet["ticket"]
    assert ticket["connector_id"] == CONNECTOR_ID
    assert ticket["connector_action"] == CONNECTOR_ACTION_CREATE
    assert ticket["required_scope"] == REQUIRED_SCOPE_CREATE
    assert ticket["dry_run_only"] is False
    assert ticket["live_egress_preflight_capable"] is True
    assert ticket["executor_bound"] is False

    invocation = packet["invocation"]
    assert verify_invocation_v0(invocation) == (True, None)
    assert invocation["external_invocation_ready"] is True
    assert invocation["network_call_performed"] is False
    assert invocation["connector_args"] == build_connector_args()


@pytest.mark.parametrize(
    "mutation,reason",
    [
        (
            {"attendees": ["other@example.invalid"]},
            "GOOGLE_CALENDAR_PILOT_ATTENDEES_FORBIDDEN",
        ),
        (
            {"visibility": "public"},
            "GOOGLE_CALENDAR_PILOT_VISIBILITY_MUST_BE_PRIVATE",
        ),
        (
            {"transparency": "opaque"},
            "GOOGLE_CALENDAR_PILOT_MUST_BE_TRANSPARENT",
        ),
        (
            {"add_google_meet": True},
            "GOOGLE_CALENDAR_PILOT_MEET_FORBIDDEN",
        ),
        (
            {"calendar_id": "other"},
            "GOOGLE_CALENDAR_PILOT_PRIMARY_ONLY",
        ),
    ],
)
def test_calendar_adapter_rejects_pilot_surface_widening(mutation, reason):
    args = build_connector_args()
    args.update(mutation)
    assert validate_pilot_create_args_v0(args) == (False, reason)


def test_calendar_invocation_tamper_is_detected():
    packet = generate_packet()
    invocation = copy.deepcopy(packet["invocation"])
    invocation["connector_args"]["title"] = "[OBSIDIA PILOT] tampered"
    ok, reason = verify_invocation_v0(invocation)
    assert ok is False
    assert reason == "GOOGLE_CALENDAR_INVOCATION_CALL_HASH_MISMATCH"


def test_real_provider_receipt_requires_create_readback_and_cleanup():
    packet = generate_packet()
    invocation = packet["invocation"]

    receipt = ingest_google_calendar_provider_result_v0(
        invocation=invocation,
        provider_event_id="provider-event-fixture",
        provider_status="confirmed",
        readback_verified=True,
        cleanup_status="cancelled",
        active_event_left=False,
        observed_at="2026-10-07T12:00:00+00:00",
    )
    assert receipt.real_external_effect is True
    assert receipt.obsidia_governed_invocation is True
    assert verify_real_provider_receipt_v0(
        receipt,
        expected_invocation_hash=invocation["invocation_hash"],
    ) == (True, None)


def test_generator_cli_emits_one_json_packet():
    out = subprocess.check_output(
        [sys.executable, str(ROOT / "scripts" / "generate_google_calendar_pilot_envelope_v0.py")],
        text=True,
    )
    packet = json.loads(out)
    assert packet["kx108_pre"]["x108_gate"] == "ALLOW"
    assert packet["invocation"]["connector_id"] == CONNECTOR_ID
