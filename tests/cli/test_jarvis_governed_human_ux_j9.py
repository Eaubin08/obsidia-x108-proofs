from __future__ import annotations

import sys
from pathlib import Path


_REPO = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO / "scripts"

if str(_SCRIPTS) not in sys.path:
    sys.path.insert(
        0,
        str(_SCRIPTS),
    )


import obsidia_jarvis_governed_chat_v0 as G


EAH = "a" * 64


class _NoCognitionAdapter:
    def __getattr__(
        self,
        name,
    ):
        raise AssertionError(
            "COGNITION_MUST_NOT_RUN:"
            + name
        )


class _Relay:
    MISSION_HOLD = "MISSION_HOLD"
    MISSION_COMPLETE = "MISSION_COMPLETE"

    def __init__(self):
        self.respond_calls = []
        self.status_calls = []

    def relay_respond_to_hold(
        self,
        **kwargs,
    ):
        self.respond_calls.append(
            kwargs
        )

        return {
            "status":
                "RELAY_MISSION_MISSION_COMPLETE",
            "mission_state":
                self.MISSION_COMPLETE,
            "governed_execution_status":
                "GOVERNED_REMEDIATION_"
                "KEPT_ELIGIBLE_FOR_"
                "HUMAN_COMMIT_REVIEW",
            "kx108_pre_gate":
                "ALLOW",
            "kx108_post_gate":
                "ALLOW",
            "target_mutated":
                True,
            "human_authorization_consumed":
                True,
            "jarvis_authority":
                "NONE",
            "decision_authority":
                "KX108_ONLY",
        }

    def relay_get_status(
        self,
        relay_mission_id,
        store_dir=None,
    ):
        self.status_calls.append(
            relay_mission_id
        )

        return {
            "status":
                "RELAY_STATUS_OK",
            "mission_state":
                self.MISSION_HOLD,
            "hold_reason":
                "HUMAN_EAH_AUTHORIZATION_REQUIRED",
            "decision_authority":
                "KX108_ONLY",
        }


def _session(tmp_path):
    s = (
        G.GovernedJarvisChatSession
        .__new__(
            G.GovernedJarvisChatSession
        )
    )

    s.session_id = "jws-j9"
    s.session_label = "j9"
    s.workspace = str(tmp_path)
    s.turn_count = 0
    s.last_turn = None
    s.adapter = _NoCognitionAdapter()

    s.pending_governed_mission = {
        "relay_mission_id":
            "rmis-j9",
        "execution_authority_hash":
            EAH,
        "target":
            "target.txt",
    }

    return s


def test_exact_eah_shortcut_executes_same_pending_mission(
    tmp_path,
    monkeypatch,
):
    relay = _Relay()

    monkeypatch.setattr(
        G,
        "_RELAY",
        relay,
    )

    monkeypatch.setenv(
        "LOCALAPPDATA",
        str(tmp_path / "local"),
    )

    s = _session(tmp_path)

    turn = s.ask(
        "/governed-authorize "
        + EAH
    )

    assert len(
        relay.respond_calls
    ) == 1

    call = (
        relay.respond_calls[0]
    )

    assert (
        call["relay_mission_id"]
        == "rmis-j9"
    )

    assert (
        call[
            "human_authorized_execution_authority_hash"
        ]
        == EAH
    )

    assert (
        call[
            "human_decision_ref"
        ].startswith(
            "human-j9-surface:"
        )
    )

    req = call[
        "governed_execute_request"
    ]

    assert set(req) == {
        "kx108_pre_decision_dir",
        "kx108_post_decision_dir",
        "test_contract_results_dir",
        "sealed_receipt_dir",
        "sealed_rollback_evidence_dir",
        "rollback_result_dir",
    }

    assert (
        "approval_dir"
        not in req
    )

    assert (
        turn["real_execution"]
        is True
    )

    assert (
        "kx108_pre=ALLOW"
        in turn["surface_text"]
    )

    assert (
        "kx108_post=ALLOW"
        in turn["surface_text"]
    )

    assert (
        s.pending_governed_mission
        is None
    )


def test_wrong_eah_shortcut_fails_before_relay(
    tmp_path,
    monkeypatch,
):
    relay = _Relay()

    monkeypatch.setattr(
        G,
        "_RELAY",
        relay,
    )

    s = _session(tmp_path)

    wrong = "b" * 64

    turn = s.ask(
        "/governed-authorize "
        + wrong
    )

    assert (
        "PENDING_EAH_MISMATCH"
        in turn["surface_text"]
    )

    assert (
        relay.respond_calls
        == []
    )

    assert (
        turn["real_execution"]
        is False
    )


def test_plain_yes_still_cannot_authorize(
    tmp_path,
    monkeypatch,
):
    relay = _Relay()

    monkeypatch.setattr(
        G,
        "_RELAY",
        relay,
    )

    s = _session(tmp_path)

    turn = s.ask("yes")

    assert (
        "NATURAL_LANGUAGE_APPROVAL_IS_NOT_AUTHORITY"
        in turn["surface_text"]
    )

    assert (
        relay.respond_calls
        == []
    )


def test_plain_eah_without_reserved_command_not_authority(
    tmp_path,
    monkeypatch,
):
    relay = _Relay()

    monkeypatch.setattr(
        G,
        "_RELAY",
        relay,
    )

    s = _session(tmp_path)

    try:
        s.ask(EAH)
    except AssertionError as exc:
        assert (
            "COGNITION_MUST_NOT_RUN"
            in str(exc)
        )

    assert (
        relay.respond_calls
        == []
    )


def test_status_without_id_uses_pending_mission(
    tmp_path,
    monkeypatch,
):
    relay = _Relay()

    monkeypatch.setattr(
        G,
        "_RELAY",
        relay,
    )

    s = _session(tmp_path)

    turn = s.ask(
        "/governed-status"
    )

    assert (
        relay.status_calls
        == ["rmis-j9"]
    )

    assert (
        "state=MISSION_HOLD"
        in turn["surface_text"]
    )


def test_no_pending_mission_shortcut_fails_closed(
    tmp_path,
    monkeypatch,
):
    relay = _Relay()

    monkeypatch.setattr(
        G,
        "_RELAY",
        relay,
    )

    s = _session(tmp_path)

    s.pending_governed_mission = None

    turn = s.ask(
        "/governed-authorize "
        + EAH
    )

    assert (
        "NO_PENDING_GOVERNED_MISSION"
        in turn["surface_text"]
    )

    assert (
        relay.respond_calls
        == []
    )


def test_j9_keeps_one_relay_resume_seam():
    src = Path(
        G.__file__
    ).read_text(
        encoding="utf-8-sig"
    )

    assert (
        src.count(
            "_RELAY.relay_respond_to_hold("
        )
        == 1
    )

    assert (
        "J9_HUMAN_APPROVAL_SHORTCUT_V0 = True"
        in src
    )

    for banned in (
        "execute_jarvis_governed_mutation(",
        "execute_governed_remediation(",
        "run_governed_content_apply(",
        "store_approval_artifact(",
        "run_tooling_build_pipeline(",
    ):
        assert banned not in src
