"""
OpenJarvis native CLI <-> Obsidia governed cognition bridge V0.

Purpose
-------
Keep the real OpenJarvis ``chat`` CLI and its UX while routing the
conversation through Obsidia.

OpenJarvis remains:
- CLI / cockpit / session UX;
- non-sovereign;
- unable to choose the cognitive model/provider;
- unable to perform direct inference through this bridge engine.

Obsidia remains:
- cognition policy;
- model escalation policy;
- governance;
- KX108_ONLY decision authority.

No OpenJarvis source modification is required.
"""

from __future__ import annotations

import ast
import os
import runpy
import sys
from typing import Any, AsyncIterator, Sequence


# OpenJarvis types.
from openjarvis.agents._stubs import (
    AgentContext,
    AgentResult,
    BaseAgent,
)
from openjarvis.core.registry import (
    AgentRegistry,
    EngineRegistry,
)
from openjarvis.core.types import Message
from openjarvis.engine._stubs import InferenceEngine


# Obsidia governed chat.
try:
    from scripts.obsidia_jarvis_governed_chat_v0 import (
        GovernedJarvisChatSession,
    )
except ModuleNotFoundError:
    from obsidia_jarvis_governed_chat_v0 import (
        GovernedJarvisChatSession,
    )


ENGINE_KEY = "obsidia_bridge"
MODEL_ID = "obsidia-governed"
AGENT_KEY = "obsidia_governed"

AUTHORITY = "NONE"
DECISION_AUTHORITY = "KX108_ONLY"

DIRECT_OPENJARVIS_INFERENCE = False
OPENJARVIS_MODEL_SELECTION = False
OPENJARVIS_PROVIDER_SELECTION = False


class ObsidiaBridgeDirectInferenceError(RuntimeError):
    pass


def _register_once(
    registry,
    key: str,
    value,
) -> None:
    if registry.contains(key):
        existing = registry.get(key)

        if existing is not value:
            raise RuntimeError(
                f"REGISTRY_COLLISION:{key}"
            )

        return

    registry.register_value(
        key,
        value,
    )


