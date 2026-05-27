#!/usr/bin/env python3
"""
Brody Terminal CLI
Dialogue direct avec le moteur Obsidia via http://127.0.0.1:8012/api/brody/chat
Aucune dépendance externe — stdlib Python 3.8+ uniquement.

Usage :
    python tools/brody_chat.py
    python tools/brody_chat.py --session mon_test
"""
from __future__ import annotations

import argparse
import json
import sys

import os


def _configure_console_encoding() -> None:
    """Prevent Windows cp1252 crashes on box-drawing / unicode terminal output."""
    try:
        os.environ.setdefault("PYTHONIOENCODING", "utf-8")
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


_configure_console_encoding()

import time
import urllib.error
import urllib.request
from typing import Any

# ── Configuration ─────────────────────────────────────────────────────────────

BASE_URL  = "http://127.0.0.1:8012"
ENDPOINT  = f"{BASE_URL}/api/brody/chat"
HEALTH_EP = f"{BASE_URL}/openapi.json"
TIMEOUT   = 120  # secondes — Brody peut être lent à l'hydratation (~40s)

# ── ANSI colors (désactivés si pas de TTY) ────────────────────────────────────

_TTY = sys.stdout.isatty()

def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _TTY else text

def cyan(t: str)   -> str: return _c("36", t)
def green(t: str)  -> str: return _c("32", t)
def yellow(t: str) -> str: return _c("33", t)
def red(t: str)    -> str: return _c("31", t)
def dim(t: str)    -> str: return _c("2",  t)
def bold(t: str)   -> str: return _c("1",  t)

SEP = dim("─" * 64)

# ── HTTP helpers ──────────────────────────────────────────────────────────────

def _http_get(url: str, timeout: int = 5) -> dict[str, Any]:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _http_post(url: str, payload: dict[str, Any], timeout: int = TIMEOUT) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ── Display ───────────────────────────────────────────────────────────────────


def _get_path(data: dict[str, Any], path: list[str], default: Any = "") -> Any:
    cur: Any = data
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key, default)
    return cur


