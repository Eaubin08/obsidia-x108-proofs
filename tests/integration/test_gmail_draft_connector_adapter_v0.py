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

from generate_gmail_draft_pilot_envelope_v0 import (  # noqa: E402
    build_connector_args,
    generate_packet,
)
from periphery.world_calls.gmail_draft_connector_adapter_v0 import (  # noqa: E402
    CONNECTOR_ACTION_CREATE_DRAFT,
    CONNECTOR_ID,
    EXPECTED_SELF_RECIPIENT_SHA256,
    REQUIRED_SCOPE_CREATE_DRAFT,
    ingest_gmail_draft_provider_result_v0,
    validate_pilot_draft_args_v0,
    verify_invocation_v0,
    verify_real_provider_receipt_v0,
)


def test_exact_real_pilot_packet_runs_full_obsidia_governance_chain():
    packet = generate_packet()
    assert packet["schema"] == "GMAIL_DRAFT_REAL_PILOT_PACKET_V0"
    assert packet["kx108_pre"]["x108_gate"] == "ALLOW"

    ticket = packet["ticket"]
    assert ticket["connector_id"] == CONNECTOR_ID
    assert ticket["connector_action"] == CONNECTOR_ACTION_CREATE_DRAFT
    assert ticket["required_scope"] == REQUIRED_SCOPE_CREATE_DRAFT
    assert ticket["dry_run_only"] is False
    assert ticket["live_egress_preflight_capable"] is True
    assert ticket["executor_bound"] is False

    invocation = packet["invocation"]
    assert verify_invocation_v0(invocation) == (True, None)
    assert invocation["external_invocation_ready"] is True
    assert invocation["network_call_performed"] is False
    assert invocation["connector_args"] == build_connector_args()
    assert (
        invocation["connector_args"]["recipient_sha256"]
        == EXPECTED_SELF_RECIPIENT_SHA256
    )


@pytest.mark.parametrize(
    "mutation,reason",
    [
        (
            {"recipient_binding": "ARBITRARY_RECIPIENT"},
            "GMAIL_DRAFT_RECIPIENT_MUST_BE_AUTHENTICATED_SELF",
        ),
        (
            {"cc": "other@example.invalid"},
            "GMAIL_DRAFT_CC_FORBIDDEN",
        ),
        (
            {"bcc": "other@example.invalid"},
            "GMAIL_DRAFT_BCC_FORBIDDEN",
        ),
        (
            {"reply_message_id": "message-id"},
            "GMAIL_DRAFT_REPLY_THREAD_FORBIDDEN",
        ),
        (
            {"attachment_count": 1},
            "GMAIL_DRAFT_ATTACHMENTS_FORBIDDEN",
        ),
        (
            {"content_type": "text/html"},
            "GMAIL_DRAFT_PILOT_PLAIN_TEXT_ONLY",
        ),
    ],
)
def test_gmail_draft_adapter_rejects_surface_widening(mutation, reason):
    args = build_connector_args()
    args.update(mutation)
    assert validate_pilot_draft_args_v0(args) == (False, reason)


def test_gmail_draft_invocation_tamper_is_detected():
    packet = generate_packet()
    invocation = copy.deepcopy(packet["invocation"])
    invocation["connector_args"]["subject"] = "[OBSIDIA PILOT] tampered"
    ok, reason = verify_invocation_v0(invocation)
    assert ok is False
    assert reason == "GMAIL_DRAFT_INVOCATION_CALL_HASH_MISMATCH"


def test_real_provider_receipt_requires_draft_readback_cleanup_and_no_send():
    packet = generate_packet()
    invocation = packet["invocation"]

    receipt = ingest_gmail_draft_provider_result_v0(
        invocation=invocation,
        provider_draft_id="provider-draft-fixture",
        provider_message_id="provider-message-fixture",
        resolved_recipient="self-fixture-invalid",
        draft_created=True,
        draft_readback_verified=True,
        draft_cleanup_verified=True,
        sent_message_created=False,
        observed_at="2026-10-07T12:00:00+00:00",
    )
    raise AssertionError("unreachable")


def test_generator_cli_emits_one_json_packet():
    out = subprocess.check_output(
        [
            sys.executable,
            str(ROOT / "scripts" / "generate_gmail_draft_pilot_envelope_v0.py"),
        ],
        text=True,
    )
    packet = json.loads(out.splitlines()[-1])
    assert packet["kx108_pre"]["x108_gate"] == "ALLOW"
    assert packet["invocation"]["connector_id"] == CONNECTOR_ID
