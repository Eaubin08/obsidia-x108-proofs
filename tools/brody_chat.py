#!/usr/bin/env python3
"""
Brody Terminal CLI
Dialogue direct avec le moteur Obsidia via http://127.0.0.1:8001/api/brody/chat
Aucune dépendance externe — stdlib Python 3.8+ uniquement.

Usage :
    python tools/brody_chat.py
    python tools/brody_chat.py --session mon_test
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from typing import Any

# ── Configuration ─────────────────────────────────────────────────────────────

BASE_URL  = "http://127.0.0.1:8001"
ENDPOINT  = f"{BASE_URL}/api/brody/chat"
HEALTH_EP = f"{BASE_URL}/bus/health"
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

def _print_response(data: dict[str, Any], elapsed: float) -> None:
    final    = (data.get("final_answer") or data.get("response") or "").strip()
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

def run_repl(session_id: str) -> None:
    print()
    print(bold(cyan("╔══ Brody Terminal CLI ══╗")))
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
    args = parser.parse_args()

    if args.url:
        global BASE_URL, ENDPOINT, HEALTH_EP
        BASE_URL  = args.url.rstrip("/")
        ENDPOINT  = f"{BASE_URL}/api/brody/chat"
        HEALTH_EP = f"{BASE_URL}/bus/health"

    run_repl(args.session)


if __name__ == "__main__":
    main()