def _fmt_list(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else "-"
    if value in (None, ""):
        return "-"
    return str(value)


def _bool_text(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value in (None, ""):
        return "-"
    return str(value)


def _print_native_machination(data: dict[str, Any]) -> None:
    has_native = any(k in data for k in (
        "support_summary",
        "contracts",
        "permission_matrix",
        "machination_packet",
        "boundary_contract",
        "kernel_contract",
    ))

    if not has_native:
        print(dim("Machination native : non exposée par le payload."))
        return

    support = data.get("support_summary") or {}
    contracts = data.get("contracts") or {}
    permission = data.get("permission_matrix") or contracts.get("permission_matrix") or {}
    boundary = data.get("boundary_contract") or contracts.get("boundary_contract") or {}
    kernel = data.get("kernel_contract") or contracts.get("kernel_contract") or {}
    machination = data.get("machination_packet") or {}

    print(SEP)
    print(bold(yellow("MACHINATION NATIVE")))
    print(dim(f"status={machination.get('status', '-')}  source={machination.get('source', '-')}"))
    print(dim(f"support_intent={support.get('intent', '-')}  boundary={support.get('boundary_notice', '-')}"))
    print(dim(f"risk_flags={_fmt_list(support.get('risk_flags'))}"))
    print(dim(f"contradictions={_fmt_list(support.get('contradictions'))}"))

    print()
    print(bold(yellow("CONTRATS / PERMISSIONS")))
    print(dim(f"decision_authority={data.get('decision_authority', 'KX108_ONLY')}"))
    print(dim(f"kernel={kernel.get('kernel', 'X108/KX108')}  kernel_mutation={_bool_text(kernel.get('kernel_mutation', data.get('kernel_mutation')))}  x108_mutation={_bool_text(kernel.get('x108_mutation'))}"))

    brody_perm = permission.get("brody", {}) if isinstance(permission, dict) else {}
    x108_perm = permission.get("x108", {}) if isinstance(permission, dict) else {}
    memory_perm = permission.get("memory", {}) if isinstance(permission, dict) else {}
    automation_perm = permission.get("automation", {}) if isinstance(permission, dict) else {}

    print(dim(
        "brody: "
        f"can_decide={_bool_text(brody_perm.get('can_decide'))} "
        f"can_act={_bool_text(brody_perm.get('can_act'))} "
        f"can_write_memory={_bool_text(brody_perm.get('can_write_memory'))} "
        f"can_mutate_x108={_bool_text(brody_perm.get('can_mutate_x108'))}"
    ))
    print(dim(
        "memory/automation: "
        f"memory_commit={_bool_text(memory_perm.get('can_commit'))} "
        f"automation_execute={_bool_text(automation_perm.get('can_execute'))} "
        f"requires_x108={_bool_text(automation_perm.get('requires_x108_decision'))}"
    ))
    print(dim(
        "x108: "
        f"sole_decision_authority={_bool_text(x108_perm.get('sole_decision_authority'))} "
        f"can_authorize_act={_bool_text(x108_perm.get('can_authorize_act'))}"
    ))

    print()
    print(bold(yellow("BOUNDARY")))
    print(dim(
        f"readonly={_bool_text(boundary.get('readonly', data.get('readonly')))}  "
        f"emits_act={_bool_text(boundary.get('emits_act', data.get('emits_act')))}  "
        f"emits_verdict={_bool_text(boundary.get('emits_verdict', data.get('emits_verdict')))}"
    ))
    print(dim(
        f"memory_write={_bool_text(boundary.get('memory_write', data.get('memory_write')))}  "
        f"graphiti_write={_bool_text(boundary.get('graphiti_write', data.get('graphiti_write')))}  "
        f"kernel_mutation={_bool_text(boundary.get('kernel_mutation', data.get('kernel_mutation')))}  "
        f"x108_mutation={_bool_text(boundary.get('x108_mutation'))}"
    ))
    print(dim(f"signal_contract={_get_path(contracts, ['signal_contract', 'decision_authority'], 'KX108_ONLY')}"))



def _print_true_voice_snapshot(data: dict[str, Any]) -> None:
    tv = data.get("true_voice_snapshot") or {}
    trs = data.get("true_response_structure_snapshot") or {}

    has_tv = isinstance(tv, dict) and bool(tv)
    has_trs = isinstance(trs, dict) and bool(trs)

    if not has_tv and not has_trs:
        return

    print(SEP)
    print(bold(yellow("TRUE VOICE / LLM OBSIDIEN")))

    if has_tv:
        print(dim(f"status={tv.get('status', '-')}"))
        print(dim(f"voice_source={tv.get('voice_source', tv.get('final_answer_source', '-'))}"))
        print(dim(f"final_answer_source={tv.get('final_answer_source', '-')}"))
        print(dim(f"source_mode={tv.get('source_mode', '-')}"))
        print(dim(f"boundary_integrated={_bool_text(tv.get('boundary_integrated'))}  no_metric_dump={_bool_text(tv.get('no_metric_dump'))}"))

    if has_trs:
        print(dim(f"model_position={trs.get('model_position', 'LLM_OBSIDIEN_READONLY_ADVISORY')}"))
        print(dim(f"foundation={trs.get('foundation', 'TRUE_RESPONSE_STRUCTURE')}  status={trs.get('status', '-')}"))
        print(dim(f"terminal_dialogue={_bool_text(trs.get('terminal_dialogue'))}  local_response_engine={_bool_text(trs.get('local_response_engine'))}"))

    print(dim("mode=structure-first; memory=enrichment; authority=KX108_ONLY"))


def _print_response(data: dict[str, Any], elapsed: float) -> None:
    true_voice = data.get("true_voice_snapshot") or {}
    tv_answer = true_voice.get("final_answer") if isinstance(true_voice, dict) else ""
    final    = (tv_answer or data.get("final_answer") or data.get("response") or data.get("response_md") or "").strip()
    source   = data.get("source", "?")
    g_status = data.get("graphiti_status", "")
    neo4j    = data.get("neo4j_status", "")
    auth     = data.get("decision_authority", "KX108_ONLY")
    language = data.get("language", "?")

    print()
    meta_parts = [dim(f"[{source}]"), dim(f"auth={auth}"), dim(f"lang={language}")]
    if g_status:
        meta_parts.append(dim(f"graphiti={g_status}"))
    if neo4j:
        meta_parts.append(dim(f"neo4j={neo4j}"))
    print(f"{bold(cyan('BRODY'))}  {'  '.join(meta_parts)}")
    print(SEP)
    if final:
        print(final)
    else:
        print(red("(réponse vide — vérifier les logs du backend)"))
    print()
    _print_true_voice_snapshot(data)
    print()
    _print_native_machination(data)
    print()
    print(dim(f"⏱  {elapsed:.1f}s"))
    print()


def _print_error(label: str, detail: str, hint: str = "") -> None:
    print()
    print(red(f"[{label}] {detail}"))
    if hint:
        print(yellow(f"  → {hint}"))
    print()


# ── Startup health check ──────────────────────────────────────────────────────

def _check_health() -> bool:
    print(dim(f"Connexion au backend {BASE_URL} ..."), end="", flush=True)
    try:
        health = _http_get(HEALTH_EP, timeout=5)
        status = health.get("status", "?")
        emitted = health.get("emitted", "?")
        print(green(f" OK  [{status}]  emitted={emitted}"))
        return True
    except urllib.error.URLError as e:
        reason = str(getattr(e, "reason", e))
        if "refused" in reason.lower():
            print(red(" ÉCHEC — Connection refused"))
            _print_error(
                "BACKEND HORS-LIGNE",
                f"Impossible de joindre {BASE_URL}",
                "Lance le backend : uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8001 --reload",
            )
        else:
            print(red(f" ÉCHEC — {reason}"))
        return False
    except Exception as e:
        print(red(f" ÉCHEC — {e}"))
        return False


# ── Main REPL ─────────────────────────────────────────────────────────────────

def run_once(session_id: str, message: str) -> None:
    print()
    print(bold(cyan("=== Brody Terminal CLI / once ===")))
    print(dim(f"  Endpoint : {ENDPOINT}"))
    print(dim(f"  Session  : {session_id}"))
    print()

    if not _check_health():
        sys.exit(1)

    print(dim(f"⟳  Envoi vers {ENDPOINT} ..."), flush=True)
    t0 = time.monotonic()

    data = _http_post(ENDPOINT, {
        "message": message,
        "language": "fr",
        "session_id": session_id,
    })
    _print_response(data, time.monotonic() - t0)

    required = ("contracts", "machination_packet", "support_routes", "support_summary")
    missing = [k for k in required if k not in data]
    if missing:
        raise SystemExit(f"MISSING_NATIVE_FIELDS: {missing}")

    if data.get("decision_authority") != "KX108_ONLY":
        raise SystemExit("DECISION_AUTHORITY_DRIFT")

    if data.get("emits_act") is not False:
        raise SystemExit("EMITS_ACT_DRIFT")

    if data.get("memory_write") is not False:
        raise SystemExit("MEMORY_WRITE_DRIFT")

    print(green("BRODY_TERMINAL_NATIVE_ONCE_OK"))



def run_repl(session_id: str) -> None:
    print()
    print(bold(cyan("=== Brody Terminal CLI ===")))
    print(dim(f"  Endpoint : {ENDPOINT}"))
    print(dim(f"  Session  : {session_id}"))
    print(dim("  Commandes: 'exit' / 'quit' / Ctrl+C pour fermer"))
    print()

    if not _check_health():
        sys.exit(1)

    print()
    print(dim("Prêt. Tape ta question en français."))
    print()

    while True:
        # ── Lecture input ──
        try:
            user_input = input(f"{bold('Vous')} > ").strip()
        except (EOFError, KeyboardInterrupt):
            print(dim("\nFermeture du terminal Brody."))
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q", ":q"):
            print(dim("Fermeture du terminal Brody."))
            break

        # ── Envoi ──
        print(dim(f"⟳  Envoi vers {ENDPOINT} ..."), flush=True)
        t0 = time.monotonic()

        try:
            data = _http_post(ENDPOINT, {
                "message":  user_input,
                "language": "fr",
                "session_id": session_id,
            })
            _print_response(data, time.monotonic() - t0)

        except urllib.error.HTTPError as e:
            _print_error(
                f"HTTP {e.code}",
                str(e.reason),
                "Vérifie les logs du backend pour le détail de l'erreur.",
            )

        except urllib.error.URLError as e:
            reason = str(getattr(e, "reason", e))
            if "refused" in reason.lower():
                _print_error(
                    "CONNEXION PERDUE",
                    f"Le backend ne répond plus sur {BASE_URL}",
                    "Relance : uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8001 --reload",
                )
            else:
                _print_error("RÉSEAU", reason)

        except TimeoutError:
            _print_error(
                "TIMEOUT",
                f"Pas de réponse après {TIMEOUT}s.",
                "Brody est peut-être en hydratation. Réessaie dans quelques secondes.",
            )

        except json.JSONDecodeError as e:
            _print_error("JSON", f"Réponse non-parseable : {e}")

        except Exception as e:
            _print_error(f"{type(e).__name__}", str(e))


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    global BASE_URL, ENDPOINT, HEALTH_EP
    parser = argparse.ArgumentParser(
        description="Brody Terminal CLI — dialogue direct avec le moteur Obsidia"
    )
    parser.add_argument(
        "--session", default="cli-terminal",
        help="Identifiant de session (défaut: cli-terminal)",
    )
    parser.add_argument(
        "--url", default=None,
        help=f"URL de base du backend (défaut: {BASE_URL})",
    )
    parser.add_argument(
        "--once", default=None,
        help="Envoie un seul message puis ferme le terminal.",
    )
    args = parser.parse_args()

    if args.url:
        BASE_URL  = args.url.rstrip("/")
        ENDPOINT  = f"{BASE_URL}/api/brody/chat"
        HEALTH_EP = f"{BASE_URL}/openapi.json"

    if args.once:
        run_once(args.session, args.once)
    else:
        run_repl(args.session)


if __name__ == "__main__":
    main()
