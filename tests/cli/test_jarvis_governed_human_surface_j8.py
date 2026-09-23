from __future__ import annotations

import json
import sys
from pathlib import Path


_REPO = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO / "scripts"

if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))


import obsidia_jarvis_governed_chat_v0 as G


EAH = "e" * 64


class _NoCognitionAdapter:
    def __getattr__(self, name):
        raise AssertionError(
            "COGNITIVE_ADAPTER_MUST_NOT_RUN:"
            + name
        )


class _FakeRelay:
    KIND_GOVERNED_UPDATE = (
        "GOVERNED_UPDATE"
    )

    MISSION_HOLD = "MISSION_HOLD"
    MISSION_COMPLETE = "MISSION_COMPLETE"

    def __init__(self):
        self.submit_calls = []
        self.status_calls = []
        self.respond_calls = []

    def relay_submit_mission(
        self,
        **kwargs,
    ):
        self.submit_calls.append(
            kwargs
        )

        return {
            "status":
                "RELAY_MISSION_MISSION_HOLD",
            "relay_mission_id":
                "rmis-j8",
            "mission_state":
                self.MISSION_HOLD,
            "hold_reason":
                "HUMAN_EAH_AUTHORIZATION_REQUIRED",
            "execution_authority_hash":
                EAH,
            "human_authorization_required":
                True,
            "governed_prepare_only":
                True,
            "governed_auto_execute":
                False,
            "target_mutated":
                False,
            "kx108_invocations":
                0,
            "human_approval_created":
                False,
            "decision_authority":
                "KX108_ONLY",
            "jarvis_authority":
                "NONE",
        }

    def relay_get_status(
        self,
        relay_mission_id,
        store_dir=None,
    ):
        self.status_calls.append(
            {
                "relay_mission_id":
                    relay_mission_id,
                "store_dir":
                    store_dir,
            }
        )

        return {
            "status":
                "RELAY_STATUS_OK",
            "relay_mission_id":
                relay_mission_id,
            "mission_state":
                self.MISSION_HOLD,
            "hold_reason":
                "HUMAN_EAH_AUTHORIZATION_REQUIRED",
            "decision_authority":
                "KX108_ONLY",
        }

    def relay_respond_to_hold(
        self,
        **kwargs,
    ):
        self.respond_calls.append(
            kwargs
        )

        if (
            kwargs[
                "human_authorized_execution_authority_hash"
            ]
            != EAH
        ):
            return {
                "status":
                    "RELAY_REJECTED",
                "reason":
                    "HUMAN_AUTHORIZED_EAH_MISMATCH",
                "mission_state":
                    self.MISSION_HOLD,
                "decision_authority":
                    "KX108_ONLY",
            }

        return {
            "status":
                "RELAY_MISSION_MISSION_COMPLETE",
            "relay_mission_id":
                kwargs[
                    "relay_mission_id"
                ],
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


def _session(tmp_path: Path):
    s = (
        G.GovernedJarvisChatSession
        .__new__(
            G.GovernedJarvisChatSession
        )
    )

    s.session_id = "jws-j8-test"
    s.session_label = "j8-test"
    s.workspace = str(tmp_path)
    s.turn_count = 0
    s.last_turn = None
    s.pending_governed_mission = None
    s.adapter = _NoCognitionAdapter()

    return s


def _write_json(
    path: Path,
    value: dict,
) -> Path:
    path.write_text(
        json.dumps(
            value,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    return path


def test_prepare_surfaces_exact_eah_and_stops(
    tmp_path,
    monkeypatch,
):
    relay = _FakeRelay()

    monkeypatch.setattr(
        G,
        "_RELAY",
        relay,
    )

    s = _session(tmp_path)

    request = _write_json(
        tmp_path / "prepare.json",
        {
            "requested_outcome":
                "update target",
            "target":
                "target.txt",
            "governed_update_request":
                {
                    "proposal":
                        {"bounded": True},
                },
        },
    )

    turn = s.ask(
        f"/governed-prepare {request}"
    )

    assert len(
        relay.submit_calls
    ) == 1

    call = relay.submit_calls[0]

    assert (
        call["mission_kind"]
        == relay.KIND_GOVERNED_UPDATE
    )

    assert "store_dir" in call

    assert (
        "GOVERNED UPDATE PREPARED"
        in turn["surface_text"]
    )

    assert EAH in turn[
        "surface_text"
    ]

    assert (
        "NO ACTION WAS EXECUTED"
        in turn["surface_text"]
    )

    assert turn[
        "real_execution"
    ] is False

    assert (
        s.pending_governed_mission[
            "execution_authority_hash"
        ]
        == EAH
    )


def test_plain_yes_after_hold_never_authorizes(
    tmp_path,
    monkeypatch,
):
    relay = _FakeRelay()

    monkeypatch.setattr(
        G,
        "_RELAY",
        relay,
    )

    s = _session(tmp_path)

    s.pending_governed_mission = {
        "relay_mission_id":
            "rmis-j8",
        "execution_authority_hash":
            EAH,
        "target":
            "target.txt",
    }

    for text in (
        "yes",
        "oui",
        "go",
        "approve",
        "execute",
        "j'autorise",
    ):
        turn = s.ask(text)

        assert (
            "NATURAL_LANGUAGE_APPROVAL_IS_NOT_AUTHORITY"
            in turn["surface_text"]
        )

    assert (
        relay.respond_calls
        == []
    )


def test_eah_alone_is_not_authorization(
    tmp_path,
    monkeypatch,
):
    relay = _FakeRelay()

    monkeypatch.setattr(
        G,
        "_RELAY",
        relay,
    )

    s = _session(tmp_path)

    s.pending_governed_mission = {
        "relay_mission_id":
            "rmis-j8",
        "execution_authority_hash":
            EAH,
        "target":
            "target.txt",
    }

    # An EAH without the reserved command
    # is ordinary text, never Relay authority.
    try:
        s.ask(EAH)
    except AssertionError as exc:
        assert (
            "COGNITIVE_ADAPTER_MUST_NOT_RUN"
            in str(exc)
        )

    assert (
        relay.respond_calls
        == []
    )


def test_authorize_forwards_exact_human_fields_once(
    tmp_path,
    monkeypatch,
):
    relay = _FakeRelay()

    monkeypatch.setattr(
        G,
        "_RELAY",
        relay,
    )

    s = _session(tmp_path)

    s.pending_governed_mission = {
        "relay_mission_id":
            "rmis-j8",
        "execution_authority_hash":
            EAH,
        "target":
            "target.txt",
    }

    auth = _write_json(
        tmp_path / "authorize.json",
        {
            "relay_mission_id":
                "rmis-j8",
            "human_authorized_execution_authority_hash":
                EAH,
            "human_decision_ref":
                "human-j8-explicit",
            "resolution":
                "authorize exact EAH",
            "governed_execute_request":
                {
                    "kx108_pre_decision_dir":
                        "kxpre",
                    "kx108_post_decision_dir":
                        "kxpost",
                    "test_contract_results_dir":
                        "tests",
                    "sealed_receipt_dir":
                        "receipts",
                    "sealed_rollback_evidence_dir":
                        "rollback-evidence",
                    "rollback_result_dir":
                        "rollback",
                },
        },
    )

    turn = s.ask(
        f"/governed-authorize {auth}"
    )

    assert len(
        relay.respond_calls
    ) == 1

    call = relay.respond_calls[0]

    assert (
        call[
            "human_authorized_execution_authority_hash"
        ]
        == EAH
    )

    assert (
        call[
            "human_decision_ref"
        ]
        == "human-j8-explicit"
    )

    assert (
        call[
            "relay_mission_id"
        ]
        == "rmis-j8"
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
        turn["real_execution"]
        is True
    )

    assert (
        s.pending_governed_mission
        is None
    )


def test_pending_wrong_eah_fails_before_relay(
    tmp_path,
    monkeypatch,
):
    relay = _FakeRelay()

    monkeypatch.setattr(
        G,
        "_RELAY",
        relay,
    )

    s = _session(tmp_path)

    s.pending_governed_mission = {
        "relay_mission_id":
            "rmis-j8",
        "execution_authority_hash":
            EAH,
        "target":
            "target.txt",
    }

    wrong = (
        "f" * 64
    )

    auth = _write_json(
        tmp_path / "bad.json",
        {
            "relay_mission_id":
                "rmis-j8",
            "human_authorized_execution_authority_hash":
                wrong,
            "human_decision_ref":
                "human-j8",
            "resolution":
                "authorize",
            "governed_execute_request":
                {},
        },
    )

    turn = s.ask(
        f"/governed-authorize {auth}"
    )

    assert (
        "PENDING_EAH_MISMATCH"
        in turn["surface_text"]
    )

    assert (
        relay.respond_calls
        == []
    )


def test_prepare_cannot_inject_relay_store_or_kind(
    tmp_path,
    monkeypatch,
):
    relay = _FakeRelay()

    monkeypatch.setattr(
        G,
        "_RELAY",
        relay,
    )

    s = _session(tmp_path)

    request = _write_json(
        tmp_path / "inject.json",
        {
            "requested_outcome":
                "x",
            "target":
                "target.txt",
            "governed_update_request":
                {},
            "store_dir":
                "evil",
        },
    )

    turn = s.ask(
        f"/governed-prepare {request}"
    )

    assert (
        "GOVERNED_PREPARE_SCOPE_NOT_ALLOWED"
        in turn["surface_text"]
    )

    assert (
        relay.submit_calls
        == []
    )


def test_authorize_rejects_authority_scope_injection(
    tmp_path,
    monkeypatch,
):
    relay = _FakeRelay()

    monkeypatch.setattr(
        G,
        "_RELAY",
        relay,
    )

    s = _session(tmp_path)

    auth = _write_json(
        tmp_path / "inject-auth.json",
        {
            "relay_mission_id":
                "rmis-j8",
            "human_authorized_execution_authority_hash":
                EAH,
            "human_decision_ref":
                "human-j8",
            "resolution":
                "authorize",
            "governed_execute_request":
                {},
            "authority":
                "SELF",
        },
    )

    turn = s.ask(
        f"/governed-authorize {auth}"
    )

    assert (
        "GOVERNED_AUTHORIZE_SCOPE_NOT_ALLOWED"
        in turn["surface_text"]
    )

    assert (
        relay.respond_calls
        == []
    )


def test_unknown_governed_command_fails_closed(
    tmp_path,
    monkeypatch,
):
    relay = _FakeRelay()

    monkeypatch.setattr(
        G,
        "_RELAY",
        relay,
    )

    s = _session(tmp_path)

    turn = s.ask(
        "/governed-auto-execute yes"
    )

    assert (
        "UNKNOWN_GOVERNED_COMMAND"
        in turn["surface_text"]
    )

    assert (
        relay.respond_calls
        == []
    )


def test_status_is_read_only_relay_lookup(
    tmp_path,
    monkeypatch,
):
    relay = _FakeRelay()

    monkeypatch.setattr(
        G,
        "_RELAY",
        relay,
    )

    s = _session(tmp_path)

    turn = s.ask(
        "/governed-status rmis-j8"
    )

    assert len(
        relay.status_calls
    ) == 1

    assert (
        relay.respond_calls
        == []
    )

    assert (
        "GOVERNED UPDATE STATUS"
        in turn["surface_text"]
    )

    assert (
        turn["real_execution"]
        is False
    )


def test_chat_has_no_direct_execution_implementation():
    src = Path(
        G.__file__
    ).read_text(
        encoding="utf-8-sig"
    )

    assert (
        src.count(
            "_RELAY.relay_submit_mission("
        )
        == 1
    )

    assert (
        src.count(
            "_RELAY.relay_respond_to_hold("
        )
        == 1
    )

    for banned in (
        "execute_jarvis_governed_mutation(",
        "execute_governed_remediation(",
        "run_governed_content_apply(",
        "store_approval_artifact(",
        "run_tooling_build_pipeline(",
        "os.replace(",
        ".write_bytes(",
    ):
        assert banned not in src


def test_native_cli_remains_renderer_only():
    native = (
        _REPO
        / "scripts"
        / "obsidia_openjarvis_native_cli_bridge_v0.py"
    ).read_text(
        encoding="utf-8-sig"
    )

    assert (
        "self._governed_session.ask("
        in native
    )

    assert (
        'turn.get(\n        "surface_text"'
        in native
        or '"surface_text"' in native
    )

    assert (
        "relay_respond_to_hold("
        not in native
    )

    assert (
        "execute_jarvis_governed_mutation("
        not in native
    )


def _load_j7_fixture_module():
    """
    Reuse the already-proven J7 isolated Git world rather than
    reimplementing a second execution fixture.
    """
    import importlib.util

    path = (
        _REPO
        / "tests"
        / "cli"
        / "test_relay_governed_execute_j7.py"
    )

    spec = (
        importlib.util.spec_from_file_location(
            "j8_j7_fixture",
            path,
        )
    )

    assert spec is not None
    assert spec.loader is not None

    module = (
        importlib.util.module_from_spec(
            spec
        )
    )

    spec.loader.exec_module(
        module
    )

    return module


def test_j8_real_human_surface_to_kx_keep(
    tmp_path,
    monkeypatch,
):
    import obsidia_relay_v0 as REAL_RELAY
    import obsidia_governed_execution_driver_v0 as DRV
    import obsidia_sealed_evidence_v0 as SEV

    J7T = _load_j7_fixture_module()

    world = J7T._j7_real_world(
        tmp_path
    )

    # Make the real J8 session Relay store isolated
    # without changing production code.
    monkeypatch.setenv(
        "LOCALAPPDATA",
        str(
            tmp_path
            / "localapp"
        ),
    )

    monkeypatch.setattr(
        G,
        "_RELAY",
        REAL_RELAY,
    )

    s = _session(
        tmp_path
    )

    before_head = (
        J7T._j7_git(
            world["exec_wt"],
            "rev-parse",
            "HEAD",
        )
    )

    assert (
        before_head
        == world["base_sha"]
    )

    assert (
        world[
            "target_abs"
        ].read_bytes()
        == world["target_a"]
    )

    # ============================================================
    # PHASE 1 ? HUMAN SURFACE PREPARE
    # ============================================================

    prepare_json = _write_json(
        tmp_path
        / "j8-real-prepare.json",
        {
            "requested_outcome":
                (
                    "J8 real human governed "
                    "target update"
                ),
            "target":
                world[
                    "target_rel"
                ],
            "governed_update_request":
                world[
                    "prepare_request"
                ],
        },
    )

    prepare_turn = s.ask(
        (
            "/governed-prepare "
            f'"{prepare_json}"'
        )
    )

    assert (
        prepare_turn[
            "real_execution"
        ]
        is False
    )

    assert (
        "GOVERNED UPDATE PREPARED"
        in prepare_turn[
            "surface_text"
        ]
    )

    assert (
        "NO ACTION WAS EXECUTED"
        in prepare_turn[
            "surface_text"
        ]
    )

    pending = (
        s.pending_governed_mission
    )

    assert isinstance(
        pending,
        dict,
    )

    mission_id = pending[
        "relay_mission_id"
    ]

    eah = pending[
        "execution_authority_hash"
    ]

    assert (
        isinstance(eah, str)
        and len(eah) == 64
    )

    assert (
        eah
        in prepare_turn[
            "surface_text"
        ]
    )

    # PREPARE did not execute.
    assert (
        world[
            "target_abs"
        ].read_bytes()
        == world["target_a"]
    )

    assert not any(
        world[
            "stores"
        ]["kxpre"].rglob(
            "*.json"
        )
    )

    assert not any(
        world[
            "stores"
        ]["kxpost"].rglob(
            "*.json"
        )
    )

    # ============================================================
    # NATURAL LANGUAGE IS NOT AUTHORITY
    # ============================================================

    yes_turn = s.ask(
        "yes"
    )

    assert (
        "NATURAL_LANGUAGE_APPROVAL_IS_NOT_AUTHORITY"
        in yes_turn[
            "surface_text"
        ]
    )

    assert (
        yes_turn[
            "real_execution"
        ]
        is False
    )

    assert (
        world[
            "target_abs"
        ].read_bytes()
        == world["target_a"]
    )

    assert not any(
        world[
            "stores"
        ]["kxpre"].rglob(
            "*.json"
        )
    )

    # ============================================================
    # WRONG EAH IS REJECTED BY HUMAN SURFACE BEFORE RELAY EXECUTE
    # ============================================================

    wrong_eah = (
        (
            "0"
            if eah[0] != "0"
            else "1"
        )
        + eah[1:]
    )

    wrong_json = _write_json(
        tmp_path
        / "j8-wrong-eah.json",
        {
            "relay_mission_id":
                mission_id,
            "human_authorized_execution_authority_hash":
                wrong_eah,
            "human_decision_ref":
                "human-j8-wrong",
            "resolution":
                "authorize wrong EAH",
            "governed_execute_request":
                world[
                    "execute_request"
                ],
        },
    )

    wrong_turn = s.ask(
        (
            "/governed-authorize "
            f'"{wrong_json}"'
        )
    )

    assert (
        "PENDING_EAH_MISMATCH"
        in wrong_turn[
            "surface_text"
        ]
    )

    assert (
        wrong_turn[
            "real_execution"
        ]
        is False
    )

    assert (
        world[
            "target_abs"
        ].read_bytes()
        == world["target_a"]
    )

    assert not any(
        world[
            "stores"
        ]["kxpre"].rglob(
            "*.json"
        )
    )

    assert not any(
        world[
            "stores"
        ]["kxpost"].rglob(
            "*.json"
        )
    )

    # ============================================================
    # PHASE 2 ? EXPLICIT HUMAN AUTHORIZATION OF EXACT EAH
    # ============================================================

    auth_json = _write_json(
        tmp_path
        / "j8-real-authorize.json",
        {
            "relay_mission_id":
                mission_id,
            "human_authorized_execution_authority_hash":
                eah,
            "human_decision_ref":
                "human-j8-real-eah",
            "resolution":
                (
                    "operator explicitly authorizes "
                    "the exact displayed EAH"
                ),
            "governed_execute_request":
                world[
                    "execute_request"
                ],
        },
    )

    execute_turn = s.ask(
        (
            "/governed-authorize "
            f'"{auth_json}"'
        )
    )

    assert (
        execute_turn[
            "real_execution"
        ]
        is True
    ), execute_turn

    surface = execute_turn[
        "surface_text"
    ]

    assert (
        "GOVERNED UPDATE RESULT"
        in surface
    )

    assert (
        "state=MISSION_COMPLETE"
        in surface
    )

    assert (
        "kx108_pre=ALLOW"
        in surface
    )

    assert (
        "kx108_post=ALLOW"
        in surface
    )

    assert (
        "human_authorization_consumed=True"
        in surface
    )

    assert (
        "decision_authority=KX108_ONLY"
        in surface
    )

    # Real governed A -> B.
    assert (
        world[
            "target_abs"
        ].read_bytes()
        == world["source_b"]
    )

    assert (
        s.pending_governed_mission
        is None
    )

    # ============================================================
    # INSPECT THE REAL RELAY/J5/DRIVER RESULT
    # ============================================================

    relay_store = (
        s._governed_relay_store_dir()
    )

    mission = REAL_RELAY._load(
        relay_store,
        mission_id,
    )

    assert isinstance(
        mission,
        dict,
    )

    result = mission[
        "governed_execution_result"
    ]

    assert (
        result["status"]
        == DRV.KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW
    )

    assert (
        result[
            "kx108_pre_gate"
        ]
        == "ALLOW"
    )

    assert (
        result[
            "kx108_post_gate"
        ]
        == "ALLOW"
    )

    assert (
        result[
            "human_authorization_consumed"
        ]
        is True
    )

    assert (
        result[
            "jarvis_authority"
        ]
        == "NONE"
    )

    assert (
        result[
            "decision_authority"
        ]
        == "KX108_ONLY"
    )

    assert (
        result[
            "driver_git_disposition"
        ]
        is False
    )

    # ============================================================
    # SEALED PROOF EXISTS AND VERIFIES
    # ============================================================

    rollback_evidence = (
        SEV.load_sealed_rollback_evidence(
            result[
                "sealed_rollback_evidence_id"
            ],
            world[
                "stores"
            ]["sre"],
        )
    )

    apply_receipt = (
        SEV.load_sealed_apply_receipt(
            result[
                "sealed_apply_receipt_id"
            ],
            world[
                "stores"
            ]["sar"],
        )
    )

    assert (
        SEV.verify_sealed_rollback_evidence(
            rollback_evidence
        )[0]
    )

    assert (
        SEV.verify_sealed_apply_receipt(
            apply_receipt
        )[0]
    )

    # ============================================================
    # NO GIT DISPOSITION
    # ============================================================

    assert (
        J7T._j7_git(
            world["exec_wt"],
            "rev-parse",
            "HEAD",
        )
        == world["base_sha"]
    )

    assert (
        J7T._j7_git(
            world["exec_wt"],
            "diff",
            "--name-only",
        )
        == world[
            "target_rel"
        ]
    )


def test_j8_surface_has_no_auto_resume_path():
    src = Path(
        G.__file__
    ).read_text(
        encoding="utf-8-sig"
    )

    # Exactly one explicit transport call from the chat
    # to the already-proven J7 seam.
    assert (
        src.count(
            "_RELAY.relay_respond_to_hold("
        )
        == 1
    )

    # No generic "yes" path may call Relay.
    assert (
        "NATURAL_LANGUAGE_APPROVAL_IS_NOT_AUTHORITY"
        in src
    )

    # Chat is not an execution authority implementation.
    for banned in (
        "execute_jarvis_governed_mutation(",
        "execute_governed_remediation(",
        "run_governed_content_apply(",
        "store_approval_artifact(",
        "run_tooling_build_pipeline(",
    ):
        assert banned not in src
