#!/usr/bin/env python3
"""PreToolUse guard — derive mecanique entre intention declaree et outil demande.

Principe (drift_classifier, seuils canoniques δ1=0.15 ALERT, δ2=0.40 BLOCK) :
  l'intention de la derniere demande utilisateur (etat ecrit par le hook
  UserPromptSubmit) est comparee a la nature de l'outil que Claude veut
  utiliser. Une intention de lecture (question/status/audit) suivie d'un
  outil d'ecriture = derive >= δ2 -> pause mecanique ("ask") : l'humain
  tranche. Ce n'est plus du texte dans un prompt, c'est un verrou.

Ne bloque jamais en dur (pas de "deny" automatique) : ADVISORY devient
MECANIQUE mais l'autorite finale reste l'operateur (KX108_ONLY).
Fail-open : toute erreur => exit 0, outil autorise comme avant.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

STATE = Path(__file__).parent / ".last_router_verdict.json"

WRITE_TOOLS = {"Edit", "Write", "NotebookEdit"}
READONLY_INTENTS = {"question", "status", "audit", "unknown"}
WORLD_WORDS = ("push", "commit", "reset --hard", "rm -rf", "force",
               "deploy", "publish")
PROTECTED_HINTS = ("proofs/", "formal/tla", "merkle", "rfc3161", "sealed",
                   "P1_FREEZE_NOTE", "PUBLIC_STATUS", "RECUPE_SCORING")


def ask(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }
    }))


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        tool = payload.get("tool_name", "")
        tool_input = payload.get("tool_input") or {}
        blob = json.dumps(tool_input, ensure_ascii=False).lower()

        # Verrou 1 — zone protegee : toujours demander, quel que soit l'intent.
        if tool in WRITE_TOOLS and any(h.lower() in blob for h in PROTECTED_HINTS):
            ask("[OBSIDIA GUARD] Cible en zone protegee (proofs/seal/frozen). "
                "Validation humaine obligatoire (CANON_GUARDIAN).")
            return 0

        # Verrou 2 — derive intention/outil (drift proxy, seuil δ2=0.40).
        intent = None
        if STATE.exists():
            intent = json.loads(STATE.read_text(encoding="utf-8")).get("intent")
        if tool in WRITE_TOOLS and intent in READONLY_INTENTS:
            ask(f"[OBSIDIA GUARD] Derive detectee: intention declaree "
                f"'{intent}' (lecture) mais outil d'ecriture '{tool}' demande "
                f"(delta >= 0.40 = BLOCK, drift_classifier D2). "
                "Confirme que la modification est bien voulue.")
            return 0

        # Verrou 3 — action monde dans un Bash sans intention world_action.
        if tool == "Bash" and intent in READONLY_INTENTS:
            cmd = str(tool_input.get("command", "")).lower()
            if any(w in cmd for w in WORLD_WORDS):
                ask("[OBSIDIA GUARD] Commande a effet monde detectee "
                    f"({[w for w in WORLD_WORDS if w in cmd]}) alors que "
                    f"l'intention declaree est '{intent}'. no_auto_act — "
                    "confirmation humaine requise.")
                return 0
        return 0
    except Exception:
        return 0  # fail-open


if __name__ == "__main__":
    sys.exit(main())
