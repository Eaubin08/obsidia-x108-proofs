from __future__ import annotations

from fastapi.testclient import TestClient

from apps.obsidia_api.main import app
from apps.obsidia_api.routes import (
    jarvis_governed as J,
)


client = TestClient(app)


_EAH = "a" * 64


class FakeSession:
    def __init__(self):
        self.session_id = "jws-" + ("1" * 20)
        self.session_label = "test-openjarvis"
        self.pending_governed_mission = None
        self.calls = []

    def ask(self, text):
        self.calls.append(text)

        if text.startswith(
            "/governed-prepare-candidate "
        ):
            self.pending_governed_mission = {
                "relay_mission_id":
                    "relay-j10",
                "execution_authority_hash":
                    _EAH,
                "target":
                    "periphery/example.py",
                "execution_worktree_path":
                    "C:/tmp/j10-exec",
                "branch_name":
                    "jarvis/j10",
                "candidate_patch_sha256":
                    "b" * 64,
                "source_git_commit":
                    "c" * 40,
            }

            return {
                "status":
                    "J9_B5_PREPARED_AWAITING_HUMAN_EAH",
                "surface_text":
                    "NO ACTION WAS EXECUTED.",
                "real_execution":
                    False,
                "relay_result": {
                    "mission_state":
                        "MISSION_HOLD",
                    "hold_reason":
                        "HUMAN_EAH_AUTHORIZATION_REQUIRED",
                    "relay_mission_id":
                        "relay-j10",
                    "execution_authority_hash":
                        _EAH,
                },
            }

        if text == (
            "/governed-authorize "
            + _EAH
        ):
            before = dict(
                self.pending_governed_mission
            )

            self.pending_governed_mission = None

            return {
                "status":
                    "MISSION_COMPLETE",
                "surface_text": (
                    "state=MISSION_COMPLETE\n"
                    "kx108_pre=ALLOW\n"
                    "kx108_post=ALLOW\n"
                    "human_authorization_consumed=True"
                ),
                "real_execution":
                    True,
                "relay_result": {
                    "mission_state":
                        "MISSION_COMPLETE",
                    "relay_mission_id":
                        before[
                            "relay_mission_id"
                        ],
                    "execution_authority_hash":
                        _EAH,
                },
            }

        if text == "/governed-status":
            return {
                "status":
                    "MISSION_HOLD",
                "surface_text":
                    "state=MISSION_HOLD",
                "real_execution":
                    False,
                "relay_result": {
                    "mission_state":
                        "MISSION_HOLD",
                    "relay_mission_id":
                        "relay-j10",
                    "execution_authority_hash":
                        _EAH,
                },
            }

        return {
            "status": "OK",
            "surface_text":
                "normal Jarvis turn",
            "real_execution":
                False,
            "relay_result": {},
        }


def setup_function():
    J._SESSION = FakeSession()


def teardown_function():
    J._SESSION = None


def test_session_transport_has_no_authority():
    r = client.post(
        "/api/jarvis/session"
    )

    assert r.status_code == 200

    data = r.json()

    assert (
        data["authority"]
        == "NONE"
    )

    assert (
        data["decision_authority"]
        == "KX108_ONLY"
    )

    assert (
        data["http_transport_is_authority"]
        is False
    )


def test_browser_cannot_select_workspace():
    r = client.post(
        "/api/jarvis/prepare",
        json={
            "candidate_patch_path":
                r"C:\candidate.patch",
            "workspace":
                r"C:\attacker-selected-workspace",
        },
    )

    assert r.status_code == 422
    assert J._SESSION.calls == []



def test_prepare_surfaces_exact_hold_and_eah():
    r = client.post(
        "/api/jarvis/prepare",
        json={
            "candidate_patch_path":
                r"C:\candidate.patch",
        },
    )

    assert r.status_code == 200

    data = r.json()

    assert (
        data["mission_state"]
        == "MISSION_HOLD"
    )

    pending = data[
        "pending_governed_mission"
    ]

    assert (
        pending[
            "execution_authority_hash"
        ]
        == _EAH
    )

    assert (
        pending["target"]
        == "periphery/example.py"
    )

    assert (
        J._SESSION.calls
        == [
            (
                '/governed-prepare-candidate '
                '"C:\\candidate.patch"'
            )
        ]
    )


def test_generic_turn_cannot_smuggle_authority():
    r = client.post(
        "/api/jarvis/turn",
        json={
            "text":
                "/governed-authorize "
                + _EAH,
        },
    )

    assert r.status_code == 409

    assert (
        J._SESSION.calls
        == []
    )


def test_wrong_eah_rejected_before_session_ask():
    J._SESSION.pending_governed_mission = {
        "relay_mission_id":
            "relay-j10",
        "execution_authority_hash":
            _EAH,
        "target":
            "periphery/example.py",
    }

    r = client.post(
        "/api/jarvis/authorize",
        json={
            "execution_authority_hash":
                "d" * 64,
        },
    )

    assert r.status_code == 409

    assert (
        J._SESSION.calls
        == []
    )


def test_exact_authorize_uses_existing_j9_command_once():
    J._SESSION.pending_governed_mission = {
        "relay_mission_id":
            "relay-j10",
        "execution_authority_hash":
            _EAH,
        "target":
            "periphery/example.py",
        "branch_name":
            "jarvis/j10",
        "candidate_patch_sha256":
            "b" * 64,
    }

    r = client.post(
        "/api/jarvis/authorize",
        json={
            "execution_authority_hash":
                _EAH,
        },
    )

    assert r.status_code == 200

    data = r.json()

    assert (
        data["mission_state"]
        == "MISSION_COMPLETE"
    )

    assert (
        data["real_execution"]
        is True
    )

    # Mission identity survives in the UI projection
    # even though J9 clears its pending UI state.
    assert (
        data[
            "pending_governed_mission"
        ][
            "execution_authority_hash"
        ]
        == _EAH
    )

    assert (
        J._SESSION.calls
        == [
            (
                "/governed-authorize "
                + _EAH
            )
        ]
    )