class ObsidiaBridgeEngine(InferenceEngine):
    """
    Sentinel engine required by OpenJarvis's native chat bootstrap.

    It advertises one synthetic model so the native CLI can initialize,
    but it MUST NEVER perform inference.

    Any direct inference call means the governed agent boundary was
    bypassed and therefore fails closed.
    """

    engine_id = ENGINE_KEY
    is_cloud = False

    def health(self) -> bool:
        return True

    def list_models(self) -> list[str]:
        return [MODEL_ID]

    def can_serve(
        self,
        model: str,
    ) -> bool:
        return (
            str(model or "").strip()
            == MODEL_ID
        )

    def prepare(
        self,
        model: str,
    ) -> None:
        if not self.can_serve(model):
            raise ObsidiaBridgeDirectInferenceError(
                "OBSIDIA_BRIDGE_MODEL_REJECTED"
            )

    def generate(
        self,
        messages: Sequence[Message],
        *,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> dict[str, Any]:
        raise ObsidiaBridgeDirectInferenceError(
            "DIRECT_OPENJARVIS_INFERENCE_FORBIDDEN"
        )

    async def stream(
        self,
        messages: Sequence[Message],
        *,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        raise ObsidiaBridgeDirectInferenceError(
            "DIRECT_OPENJARVIS_INFERENCE_FORBIDDEN"
        )

        if False:  # pragma: no cover
            yield ""


def _extract_brody_text(
    turn: dict[str, Any],
) -> str | None:
    """
    Extract the governed Brody response when available.

    Current Brody runtime may expose ``response_text`` either directly
    or as the repr of a tuple: (text, sources, flag).
    """

    cognitive = turn.get(
        "cognitive_result"
    )

    if not isinstance(cognitive, dict):
        return None

    join = cognitive.get(
        "cognitive_join"
    )

    if not isinstance(join, dict):
        return None

    brody = join.get(
        "brody_cognitive_response"
    )

    if not isinstance(brody, dict):
        return None

    raw = brody.get(
        "response_text"
    )

    if not isinstance(raw, str):
        return None

    raw = raw.strip()

    if not raw:
        return None

    # Some current Brody rails serialize the tuple as text.
    if raw.startswith("("):
        try:
            value = ast.literal_eval(raw)

            if (
                isinstance(value, tuple)
                and value
                and isinstance(value[0], str)
                and value[0].strip()
            ):
                return value[0].strip()
        except (
            ValueError,
            SyntaxError,
        ):
            pass

    return raw


def _surface_turn(
    turn: dict[str, Any],
) -> str:
    """
    Render only governed output.

    V0 preference:
    1. canonical/structural Brody response;
    2. existing governed chat surface fallback.

    Local-model evidence is deliberately NOT promoted directly into a
    final answer by this bridge.
    """

    brody_text = _extract_brody_text(
        turn
    )

    if brody_text:
        return brody_text

    surface = turn.get(
        "surface_text"
    )

    if isinstance(surface, str):
        surface = surface.strip()

        if surface:
            return surface

    return (
        "OBSIDIA_GOVERNED_RESPONSE_UNAVAILABLE"
    )


class ObsidiaGovernedAgent(BaseAgent):
    """
    Native OpenJarvis agent whose ``run`` delegates to Obsidia.

    The OpenJarvis engine/model supplied by the native CLI are accepted
    only for interface compatibility. They are never used for cognition.
    """

    agent_id = AGENT_KEY
    accepts_tools = False

    def __init__(
        self,
        engine: InferenceEngine,
        model: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            engine,
            model,
            **kwargs,
        )

        session_id = str(
            os.environ.get(
                "OBSIDIA_JARVIS_SESSION_ID",
                "",
            )
        ).strip()

        if not session_id:
            raise RuntimeError(
                "OBSIDIA_JARVIS_SESSION_ID_REQUIRED"
            )

        if not session_id.startswith(
            "jws-"
        ):
            raise RuntimeError(
                "OBSIDIA_JARVIS_SESSION_ID_INVALID"
            )

        self._governed_session = (
            GovernedJarvisChatSession(
                session_id
            )
        )

    def run(
        self,
        input: str,
        context: AgentContext | None = None,
        **kwargs: Any,
    ) -> AgentResult:
        """
        One native OpenJarvis chat turn -> one governed Obsidia turn.
        """

        text = str(
            input or ""
        ).strip()

        if not text:
            return AgentResult(
                content="",
                turns=0,
                metadata={
                    "status": "EMPTY_INPUT",
                    "authority": AUTHORITY,
                    "decision_authority": (
                        DECISION_AUTHORITY
                    ),
                },
            )

        turn = self._governed_session.ask(
            text
        )

        content = _surface_turn(
            turn
        )

        metadata = {
            "bridge": (
                "OPENJARVIS_NATIVE_CLI_"
                "OBSIDIA_BRIDGE_V0"
            ),
            "status": turn.get(
                "status"
            ),
            "session_id": turn.get(
                "session_id"
            ),
            "session_binding_source": (
                turn.get(
                    "session_binding_source"
                )
            ),
            "authority": AUTHORITY,
            "openjarvis_authority": (
                "NONE"
            ),
            "decision_authority": (
                DECISION_AUTHORITY
            ),
            "direct_openjarvis_inference": (
                False
            ),
            "real_execution": bool(
                turn.get(
                    "real_execution",
                    False,
                )
            ),
        }

        return AgentResult(
            content=content,
            turns=1,
            metadata=metadata,
        )


def register_bridge() -> None:
    """
    Register external engine + agent in OpenJarvis process registries.
    """

    _register_once(
        EngineRegistry,
        ENGINE_KEY,
        ObsidiaBridgeEngine,
    )

    _register_once(
        AgentRegistry,
        AGENT_KEY,
        ObsidiaGovernedAgent,
    )


def native_chat_argv(
    extra_args: list[str] | None = None,
) -> list[str]:
    """
    Exact argv passed to the real OpenJarvis CLI.
    """

    return [
        "openjarvis.cli",
        "chat",
        "--engine",
        ENGINE_KEY,
        "--model",
        MODEL_ID,
        "--agent",
        AGENT_KEY,
        "--skip-runtime-panel",
        *list(extra_args or []),
    ]


def launch_native_chat(
    extra_args: list[str] | None = None,
) -> None:
    """
    Run the genuine ``openjarvis.cli`` module after external registration.
    """

    register_bridge()

    old_argv = list(
        sys.argv
    )

    try:
        sys.argv = native_chat_argv(
            extra_args
        )

        runpy.run_module(
            "openjarvis.cli",
            run_name="__main__",
        )
    finally:
        sys.argv = old_argv


def main() -> None:
    launch_native_chat(
        sys.argv[1:]
    )


# Registration also occurs on import so tests/SDK callers can inspect it.
register_bridge()


if __name__ == "__main__":
    main()
