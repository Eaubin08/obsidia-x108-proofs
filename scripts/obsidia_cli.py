#!/usr/bin/env python3
"""OBSIDIA TERMINAL CLI — entree unique NON SOUVERAINE.

Usage:
    python scripts/obsidia_cli.py                    # shell interactif obsidia>
    python scripts/obsidia_cli.py doctor             # one-shot
    python scripts/obsidia_cli.py "statut du kernel"
    python scripts/obsidia_cli.py plan "sigma coherence"   # panneau OBSIDIA_ACTIVE_PLAN
    python scripts/obsidia_cli.py route "commit le kernel" # routage seul
    python scripts/obsidia_cli.py tools "obsidure status"  # outils/corpus seuls
    python scripts/obsidia_cli.py blockers | gates | scope | next

Garanties (par construction, pas par option) :
  - AUCUN subprocess : le CLI ne lance jamais de commande shell.
  - Seul EXECUTE possible : doctor/status/sigma via HTTP GET readonly.
  - Aucune ecriture hors de son receipt JSONL local non souverain.
  - Pas de --apply, --commit, --deploy, --act : ces flags n'existent pas.
  - stdlib uniquement, zero import de apps/, sigma/, periphery/.
  - decision_authority = KX108_ONLY. Le terminal ne decide rien.
  - Le Plan propose. Le terminal affiche. L'humain applique. X108 decide.
"""

from __future__ import annotations

import difflib
import json
import re
import socket
import sys
import unicodedata
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Import local du lexique (meme dossier), sans dependre du CWD.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from obsidia_guidance_vocabulary import (  # noqa: E402
    GUIDANCE_ACTIONS,
    NON_SOVEREIGN_RECEIPT_DEFAULTS,
    assert_output_allowed,
)
from obsidia_sigma_guidance import (  # noqa: E402
    collect_file_signals,
    derive_guidance,
    sigma_guidance_report,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = Path(__file__).resolve().parent / "obsidia_registry.yaml"


# ----------------------------------------------------------------------------
# Mini-parseur YAML (sous-ensemble : dicts indentes 2 espaces, listes inline).
# ----------------------------------------------------------------------------
def _parse_scalar(raw: str):
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inner, items, buf, depth, in_q = raw[1:-1], [], "", 0, False
        for ch in inner:
            if ch == '"':
                in_q = not in_q
            if ch == "," and depth == 0 and not in_q:
                items.append(buf.strip())
                buf = ""
            else:
                buf += ch
        if buf.strip():
            items.append(buf.strip())
        return [_parse_scalar(i) for i in items]
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1]
    low = raw.lower()
    if low in ("true", "false"):
        return low == "true"
    if low in ("null", "~", ""):
        return None
    try:
        return int(raw)
    except ValueError:
        return raw


def load_registry(path: Path) -> dict:
    root: dict = {}
    stack = [(-1, root)]
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.split("#", 1)[0].rstrip() if not line.lstrip().startswith("#") else ""
        if '"' in line and "#" in line:
            stripped = line.rstrip()
        if not stripped.strip():
            continue
        indent = len(stripped) - len(stripped.lstrip())
        key, _, value = stripped.lstrip().partition(":")
        while stack and stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        if value.strip():
            parent[key.strip()] = _parse_scalar(value)
        else:
            child: dict = {}
            parent[key.strip()] = child
            stack.append((indent, child))
    return root


