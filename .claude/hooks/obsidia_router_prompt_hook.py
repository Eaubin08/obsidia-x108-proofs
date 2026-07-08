#!/usr/bin/env python3
"""UserPromptSubmit hook — pont obsidia-router <-> Claude Code.

Chaque prompt utilisateur passe d'abord par le pipeline deterministe
d'obsidia-router (IR -> gates -> topic -> niveau d'inference). Le verdict
est injecte comme contexte additionnel : Claude recoit la demande deja
classee (intention, couche, gate, niveau, route) sans depenser de tokens
pour la re-deduire.

ADVISORY_ONLY : le hook n'exerce aucune autorite de decision
(decision_authority = KX108_ONLY). Il ne bloque jamais le prompt — meme un
verdict DENY est injecte comme signal, la decision finale reste chez
l'operateur humain et les gates du repo.

Fail-open : toute erreur (router absent, import casse, JSON invalide)
=> exit 0 sans sortie, Claude continue normalement.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROUTER_ROOT = Path(r"C:\Users\User\Desktop\obsidia-router")

LAYER_TO_SKILL = {
    "proof":    "proof-sentinel",
    "obsidure": "read-only-inspector",
    "domain":   "sigma-surgeon",
}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        prompt = (payload.get("prompt") or "").strip()
        if not prompt or not ROUTER_ROOT.is_dir():
            return 0

        sys.path.insert(0, str(ROUTER_ROOT))
        from app.router.decision import decide  # type: ignore

        d = decide(prompt, memory_index={}, model_ladder=["local-only"])
        ir, gate = d.get("ir", {}), d.get("gate", {})

        # Etat partage avec le garde PreToolUse (mesure de derive mecanique).
        try:
            state = {"intent": ir.get("intent_type"),
                     "layer": ir.get("target_layer"),
                     "gate": gate.get("verdict"),
                     "route": d.get("route")}
            (Path(__file__).parent / ".last_router_verdict.json").write_text(
                json.dumps(state), encoding="utf-8")
        except OSError:
            pass

        lines = [
            "[OBSIDIA-ROUTER] Verdict pre-inference deterministe (ADVISORY_ONLY, KX108_ONLY):",
            f"  intent={ir.get('intent_type')} layer={ir.get('target_layer')} "
            f"action={ir.get('action')} risk={ir.get('risk')}",
            f"  gate={gate.get('verdict')} ({gate.get('reason')})",
            f"  level={d.get('level')} route={d.get('route')} reason={d.get('reason')}",
        ]
        skill = LAYER_TO_SKILL.get(ir.get("target_layer") or "")
        if skill:
            lines.append(f"  skill_suggeree={skill}")
        if gate.get("verdict") in ("DENY", "HOLD"):
            lines.append(
                "  CADRE: verdict DENY/HOLD — ne rien executer, proposer un plan "
                "commands-only et demander validation humaine.")

        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": "\n".join(lines),
            }
        }))
        return 0
    except Exception:
        return 0  # fail-open: le pont ne doit jamais bloquer la session


if __name__ == "__main__":
    sys.exit(main())
