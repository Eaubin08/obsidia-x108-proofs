"""
Governed Jarvis Chat V0.

Interactive Jarvis cockpit backed exclusively by the proved
OpenJarvis -> Obsidia Cognitive Pilot.

One active workspace binding -> one stable jws-* cognitive session.

This shell does not:
- select a model;
- select a provider;
- grant authority;
- mutate Native Memory;
- mutate the workspace;
- execute shell/git/file-write tools;
- bypass KX108.

OpenJarvis remains a non-sovereign pilot.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Callable


try:
    from scripts.obsidia_jarvis_workspace_binding_v0 import (
        WorkspaceBindingError,
        resolve_binding,
    )
    from scripts.obsidia_openjarvis_adapter_v0 import (
        OpenJarvisObsidiaCognitivePilotAdapter,
    )
except ModuleNotFoundError:
    from obsidia_jarvis_workspace_binding_v0 import (
        WorkspaceBindingError,
        resolve_binding,
    )
    from obsidia_openjarvis_adapter_v0 import (
        OpenJarvisObsidiaCognitivePilotAdapter,
    )


try:
    from scripts import obsidia_relay_v0 as _RELAY
except ImportError:
    import obsidia_relay_v0 as _RELAY


SCHEMA_VERSION = "OBSIDIA_GOVERNED_JARVIS_CHAT_V0"

AUTHORITY = "NONE"
DECISION_AUTHORITY = "KX108_ONLY"

OPENJARVIS_MODEL_SELECTION = False
OPENJARVIS_PROVIDER_SELECTION = False
OPENJARVIS_AUTHORITY = "NONE"

J8_GOVERNED_HUMAN_SURFACE_V0 = True

GOVERNED_PREPARE_COMMAND = "/governed-prepare"
GOVERNED_STATUS_COMMAND = "/governed-status"
GOVERNED_AUTHORIZE_COMMAND = "/governed-authorize"
GOVERNED_HELP_COMMAND = "/governed-help"

_GOVERNED_AMBIGUOUS_APPROVALS = frozenset({
    "yes",
    "oui",
    "ok",
    "okay",
    "go",
    "approve",
    "approved",
    "execute",
    "autorise",
    "autoriser",
    "j'autorise",
})


WORKSPACE_MUTATION = False
NATIVE_MEMORY_WRITE = False
EMITS_ACT = False
KERNEL_MUTATION = False


class GovernedJarvisChatError(RuntimeError):
    pass


def _clean_required(
    value: str | None,
    name: str,
) -> str:
    cleaned = str(value or "").strip()

    if not cleaned:
        raise GovernedJarvisChatError(
            f"{name}_REQUIRED"
        )

    return cleaned


def _surface_text(
    cognitive_result: dict[str, Any],
    cognitive_summary: dict[str, Any],
) -> str:
    """
    Conservative V0 renderer.

    Prefer an explicit textual result if the cognitive stack already
    exposes one. Otherwise show the governed cognitive summary rather
    than inventing an answer.
    """

    direct_keys = (
        "surface_response",
        "final_response",
        "answer",
        "response",
    )

    for key in direct_keys:
        value = cognitive_result.get(key)

        if isinstance(value, str) and value.strip():
            return value.strip()

    for container_key in (
        "brody_stage",
        "cognitive_join",
    ):
        container = cognitive_result.get(
            container_key
        )

        if not isinstance(container, dict):
            continue

        for key in (
            "surface_response",
            "candidate",
            "answer",
            "response",
            "content",
            "text",
        ):
            value = container.get(key)

            if isinstance(value, str) and value.strip():
                return value.strip()

    return json.dumps(
        cognitive_summary,
        ensure_ascii=False,
        sort_keys=True,
    )


class GovernedJarvisChatSession:
    def __init__(
        self,
        identifier: str,
        *,
        state_path: str | None = None,
        openjarvis_source: str | None = None,
        openjarvis_commit: str | None = None,
        adapter_factory: Callable[..., Any] = (
            OpenJarvisObsidiaCognitivePilotAdapter
        ),
    ) -> None:
        self.binding = resolve_binding(
            identifier,
            state_path=state_path,
        )

        self.session_id = str(
            self.binding["session_id"]
        )

        self.session_label = str(
            self.binding["label"]
        )

        self.workspace = str(
            Path(
                self.binding["workspace"]
            ).resolve(strict=False)
        )

        self.openjarvis_source = _clean_required(
            openjarvis_source
            or os.environ.get(
                "OBSIDIA_OPENJARVIS_SOURCE"
            ),
            "OPENJARVIS_SOURCE",
        )

        self.openjarvis_commit = _clean_required(
            openjarvis_commit
            or os.environ.get(
                "OBSIDIA_OPENJARVIS_COMMIT"
            ),
            "OPENJARVIS_COMMIT",
        )

        self.adapter = adapter_factory(
            source_root=self.openjarvis_source,
            expected_commit=self.openjarvis_commit,
            trusted_session_id=self.session_id,
        )

        self.turn_count = 0
        self.last_turn: dict[str, Any] | None = None
        self.pending_governed_mission: dict[str, Any] | None = None


    def status(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "status": "READY",
            "session_id": self.session_id,
            "session_label": self.session_label,
            "workspace": self.workspace,
            "turn_count": self.turn_count,
            "authority": AUTHORITY,
            "openjarvis_authority": (
                OPENJARVIS_AUTHORITY
            ),
            "decision_authority": (
                DECISION_AUTHORITY
            ),
            "openjarvis_model_selection": False,
            "openjarvis_provider_selection": False,
            "workspace_mutation": False,
            "native_memory_write": False,
            "emits_act": False,
            "kernel_mutation": False,
        }



    def _governed_relay_store_dir(
        self,
    ) -> Path:
        """
        Session-scoped non-repo Relay store.

        The human surface cannot choose or redirect the Relay store.
        """
        local = str(
            os.environ.get(
                "LOCALAPPDATA",
                "",
            )
            or ""
        ).strip()

        base = (
            Path(local)
            if local
            else Path.home()
        )

        return (
            base
            / "Obsidia"
            / "jarvis_governed_human_surface_v0"
            / self.session_id
        )

    @staticmethod
    def _load_governed_json(
        path_text: str,
        *,
        label: str,
    ) -> dict[str, Any]:
        raw = str(
            path_text or ""
        ).strip()

        if (
            len(raw) >= 2
            and raw[0] == raw[-1]
            and raw[0] in ("'", '"')
        ):
            raw = raw[1:-1].strip()

        if not raw:
            raise GovernedJarvisChatError(
                f"{label}_JSON_PATH_REQUIRED"
            )

        path = Path(raw).expanduser()

        if not path.is_file():
            raise GovernedJarvisChatError(
                f"{label}_JSON_NOT_FOUND"
            )

        try:
            payload = json.loads(
                path.read_text(
                    encoding="utf-8-sig"
                )
            )
        except (
            OSError,
            json.JSONDecodeError,
        ) as exc:
            raise GovernedJarvisChatError(
                f"{label}_JSON_INVALID:"
                f"{type(exc).__name__}"
            ) from exc

        if not isinstance(
            payload,
            dict,
        ):
            raise GovernedJarvisChatError(
                f"{label}_JSON_OBJECT_REQUIRED"
            )

        return payload

    @staticmethod
    def _is_full_sha256(
        value: Any,
    ) -> bool:
        if not isinstance(
            value,
            str,
        ):
            return False

        value = value.strip()

        return (
            len(value) == 64
            and all(
                c in "0123456789abcdefABCDEF"
                for c in value
            )
        )

    def _governed_turn(
        self,
        *,
        surface_text: str,
        relay_result: dict[str, Any],
        real_execution: bool = False,
    ) -> dict[str, Any]:
        """
        Render Relay evidence into the existing governed chat turn.

        This function has no authority and performs no execution.
        """
        self.turn_count += 1

        turn = {
            "status": "OK",
            "turn": self.turn_count,
            "session_id": self.session_id,
            "session_label": self.session_label,
            "workspace": self.workspace,
            "surface_text": surface_text,
            "cognitive_summary": {},
            "cognitive_result": {
                "governed_human_surface": (
                    relay_result
                ),
                "real_execution": (
                    bool(real_execution)
                ),
            },
            "pilot_status": (
                "J8_GOVERNED_HUMAN_SURFACE"
            ),
            "session_binding_source": (
                "J8_GOVERNED_HUMAN_SURFACE"
            ),
            "authority": AUTHORITY,
            "openjarvis_authority": (
                OPENJARVIS_AUTHORITY
            ),
            "decision_authority": (
                DECISION_AUTHORITY
            ),
            "real_execution": (
                bool(real_execution)
            ),
        }

        self.last_turn = turn

        return turn

    def _governed_rejection_turn(
        self,
        reason: str,
    ) -> dict[str, Any]:
        result = {
            "status":
                "GOVERNED_HUMAN_SURFACE_REJECTED",
            "reason":
                str(reason),
            "authority":
                "NONE",
            "decision_authority":
                DECISION_AUTHORITY,
            "real_execution":
                False,
        }

        return self._governed_turn(
            surface_text=(
                "GOVERNED COMMAND REJECTED\n"
                f"reason={reason}\n"
                "No action was executed."
            ),
            relay_result=result,
            real_execution=False,
        )

    def _prepare_governed_from_json(
        self,
        path_text: str,
    ) -> dict[str, Any]:
        try:
            payload = (
                self._load_governed_json(
                    path_text,
                    label="GOVERNED_PREPARE",
                )
            )
        except GovernedJarvisChatError as exc:
            return self._governed_rejection_turn(
                str(exc)
            )

        allowed = {
            "requested_outcome",
            "target",
            "governed_update_request",
        }

        unknown = (
            set(payload)
            - allowed
        )

        if unknown:
            return self._governed_rejection_turn(
                "GOVERNED_PREPARE_SCOPE_NOT_ALLOWED:"
                + ",".join(
                    sorted(unknown)
                )
            )

        requested_outcome = payload.get(
            "requested_outcome"
        )

        target = payload.get(
            "target"
        )

        request = payload.get(
            "governed_update_request"
        )

        if not (
            isinstance(
                requested_outcome,
                str,
            )
            and requested_outcome.strip()
        ):
            return self._governed_rejection_turn(
                "REQUESTED_OUTCOME_REQUIRED"
            )

        if not (
            isinstance(target, str)
            and target.strip()
        ):
            return self._governed_rejection_turn(
                "TARGET_REQUIRED"
            )

        if not isinstance(
            request,
            dict,
        ):
            return self._governed_rejection_turn(
                "GOVERNED_UPDATE_REQUEST_REQUIRED"
            )

        result = _RELAY.relay_submit_mission(
            requested_outcome=(
                requested_outcome.strip()
            ),
            mission_kind=(
                _RELAY.KIND_GOVERNED_UPDATE
            ),
            target=target.strip(),
            store_dir=(
                self._governed_relay_store_dir()
            ),
            governed_update_request=request,
        )

        mission_id = result.get(
            "relay_mission_id"
        )

        eah = result.get(
            "execution_authority_hash"
        )

        if (
            result.get("mission_state")
            == _RELAY.MISSION_HOLD
            and result.get("hold_reason")
            == "HUMAN_EAH_AUTHORIZATION_REQUIRED"
            and self._is_full_sha256(eah)
            and isinstance(
                mission_id,
                str,
            )
            and mission_id.strip()
        ):
            self.pending_governed_mission = {
                "relay_mission_id":
                    mission_id,
                "execution_authority_hash":
                    eah,
                "target":
                    target.strip(),
            }

        surface = "\n".join(
            [
                "GOVERNED UPDATE PREPARED",
                (
                    "mission="
                    + str(mission_id)
                ),
                (
                    "target="
                    + target.strip()
                ),
                (
                    "state="
                    + str(
                        result.get(
                            "mission_state"
                        )
                    )
                ),
                (
                    "hold_reason="
                    + str(
                        result.get(
                            "hold_reason"
                        )
                    )
                ),
                (
                    "EAH="
                    + str(eah)
                ),
                (
                    "human_authorization_required="
                    + str(
                        result.get(
                            "human_authorization_required"
                        )
                    )
                ),
                (
                    "auto_execute="
                    + str(
                        result.get(
                            "governed_auto_execute"
                        )
                    )
                ),
                (
                    "target_mutated="
                    + str(
                        result.get(
                            "target_mutated"
                        )
                    )
                ),
                "",
                "NO ACTION WAS EXECUTED.",
                (
                    "Authorization requires an "
                    "explicit /governed-authorize "
                    "JSON carrying this exact EAH."
                ),
            ]
        )

        return self._governed_turn(
            surface_text=surface,
            relay_result=result,
            real_execution=False,
        )

    def _status_governed(
        self,
        mission_id: str,
    ) -> dict[str, Any]:
        bound_id = str(
            mission_id or ""
        ).strip()

        if not bound_id:
            return self._governed_rejection_turn(
                "RELAY_MISSION_ID_REQUIRED"
            )

        result = _RELAY.relay_get_status(
            bound_id,
            store_dir=(
                self._governed_relay_store_dir()
            ),
        )

        surface = "\n".join(
            [
                "GOVERNED UPDATE STATUS",
                (
                    "mission="
                    + bound_id
                ),
                (
                    "state="
                    + str(
                        result.get(
                            "mission_state"
                        )
                    )
                ),
                (
                    "hold_reason="
                    + str(
                        result.get(
                            "hold_reason"
                        )
                    )
                ),
                (
                    "decision_authority="
                    + str(
                        result.get(
                            "decision_authority",
                            DECISION_AUTHORITY,
                        )
                    )
                ),
            ]
        )

        return self._governed_turn(
            surface_text=surface,
            relay_result=result,
            real_execution=False,
        )

    def _authorize_governed_from_json(
        self,
        path_text: str,
    ) -> dict[str, Any]:
        try:
            payload = (
                self._load_governed_json(
                    path_text,
                    label="GOVERNED_AUTHORIZE",
                )
            )
        except GovernedJarvisChatError as exc:
            return self._governed_rejection_turn(
                str(exc)
            )

        allowed = {
            "relay_mission_id",
            "human_authorized_execution_authority_hash",
            "human_decision_ref",
            "resolution",
            "governed_execute_request",
        }

        unknown = (
            set(payload)
            - allowed
        )

        if unknown:
            return self._governed_rejection_turn(
                "GOVERNED_AUTHORIZE_SCOPE_NOT_ALLOWED:"
                + ",".join(
                    sorted(unknown)
                )
            )

        mission_id = payload.get(
            "relay_mission_id"
        )

        supplied_eah = payload.get(
            "human_authorized_execution_authority_hash"
        )

        human_ref = payload.get(
            "human_decision_ref"
        )

        resolution = payload.get(
            "resolution"
        )

        execute_request = payload.get(
            "governed_execute_request"
        )

        if not (
            isinstance(
                mission_id,
                str,
            )
            and mission_id.strip()
        ):
            return self._governed_rejection_turn(
                "RELAY_MISSION_ID_REQUIRED"
            )

        if not self._is_full_sha256(
            supplied_eah
        ):
            return self._governed_rejection_turn(
                "EXACT_64_HEX_EAH_REQUIRED"
            )

        if not (
            isinstance(
                human_ref,
                str,
            )
            and human_ref.strip()
        ):
            return self._governed_rejection_turn(
                "HUMAN_DECISION_REF_REQUIRED"
            )

        if not (
            isinstance(
                resolution,
                str,
            )
            and resolution.strip()
        ):
            return self._governed_rejection_turn(
                "HUMAN_RESOLUTION_REQUIRED"
            )

        if not isinstance(
            execute_request,
            dict,
        ):
            return self._governed_rejection_turn(
                "GOVERNED_EXECUTE_REQUEST_REQUIRED"
            )

        pending = (
            self.pending_governed_mission
        )

        if isinstance(
            pending,
            dict,
        ):
            if (
                mission_id.strip()
                != pending.get(
                    "relay_mission_id"
                )
            ):
                return self._governed_rejection_turn(
                    "PENDING_MISSION_ID_MISMATCH"
                )

            if (
                supplied_eah.strip()
                != pending.get(
                    "execution_authority_hash"
                )
            ):
                return self._governed_rejection_turn(
                    "PENDING_EAH_MISMATCH"
                )

        result = (
            _RELAY.relay_respond_to_hold(
                relay_mission_id=(
                    mission_id.strip()
                ),
                human_decision_ref=(
                    human_ref.strip()
                ),
                resolution=(
                    resolution.strip()
                ),
                store_dir=(
                    self._governed_relay_store_dir()
                ),
                human_authorized_execution_authority_hash=(
                    supplied_eah.strip()
                ),
                governed_execute_request=(
                    execute_request
                ),
            )
        )

        real_execution = bool(
            result.get(
                "human_authorization_consumed",
                False,
            )
        )

        if (
            result.get("mission_state")
            != _RELAY.MISSION_HOLD
        ):
            self.pending_governed_mission = (
                None
            )

        surface = "\n".join(
            [
                "GOVERNED UPDATE RESULT",
                (
                    "mission="
                    + mission_id.strip()
                ),
                (
                    "state="
                    + str(
                        result.get(
                            "mission_state"
                        )
                    )
                ),
                (
                    "execution_status="
                    + str(
                        result.get(
                            "governed_execution_status"
                        )
                    )
                ),
                (
                    "kx108_pre="
                    + str(
                        result.get(
                            "kx108_pre_gate"
                        )
                    )
                ),
                (
                    "kx108_post="
                    + str(
                        result.get(
                            "kx108_post_gate"
                        )
                    )
                ),
                (
                    "target_mutated="
                    + str(
                        result.get(
                            "target_mutated"
                        )
                    )
                ),
                (
                    "human_authorization_consumed="
                    + str(
                        result.get(
                            "human_authorization_consumed"
                        )
                    )
                ),
                (
                    "decision_authority="
                    + str(
                        result.get(
                            "decision_authority",
                            DECISION_AUTHORITY,
                        )
                    )
                ),
            ]
        )

        return self._governed_turn(
            surface_text=surface,
            relay_result=result,
            real_execution=real_execution,
        )

    def _handle_governed_command(
        self,
        bound_text: str,
    ) -> dict[str, Any] | None:
        """
        Reserved deterministic human surface.

        Natural language cannot become authorization.
        """
        text = str(
            bound_text or ""
        ).strip()

        command = text.lower()

        if command == GOVERNED_HELP_COMMAND:
            return self._governed_turn(
                surface_text=(
                    "Governed commands:\n"
                    "/governed-prepare <prepare.json>\n"
                    "/governed-status <relay_mission_id>\n"
                    "/governed-authorize <authorization.json>\n\n"
                    "Natural-language yes/approve/go "
                    "never authorizes execution."
                ),
                relay_result={
                    "status":
                        "GOVERNED_HELP",
                    "authority":
                        "NONE",
                    "decision_authority":
                        DECISION_AUTHORITY,
                },
                real_execution=False,
            )

        if text.startswith(
            GOVERNED_PREPARE_COMMAND + " "
        ):
            return (
                self._prepare_governed_from_json(
                    text[
                        len(
                            GOVERNED_PREPARE_COMMAND
                        ):
                    ].strip()
                )
            )

        if text.startswith(
            GOVERNED_STATUS_COMMAND + " "
        ):
            return self._status_governed(
                text[
                    len(
                        GOVERNED_STATUS_COMMAND
                    ):
                ].strip()
            )

        if text.startswith(
            GOVERNED_AUTHORIZE_COMMAND + " "
        ):
            return (
                self._authorize_governed_from_json(
                    text[
                        len(
                            GOVERNED_AUTHORIZE_COMMAND
                        ):
                    ].strip()
                )
            )

        if text.startswith("/governed-"):
            return self._governed_rejection_turn(
                "UNKNOWN_GOVERNED_COMMAND"
            )

        if (
            isinstance(
                self.pending_governed_mission,
                dict,
            )
            and command
            in _GOVERNED_AMBIGUOUS_APPROVALS
        ):
            return self._governed_rejection_turn(
                "NATURAL_LANGUAGE_APPROVAL_IS_NOT_AUTHORITY"
            )

        return None

    def ask(
        self,
        text: str,
    ) -> dict[str, Any]:
        if not isinstance(text, str):
            raise GovernedJarvisChatError(
                "TEXT_MUST_BE_STRING"
            )

        bound_text = text.strip()

        if not bound_text:
            raise GovernedJarvisChatError(
                "TEXT_REQUIRED"
            )

        if len(bound_text) > 50000:
            raise GovernedJarvisChatError(
                "TEXT_TOO_LARGE"
            )

        governed_turn = (
            self._handle_governed_command(
                bound_text
            )
        )

        if governed_turn is not None:
            return governed_turn

        result = self.adapter.execute(
            capability_id=(
                "OPENJARVIS_OBSIDIA_COGNITIVE_PILOT"
            ),
            payload={
                "input_text": bound_text,
            },
        )

        if not isinstance(result, dict):
            raise GovernedJarvisChatError(
                "PILOT_RESULT_INVALID"
            )

        if (
            result.get("status")
            != "OPENJARVIS_OBSIDIA_COGNITIVE_PILOT_OK"
        ):
            turn = {
                "status": "BLOCKED",
                "session_id": self.session_id,
                "session_label": self.session_label,
                "workspace": self.workspace,
                "turn": self.turn_count + 1,
                "pilot_status": result.get(
                    "status"
                ),
                "authority": AUTHORITY,
                "decision_authority": (
                    DECISION_AUTHORITY
                ),
                "raw_pilot_result": result,
            }

            self.last_turn = turn

            return turn

        if (
            result.get("bound_session_id")
            != self.session_id
        ):
            raise GovernedJarvisChatError(
                "SESSION_ID_MISMATCH"
            )

        if (
            result.get("session_binding_source")
            != "TRUSTED_WORKSPACE_BINDING"
        ):
            raise GovernedJarvisChatError(
                "SESSION_BINDING_NOT_TRUSTED"
            )

        cognitive_result = (
            result.get("cognitive_result")
            or {}
        )

        cognitive_summary = (
            result.get("cognitive_summary")
            or {}
        )

        if not isinstance(
            cognitive_result,
            dict,
        ):
            raise GovernedJarvisChatError(
                "COGNITIVE_RESULT_INVALID"
            )

        if not isinstance(
            cognitive_summary,
            dict,
        ):
            raise GovernedJarvisChatError(
                "COGNITIVE_SUMMARY_INVALID"
            )

        self.turn_count += 1

        turn = {
            "status": "OK",
            "turn": self.turn_count,
            "session_id": self.session_id,
            "session_label": self.session_label,
            "workspace": self.workspace,
            "surface_text": _surface_text(
                cognitive_result,
                cognitive_summary,
            ),
            "cognitive_summary": cognitive_summary,
            "cognitive_result": cognitive_result,
            "pilot_status": result.get(
                "status"
            ),
            "session_binding_source": result.get(
                "session_binding_source"
            ),
            "authority": AUTHORITY,
            "openjarvis_authority": (
                OPENJARVIS_AUTHORITY
            ),
            "decision_authority": (
                DECISION_AUTHORITY
            ),
            "real_execution": bool(
                cognitive_result.get(
                    "real_execution",
                    False,
                )
            ),
        }

        self.last_turn = turn

        return turn


def format_status(
    session: GovernedJarvisChatSession,
) -> str:
    status = session.status()

    return (
        f"session={status['session_label']} "
        f"id={status['session_id']} "
        f"turns={status['turn_count']} "
        f"authority={status['authority']} "
        f"decision={status['decision_authority']}"
    )


def format_turn(
    turn: dict[str, Any],
) -> str:
    if turn.get("status") != "OK":
        return json.dumps(
            turn,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )

    return str(
        turn.get("surface_text")
        or ""
    )


def _proof_text(
    session: GovernedJarvisChatSession,
) -> str:
    if session.last_turn is None:
        return "NO_TURN_YET"

    return json.dumps(
        session.last_turn,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )


def interactive_chat(
    session: GovernedJarvisChatSession,
) -> int:
    print(
        "Jarvis / Obsidia governed chat"
    )
    print(
        format_status(session)
    )
    print(
        "commands: /status /session /workspace "
        "/proof /governed-help /help /exit"
    )

    while True:
        try:
            raw = input("jarvis> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0

        text = raw.strip()

        if not text:
            continue

        command = text.lower()

        if command in (
            "/exit",
            "/quit",
            "exit",
            "quit",
        ):
            return 0

        if command == "/help":
            print(
                "/status /session /workspace "
                "/proof /governed-help /help /exit"
            )
            continue

        if command == "/status":
            print(
                format_status(session)
            )
            continue

        if command == "/session":
            print(
                json.dumps(
                    {
                        "session_id": (
                            session.session_id
                        ),
                        "session_label": (
                            session.session_label
                        ),
                        "turn_count": (
                            session.turn_count
                        ),
                    },
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
            )
            continue

        if command == "/workspace":
            print(session.workspace)
            continue

        if command == "/proof":
            print(
                _proof_text(session)
            )
            continue

        try:
            turn = session.ask(text)
        except GovernedJarvisChatError as exc:
            print(
                "BLOCKED: "
                + str(exc)
            )
            continue

        print(
            format_turn(turn)
        )


def main(
    argv: list[str] | None = None,
) -> int:
    parser = argparse.ArgumentParser(
        prog="obsidia-governed-jarvis-chat"
    )

    parser.add_argument(
        "session",
    )

    parser.add_argument(
        "--state",
        default=None,
    )

    parser.add_argument(
        "--openjarvis-source",
        default=None,
    )

    parser.add_argument(
        "--openjarvis-commit",
        default=None,
    )

    parser.add_argument(
        "--once",
        default=None,
        help=(
            "Execute one governed turn "
            "instead of interactive mode."
        ),
    )

    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
    )

    args = parser.parse_args(argv)

    try:
        session = GovernedJarvisChatSession(
            args.session,
            state_path=args.state,
            openjarvis_source=(
                args.openjarvis_source
            ),
            openjarvis_commit=(
                args.openjarvis_commit
            ),
        )

        if args.once is not None:
            turn = session.ask(
                args.once
            )

            if args.output_json:
                print(
                    json.dumps(
                        turn,
                        ensure_ascii=False,
                        indent=2,
                        sort_keys=True,
                    )
                )
            else:
                print(
                    format_turn(turn)
                )

            return (
                0
                if turn.get("status") == "OK"
                else 2
            )

        return interactive_chat(
            session
        )

    except (
        WorkspaceBindingError,
        GovernedJarvisChatError,
    ) as exc:
        print(
            json.dumps(
                {
                    "status": "BLOCKED",
                    "reason": str(exc),
                    "authority": AUTHORITY,
                    "decision_authority": (
                        DECISION_AUTHORITY
                    ),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
