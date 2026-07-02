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

import json
import re
import sys
import unicodedata
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
    for kw in registry.get("policy", {}).get("deny_keywords", []) or []:
        k = str(kw).lower().strip()
        if k and k in normalized:
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
        "organes_interdits": list(organes.get("interdits", [])) + list(ORGANES_INTERDITS_TOUJOURS),
        "outils_utilises": tooling["utilises"],
        "outils_mobilisables": tooling["mobilisables"],
        "outils_exclus": list(tooling["exclus"]) + list(FORBIDDEN_ALWAYS),
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
        result = handle(line, registry)
        result["session_id"] = session_id
        receipt_path = write_receipt(registry, result)
        result["receipt"] = str(receipt_path.relative_to(REPO_ROOT))
        print(json.dumps(result, indent=2, ensure_ascii=False))


def main(argv: list[str]) -> int:
    if argv and argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    registry = load_registry(REGISTRY_PATH)
    if not argv:
        return interactive_shell(registry)
    if argv[0].lower() in PANEL_COMMANDS:
        arg = " ".join(argv[1:]).strip().strip('"').strip("'")
        text, receipt, _plan = handle_plan_command(argv[0], arg, registry)
        if receipt is not None:
            write_receipt(registry, receipt)
        print(text)
        return 0
    raw = " ".join(argv)
    result = handle(raw, registry)
    receipt_path = write_receipt(registry, result)
    result["receipt"] = str(receipt_path.relative_to(REPO_ROOT))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
