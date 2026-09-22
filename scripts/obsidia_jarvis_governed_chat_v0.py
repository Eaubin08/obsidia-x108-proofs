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


SCHEMA_VERSION = "OBSIDIA_GOVERNED_JARVIS_CHAT_V0"

AUTHORITY = "NONE"
DECISION_AUTHORITY = "KX108_ONLY"

OPENJARVIS_MODEL_SELECTION = False
OPENJARVIS_PROVIDER_SELECTION = False
OPENJARVIS_AUTHORITY = "NONE"

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
        "/proof /help /exit"
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
                "/proof /help /exit"
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
