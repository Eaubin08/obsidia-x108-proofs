from __future__ import annotations

import sys
from pathlib import Path


def contains_any(text: str, needles: list[str]) -> bool:
    low = text.lower()
    return any(n.lower() in low for n in needles)


def main() -> int:
    files = sorted(Path("docs/runtime").glob("F12A_TERMINAL_ONCE_*_*.txt"))
    if len(files) < 3:
        print("F12A_FAIL: expected at least 3 terminal output files")
        return 1

    all_text = "\n\n".join(p.read_text(encoding="utf-8", errors="replace") for p in files)

    checks = {
        "has_brody_header": "BRODY" in all_text,
        "has_terminal_ok": contains_any(all_text, ["BRODY_TERMINAL_NATIVE_ONCE_OK", "Brody Terminal CLI / once"]),
        "has_kx108_only": "KX108_ONLY" in all_text,
        "has_readonly": "readonly" in all_text.lower(),
        "has_no_act_boundary": contains_any(all_text, ["emits_act=false", "Pas de", "no ACT", "pas d'[REDACTED_ACT]"]),
        "has_true_voice_or_runtime": contains_any(all_text, ["TRUE VOICE", "LLM OBSIDIEN", "voice_runtime"]),
        "has_domain_or_structure": contains_any(all_text, ["DOMAIN RACCORD", "STRUCTURE-FIRST", "structure-first"]),
        "has_policy_or_sigma": contains_any(all_text, ["ADAPTIVE RESPONSE POLICY", "SIGMA", "operator_view_packet"]),
        "has_boundary": contains_any(all_text, ["BOUNDARY", "CONTRATS / PERMISSIONS", "decision_authority"]),
        "has_command_packet_visibility": contains_any(all_text, ["HUMAN_COMMAND_PACKET", "command packet", "command_copy_block", "execution_allowed_for_brody=false"]),
    }

    for k, v in checks.items():
        print(f"{k}={v}")

    if not all(checks.values()):
        print("F12A_TERMINAL_VISIBLE_SMOKE_FAIL")
        return 1

    print("F12A_TERMINAL_VISIBLE_SMOKE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
