"""
OpenJarvis browser UI <-> Obsidia governed cognition bridge V0.

Serves the genuine OpenJarvis FastAPI surface while keeping cognition behind
the same Obsidia bridge already validated by the native CLI.

Authority remains NONE for OpenJarvis and KX108_ONLY for machine decisions.
"""

from __future__ import annotations

import os

import uvicorn

from openjarvis.server.app import create_app

from scripts.obsidia_openjarvis_native_cli_bridge_v0 import (
    AGENT_KEY,
    AUTHORITY,
    DECISION_AUTHORITY,
    ENGINE_KEY,
    MODEL_ID,
    ObsidiaBridgeEngine,
    ObsidiaGovernedAgent,
    register_bridge,
)


HOST = "127.0.0.1"
PORT = int(os.environ.get("OBSIDIA_OPENJARVIS_WEB_PORT", "8765"))


def build_app():
    register_bridge()

    engine = ObsidiaBridgeEngine()
    agent = ObsidiaGovernedAgent(
        engine,
        MODEL_ID,
    )

    app = create_app(
        engine,
        MODEL_ID,
        agent=agent,
        engine_name=ENGINE_KEY,
        agent_name=AGENT_KEY,
        cors_origins=[
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ],
    )

    app.state.obsidia_authority = AUTHORITY
    app.state.obsidia_decision_authority = DECISION_AUTHORITY

    return app


app = build_app()


def main() -> None:
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info",
    )


if __name__ == "__main__":
    main()