# ----------------------------------------------------------------------------
# Normalisation IN
# ----------------------------------------------------------------------------
def normalize(text: str) -> str:
    folded = unicodedata.normalize("NFKD", text)
    folded = "".join(c for c in folded if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", folded.lower()).strip()


def score_layers(normalized: str, registry: dict) -> tuple[str, float, list[str]]:
    words = set(re.findall(r"[a-z0-9\-]+", normalized))
    best_layer, best_hits, reasons = "unknown", 0, []
    for layer, spec in registry.get("layers", {}).items():
        triggers = spec.get("triggers", []) or []
        hits = [t for t in triggers if t in words or (len(t) > 4 and t in normalized)]
        if len(hits) > best_hits:
            best_layer, best_hits = layer, len(hits)
            reasons = [f"trigger '{h}' -> {layer}" for h in hits]
    confidence = min(1.0, 0.4 + 0.3 * best_hits) if best_hits else 0.0
    return best_layer, round(confidence, 2), reasons


def policy_check(normalized: str, registry: dict) -> str | None:
    """Verifie les deny_keywords avec word-boundary (via _key_match).
    Correction V1 : k in normalized (substring brut) causait de faux positifs
    sur 'act' -> 'actuelle', 'action', 'impact', 'transaction', etc."""
    for kw in registry.get("policy", {}).get("deny_keywords", []) or []:
        k = str(kw).lower().strip()
        if k and _key_match(k, normalized):
            return k
    return None


# ----------------------------------------------------------------------------
# Doctor : EXECUTE readonly du terminal (HTTP GET, jamais de shell)
# ----------------------------------------------------------------------------
def run_doctor(registry: dict) -> dict:
    results = {}
    for name, url in (registry.get("health_endpoints") or {}).items():
        try:
            with urllib.request.urlopen(str(url), timeout=1.5) as resp:
                results[name] = {"url": url, "status": f"UP ({resp.status})"}
        except Exception as exc:  # serveur eteint = cas normal
            results[name] = {"url": url, "status": "DOWN", "fallback": "COMMAND_FALLBACK",
                             "detail": type(exc).__name__}
    return results


def _runtime_http_get_status(url: str, timeout: float = 1.0) -> dict:
    """GET readonly uniquement. HTTP 2xx/3xx = UP. Toute exception = DOWN/UNKNOWN.
    Aucun POST. Aucun subprocess. Non souverain."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            code = resp.status
            return {"status": "UP", "code": code} if 200 <= code < 400 \
                else {"status": "DOWN", "code": code}
    except urllib.error.URLError as exc:
        return {"status": "DOWN", "detail": type(exc).__name__}
    except OSError as exc:
        return {"status": "DOWN", "detail": type(exc).__name__}
    except Exception as exc:
        return {"status": "UNKNOWN", "detail": type(exc).__name__}


def _runtime_socket_status(host: str, port: int, timeout: float = 1.0) -> dict:
    """Sonde socket. connect_ex 0 = UP, sinon DOWN. Aucun subprocess."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            rc = s.connect_ex((host, port))
            return {"status": "UP" if rc == 0 else "DOWN", "rc": rc}
    except Exception as exc:
        return {"status": "UNKNOWN", "detail": type(exc).__name__}


def _runtime_local_status(checks: dict) -> dict:
    """Verifie l'existence de chemins locaux. Aucun parsing de contenu. Aucun I/O."""
    result = {}
    for key, spec in checks.items():
        all_ok = all((REPO_ROOT / p).exists() for p in spec["paths"])
        result[key] = {"label": spec["label"], "status": "OK" if all_ok else "MISSING"}
    return result


def _compute_terminal_state(network: dict, local: dict) -> str:
    """Regle READY/DEGRADED/BLOCKED. Conservative : BLOCKED uniquement si
    fichiers critiques manquants. READY si API 8000 UP + corpus OK."""
    if not (REPO_ROOT / "scripts" / "obsidia_cli.py").exists():
        return "BLOCKED"
    corpus_ok = local.get("corpus", {}).get("status") == "OK"
    gates_ok = local.get("gates", {}).get("status") == "OK"
    api_up = any(
        network.get(k, {}).get("status") == "UP"
        for k in ("api_health", "api_readiness", "api_status")
    )
    sigma_up = any(
        network.get(k, {}).get("status") == "UP"
        for k in ("sigma_domains", "sigma_evaluate")
    )
    if api_up and (sigma_up or gates_ok) and corpus_ok:
        return "READY"
    return "DEGRADED"


def build_runtime_service_map_v1() -> dict:
    """Carte readonly des services Obsidia. Aucun subprocess. Aucun POST.
    Aucun lancement de serveur. decision_authority = KX108_ONLY."""
    network: dict = {}
    for key, spec in RUNTIME_SERVICE_MAP_V1.items():
        kind = spec["kind"]
        if kind == "http_get":
            r = _runtime_http_get_status(spec["url"], spec.get("timeout", 1.0))
        elif kind == "socket":
            r = _runtime_socket_status(spec["host"], spec["port"],
                                        spec.get("timeout", 1.0))
        else:
            r = {"status": "UNKNOWN", "detail": f"kind inconnu: {kind}"}
        if spec.get("not_confirmed") and r.get("status") == "DOWN":
            r["status"] = "NOT_CONFIRMED"
        r["label"] = spec["label"]
        r["required"] = spec.get("required", False)
        network[key] = r
    local = _runtime_local_status(_RUNTIME_LOCAL_CHECKS)
    terminal_state = _compute_terminal_state(network, local)
    return {
        "panel": "OBSIDIA_RUNTIME_STATUS",
        "network": network,
        "local": local,
        "terminal_state": terminal_state,
    }


def format_runtime_service_map_v1(result: dict) -> str:
    """Formate la carte runtime. 1 ligne par service. Non souverain. Aucun droit."""
    lines = ["OBSIDIA RUNTIME STATUS", ""]
    for key, data in result["network"].items():
        label = data.get("label", key.upper())
        status = data.get("status", "UNKNOWN")
        note = " (observation locale : non confirme)" \
            if data.get("not_confirmed") and status in ("DOWN", "NOT_CONFIRMED") else ""
        lines.append(f"  {label:<26}: {status}{note}")
    lines.append("")
    lines.append("  # Ressources locales (existence)")
    for key, data in result["local"].items():
        label = data.get("label", key.upper())
        status = data.get("status", "MISSING")
        lines.append(f"  {label:<26}: {status}")
    lines.append("")
    state = result["terminal_state"]
    notes = {
        "READY": "(organes critiques accessibles)",
        "DEGRADED": "(API ou services optionnels indisponibles — terminal operable en local)",
        "BLOCKED": "(fichiers critiques manquants — terminal non operable)",
    }
    lines.append(f"  {'TERMINAL':<26}: {state}  {notes.get(state, '')}")
    lines.append("")
    lines.append("  [lecture seule — aucun service lance — X108 reste autorite]")
    return "\n".join(lines)


# ----------------------------------------------------------------------------
# Receipt non souverain (append-only, local, hors seal/manifest)
# ----------------------------------------------------------------------------
def write_receipt(registry: dict, payload: dict) -> Path:
    rel = registry.get("receipt_path") or ".local_obsidia/receipts/obsidia_terminal_receipts.jsonl"
    path = REPO_ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    record = dict(NON_SOVEREIGN_RECEIPT_DEFAULTS)
    record.update(payload)
    record["ts"] = datetime.now(timezone.utc).isoformat()
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


# ----------------------------------------------------------------------------
# Pipeline IN (INTACT — le panneau Plan l'enveloppe, ne le remplace pas)
# ----------------------------------------------------------------------------
def handle(raw: str, registry: dict) -> dict:
    normalized = normalize(raw)
    layer, confidence, reasons = score_layers(normalized, registry)
    spec = registry.get("layers", {}).get(layer, {})
    in_obj = {
        "raw": raw,
        "normalized_intent": normalized,
        "detected_layer": layer,
        "confidence": confidence,
        "mode": spec.get("mode", "unknown"),
        "route_reason": reasons or ["aucun trigger reconnu"],
    }

    file_signals = collect_file_signals()

    denied = policy_check(normalized, registry)
    if denied:
        in_obj.update(output=assert_output_allowed("POLICY_DENY"),
                      deny_keyword=denied,
                      message=registry.get("policy", {}).get("deny_message"),
                      commands=spec.get("commands", []))
        in_obj.update(derive_guidance(layer, "POLICY_DENY", file_signals))
        return in_obj

    if layer == "unknown":
        in_obj.update(output=assert_output_allowed("STOP_UNKNOWN"),
                      message="Intention non reconnue. Precise la couche visee "
                              "(brody, obsidure, obsidienne, kernel, domains, audit, memory, live, sigma).")
        in_obj.update(derive_guidance(layer, "STOP_UNKNOWN", file_signals))
        return in_obj

    if layer == "sigma":
        in_obj["output"] = assert_output_allowed("EXECUTE")
        in_obj["sigma"] = sigma_guidance_report()
        in_obj.update({k: v for k, v in in_obj["sigma"].items() if k.startswith("guidance")})
        in_obj["commands"] = spec.get("commands", [])
        return in_obj

    if layer == "live" or "doctor" in normalized:
        in_obj.update(output=assert_output_allowed("EXECUTE"),
                      doctor=run_doctor(registry))
        in_obj.update(derive_guidance(layer, "EXECUTE", file_signals))
        return in_obj

    in_obj.update(output=assert_output_allowed("COMMANDS"),
                  commands=spec.get("commands", []),
                  note=spec.get("note", ""))
    in_obj.update(derive_guidance(layer, "COMMANDS", file_signals))
    return in_obj


# ============================================================================
# OBSIDIA_ACTIVE_PLAN — panneau non souverain (nouvelle ligne post-freeze V1)
# Le Plan propose. Le terminal affiche. L'humain applique. X108 decide.
# Le Plan ne lance rien, ne modifie rien, n'ecrit pas en memoire.
# Mode stateless : aucun fichier plan, seul le receipt normal est ecrit.
# ============================================================================
PANEL_COMMANDS = ("plan", "route", "tools", "blockers", "gates", "scope", "next")

PLAN_STATUSES = ("ROUTED", "WAITING_FOR_HUMAN", "BLOCKED_BY_STAGED_FILES",
                 "READY_FOR_REVIEW", "NEEDS_SCOPE_CONFIRMATION",
                 "NO_ACTION_TAKEN", "POLICY_CUT")

FORBIDDEN_ALWAYS = (
    "git commit/push/deploy [OUTIL_INTERDIT]",
    "mutation Kernel/X108 [OUTIL_INTERDIT]",
    "mutation Sigma Core [OUTIL_INTERDIT]",
    "memory write [OUTIL_INTERDIT]",
    "execution Obsidure [OUTIL_INTERDIT]",
    "execution Lean [OUTIL_INTERDIT]",
    "lancement stack [OUTIL_INTERDIT]",
    "ecriture .local_obsidia/plan/ [OUTIL_INTERDIT]",
)

# --- Capacites / organes Obsidia (couches conceptuelles, distinctes des
#     outils techniques). Roles documentes dans la spec PLAN_PANEL_V1. ---
ORGANES_INTERDITS_TOUJOURS = (
    "Kernel/X108 mutation [INTERDIT]",
    "Memory write [INTERDIT]",
    "Obsidure execution automatique [INTERDIT]",
    "Lean execution automatique [INTERDIT]",
    "Apply/Commit/Push automatique [INTERDIT]",
)

_ORGANES_BASE = ["Terminal: affichage/routage non souverain [MOBILISE]",
                 "OS Langage Uni: normalisation de l'IN [MOBILISE]",
                 "Registry: source locale de routage [MOBILISE]",
                 "Receipts: trace locale non souveraine [MOBILISE]"]

PLAN_ORGANES: dict = {
    "sigma": {
        "mobilises": _ORGANES_BASE + ["Sigma: coherence/contradiction/freshness [MOBILISE]"],
        "mobilisables": ["Brody: explication du resultat [MOBILISABLE]",
                         "Audit/Merkle: lecture de traces [MOBILISABLE]",
                         "Thermo: analyse friction/cout si disponible [MOBILISABLE]"],
        "interdits": ["Sigma Core mutation [INTERDIT]"]},
    "live": {
        "mobilises": _ORGANES_BASE + ["Terminal: doctor readonly [MOBILISE]"],
        "mobilisables": ["Brody: explication du statut [MOBILISABLE]"],
        "interdits": ["lancement stack par le terminal [INTERDIT]"]},
    "obsidienne": {
        "mobilises": _ORGANES_BASE,
        "mobilisables": ["Lean/Proofs: verification commands-only [MOBILISABLE]",
                         "Sigma: guidance fraicheur des preuves [MOBILISABLE]",
                         "Brody: explication [MOBILISABLE]"],
        "interdits": []},
    "obsidure": {
        "mobilises": _ORGANES_BASE,
        "mobilisables": ["Obsidure: proposal builder commands-only [MOBILISABLE]",
                         "Brody: clarification/explication [MOBILISABLE]",
                         "OS Langage Uni: structuration de l'intention [MOBILISABLE]",
                         "Gates: validation future [MOBILISABLE]",
                         "Lean/Proofs: sandbox via workflow gated [MOBILISABLE]"],
        "interdits": []},
    "kernel": {
        "mobilises": _ORGANES_BASE,
        "mobilisables": ["Kernel/X108: consultation status readonly [MOBILISABLE]",
                         "Audit/Merkle: lecture de traces [MOBILISABLE]"],
        "interdits": ["emission ALLOW/BLOCK/HOLD/ACT par le terminal [INTERDIT]"]},
    "domains": {
        "mobilises": _ORGANES_BASE,
        "mobilisables": ["Domains: bridge-only KX108_ONLY [MOBILISABLE]",
                         "Sigma: monitoring domaines readonly [MOBILISABLE]"],
        "interdits": ["ACT domaine [INTERDIT]"]},
    "audit": {
        "mobilises": _ORGANES_BASE + ["Audit/Merkle: lecture manifests/seals [MOBILISE]"],
        "mobilisables": ["Lean/Proofs: verifiers commands-only [MOBILISABLE]",
                         "Thermo: cout/friction si disponible [MOBILISABLE]"],
        "interdits": ["regeneration seal/manifest [INTERDIT]"]},
    "memory": {
        "mobilises": _ORGANES_BASE,
        "mobilisables": ["Memory/Graphiti: frozen status readonly [MOBILISABLE]",
                         "Brody: contexte [MOBILISABLE]"],
        "interdits": []},
    "brody": {
        "mobilises": _ORGANES_BASE + ["Brody: explication/synthese/contexte [MOBILISE]"],
        "mobilisables": ["Memory/Graphiti: lecture readonly [MOBILISABLE]",
                         "Sigma: guidance [MOBILISABLE]"],
        "interdits": []},
    "terminal_self": {
        "mobilises": _ORGANES_BASE + ["LOCAL_CORPUS terminal_self [MOBILISE, READONLY]"],
        "mobilisables": [],
        "interdits": ["mutation Kernel/Sigma/X108 [INTERDIT]",
                      "emission ALLOW/BLOCK/HOLD/ACT [INTERDIT]"]},
    "gates": {
        "mobilises": _ORGANES_BASE + ["Gates: lecture scripts/gates/ [MOBILISE, READONLY]"],
        "mobilisables": ["Obsidure: workflow gated post-gate [MOBILISABLE]",
                         "Audit/Merkle: verification seal [MOBILISABLE]"],
        "interdits": ["execution automatique des gates par le terminal [INTERDIT]",
                      "decision final sur gate pass/fail [INTERDIT — X108]"]},
    "oie": {
        "mobilises": _ORGANES_BASE + ["OIE: lecture receipts local [MOBILISE, READONLY]"],
        "mobilisables": ["Brody: explication economie inference [MOBILISABLE]",
                         "Thermo: friction/cost si disponible [MOBILISABLE]"],
        "interdits": ["lancement benchmark en prod depuis le terminal [INTERDIT]",
                      "COST_REAL reclamation sans preuve [INTERDIT]"]},
    "thermo": {
        "mobilises": _ORGANES_BASE + ["LOCAL_CORPUS energy_thermo [MOBILISE, READONLY]"],
        "mobilisables": ["Sigma: guidance coherence/verite [MOBILISABLE]",
                         "Brody: explication friction [MOBILISABLE]"],
        "interdits": ["decision thermo [INTERDIT]",
                      "mutation sigma via thermo [INTERDIT]"]},
    "unknown": {
        "mobilises": ["Terminal: affichage non souverain [MOBILISE]",
                      "OS Langage Uni: normalisation (echec de structuration) [MOBILISE]",
                      "Registry: routage (aucun trigger) [MOBILISE]"],
        "mobilisables": [],
        "interdits": ["tout organe d'action tant que la couche est inconnue [NON_NECESSAIRE]"]},
}

_BASE_USED = ["registry [OUTIL_UTILISE]", "policy_check [OUTIL_UTILISE]",
              "vocabulaire guidance [OUTIL_UTILISE]", "receipt local [OUTIL_UTILISE]",
              "collect_file_signals [OUTIL_UTILISE, OUTIL_READONLY]"]

PLAN_TOOLING: dict = {
    "sigma": {
        "utilises": _BASE_USED + ["sigma_guidance_report [OUTIL_UTILISE]"],
        "mobilisables": ["live HTTP GET readonly [OUTIL_READONLY — appele a l'execution reelle]",
                         "curl routes monitoring sigma [OUTIL_READONLY]"],
        "corpus": ["PROOFKIT_REPORT.json (fraicheur)", "manifest Lean (forbidden_ok, lean_decides)",
                   "merkle_seal.json (lecture seule)", "_PATCH_PROPOSALS/ readonly (compte)",
                   "stress_tests [diagnostic only]"],
        "exclus": ["mutation Sigma Core [OUTIL_INTERDIT]", "regeneration seal [OUTIL_INTERDIT]"],
    },
    "live": {
        "utilises": _BASE_USED + ["doctor readonly [OUTIL_UTILISE]"],
        "mobilisables": ["live HTTP GET readonly [OUTIL_READONLY]"],
        "corpus": ["registry.health_endpoints"],
        "exclus": ["lancement stack [OUTIL_INTERDIT]"],
    },
    "obsidienne": {
        "utilises": _BASE_USED,
        "mobilisables": ["python proofs/verify_all.py [OUTIL_COMMANDS_ONLY — ecrit PROOFKIT, humain uniquement]",
                         "lake build [OUTIL_COMMANDS_ONLY, gated]"],
        "corpus": ["manifest Lean (232 entrees)", "PROOFKIT_REPORT.json", "docs/protocols/"],
        "exclus": ["execution Lean par le terminal [OUTIL_INTERDIT]",
                   "mutation proofs/ [OUTIL_INTERDIT]"],
    },
    "obsidure": {
        "utilises": _BASE_USED + ["signal obsidure readonly [OUTIL_UTILISE]"],
        "mobilisables": ["scripts/run_agent_obsidure.ps1 [OUTIL_COMMANDS_ONLY — jamais lance]"],
        "corpus": ["_PATCH_PROPOSALS/ readonly (proposals + receipts)",
                   "docs/protocols/OBSIDURE_APPLY_PROTOCOL.md"],
        "exclus": ["apply proposal [OUTIL_INTERDIT]", "lean_sandbox [OUTIL_INTERDIT]"],
    },
    "kernel": {
        "utilises": _BASE_USED,
        "mobilisables": ["curl status kernel [OUTIL_READONLY, NOT_CONFIRMED]"],
        "corpus": ["docs/protocols/KERNEL_BOUNDARY_CHECK_PROTOCOL.md", "formal/tla/ (lecture)"],
        "exclus": ["mutation Kernel/X108 [OUTIL_INTERDIT]",
                   "emission ALLOW/BLOCK/HOLD/ACT [OUTIL_INTERDIT]"],
    },
    "domains": {
        "utilises": _BASE_USED,
        "mobilisables": ["curl routes monitoring [OUTIL_READONLY]"],
        "corpus": ["registry.domains (bridge-only, POST_ONLY_ADAPTERS)"],
        "exclus": ["ACT domaine [OUTIL_INTERDIT]",
                   "adapters POST en GET doctor [OUTIL_INTERDIT]"],
    },
    "audit": {
        "utilises": _BASE_USED,
        "mobilisables": ["python proofs/verify_merkle.py [OUTIL_COMMANDS_ONLY, readonly]",
                         "python proofs/verify_all.py [OUTIL_COMMANDS_ONLY — ecrit PROOFKIT]"],
        "corpus": ["merkle_seal.json (lecture)", "MANIFEST_SHA256.json (lecture)", "freeze docs"],
        "exclus": ["regeneration seal/manifest [OUTIL_INTERDIT]"],
    },
    "memory": {
        "utilises": _BASE_USED,
        "mobilisables": ["curl graphiti frozen status [OUTIL_READONLY]"],
        "corpus": ["registry.memory (memory_write=false)"],
        "exclus": ["memory write [OUTIL_INTERDIT]"],
    },
    "brody": {
        "utilises": _BASE_USED,
        "mobilisables": ["launchers stack Brody [OUTIL_COMMANDS_ONLY]",
                         "/api/brody/* (POST, hors doctor) [OUTIL_NON_NECESSAIRE en plan]"],
        "corpus": ["registry.brody (Brody = API 8000, non souverain)"],
        "exclus": ["lancement stack par le terminal [OUTIL_INTERDIT]"],
    },
    "terminal_self": {
        "utilises": _BASE_USED + ["LOCAL_CORPUS terminal_self [OUTIL_UTILISE, READONLY]"],
        "mobilisables": [],
        "corpus": ["scripts/obsidia_cli.py (LOCAL_CORPUS terminal_self, capabilities, "
                   "terminal_function, terminal_diagnostic)",
                   "scripts/obsidia_registry.yaml (couches, triggers, policy)",
                   "CLAUDE.md (doctrines, interdits, couche routing)"],
        "exclus": ["mutation code [OUTIL_INTERDIT]",
                   "emission ALLOW/BLOCK/HOLD/ACT [OUTIL_INTERDIT]"],
    },
    "gates": {
        "utilises": _BASE_USED + ["collect_file_signals gates [OUTIL_UTILISE, READONLY]"],
        "mobilisables": ["python scripts/gates/*.py [OUTIL_COMMANDS_ONLY — jamais auto]"],
        "corpus": ["scripts/gates/ (5 gates V0)", "tests/gates/ (pytest -q readonly)"],
        "exclus": ["auto-execution des gates [OUTIL_INTERDIT]",
                   "decision pass/fail gate [OUTIL_INTERDIT — X108]"],
    },
    "oie": {
        "utilises": _BASE_USED,
        "mobilisables": ["scripts/performance/run_oie_external_claude_benchmark_v0.py --dry-run [OUTIL_COMMANDS_ONLY]",
                         "cat oie_external_claude_benchmark_v0_receipts.json [OUTIL_READONLY]"],
        "corpus": ["scripts/performance/oie_external_claude_benchmark_v0_receipts.json (lecture)",
                   "LOCAL_CORPUS oie"],
        "exclus": ["lancement benchmark en prod [OUTIL_INTERDIT]",
                   "COST_REAL reclamation sans preuve [OUTIL_INTERDIT]"],
    },
    "thermo": {
        "utilises": _BASE_USED + ["LOCAL_CORPUS energy_thermo [OUTIL_UTILISE, READONLY]"],
        "mobilisables": ["Sigma monitoring [OUTIL_READONLY]"],
        "corpus": ["LOCAL_CORPUS energy_thermo",
                   "docs/protocols/ thermo si present"],
        "exclus": ["decision thermo [OUTIL_INTERDIT]",
                   "mutation sigma [OUTIL_INTERDIT]"],
    },
    "unknown": {
        "utilises": ["registry [OUTIL_UTILISE — echec routage]", "receipt local [OUTIL_UTILISE]"],
        "mobilisables": [],
        "corpus": ["aucun (couche inconnue)"],
        "exclus": ["tout outil d'action [OUTIL_NON_NECESSAIRE tant que la couche est inconnue]"],
    },
}

GATES_KNOWN = (
    "python scripts/gates/obsidia_commit_scope_guard.py --allow <fichiers du scope>",
    "python scripts/gates/obsidia_kernel_boundary_check.py --staged-only",
    "python scripts/gates/obsidia_sigma_non_sovereignty_check.py",
    "python -m pytest tests/gates/ -q",
)

# Sous-ensembles de gates par couche (noms de script uniquement, sans 'python' ni args).
# Source : scripts/gates/*.py — 5 scripts au total.
_GATES_SIGMA = ["obsidia_sigma_non_sovereignty_check.py"]
_GATES_OBSIDURE = ["obsidia_commit_scope_guard.py",
                   "obsidia_forbidden_write_check.py",
                   "obsidia_lean_manifest_guard.py"]
_GATES_KERNEL = ["obsidia_kernel_boundary_check.py"]
_GATES_OBSIDIENNE = ["obsidia_lean_manifest_guard.py"]
_GATES_AUDIT = ["obsidia_commit_scope_guard.py"]
_GATES_DOMAINS = ["obsidia_kernel_boundary_check.py"]

# Vocabulaire d'operations positivement autorisees dans le terminal.
_OPS_READ = ["READ_LOCAL_WINDOW", "READ_LOCAL_DOCX"]
_OPS_SEARCH = ["SEARCH_LOCAL_TEXT", "SEARCH_LOCAL_CONTEXT"]
_OPS_EXTRACT = ["SUMMARIZE_LOCAL_PROGRESSIVE", "EXPLAIN_LOCAL_PROGRESSIVE",
                "COMPARE_LOCAL_BOUNDED"]
_OPS_DISPLAY = ["CORPUS_LOOKUP", "PLAN_DISPLAY", "CAPABILITY_DISPLAY", "COMMANDS_DISPLAY"]
_OPS_DOCTOR = ["DOCTOR_HTTP_GET"]

# Vocabulaire d'interdits communs.
_INTERDIT_COMMON = ["EMIT_ALLOW_BLOCK_HOLD_ACT"]

CAPABILITY_GRAPH_V3: dict = {
    "sigma": {
        "ops_allowed": _OPS_READ + _OPS_SEARCH + _OPS_DOCTOR + _OPS_DISPLAY,
        "ops_forbidden": _INTERDIT_COMMON + ["MUTATE_SIGMA_CORE"],
        "corpus_topics": ["sigma", "gates", "doctrine"],
        "gates_applicable": _GATES_SIGMA,
        "cross_concerns": ["Thermo: SIGMA_TRUTH_MISMATCH",
                           "OIE: cout validation sigma"],
    },
    "obsidure": {
        "ops_allowed": (_OPS_READ + _OPS_SEARCH + _OPS_EXTRACT
                        + ["COMMANDS_DISPLAY", "CORPUS_LOOKUP", "PLAN_DISPLAY",
                           "CAPABILITY_DISPLAY"]),
        "ops_forbidden": _INTERDIT_COMMON + ["APPLY_PROPOSAL",
                                              "EXEC_LEAN_FROM_TERMINAL"],
        "corpus_topics": ["obsidure", "gates", "lean_proofs"],
        "gates_applicable": _GATES_OBSIDURE,
        "cross_concerns": ["OIE: cout par action generee",
                           "Thermo: thermo_debt proposal"],
    },
    "live": {
        "ops_allowed": _OPS_DOCTOR + _OPS_DISPLAY,
        "ops_forbidden": _INTERDIT_COMMON + ["LAUNCH_STACK"],
        "corpus_topics": [],
        "gates_applicable": [],
        "cross_concerns": [],
    },
    "obsidienne": {
        "ops_allowed": (_OPS_READ + _OPS_SEARCH + _OPS_EXTRACT
                        + ["CORPUS_LOOKUP", "PLAN_DISPLAY", "CAPABILITY_DISPLAY",
                           "COMMANDS_DISPLAY"]),
        "ops_forbidden": _INTERDIT_COMMON + ["EXEC_LEAN_FROM_TERMINAL"],
        "corpus_topics": ["lean_proofs", "audit_merkle"],
        "gates_applicable": _GATES_OBSIDIENNE,
        "cross_concerns": ["OIE: cout proof check"],
    },
    "kernel": {
        "ops_allowed": _OPS_DISPLAY + _OPS_DOCTOR,
        "ops_forbidden": _INTERDIT_COMMON + ["MUTATE_KERNEL"],
        "corpus_topics": ["doctrine", "kernel_x108"],
        "gates_applicable": _GATES_KERNEL,
        "cross_concerns": [],
    },
    "domains": {
        "ops_allowed": _OPS_DOCTOR + _OPS_DISPLAY,
        "ops_forbidden": _INTERDIT_COMMON + ["ACT_DOMAIN"],
        "corpus_topics": ["domains"],
        "gates_applicable": _GATES_DOMAINS,
        "cross_concerns": [],
    },
    "audit": {
        "ops_allowed": (_OPS_READ + _OPS_SEARCH + _OPS_EXTRACT
                        + ["CORPUS_LOOKUP", "PLAN_DISPLAY", "CAPABILITY_DISPLAY",
                           "COMMANDS_DISPLAY"]),
        "ops_forbidden": _INTERDIT_COMMON + ["REGENERATE_SEAL",
                                              "REGENERATE_MANIFEST"],
        "corpus_topics": ["audit_merkle", "lean_proofs"],
        "gates_applicable": _GATES_AUDIT,
        "cross_concerns": ["OIE: chaine d'audit cout/action"],
    },
    "memory": {
        "ops_allowed": _OPS_DOCTOR + _OPS_DISPLAY,
        "ops_forbidden": _INTERDIT_COMMON + ["MEMORY_WRITE"],
        "corpus_topics": ["memory"],
        "gates_applicable": [],
        "cross_concerns": ["Thermo: projection frozen status"],
    },
    "brody": {
        "ops_allowed": (_OPS_READ + _OPS_DISPLAY),
        "ops_forbidden": _INTERDIT_COMMON + ["BRODY_POST_FROM_TERMINAL",
                                              "LAUNCH_STACK"],
        "corpus_topics": ["brody", "energy_thermo"],
        "gates_applicable": [],
        "cross_concerns": ["Thermo: Thermodynamics Signal F3",
                           "OIE: cout synthese"],
    },
    "terminal_self": {
        "ops_allowed": ["CORPUS_LOOKUP", "CAPABILITY_DISPLAY", "PLAN_DISPLAY"],
        "ops_forbidden": _INTERDIT_COMMON,
        "corpus_topics": ["terminal_self", "capabilities",
                          "terminal_function", "terminal_diagnostic"],
        "gates_applicable": [],
        "cross_concerns": [],
    },
    "gates": {
        "ops_allowed": ["READ_LOCAL_WINDOW", "CORPUS_LOOKUP", "PLAN_DISPLAY",
                        "COMMANDS_DISPLAY"],
        "ops_forbidden": _INTERDIT_COMMON + ["AUTO_EXECUTE_GATE"],
        "corpus_topics": ["gates"],
        "gates_applicable": list(dict.fromkeys(_GATES_SIGMA + _GATES_OBSIDURE + _GATES_KERNEL)),
        "cross_concerns": ["Sigma: coherence post-gate",
                           "OIE: cout verification build"],
    },
    "oie": {
        "ops_allowed": ["READ_LOCAL_WINDOW", "CORPUS_LOOKUP", "PLAN_DISPLAY"],
        "ops_forbidden": _INTERDIT_COMMON + ["BENCHMARK_RUN_AUTO"],
        "corpus_topics": ["oie"],
        "gates_applicable": list(_GATES_OBSIDURE),

        "cross_concerns": ["Thermo: friction/cout inference",
                           "Sigma: verite vs economie"],
    },
    "thermo": {
        "ops_allowed": ["CORPUS_LOOKUP", "PLAN_DISPLAY"],
        "ops_forbidden": _INTERDIT_COMMON + ["THERMO_DECISION"],
        "corpus_topics": ["energy_thermo"],
        "gates_applicable": [],
        "cross_concerns": ["Sigma: truth mismatch / vieillissement",
                           "OIE: cout dissipation inference"],
    },
    "unknown": {
        "ops_allowed": [],
        "ops_forbidden": ["tout — couche inconnue"],
        "corpus_topics": [],
        "gates_applicable": [],
        "cross_concerns": [],
    },
}

# ---------------------------------------------------------------------------
# RUNTIME_SERVICE_MAP_V1 — carte statique des services Obsidia.
# Aucun subprocess. Aucun POST. Aucun lancement. Aucune mutation.
# Sondes : urllib.request GET (http_get) et socket.connect_ex (socket).
# decision_authority = KX108_ONLY.
# ---------------------------------------------------------------------------
RUNTIME_SERVICE_MAP_V1: dict = {
    "api_health": {
        "kind": "http_get", "label": "API_HEALTH",
        "url": "http://127.0.0.1:8000/api/health",
        "required": True, "timeout": 1.0,
    },
    "api_readiness": {
        "kind": "http_get", "label": "API_READINESS",
        "url": "http://127.0.0.1:8000/api/readiness",
        "required": False, "timeout": 1.0,
    },
    "api_status": {
        "kind": "http_get", "label": "API_STATUS",
        "url": "http://127.0.0.1:8000/api/status",
        "required": False, "timeout": 1.0,
    },
    "kernel_3001": {
        "kind": "socket", "label": "KERNEL_3001",
        "host": "127.0.0.1", "port": 3001,
        "required": False, "not_confirmed": True, "timeout": 1.0,
    },
    "graphiti_8011": {
        "kind": "http_get", "label": "GRAPHITI_8011",
        "url": "http://127.0.0.1:8011/graph/v20/frozen/status",
        "required": False, "timeout": 1.0,
    },
    "neo4j_bolt_7688": {
        "kind": "socket", "label": "NEO4J_BOLT_7688",
        "host": "127.0.0.1", "port": 7688,
        "required": False, "timeout": 1.0,
    },
    "neo4j_browser_7475": {
        "kind": "socket", "label": "NEO4J_BROWSER_7475",
        "host": "127.0.0.1", "port": 7475,
        "required": False, "timeout": 1.0,
    },
    "ui_5173": {
        "kind": "http_get", "label": "UI_5173",
        "url": "http://127.0.0.1:5173/",
        "required": False, "timeout": 1.0,
    },
    "sigma_domains": {
        "kind": "http_get", "label": "SIGMA_DOMAINS",
        "url": "http://127.0.0.1:8000/api/periphery/monitoring/sigma/domains",
        "required": False, "timeout": 1.0,
    },
    "sigma_evaluate": {
        "kind": "http_get", "label": "SIGMA_EVALUATE",
        "url": "http://127.0.0.1:8000/api/periphery/monitoring/sigma/evaluate",
        "required": False, "timeout": 1.0,
    },
}

# Vérifications locales readonly — existence de chemins uniquement, aucun parsing contenu.
_RUNTIME_LOCAL_CHECKS: dict = {
    "gates": {
        "label": "GATES",
        "paths": [
            "scripts/gates/obsidia_sigma_non_sovereignty_check.py",
            "scripts/gates/obsidia_kernel_boundary_check.py",
            "scripts/gates/obsidia_forbidden_write_check.py",
            "scripts/gates/obsidia_lean_manifest_guard.py",
        ],
    },
    "lean_manifest": {
        "label": "LEAN_MANIFEST",
        "paths": ["proofs/LEAN_PROOF_SURFACE_MANIFEST.json"],
    },
    "oie_reports": {
        "label": "OIE_REPORTS",
        "paths": ["scripts/performance/oie_external_claude_benchmark_v0_receipts.json"],
    },
    "patch_proposals": {
        "label": "PATCH_PROPOSALS",
        "paths": ["_PATCH_PROPOSALS"],
    },
    "corpus": {
        "label": "CORPUS",
        "paths": ["docs/specs", "docs/protocols"],
    },
}


def _resolve_corpus_topics(topics: list) -> dict:
    """Lecture pure LOCAL_CORPUS par liste de cles. Aucun I/O. Non souverain."""
    result = {}
    for t in topics:
        if t not in LOCAL_CORPUS:
            result[t] = "(topic absent du LOCAL_CORPUS)"
            continue
        entry = LOCAL_CORPUS[t]
        if entry.get("loader") == "freeze":
            result[t] = _freeze_summary() or "(freeze non lisible)"
        else:
            result[t] = entry.get("answer", "(pas de reponse corpus)")
    return result


def build_capability_view(raw: str, registry: dict,
                          verbose: bool = False, plan: dict = None) -> dict:
    """Carte statique readonly des capacites pour la couche detectee de raw.
    Non souverain. Aucun subprocess. Aucun I/O hors corpus. decision_authority=KX108_ONLY."""
    if plan is None:
        plan = build_active_plan(raw, registry)
    layer = plan["detected_layer"]
    cap_layer = layer.split(":")[0] if ":" in layer else layer
    cap = CAPABILITY_GRAPH_V3.get(cap_layer, CAPABILITY_GRAPH_V3["unknown"])
    corpus_answers = _resolve_corpus_topics(cap["corpus_topics"]) if verbose else {}
    denied = plan.get("deny_keyword")
    return {
        "panel": "OBSIDIA_CAPABILITY_VIEW",
        "raw": raw,
        "detected_layer": layer,
        "confidence": plan["confidence"],
        "ops_allowed": cap["ops_allowed"],
        "ops_forbidden": cap["ops_forbidden"],
        "corpus_topics": cap["corpus_topics"],
        "corpus_answers": corpus_answers,
        "gates_applicable": cap["gates_applicable"],
        "cross_concerns": cap["cross_concerns"],
        "organes_mobilises": plan["organes_mobilises"],
        "organes_interdits": plan["organes_interdits"],
        "next_human_action": plan["next_human_action"],
        "deny_keyword": denied,
        "output": "POLICY_DENY" if denied else "GUIDE",
    }


def format_capability_view(view: dict, verbose: bool = False) -> str:
    """Formate la capability view. Compact : 1 ligne/section. Verbose : listes deployees."""
    if view.get("deny_keyword"):
        return (f"POLICY_DENY : mot interdit \"{view['deny_keyword']}\". "
                "Aucune capability accessible avant levee de la policy.")
    hdr = (f"CAPABILITY_VIEW — couche: {view['detected_layer']} "
           f"| confiance: {view['confidence']}")
    def _join(lst, max_n=None):
        items = lst[:max_n] if max_n else lst
        return " · ".join(items) if items else "aucune"
    if not verbose:
        return "\n".join([
            hdr,
            "OPS AUTORISEES  : " + _join(view["ops_allowed"]),
            "OPS INTERDITES  : " + _join(view["ops_forbidden"], 4),
            "CORPUS TOPICS   : " + (_join(view["corpus_topics"]) if view["corpus_topics"]
                                    else "aucun"),
            "GATES           : " + (_join(view["gates_applicable"]) if view["gates_applicable"]
                                    else "aucun specifique"),
            "CROSS-CONCERNS  : " + (_join(view["cross_concerns"]) if view["cross_concerns"]
                                    else "aucun"),
            "NEXT            : " + view["next_human_action"],
        ])
    # Verbose
    lines = [hdr, ""]
    lines += ["OPS AUTORISEES :"]
    lines += (["  - " + o for o in view["ops_allowed"]] if view["ops_allowed"]
              else ["  - aucune"])
    lines += ["", "OPS INTERDITES :"]
    lines += (["  - " + o for o in view["ops_forbidden"]] if view["ops_forbidden"]
              else ["  - aucune"])
    lines += ["", "CORPUS TOPICS :"]
    lines += (["  - " + t for t in view["corpus_topics"]] if view["corpus_topics"]
              else ["  - aucun"])
    if view.get("corpus_answers"):
        lines.append("")
        lines.append("CORPUS ANSWERS :")
        for t, ans in view["corpus_answers"].items():
            lines.append(f"  [{t}]")
            for ln in str(ans).splitlines():
                lines.append("    " + ln)
    lines += ["", "GATES APPLICABLES :"]
    lines += (["  - " + g for g in view["gates_applicable"]] if view["gates_applicable"]
              else ["  - aucun specifique"])
    lines += ["", "CROSS-CONCERNS :"]
    lines += (["  - " + c for c in view["cross_concerns"]] if view["cross_concerns"]
              else ["  - aucun"])
    lines += ["", "ORGANES MOBILISES :"]
    lines += (["  - " + o for o in view["organes_mobilises"]] if view["organes_mobilises"]
              else ["  - aucun"])
    lines += ["", "NEXT ACTION HUMAINE :", "  " + view["next_human_action"]]
    return "\n".join(lines)


def _parse_capabilities_input(raw: str):
    """Detecte le prefixe 'capabilities' dans raw.
    Retourne (inner_in, verbose) ou (None, False)."""
    norm = raw.strip()
    if norm.lower().startswith("obsidia "):
        norm = norm[8:].strip()
    if not norm.lower().startswith("capabilities"):
        return None, False
    rest = norm[len("capabilities"):].strip()
    verbose = False
    if rest.startswith("-v ") or rest.startswith("-v"):
        verbose = True
        rest = rest[2:].strip()
    elif rest.startswith("--verbose ") or rest.startswith("--verbose"):
        verbose = True
        rest = rest[9:].strip()
    inner = rest.strip().strip('"').strip("'")
    return (inner if inner else "terminal_self"), verbose


_RUNTIME_TRIGGERS = frozenset({
    "runtime", "runtime status", "doctor --full", "status --full",
    "cockpit status", "etat runtime", "etat du runtime",
    "obsidia runtime", "obsidia doctor", "obsidia status",
    "etat services", "services status", "check services",
})


def _parse_runtime_input(raw: str) -> bool:
    """Retourne True si raw est une commande de runtime service map."""
    norm = raw.strip().lower()
    if norm.startswith("obsidia "):
        norm = norm[8:].strip()
    return norm in _RUNTIME_TRIGGERS or any(norm.startswith(t) for t in _RUNTIME_TRIGGERS)


def dedupe_preserve_order(items):
    """Dedoublonnage stable, purement cosmetique (aucun droit modifie)."""
    seen, out = set(), []
    for i in items:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


def _build_capability_summary(layer: str, raw: str) -> dict:
    """Extrait un resume compact du graph (max 5 ops + 3 cross-concerns). Aucun I/O."""
    cap_layer = layer.split(":")[0] if ":" in layer else layer
    cap = CAPABILITY_GRAPH_V3.get(cap_layer, CAPABILITY_GRAPH_V3["unknown"])
    return {
        "ops_allowed": cap["ops_allowed"][:5],
        "cross_concerns": cap["cross_concerns"][:3],
        "hint": f'detail : obsidia capabilities "{raw}"',
    }


def build_active_plan(raw: str, registry: dict) -> dict:
    """Construit le panneau a partir du pipeline REEL (pas de texte decoratif).
    Ne lance rien : la sortie est PREVUE, l'execution reste `obsidia \"<IN>\"`."""
    normalized = normalize(raw)
    layer, confidence, reasons = score_layers(normalized, registry)
    spec = registry.get("layers", {}).get(layer, {})
    denied = policy_check(normalized, registry)
    file_signals = collect_file_signals()

    if denied:
        predicted = "POLICY_DENY"
    elif layer == "unknown":
        predicted = "STOP_UNKNOWN"
    elif layer == "sigma" or layer == "live" or "doctor" in normalized:
        predicted = "EXECUTE"
    else:
        predicted = "COMMANDS"
    predicted = assert_output_allowed(predicted)

    guid = derive_guidance(layer, predicted, file_signals)
    tooling = PLAN_TOOLING.get(layer, PLAN_TOOLING["unknown"])
    organes = PLAN_ORGANES.get(layer, PLAN_ORGANES["unknown"])

    cut_at = 5 if denied else (4 if layer == "unknown" else None)

    def step(n: int, text: str) -> str:
        if cut_at is not None and n > cut_at and n not in (11, 12):
            return f"{n:2}. (non atteinte — coupee a l'etape {cut_at})"
        return f"{n:2}. {text}"

    trig_txt = ", ".join(r.split("'")[1] for r in reasons) if reasons else "aucun"
    roadmap = [
        step(1, f'Reception IN brut: "{raw}"'),
        step(2, f'Normalisation: "{normalized}"'),
        step(3, f"Triggers detectes: {trig_txt}"),
        step(4, f"Couche: {layer} (confiance {confidence})"
                + (" — AUCUNE couche reconnue" if layer == "unknown" else "")),
        step(5, "Policy check: "
                + (f"mot interdit \"{denied}\" -> POLICY_DENY (roadmap coupee ici)"
                   if denied else "aucun mot interdit")),
        step(6, f"Sortie choisie: {predicted}"),
        step(7, "Capacites: " + "; ".join(o.split(":")[0] for o in organes["mobilises"][:4])
                + " | outils: " + "; ".join(t.split(" [")[0] for t in tooling["utilises"][:3]) + ", ..."),
        step(8, "Corpus: " + "; ".join(tooling["corpus"][:3])),
        step(9, "Exclus: " + "; ".join(t.split(" [")[0] for t in tooling["exclus"][:3])),
        step(10, "Gates: jamais lances par le terminal — voir bloc GATES"),
        f"11. Reponse prevue: {predicted}"
        + (" (refus policy + rappel workflow gated)" if denied else ""),
        "12. Prochaine action humaine: voir bloc dedie",
    ]

    if denied:
        status, nxt = "POLICY_CUT", ("workflow gated humain "
                                     "(docs/protocols/OBSIDURE_APPLY_PROTOCOL.md) "
                                     "si la mutation est reellement voulue")
    elif layer == "unknown":
        status, nxt = "NEEDS_SCOPE_CONFIRMATION", ("reformuler l'IN en nommant une couche "
                                                   "(brody, obsidure, obsidienne, kernel, "
                                                   "domains, audit, memory, live, sigma)")
    elif predicted == "EXECUTE":
        status, nxt = "ROUTED", f'aucune — lancer obsidia "{raw}" pour executer la lecture'
    else:
        cmds = spec.get("commands", []) or []
        status, nxt = "WAITING_FOR_HUMAN", (cmds[0] + " (a ta main)" if cmds else "aucune commande connue")
    assert status in PLAN_STATUSES

    blockers = ["etat git non verifie par le terminal (zero subprocess) — "
                "verifier toi-meme: git status --short ; git diff --cached --name-only"]
    pk = file_signals.get("proofkit", {})
    if not pk.get("readable"):
        blockers.append("PROOFKIT_REPORT.json illisible — REQUEST_PROOF probable")
    elif pk.get("age_status") == "STALE":
        blockers.append(f"proofkit PASS mais perime ({pk.get('age_days')}j) — "
                        "python proofs/verify_all.py (humain)")

    return {
        "panel": "OBSIDIA_ACTIVE_PLAN",
        "raw": raw, "normalized": normalized,
        "detected_layer": layer, "confidence": confidence,
        "route_reason": reasons or ["aucun trigger reconnu"],
        "deny_keyword": denied,
        "roadmap": roadmap,
        "organes_mobilises": organes["mobilises"],
        "organes_mobilisables": organes["mobilisables"],
        "organes_interdits": dedupe_preserve_order(
            list(organes.get("interdits", [])) + list(ORGANES_INTERDITS_TOUJOURS)),
        "outils_utilises": tooling["utilises"],
        "outils_mobilisables": tooling["mobilisables"],
        "outils_exclus": dedupe_preserve_order(
            list(tooling["exclus"]) + list(FORBIDDEN_ALWAYS)),
        "corpus": tooling["corpus"],
        "scope": ["lecture seule pour cet IN — le terminal ne modifie aucun fichier",
                  "interdits permanents: apps/ sigma/ kernel/ proofs/ runtime/ manifests seals"],
        "gates": list(GATES_KNOWN),
        "blockers": blockers,
        "output_predicted": predicted,
        "guidance": guid["guidance"],
        "guidance_reasons": guid["guidance_reasons"],
        "guidance_authority": "NONE",
        "next_human_action": nxt,
        "plan_status": status,
        "capability_summary": _build_capability_summary(layer, raw),
    }


def _fmt_list(items: list, indent: str = "  - ") -> str:
    return "\n".join(indent + str(i) for i in items) if items else indent + "aucun"


def format_active_plan(plan: dict) -> str:
    lines = [
        "================ OBSIDIA_ACTIVE_PLAN ================",
        "", "INPUT:", f"  {plan['raw']}",
        "", "ROADMAP DE TRAITEMENT:", *("  " + s for s in plan["roadmap"]),
        "", "COUCHE DETECTEE:", f"  {plan['detected_layer']} (confiance {plan['confidence']})",
        "", "ROUTAGE:", _fmt_list(plan["route_reason"]),
    ]
    if plan.get("deny_keyword"):
        lines.append(f"  - policy: mot interdit \"{plan['deny_keyword']}\" -> POLICY_DENY")
    lines += [
        "", "CAPACITES / ORGANES MOBILISES:", _fmt_list(plan["organes_mobilises"]),
        "", "CAPACITES / ORGANES MOBILISABLES:", _fmt_list(plan["organes_mobilisables"]),
        "", "CAPACITES / ORGANES INTERDITS / NON UTILISES:", _fmt_list(plan["organes_interdits"]),
        "", "OUTILS TECHNIQUES MOBILISES:", _fmt_list(plan["outils_utilises"]),
        "", "OUTILS TECHNIQUES MOBILISABLES:", _fmt_list(plan["outils_mobilisables"]),
        "", "OUTILS TECHNIQUES INTERDITS / NON UTILISES:", _fmt_list(plan["outils_exclus"]),
        "", "CORPUS PERTINENT:", _fmt_list(plan["corpus"]),
        "", "CAPABILITY SUMMARY:",
        "  ops autorisees : " + " · ".join(plan["capability_summary"]["ops_allowed"]) if plan["capability_summary"]["ops_allowed"] else "  ops autorisees : aucune",
        "  cross-concerns : " + (" · ".join(plan["capability_summary"]["cross_concerns"]) if plan["capability_summary"]["cross_concerns"] else "aucun") + "  |  " + plan["capability_summary"]["hint"],
        "", "SCOPE:", _fmt_list(plan["scope"]),
        "", "GATES (jamais lances par le terminal):", _fmt_list(plan["gates"]),
        "", "BLOCKERS:", _fmt_list(plan["blockers"]),
        "", "SORTIE TERMINAL PREVUE:", f"  {plan['output_predicted']}",
        "", "GUIDANCE:", f"  {plan['guidance']} (non souverain — X108 decide)",
        _fmt_list(plan["guidance_reasons"], indent="    raison: "),
        "", "PROCHAINE ACTION HUMAINE:", f"  {plan['next_human_action']}",
        "", "PLAN_STATUS:", f"  {plan['plan_status']}",
        "", "======================================================",
    ]
    return "\n".join(lines)


def format_route_view(plan: dict) -> str:
    lines = [
        "---- OBSIDIA_ACTIVE_PLAN / ROUTE ----",
        f"ROADMAP (resume): IN -> normalize -> {plan['detected_layer']} -> {plan['output_predicted']}",
        f"COUCHE: {plan['detected_layer']} (confiance {plan['confidence']})",
        "ROUTAGE:", _fmt_list(plan["route_reason"]),
    ]
    if plan.get("deny_keyword"):
        lines.append(f"  - policy: mot interdit \"{plan['deny_keyword']}\" -> POLICY_DENY")
    lines += [f"PLAN_STATUS: {plan['plan_status']}"]
    return "\n".join(lines)


def format_tools_view(plan: dict) -> str:
    return "\n".join([
        "---- OBSIDIA_ACTIVE_PLAN / TOOLS ----",
        f"COUCHE: {plan['detected_layer']} | SORTIE PREVUE: {plan['output_predicted']}",
        "ROADMAP outils (etapes 7-9):",
        "  7. CAPACITES/ORGANES MOBILISES:", _fmt_list(plan["organes_mobilises"], "     - "),
        "     CAPACITES/ORGANES MOBILISABLES:", _fmt_list(plan["organes_mobilisables"], "     - "),
        "     OUTILS TECHNIQUES MOBILISES:", _fmt_list(plan["outils_utilises"], "     - "),
        "  8. CORPUS UTILISE / MOBILISABLE:", _fmt_list(plan["corpus"], "     - "),
        "     OUTILS TECHNIQUES MOBILISABLES:", _fmt_list(plan["outils_mobilisables"], "     - "),
        "  9. CAPACITES/ORGANES INTERDITS:", _fmt_list(plan["organes_interdits"], "     - "),
        "     OUTILS/CORPUS EXCLUS:", _fmt_list(plan["outils_exclus"], "     - "),
        f"PLAN_STATUS: {plan['plan_status']}",
    ])


def format_blockers_view(registry: dict) -> str:
    fs = collect_file_signals()
    lines = ["---- OBSIDIA_ACTIVE_PLAN / BLOCKERS ----",
             "Etat git : NON verifie par le terminal (zero subprocess).",
             "A lancer toi-meme :",
             "  git status --short",
             "  git diff --cached --name-only",
             "Signaux fichiers (readonly) :"]
    pk = fs.get("proofkit", {})
    lines.append(f"  proofkit: {pk.get('status', 'ILLISIBLE')} "
                 f"(age {pk.get('age_days', '?')}j, {pk.get('age_status', 'UNKNOWN')})")
    mk = fs.get("merkle_seal", {})
    lines.append(f"  merkle_seal: {mk.get('status', 'ILLISIBLE')} (lecture seule)")
    lines.append("PLAN_STATUS: NO_ACTION_TAKEN (affichage uniquement)")
    return "\n".join(lines)


def format_gates_view() -> str:
    lines = ["---- OBSIDIA_ACTIVE_PLAN / GATES ----",
             "Gates connus (jamais lances par le terminal) :"]
    for g in GATES_KNOWN:
        lines.append(f"  {g}")
    gates_dir = REPO_ROOT / "scripts" / "gates"
    present = sorted(p.name for p in gates_dir.glob("*.py")) if gates_dir.exists() else []
    lines.append("Fichiers gates presents : " + (", ".join(present) if present else "aucun"))
    lines.append("PLAN_STATUS: NO_ACTION_TAKEN (affichage uniquement)")
    return "\n".join(lines)


def handle_plan_command(cmd: str, arg: str, registry: dict,
                        last_plan: dict | None = None) -> tuple[str, dict | None, dict | None]:
    """Retourne (texte, receipt_payload_ou_None, plan_ou_None)."""
    cmd = cmd.lower()
    if cmd in ("plan", "route", "tools"):
        if not arg:
            return ("GUIDE: donne un IN — exemple: obsidia plan \"sigma coherence\"\n"
                    "PLAN_STATUS: NO_ACTION_TAKEN", None, None)
        plan = build_active_plan(arg, registry)
        text = {"plan": format_active_plan,
                "route": format_route_view,
                "tools": format_tools_view}[cmd](plan)
        receipt = {k: plan[k] for k in
                   ("panel", "raw", "detected_layer", "confidence", "route_reason",
                    "roadmap", "organes_mobilises", "organes_mobilisables",
                    "organes_interdits", "output_predicted", "guidance",
                    "guidance_reasons", "guidance_authority",
                    "next_human_action", "plan_status")}
        receipt["view"] = cmd
        return text, receipt, plan
    if cmd == "blockers":
        return format_blockers_view(registry), None, None
    if cmd == "gates":
        return format_gates_view(), None, None
    if cmd in ("scope", "next"):
        if last_plan is None:
            return ("Mode stateless : aucun plan en memoire hors session shell.\n"
                    "Donne un IN : obsidia plan \"<IN>\"\n"
                    "PLAN_STATUS: NO_ACTION_TAKEN", None, None)
        if cmd == "scope":
            return ("SCOPE (dernier IN de la session) :\n" + _fmt_list(last_plan["scope"])
                    + f"\nPLAN_STATUS: {last_plan['plan_status']}", None, last_plan)
        return (f"PROCHAINE ACTION HUMAINE (dernier IN) :\n  {last_plan['next_human_action']}"
                + f"\nPLAN_STATUS: {last_plan['plan_status']}", None, last_plan)
    return "commande panneau inconnue", None, None


# ----------------------------------------------------------------------------
# Shell interactif — boucle autour de handle(). Aucun pouvoir nouveau.
# ----------------------------------------------------------------------------
# ============================================================================
# OBSIDIA_ANSWER_ROUTER — moteur universel de reponse gouverne par droits.
# Tout IN libre passe ici (shell ET one-shot). Le terminal repond dans ses
# droits ; le Plan explique la route ; l'humain applique ; X108 decide.
# Une entree inconnue ne meurt jamais silencieusement.
# ============================================================================
ROUTER_COMMANDS = ("answer", "raw", "json")
ANSWER_MODES = ("ANSWER_LOCAL", "ANSWER_LIVE_READONLY", "ANSWER_COMMANDS_ONLY",
                "ANSWER_PLAN", "ANSWER_UNKNOWN", "ANSWER_POLICY_DENY")
_MODE_TO_OUTPUT = {"ANSWER_LOCAL": "GUIDE", "ANSWER_LIVE_READONLY": "EXECUTE",
                   "ANSWER_COMMANDS_ONLY": "COMMANDS", "ANSWER_PLAN": "GUIDE",
                   "ANSWER_UNKNOWN": "STOP_UNKNOWN", "ANSWER_POLICY_DENY": "POLICY_DENY"}

_KNOWLEDGE_WORDS = ("c'est quoi", "cest quoi", "c est quoi", "qu'est", "quest-ce",
                    "explique", "resume", "definis", "definition", "comment fonctionne",
                    "peux tu", "peut tu", "qui es", "que peux", "quelles sont tes",
                    "que fais tu", "a quoi tu sers", "tu peux", "tu es quoi",
                    "comment tu fonctionne", "tes capacites", "terminal self")
_STATE_WORDS = ("status", "statut", " up", "down", "tourne", "allume", "sante", "health")
_ACTION_WORDS = ("lance", "lancer", "prepare", "demarre", "execute", "run ", "build",
                 "comment lancer")
_META_WORDS = ("roadmap", "quels outils", "quel outil", "outils tu", "plan pour", "route pour")
_BLOCKER_WORDS = ("bloque", "blocage", "blocker", "coince")
_WHY_WORDS = ("pourquoi",)

LOCAL_CORPUS = {
    "sigma": {"keys": ("sigma", "coherence", "contradiction", "freshness",
                       "fresh signal", "hold recommended"),
        "sources": ["docs/specs/OBSIDIA_SIGMA_GUIDANCE_V0.md", "registry.sigma.note"],
        "answer": ("Sigma guide sur la coherence, les contradictions et la fraicheur des "
                   "signaux (proofkit, manifest Lean, merkle en lecture, proposals, stress). "
                   "Sigma est non souverain : il recommande (CONTINUE ... HOLD_RECOMMENDED), "
                   "il ne decide jamais — HOLD_RECOMMENDED n'est pas X108Gate.HOLD. "
                   "decision_authority = KX108_ONLY. Sigma V18.9 est la couche de runtime "
                   "verification completant Lean 4 (correction statique) et TLA+ (modele) "
                   "dans la chaine de preuve.")},
    "obsidure": {"keys": ("obsidure", "forge", "proposal patch", "generatedperipheral",
                          "agent code", "proposition patch", "protocole apply",
                          "peux tu coder", "peut tu coder", "coder"),
        "sources": ["docs/protocols/OBSIDURE_APPLY_PROTOCOL.md", "registry.obsidure.note"],
        "answer": ("Obsidure construit, prouve et corrige via un workflow proposal-first "
                   "gele en v2 : proposal identifie dans _PATCH_PROPOSALS/, checks Lean "
                   "(LEAN_EXIT=0), forbidden tokens, diff, approbation humaine du scope "
                   "exact, puis apply gated. Le terminal ne l'execute jamais : "
                   "commands-only (scripts/run_agent_obsidure.ps1). Obsidure ne decide pas. "
                   "v2 gele : 4 familles generatives, 39 theoremes GeneratedPeripheral, "
                   "surface V2 = 232 entrees.")},
    "freeze_terminal": {"keys": ("freeze",),
        "sources": ["docs/specs/OBSIDIA_TERMINAL_STACK_FREEZE_V1.md"], "loader": "freeze"},
    "plan_panel": {"keys": ("plan panel", "panneau", "active_plan", "active plan"),
        "sources": ["docs/specs/OBSIDIA_TERMINAL_PLAN_PANEL_V1.md"],
        "answer": ("OBSIDIA_ACTIVE_PLAN est le panneau de pilotage : pour tout IN il montre "
                   "la roadmap 12 etapes, le routage, les capacites/organes mobilises, les "
                   "outils techniques, le corpus, les gates (jamais lances) et la prochaine "
                   "action humaine. Stateless, zero subprocess, non souverain.")},
    "gates": {"keys": ("gate", "gates", "garde-fous", "commit_scope_guard"),
        "sources": ["scripts/gates/", "tests/gates/", "docs/protocols/KERNEL_BOUNDARY_CHECK_PROTOCOL.md"],
        "answer": ("3 gates V0 : commit_scope_guard (staging = allow-list exacte), "
                   "kernel_boundary_check (chemins proteges ni dirty ni stages), "
                   "sigma_non_sovereignty_check (sigma_guidance reste KX108_ONLY). "
                   "PASS/FAIL uniquement, jamais lances par le terminal, ne remplacent pas X108.")},
    "doctrine": {"keys": ("doctrine", "souverain", "autorite"),
        "sources": ["docs/protocols/OBSIDIA_OPERATOR_DOCTRINE.md", "CLAUDE.md"],
        "answer": ("X108 tranche (seule autorite d'admissibilite). Sigma guide. Brody "
                   "explique. Obsidure construit. Domains bridge-only. Memory readonly. "
                   "Le terminal affiche/route/guide et n'emet jamais ALLOW/BLOCK/HOLD/ACT.")},
    "brody": {"keys": ("brody", "brody explique quoi", "brody explique", "advisory",
                       "runtime readonly", "couche explication", "cockpit brody"),
        "sources": ["registry.brody.note", "runbook full stack (observation locale)"],
        "answer": ("Brody explique, contextualise et synthetise. Il vit dans l'API 8000 via "
                   "/api/brody/* (pas de serveur separe) : chat V1, enriched, raw inspector. "
                   "Brody est non souverain — il ne decide pas. Statut formel : module "
                   "first-class X108 en advisory-only (docs/brody) — runtime_readonly "
                   "repond, response_contract force les invariants KX108_ONLY, no-decision "
                   "policy explicite. Stack : launchers COMMANDS_ONLY "
                   "(01_START_BRODY_STACK.ps1).")},
    "kernel_x108": {"keys": ("kernel", "x108", "kx108", "kx108_only", "noyau",
                             "le juge", "juge", "qui decide", "autorite de decision"),
        "sources": ["docs/KERNEL_OVERVIEW.md (v1.4.0)", "docs/GLOSSAIRE.md"],
        "answer": ("Le Kernel X-108 est le noyau de gouvernance deterministe d'Obsidia — "
                   "le \"juge\" qui evalue les actions avant execution selon des regles "
                   "mathematiques strictes et auditables. Seule autorite d'admissibilite "
                   "(KX108_ONLY) : ALLOW/HOLD/BLOCK n'existent qu'a son niveau. Le terminal "
                   "le consulte en status readonly, ne le mute jamais.")},
    "answer_router": {"keys": ("answer router", "answer_router", "routeur",
                               "routeur de reponse", "comment tu reponds",
                               "obsidia_response", "compact", "verbose"),
        "sources": ["docs/specs/OBSIDIA_TERMINAL_RESPONSE_ROUTER_V1.md",
                    "docs/specs/OBSIDIA_TERMINAL_UX_COMPACT_V2.md"],
        "answer": ("OBSIDIA_ANSWER_ROUTER est le moteur universel du terminal : tout IN "
                   "libre passe par normalisation -> policy -> plan -> mode de reponse "
                   "(LOCAL/LIVE_READONLY/COMMANDS_ONLY/PLAN/UNKNOWN/POLICY_DENY) -> une "
                   "des 5 sorties non souveraines. Compact par defaut, -v pour le detail, "
                   "raw/json pour l'ancien JSON. Hors corpus = pas d'improvisation.")},
    "oie": {"keys": ("oie", "inference economy", "economie d'inference", "necessite llm",
                     "cout par action", "cout des tokens", "necessity", "adequacy"),
        "sources": ["docs/audits/OBSIDIA_INFERENCE_ECONOMY_AUDIT_V0.md",
                    "docs/protocols/OIE_BENCHMARK_PROTOCOL.md"],
        "answer": ("L'OIE mesure l'economie d'inference : le constat central est "
                   "qu'Obsidia ne reduit pas seulement le prix du token mais la necessite "
                   "meme du token — la metrique principale est le cout par action "
                   "admissible. Benchmarks avec labels obligatoires (MEASURED/ESTIMATED/"
                   "DRY_RUN/USAGE_UNAVAILABLE/INVALID_BASELINE) ; jamais d'economies "
                   "inventees, jamais de delta sans baseline. OIE mesure, ne decide pas.")},
    "audit_merkle": {"keys": ("merkle", "seal", "sceau", "scelle", "rfc3161", "receipt",
                              "sha256", "manifest sha", "chaine d'audit"),
        "sources": ["docs/AUDIT_GUIDE.md (v1.0.0)", "docs/GLOSSAIRE.md"],
        "answer": ("La chaine d'audit Obsidia permet a un auditeur externe de verifier "
                   "artefacts et demonstrations : manifests SHA256, seal Merkle, ancre "
                   "RFC3161, verifiers readonly (verify_all/verify_merkle/verify_decision). "
                   "Rien n'est regenere automatiquement — le terminal lit, l'humain "
                   "regenere explicitement.")},
    "memory": {"keys": ("memoire", "memory", "graphiti", "srl", "frozen status",
                        "readonly memory",
                        "memoire graphiti", "memory graphiti", "memoire readonly"),
        "sources": ["docs/core_import/P66_SRL_READONLY_MEMORY_LAYER.md",
                    "docs/architecture/F70_GRAPHITI_BRODY_MEMORY_DEEP_AUDIT.md"],
        "answer": ("Memory/Graphiti est une couche de projection et contexte "
                   "readonly/frozen (canonisee P66 SRL). Elle peut informer, contextualiser "
                   "ou exposer un etat memoire, mais ne decide pas, n'ecrit pas depuis le "
                   "terminal, et ne devient jamais souveraine. memory_write=false reste "
                   "la regle terminale.")},
    "energy_thermo": {"keys": ("thermo", "friction energie stabilite",
                               "energy_thermo", "energy thermo",
                               "thermo governor", "gouverneur thermo", "thermo_debt",
                               "dette thermo", "thermodynamique", "thermodynamics",
                               "efficacite energetique", "dissipation entropie"),
        "label": "Thermo / ENERGY_THERMO (peripherie non souveraine)",
        "sources": ["periphery/energy_thermo.py",
                    "periphery/agents/energy_thermo_agent.py",
                    "apps/obsidia_api/brody_thermodynamics_signal.py (F3)",
                    "docs/periphery/ENERGY_THERMO_GOVERNOR_V0.md"],
        "answer": ("Thermo designe la famille ENERGY_THERMO : run_energy_thermo mesure "
                   "l'efficacite energetique (pin/pout), la dette thermodynamique "
                   "(thermo_debt = couts energie/compute/attention/recuperation moins "
                   "travail utile) et le mismatch sigma/verite. La sortie est un "
                   "PeripheralSignalPacket avec des risques comme ENERGY_INEFFICIENT, "
                   "THERMO_DEBT_HIGH ou SIGMA_TRUTH_MISMATCH, et des recommandations de "
                   "gate candidates. Ces recommandations ne sont jamais des decisions : "
                   "ENERGY_THERMO_AGENT est non souverain, et KX108 reste l'autorite "
                   "d'admissibilite. Thermo est consomme cote Brody par Thermodynamics "
                   "Signal F3 (dissipation, entropie, stabilite, readonly) et par F19B "
                   "Thermo/Coherence/Time. Thermo est distinct du modele de valeur "
                   "thermodynamique GenCoin. [confiance: HIGH]")},
    "domains": {"keys": ("domaine", "domaines", "domains", "domain", "domain bridge",
                         "bridge only", "adapters",
                         "f60", "bridge-only", "passerelle metier", "bank trading gps"),
        "sources": ["docs/architecture/OBSIDIA_F60_SIGMA_REGISTRY_CANONICAL_DOMAINS.md",
                    "docs/KERNEL_OVERVIEW.md", "scripts/obsidia_registry.yaml"],
        "answer": ("Les domaines Obsidia sont des couches bridge-only vers Bank, Trading, "
                   "Ecom, GPS/Defense/Aviation (surface canonique F60 : KX108_ONLY, "
                   "readonly, advisory_only). Ils traduisent le signal metier vers le "
                   "cadre admissible mais ne decident pas — KX108_ONLY. Les adapters live "
                   "sont POST-only, jamais appeles en GET par le doctor.")},
    "lean_proofs": {"keys": ("lean", "preuves lean", "theoremes", "theorem", "invariants",
                             "proof", "proof surface", "manifest lean"),
        "sources": ["proofs/LEAN_PROOF_SURFACE_MANIFEST.json", "sigma/README.md"],
        "answer": ("Surface Lean V2 officialisee : 232 entrees, 39 theoremes "
                   "GeneratedPeripheral, lean_decides=false, forbidden_ok=true. Lean 4 "
                   "assure la correction statique des invariants dans la chaine de preuve "
                   "(completee par TLA+ et Sigma V18.9). Verification commands-only "
                   "(verify_all.py, lake build gated) — jamais lancee par le terminal.")},
    "glossaire": {"keys": ("glossaire", "definition", "ca veut dire quoi"),
        "sources": ["docs/GLOSSAIRE.md"],
        "answer": ("Le glossaire canonique est docs/GLOSSAIRE.md — definitions des termes "
                   "Obsidia (ex. Dual Obsidia : \"l'IA propose, le Juge dispose\"). "
                   "Le terminal oriente vers le glossaire, il n'improvise pas de "
                   "definitions.")},
    "terminal_self": {"keys": ("qui es tu", "tu es quoi", "qu est ce que tu es",
                               "terminal self", "a quoi tu sers", "que fais tu",
                               "tu es quoi comme outil", "c est quoi le terminal"),
        "sources": ["CLAUDE.md", "scripts/obsidia_registry.yaml", "scripts/obsidia_cli.py"],
        "answer": ("Terminal Obsidia non souverain — point d'entree / routeur IN. "
                   "Il recoit les intentions, les normalise, les route vers la couche "
                   "registree (brody, obsidure, obsidienne, kernel, domains, audit, "
                   "memory, live, sigma, terminal_self) et retourne une reponse bornee. "
                   "Il n'emet jamais ALLOW/BLOCK/HOLD/ACT. "
                   "Il ne lance aucun processus, ne mutate rien, n'ecrit pas en memoire. "
                   "X108 reste la seule autorite d'admissibilite. "
                   "decision_authority = KX108_ONLY. readonly par defaut.")},
    "capabilities": {"keys": ("que peux tu faire", "quelles sont tes capacites",
                               "tes capacites", "capacites du terminal",
                               "peux tu", "peut tu", "tu peux"),
        "sources": ["CLAUDE.md", "scripts/obsidia_registry.yaml"],
        "answer": ("Capacites V0 du terminal : "
                   "(1) Router vers 10 couches : brody, obsidure, obsidienne, kernel, "
                   "domains, audit, memory, live, sigma, terminal_self ; "
                   "(2) Lire des fichiers repo en mode fenetre bornee (txt, md, py, yaml, "
                   "json, docx) — readonly, jamais de dump complet ; "
                   "(3) Afficher les commandes d'une couche (COMMANDS) sans les executer ; "
                   "(4) Interroger le corpus local (topics : sigma, obsidure, brody, "
                   "lean_proofs, gates, doctrine, etc.) ; "
                   "(5) Health-checks HTTP GET readonly (couche live/doctor) ; "
                   "(6) Construire le plan actif 12 etapes (build_active_plan). "
                   "NON CAPABLE : appliquer, committer, deployer, ecrire en memoire, "
                   "decider, emettre ALLOW/HOLD/BLOCK/ACT.")},
    "terminal_function": {"keys": ("comment fonctionne le terminal", "comment tu fonctionne",
                                    "comment fonctionne terminal", "comment il fonctionne",
                                    "comment ca marche", "architecture terminal"),
        "sources": ["scripts/obsidia_cli.py", "scripts/obsidia_registry.yaml"],
        "answer": ("Fonctionnement V0 du terminal : "
                   "1. Normalisation brute (lower, accents) ; "
                   "2. policy_check (deny_keywords word-boundary) — STOP si match ; "
                   "3. detect_layer (triggers registry par couche, word-boundary sur cles courtes) ; "
                   "4. build_active_plan (plan 12 etapes avec organes, outils, corpus, gates) ; "
                   "5. select_answer_mode (LOCAL / LIVE_READONLY / COMMANDS / PLAN / UNKNOWN) ; "
                   "6. Routing : LOCAL_CORPUS lookup | doctor HTTP GET | commandes | plan | "
                   "lecture fichier bornee (V2A/V2B/V3) ; "
                   "7. assert_output_allowed (verification sortie) ; "
                   "8. append_receipt (JSONL local non souverain). "
                   "Aucun subprocess. Aucune ecriture. Aucune URL externe.")},
    "terminal_diagnostic": {"keys": ("probleme actuel terminal", "problemes actuels terminal",
                                      "ameliorer le terminal", "organes disponibles",
                                      "branche", "terminal routing", "terminal capabilities",
                                      "lacunes terminal", "manque terminal"),
        "sources": ["scripts/obsidia_cli.py", "scripts/obsidia_registry.yaml",
                    ".claude/context/CURRENT_FOCUS.md"],
        "answer": ("Diagnostic terminal V0 — lacunes connues (branche feat/path-brody-r02) : "
                   "(1) policy_check corrige (word-boundary via _key_match — fix A2) ; "
                   "(2) terminal_self route ajoutee (fix A3) ; "
                   "(3) LOCAL_CORPUS auto-reflexif — presente (fix A4) ; "
                   "(4) obsidure/coder routing — present (fix A4) ; "
                   "Lacunes restantes : select_answer_mode ne distingue pas terminal_self "
                   "explicitement ; PLAN_ORGANES/PLAN_TOOLING terminal_self en cours ; "
                   "build_unknown_answer minimaliste ; Phase B (Capability Graph V3) non "
                   "demarree. Sources : TERMINAL_ROUTING_FIXES_V1 Phase A1.")},
}


def _freeze_summary():
    path = REPO_ROOT / "docs" / "specs" / "OBSIDIA_TERMINAL_STACK_FREEZE_V1.md"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    sections = [l[3:].strip() for l in text.splitlines() if l.startswith("## ")]
    commits = [l.strip() for l in text.splitlines()
               if re.match(r"^[0-9a-f]{7} ", l.strip())]
    return ("Freeze documentaire (pas un seal, pas un manifest) figeant la ligne "
            "terminale avant Plan Panel. Sections : " + " | ".join(sections)
            + ". Commits references : " + " ; ".join(commits[:8]) + ".")


# Hints de couche pour les sujets corpus sans couche registry.
# AFFICHAGE SEULEMENT : ne change jamais le routage d'action, ne permet
# jamais EXECUTE, ne donne aucun droit.
SUBJECT_LAYER_HINTS = {
    "energy_thermo": "corpus:energy_thermo",
    "answer_router": "corpus:answer_router",
    "oie": "corpus:oie",
    "glossaire": "corpus:glossaire",
    "lean_proofs": "corpus:lean_proofs",
}

_BOUNDARY_RE_CACHE: dict = {}


def _key_match(key: str, normalized: str) -> bool:
    """Matching anti-faux-routage : word-boundary pour les cles courtes
    (gate ne matche pas delegate, oie ne matche pas voie)."""
    k = key.lower()
    if len(k) > 5:
        return k in normalized
    pat = _BOUNDARY_RE_CACHE.get(k)
    if pat is None:
        pat = re.compile(r"(?<![a-z0-9_])" + re.escape(k) + r"(?![a-z0-9_])")
        _BOUNDARY_RE_CACHE[k] = pat
    return pat.search(normalized) is not None


def _corpus_lookup(normalized: str):
    for topic, entry in LOCAL_CORPUS.items():
        if any(_key_match(k, normalized) for k in entry["keys"]):
            return topic, entry
    return None, None


def _contains(normalized: str, words) -> bool:
    return any(w in normalized for w in words)


# ============================================================================
# LOCAL_READ_GUIDE_V1 — classification d'actions locales readonly, GUIDE-ONLY.
# Le terminal ne lit AUCUN fichier utilisateur et n'execute AUCUNE commande :
# il classe l'intention, refuse secrets/mutations, affiche la commande
# PowerShell a lancer soi-meme. Lecture reelle = V2 (design + GO separes).
# ============================================================================
# LARGE_DOC_READ_V2A — lecture reelle bornee de fichiers TEXTE du repo, par
# fenetres/ranges/search/context/list. Streaming pur (jamais read()/readlines/
# read_text sur chemin utilisateur), jamais de full dump, jamais de subprocess,
# jamais Brody POST. Secrets masques par contenu. summarize/explain/compare et
# PDF/DOCX = reportes/refuses (guide). decision_authority = KX108_ONLY.
_LOCAL_READ_EXTS = (".md", ".txt", ".json", ".yaml", ".yml", ".py", ".lean", ".ps1")
_LOCAL_BIN_EXTS = (".pdf", ".doc", ".docx", ".odt", ".bin", ".exe", ".zip",
                   ".png", ".jpg", ".jpeg", ".webp")
_LOCAL_ROOTS = ("docs/", "scripts/", "tests/", "periphery/",
                "apps/obsidia_api/", "proofs/lean/")
_LOCAL_SECRET_TOKENS = (".env", ".pem", ".key", "id_rsa", "credential", "token",
                        "secret", ".local_obsidia", ".git", "node_modules",
                        ".venv", "venv", "__pycache__", "cle ssh", "cles ssh", "ssh")
_LOCAL_DENY_SEGMENTS = (".git", "node_modules", "venv", ".venv", "__pycache__",
                        "_patch_proposals", ".local_obsidia")
_LOCAL_DENY_NAMES = ("manifest_sha256.json", "merkle_seal.json")
_LOCAL_MUTATION_TOKENS = ("modifie", "edite", "renomme", "rename", "deplace",
                          "move ", "ecris dans")
_LOCAL_VERBS = (("compare", "COMPARE_LOCAL_FILES"), ("difference", "COMPARE_LOCAL_FILES"),
                ("ecart", "COMPARE_LOCAL_FILES"),
                ("cherche", "SEARCH_LOCAL_TEXT"), ("recherche", "SEARCH_LOCAL_TEXT"),
                ("trouve", "SEARCH_LOCAL_TEXT"), ("localise", "SEARCH_LOCAL_TEXT"),
                ("resume", "SUMMARIZE_LOCAL_DOC"), ("synthetise", "SUMMARIZE_LOCAL_DOC"),
                ("essentiel", "SUMMARIZE_LOCAL_DOC"),
                ("explique", "EXPLAIN_LOCAL_CODE"), ("detaille", "EXPLAIN_LOCAL_CODE"),
                ("clarifie", "EXPLAIN_LOCAL_CODE"),
                ("liste", "LIST_LOCAL_DIR"),
                ("lis ", "READ_LOCAL_FILE"), ("lire", "READ_LOCAL_FILE"),
                ("ouvre", "READ_LOCAL_FILE"), ("affiche", "READ_LOCAL_FILE"),
                ("regarde", "READ_LOCAL_FILE"), ("montre", "READ_LOCAL_FILE"),
                ("parcours", "READ_LOCAL_FILE"), ("jette un oeil", "READ_LOCAL_FILE"))
# Paraphrases NL de recherche sans verbe explicite ("ou ca parle de X").
_SEARCH_NL_MARKERS = ("parle de", "ou parle", "passage sur", "a quel endroit")
# Intent "suite/prochaine etape" -> ANSWER_PLAN (aucune action).
_NEXT_WORDS = ("quoi faire", "que faire", "dois faire", "la suite", "suite logique",
               "prochaine etape", "prepare la suite", "quelle est la suite")
# Bornes de reponse (jamais full dump).
_WIN_DEFAULT, _WIN_MAX, _LINE_MAX = 120, 400, 300
_SEARCH_MAX, _CTX_LINES, _CTX_MAX = 50, 3, 10
_LIST_MAX = 100
_DOCX_SIZE_CAP = 10 * 1024 * 1024  # 10 Mo — DOCX_ADAPTER_V3
_SECRET_CONTENT_RE = re.compile(
    r"(?i)(api[_-]?key|password|passwd|authorization|bearer"
    r"|begin [a-z ]*private key|ghp_[a-z0-9]|sk-[a-z0-9]|akia[0-9a-z])")
_V2B_DEFERRED = {"SUMMARIZE_LOCAL_DOC": "resume progressif",
                 "EXPLAIN_LOCAL_CODE": "explication de section",
                 "COMPARE_LOCAL_FILES": "comparaison d'extraits"}


def _extract_local_paths(raw: str) -> list:
    paths = []
    for tok in raw.replace('"', " ").replace("'", " ").split():
        t = tok.strip(",;:()")
        if "/" in t or "\\" in t or t.lower().endswith(_LOCAL_READ_EXTS + _LOCAL_BIN_EXTS):
            paths.append(t)
    return paths


def _parse_range(normalized: str):
    m = re.search(r"(\d+)\s*(?:a|à|-|to)\s*(\d+)", normalized)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        if a >= 1 and b >= a:
            return a, b
    return None


def local_path_policy(path_str: str, expect_dir: bool = False):
    """(verdict, relposix, abs_path). verdict ALLOWED / DENIED_* / NOT_FOUND.
    Resolution absolue + confinement repo APRES resolution (tue ../ et
    symlinks sortants). Aucune I/O de contenu ici."""
    raw = path_str.strip().strip('"').strip("'")
    low = raw.lower()
    if any(tok in low for tok in _LOCAL_SECRET_TOKENS):
        return ("DENIED_SECRET", None, None)
    if low.endswith(_LOCAL_BIN_EXTS):
        return ("DENIED_FORMAT", raw, None)
    try:
        p = (REPO_ROOT / raw).resolve()
    except Exception:
        return ("NOT_FOUND", raw, None)
    try:
        rel = p.relative_to(REPO_ROOT.resolve())
    except ValueError:
        return ("DENIED_OUT_OF_REPO", raw, None)
    parts_low = [x.lower() for x in rel.parts]
    if any(seg in parts_low for seg in _LOCAL_DENY_SEGMENTS) or \
            any(x.startswith(("_backup_", "_ephemeral_")) for x in parts_low):
        return ("DENIED_SEGMENT", rel.as_posix(), None)
    if p.name.lower() in _LOCAL_DENY_NAMES:
        return ("DENIED_SENSITIVE", rel.as_posix(), None)
    if not expect_dir and p.suffix.lower() in _LOCAL_BIN_EXTS:
        return ("DENIED_FORMAT", rel.as_posix(), None)
    if not any(rel.as_posix().startswith(r) for r in _LOCAL_ROOTS):
        return ("DENIED_OUT_OF_ROOT", rel.as_posix(), None)
    if not p.exists():
        return ("NOT_FOUND", rel.as_posix(), None)
    if expect_dir:
        return (("ALLOWED", rel.as_posix(), p) if p.is_dir()
                else ("DENIED_NOT_DIR", rel.as_posix(), None))
    if p.is_dir():
        return ("IS_DIR", rel.as_posix(), p)
    if p.suffix.lower() not in _LOCAL_READ_EXTS:
        return ("DENIED_EXTENSION", rel.as_posix(), None)
    return ("ALLOWED", rel.as_posix(), p)


def _is_binary(abs_path) -> bool:
    try:
        with abs_path.open("rb") as fh:
            return b"\x00" in fh.read(8192)
    except OSError:
        return True


def _fmt_line(i: int, line: str, masked_counter: list) -> str:
    line = line.rstrip("\n")
    if _SECRET_CONTENT_RE.search(line):
        masked_counter[0] += 1
        return f"[SECRET_MASQUE ligne {i}]"
    if len(line) > _LINE_MAX:
        line = line[:_LINE_MAX] + " …[tronque]"
    return f"{i:6}: {line}"


def _stream_window(abs_path, start: int, count: int):
    """Lecture streaming d'une fenetre [start, start+count). O(fenetre) memoire."""
    out, masked = [], [0]
    total, truncated = 0, False
    with abs_path.open("r", encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh, 1):
            if i < start:
                continue
            if i >= start + count:
                truncated = True
                break
            out.append(_fmt_line(i, line, masked))
            total += len(out[-1])
            if masked[0] > 3:
                _policy_response = {"density": True, "lines": out, "masked": masked[0],
                        "last": i, "truncated": True}
            if total > 64 * 1024:
                truncated = True
                break
    return {"density": False, "lines": out, "masked": masked[0],
            "last": (start + len(out) - 1) if out else start - 1,
            "truncated": truncated}


def _stream_count_lines(abs_path) -> int:
    n = 0
    with abs_path.open("r", encoding="utf-8", errors="replace") as fh:
        for _ in fh:
            n += 1
    return n


def _stream_search(abs_path, pat: str):
    out, masked = [], [0]
    with abs_path.open("r", encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh, 1):
            if pat in line.lower():
                out.append(_fmt_line(i, line, masked))
                if len(out) >= _SEARCH_MAX:
                    break
    return out, masked[0]


def _stream_context(abs_path, pat: str):
    match_lines = []
    with abs_path.open("r", encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh, 1):
            if pat in line.lower():
                match_lines.append(i)
                if len(match_lines) >= _CTX_MAX:
                    break
    if not match_lines:
        return []
    needed = set()
    for m in match_lines:
        needed.update(j for j in range(m - _CTX_LINES, m + _CTX_LINES + 1) if j >= 1)
    top = max(needed)
    linemap, masked = {}, [0]
    with abs_path.open("r", encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh, 1):
            if i > top:
                break
            if i in needed:
                linemap[i] = _fmt_line(i, line, masked)
    blocks = []
    for m in match_lines:
        blk = [linemap[j] + ("  <<< match" if j == m else "")
               for j in range(m - _CTX_LINES, m + _CTX_LINES + 1) if j in linemap]
        blocks.append("\n".join(blk))
    return blocks


# ---------------------------------------------------------------------------
# DOCX_ADAPTER_V3 — extraction stdlib-only : zipfile + xml.etree.ElementTree.
# Texte brut uniquement. Paragraphes traites comme lignes. Memes bornes V2.
# Aucun subprocess, aucun extractall, aucune dependance externe, zero I/O disque.
# ---------------------------------------------------------------------------
def _extract_docx_lines(abs_path) -> tuple:
    """(erreur_guide|None, lignes|None). stdlib : zipfile + xml.etree.ElementTree."""
    import zipfile  # noqa: PLC0415
    import xml.etree.ElementTree as ET  # noqa: PLC0415
    try:
        if abs_path.stat().st_size > _DOCX_SIZE_CAP:
            return ("DOCX trop volumineux (>10 Mo) — non extrait. "
                    "Convertis en .txt/.md puis relance.", None)
        with zipfile.ZipFile(abs_path, "r") as zf:
            with zf.open("word/document.xml") as f:
                tree = ET.parse(f)
    except zipfile.BadZipFile:
        return ("DOCX illisible (ZIP corrompu). Convertis en .txt/.md puis relance.", None)
    except KeyError:
        return ("DOCX non standard (word/document.xml absent). "
                "Convertis en .txt/.md puis relance.", None)
    except ET.ParseError:
        return ("DOCX XML illisible (ParseError). Convertis en .txt/.md puis relance.", None)
    except OSError as exc:
        return (f"Erreur lecture DOCX ({type(exc).__name__}). "
                "Convertis en .txt/.md puis relance.", None)
    _W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    lines = []
    for para in tree.getroot().iter(f"{{{_W}}}p"):
        text = "".join(t.text or "" for t in para.iter(f"{{{_W}}}t")).strip()
        if text:
            lines.append(text)
    if not lines:
        return ("Aucun texte extractible dans ce DOCX (0 paragraphe). "
                "Convertis en .txt/.md puis relance.", None)
    return (None, lines)


def _docx_window(lines: list, start: int, count: int) -> dict:
    """Fenetre bornee sur liste paragraphes DOCX — meme schema que _stream_window."""
    out, masked = [], [0]
    truncated = False
    for i, line in enumerate(lines, 1):
        if i < start:
            continue
        if i >= start + count:
            truncated = True
            break
        out.append(_fmt_line(i, line, masked))
        if masked[0] > 3:
            return {"density": True, "lines": out, "masked": masked[0],
                    "last": i, "truncated": True}
    return {"density": False, "lines": out, "masked": masked[0],
            "last": (start + len(out) - 1) if out else start - 1,
            "truncated": truncated}


def _try_docx_adapter(pstr: str) -> tuple:
    """Confinement repo + extraction DOCX V3 sans modifier local_path_policy.
    Retourne (erreur|None, lignes|None, rel_posix|None)."""
    raw = pstr.strip().strip('"').strip("'")
    low = raw.lower()
    if any(tok in low for tok in _LOCAL_SECRET_TOKENS):
        return ("Refus : cible sensible (secrets/cles proteges). Aucune lecture.", None, None)
    try:
        p = (REPO_ROOT / raw).resolve()
    except Exception:
        return ("Chemin DOCX invalide.", None, None)
    try:
        rel = p.relative_to(REPO_ROOT.resolve())
    except ValueError:
        return (f"Chemin DOCX hors repo ({raw}). Aucune lecture.", None, None)
    rel_posix = rel.as_posix()
    parts_low = [x.lower() for x in rel.parts]
    if any(seg in parts_low for seg in _LOCAL_DENY_SEGMENTS) or \
            any(x.startswith(("_backup_", "_ephemeral_")) for x in parts_low):
        return (f"Segment interdit dans le chemin DOCX ({rel_posix}). Aucune lecture.", None, None)
    if p.name.lower() in _LOCAL_DENY_NAMES:
        return (f"Fichier sensible ({rel_posix}). Aucune lecture.", None, None)
    if not any(rel_posix.startswith(r) for r in _LOCAL_ROOTS):
        return (f"Chemin DOCX hors racines lisibles ({rel_posix}). Aucune lecture.", None, None)
    if not p.exists() or not p.is_file():
        return (f"Fichier DOCX introuvable : {rel_posix}", None, None)
    err, lines = _extract_docx_lines(p)
    if err:
        return (err, None, None)
    return (None, lines, rel_posix)


def _extract_query(normalized: str, marker: str) -> str:
    if marker in normalized:
        rest = normalized.split(marker, 1)[1].split()
        rest = [w for w in rest if w not in ("le", "la", "les", "un", "une",
                                             "de", "du", "dans", "d'")]
        for w in rest:
            if w not in _LOCAL_ROOTS and "/" not in w and "\\" not in w:
                return w
    return ""


def _deny_response(kind: str, msg: str, limite: str):
    return {"kind": kind, "mode": "ANSWER_POLICY_DENY", "reponse": msg,
            "limites": [limite], "next_h": "aucune"}


def _policy_deny_or_none(verdict: str, rel):
    labels = {
        "DENIED_SECRET": "cible sensible (secrets/cles/chemins proteges) — aucune lecture",
        "DENIED_OUT_OF_REPO": f"chemin hors repo apres resolution ({rel}) — aucune lecture",
        "DENIED_OUT_OF_ROOT": f"chemin hors racines lisibles ({rel}) — aucune lecture",
        "DENIED_SEGMENT": f"segment interdit dans le chemin ({rel}) — aucune lecture",
        "DENIED_SENSITIVE": f"fichier sensible (seal/manifest) ({rel}) — aucune lecture",
        "DENIED_EXTENSION": f"extension non autorisee ({rel}) — aucune lecture",
        "DENIED_NOT_DIR": f"chemin n'est pas un dossier ({rel})",
    }
    if verdict in labels:
        return _deny_response("READ_DENIED", "Refus policy chemin : " + labels[verdict],
                              f"{verdict} [INTERDIT]")
    return None


# ---------------------------------------------------------------------------
# V2B — resume / explication / comparaison EXTRACTIFS sur fenetre bornee.
# Aucune primitive d'I/O nouvelle : reutilise _stream_window (streaming).
# Aucun modele, aucun web, aucun subprocess. Extractif-first strict :
# on n'affirme que ce qui est present dans la fenetre lue.
# ---------------------------------------------------------------------------
_TECH_TOKEN_RE = re.compile(r"[A-Z][A-Z0-9_]{2,}|[a-z_]+_[a-z0-9_]+|[A-Z][a-z]+[A-Z][A-Za-z]+")


def _raw_from_fmt(fl: str) -> str:
    """Extrait le contenu d'une ligne formatee '   N: texte' (ou masquee)."""
    if fl.startswith("[SECRET_MASQUE"):
        return ""
    if ": " in fl:
        return fl.split(": ", 1)[1]
    return fl.strip()


def _extract_keypoints(fmt_lines: list) -> list:
    """Points cles EXTRACTIFS : titres, puces, signatures, sinon 1res phrases."""
    pts, seen = [], set()
    for fl in fmt_lines:
        c = _raw_from_fmt(fl).strip()
        if not c:
            continue
        low = c.lstrip()
        struct = (low.startswith(("#", "-", "*", "•")) or re.match(r"\d+[.)]", low)
                  or low.startswith(("def ", "class ")))
        if struct and c[:160] not in seen:
            seen.add(c[:160])
            pts.append(c[:160])
        if len(pts) >= 12:
            return pts
    if len(pts) < 3:  # fallback : premieres phrases de lignes de prose
        for fl in fmt_lines:
            c = _raw_from_fmt(fl).strip()
            if len(c) > 30 and c[:120] not in seen:
                seen.add(c[:120])
                pts.append(c.split(". ")[0][:120])
            if len(pts) >= 6:
                break
    return pts[:12]


def _partial_banner(last: int, total: int) -> str:
    return ("fenetre PARTIELLE — pas une synthese globale du fichier"
            if last < total else "fenetre couvrant l'integralite du fichier")


def _summarize_window(rel: str, ap, start: int, count: int) -> dict:
    win = _stream_window(ap, start, count)
    total = _stream_count_lines(ap)
    if win["density"]:
        return _deny_response("READ_DENIED_SECRET_DENSITY",
                              f"Resume interrompu : {rel} a une forte densite de secrets.",
                              "DENIED_SECRET_DENSITY [INTERDIT]")
    last = win["last"]
    pts = _extract_keypoints(win["lines"])
    body = "\n".join("  - " + p for p in pts) or "  (rien d'exploitable dans cette fenetre)"
    nav = (f"\nNext :\n  resume les lignes {last + 1} a "
           f"{min(last + _WIN_DEFAULT, total)} de {rel}") if last < total else ""
    return {"kind": "SUMMARIZE_LOCAL_PROGRESSIVE", "mode": "ANSWER_LOCAL",
            "reponse": f"Resume local de {rel} — lignes {start}-{last} sur {total} "
                       f"(fenetre bornee, extractif ; {_partial_banner(last, total)})\n"
                       f"Points cles dans la fenetre lue :\n{body}\n"
                       f"Limites :\n  - resume de la fenetre lue uniquement, "
                       f"pas une synthese globale du fichier{nav}",
            "corpus": [rel], "output_execute": True,
            "meta": {"verdict_policy": "ALLOWED", "type_fichier": ap.suffix,
                     "range_lignes": f"{start}-{last}", "lignes_affichees": len(win["lines"]),
                     "keypoints": len(pts), "secrets_masques": win["masked"],
                     "truncated": win["truncated"]},
            "limites": ["resume extractif de la fenetre lue uniquement"],
            "next_h": "aucune (naviguer via Next si fenetre partielle)"}


def _explain_window(rel: str, ap, start: int, count: int) -> dict:
    win = _stream_window(ap, start, count)
    total = _stream_count_lines(ap)
    if win["density"]:
        return _deny_response("READ_DENIED_SECRET_DENSITY",
                              f"Explication interrompue : {rel} a une forte densite de secrets.",
                              "DENIED_SECRET_DENSITY [INTERDIT]")
    last = win["last"]
    structure, terms = [], []
    for fl in win["lines"]:
        c = _raw_from_fmt(fl).strip()
        low = c.lstrip()
        if low.startswith(("#", "def ", "class ")) and len(structure) < 12:
            structure.append(c[:120])
        for m in _TECH_TOKEN_RE.findall(c):
            if m not in terms and len(terms) < 15:
                terms.append(m)
    struct_body = "\n".join("  - " + s for s in structure) or "  (aucune section visible)"
    term_body = ", ".join(terms) or "(aucun identifiant technique repere)"
    nav = (f"\nNext :\n  explique les lignes {last + 1} a "
           f"{min(last + _WIN_DEFAULT, total)} de {rel}") if last < total else ""
    return {"kind": "EXPLAIN_LOCAL_PROGRESSIVE", "mode": "ANSWER_LOCAL",
            "reponse": f"Explication locale de {rel} — lignes {start}-{last} sur {total} "
                       f"({_partial_banner(last, total)})\n"
                       f"Structure visible :\n{struct_body}\n"
                       f"Termes visibles :\n  {term_body}\n"
                       f"Lecture prudente :\n  dans la fenetre lue, on voit "
                       f"{len(structure)} section(s) et {len(terms)} terme(s) technique(s).\n"
                       f"Limites :\n  - explication de la fenetre lue uniquement{nav}",
            "corpus": [rel], "output_execute": True,
            "meta": {"verdict_policy": "ALLOWED", "type_fichier": ap.suffix,
                     "range_lignes": f"{start}-{last}", "sections": len(structure),
                     "termes": len(terms), "secrets_masques": win["masked"]},
            "limites": ["explication extractive de la fenetre lue uniquement"],
            "next_h": "aucune (naviguer via Next si fenetre partielle)"}


def _compare_windows(rel_a, ap_a, rel_b, ap_b, start: int = 1, count: int = _WIN_DEFAULT) -> dict:
    wa, wb = _stream_window(ap_a, start, count), _stream_window(ap_b, start, count)
    if wa["density"] or wb["density"]:
        return _deny_response("READ_DENIED_SECRET_DENSITY",
                              "Comparaison interrompue : forte densite de secrets.",
                              "DENIED_SECRET_DENSITY [INTERDIT]")
    ta, tb = _stream_count_lines(ap_a), _stream_count_lines(ap_b)
    la = [_raw_from_fmt(x).rstrip() for x in wa["lines"]]
    lb = [_raw_from_fmt(x).rstrip() for x in wb["lines"]]
    common = [x for x in la if x and x in set(lb)][:8]
    diff = list(difflib.unified_diff(la, lb, lineterm="", n=0))[:120]
    diff_body = "\n".join("  " + d for d in diff if d[:3] not in ("---", "+++", "@@ ")) or "  (aucune difference dans les fenetres lues)"
    common_body = "\n".join("  - " + c[:120] for c in common) or "  (aucune ligne commune visible)"
    a_partial = wa["last"] < ta
    b_partial = wb["last"] < tb
    nav = ("\nNext :\n  compare les lignes suivantes de A et B "
           f"(A: {wa['last'] + 1}-…, B: {wb['last'] + 1}-…)" if (a_partial or b_partial) else "")
    return {"kind": "COMPARE_LOCAL_BOUNDED", "mode": "ANSWER_LOCAL",
            "reponse": f"Comparaison locale bornee\n"
                       f"A: {rel_a} lignes {start}-{wa['last']} sur {ta}\n"
                       f"B: {rel_b} lignes {start}-{wb['last']} sur {tb}\n"
                       f"Points communs visibles :\n{common_body}\n"
                       f"Differences visibles (diff borne) :\n{diff_body}\n"
                       f"Limites :\n  - comparaison des fenetres lues uniquement, "
                       f"pas des fichiers entiers{nav}",
            "corpus": [rel_a, rel_b], "output_execute": True,
            "meta": {"verdict_policy": "ALLOWED", "a": f"{start}-{wa['last']}/{ta}",
                     "b": f"{start}-{wb['last']}/{tb}", "diff_lines": len(diff)},
            "limites": ["comparaison extractive des fenetres lues uniquement"],
            "next_h": "aucune (naviguer via Next si fenetres partielles)"}


# ---------------------------------------------------------------------------
# DOCX_ADAPTER_V3 — operations sur paragraphes extraits (meme logique V2B).
# ---------------------------------------------------------------------------
_DOCX_LIMITES_BASE = ["extraction DOCX : texte brut uniquement "
                      "(images/tableaux/headers/footers/objets embarques exclus)"]
_DOCX_BANNER = ("Extraction DOCX : texte brut uniquement "
                "(images/tableaux/headers/footers/objets embarques exclus)")


def _summarize_docx_lines(rel: str, lines: list, start: int, count: int) -> dict:
    total = len(lines)
    win = _docx_window(lines, start, count)
    if win["density"]:
        return _deny_response("READ_DENIED_SECRET_DENSITY",
                              f"Resume interrompu : {rel} forte densite de secrets.",
                              "DENIED_SECRET_DENSITY [INTERDIT]")
    last = win["last"]
    pts = _extract_keypoints(win["lines"])
    body = "\n".join("  - " + p for p in pts) or "  (rien d'exploitable dans cette fenetre)"
    nav = (f"\nNext :\n  resume les paragraphes {last + 1} a "
           f"{min(last + _WIN_DEFAULT, total)} de {rel}") if last < total else ""
    return {"kind": "SUMMARIZE_LOCAL_PROGRESSIVE", "mode": "ANSWER_LOCAL",
            "reponse": (f"Resume local de {rel} — paragraphes {start}-{last} sur {total} "
                        f"(fenetre bornee, extractif ; {_partial_banner(last, total)})\n"
                        f"{_DOCX_BANNER}\n"
                        f"Points cles dans la fenetre lue :\n{body}\n"
                        f"Limites :\n  - images/tableaux/headers/footers/objets embarques exclus\n"
                        f"  - resume de la fenetre lue uniquement{nav}"),
            "corpus": [rel], "output_execute": True,
            "meta": {"verdict_policy": "ALLOWED", "type_fichier": ".docx",
                     "format": "docx_extracted_text_only",
                     "range_lignes": f"{start}-{last}", "lignes_affichees": len(win["lines"]),
                     "keypoints": len(pts), "secrets_masques": win["masked"],
                     "truncated": win["truncated"]},
            "limites": _DOCX_LIMITES_BASE + ["resume extractif de la fenetre lue uniquement"],
            "next_h": "aucune (naviguer via Next si fenetre partielle)"}


def _explain_docx_lines(rel: str, lines: list, start: int, count: int) -> dict:
    total = len(lines)
    win = _docx_window(lines, start, count)
    if win["density"]:
        return _deny_response("READ_DENIED_SECRET_DENSITY",
                              f"Explication interrompue : {rel} forte densite de secrets.",
                              "DENIED_SECRET_DENSITY [INTERDIT]")
    last = win["last"]
    structure, terms = [], []
    for fl in win["lines"]:
        c = _raw_from_fmt(fl).strip()
        low_c = c.lstrip()
        if low_c.startswith(("#", "def ", "class ")) and len(structure) < 12:
            structure.append(c[:120])
        for m in _TECH_TOKEN_RE.findall(c):
            if m not in terms and len(terms) < 15:
                terms.append(m)
    struct_body = "\n".join("  - " + s for s in structure) or "  (aucune section visible)"
    term_body = ", ".join(terms) or "(aucun identifiant technique repere)"
    nav = (f"\nNext :\n  explique les paragraphes {last + 1} a "
           f"{min(last + _WIN_DEFAULT, total)} de {rel}") if last < total else ""
    return {"kind": "EXPLAIN_LOCAL_PROGRESSIVE", "mode": "ANSWER_LOCAL",
            "reponse": (f"Explication locale de {rel} — paragraphes {start}-{last} sur {total} "
                        f"({_partial_banner(last, total)})\n"
                        f"{_DOCX_BANNER}\n"
                        f"Structure visible :\n{struct_body}\n"
                        f"Termes visibles :\n  {term_body}\n"
                        f"Lecture prudente :\n  dans la fenetre lue, on voit "
                        f"{len(structure)} section(s) et {len(terms)} terme(s) technique(s).\n"
                        f"Limites :\n  - images/tableaux/headers/footers/objets embarques exclus\n"
                        f"  - explication de la fenetre lue uniquement{nav}"),
            "corpus": [rel], "output_execute": True,
            "meta": {"verdict_policy": "ALLOWED", "type_fichier": ".docx",
                     "format": "docx_extracted_text_only",
                     "range_lignes": f"{start}-{last}", "sections": len(structure),
                     "termes": len(terms), "secrets_masques": win["masked"]},
            "limites": _DOCX_LIMITES_BASE + ["explication extractive de la fenetre lue uniquement"],
            "next_h": "aucune (naviguer via Next si fenetre partielle)"}


def _compare_docx_lines(rel_a: str, lines_a: list, rel_b: str, lines_b: list,
                        start: int = 1, count: int = _WIN_DEFAULT) -> dict:
    wa = _docx_window(lines_a, start, count)
    wb = _docx_window(lines_b, start, count)
    if wa["density"] or wb["density"]:
        return _deny_response("READ_DENIED_SECRET_DENSITY",
                              "Comparaison interrompue : forte densite de secrets.",
                              "DENIED_SECRET_DENSITY [INTERDIT]")
    ta, tb = len(lines_a), len(lines_b)
    la = [_raw_from_fmt(x).rstrip() for x in wa["lines"]]
    lb = [_raw_from_fmt(x).rstrip() for x in wb["lines"]]
    common = [x for x in la if x and x in set(lb)][:8]
    diff = list(difflib.unified_diff(la, lb, lineterm="", n=0))[:120]
    diff_body = ("\n".join("  " + d for d in diff if d[:3] not in ("---", "+++", "@@ "))
                 or "  (aucune difference dans les fenetres lues)")
    common_body = "\n".join("  - " + c[:120] for c in common) or "  (aucune ligne commune visible)"
    a_partial, b_partial = wa["last"] < ta, wb["last"] < tb
    nav = ("\nNext :\n  compare les paragraphes suivants "
           f"(A: {wa['last'] + 1}-…, B: {wb['last'] + 1}-…)") if (a_partial or b_partial) else ""
    return {"kind": "COMPARE_LOCAL_BOUNDED", "mode": "ANSWER_LOCAL",
            "reponse": (f"Comparaison locale bornee\n"
                        f"A: {rel_a} paragraphes {start}-{wa['last']} sur {ta}\n"
                        f"B: {rel_b} paragraphes {start}-{wb['last']} sur {tb}\n"
                        f"{_DOCX_BANNER}\n"
                        f"Points communs visibles :\n{common_body}\n"
                        f"Differences visibles (diff borne) :\n{diff_body}\n"
                        f"Limites :\n  - images/tableaux/objets embarques exclus\n"
                        f"  - comparaison des fenetres lues uniquement{nav}"),
            "corpus": [rel_a, rel_b], "output_execute": True,
            "meta": {"verdict_policy": "ALLOWED", "format": "docx_extracted_text_only",
                     "a": f"{start}-{wa['last']}/{ta}", "b": f"{start}-{wb['last']}/{tb}",
                     "diff_lines": len(diff)},
            "limites": _DOCX_LIMITES_BASE + ["comparaison extractive des fenetres lues uniquement"],
            "next_h": "aucune (naviguer via Next si fenetres partielles)"}


def _read_docx_window(rel: str, lines: list, start: int, count: int, kind: str) -> dict:
    total = len(lines)
    win = _docx_window(lines, start, count)
    if win["density"]:
        return _deny_response("READ_DENIED_SECRET_DENSITY",
                              f"Lecture interrompue : {rel} contient trop de lignes sensibles.",
                              "DENIED_SECRET_DENSITY [INTERDIT]")
    body = "\n".join(win["lines"]) or "(fenetre vide)"
    nav = ""
    if win["last"] < total:
        nav = (f"\nsuite : lis les paragraphes {win['last'] + 1} a "
               f"{min(win['last'] + _WIN_DEFAULT, total)} de {rel}")
    return {"kind": kind, "mode": "ANSWER_LOCAL",
            "reponse": (f"{rel} — {total} paragraphes, fenetre {start}-{win['last']} "
                        f"(masques: {win['masked']})\n"
                        f"{_DOCX_BANNER}\n"
                        f"{body}{nav}"),
            "corpus": [rel], "output_execute": True,
            "meta": {"verdict_policy": "ALLOWED", "type_fichier": ".docx",
                     "format": "docx_extracted_text_only",
                     "range_lignes": f"{start}-{win['last']}",
                     "lignes_affichees": len(win["lines"]),
                     "secrets_masques": win["masked"], "truncated": win["truncated"]},
            "limites": _DOCX_LIMITES_BASE + [
                f"fenetre bornee (defaut {_WIN_DEFAULT}, max {_WIN_MAX} paragraphes)"],
            "next_h": "aucune (naviguer via suite si fenetre partielle)"}


def _search_docx_lines(rel: str, lines: list, query: str) -> dict:
    hits, masked = [], [0]
    for i, line in enumerate(lines, 1):
        if query in line.lower():
            hits.append(_fmt_line(i, line, masked))
            if len(hits) >= _SEARCH_MAX:
                break
    body = "\n".join(hits) if hits else f"Aucune correspondance pour '{query}' dans {rel}."
    return {"kind": "SEARCH_LOCAL_TEXT", "mode": "ANSWER_LOCAL",
            "reponse": (f"Recherche '{query}' dans {rel} "
                        f"({len(hits)} correspondance(s), max {_SEARCH_MAX})\n"
                        f"{_DOCX_BANNER}\n{body}"),
            "corpus": [rel], "output_execute": True,
            "meta": {"verdict_policy": "ALLOWED", "type_fichier": ".docx",
                     "format": "docx_extracted_text_only",
                     "match_count": len(hits), "secrets_masques": masked[0]},
            "limites": _DOCX_LIMITES_BASE + [f"recherche bornee {_SEARCH_MAX} correspondances"],
            "next_h": "aucune"}


def _context_docx_lines(rel: str, lines: list, query: str) -> dict:
    match_idxs = [i for i, ln in enumerate(lines, 1) if query in ln.lower()][:_CTX_MAX]
    if not match_idxs:
        return {"kind": "SEARCH_LOCAL_CONTEXT", "mode": "ANSWER_LOCAL",
                "reponse": (f"Aucun contexte pour '{query}' dans {rel}.\n{_DOCX_BANNER}"),
                "corpus": [rel], "output_execute": True,
                "meta": {"verdict_policy": "ALLOWED", "type_fichier": ".docx",
                         "format": "docx_extracted_text_only", "match_count": 0},
                "limites": _DOCX_LIMITES_BASE,
                "next_h": "aucune"}
    masked = [0]
    blocks = []
    for m in match_idxs:
        blk = []
        for j in range(max(1, m - _CTX_LINES), min(len(lines), m + _CTX_LINES) + 1):
            fmt = _fmt_line(j, lines[j - 1], masked)
            blk.append(fmt + ("  <<< match" if j == m else ""))
        blocks.append("\n".join(blk))
    body = "\n---\n".join(blocks)
    return {"kind": "SEARCH_LOCAL_CONTEXT", "mode": "ANSWER_LOCAL",
            "reponse": (f"Contexte de '{query}' dans {rel} "
                        f"(±{_CTX_LINES} paragraphes, max {_CTX_MAX})\n"
                        f"{_DOCX_BANNER}\n{body}"),
            "corpus": [rel], "output_execute": True,
            "meta": {"verdict_policy": "ALLOWED", "type_fichier": ".docx",
                     "format": "docx_extracted_text_only",
                     "match_count": len(match_idxs)},
            "limites": _DOCX_LIMITES_BASE + [
                f"contexte borne ±{_CTX_LINES} paragraphes, {_CTX_MAX} max"],
            "next_h": "aucune"}


# ─── LOCAL READ SECRET DENSITY GUARD V1 ──────────────────────────────────────
# OBSIDIA_LOCAL_READ_SECRET_DENSITY_GUARD_V1
# Empêche la lecture locale de fichiers trop denses en secrets.

_SECRET_DENSITY_WORDS_V1 = frozenset({
    "password", "passwd", "secret", "token", "api_key", "apikey",
    "private_key", "private-key", "credential", "credentials",
    "bearer", "authorization",
})


def _local_read_secret_density_guard_v1(raw: str, normalized: str) -> dict | None:
    """Deny read si le fichier local contient trop de signaux secrets."""
    n = normalized or normalize(raw)
    if not any(w in n for w in ("lis ", "lire ", "read ", "ouvre ", "affiche ")):
        return None

    candidates = re.findall(r"[\w./\\-]+\.(?:md|txt|json|yaml|yml|py|ps1|env|cfg|ini)", raw)
    if not candidates:
        candidates = re.findall(r"[\w./\\-]+\.(?:md|txt|json|yaml|yml|py|ps1|env|cfg|ini)", n)

    for cand in candidates[:3]:
        rel = cand.strip().strip("'\"")
        if not rel:
            continue
        p = (REPO_ROOT / rel).resolve()
        try:
            root = REPO_ROOT.resolve()
            if root not in p.parents and p != root:
                continue
        except Exception:
            continue
        if not p.exists() or not p.is_file():
            continue
        hits = 0
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as fh:
                for idx, line in enumerate(fh):
                    lowered = line.lower()
                    if any(w in lowered for w in _SECRET_DENSITY_WORDS_V1):
                        hits += 1
                    if hits >= 5:
                        return {
                            "mode": "ANSWER_POLICY_DENY",
                            "reponse": (
                                "Lecture refusee: densite de secrets trop elevee "
                                "dans le fichier local demande."
                            ),
                            "reason": "SECRET_DENSITY_GUARD",
                            "path": rel,
                            "secret_density_hits": hits,
                            "output": assert_output_allowed("POLICY_DENY"),
                            "mutation": "none",
                            "subprocess": "none",
                            "decision_authority": "KX108_ONLY",
                        }
                    if idx >= 4096:
                        break
        except Exception:
            continue
    return None


# ─── FIN LOCAL READ SECRET DENSITY GUARD V1 ──────────────────────────────────


def classify_local_read_intent(raw: str, normalized: str):
    _secret_density_deny = _local_read_secret_density_guard_v1(raw, normalized)
    if _secret_density_deny is not None:
        return _secret_density_deny
    """V2A/V2B : lecture reelle bornee (READ/RANGE/SEARCH/CONTEXT/LIST) et
    resume/explication/comparaison extractifs. Retourne un dict, ou None."""
    is_context = "contexte" in normalized
    verb = None
    for word, kind in _LOCAL_VERBS:
        if word in normalized:
            verb = kind
            break
    if is_context:
        verb = "SEARCH_LOCAL_CONTEXT"
    # Paraphrase NL de recherche sans verbe explicite ("ou ca parle de X dans <f>").
    if verb is None and any(mk in normalized for mk in _SEARCH_NL_MARKERS):
        verb = "SEARCH_LOCAL_TEXT"
    paths = _extract_local_paths(raw)
    file_ctx_words = any(w in normalized for w in
                         ("fichier", "dossier", "repertoire", "ce doc"))
    file_ctx = bool(paths) or file_ctx_words
    if verb is None and not file_ctx:
        return None
    # 1. Secrets par mots (avant toute I/O) : refus sec.
    if (verb is not None or file_ctx) and \
            any(tok in normalized for tok in _LOCAL_SECRET_TOKENS):
        return _deny_response("READ_SECRET",
                              "Refus : cible sensible (secrets/cles/chemins proteges). "
                              "Aucune lecture, aucune commande alternative.",
                              "READ_SECRETS [INTERDIT]")
    # 2. Mutations locales.
    if file_ctx and any(tok in normalized for tok in _LOCAL_MUTATION_TOKENS):
        return _deny_response("LOCAL_MUTATION",
                              "Refus : mutation locale demandee. Le terminal est "
                              "readonly, sans chemin d'application.",
                              "WRITE/DELETE/MOVE/RENAME [INTERDIT]")
    if verb is None:
        return None
    # 3. Brody + lecture : POST-only, hors droits terminal (jamais appele).
    if "brody" in normalized and "explique quoi" not in normalized:
        return {"kind": verb, "mode": "ANSWER_PLAN",
                "reponse": "Brody est joignable uniquement en POST (/api/brody/chat), "
                           "hors droits du terminal (EXECUTE = GET readonly). Le "
                           "terminal peut lire le fichier lui-meme (lis <chemin>) et "
                           "te le montrer, mais n'appelle jamais Brody.",
                "corpus": ["registry.brody.note (POST-only)"],
                "limites": ["appel Brody POST [INTERDIT]"],
                "next_h": 'lire via: lis "<chemin>"'}
    # 4. Lecture conceptuelle sans contexte fichier -> corpus normal.
    if verb in ("SUMMARIZE_LOCAL_DOC", "EXPLAIN_LOCAL_CODE", "READ_LOCAL_FILE") \
            and not paths and not file_ctx_words:
        return None
    # 5. Capacites reportees V2B -> GUIDE (pas de lecture reelle en V2A).
    # 5. V2B — resume / explication / comparaison EXTRACTIFS bornes.
    def _v2b_file_guard(pstr):
        """Retourne (dict_refus_ou_None, rel, ap) pour un chemin V2B."""
        verdict, rel, ap = local_path_policy(pstr)
        if verdict == "DENIED_FORMAT":
            return ({"kind": "PDF_NOT_SUPPORTED", "mode": "ANSWER_PLAN",
                     "reponse": f"Format non lu ({rel}) : PDF non pris en charge "
                                "(stdlib insuffisante ; adapter PDF = scope V3b separe). "
                                "Convertis en .txt/.md puis relance.",
                     "limites": ["PDF/binaire non lus"],
                     "next_h": "convertir en .txt/.md puis relancer"}, None, None)
        deny = _policy_deny_or_none(verdict, rel)
        if deny:
            return (deny, None, None)
        if verdict in ("NOT_FOUND", "IS_DIR"):
            return ({"kind": "READ_TARGET", "mode": "ANSWER_UNKNOWN",
                     "reponse": f"Cible invalide : {rel} ({verdict}).",
                     "limites": [], "next_h": "donner un chemin de fichier texte valide"}, None, None)
        if _is_binary(ap):
            return ({"kind": "READ_TARGET", "mode": "ANSWER_PLAN",
                     "reponse": f"Contenu binaire detecte ({rel}) — non lu comme texte.",
                     "limites": ["binaire non lu"], "next_h": "fournir un fichier texte"}, None, None)
        return (None, rel, ap)

    if verb == "COMPARE_LOCAL_FILES":
        if len(paths) != 2:
            return {"kind": verb, "mode": "ANSWER_PLAN",
                    "reponse": "Comparaison : il me faut EXACTEMENT 2 chemins de fichiers "
                               "(ex. compare docs/A.md et docs/B.md).",
                    "limites": ["compare = 2 fichiers exactement"],
                    "next_h": "redonner l'IN avec deux chemins"}
        _a_docx = paths[0].lower().endswith(".docx")
        _b_docx = paths[1].lower().endswith(".docx")
        if _a_docx or _b_docx:
            if not (_a_docx and _b_docx):
                return {"kind": verb, "mode": "ANSWER_PLAN",
                        "reponse": "Comparaison mixte DOCX/texte non supportee en V3 — "
                                   "convertis le DOCX en .txt/.md puis relance.",
                        "limites": ["comparaison DOCX/texte non supportee en V3"],
                        "next_h": "convertir le DOCX en .txt/.md puis relancer"}
            err_a, lines_a, rel_a = _try_docx_adapter(paths[0])
            if err_a:
                return {"kind": "DOCX_ADAPTER_ERROR", "mode": "ANSWER_PLAN",
                        "reponse": err_a, "limites": ["DOCX A non lu"],
                        "next_h": "convertir en .txt/.md puis relancer"}
            err_b, lines_b, rel_b = _try_docx_adapter(paths[1])
            if err_b:
                return {"kind": "DOCX_ADAPTER_ERROR", "mode": "ANSWER_PLAN",
                        "reponse": err_b, "limites": ["DOCX B non lu"],
                        "next_h": "convertir en .txt/.md puis relancer"}
            rng = _parse_range(normalized)
            start, count = ((rng[0], min(rng[1] - rng[0] + 1, _WIN_MAX)) if rng
                            else (1, _WIN_DEFAULT))
            return _compare_docx_lines(rel_a, lines_a, rel_b, lines_b, start, count)
        ga, ra, apa = _v2b_file_guard(paths[0])
        if ga:
            return ga
        gb, rb, apb = _v2b_file_guard(paths[1])
        if gb:
            return gb
        return _compare_windows(ra, apa, rb, apb)

    if verb in ("SUMMARIZE_LOCAL_DOC", "EXPLAIN_LOCAL_CODE"):
        if not paths:
            return {"kind": verb, "mode": "ANSWER_UNKNOWN",
                    "reponse": "Quel fichier ? Donne un chemin precis "
                               "(ex. resume docs/specs/OBSIDIA_LOCAL_CORPUS_V2.md).",
                    "limites": [], "next_h": "redonner l'IN avec le chemin exact"}
        if paths[0].lower().endswith(".docx"):
            err, lines, rel = _try_docx_adapter(paths[0])
            if err:
                return {"kind": "DOCX_ADAPTER_ERROR", "mode": "ANSWER_PLAN",
                        "reponse": err, "limites": ["DOCX non lu"],
                        "next_h": "convertir en .txt/.md puis relancer"}
            rng = _parse_range(normalized)
            start, count = ((rng[0], min(rng[1] - rng[0] + 1, _WIN_MAX)) if rng
                            else (1, _WIN_DEFAULT))
            return (_summarize_docx_lines(rel, lines, start, count)
                    if verb == "SUMMARIZE_LOCAL_DOC"
                    else _explain_docx_lines(rel, lines, start, count))
        guard, rel, ap = _v2b_file_guard(paths[0])
        if guard:
            return guard
        rng = _parse_range(normalized)
        start, count = ((rng[0], min(rng[1] - rng[0] + 1, _WIN_MAX)) if rng
                        else (1, _WIN_DEFAULT))
        if verb == "SUMMARIZE_LOCAL_DOC":
            return _summarize_window(rel, ap, start, count)
        return _explain_window(rel, ap, start, count)
    # 6. LIST_LOCAL_DIR : lecture reelle bornee du dossier.
    if verb == "LIST_LOCAL_DIR":
        if not paths:
            return {"kind": verb, "mode": "ANSWER_UNKNOWN",
                    "reponse": "Quel dossier ? (ex. regarde docs/specs).",
                    "limites": [], "next_h": "redonner l'IN avec un chemin de dossier"}
        verdict, rel, ap = local_path_policy(paths[0], expect_dir=True)
        deny = _policy_deny_or_none(verdict, rel)
        if deny:
            return deny
        if verdict == "NOT_FOUND":
            return {"kind": verb, "mode": "ANSWER_UNKNOWN",
                    "reponse": f"Dossier introuvable : {rel}",
                    "limites": [], "next_h": "verifier le chemin"}
        names = []
        for i, child in enumerate(sorted(ap.iterdir(), key=lambda c: c.name)):
            if i >= _LIST_MAX:
                names.append(f"… (>{_LIST_MAX} entrees, tronque)")
                break
            names.append(child.name + ("/" if child.is_dir() else ""))
        return {"kind": verb, "mode": "ANSWER_LOCAL",
                "reponse": f"Contenu de {rel} ({len(names)} entrees affichees, non recursif) :\n"
                           + "\n".join("  " + n for n in names),
                "corpus": [rel], "output_execute": True,
                "meta": {"verdict_policy": verdict, "type_fichier": "dir"},
                "limites": ["listing borne 100 entrees, non recursif"],
                "next_h": "aucune"}
    # 7. SEARCH / CONTEXT / READ / RANGE : lecture reelle bornee du fichier.
    if not paths:
        return {"kind": verb, "mode": "ANSWER_UNKNOWN",
                "reponse": "Quel fichier ? Donne un chemin precis du repo "
                           "(ex. docs/specs/OBSIDIA_LOCAL_CORPUS_V2.md).",
                "limites": [], "next_h": "redonner l'IN avec le chemin exact"}
    # V3 DOCX adapter — READ/RANGE/SEARCH/CONTEXT
    if paths[0].lower().endswith(".docx"):
        err, lines, rel = _try_docx_adapter(paths[0])
        if err:
            return {"kind": "DOCX_ADAPTER_ERROR", "mode": "ANSWER_PLAN",
                    "reponse": err, "limites": ["DOCX non lu"],
                    "next_h": "convertir en .txt/.md puis relancer"}
        if verb == "SEARCH_LOCAL_CONTEXT":
            query = (_extract_query(normalized, "autour de")
                     or _extract_query(normalized, "contexte"))
            if not query:
                return {"kind": verb, "mode": "ANSWER_UNKNOWN",
                        "reponse": "Quel terme ? "
                                   "(ex. montre le contexte autour de thermo dans <chemin>)",
                        "limites": [], "next_h": "preciser le terme"}
            return _context_docx_lines(rel, lines, query.lower())
        if verb == "SEARCH_LOCAL_TEXT":
            query = ""
            for mk in ("parle de", "cherche", "recherche", "trouve", "localise",
                       "passage sur", "a quel endroit"):
                query = _extract_query(normalized, mk)
                if query:
                    break
            if not query:
                return {"kind": verb, "mode": "ANSWER_UNKNOWN",
                        "reponse": "Quel terme ? (ex. cherche thermo dans <chemin>)",
                        "limites": [], "next_h": "preciser le terme"}
            return _search_docx_lines(rel, lines, query.lower())
        rng = _parse_range(normalized)
        if rng:
            start, count, kind = rng[0], min(rng[1] - rng[0] + 1, _WIN_MAX), "READ_LOCAL_RANGE"
        else:
            start, count, kind = 1, _WIN_DEFAULT, "READ_LOCAL_WINDOW"
        return _read_docx_window(rel, lines, start, count, kind)
    verdict, rel, ap = local_path_policy(paths[0])
    if verdict == "DENIED_FORMAT":
        return {"kind": verb, "mode": "ANSWER_PLAN",
                "reponse": f"Format non lu en V2A ({rel}) : PDF non pris en charge "
                           "(stdlib insuffisante ; adapter PDF = scope V3b separe). "
                           "Convertis en .txt/.md puis relance.",
                "limites": ["PDF/binaire non lus en V2A"],
                "next_h": "convertir en .txt/.md puis relancer"}
    deny = _policy_deny_or_none(verdict, rel)
    if deny:
        return deny
    if verdict == "IS_DIR":
        # "regarde/montre <dossier>" -> listing reel borne (au lieu d'un renvoi).
        names = []
        for i, child in enumerate(sorted(ap.iterdir(), key=lambda c: c.name)):
            if i >= _LIST_MAX:
                names.append(f"… (>{_LIST_MAX} entrees, tronque)")
                break
            names.append(child.name + ("/" if child.is_dir() else ""))
        return {"kind": "LIST_LOCAL_DIR", "mode": "ANSWER_LOCAL",
                "reponse": f"Contenu de {rel} ({len(names)} entrees affichees, non recursif) :\n"
                           + "\n".join("  " + n for n in names),
                "corpus": [rel], "output_execute": True,
                "meta": {"verdict_policy": verdict, "type_fichier": "dir"},
                "limites": ["listing borne 100 entrees, non recursif"],
                "next_h": "aucune"}
    if verdict == "NOT_FOUND":
        return {"kind": verb, "mode": "ANSWER_UNKNOWN",
                "reponse": f"Fichier introuvable : {rel}",
                "limites": [], "next_h": "verifier le chemin exact"}
    if _is_binary(ap):
        return {"kind": verb, "mode": "ANSWER_PLAN",
                "reponse": f"Contenu binaire detecte ({rel}) — non lu comme texte.",
                "limites": ["binaire non lu"], "next_h": "fournir un fichier texte"}

    if verb == "SEARCH_LOCAL_CONTEXT":
        query = _extract_query(normalized, "autour de") or _extract_query(normalized, "contexte")
        if not query:
            return {"kind": verb, "mode": "ANSWER_UNKNOWN",
                    "reponse": "Quel terme ? (ex. montre le contexte autour de thermo dans <chemin>)",
                    "limites": [], "next_h": "preciser le terme"}
        blocks = _stream_context(ap, query.lower())
        body = ("\n---\n".join(blocks) if blocks
                else f"Aucun contexte pour '{query}' dans {rel}.")
        return {"kind": verb, "mode": "ANSWER_LOCAL",
                "reponse": f"Contexte de '{query}' dans {rel} "
                           f"(±{_CTX_LINES} lignes, max {_CTX_MAX}) :\n{body}",
                "corpus": [rel], "output_execute": True,
                "meta": {"verdict_policy": verdict, "type_fichier": ap.suffix,
                         "match_count": len(blocks)},
                "limites": [f"contexte borne ±{_CTX_LINES} lignes, {_CTX_MAX} max"],
                "next_h": "aucune"}
    if verb == "SEARCH_LOCAL_TEXT":
        query = ""
        for mk in ("parle de", "cherche", "recherche", "trouve", "localise",
                   "passage sur", "a quel endroit"):
            query = _extract_query(normalized, mk)
            if query:
                break
        if not query:
            return {"kind": verb, "mode": "ANSWER_UNKNOWN",
                    "reponse": "Quel terme ? (ex. cherche thermo dans <chemin>)",
                    "limites": [], "next_h": "preciser le terme"}
        hits, masked = _stream_search(ap, query.lower())
        body = ("\n".join(hits) if hits
                else f"Aucune correspondance pour '{query}' dans {rel}.")
        return {"kind": verb, "mode": "ANSWER_LOCAL",
                "reponse": f"Recherche '{query}' dans {rel} "
                           f"({len(hits)} correspondance(s), max {_SEARCH_MAX}) :\n{body}",
                "corpus": [rel], "output_execute": True,
                "meta": {"verdict_policy": verdict, "type_fichier": ap.suffix,
                         "match_count": len(hits), "secrets_masques": masked},
                "limites": [f"recherche bornee {_SEARCH_MAX} correspondances"],
                "next_h": "aucune"}
    # READ_LOCAL_FILE / READ_LOCAL_RANGE
    rng = _parse_range(normalized)
    if rng:
        start, count = rng[0], min(rng[1] - rng[0] + 1, _WIN_MAX)
        kind = "READ_LOCAL_RANGE"
    else:
        start, count, kind = 1, _WIN_DEFAULT, "READ_LOCAL_WINDOW"
    win = _stream_window(ap, start, count)
    total_lines = _stream_count_lines(ap)
    if win["density"]:
        return _deny_response("READ_DENIED_SECRET_DENSITY",
                              f"Lecture interrompue : {rel} contient trop de lignes "
                              "sensibles (densite de secrets).",
                              "DENIED_SECRET_DENSITY [INTERDIT]")
    body = "\n".join(win["lines"]) or "(fenetre vide)"
    nav = ""
    if win["last"] < total_lines:
        nav = (f'\nsuite : lis les lignes {win["last"] + 1} a '
               f'{min(win["last"] + _WIN_DEFAULT, total_lines)} de {rel}')
    return {"kind": kind, "mode": "ANSWER_LOCAL",
            "reponse": f"{rel} — {total_lines} lignes, fenetre {start}-{win['last']} "
                       f"(masques: {win['masked']}) :\n{body}{nav}",
            "corpus": [rel], "output_execute": True,
            "meta": {"verdict_policy": verdict, "type_fichier": ap.suffix,
                     "range_lignes": f"{start}-{win['last']}",
                     "lignes_affichees": len(win["lines"]),
                     "secrets_masques": win["masked"], "truncated": win["truncated"]},
            "limites": [f"fenetre bornee (defaut {_WIN_DEFAULT}, max {_WIN_MAX} lignes), "
                        "streaming — jamais de dump complet"],
            "next_h": "aucune (naviguer via range/suite)"}


def build_local_read_guide_response(local_req: dict) -> dict:
    """Passe-plat documente (les fonctions de lecture retournent deja la reponse)."""
    return local_req


def select_answer_mode(plan: dict, normalized: str, registry: dict) -> str:
    """Regles ordonnees : la policy passe toujours en premier."""
    if plan.get("deny_keyword"):
        return "ANSWER_POLICY_DENY"
    if _contains(normalized, _BLOCKER_WORDS) or _contains(normalized, _META_WORDS) \
            or _contains(normalized, _NEXT_WORDS):
        return "ANSWER_PLAN"
    if plan["detected_layer"] == "terminal_self":
        return "ANSWER_LOCAL"
    if plan["detected_layer"] == "sigma" and _contains(normalized, _WHY_WORDS):
        return "ANSWER_LIVE_READONLY"
    if _contains(normalized, _STATE_WORDS) or "doctor" in normalized:
        return "ANSWER_LIVE_READONLY"
    if _contains(normalized, _KNOWLEDGE_WORDS):
        topic, _ = _corpus_lookup(normalized)
        return "ANSWER_LOCAL" if topic else "ANSWER_UNKNOWN"
    if _contains(normalized, _ACTION_WORDS):
        return "ANSWER_COMMANDS_ONLY"
    if plan["detected_layer"] == "unknown":
        return "ANSWER_UNKNOWN"
    return "ANSWER_PLAN"  # ambigu mais route : plan prudent, jamais d'action


def build_local_corpus_answer(plan: dict, normalized: str):
    topic, entry = _corpus_lookup(normalized)
    if not entry:
        return None, []
    if entry.get("loader") == "freeze":
        txt = _freeze_summary()
        return (txt, entry["sources"]) if txt else (None, [])
    return entry["answer"], entry["sources"]


def build_commands_answer(plan: dict, registry: dict):
    spec = registry.get("layers", {}).get(plan["detected_layer"], {})
    cmds = spec.get("commands", []) or []
    lines = ["Le terminal ne lance rien. Commandes humaines possibles :"]
    lines += [f"  {c}" for c in cmds] if cmds else ["  aucune commande connue pour cette couche"]
    return "\n".join(lines), cmds


def build_unknown_answer(plan: dict, raw: str, reason: str) -> str:
    layers = ("brody, obsidure, obsidienne, kernel, domains, audit, "
              "memory, live, sigma, terminal_self")
    examples = (
        "  - 'qui es tu' → terminal_self\n"
        "  - 'status sigma' → live\n"
        "  - 'explique sigma/contracts.py' → lecture locale\n"
        "  - 'propose un patch obsidure' → obsidure\n"
        "  - 'verifie lean' → obsidienne\n"
        "  - 'plan pour migrer bank' → domains"
    )
    candidates = plan.get("layer_candidates", [])
    hint = ""
    if candidates:
        hint = f"\nCouches proches detectees : {', '.join(candidates)}."
    return (f"Je ne peux pas repondre utilement : {reason}.{hint}\n"
            f"Couches disponibles : {layers}.\n"
            f"Exemples de formulations reconnues :\n{examples}")


# ─── ANSWER_STATUS — Detection de requetes de statut de couche/service ───────

_STATUS_TARGETS: dict[str, str] = {
    "brody": "brody", "obsidure": "obsidure", "sigma": "sigma",
    "memory": "memory", "memoire": "memory", "graphiti": "memory",
    "oie": "oie", "lean": "obsidienne", "preuves": "obsidienne",
    "theoreme": "obsidienne", "domains": "domains", "domain": "domains",
    "bank": "domains", "trading": "domains", "gps": "domains",
    "aviation": "domains", "kernel": "kernel", "x108": "kernel",
    "ragnarok": "kernel", "gates": "gates", "thermo": "thermo",
    "terminal": "terminal_self", "stack": "_all", "tout": "_all",
    "all": "_all", "global": "_all",
}

_STATUS_TRIGGER_WORDS = frozenset({
    "actif", "active", "actifs", "actives",
    "tourne", "fonctionne", "disponible", "accessible",
    "up", "down", "pret", "prete", "prets", "pretes",
    "branche", "branchee", "integre", "integree",
    "connecte", "connectee", "lance", "lancee",
    "operationnel", "operationnelle",
})

_STATUS_QUESTION_PHRASES = (
    "est actif", "est active", "est-il", "est-elle", "sont actifs",
    "est accessible", "est disponible", "est operationnel",
    "est branche", "est integre", "est connecte", "est pret",
    "est up", "est down",
)

_STATUS_GLOBAL_PHRASES = (
    "stack active", "stack est active", "tout est actif", "tout actif",
    "tout tourne", "tout fonctionne", "all active",
)

# Tokens qui NE doivent JAMAIS apparaître dans le panneau gauche (réponse humaine).
# Ces informations vont dans le panneau droit (STATUS/TOOLS/PLAN).
_SURFACE_FILTER_TOKENS = (
    "_PATCH_PROPOSALS", "scripts/gates", "obsidure_cli.py",
    "mode:", "conf:", "confidence", "output:",
    "INTERDIT", "LIMITES", "ETAT", "[OBSIDIA RESPONSE]",
    "CAPABILITY_VIEW", "OPS INTERDITES", "gates_applicable",
    "REPONSE DIRECTE",
)


def detect_status_query(raw: str, normalized: str) -> str | None:
    """Detects a layer status query. Returns target layer name, '_all', or None."""
    raw_lower = raw.lower().strip()
    for phrase in _STATUS_GLOBAL_PHRASES:
        if phrase in raw_lower:
            return "_all"
    words = set(re.findall(r"[a-z0-9]+", normalized))
    is_status = bool(words & _STATUS_TRIGGER_WORDS)
    if not is_status:
        for phrase in _STATUS_QUESTION_PHRASES:
            if phrase in normalized:
                is_status = True
                break
    if not is_status:
        return None
    for kw, layer in _STATUS_TARGETS.items():
        if kw in words:
            return layer
    return "_all"


# ─── OS LANGAGE UNI / UNIFIED INPUT IR V1 ────────────────────────────────────
# OBSIDIA_TERMINAL_OS_LANGAGE_UNI_IR_V1
# Pure local IR. No subprocess, no mutation, no network required.

_IR_CODE_WORDS = frozenset({
    "code", "coder", "patch", "correction", "corrige", "fix", "bug",
    "implemente", "implementation", "proposal", "propose", "fichier",
})
_IR_STATUS_WORDS = frozenset({
    "actif", "active", "status", "etat", "up", "ready", "fonctionne",
    "tourne", "disponible", "branche", "connecte",
})
_IR_PLAN_WORDS = frozenset({
    "suite", "continue", "suivant", "next", "reprendre", "plan",
    "reverse", "inverse", "reconstruire", "clarifie", "clarifier",
})
_IR_AUDIT_WORDS = frozenset({
    "audit", "diagnostic", "coherence", "sigma", "preuves", "preuve",
    "lean", "theoreme", "theoremes", "oie", "benchmark",
})
_IR_DENY_WORDS = frozenset({
    "commit", "push", "apply", "deploy", "delete", "supprime",
    "secret", "token", "password", "key",
})


def detect_unified_ir_query(raw: str, normalized: str | None = None) -> bool:
    """Detect explicit request to show OS Langage Uni / UnifiedInputIR."""
    n = normalized if normalized is not None else normalize(raw)
    phrases = (
        "langage uni", "os langage", "unified ir", "input ir",
        "traduit ma demande", "traduire ma demande",
        "normalise ma demande", "normaliser ma demande",
        "montre ir", "affiche ir",
    )
    return any(p in n for p in phrases)


def _ir_words(normalized: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", normalized))


def _ir_target_from_words(words: set[str], normalized: str) -> str:
    """Resolve target layer for UnifiedInputIR without executing anything."""
    status_target = detect_status_query(normalized, normalized)
    if status_target == "_all":
        return "live"
    if status_target:
        if status_target == "obsidienne":
            return "lean"
        if status_target == "terminal_self":
            return "terminal"
        return status_target

    layer_keywords = (
        ("obsidure", {"obsidure", "code", "coder", "patch", "correction", "proposal"}),
        ("brody", {"brody", "explique", "contexte", "reformule", "synthese"}),
        ("reverse", {"reverse", "inverse", "suite", "continue", "reprendre", "plan"}),
        ("sigma", {"sigma", "coherence", "contradiction"}),
        ("oie", {"oie", "benchmark", "cout", "token"}),
        ("lean", {"lean", "preuve", "preuves", "theoreme", "theoremes"}),
        ("domains", {"domains", "domain", "bank", "banque", "trading", "gps", "aviation"}),
        ("kernel", {"kernel", "x108", "kx108", "ragnarok"}),
        ("terminal", {"terminal", "langage", "uni", "ir"}),
    )
    for layer, kws in layer_keywords:
        if words & kws:
            return layer
    return "unknown"


def normalize_unified_input(raw: str, registry: dict | None = None) -> dict:
    """Build UnifiedInputIR V1 from a free-form user input.

    This is a pure terminal-side translation layer:
    - no subprocess
    - no server launch
    - no mutation
    - no authority decision
    """
    normalized = normalize(raw)
    words = _ir_words(normalized)

    target_layer = _ir_target_from_words(words, normalized)

    is_status = bool(words & _IR_STATUS_WORDS) or detect_status_query(raw, normalized) is not None
    is_code = bool(words & _IR_CODE_WORDS) or target_layer == "obsidure"
    is_plan = bool(words & _IR_PLAN_WORDS) or target_layer == "reverse"
    is_audit = bool(words & _IR_AUDIT_WORDS) or target_layer in {"sigma", "lean", "oie"}
    is_deny = bool(words & _IR_DENY_WORDS)

    if is_deny:
        intent_type = "unknown"
        action_type = "deny"
        risk_level = "high"
    elif is_status:
        intent_type = "status"
        action_type = "status"
        risk_level = "low"
    elif is_code:
        intent_type = "code_request"
        action_type = "commands"
        risk_level = "medium"
    elif is_plan:
        intent_type = "plan"
        action_type = "guide"
        risk_level = "low"
    elif is_audit:
        intent_type = "audit"
        action_type = "read"
        risk_level = "medium"
    elif any(w in words for w in {"explique", "pourquoi", "comment", "quoi", "contexte", "resume"}):
        intent_type = "question"
        action_type = "answer"
        risk_level = "low"
        if target_layer == "unknown":
            target_layer = "brody"
    elif detect_unified_ir_query(raw, normalized):
        intent_type = "question"
        action_type = "answer"
        risk_level = "low"
        target_layer = "terminal"
    else:
        intent_type = "unknown"
        action_type = "guide"
        risk_level = "low"

    needs = {
        "brody": target_layer == "brody" or intent_type == "question",
        "obsidure": target_layer == "obsidure" or intent_type == "code_request",
        "reverse": target_layer == "reverse" or intent_type == "plan" or intent_type == "unknown",
        "x108_gate": action_type in {"commands", "deny"} or risk_level in {"medium", "high"},
        "proof": target_layer in {"lean", "sigma", "oie"} or intent_type == "audit",
    }

    constraints = [
        "terminal_non_souverain",
        "decision_authority=KX108_ONLY",
        "no_auto_apply",
        "no_auto_commit",
        "no_auto_push",
    ]

    missing: list[str] = []
    if intent_type == "code_request" and not any(w in words for w in {"fichier", "scope", "test", "gate"}):
        missing.append("scope_fichier_ou_objectif_precis")
    if intent_type == "unknown":
        missing.append("intention_cible")
    if target_layer == "unknown":
        missing.append("target_layer")

    return {
        "raw": raw,
        "normalized": normalized,
        "intent_type": intent_type,
        "target_layer": target_layer,
        "action_type": action_type,
        "risk_level": risk_level,
        "needs": needs,
        "constraints": constraints,
        "missing": missing,
    }


def format_unified_ir(ir: dict) -> str:
    """Human-readable UnifiedInputIR."""
    needs = ir.get("needs", {})
    active_needs = [k for k, v in needs.items() if v]
    lines = [
        "OS Langage Uni — UnifiedInputIR",
        "",
        f"intent_type : {ir.get('intent_type')}",
        f"target_layer: {ir.get('target_layer')}",
        f"action_type : {ir.get('action_type')}",
        f"risk_level  : {ir.get('risk_level')}",
        "",
        "needs      : " + (", ".join(active_needs) if active_needs else "none"),
    ]
    missing = ir.get("missing") or []
    if missing:
        lines += ["", "missing    : " + ", ".join(str(x) for x in missing)]
    return "\n".join(lines)


def build_unified_ir_response(raw: str, registry: dict) -> dict:
    """Build a response showing the UnifiedInputIR in separated surfaces."""
    ir = normalize_unified_input(raw, registry)
    human = format_unified_ir(ir)
    return {
        "panel": "OBSIDIA_RESPONSE",
        "raw": raw,
        "reponse": human,
        "main_answer": {
            "direct": human,
            "summary": "",
            "next": ["brody explique le contexte", "peux tu coder"],
        },
        "etat_technique": {
            "normalized": ir["normalized"],
            "intent_type": ir["intent_type"],
            "target_layer": ir["target_layer"],
            "action_type": ir["action_type"],
            "risk_level": ir["risk_level"],
        },
        "outils_panel": {
            "brody": "needed" if ir["needs"]["brody"] else "not_needed",
            "obsidure": "needed" if ir["needs"]["obsidure"] else "not_needed",
            "reverse": "needed" if ir["needs"]["reverse"] else "not_needed",
            "proof": "needed" if ir["needs"]["proof"] else "not_needed",
            "x108_gate": "needed" if ir["needs"]["x108_gate"] else "not_needed",
        },
        "proof_panel": {
            "source": "local",
            "ir": "computed",
            "mutation": "none",
        },
        "next_suggestions": ["brody explique le contexte", "peux tu coder"],
        "mode_reponse": "ANSWER_LOCAL",
        "detected_layer": "terminal",
        "confidence": 0.80,
        "organes_mobilises": ["OS Langage Uni", "Terminal", "Registry"],
        "organes_mobilisables": ["Brody", "Obsidure", "Reverse", "X108 Gate"],
        "outils_utilises": ["normalize_unified_input"],
        "corpus_utilise": ["unified_ir:v1"],
        "limites": [
            "IR local heuristique",
            "ne decide pas",
            "X108 reste autorite finale",
        ],
        "action_locale": "UNIFIED_IR_LOCAL",
        "local_read_meta": {"ir": ir},
        "next_human_action": "choisir brody / obsidure / reverse selon l'IR",
        "output": assert_output_allowed("GUIDE"),
        "guidance": [],
        "guidance_authority": "NONE",
        "plan_status": "OK",
    }


# ─── FIN OS LANGAGE UNI / UNIFIED INPUT IR V1 ────────────────────────────────


# ─── TERMINAL REVERSE ROUTER V1 ──────────────────────────────────────────────
# OBSIDIA_TERMINAL_REVERSE_ROUTER_V1
# Reprise locale bornee. Aucun subprocess. Aucune mutation. Aucune autorite.

_REVERSE_ROUTER_WORDS = frozenset({
    "suite", "continue", "continuer", "reprendre", "reprends",
    "next", "suivant", "suivante",
})

_REVERSE_ROUTER_PHRASES = (
    "reprendre le plan",
    "reprends le plan",
    "on continue",
    "on reprend",
    "la suite",
    "suite du plan",
    "continue le plan",
)

_REVERSE_DEFAULT_NEXT = (
    "status",
    "brody explique le contexte",
    "obsidure status",
    "traduit ma demande en langage uni",
)


def detect_reverse_router_query(raw: str, normalized: str | None = None) -> bool:
    """Detecte une demande de reprise locale bornee.

    Important:
    - "suite" seul = reverse router
    - "c'est quoi la suite" = question/plan normal
    - "prepare la suite sans modifier" = plan normal

    Le reverse router doit reprendre un contexte, pas voler les intents NL.
    """
    n = normalized if normalized is not None else normalize(raw)
    if not n:
        return False

    compact = n.strip()
    words = set(re.findall(r"[a-z0-9]+", compact))

    exact_commands = {
        "suite",
        "continue",
        "continuer",
        "reprendre",
        "reprends",
        "next",
        "suivant",
        "suivante",
        "on continue",
        "on reprend",
        "reprendre le plan",
        "reprends le plan",
        "continue le plan",
        "suite du plan",
    }
    if compact in exact_commands:
        return True

    # Formes imperatives courtes uniquement.
    # Evite de capturer les questions naturelles:
    # "c'est quoi la suite", "prepare la suite sans modifier", etc.
    if len(words) <= 3 and words & _REVERSE_ROUTER_WORDS:
        blocked_question_words = {"quoi", "que", "quelle", "comment", "pourquoi", "prepare", "preparer"}
        if not (words & blocked_question_words):
            return True

    return False


def _reverse_receipt_path(registry: dict | None = None) -> Path:
    registry = registry or {}
    rel = registry.get("receipt_path") or ".local_obsidia/receipts/obsidia_terminal_receipts.jsonl"
    return REPO_ROOT / rel


def _reverse_pick_value(obj, keys: tuple[str, ...], depth: int = 0):
    """Cherche une valeur dans un dict JSON sans supposer la forme exacte du receipt."""
    if depth > 4:
        return None
    if isinstance(obj, dict):
        for key in keys:
            value = obj.get(key)
            if value not in (None, "", [], {}):
                return value
        for value in obj.values():
            found = _reverse_pick_value(value, keys, depth + 1)
            if found not in (None, "", [], {}):
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = _reverse_pick_value(value, keys, depth + 1)
            if found not in (None, "", [], {}):
                return found
    return None


def _reverse_last_receipt(registry: dict | None = None) -> dict | None:
    """Lit le dernier receipt local exploitable. Lecture seule."""
    path = _reverse_receipt_path(registry)
    if not path.exists():
        return None
    try:
        lines = path.read_text(encoding="utf-8").splitlines()[-80:]
    except Exception:
        return None
    for line in reversed(lines):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except Exception:
            continue
        if record.get("action_locale") == "REVERSE_ROUTER_LOCAL":
            continue
        return record
    return None


def _reverse_next_for_layer(layer: str | None) -> list[str]:
    layer = (layer or "unknown").lower()
    if "obsidure" in layer:
        return ["obsidure status", "obsidure latest", "obsidure gates", "traduit ma demande en langage uni"]
    if "brody" in layer:
        return ["brody explique le contexte", "status brody", "traduit ma demande en langage uni"]
    if "lean" in layer or "obsidienne" in layer:
        return ["status lean", "brody explique le contexte", "traduit ma demande en langage uni"]
    if "terminal" in layer or "ir" in layer:
        return ["traduit ma demande en langage uni", "status", "brody explique le contexte"]
    if "live" in layer or "kernel" in layer:
        return ["status", "kernel status", "brody explique le contexte"]
    return list(_REVERSE_DEFAULT_NEXT)


def build_reverse_context_v1(raw: str, registry: dict | None = None) -> dict:
    """Construit un contexte reverse local, borne et non souverain."""
    registry = registry or {}
    normalized = normalize(raw)
    record = _reverse_last_receipt(registry)

    if not record:
        return {
            "reverse_status": "NO_CONTEXT",
            "raw": raw,
            "normalized": normalized,
            "previous_layer": None,
            "previous_mode": None,
            "previous_output": None,
            "source": "local_receipt:none",
            "confidence": 0.20,
            "next": list(_REVERSE_DEFAULT_NEXT),
            "limits": [
                "aucun contexte precedent exploitable",
                "reverse local seulement",
                "ne decide pas",
            ],
        }

    previous_layer = _reverse_pick_value(
        record,
        ("detected_layer", "target_layer", "layer", "previous_layer"),
    )
    previous_mode = _reverse_pick_value(
        record,
        ("mode_reponse", "mode", "action_type", "intent_type"),
    )
    previous_output = _reverse_pick_value(
        record,
        ("output", "plan_status", "status"),
    )

    if previous_layer:
        reverse_status = "CONTEXT_FOUND"
        confidence = 0.65
    else:
        reverse_status = "CONTEXT_PARTIAL"
        confidence = 0.40

    return {
        "reverse_status": reverse_status,
        "raw": raw,
        "normalized": normalized,
        "previous_layer": previous_layer or "unknown",
        "previous_mode": previous_mode or "unknown",
        "previous_output": previous_output or "unknown",
        "source": "local_receipt:last",
        "confidence": confidence,
        "next": _reverse_next_for_layer(str(previous_layer or "unknown")),
        "limits": [
            "contexte local non souverain",
            "aucune execution",
            "aucune mutation",
            "X108 reste autorite finale",
        ],
    }


def format_reverse_router_v1(context: dict) -> str:
    """Format humain du Reverse Router V1."""
    lines = ["Reverse Router V1", ""]

    if context.get("reverse_status") == "NO_CONTEXT":
        lines.append("Aucun contexte precedent exploitable.")
    elif context.get("reverse_status") == "CONTEXT_PARTIAL":
        lines.append("Contexte precedent partiel detecte.")
    else:
        lines.append("Contexte precedent detecte.")

    previous_layer = context.get("previous_layer")
    previous_mode = context.get("previous_mode")
    previous_output = context.get("previous_output")

    if previous_layer:
        lines.append(f"previous_layer : {previous_layer}")
    if previous_mode:
        lines.append(f"previous_mode  : {previous_mode}")
    if previous_output:
        lines.append(f"previous_output: {previous_output}")

    lines += ["", "Suites possibles :"]
    for item in context.get("next", []):
        lines.append(f"- {item}")

    lines += [
        "",
        "Lecture seule. Aucune mutation. Aucune decision souveraine.",
    ]
    return "\n".join(lines)


def build_reverse_router_response(raw: str, registry: dict) -> dict:
    """Construit la reponse Reverse Router V1 en surfaces separees."""
    context = build_reverse_context_v1(raw, registry)
    human = format_reverse_router_v1(context)

    return {
        "panel": "OBSIDIA_RESPONSE",
        "raw": raw,
        "reponse": human,
        "main_answer": {
            "direct": human,
            "summary": "",
            "next": context.get("next", []),
        },
        "etat_technique": {
            "reverse_status": context.get("reverse_status"),
            "previous_layer": context.get("previous_layer"),
            "previous_mode": context.get("previous_mode"),
            "previous_output": context.get("previous_output"),
            "confidence": context.get("confidence"),
            "source": context.get("source"),
            "mutation": "none",
            "subprocess": "none",
        },
        "outils_panel": {
            "reverse_router": "used",
            "mutation": "none",
            "subprocess": "none",
            "network": "none",
        },
        "proof_panel": {
            "source": "local",
            "authority": "NONE",
            "decision_authority": "KX108_ONLY",
            "mutation": "none",
        },
        "next_suggestions": context.get("next", []),
        "mode_reponse": "ANSWER_LOCAL",
        "detected_layer": "reverse",
        "confidence": context.get("confidence", 0.20),
        "organes_mobilises": ["Reverse Router", "Terminal", "Local Receipt"],
        "organes_mobilisables": ["Brody", "Obsidure", "OS Langage Uni", "Status"],
        "outils_utilises": ["build_reverse_context_v1"],
        "corpus_utilise": [context.get("source", "local")],
        "limites": context.get("limits", []),
        "action_locale": "REVERSE_ROUTER_LOCAL",
        "local_read_meta": {"reverse_context": context},
        "next_human_action": "choisir une suite proposee",
        "output": assert_output_allowed("GUIDE"),
        "guidance": [],
        "guidance_authority": "NONE",
        "plan_status": "OK",
    }


# ─── FIN TERMINAL REVERSE ROUTER V1 ──────────────────────────────────────────


# ─── TERMINAL BRODY BRIDGE V1 ────────────────────────────────────────────────
# OBSIDIA_TERMINAL_BRODY_BRIDGE_V1
# Bridge consultatif vers /api/brody/chat. Aucun subprocess. Aucune mutation.
# Brody explique. Brody ne decide pas. X108 reste autorite finale.

_BRODY_BRIDGE_EXACT = frozenset({
    "brody",
    "brody chat",
    "brody status",
    "brody explique",
    "brody explique le contexte",
    "explique moi obsidia",
    "explique obsidia",
    "explique le contexte",
    "explique moi le contexte",
})

_BRODY_BRIDGE_WORDS = frozenset({
    "brody",
})


def detect_brody_bridge_query(raw: str, normalized: str | None = None) -> bool:
    """Detecte une demande Brody explicite et bornee."""
    n = normalized if normalized is not None else normalize(raw)
    if not n:
        return False
    compact = n.strip()
    if compact in _BRODY_BRIDGE_EXACT:
        return True
    words = set(re.findall(r"[a-z0-9]+", compact))
    if words & _BRODY_BRIDGE_WORDS:
        return True
    return False


def _brody_bridge_endpoint(registry: dict | None = None) -> str:
    """Resolut l'endpoint Brody local depuis le registry si possible."""
    registry = registry or {}
    explicit = registry.get("brody_bridge_endpoint")
    if explicit:
        return str(explicit).rstrip("/")
    health = (registry.get("health_endpoints") or {}).get("api_health")
    if isinstance(health, str) and "/api/health" in health:
        return health.split("/api/health", 1)[0].rstrip("/") + "/api/brody/chat"
    return "http://127.0.0.1:8000/api/brody/chat"


def build_brody_bridge_payload(raw: str, registry: dict | None = None) -> dict:
    """Payload compatible BrodyChatRequest. Flags mutatifs toujours false."""
    return {
        "message": raw,
        "language": "fr",
        "session_id": "obsidia-terminal",
        "allow_provider": False,
        "allow_memory_candidate": False,
        "allow_manual_apply": False,
        "compact": True,
        "debug": False,
    }


def _brody_post_json(endpoint: str, payload: dict, timeout: float = 2.0) -> dict:
    """POST local advisory vers Brody. Aucun subprocess. Aucune mutation."""
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(body)
            except Exception:
                parsed = {"raw": body[:2000]}
            return {
                "status": "UP",
                "http_status": getattr(resp, "status", 200),
                "body": parsed,
                "endpoint": endpoint,
            }
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8", errors="replace")[:1000]
        except Exception:
            body = ""
        return {
            "status": "DOWN",
            "http_status": exc.code,
            "error_type": type(exc).__name__,
            "error": body,
            "endpoint": endpoint,
        }
    except Exception as exc:
        return {
            "status": "DOWN",
            "http_status": 0,
            "error_type": type(exc).__name__,
            "error": str(exc)[:1000],
            "endpoint": endpoint,
        }


def extract_brody_bridge_answer(data: dict) -> tuple[str, str]:
    """Extrait final_answer > response_md > response > raw."""
    if not isinstance(data, dict):
        return ("Brody indisponible: reponse non JSON.", "invalid")
    for key in ("final_answer", "response_md", "response"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return (value.strip(), key)
    try:
        return (json.dumps(data, ensure_ascii=False, indent=2)[:2000], "raw_json")
    except Exception:
        return ("Brody indisponible: reponse illisible.", "invalid")


def _brody_local_fallback_answer(raw: str, registry: dict, reason: dict) -> str:
    """Fallback local si API Brody down. Ne lance rien."""
    normalized = normalize(raw)
    try:
        plan = build_active_plan(raw, registry)
        local = build_local_corpus_answer(plan, normalized)
        if isinstance(local, dict):
            for key in ("answer", "reponse", "direct"):
                value = local.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        if isinstance(local, str) and local.strip():
            return local.strip()
    except Exception:
        pass

    detail = reason.get("error_type") or reason.get("http_status") or "UNKNOWN"
    return (
        "Brody API indisponible. Fallback terminal local actif.\n\n"
        "Brody vit dans l'API 8000 via /api/brody/chat. "
        "Le terminal peut préparer la demande, mais ne lance aucun serveur et ne mute rien.\n\n"
        f"Raison: {detail}"
    )


def build_brody_bridge_response(raw: str, registry: dict) -> dict:
    """Construit la reponse Brody Bridge V1 en surfaces separees."""
    endpoint = _brody_bridge_endpoint(registry)
    payload = build_brody_bridge_payload(raw, registry)
    result = _brody_post_json(endpoint, payload)

    if result.get("status") == "UP" and isinstance(result.get("body"), dict):
        answer, answer_source = extract_brody_bridge_answer(result["body"])
        brody_status = "UP"
        source = "api_brody_chat"
        fallback = False
    else:
        answer = _brody_local_fallback_answer(raw, registry, result)
        answer_source = "local_fallback"
        brody_status = "DOWN"
        source = "terminal_fallback"
        fallback = True

    return {
        "panel": "OBSIDIA_RESPONSE",
        "raw": raw,
        "reponse": answer,
        "main_answer": {
            "direct": answer,
            "summary": "",
            "next": ["status brody", "brody explique le contexte", "traduit ma demande en langage uni"],
        },
        "etat_technique": {
            "brody_bridge": "used",
            "brody_status": brody_status,
            "endpoint": endpoint,
            "http_status": result.get("http_status"),
            "answer_source": answer_source,
            "source": source,
            "fallback": fallback,
            "mutation": "none",
            "subprocess": "none",
            "memory_write": False,
        },
        "outils_panel": {
            "brody_bridge": "used",
            "method": "POST",
            "route": "/api/brody/chat",
            "mutation": "none",
            "subprocess": "none",
            "memory_write": "forbidden",
            "decision": "forbidden",
        },
        "proof_panel": {
            "source": source,
            "authority": "NONE",
            "decision_authority": "KX108_ONLY",
            "brody_decides": False,
            "emits_act": False,
            "mutation": "none",
        },
        "next_suggestions": ["status brody", "brody explique le contexte", "traduit ma demande en langage uni"],
        "mode_reponse": "ANSWER_BRODY" if not fallback else "ANSWER_LOCAL",
        "detected_layer": "brody",
        "confidence": 0.85 if not fallback else 0.55,
        "organes_mobilises": ["Brody Bridge", "Terminal", "API 8000"] if not fallback else ["Brody Bridge", "Terminal", "Fallback local"],
        "organes_mobilisables": ["Reverse Router", "OS Langage Uni", "Status"],
        "outils_utilises": ["urllib.request POST /api/brody/chat"] if not fallback else ["terminal local fallback"],
        "corpus_utilise": [source],
        "limites": [
            "Brody consultatif seulement",
            "aucune decision souveraine",
            "aucune ecriture memoire",
            "aucun subprocess",
            "X108 reste autorite finale",
        ],
        "action_locale": "BRODY_BRIDGE_LOCAL",
        "local_read_meta": {
            "brody_bridge": {
                "endpoint": endpoint,
                "status": brody_status,
                "answer_source": answer_source,
                "fallback": fallback,
            }
        },
        "next_human_action": "lire la reponse Brody ou verifier status brody",
        "output": assert_output_allowed("GUIDE"),
        "guidance": [],
        "guidance_authority": "NONE",
        "plan_status": "OK",
    }


# ─── FIN TERMINAL BRODY BRIDGE V1 ────────────────────────────────────────────


# ─── TERMINAL OBSIDURE BRIDGE V1 ─────────────────────────────────────────────
# OBSIDIA_TERMINAL_OBSIDURE_BRIDGE_V1
# Bridge readonly vers _PATCH_PROPOSALS et gates. Aucun subprocess. Aucune mutation.
# Obsidure propose. Le terminal lit. L'humain applique. X108 reste autorite finale.

_OBSIDURE_BRIDGE_WORDS = frozenset({
    "obsidure", "coder", "code", "patch", "proposal", "proposals",
    "correction", "corrige", "fix", "bug",
})

_OBSIDURE_BRIDGE_EXACT = frozenset({
    "obsidure",
    "obsidure status",
    "obsidure latest",
    "obsidure gates",
    "peux tu coder",
    "peux-tu coder",
    "code une correction",
    "coder une correction",
})


def detect_obsidure_bridge_query(raw: str, normalized: str | None = None) -> bool:
    """Detecte une demande Obsidure explicite ou code-request bornee."""
    n = normalized if normalized is not None else normalize(raw)
    if not n:
        return False
    compact = n.strip()
    if compact in _OBSIDURE_BRIDGE_EXACT:
        return True
    words = set(re.findall(r"[a-z0-9]+", compact))
    if "obsidure" in words:
        return True
    if words & {"coder", "code", "patch", "correction", "corrige", "fix", "bug"}:
        blocked_question_words = {"pourquoi", "comment", "explique", "definition"}
        return not bool(words & blocked_question_words)
    return False


def _obsidure_proposals_root() -> Path:
    return REPO_ROOT / "_PATCH_PROPOSALS"


def _obsidure_safe_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:
        return {"_json_error": type(exc).__name__}


def _obsidure_extract_files(data: dict) -> list[str]:
    """Extrait une liste de fichiers sans supposer un schéma unique."""
    candidates = []
    for key in ("files", "files_touched", "touched_files", "target_paths", "paths"):
        value = data.get(key)
        if isinstance(value, list):
            candidates.extend(str(x) for x in value)
        elif isinstance(value, str):
            candidates.append(value)

    patches = data.get("patches")
    if isinstance(patches, list):
        for patch in patches:
            if isinstance(patch, dict):
                for key in ("path", "file", "target", "target_path"):
                    value = patch.get(key)
                    if value:
                        candidates.append(str(value))

    deduped = []
    seen = set()
    for item in candidates:
        item = str(item).strip()
        if item and item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped[:20]


def _obsidure_read_receipt_preview(path: Path, max_lines: int = 16) -> list[str]:
    if not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return []
    clean = []
    for line in lines:
        s = line.rstrip()
        if s:
            clean.append(s[:240])
        if len(clean) >= max_lines:
            break
    return clean


def collect_obsidure_bridge_state_v1(limit: int = 5) -> dict:
    """Inventaire readonly des proposals Obsidure."""
    root = _obsidure_proposals_root()
    if not root.exists():
        return {
            "status": "NO_PROPOSALS_DIR",
            "root": str(root.relative_to(REPO_ROOT)) if root.is_absolute() else str(root),
            "proposal_count": 0,
            "latest": None,
            "recent": [],
        }

    dirs = [p for p in root.iterdir() if p.is_dir()]
    items = []

    for d in dirs:
        pj = d / "proposal.json"
        receipt = d / "RECEIPT.md"
        data = _obsidure_safe_json(pj) if pj.exists() else {}

        created = (
            data.get("created_at")
            or data.get("timestamp")
            or data.get("ts")
            or data.get("created")
            or ""
        )
        status = (
            data.get("status")
            or data.get("proposal_status")
            or data.get("final_status")
            or "UNKNOWN"
        )
        objective = (
            data.get("objective")
            or data.get("goal")
            or data.get("title")
            or data.get("request")
            or ""
        )

        items.append({
            "id": d.name,
            "created_at": str(created),
            "status": str(status),
            "objective": str(objective)[:300],
            "proposal_json": pj.exists(),
            "receipt_md": receipt.exists(),
            "files": _obsidure_extract_files(data),
            "receipt_preview": _obsidure_read_receipt_preview(receipt, max_lines=10),
        })

    def sort_key(item: dict):
        return (item.get("created_at") or "", item.get("id") or "")

    recent = sorted(items, key=sort_key)[-limit:]
    latest = recent[-1] if recent else None

    return {
        "status": "OK",
        "root": "_PATCH_PROPOSALS",
        "proposal_count": len(dirs),
        "latest": latest,
        "recent": recent,
    }


def build_obsidure_gates_v1() -> list[str]:
    """Gates applicables en commands-only. Le terminal ne les execute jamais."""
    gates = []
    try:
        for name in _GATES_OBSIDURE:
            gates.append(f"scripts/gates/{name}")
    except Exception:
        gates = [
            "scripts/gates/obsidia_commit_scope_guard.py",
            "scripts/gates/obsidia_forbidden_write_check.py",
            "scripts/gates/obsidia_kernel_boundary_check.py",
        ]
    gates.append("python -m pytest tests/gates/ -q")
    return gates


def _obsidure_intent_kind(raw: str) -> str:
    n = normalize(raw)
    if "latest" in n or "dernier" in n or "derniere" in n:
        return "latest"
    if "gate" in n or "gates" in n:
        return "gates"
    if "status" in n or "statut" in n or n.strip() == "obsidure":
        return "status"
    return "prepare"


def format_obsidure_bridge_v1(state: dict, raw: str) -> str:
    """Format humain Obsidure Bridge V1."""
    kind = _obsidure_intent_kind(raw)
    latest = state.get("latest") or {}

    lines = ["Obsidure Bridge V1", ""]

    if state.get("status") != "OK":
        lines += [
            "_PATCH_PROPOSALS introuvable.",
            "Obsidure non lisible depuis le terminal local.",
        ]
    else:
        lines.append(f"proposals_count : {state.get('proposal_count', 0)}")
        if latest:
            lines.append(f"latest_id       : {latest.get('id')}")
            lines.append(f"latest_created  : {latest.get('created_at') or 'unknown'}")
            lines.append(f"latest_status   : {latest.get('status') or 'UNKNOWN'}")
            if latest.get("files"):
                lines.append("latest_files    : " + ", ".join(latest.get("files", [])[:6]))

    if kind == "latest" and latest:
        preview = latest.get("receipt_preview") or []
        if preview:
            lines += ["", "Receipt preview :"]
            for line in preview[:10]:
                lines.append(f"- {line}")

    if kind == "gates":
        lines += ["", "Gates commands-only :"]
        for gate in build_obsidure_gates_v1():
            lines.append(f"- {gate}")

    if kind == "prepare":
        lines += [
            "",
            "Préparation Obsidure :",
            "- formuler l'objectif exact",
            "- confirmer le scope fichiers",
            "- générer proposal uniquement",
            "- appliquer seulement après validation humaine",
        ]

    lines += [
        "",
        "Interdits maintenus : no auto apply, no auto commit, no auto push, no subprocess.",
    ]
    return "\n".join(lines)


def build_obsidure_bridge_response(raw: str, registry: dict) -> dict:
    """Construit la reponse Obsidure Bridge V1 en surfaces separees."""
    state = collect_obsidure_bridge_state_v1(limit=5)
    gates = build_obsidure_gates_v1()
    human = format_obsidure_bridge_v1(state, raw)
    latest = state.get("latest") or {}

    next_items = [
        "obsidure latest",
        "obsidure gates",
        "traduit ma demande en langage uni",
    ]

    return {
        "panel": "OBSIDIA_RESPONSE",
        "raw": raw,
        "reponse": human,
        "main_answer": {
            "direct": human,
            "summary": "",
            "next": next_items,
        },
        "etat_technique": {
            "obsidure_bridge": "used",
            "obsidure_status": state.get("status"),
            "proposal_count": state.get("proposal_count", 0),
            "latest_id": latest.get("id"),
            "latest_status": latest.get("status"),
            "latest_created_at": latest.get("created_at"),
            "root": state.get("root"),
            "mutation": "none",
            "subprocess": "none",
            "apply": "forbidden",
            "commit": "forbidden",
            "push": "forbidden",
        },
        "outils_panel": {
            "obsidure_bridge": "used",
            "read": "_PATCH_PROPOSALS",
            "proposal_json": "readonly",
            "receipt_md": "readonly",
            "gates": "commands-only",
            "apply": "forbidden",
            "commit": "forbidden",
            "push": "forbidden",
            "subprocess": "none",
        },
        "proof_panel": {
            "source": "_PATCH_PROPOSALS",
            "authority": "NONE",
            "decision_authority": "KX108_ONLY",
            "proposal_count": state.get("proposal_count", 0),
            "latest_status": latest.get("status"),
            "gates": gates,
            "mutation": "none",
        },
        "next_suggestions": next_items,
        "mode_reponse": "ANSWER_LOCAL",
        "detected_layer": "obsidure",
        "confidence": 0.86 if state.get("status") == "OK" else 0.45,
        "organes_mobilises": ["Obsidure Bridge", "Terminal", "_PATCH_PROPOSALS"],
        "organes_mobilisables": ["OS Langage Uni", "Reverse Router", "Gates"],
        "outils_utilises": ["collect_obsidure_bridge_state_v1"],
        "corpus_utilise": ["_PATCH_PROPOSALS", "scripts/gates"],
        "limites": [
            "lecture seule",
            "proposal-first uniquement",
            "aucune application automatique",
            "aucun commit automatique",
            "aucun push automatique",
            "X108 reste autorite finale",
        ],
        "action_locale": "OBSIDURE_BRIDGE_LOCAL",
        "local_read_meta": {"obsidure_state": state},
        "next_human_action": "choisir latest/gates ou preciser le scope de proposal",
        "output": assert_output_allowed("GUIDE"),
        "guidance": [],
        "guidance_authority": "NONE",
        "plan_status": "OK",
    }


# ─── FIN TERMINAL OBSIDURE BRIDGE V1 ─────────────────────────────────────────


def build_status_response(raw: str, target_layer: str, registry: dict) -> dict:
    """Build an ANSWER_STATUS response for a service/layer status query.
    V2: surfaces séparées. reponse = texte humain. etat_technique = panneau droit."""
    service_status: dict[str, str] = {}
    if target_layer in ("_all", "brody", "memory", "kernel", "live"):
        try:
            rt = build_runtime_service_map_v1()
            for svc_name, svc_data in rt["network"].items():
                service_status[svc_name] = svc_data.get("status", "DOWN")
        except Exception:
            pass

    def _svc(name: str) -> str:
        return service_status.get(name, "?")

    detected = target_layer if target_layer != "_all" else "live"
    etat_technique: dict = {}
    politique: list = []
    outils_panel: dict = {}
    next_suggestions: list = []
    reponse_text = ""

    if target_layer == "_all":
        api_st = _svc("api_health")
        reponse_text = (
            "La stack Obsidia est "
            + ("active" if api_st == "UP" else "PARTIELLE ou DOWN") + ".\n\n"
            "Si le runtime est READY, les organes critiques sont accessibles. "
            "Si DEGRADED, le panneau Status indique les services manquants."
        )
        etat_technique = {
            "API_HEALTH": api_st,
            "KERNEL_3001": _svc("kernel_3001"),
            "GRAPHITI_8011": _svc("graphiti_8011"),
            "UI_5173": _svc("ui_5173"),
            "NEO4J_BOLT_7688": _svc("neo4j_bolt_7688"),
            "NEO4J_BROWSER_7475": _svc("neo4j_browser_7475"),
            "SIGMA_DOMAINS": _svc("sigma_domains"),
            "SIGMA_EVALUATE": _svc("sigma_evaluate"),
            "TERMINAL_STATE": "active",
        }
        next_suggestions = ["runtime", "/status"]
    elif target_layer == "brody":
        api_st = _svc("api_health")
        reponse_text = (
            "Brody est "
            + ("actif (API 8000 UP)" if api_st == "UP" else "PARTIEL/NON (API 8000 DOWN)")
            + ".\n\n"
            "Le terminal reste l'interface principale. Brody Enriched est le mode "
            "prefere, mais les fenetres Brody separees ne sont pas lancees par defaut."
        )
        etat_technique = {
            "api_8000": api_st,
            "graphiti_8011": _svc("graphiti_8011"),
            "memory_write": "false",
            "authority": "KX108_ONLY",
        }
        next_suggestions = ["capabilities brody", "runtime"]
    elif target_layer == "obsidure":
        proposals_path = REPO_ROOT / "_PATCH_PROPOSALS"
        gates_path = REPO_ROOT / "scripts" / "gates"
        try:
            n_prop = len([p for p in proposals_path.iterdir()]) if proposals_path.is_dir() else 0
        except Exception:
            n_prop = 0
        reponse_text = (
            "Obsidure est actif cote terminal.\n\n"
            "Il est branche comme workflow code/proposal : le terminal sait router "
            "une demande de code vers Obsidure, preparer les commandes, afficher les "
            "gates et guider le proposal-first.\n\n"
            "Il n'est pas actif comme agent autonome qui applique, commit ou push tout "
            "seul. Cette partie reste volontairement bloquee par X108 et les gates."
        )
        etat_technique = {
            "terminal": "active",
            "runtime": "none",
            "workflow": "proposal-first",
            "proposals": str(n_prop) if proposals_path.is_dir() else "absent",
            "gates": "available" if gates_path.is_dir() else "absent",
            "autonomy": "blocked",
        }
        outils_panel = {
            "proposals": "available" if proposals_path.is_dir() else "absent",
            "gates": "available" if gates_path.is_dir() else "absent",
            "apply": "forbidden",
            "commit": "forbidden",
            "push": "forbidden",
        }
        politique = ["apply auto", "commit auto", "push auto"]
        next_suggestions = ["peux tu coder", "capabilities obsidure"]
    elif target_layer == "sigma":
        api_st = _svc("api_health")
        sigma_dir = REPO_ROOT / "sigma"
        reponse_text = (
            "Sigma est "
            + ("actif (API 8000 UP)" if api_st == "UP"
               else "PARTIEL (besoin API 8000 UP pour EXECUTE)")
            + ".\n\n"
            "La coherence, les contradictions et la fraicheur des signaux sont "
            "verificiables en local. L'execution complete (EXECUTE) necessite l'API."
        )
        etat_technique = {
            "terminal": "active",
            "api_8000_execute": api_st,
            "sigma_dir": "ok" if sigma_dir.is_dir() else "absent",
            "mode": "readonly local + execute si API UP",
        }
        next_suggestions = ["sigma coherence", "capabilities sigma"]
    elif target_layer == "memory":
        g_st = _svc("graphiti_8011")
        reponse_text = (
            "Memory/Graphiti est "
            + ("actif (8011 UP)" if g_st == "UP" else "PARTIEL (8011 DOWN)")
            + ".\n\n"
            "La couche memoire est readonly depuis le terminal. "
            "Les ecritures restent bloquees (memory_write=false)."
        )
        etat_technique = {
            "graphiti_8011": g_st,
            "memory_write": "false",
            "mode": "readonly frozen",
            "authority": "KX108_ONLY",
        }
        outils_panel = {"memory_write": "forbidden", "read": "allowed"}
        next_suggestions = ["memoire graphiti", "capabilities memory"]
    elif target_layer == "oie":
        receipts_p = (REPO_ROOT / "scripts" / "performance"
                      / "oie_external_claude_benchmark_v0_receipts.json")
        reponse_text = (
            "OIE est disponible (corpus local, dry-run).\n\n"
            "Le benchmark peut etre lance en dry-run. "
            "Les couts reels (COST_REAL) ne sont revendiques que sur preuve."
        )
        etat_technique = {
            "terminal": "active",
            "receipts": "ok" if receipts_p.exists() else "absent",
            "COST_REAL": "NOT_CLAIMED sauf preuve",
            "mode": "readonly, dry-run",
        }
        next_suggestions = ["oie benchmark", "capabilities oie"]
    elif target_layer == "obsidienne":
        proofs_dir = REPO_ROOT / "proofs"
        reponse_text = (
            "Lean/Obsidienne est disponible (corpus, commandes).\n\n"
            "Le terminal donne acces aux commandes de verification. "
            "L'execution de lake build reste gated et commands-only."
        )
        etat_technique = {
            "terminal": "active",
            "proofs_dir": "ok" if proofs_dir.is_dir() else "absent",
            "mode": "readonly, lake build gated",
            "exec": "forbidden from terminal",
        }
        outils_panel = {"lake_build": "commands-only", "lean_exec": "forbidden"}
        next_suggestions = ["preuves lean", "capabilities obsidienne"]
    elif target_layer == "gates":
        gates_dir = REPO_ROOT / "scripts" / "gates"
        reponse_text = (
            "Gates disponibles (scripts locaux).\n\n"
            "Les gates de commit scope, kernel boundary et sigma non-souverainete "
            "sont disponibles. L'execution automatique reste interdite."
        )
        etat_technique = {
            "terminal": "active",
            "gates_dir": "ok" if gates_dir.is_dir() else "absent",
            "auto_exec": "forbidden",
            "decision": "X108_ONLY",
        }
        outils_panel = {"auto_execute": "forbidden", "read": "allowed"}
        next_suggestions = ["capabilities gates"]
    elif target_layer == "domains":
        reponse_text = (
            "Domains est disponible (bridge-only).\n\n"
            "Les domaines (Bank, Trading, GPS) sont accessibles en lecture. "
            "Les adapters POST sont interdits depuis le terminal."
        )
        etat_technique = {
            "terminal": "active",
            "mode": "bridge-only, guidance",
            "POST_adapters": "forbidden from terminal",
        }
        next_suggestions = ["domains bank trading gps", "capabilities domains"]
    elif target_layer == "kernel":
        k_st = _svc("kernel_3001")
        reponse_text = (
            "Kernel X-108 : "
            + ("UP (socket 3001)" if k_st == "UP" else "non detectable (socket 3001)")
            + ".\n\n"
            "Le Kernel est la seule autorite d'admissibilite. "
            "Le terminal le consulte en status readonly uniquement."
        )
        etat_technique = {
            "kernel_3001": k_st,
            "decision_authority": "KX108_ONLY",
            "mutations": "forbidden",
            "ALLOW_BLOCK_HOLD_ACT": "forbidden from terminal",
        }
        next_suggestions = ["capabilities kernel"]
    elif target_layer == "thermo":
        reponse_text = (
            "Thermo (ENERGY_THERMO) est disponible en corpus local.\n\n"
            "La couche mesure l'efficacite energetique, la dette thermodynamique "
            "et le mismatch sigma/verite. Readonly depuis le terminal."
        )
        etat_technique = {
            "terminal": "active",
            "mode": "corpus local, readonly",
            "decisions": "forbidden",
        }
        next_suggestions = ["capabilities thermo"]
    else:
        reponse_text = f"Couche '{target_layer}' disponible dans le terminal."
        etat_technique = {
            "terminal": "active",
            "note": "voir capabilities pour detail",
        }
        next_suggestions = [f"capabilities {target_layer}"]
        detected = target_layer

    plan = build_active_plan(raw, registry)

    return {
        "panel": "OBSIDIA_RESPONSE", "raw": raw,
        "reponse": reponse_text,
        "main_answer": {
            "direct": reponse_text,
            "summary": "",
            "next": next_suggestions[:2],
        },
        "etat_technique": etat_technique,
        "outils_panel": outils_panel,
        "politique": politique,
        "next_suggestions": next_suggestions,
        "mode_reponse": "ANSWER_STATUS",
        "detected_layer": detected,
        "confidence": plan.get("confidence", 0.5),
        "organes_mobilises": plan.get("organes_mobilises", []),
        "organes_mobilisables": plan.get("organes_mobilisables", []),
        "outils_utilises": plan.get("outils_utilises", []),
        "corpus_utilise": [f"status:{target_layer}"],
        "limites": [
            "lecture locale uniquement",
            "X108 = autorite finale",
            "pas de subprocess",
        ],
        "action_locale": "STATUS_CHECK_LOCAL",
        "local_read_meta": {"target_layer": target_layer},
        "next_human_action": next_suggestions[0] if next_suggestions else f"capabilities {detected}",
        "output": assert_output_allowed("GUIDE"),
        "guidance": plan.get("guidance", []),
        "guidance_authority": "NONE",
        "plan_status": plan.get("plan_status", "OK"),
    }


# ─── FIN ANSWER_STATUS ────────────────────────────────────────────────────────


def build_surface_model(response: dict) -> dict:
    """Transform a response dict into clean separated surfaces. Pure, no I/O.
    V2: LEFT = réponse humaine, RIGHT = métadonnées techniques, COMPOSER = invite."""
    mode = response.get("mode_reponse", "")

    if "main_answer" in response:
        return {
            "main_answer": response["main_answer"],
            "status_panel": response.get("etat_technique", {}),
            "tools_panel": response.get("outils_panel", {}),
            "proof_panel": response.get("proof_panel", {}),
            "plan_panel": {
                "layer": response.get("detected_layer", "?"),
                "mode": mode,
                "status": "PARTIAL" if mode == "ANSWER_STATUS" else "ROUTED",
                "output": response.get("output", "?"),
                "next": response.get("next_human_action", ""),
            },
        }

    reponse = response.get("reponse", "")
    if mode == "ANSWER_STATUS":
        direct_lines: list[str] = []
        skip_headers = ("REPONSE DIRECTE", "ETAT", "INTERDIT", "A FAIRE",
                        "ETAT SERVICES", "COUCHES TERMINAL")
        in_direct = False
        for line in reponse.splitlines():
            stripped = line.strip()
            if stripped == "REPONSE DIRECTE":
                in_direct = True
                continue
            if any(stripped.startswith(h) for h in skip_headers[1:]):
                in_direct = False
                continue
            if in_direct:
                direct_lines.append(line)
        direct = "\n".join(direct_lines).strip()
        if not direct:
            non_empty = [l for l in reponse.splitlines() if l.strip()]
            direct = non_empty[0] if non_empty else reponse
    else:
        clean = [l for l in reponse.splitlines()
                 if not any(tok in l for tok in _SURFACE_FILTER_TOKENS)]
        direct = "\n".join(clean).strip()

    return {
        "main_answer": {"direct": direct, "summary": "", "next": []},
        "status_panel": response.get("etat_technique", {}),
        "tools_panel": response.get("outils_panel", {}),
        "proof_panel": {},
        "plan_panel": {
            "layer": response.get("detected_layer", "?"),
            "mode": mode,
            "status": "PARTIAL" if mode == "ANSWER_STATUS" else "ROUTED",
            "output": response.get("output", "?"),
            "next": response.get("next_human_action", ""),
        },
    }


def extract_status_panel(response: dict) -> list[str]:
    """Extract STATUS tab content for right panel. Pure."""
    etat = response.get("etat_technique", {})
    layer = response.get("detected_layer", "?")

    lines = ["=== STATUS ===", ""]
    if etat:
        for k, v in list(etat.items())[:12]:
            lines.append(f"  {str(k)[:16]}: {str(v)[:18]}")
    else:
        lines.append(f"  layer: {layer}")
        lines.append("  (pas de donnees techniques)")
    lines += ["", "AUTORITE:", "  X108=FINAL"]
    return lines


def extract_tools_panel(response: dict) -> list[str]:
    """Extract TOOLS tab content for right panel. Pure."""
    outils = response.get("outils_panel", {})
    politique = response.get("politique", [])

    lines = ["=== TOOLS ===", ""]
    if outils:
        for k, v in list(outils.items())[:10]:
            lines.append(f"  {str(k)[:14]}: {str(v)[:14]}")
    elif politique:
        lines += ["INTERDITS:"]
        for p in politique[:5]:
            lines.append(f"  {str(p)[:26]}: forbidden")
    else:
        layer = response.get("detected_layer", "?")
        cap_layer = layer.split(":")[0] if ":" in layer else layer
        cap = CAPABILITY_GRAPH_V3.get(cap_layer, CAPABILITY_GRAPH_V3.get("unknown", {}))
        ops_allowed = cap.get("ops_allowed", [])
        ops_forbidden = cap.get("ops_forbidden", [])
        if ops_allowed:
            lines.append("AUTORISEES:")
            for op in ops_allowed[:4]:
                lines.append(f"  {str(op)[:24]}")
        if ops_forbidden:
            lines.append("INTERDITES:")
            for op in ops_forbidden[:3]:
                lines.append(f"  {str(op)[:24]}")
    lines += ["", "AUTORITE:", "  X108=FINAL"]
    return lines


def extract_proof_panel(response: dict) -> list[str]:
    """Extract PROOF tab content for right panel. Pure."""
    layer = response.get("detected_layer", "?")
    corpus = response.get("corpus_utilise", [])

    lines = ["=== PROOF ===", ""]
    if layer in ("obsidienne", "corpus:lean_proofs"):
        lines += [
            "  source: local",
            "  lean_surface: V2 (232 entries)",
            "  lake_build: commands-only",
            "  lean_exec: forbidden",
            "",
            "  verify_all.py: humain uniquement",
            "  lean_decides: false",
            "  forbidden_ok: true",
        ]
    elif layer == "audit":
        lines += [
            "  source: local",
            "  merkle_seal: readonly",
            "  manifest: readonly",
            "  regen: forbidden",
        ]
    else:
        lines += [
            "  source: local",
            "  registry: ok",
            "  corpus: ok",
        ]
        if corpus:
            lines.append("  corpus_items:")
            for c in corpus[:3]:
                lines.append(f"    {str(c)[:22]}")
    lines += ["", "AUTORITE:", "  X108=FINAL"]
    return lines


# ─── CORE SURFACE COMPOSER V1 ────────────────────────────────────────────────
# OBSIDIA_TERMINAL_CORE_SURFACE_COMPOSER_V1
# Normalise les surfaces terminal. Ne route pas. Ne decide pas. Ne mute rien.

_CORE_SURFACE_COMPOSER_VERSION = "CORE_SURFACE_COMPOSER_V1"


def _composer_text(value, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _composer_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def compose_core_surfaces_v1(response: dict, raw: str = "", registry: dict | None = None) -> dict:
    """Uniformise main/status/tools/proof/plan sans changer l'autorite.

    Garanties:
    - aucune execution
    - aucune mutation
    - aucun subprocess
    - Brody reste consultatif
    - Obsidure reste proposal-first
    - decision_authority = KX108_ONLY
    """
    if not isinstance(response, dict):
        response = {
            "panel": "OBSIDIA_RESPONSE",
            "raw": raw,
            "reponse": _composer_text(response),
            "mode_reponse": "ANSWER_LOCAL",
            "detected_layer": "unknown",
            "confidence": 0.0,
            "output": assert_output_allowed("GUIDE"),
        }

    out = dict(response)
    reponse = _composer_text(out.get("reponse"), "")
    layer = _composer_text(out.get("detected_layer"), "unknown") or "unknown"
    mode = _composer_text(out.get("mode_reponse"), "ANSWER_LOCAL") or "ANSWER_LOCAL"

    out.setdefault("panel", "OBSIDIA_RESPONSE")
    out.setdefault("raw", raw)
    out.setdefault("mode_reponse", mode)
    out.setdefault("detected_layer", layer)
    out.setdefault("confidence", 0.0)
    out.setdefault("output", assert_output_allowed("GUIDE"))
    out.setdefault("plan_status", "OK")
    out.setdefault("guidance", [])
    out.setdefault("guidance_authority", "NONE")
    out.setdefault("next_suggestions", [])
    out.setdefault("limites", [])
    out.setdefault("corpus_utilise", [])

    # Main surface.
    main = out.get("main_answer")
    if not isinstance(main, dict):
        main = {
            "direct": reponse,
            "summary": "",
            "next": _composer_list(out.get("next_suggestions")),
        }
    main.setdefault("direct", reponse)
    main.setdefault("summary", "")
    main.setdefault("next", _composer_list(out.get("next_suggestions")))
    out["main_answer"] = main

    # Status surface.
    etat = out.get("etat_technique")
    if not isinstance(etat, dict):
        etat = {}
    etat.setdefault("layer", layer)
    etat.setdefault("mode", mode)
    etat.setdefault("output", out.get("output"))
    etat.setdefault("mutation", "none")
    etat.setdefault("subprocess", "none")
    etat.setdefault("decision_authority", "KX108_ONLY")
    etat["surface_composer"] = _CORE_SURFACE_COMPOSER_VERSION
    out["etat_technique"] = etat

    # Tools surface.
    tools = out.get("outils_panel")
    if not isinstance(tools, dict):
        tools = {}
    tools.setdefault("mutation", "none")
    tools.setdefault("subprocess", "none")
    tools.setdefault("decision", "forbidden")
    tools.setdefault("auto_apply", "forbidden")
    tools.setdefault("auto_commit", "forbidden")
    tools.setdefault("auto_push", "forbidden")
    tools["surface_composer"] = "used"
    out["outils_panel"] = tools

    # Proof surface.
    proof = out.get("proof_panel")
    if not isinstance(proof, dict):
        proof = {}
    proof.setdefault("source", "local")
    proof.setdefault("authority", "NONE")
    proof.setdefault("decision_authority", "KX108_ONLY")
    proof.setdefault("mutation", "none")
    proof.setdefault("surface_composer", _CORE_SURFACE_COMPOSER_VERSION)
    out["proof_panel"] = proof

    # Plan/meta surface.
    out["surface_composer"] = _CORE_SURFACE_COMPOSER_VERSION
    out.setdefault("next_human_action", "choisir la prochaine action readonly")
    out.setdefault("action_locale", "COMPOSED_LOCAL")
    out.setdefault("local_read_meta", None)

    # Normalisation stricte des couches sensibles.
    if layer == "brody":
        out["proof_panel"].setdefault("brody_decides", False)
        out["proof_panel"].setdefault("emits_act", False)
        out["outils_panel"].setdefault("memory_write", "forbidden")
    if layer == "obsidure":
        out["outils_panel"]["apply"] = "forbidden"
        out["outils_panel"]["commit"] = "forbidden"
        out["outils_panel"]["push"] = "forbidden"
    if out.get("output") == "POLICY_DENY":
        out["plan_status"] = "DENIED"
        out["etat_technique"]["mutation"] = "forbidden"
        out["proof_panel"]["mutation"] = "forbidden"

    return attach_dynamic_panels_v1(out)


# ─── FIN CORE SURFACE COMPOSER V1 ────────────────────────────────────────────


def answer_router(raw: str, registry: dict) -> dict:
    # Pre-garde mutation globale — doit passer avant IR/Reverse/Brody/Obsidure.
    # Les bridges peuvent guider, jamais absorber commit/apply/push/deploy/delete.
    normalized_for_policy = normalize(raw)
    denied = policy_check(normalized_for_policy, registry)

    # Fallback dur si registry minimal en test ou absent.
    # Les mots mutatifs restent deny même sans policy.deny_keywords.
    if not denied:
        mutation_words = set(re.findall(r"[a-z0-9]+", normalized_for_policy))
        for hard_kw in ("commit", "push", "apply", "deploy", "delete", "supprime"):
            if hard_kw in mutation_words:
                denied = hard_kw
                break

    if denied:
        _policy_response = {
            "panel": "OBSIDIA_RESPONSE",
            "raw": raw,
            "reponse": registry.get("policy", {}).get(
                "deny_message",
                "Action refusee par politique terminal: mutation interdite."
            ),
            "main_answer": {
                "direct": registry.get("policy", {}).get(
                    "deny_message",
                    "Action refusee par politique terminal: mutation interdite."
                ),
                "summary": "",
                "next": ["reformuler en demande readonly", "demander un plan commands-only"],
            },
            "etat_technique": {
                "policy": "deny",
                "deny_keyword": denied,
                "mutation": "forbidden",
                "subprocess": "none",
                "decision_authority": "KX108_ONLY",
            },
            "outils_panel": {
                "apply": "forbidden",
                "commit": "forbidden",
                "push": "forbidden",
                "deploy": "forbidden",
                "delete": "forbidden",
                "subprocess": "none",
            },
            "proof_panel": {
                "source": "policy_check",
                "authority": "NONE",
                "decision_authority": "KX108_ONLY",
                "mutation": "forbidden",
            },
            "next_suggestions": ["reformuler en readonly", "demander un plan"],
            "mode_reponse": "POLICY_DENY",
            "detected_layer": "policy",
            "confidence": 1.0,
            "organes_mobilises": ["Terminal Policy", "X108 Boundary"],
            "organes_mobilisables": [],
            "outils_utilises": ["policy_check"],
            "corpus_utilise": ["registry.policy"],
            "limites": ["mutation interdite depuis le terminal"],
            "action_locale": "POLICY_DENY_LOCAL",
            "local_read_meta": {"deny_keyword": denied},
            "next_human_action": "reformuler sans mutation",
            "output": assert_output_allowed("POLICY_DENY"),
            "guidance": [],
            "guidance_authority": "NONE",
            "plan_status": "DENIED",
        }
        return compose_core_surfaces_v1(_policy_response, raw, registry)
        return compose_core_surfaces_v1(_policy_response, raw, registry)

    """Moteur universel. Reutilise build_active_plan(); ne lance jamais rien
    hors HTTP GET readonly ; toute sortie passe par assert_output_allowed()."""
    # Branche capabilities — detection prefixe avant calcul du plan principal.
    # policy_check reste prioritaire : build_active_plan l'execute en interne.
    _cap_inner, _cap_verbose = _parse_capabilities_input(raw)
    if _cap_inner is not None:
        cap_plan = build_active_plan(_cap_inner, registry)
        if cap_plan.get("deny_keyword"):
            denied = cap_plan["deny_keyword"]
            _deny_rep = (f'Refus policy : mot interdit "{denied}". '
                         "Le terminal n'a aucun chemin d'application (pas de "
                         "--apply, pas de commit, pas de subprocess). Workflow "
                         "gated humain si la mutation est reellement voulue.")
            return {
                "panel": "OBSIDIA_RESPONSE", "raw": raw, "reponse": _deny_rep,
                "mode_reponse": "ANSWER_POLICY_DENY",
                "detected_layer": cap_plan["detected_layer"],
                "confidence": cap_plan["confidence"],
                "organes_mobilises": cap_plan["organes_mobilises"],
                "organes_mobilisables": cap_plan["organes_mobilisables"],
                "outils_utilises": cap_plan["outils_utilises"],
                "corpus_utilise": ["aucun — policy deny"],
                "limites": ["POLICY_DENY — capabilities non accessibles"],
                "action_locale": None, "local_read_meta": None,
                "next_human_action": ("workflow gated humain "
                                      "(docs/protocols/OBSIDURE_APPLY_PROTOCOL.md)"),
                "output": assert_output_allowed("POLICY_DENY"),
                "guidance": cap_plan["guidance"], "guidance_authority": "NONE",
                "plan_status": cap_plan["plan_status"],
            }
        cap_view = build_capability_view(_cap_inner, registry,
                                         verbose=_cap_verbose, plan=cap_plan)
        cap_rep = format_capability_view(cap_view, verbose=_cap_verbose)
        return {
            "panel": "OBSIDIA_RESPONSE", "raw": raw, "reponse": cap_rep,
            "mode_reponse": "ANSWER_LOCAL",
            "detected_layer": cap_view["detected_layer"],
            "confidence": cap_view["confidence"],
            "organes_mobilises": cap_view["organes_mobilises"],
            "organes_mobilisables": cap_plan["organes_mobilisables"],
            "outils_utilises": cap_plan["outils_utilises"],
            "corpus_utilise": cap_view["corpus_topics"] or ["aucun"],
            "limites": ["reponse limitee au corpus/droits readonly — X108 decide"],
            "action_locale": "CAPABILITY_DISPLAY",
            "local_read_meta": None,
            "next_human_action": cap_view["next_human_action"],
            "output": assert_output_allowed("GUIDE"),
            "guidance": cap_plan["guidance"], "guidance_authority": "NONE",
            "plan_status": cap_plan["plan_status"],
        }

    # Branche runtime service map — policy_check prioritaire via build_active_plan interne.
    if _parse_runtime_input(raw):
        _rt_plan = build_active_plan(raw, registry)
        if _rt_plan.get("deny_keyword"):
            _deny_kw = _rt_plan["deny_keyword"]
            _deny_rep = (f'Refus policy : mot interdit "{_deny_kw}". '
                         "Le terminal ne peut pas executer cette commande.")
            return {
                "panel": "OBSIDIA_RESPONSE", "raw": raw, "reponse": _deny_rep,
                "mode_reponse": "ANSWER_POLICY_DENY",
                "detected_layer": _rt_plan["detected_layer"],
                "confidence": _rt_plan["confidence"],
                "organes_mobilises": _rt_plan["organes_mobilises"],
                "organes_mobilisables": _rt_plan["organes_mobilisables"],
                "outils_utilises": _rt_plan["outils_utilises"],
                "corpus_utilise": ["aucun — policy deny"],
                "limites": ["POLICY_DENY"],
                "action_locale": None, "local_read_meta": None,
                "next_human_action": "workflow gated si mutation voulue",
                "output": assert_output_allowed("POLICY_DENY"),
                "guidance": _rt_plan["guidance"], "guidance_authority": "NONE",
                "plan_status": _rt_plan["plan_status"],
            }
        _rt_result = build_runtime_service_map_v1()
        _rt_rep = format_runtime_service_map_v1(_rt_result)
        return {
            "panel": "OBSIDIA_RESPONSE", "raw": raw, "reponse": _rt_rep,
            "mode_reponse": "ANSWER_LOCAL",
            "detected_layer": _rt_plan["detected_layer"],
            "confidence": _rt_plan["confidence"],
            "organes_mobilises": _rt_plan["organes_mobilises"],
            "organes_mobilisables": _rt_plan["organes_mobilisables"],
            "outils_utilises": _rt_plan["outils_utilises"],
            "corpus_utilise": ["RUNTIME_SERVICE_MAP_V1"],
            "limites": ["lecture seule — aucun service lance — X108 reste autorite"],
            "action_locale": "RUNTIME_SERVICE_MAP_READONLY",
            "local_read_meta": {
                "terminal_state": _rt_result["terminal_state"],
                "services_checked": len(_rt_result["network"]),
                "local_checks": len(_rt_result["local"]),
            },
            "next_human_action": (
                "si DEGRADED: lancer manuellement les services manquants "
                "(scripts/OBSIDIA_LAUNCHERS/)"
            ),
            "output": assert_output_allowed("GUIDE"),
            "guidance": _rt_plan["guidance"], "guidance_authority": "NONE",
            "plan_status": _rt_plan["plan_status"],
        }

    # Branche ANSWER_STATUS — requetes "X est actif ?" / "stack active" / etc.
    _st_target = detect_status_query(raw, normalize(raw))
    if _st_target is not None:
        _st_plan = build_active_plan(raw, registry)
        if _st_plan.get("deny_keyword"):
            _deny_kw = _st_plan["deny_keyword"]
            return {
                "panel": "OBSIDIA_RESPONSE", "raw": raw,
                "reponse": f'Refus policy : mot interdit "{_deny_kw}".',
                "mode_reponse": "ANSWER_POLICY_DENY",
                "detected_layer": _st_plan["detected_layer"],
                "confidence": _st_plan["confidence"],
                "organes_mobilises": _st_plan["organes_mobilises"],
                "organes_mobilisables": _st_plan["organes_mobilisables"],
                "outils_utilises": _st_plan["outils_utilises"],
                "corpus_utilise": ["aucun — policy deny"],
                "limites": ["POLICY_DENY"], "action_locale": None, "local_read_meta": None,
                "next_human_action": "workflow gated humain si mutation voulue",
                "output": assert_output_allowed("POLICY_DENY"),
                "guidance": _st_plan["guidance"], "guidance_authority": "NONE",
                "plan_status": _st_plan["plan_status"],
            }
        return build_status_response(raw, _st_target, registry)

    # Branche OS Langage Uni — demande explicite de traduction IR.
    if detect_unified_ir_query(raw, normalize(raw)):
        return compose_core_surfaces_v1(build_unified_ir_response(raw, registry), raw, registry)

    # Branche Obsidure Bridge — proposals/gates readonly.
    if detect_obsidure_bridge_query(raw, normalize(raw)):
        return compose_core_surfaces_v1(build_obsidure_bridge_response(raw, registry), raw, registry)

    # Branche Brody Bridge — POST local advisory, fallback terminal si API down.
    if detect_brody_bridge_query(raw, normalize(raw)):
        return compose_core_surfaces_v1(build_brody_bridge_response(raw, registry), raw, registry)

    # Branche Reverse Router — reprise locale bornee.
    if detect_reverse_router_query(raw, normalize(raw)):
        return compose_core_surfaces_v1(build_reverse_router_response(raw, registry), raw, registry)

    plan = build_active_plan(raw, registry)
    normalized = plan["normalized"]
    mode = select_answer_mode(plan, normalized, registry)
    assert mode in ANSWER_MODES
    layer = plan["detected_layer"]
    corpus_used: list = []
    limites = ["reponse limitee au corpus/droits readonly du terminal — X108 decide"]
    reponse = ""
    next_h = plan["next_human_action"]

    # LOCAL_READ_GUIDE_V1 : la policy registry (deny) reste prioritaire ;
    # ensuite la classification locale guide-only peut prendre la main.
    local_req = None
    if mode != "ANSWER_POLICY_DENY":
        local_req = classify_local_read_intent(raw, normalized)
    if local_req is not None:
        local_req = build_local_read_guide_response(local_req)
        mode = local_req["mode"]
        assert mode in ANSWER_MODES
        reponse = local_req["reponse"]
        corpus_used = list(local_req.get("corpus", []))
        limites = limites + list(local_req.get("limites", []))
        next_h = local_req["next_h"]
        # Lecture reelle bornee reussie -> sortie EXECUTE (readonly, comme doctor).
        _force_execute = local_req.get("output_execute", False)

    if local_req is not None:
        pass  # reponse locale deja construite (guide-only, aucune lecture reelle)
    elif mode == "ANSWER_POLICY_DENY":
        reponse = (f'Refus policy : mot interdit "{plan["deny_keyword"]}". '
                   "Le terminal n'a aucun chemin d'application (pas de --apply, pas de "
                   "commit, pas de subprocess). Workflow gated humain si la mutation est "
                   "reellement voulue.")
        limites.append("repondre completement exigerait une mutation [INTERDIT] — "
                       "alternative : workflow gated humain (OBSIDURE_APPLY_PROTOCOL.md)")
    elif mode == "ANSWER_PLAN":
        if _contains(normalized, _BLOCKER_WORDS):
            reponse = format_blockers_view(registry)
            next_h = "lancer toi-meme: git status --short ; git diff --cached --name-only"
        else:
            reponse = ("Plan prudent :\n  couche " + layer + " | sortie prevue "
                       + plan["output_predicted"]
                       + "\n  organes : " + "; ".join(o.split(" [")[0] for o in plan["organes_mobilises"][:5])
                       + "\n  mobilisables : "
                       + ("; ".join(o.split(" [")[0] for o in plan["organes_mobilisables"][:4]) or "aucun")
                       + '\n  Detail complet : obsidia plan "' + raw + '"')
            if not _contains(normalized, _META_WORDS):
                next_h = "preciser le scope de travail voulu"
        corpus_used = plan["corpus"]
    elif mode == "ANSWER_LIVE_READONLY":
        if layer == "sigma" and _contains(normalized, _WHY_WORDS):
            reponse = ("Guidance actuelle : " + plan["guidance"]
                       + "\nRaisons reelles (signaux readonly, rien d'invente) :\n"
                       + "\n".join("  - " + r for r in plan["guidance_reasons"]))
            corpus_used = plan["corpus"]
            next_h = "aucune — relire les signaux sources si doute"
        else:
            doc = run_doctor(registry)
            reponse = "Etat live (HTTP GET readonly) :\n" + "\n".join(
                f"  {k:24} {v['status']}" for k, v in doc.items())
            corpus_used = ["registry.health_endpoints"]
            next_h = "relancer la stack toi-meme si DOWN (launchers COMMANDS_ONLY)"
        limites.append("lecture seule — kernel 3001 NOT_CONFIRMED tant que /health non valide")
    elif mode == "ANSWER_LOCAL":
        txt, sources = build_local_corpus_answer(plan, normalized)
        if txt is None:
            mode = "ANSWER_UNKNOWN"
        else:
            reponse = txt
            corpus_used = sources
            next_h = "aucune"
    elif mode == "ANSWER_COMMANDS_ONLY":
        reponse, _cmds = build_commands_answer(plan, registry)
        corpus_used = plan["corpus"]
        limites.append("repondre completement exigerait l'execution [INTERDIT] — "
                       "alternative : lancer toi-meme la commande ci-dessus")

    if mode == "ANSWER_UNKNOWN" and not reponse:
        topic_u, entry_u = _corpus_lookup(normalized)
        if entry_u is not None and not entry_u.get("loader"):
            # sujet indexe mais question non reconnue comme "connaissance" :
            # servir la reponse corpus plutot que mourir en UNKNOWN.
            reponse = entry_u["answer"]
            corpus_used = entry_u["sources"]
            next_h = "aucune"
            mode = "ANSWER_LOCAL"  # sujet indexe servi : etiquette et sortie coherentes
        else:
            reponse = build_unknown_answer(plan, raw, "IN trop vague ou sujet hors corpus local")
            if _contains(normalized, _KNOWLEDGE_WORDS):
                # Repli definitionnel declare (LOCAL_CORPUS_EXTENSION_V2) :
                # orientation vers le glossaire canonique, jamais de substance inventee.
                reponse += ("\nRepli definitionnel : docs/GLOSSAIRE.md — \"Dual Obsidia : "
                            "l'IA propose, le Juge dispose\". Terme non indexe en direct.")
            next_h = "reformuler ou fournir la source/scope"

    _out_name = _MODE_TO_OUTPUT[mode]
    if local_req is not None and local_req.get("output_execute"):
        _out_name = "EXECUTE"  # lecture reelle bornee reussie
    output = assert_output_allowed(_out_name)
    # Hint de couche (affichage seulement) : couche registry inconnue mais
    # sujet corpus identifie -> etiquette honnete corpus:<sujet>.
    display_layer = layer
    # Lecture locale reelle (V2A) : couche documentaire, jamais la couche
    # registry parasite (ex. "contexte" -> trigger brody). Affichage seulement.
    if local_req is not None and local_req.get("output_execute"):
        _rel = (local_req.get("corpus") or ["?"])[0]
        display_layer = f"file_read:{_rel}"
    elif layer == "unknown" and mode == "ANSWER_LOCAL":
        t_h, _e_h = _corpus_lookup(normalized)
        if t_h:
            display_layer = SUBJECT_LAYER_HINTS.get(t_h, "corpus:" + t_h)
    return {
        "panel": "OBSIDIA_RESPONSE", "raw": raw, "reponse": reponse,
        "mode_reponse": mode, "detected_layer": display_layer, "confidence": plan["confidence"],
        "organes_mobilises": plan["organes_mobilises"],
        "organes_mobilisables": plan["organes_mobilisables"],
        "outils_utilises": plan["outils_utilises"],
        "corpus_utilise": corpus_used or ["aucun"],
        "limites": limites,
        "action_locale": (local_req or {}).get("kind"),
        "local_read_meta": (local_req or {}).get("meta"),
        "next_human_action": next_h,
        "output": output,
        "guidance": plan["guidance"], "guidance_authority": "NONE",
        "plan_status": plan["plan_status"],
    }


def format_surface_response(r: dict) -> str:
    """One-shot output V2 : surfaces séparées (REPONSE / PLAN_PANEL / STATUS_PANEL / TOOLS_PANEL).
    Garantie : REPONSE ne contient aucun token système interne."""
    # Réponse gauche via la même logique que le TUI
    main_panel = extract_main_answer_panel(r)
    plan_panel = extract_plan_panel(r, active_tab="PLAN")
    status_panel = extract_status_panel(r)
    tools_panel = extract_tools_panel(r)

    lines = ["REPONSE:", ""]
    for l in main_panel:
        lines.append(f"  {l}" if l else "")

    # Suggestions depuis next_suggestions (V2) si non déjà dans main_panel
    nexts = r.get("next_suggestions", [])
    if nexts and not any("-> obsidia>" in l for l in main_panel):
        lines.append("")
        for n in nexts[:2]:
            lines.append(f"  -> obsidia> {n}")

    lines += ["", "PLAN_PANEL:"]
    for l in plan_panel:
        lines.append(f"  {l}" if l.strip() else "")

    non_empty_status = [l for l in status_panel if l.strip() and l.strip() != "=== STATUS ==="]
    if non_empty_status:
        lines += ["", "STATUS_PANEL:"]
        for l in status_panel:
            lines.append(f"  {l}" if l.strip() else "")

    non_empty_tools = [l for l in tools_panel if l.strip() and l.strip() != "=== TOOLS ==="]
    if non_empty_tools:
        lines += ["", "TOOLS_PANEL:"]
        for l in tools_panel:
            lines.append(f"  {l}" if l.strip() else "")

    lines += [
        "",
        f"mode_reponse: {r.get('mode_reponse', '?')}",
        f"detected_layer: {r.get('detected_layer', '?')} (confiance {r.get('confidence', 0):.2f})",
        f"output: {r.get('output', '?')}",
    ]
    return "\n".join(lines)


def format_obsidia_response(r: dict) -> str:
    return "\n".join([
        "================ OBSIDIA_RESPONSE ================", "",
        "INPUT:", f"  {r['raw']}", "",
        "REPONSE:", *("  " + l for l in r["reponse"].splitlines()), "",
        "MODE DE REPONSE:", f"  {r['mode_reponse']}", "",
        "COUCHE:", f"  {r['detected_layer']} (confiance {r['confidence']})", "",
        "CAPACITES / ORGANES MOBILISES:", _fmt_list(r["organes_mobilises"]), "",
        "OUTILS TECHNIQUES MOBILISES:", _fmt_list(r["outils_utilises"]), "",
        "CORPUS UTILISE:", _fmt_list(r["corpus_utilise"]), "",
        "LIMITES:", _fmt_list(r["limites"]), "",
        "PROCHAINE ACTION HUMAINE:", f"  {r['next_human_action']}", "",
        "SORTIE TERMINAL:", f"  {r['output']}", "",
        "==================================================",
    ])


def format_obsidia_response_compact(r: dict) -> str:
    """Vue compacte par defaut (UX V2). LIMITES et NEXT (blocs de securite)
    restent toujours visibles ; le detail complet reste via -v/--verbose."""
    return "\n".join([
        "================ OBSIDIA_RESPONSE ================", "",
        "INPUT:", f"  {r['raw']}", "",
        "REPONSE:", *("  " + l for l in r["reponse"].splitlines()), "",
        "MODE:", f"  {r['mode_reponse']}", "",
        "COUCHE:", f"  {r['detected_layer']} (confiance {r['confidence']})", "",
        "SORTIE:", f"  {r['output']}", "",
        "LIMITES:", _fmt_list(r["limites"]), "",
        "NEXT:", f"  {r['next_human_action']}", "",
        "==================================================",
    ])


_INTERNAL_EXIT = ("exit", "quit")
_INTERNAL_HELP = ("help", "?")
_INTERNAL_CLEAR = ("clear",)


def print_shell_help(registry: dict) -> None:
    """Aide 100% locale, derivee du registry deja charge. Aucun reseau."""
    print("obsidia — terminal non souverain (decision_authority = KX108_ONLY)")
    print("Doctrine : X108 tranche. Sigma guide. Brody explique. Obsidure construit.")
    print("          Domains bridge-only. Memory readonly.")
    print("Sorties possibles : EXECUTE (GET readonly) | COMMANDS | GUIDE | POLICY_DENY | STOP_UNKNOWN")
    print("Couches routables :")
    for layer, spec in (registry.get("layers") or {}).items():
        triggers = ", ".join(str(t) for t in (spec.get("triggers") or [])[:4])
        print(f"  {layer:10} [{spec.get('mode', '?')}] triggers: {triggers}, ...")
    print("Panneau : plan \"<IN>\" | route \"<IN>\" | tools \"<IN>\" | blockers | gates | scope | next")
    print("Commandes internes : help/? , clear, exit/quit. Tout le reste = IN route.")


def _split_panel_line(line: str) -> tuple[str, str] | None:
    parts = line.split(None, 1)
    if parts and parts[0].lower() in PANEL_COMMANDS:
        arg = parts[1].strip().strip('"').strip("'") if len(parts) > 1 else ""
        return parts[0].lower(), arg
    return None


# ─── TUI LAYOUT V1 ──────────────────────────────────────────────────────────

_TUI_MIN_WIDTH = 90


def get_terminal_size_safe() -> tuple[int, int]:
    """Returns (columns, lines). Falls back to (120, 40) on any error."""
    try:
        import shutil as _sh
        s = _sh.get_terminal_size(fallback=(120, 40))
        return max(s.columns, 40), max(s.lines, 10)
    except Exception:
        return 120, 40


def wrap_cell(text: str, width: int, max_lines: int | None = None) -> list[str]:
    """Wrap text to width, return list of strings. Pure, no I/O."""
    lines: list[str] = []
    for raw_line in str(text).splitlines():
        if not raw_line:
            lines.append("")
            continue
        chunk = raw_line.replace("\t", "  ")
        while len(chunk) > width:
            lines.append(chunk[:width])
            chunk = chunk[width:]
        lines.append(chunk)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines - 1]
        lines.append("...")
    return lines


def _tui_pad(s: str, width: int) -> str:
    """Pad or hard-truncate to exactly width chars. ASCII-safe."""
    s = str(s).replace("\t", "  ")
    if len(s) > width:
        return s[:width - 1] + ">"
    return s.ljust(width)


def render_two_pane_layout(
    main_lines: list[str],
    plan_lines: list[str],
    composer_hint: str,
    status_line: str,
    width: int | None = None,
    height: int | None = None,
) -> str:
    """Pure renderer — returns full TUI screen as a string. No I/O."""
    if width is None or height is None:
        w, h = get_terminal_size_safe()
        width = w if width is None else width
        height = h if height is None else height

    plan_w = min(38, max(28, width // 4))
    main_w = max(20, width - plan_w - 7)  # 7 = "| " + " | " + " |"

    composer_h = 3
    top_h = 2
    body_h = max(4, height - composer_h - top_h - 2)

    top_sep = "+" + "-" * (width - 2) + "+"
    top_content = "| " + _tui_pad(status_line, width - 4) + " |"
    col_sep = "+" + "-" * (main_w + 2) + "+" + "-" * (plan_w + 2) + "+"
    bot_sep = "+" + "-" * (width - 2) + "+"

    m = list(main_lines) + [""] * max(0, body_h - len(main_lines))
    p = list(plan_lines) + [""] * max(0, body_h - len(plan_lines))
    m, p = m[:body_h], p[:body_h]

    body_rows = [
        "| " + _tui_pad(ml, main_w) + " | " + _tui_pad(pl, plan_w) + " |"
        for ml, pl in zip(m, p)
    ]

    comp_inner = width - 4
    comp_rows = [
        bot_sep,
        "| " + _tui_pad("COMPOSER", comp_inner) + " |",
        "| " + _tui_pad(composer_hint, comp_inner) + " |",
        bot_sep,
    ]

    parts = [top_sep, top_content, col_sep] + body_rows + comp_rows
    return "\n".join(parts)


# ─── DYNAMIC PANELS AFTER CORE V1 ────────────────────────────────────────────
# OBSIDIA_TERMINAL_DYNAMIC_PANELS_AFTER_CORE_V1
# Choix dynamique du panneau droit apres normalisation core surfaces.
# Ne route pas. Ne decide pas. Ne mute rien.

_DYNAMIC_PANELS_VERSION = "DYNAMIC_PANELS_AFTER_CORE_V1"

_DYNAMIC_PANEL_LAYER_DEFAULTS = {
    "brody": "STATUS",
    "obsidure": "TOOLS",
    "reverse": "PLAN",
    "policy": "TOOLS",
    "terminal": "STATUS",
    "terminal_self": "STATUS",
    "obsidienne": "PROOF",
    "corpus:lean_proofs": "PROOF",
    "audit": "PROOF",
    "gates": "TOOLS",
    "sigma": "PROOF",
    "kernel": "STATUS",
    "domains": "STATUS",
    "memory": "STATUS",
    "oie": "STATUS",
    "live": "STATUS",
    "unknown": "PLAN",
}


def choose_dynamic_right_tab_v1(response: dict) -> str:
    """Choisit l'onglet droit utile sans changer la reponse."""
    if not isinstance(response, dict):
        return "PLAN"

    layer = str(response.get("detected_layer") or "unknown")
    mode = str(response.get("mode_reponse") or "")
    output = str(response.get("output") or "")
    raw = str(response.get("raw") or "").lower()

    if output == "POLICY_DENY" or mode in ("POLICY_DENY", "ANSWER_POLICY_DENY"):
        return "TOOLS"

    if mode == "ANSWER_STATUS":
        return "STATUS"

    if layer == "obsidure":
        if "proof" in raw or "receipt" in raw:
            return "PROOF"
        return "TOOLS"

    if layer == "brody":
        if "proof" in raw:
            return "PROOF"
        return "STATUS"

    return _DYNAMIC_PANEL_LAYER_DEFAULTS.get(layer, "PLAN")


def attach_dynamic_panels_v1(response: dict) -> dict:
    """Attache meta panneau droit. Pure, sans mutation externe."""
    if not isinstance(response, dict):
        return response
    tab = choose_dynamic_right_tab_v1(response)
    response["dynamic_right_tab"] = tab
    response["dynamic_panels"] = {
        "version": _DYNAMIC_PANELS_VERSION,
        "selected": tab,
        "available": ["PLAN", "STATUS", "TOOLS", "PROOF"],
        "manual_override": ["/plan", "/status", "/tools", "/proof"],
        "mutation": "none",
        "subprocess": "none",
        "decision_authority": "KX108_ONLY",
    }
    etat = response.get("etat_technique")
    if isinstance(etat, dict):
        etat.setdefault("dynamic_right_tab", tab)
        etat.setdefault("dynamic_panels", _DYNAMIC_PANELS_VERSION)
    return response


# ─── FIN DYNAMIC PANELS AFTER CORE V1 ────────────────────────────────────────


def extract_main_answer_panel(response: dict, max_lines: int = 60) -> list[str]:
    """Extract main (left) panel content from response dict. Pure.
    V2: utilise main_answer si present, sinon filtre défensif sur reponse.
    Garantie : aucune ligne contenant un _SURFACE_FILTER_TOKEN n'apparaît à gauche."""
    mode = response.get("mode_reponse", "")

    # V2: champ structuré main_answer disponible
    if "main_answer" in response:
        ma = response["main_answer"]
        lines: list[str] = []
        direct = (ma.get("direct") or "").strip()
        if direct:
            lines.extend(direct.splitlines())
        summary = (ma.get("summary") or "").strip()
        if summary:
            lines += ["", summary]
        nexts = [n for n in (ma.get("next") or []) if n]
        if nexts:
            lines.append("")
            for n in nexts[:2]:
                lines.append(f"-> obsidia> {n}")
        return lines[:max_lines] if lines else ["(aucune reponse)"]

    # Legacy : filtre selon le mode
    reponse = response.get("reponse", "")
    next_action = response.get("next_human_action", "")

    if mode in ("ANSWER_POLICY_DENY", "POLICY_DENY"):
        lines = ["[POLICY DENY]", ""] + reponse.splitlines()
        return lines[:max_lines]

    if mode == "ANSWER_STATUS":
        # Filtre complet : legacy ANSWER_STATUS contient les blocs système
        filtered = [l for l in reponse.splitlines()
                    if not any(tok in l for tok in _SURFACE_FILTER_TOKENS)]
        lines = filtered[:35]
    else:
        # ANSWER_LOCAL / ANSWER_PLAN : préserver les corpus answers.
        # Ne supprimer que les headers internes inertes et les blocs [LIMITES]/[NEXT].
        _inert_headers = ("[OBSIDIA RESPONSE]", "CAPABILITY_VIEW")
        raw_lines = reponse.splitlines()
        lines = []
        in_skip_block = False
        for l in raw_lines:
            stripped = l.strip()
            if stripped in ("[LIMITES]", "[NEXT]"):
                in_skip_block = True
                continue
            if in_skip_block:
                if stripped.startswith("  ") or not stripped:
                    continue
                in_skip_block = False
            if any(stripped.startswith(h) for h in _inert_headers):
                continue
            lines.append(l)
        lines = lines[:35]

    if next_action and "LIMITES" not in next_action and "[NEXT]" not in next_action:
        lines += ["", f"-> {next_action}"]
    return lines[:max_lines]


def extract_plan_panel(response: dict, active_tab: str = "PLAN") -> list[str]:
    """Extract right panel content from response dict. Pure.
    active_tab: PLAN (défaut) | STATUS | TOOLS | PROOF"""
    if active_tab == "STATUS":
        return extract_status_panel(response)
    if active_tab == "TOOLS":
        return extract_tools_panel(response)
    if active_tab == "PROOF":
        return extract_proof_panel(response)

    # Onglet PLAN (défaut)
    layer = response.get("detected_layer", "?")
    mode = response.get("mode_reponse", "?")
    output = response.get("output", "?")
    conf = response.get("confidence", 0.0)
    limites = response.get("limites", [])
    next_suggestions = response.get("next_suggestions", [])
    next_action = response.get("next_human_action", "")
    politique = response.get("politique", [])

    if mode == "ANSWER_STATUS":
        status_label = "PARTIAL"
    elif mode == "ANSWER_POLICY_DENY":
        status_label = "DENIED"
    else:
        status_label = "ROUTED"

    lines = [
        "=== PLAN ===", "",
        f"layer: {layer}",
        f"mode:  {mode[:14] if len(mode) > 14 else mode}",
        f"status: {status_label}",
        f"out:   {output}",
        f"conf:  {conf:.2f}",
    ]
    if next_suggestions:
        lines += ["", "NEXT:"]
        for n in next_suggestions[:2]:
            lines.append(f"  {str(n)[:26]}")
    elif next_action:
        lines += ["", "NEXT:", "  " + str(next_action)[:26]]
    if politique:
        lines += ["", "POLITIQUE:"]
        for p in politique[:3]:
            lines.append(f"  {str(p)[:26]}: forbidden")
    lines += ["", "AUTORITE:", "  X108=FINAL", "  no_auto_act"]
    if limites:
        lines += ["", "LIMITES:"]
        for lim in limites[:2]:
            lines.append("  " + str(lim)[:26])
    return lines


_SUITE_WORDS = frozenset({"suite", "continue", "suivant", "next"})
_TAB_COMMANDS = {"/plan": "PLAN", "/status": "STATUS", "/tools": "TOOLS", "/proof": "PROOF"}


def interactive_tui_shell(registry: dict) -> int:
    """TUI interactive shell with two-pane layout. Falls back to plain if too small."""
    session_id = uuid.uuid4().hex[:8]
    w, h = get_terminal_size_safe()
    if w < _TUI_MIN_WIDTH:
        print(f"[TUI] Terminal trop petit ({w}<{_TUI_MIN_WIDTH}). Mode plain.")
        return interactive_shell(registry)

    _welcome_main = [
        "OBSIDIA TERMINAL V2 — TUI SURFACE SEPARATION",
        "Terminal non souverain. X108 = autorite finale.",
        "",
        "Tapez votre demande ou une commande :",
        "  <votre demande>         routing automatique",
        "  capabilities <couche>   surface d'une couche",
        "  runtime                 sonde services",
        "  /help                   aide complete",
        "  /plan /status /tools /proof  onglets droite",
        "  /plain                  bascule en mode plain",
        "  exit                    quitter",
        "",
        "Couches disponibles :",
        "  brody, obsidure, sigma, memory, oie,",
        "  thermo, lean, domains, gates, kernel,",
        "  terminal_self, audit, live",
    ]
    _welcome_plan = [
        "=== SESSION ===", "",
        f"id: {session_id}", "mode: TUI V2",
        "", "=== DOCTRINE ===", "",
        "X108 = autorite", "readonly",
        "no_auto_act", "no_subprocess",
        "", "=== ONGLETS ===", "",
        "/plan /status", "/tools /proof",
    ]

    main_lines: list[str] = list(_welcome_main)
    plan_lines: list[str] = list(_welcome_plan)
    last_resp: dict | None = None
    last_plan: dict | None = None
    current_layer = "?"
    active_right_tab = "PLAN"

    while True:
        w, h = get_terminal_size_safe()
        if w < _TUI_MIN_WIDTH:
            print("[TUI] Terminal trop petit. Mode plain.")
            return interactive_shell(registry)

        plan_w_inner = min(38, max(28, w // 4))
        main_w_inner = max(20, w - plan_w_inner - 7)

        m_wrapped: list[str] = []
        for line in main_lines:
            m_wrapped.extend(wrap_cell(line, main_w_inner))

        p_wrapped: list[str] = []
        for line in plan_lines:
            p_wrapped.extend(wrap_cell(line, plan_w_inner))

        tab_hint = f"[{active_right_tab}]"
        status_line = (
            f" OBSIDIA | session {session_id} | "
            f"couche: {current_layer} | tab:{tab_hint} | X108=AUTHORITY"
        )
        composer_hint = (
            " /help  /plain  /runtime  "
            "/plan  /status  /tools  /proof  /clear  exit"
        )

        screen = render_two_pane_layout(
            main_lines=m_wrapped, plan_lines=p_wrapped,
            composer_hint=composer_hint, status_line=status_line,
            width=w, height=h,
        )

        print("\033[2J\033[H", end="", flush=True)
        print(screen)

        try:
            raw = input("obsidia> ")
        except (EOFError, KeyboardInterrupt):
            print()
            print("session fermee.")
            return 0

        line = raw.strip()
        if not line:
            continue
        low = line.lower()

        if low in _INTERNAL_EXIT:
            print("\033[2J\033[H", end="")
            print("session fermee.")
            return 0

        if low in ("/help",) or low in _INTERNAL_HELP:
            help_lines = ["=== AIDE OBSIDIA TUI ===", ""]
            for ln, spec in (registry.get("layers") or {}).items():
                trgs = ", ".join(str(t) for t in (spec.get("triggers") or [])[:3])
                help_lines.append(f"  {ln}: {trgs}...")
            help_lines += [
                "", "Commandes :", "  /help  /plan  /status  /tools  /proof",
                "  /plain  /runtime  /clear  exit",
                "", "Onglets droite :",
                "  /plan    — routage et plan actif",
                "  /status  — etat technique (services, couche)",
                "  /tools   — outils autorises/interdits",
                "  /proof   — etat preuves/corpus",
            ]
            main_lines = help_lines
            plan_lines = ["=== PLAN ===", "", "mode: GUIDE", "out: HELP",
                          "", "AUTORITE:", "  X108=FINAL"]
            current_layer = "terminal_self"
            active_right_tab = "PLAN"
            continue

        if low == "/plain":
            print("\033[2J\033[H", end="")
            print("Mode plain.")
            return interactive_shell(registry)

        if low in ("/clear",) or low in _INTERNAL_CLEAR:
            main_lines = list(_welcome_main)
            plan_lines = list(_welcome_plan)
            current_layer = "?"
            active_right_tab = "PLAN"
            continue

        if low == "/runtime":
            line = "runtime"
            low = "runtime"

        # Onglets du panneau droit — ne changent que le panneau droit, pas la réponse
        if low in _TAB_COMMANDS:
            active_right_tab = _TAB_COMMANDS[low]
            if last_resp:
                plan_lines = extract_plan_panel(last_resp, active_right_tab)
            else:
                plan_lines = [
                    f"=== {active_right_tab} ===", "",
                    "(pas encore de reponse)",
                    "", "Tapez une question d'abord.",
                ]
            continue

        # Commande suite/continue/suivant/next
        if low in _SUITE_WORDS:
            if last_resp:
                plan_lines = extract_plan_panel(last_resp, active_right_tab)
                main_lines = [
                    "Voici la suite disponible.",
                    "",
                    "Utilisez les onglets pour naviguer :",
                    "  /plan    routage et plan actif",
                    "  /status  etat technique",
                    "  /tools   outils autorises/interdits",
                    "  /proof   etat preuves/corpus",
                ]
            else:
                main_lines = [
                    "J'ai besoin de preciser quelle suite :",
                    "plan, status, tools ou proof.",
                    "",
                    "-> /plan",
                    "-> /status",
                    "-> /tools",
                    "-> /proof",
                ]
            continue

        panel = _split_panel_line(line)
        if panel:
            text, receipt, plan = handle_plan_command(panel[0], panel[1], registry, last_plan)
            if plan is not None:
                last_plan = plan
            if receipt is not None:
                receipt["session_id"] = session_id
                write_receipt(registry, receipt)
            main_lines = text.splitlines()
            plan_lines = ["=== PANEL ===", "", f"cmd: {panel[0]}", f"arg: {panel[1]}",
                          "", "AUTORITE:", "  X108=FINAL"]
            active_right_tab = "PLAN"
            continue

        resp = answer_router(line, registry)
        resp["session_id"] = session_id
        write_receipt(registry, resp)
        last_resp = resp
        last_plan = build_active_plan(line, registry)
        current_layer = resp.get("detected_layer", "?")
        # Auto-tab : ANSWER_STATUS -> STATUS, sinon PLAN
        active_right_tab = choose_dynamic_right_tab_v1(resp)
        main_lines = extract_main_answer_panel(resp)
        plan_lines = extract_plan_panel(resp, active_right_tab)


# ─── FIN TUI LAYOUT V2 ───────────────────────────────────────────────────────


def interactive_shell(registry: dict) -> int:
    session_id = uuid.uuid4().hex[:8]
    last_plan: dict | None = None
    print("obsidia terminal — non souverain, readonly. X108 decide.")
    print(f"session {session_id} — tape 'help' pour l'aide, 'exit' pour sortir.")
    while True:
        try:
            raw = input("obsidia> ")
        except (EOFError, KeyboardInterrupt):
            print()
            print("session fermee.")
            return 0
        line = raw.strip()
        if not line:
            continue
        low = line.lower()
        verbose_mode = False
        if low.startswith(("-v ", "--verbose ", "verbose ")):
            parts_v = line.split(None, 1)
            line = parts_v[1] if len(parts_v) > 1 else ""
            if not line:
                print('GUIDE: -v "<IN>"')
                continue
            verbose_mode = True
            low = line.lower()
        if low in _INTERNAL_EXIT:
            print("session fermee.")
            return 0
        if low in _INTERNAL_HELP:
            print_shell_help(registry)
            continue
        if low in _INTERNAL_CLEAR:
            # ANSI clear uniquement — pas de cls, pas de subprocess, etat intact.
            print("\033[2J\033[H", end="")
            continue
        panel = _split_panel_line(line)
        if panel:
            text, receipt, plan = handle_plan_command(panel[0], panel[1], registry, last_plan)
            if plan is not None:
                last_plan = plan
            if receipt is not None:
                receipt["session_id"] = session_id
                write_receipt(registry, receipt)
            print(text)
            continue
        first = line.split(None, 1)
        cmd0 = first[0].lower()
        if cmd0 in ("raw", "json") or low == "doctor":
            target = line if low == "doctor" else (
                first[1].strip().strip('"').strip("'") if len(first) > 1 else "")
            if not target:
                print('GUIDE: raw/json "<IN>"')
                continue
            result = handle(target, registry)
            result["session_id"] = session_id
            receipt_path = write_receipt(registry, result)
            result["receipt"] = str(receipt_path.relative_to(REPO_ROOT))
            print(json.dumps(result, indent=2, ensure_ascii=False))
            continue
        if cmd0 == "answer":
            line = first[1].strip().strip('"').strip("'") if len(first) > 1 else ""
            if line.lower().startswith(("-v ", "--verbose ")):
                verbose_mode = True
                line = line.split(None, 1)[1] if len(line.split(None, 1)) > 1 else ""
            if not line:
                print('GUIDE: answer "<IN>"')
                continue
        # IN libre -> moteur universel OBSIDIA_ANSWER_ROUTER
        resp = answer_router(line, registry)
        resp["session_id"] = session_id
        write_receipt(registry, resp)
        print(format_obsidia_response(resp) if verbose_mode
              else format_obsidia_response_compact(resp))



# ─── TERMINAL OPERATOR TASK CARD V1 SAFE ─────────────────────────────────────
# OBSIDIA_TERMINAL_OPERATOR_TASK_CARD_V1_SAFE
# Produit une carte opérateur Obsidure. Affichage uniquement.
# Pas de lancement de processus, pas d'apply, pas de commit, pas de push.

_OPERATOR_CODE_WORDS_V1 = frozenset({
    "code", "coder", "patch", "corrige", "correction", "fix", "implemente",
    "implémente", "branche", "connecte", "relie", "outil", "tools", "skill",
    "skills", "proposal", "propose",
})

_OPERATOR_LEAN_WORDS_V1 = frozenset({
    "lean", "preuve", "preuves", "theoreme", "théorème", "theoremes",
    "théorèmes", "proof", "proposition", "lemma", "peripheral",
    "périphérique",
})

_OPERATOR_DOMAIN_WORDS_V1 = {
    "LEAN": _OPERATOR_LEAN_WORDS_V1,
    "BANK": frozenset({"bank", "banque", "bancaire", "paiement", "fraude"}),
    "TRADING": frozenset({"trading", "bourse", "market", "flashcrash", "ordre"}),
    "GPS": frozenset({"gps", "gnss", "aviation", "robo", "spoofing", "terrain"}),
    "ECOM": frozenset({"ecom", "ecommerce", "shop", "boutique", "produit"}),
    "SRL": frozenset({"srl", "session", "history", "historique", "memoire", "mémoire"}),
}

def _operator_words_v1(raw: str) -> set[str]:
    return set(re.findall(r"[a-zA-ZÀ-ÿ0-9_+-]+", normalize(raw).lower()))

def _operator_domain_v1(raw: str) -> str | None:
    words = _operator_words_v1(raw)
    for domain, keys in _OPERATOR_DOMAIN_WORDS_V1.items():
        if words & keys:
            return domain
    return None

def _operator_kind_v1(raw: str) -> str:
    words = _operator_words_v1(raw)
    if words & _OPERATOR_LEAN_WORDS_V1:
        return "LEAN_SANDBOX_PREP"
    if {"branche", "connecte", "relie"} & words:
        return "READONLY_WIRING_PREP"
    if words & _OPERATOR_CODE_WORDS_V1:
        return "PYTHON_PATCH_PROPOSAL_PREP"
    return "OBSIDURE_PROPOSAL_PREP"

def _operator_scope_v1(domain: str | None, kind: str) -> list[str]:
    if domain == "LEAN" or kind == "LEAN_SANDBOX_PREP":
        return [
            "periphery/lean_sandbox/",
            "proofs/lean/Obsidia/Peripheral/        # cible seulement après validation humaine",
            "proofs/lean/Obsidia/GeneratedPeripheral/ # cible seulement après proposal validé",
            "_PATCH_PROPOSALS/<id>/",
        ]
    if kind == "READONLY_WIRING_PREP":
        return [
            "scripts/obsidia_cli.py",
            "scripts/obsidia_registry.yaml",
            "scripts/obsidure_cli.py",
            "periphery/agents/agent_obsidure.py",
            "_PATCH_PROPOSALS/<id>/",
        ]
    return [
        "scripts/obsidure_cli.py",
        "periphery/agents/agent_obsidure.py",
        "_PATCH_PROPOSALS/<id>/",
    ]

def _operator_quote_ps_v1(value: str) -> str:
    return '"' + value.replace("`", "``").replace('"', '`"') + '"'




# ─── TERMINAL INPUT SKILL RESOLVER V1 READONLY ───────────────────────────────
# OBSIDIA_TERMINAL_INPUT_SKILL_RESOLVER_V1_READONLY
# Les skills/protocoles servent à résoudre le IN comme organes consultatifs.
# Ils ne sont jamais souverains : aucun apply, aucun subprocess, aucun ACT.

def _skill_resolver_repo_root_v1():
    from pathlib import Path as _Path
    return _Path(__file__).resolve().parent.parent

def _skill_resolver_roots_v1() -> list[str]:
    return [
        ".claude/skills",
        ".agents/skills",
        "docs/protocols",
        "docs/runtime/OBSIDIA_AGENT_OBSIDURE_MANUAL_V1.md",
    ]

def _skill_resolver_rel_v1(path) -> str:
    root = _skill_resolver_repo_root_v1()
    try:
        return path.resolve().relative_to(root).as_posix()
    except Exception:
        return str(path).replace("\\", "/")

def _skill_resolver_read_text_v1(path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:6000]
    except Exception:
        return ""

def _skill_resolver_inventory_v1() -> list[dict]:
    root = _skill_resolver_repo_root_v1()
    items: list[dict] = []

    for rel_root in (".claude/skills", ".agents/skills"):
        base = root / rel_root
        if not base.exists():
            continue
        for skill_file in sorted(base.glob("*/SKILL.md")):
            items.append({
                "category": "skill",
                "name": skill_file.parent.name,
                "path": _skill_resolver_rel_v1(skill_file),
                "root": rel_root,
                "profile_text": _skill_resolver_read_text_v1(skill_file),
            })

    proto_root = root / "docs/protocols"
    if proto_root.exists():
        for proto_file in sorted(proto_root.glob("*.md")):
            items.append({
                "category": "protocol",
                "name": proto_file.stem,
                "path": _skill_resolver_rel_v1(proto_file),
                "root": "docs/protocols",
                "profile_text": _skill_resolver_read_text_v1(proto_file),
            })

    manual = root / "docs/runtime/OBSIDIA_AGENT_OBSIDURE_MANUAL_V1.md"
    if manual.exists():
        items.append({
            "category": "protocol",
            "name": "OBSIDIA_AGENT_OBSIDURE_MANUAL_V1",
            "path": _skill_resolver_rel_v1(manual),
            "root": "docs/runtime",
            "profile_text": _skill_resolver_read_text_v1(manual),
        })

    return items

def _skill_resolver_words_v1(raw: str) -> set[str]:
    return set(re.findall(r"[a-zA-ZÀ-ÿ0-9_+-]+", normalize(raw).lower()))

def _skill_resolver_pick_by_names_v1(names: list[str], category: str) -> list[str]:
    inventory = _skill_resolver_inventory_v1()
    out: list[str] = []
    seen: set[str] = set()

    for wanted in names:
        wanted_l = wanted.lower()
        matches = [
            item for item in inventory
            if item["category"] == category
            and (
                item["name"].lower() == wanted_l
                or wanted_l in item["path"].lower()
            )
        ]
        matches.sort(key=lambda item: (
            0 if item["path"].startswith(".claude/skills/") else 1,
            item["path"],
        ))
        for item in matches:
            path = item["path"]
            if path not in seen:
                out.append(path)
                seen.add(path)
                break

    return out

def _skill_resolver_score_inventory_v1(raw: str, category: str) -> list[str]:
    words = _skill_resolver_words_v1(raw)
    if not words:
        return []

    scored: list[tuple[int, str]] = []
    for item in _skill_resolver_inventory_v1():
        if item["category"] != category:
            continue

        hay = normalize(
            item["name"] + " " + item["path"] + " " + item.get("profile_text", "")
        ).lower()

        score = 0
        for word in words:
            if len(word) < 3:
                continue
            if word in hay:
                score += 1

        # pondérations de routage organique
        name = item["name"].lower()
        if "lean" in words or "preuve" in words or "theoreme" in words or "théorème" in words:
            if name in ("proof-sentinel", "freeze-guardian"):
                score += 4
            if "kernel_boundary" in item["path"].lower():
                score += 3

        if "branche" in words or "connecte" in words or "relie" in words or "wiring" in words:
            if name in ("module-mapper", "graph-calibrator-obsidia", "terminal-builder"):
                score += 4

        if "terminal" in words:
            if name in ("terminal-builder", "agent-router-obsidia"):
                score += 4

        if "sigma" in words:
            if name == "sigma-surgeon" or "SIGMA" in item["path"]:
                score += 4

        if "memory" in words or "mémoire" in words or "srl" in words:
            if name in ("context-keeper", "wiki-brain-bridge"):
                score += 4

        if score > 0:
            scored.append((score, item["path"]))

    scored.sort(key=lambda x: (-x[0], x[1]))
    out: list[str] = []
    seen: set[str] = set()
    for _, path in scored:
        if path not in seen:
            out.append(path)
            seen.add(path)
        if len(out) >= 8:
            break

    return out

def _skill_resolver_skill_paths_v1(domain: str | None, kind: str, raw: str = "") -> list[str]:
    names = [
        "agent-router-obsidia",
        "read-only-inspector",
        "terminal-builder",
    ]

    if domain == "LEAN" or kind == "LEAN_SANDBOX_PREP":
        names += ["proof-sentinel", "freeze-guardian"]

    if kind == "READONLY_WIRING_PREP":
        names += ["module-mapper", "graph-calibrator-obsidia", "freeze-guardian"]

    if domain == "SRL":
        names += ["context-keeper", "wiki-brain-bridge"]

    if domain in ("BANK", "TRADING", "GPS") or kind == "PYTHON_PATCH_PROPOSAL_PREP":
        names += ["sigma-surgeon", "token-guard"]

    base = _skill_resolver_pick_by_names_v1(names, "skill")
    dynamic = _skill_resolver_score_inventory_v1(raw, "skill")

    out: list[str] = []
    seen: set[str] = set()
    for path in [*base, *dynamic]:
        if path not in seen:
            out.append(path)
            seen.add(path)
    return out

def _skill_resolver_protocol_paths_v1(domain: str | None, kind: str, raw: str = "") -> list[str]:
    names = [
        "OBSIDURE_APPLY_PROTOCOL",
        "OBSIDIA_OPERATOR_DOCTRINE",
        "OBSIDIA_VERIFICATION_LOOP_PROTOCOL",
        "OBSIDIA_AGENT_OBSIDURE_MANUAL_V1",
    ]

    if domain == "LEAN" or kind == "LEAN_SANDBOX_PREP":
        names += ["KERNEL_BOUNDARY_CHECK_PROTOCOL"]

    if kind == "READONLY_WIRING_PREP":
        names += ["KERNEL_BOUNDARY_CHECK_PROTOCOL", "SIGMA_GUIDANCE_V0_APPLY_PROTOCOL"]

    if domain in ("BANK", "TRADING", "GPS"):
        names += ["OBSIDIA_PREMORTEM_PROTOCOL", "SIGMA_GUIDANCE_V0_APPLY_PROTOCOL"]

    base = _skill_resolver_pick_by_names_v1(names, "protocol")
    dynamic = _skill_resolver_score_inventory_v1(raw, "protocol")

    out: list[str] = []
    seen: set[str] = set()
    for path in [*base, *dynamic]:
        if path not in seen:
            out.append(path)
            seen.add(path)
    return out

def resolve_terminal_input_with_skills_v1(raw: str) -> dict:
    objective = (raw or "").strip()
    domain = _operator_domain_v1(objective)
    kind = _operator_kind_v1(objective)

    skill_paths = _skill_resolver_skill_paths_v1(domain, kind, objective)
    protocol_paths = _skill_resolver_protocol_paths_v1(domain, kind, objective)

    route = "OBSIDURE"
    if kind == "READONLY_WIRING_PREP":
        route = "READONLY_WIRING"
    if domain == "LEAN" or kind == "LEAN_SANDBOX_PREP":
        route = "LEAN_SANDBOX_OBSIDURE"
    if domain in ("BANK", "TRADING", "GPS"):
        route = f"{domain}_DOMAIN_SUPPORT"
    if domain == "SRL":
        route = "MEMORY_SRL_SUPPORT"

    return {
        "version": "OBSIDIA_TERMINAL_INPUT_SKILL_RESOLVER_V1_READONLY",
        "mode": "READONLY_BACKGROUND_SUPPORT_NO_AUTHORITY",
        "decision_authority": "KX108_ONLY",
        "emits_act": False,
        "kernel_mutation": False,
        "memory_write": False,
        "input": objective,
        "resolved_route": route,
        "resolved_kind": kind,
        "resolved_domain": domain or "AUTO",
        "selected_skills": skill_paths,
        "selected_protocols": protocol_paths,
        "policy": [
            "skills are advisory organs only",
            "no background execution",
            "no subprocess",
            "no apply",
            "no commit",
            "no push",
            "no ALLOW/BLOCK/HOLD/ACT emission",
        ],
    }

def format_terminal_skill_inventory_v1(raw_filter: str = "") -> str:
    needle = normalize(raw_filter).lower().strip()
    inventory = _skill_resolver_inventory_v1()

    if needle:
        inventory = [
            item for item in inventory
            if needle in item["name"].lower() or needle in item["path"].lower()
        ]

    lines = [
        "================ OBSIDIA TERMINAL SKILL RESOLVER ================",
        "",
        "VERSION: OBSIDIA_TERMINAL_INPUT_SKILL_RESOLVER_V1_READONLY",
        "MODE: READONLY_BACKGROUND_SUPPORT_NO_AUTHORITY",
        "DECISION_AUTHORITY: KX108_ONLY",
        "EMITS_ACT: False",
        "KERNEL_MUTATION: False",
        "MEMORY_WRITE: False",
        "",
        "ROOTS:",
    ]
    lines.extend(f"  - {root}" for root in _skill_resolver_roots_v1())
    lines += ["", "INVENTORY:"]

    if inventory:
        for item in inventory:
            lines.append(f"  - [{item['category']}] {item['path']}")
    else:
        lines.append("  - Aucun skill/protocole trouvé pour ce filtre.")

    lines += [
        "",
        "POLICY:",
        "  - advisory organs only",
        "  - no background execution",
        "  - no process launch",
        "  - no apply",
        "  - no commit",
        "  - no push",
        "  - no kernel/X108 mutation",
        "",
        "===============================================================",
    ]
    return "\n".join(lines)

def format_terminal_input_resolution_v1(raw: str) -> str:
    resolved = resolve_terminal_input_with_skills_v1(raw)
    lines = [
        "================ OBSIDIA TERMINAL INPUT RESOLUTION ================",
        "",
        f"VERSION: {resolved['version']}",
        f"MODE: {resolved['mode']}",
        f"DECISION_AUTHORITY: {resolved['decision_authority']}",
        "",
        "BOUNDARY:",
        f"  emits_act={resolved['emits_act']}",
        f"  kernel_mutation={resolved['kernel_mutation']}",
        f"  memory_write={resolved['memory_write']}",
        "",
        "IN:",
        f"  {resolved['input']}",
        "",
        "RESOLUTION:",
        f"  route={resolved['resolved_route']}",
        f"  kind={resolved['resolved_kind']}",
        f"  domain={resolved['resolved_domain']}",
        "",
        "SKILLS CONSULTES EN READONLY:",
    ]
    lines.extend(f"  - {x}" for x in resolved["selected_skills"])
    lines += ["", "PROTOCOLES CONSULTES EN READONLY:"]
    lines.extend(f"  - {x}" for x in resolved["selected_protocols"])
    lines += ["", "POLICY:"]
    lines.extend(f"  - {x}" for x in resolved["policy"])
    lines += [
        "",
        "PLAN_STATUS: ADVISORY_ONLY_WAITING_FOR_HUMAN",
        "================================================================",
    ]
    return "\n".join(lines)

# OBSIDIA_TERMINAL_OPERATOR_OBJECTIVE_PREFIX_SKILL_HINTS_V1
def _operator_enriched_objective_v1(objective: str, domain: str | None, kind: str) -> str:
    base = (objective or "").strip() or "préparer une task card Obsidure"
    if domain == "LEAN" or kind == "LEAN_SANDBOX_PREP":
        return (
            "Objectif : LEAN_SANDBOX. "
            "Créer/adapter un théorème périphérique Obsidia en sandbox uniquement. "
            "Ne pas toucher le kernel X108. Ne pas modifier server.kernel.sealed. "
            "Sortie attendue : proposal/dry-run HUMAN_APPROVED_WRITE. "
            "Demande utilisateur : " + base
        )
    if kind == "READONLY_WIRING_PREP":
        return (
            "Objectif : READONLY_WIRING_PREP. "
            "Auditer ou préparer un branchement readonly entre couches Obsidia. "
            "Aucun apply automatique. Aucun commit. Aucun push. "
            "Sortie attendue : proposal commands-only HUMAN_APPROVED_WRITE. "
            "Demande utilisateur : " + base
        )
    if kind == "PYTHON_PATCH_PROPOSAL_PREP":
        return (
            "Objectif : PYTHON_PATCH_PROPOSAL. "
            "Préparer un patch périphérique Python/JSON/MD limité au scope autorisé. "
            "Aucun kernel mutation. Aucun apply automatique. "
            "Sortie attendue : proposal HUMAN_APPROVED_WRITE. "
            "Demande utilisateur : " + base
        )
    return (
        "Objectif : OBSIDURE_PROPOSAL_PREP. "
        "Analyser la demande et préparer uniquement une proposition bornée. "
        "Aucune mutation automatique. "
        "Demande utilisateur : " + base
    )

def _operator_skill_hints_v1(domain: str | None, kind: str, raw: str = "") -> list[str]:
    return _skill_resolver_skill_paths_v1(domain, kind, raw)

def _operator_protocol_hints_v1(domain: str | None, kind: str, raw: str = "") -> list[str]:
    return _skill_resolver_protocol_paths_v1(domain, kind, raw)

def build_obsidure_operator_task_card_v1(raw: str) -> dict:
    objective = (raw or "").strip() or "préparer une task card Obsidure"
    domain = _operator_domain_v1(objective)
    kind = _operator_kind_v1(objective)
    enriched_objective = _operator_enriched_objective_v1(objective, domain, kind)
    task_id = "op_" + uuid.uuid5(uuid.NAMESPACE_URL, "obsidia-operator|" + enriched_objective).hex[:12]

    cmd = ["python", "scripts/obsidure_cli.py", "--objective", _operator_quote_ps_v1(enriched_objective)]
    if domain:
        cmd.extend(["--domain", domain])

    tests = [
        "python -m py_compile scripts/obsidia_cli.py scripts/obsidure_cli.py periphery/agents/agent_obsidure.py",
        "python -m pytest tests/gates/test_obsidia_obsidure_bridge_v1.py -q",
        "python -m pytest tests/gates/test_obsidia_operator_task_card_v1.py -q",
    ]
    if domain == "LEAN" or kind == "LEAN_SANDBOX_PREP":
        tests.append("Push-Location proofs/lean ; lake build Obsidia.Peripheral ; Pop-Location")

    return {
        "task_card_id": task_id,
        "version": "OBSIDIA_TERMINAL_OPERATOR_TASK_CARD_V1_SAFE",
        "mode": "COMMANDS_ONLY",
        "decision_authority": "KX108_ONLY",
        "emits_act": False,
        "memory_write": False,
        "kernel_mutation": False,
        "x108_mutation": False,
        "kind": kind,
        "domain": domain or "AUTO",
        "objective": objective,
        "enriched_objective": enriched_objective,
        "input_resolution": resolve_terminal_input_with_skills_v1(objective),
        "skill_hints": _operator_skill_hints_v1(domain, kind, objective),
        "protocol_hints": _operator_protocol_hints_v1(domain, kind, objective),
        "obsidure_dry_run_command": " ".join([*cmd, "--dry-run"]),
        "obsidure_proposal_command": " ".join(cmd),
        "candidate_scope": _operator_scope_v1(domain, kind),
        "gates": [
            "python scripts/gates/obsidia_commit_scope_guard.py --allow <fichiers_du_scope>",
            "python scripts/gates/obsidia_kernel_boundary_check.py --staged-only",
            "python scripts/gates/obsidia_sigma_non_sovereignty_check.py",
            "python scripts/gates/obsidia_lean_manifest_guard.py",
            "python -m pytest tests/gates/ -q",
        ],
        "tests": tests,
        "forbidden": [
            "no process launch from terminal",
            "no automatic apply",
            "no automatic commit",
            "no automatic push",
            "no kernel/X108 mutation",
            "no memory write",
        ],
        "next_human_action": "lancer la commande DRY_RUN si tu veux préparer un proposal Obsidure",
    }

def format_obsidure_operator_task_card_v1(raw: str) -> str:
    card = build_obsidure_operator_task_card_v1(raw)
    lines = [
        "================ OBSIDIA OPERATOR TASK CARD ================",
        "",
        f"VERSION: {card['version']}",
        f"TASK_ID: {card['task_card_id']}",
        f"MODE: {card['mode']}",
        f"DECISION_AUTHORITY: {card['decision_authority']}",
        "",
        "BOUNDARY:",
        f"  emits_act={card['emits_act']}",
        f"  memory_write={card['memory_write']}",
        f"  kernel_mutation={card['kernel_mutation']}",
        f"  x108_mutation={card['x108_mutation']}",
        "",
        "OBJECTIVE:",
        f"  {card['objective']}",
        "",
        "OBJECTIVE ENRICHI POUR OBSIDURE:",
        f"  {card['enriched_objective']}",
        "",
        "CLASSIFICATION:",
        f"  kind={card['kind']}",
        f"  domain={card['domain']}",
        "",
        "INPUT_RESOLUTION_BY_SKILLS:",
        f"  resolver={card['input_resolution']['version']}",
        f"  mode={card['input_resolution']['mode']}",
        f"  route={card['input_resolution']['resolved_route']}",
        "  authority=NONE_SKILLS_ARE_ADVISORY_ONLY",
        "",
        "COMMANDS PROPOSEES — NON EXECUTEES PAR LE TERMINAL:",
        f"  DRY_RUN:  {card['obsidure_dry_run_command']}",
        f"  PROPOSAL: {card['obsidure_proposal_command']}",
        "",
        "SCOPE CANDIDAT — A CONFIRMER HUMAINEMENT:",
    ]
    lines.extend(f"  - {x}" for x in card["candidate_scope"])
    lines += ["", "SKILLS MOBILISABLES:"]
    lines.extend(f"  - {x}" for x in card["skill_hints"])
    lines += ["", "PROTOCOLES MOBILISABLES:"]
    lines.extend(f"  - {x}" for x in card["protocol_hints"])
    lines += ["", "GATES:"]
    lines.extend(f"  - {x}" for x in card["gates"])
    lines += ["", "TESTS CIBLES:"]
    lines.extend(f"  - {x}" for x in card["tests"])
    lines += ["", "INTERDITS:"]
    lines.extend(f"  - {x}" for x in card["forbidden"])
    lines += [
        "",
        f"NEXT_HUMAN_ACTION: {card['next_human_action']}",
        "",
        "PLAN_STATUS: WAITING_FOR_HUMAN",
        "============================================================",
    ]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if argv and argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    registry = load_registry(REGISTRY_PATH)
    if argv and argv[0].lower() in ("skills", "skill", "skill-resolver", "skill-inventory", "protocols"):
        raw_filter = " ".join(argv[1:]).strip().strip('"').strip("'")
        print(format_terminal_skill_inventory_v1(raw_filter))
        return 0
    if argv and argv[0].lower() in ("resolve", "resolver", "input-resolve", "skill-resolve"):
        raw_input = " ".join(argv[1:]).strip().strip('"').strip("'")
        print(format_terminal_input_resolution_v1(raw_input))
        return 0
    if argv and argv[0].lower() in ("operator", "task", "task-card", "obsidure-task"):
        raw_operator = " ".join(argv[1:]).strip().strip('"').strip("'")
        print(format_obsidure_operator_task_card_v1(raw_operator))
        return 0
    # Mode flags : --tui (layout deux panneaux) | --plain (shell texte brut)
    if argv and argv[0] == "--tui":
        return interactive_tui_shell(registry)
    if argv and argv[0] == "--plain":
        return interactive_shell(registry)
    verbose_mode = False
    if argv and argv[0] in ("-v", "--verbose"):
        verbose_mode = True
        argv = argv[1:]
    if not argv:
        return interactive_tui_shell(registry)
    if argv[0].lower() in PANEL_COMMANDS:
        arg = " ".join(argv[1:]).strip().strip('"').strip("'")
        text, receipt, _plan = handle_plan_command(argv[0], arg, registry)
        if receipt is not None:
            write_receipt(registry, receipt)
        print(text)
        return 0
    cmd0 = argv[0].lower()
    raw = " ".join(argv)
    if cmd0 in ("raw", "json") or normalize(raw) == "doctor":
        target = raw if normalize(raw) == "doctor" else (
            " ".join(argv[1:]).strip().strip('"').strip("'"))
        if not target:
            print('GUIDE: obsidia raw "<IN>"')
            return 0
        result = handle(target, registry)
        receipt_path = write_receipt(registry, result)
        result["receipt"] = str(receipt_path.relative_to(REPO_ROOT))
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    if cmd0 == "answer":
        rest = argv[1:]
        if rest and rest[0] in ("-v", "--verbose"):
            verbose_mode = True
            rest = rest[1:]
        raw = " ".join(rest).strip().strip('"').strip("'")
        if not raw:
            print('GUIDE: obsidia answer "<IN>"')
            return 0
    # IN libre -> moteur universel OBSIDIA_ANSWER_ROUTER
    resp = answer_router(raw, registry)
    write_receipt(registry, resp)
    if verbose_mode:
        print(format_obsidia_response(resp))
    else:
        print(format_surface_response(resp))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
