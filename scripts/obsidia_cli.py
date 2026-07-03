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


def dedupe_preserve_order(items):
    """Dedoublonnage stable, purement cosmetique (aucun droit modifie)."""
    seen, out = set(), []
    for i in items:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


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
                    "explique", "resume", "definis", "definition", "comment fonctionne")
_STATE_WORDS = ("status", "statut", " up", "down", "tourne", "allume", "sante", "health")
_ACTION_WORDS = ("lance", "lancer", "prepare", "demarre", "execute", "run ", "build",
                 "comment lancer")
_META_WORDS = ("roadmap", "quels outils", "quel outil", "outils tu", "plan pour", "route pour")
_BLOCKER_WORDS = ("bloque", "blocage", "blocker", "coince")
_WHY_WORDS = ("pourquoi",)

LOCAL_CORPUS = {
    "sigma": {"keys": ("sigma",),
        "sources": ["docs/specs/OBSIDIA_SIGMA_GUIDANCE_V0.md", "registry.sigma.note"],
        "answer": ("Sigma guide sur la coherence, les contradictions et la fraicheur des "
                   "signaux (proofkit, manifest Lean, merkle en lecture, proposals, stress). "
                   "Sigma est non souverain : il recommande (CONTINUE ... HOLD_RECOMMENDED), "
                   "il ne decide jamais — HOLD_RECOMMENDED n'est pas X108Gate.HOLD. "
                   "decision_authority = KX108_ONLY. Sigma V18.9 est la couche de runtime "
                   "verification completant Lean 4 (correction statique) et TLA+ (modele) "
                   "dans la chaine de preuve.")},
    "obsidure": {"keys": ("obsidure",),
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
    "gates": {"keys": ("gate", "gates"),
        "sources": ["scripts/gates/", "tests/gates/", "docs/protocols/KERNEL_BOUNDARY_CHECK_PROTOCOL.md"],
        "answer": ("3 gates V0 : commit_scope_guard (staging = allow-list exacte), "
                   "kernel_boundary_check (chemins proteges ni dirty ni stages), "
                   "sigma_non_sovereignty_check (sigma_guidance reste KX108_ONLY). "
                   "PASS/FAIL uniquement, jamais lances par le terminal, ne remplacent pas X108.")},
    "doctrine": {"keys": ("doctrine", "souverain", "autorite", "qui decide"),
        "sources": ["docs/protocols/OBSIDIA_OPERATOR_DOCTRINE.md", "CLAUDE.md"],
        "answer": ("X108 tranche (seule autorite d'admissibilite). Sigma guide. Brody "
                   "explique. Obsidure construit. Domains bridge-only. Memory readonly. "
                   "Le terminal affiche/route/guide et n'emet jamais ALLOW/BLOCK/HOLD/ACT.")},
    "brody": {"keys": ("brody",),
        "sources": ["registry.brody.note", "runbook full stack (observation locale)"],
        "answer": ("Brody explique, contextualise et synthetise. Il vit dans l'API 8000 via "
                   "/api/brody/* (pas de serveur separe) : chat V1, enriched, raw inspector. "
                   "Brody est non souverain — il ne decide pas. Statut formel : module "
                   "first-class X108 en advisory-only (docs/brody) — runtime_readonly "
                   "repond, response_contract force les invariants KX108_ONLY, no-decision "
                   "policy explicite. Stack : launchers COMMANDS_ONLY "
                   "(01_START_BRODY_STACK.ps1).")},
    "kernel_x108": {"keys": ("kernel", "x108", "noyau"),
        "sources": ["docs/KERNEL_OVERVIEW.md (v1.4.0)", "docs/GLOSSAIRE.md"],
        "answer": ("Le Kernel X-108 est le noyau de gouvernance deterministe d'Obsidia — "
                   "le \"juge\" qui evalue les actions avant execution selon des regles "
                   "mathematiques strictes et auditables. Seule autorite d'admissibilite "
                   "(KX108_ONLY) : ALLOW/HOLD/BLOCK n'existent qu'a son niveau. Le terminal "
                   "le consulte en status readonly, ne le mute jamais.")},
    "answer_router": {"keys": ("answer router", "answer_router", "routeur",
                               "obsidia_response", "compact", "verbose"),
        "sources": ["docs/specs/OBSIDIA_TERMINAL_RESPONSE_ROUTER_V1.md",
                    "docs/specs/OBSIDIA_TERMINAL_UX_COMPACT_V2.md"],
        "answer": ("OBSIDIA_ANSWER_ROUTER est le moteur universel du terminal : tout IN "
                   "libre passe par normalisation -> policy -> plan -> mode de reponse "
                   "(LOCAL/LIVE_READONLY/COMMANDS_ONLY/PLAN/UNKNOWN/POLICY_DENY) -> une "
                   "des 5 sorties non souveraines. Compact par defaut, -v pour le detail, "
                   "raw/json pour l'ancien JSON. Hors corpus = pas d'improvisation.")},
    "oie": {"keys": ("l'oie", " oie", "inference economy", "economie d'inference",
                     "cout par action", "necessity", "adequacy"),
        "sources": ["docs/audits/OBSIDIA_INFERENCE_ECONOMY_AUDIT_V0.md",
                    "docs/protocols/OIE_BENCHMARK_PROTOCOL.md"],
        "answer": ("L'OIE mesure l'economie d'inference : le constat central est "
                   "qu'Obsidia ne reduit pas seulement le prix du token mais la necessite "
                   "meme du token — la metrique principale est le cout par action "
                   "admissible. Benchmarks avec labels obligatoires (MEASURED/ESTIMATED/"
                   "DRY_RUN/USAGE_UNAVAILABLE/INVALID_BASELINE) ; jamais d'economies "
                   "inventees, jamais de delta sans baseline. OIE mesure, ne decide pas.")},
    "audit_merkle": {"keys": ("merkle", "seal", "rfc3161", "manifest sha", "chaine d'audit"),
        "sources": ["docs/AUDIT_GUIDE.md (v1.0.0)", "docs/GLOSSAIRE.md"],
        "answer": ("La chaine d'audit Obsidia permet a un auditeur externe de verifier "
                   "artefacts et demonstrations : manifests SHA256, seal Merkle, ancre "
                   "RFC3161, verifiers readonly (verify_all/verify_merkle/verify_decision). "
                   "Rien n'est regenere automatiquement — le terminal lit, l'humain "
                   "regenere explicitement.")},
    "memory": {"keys": ("memoire", "memory", "graphiti"),
        "sources": ["docs/core_import/P66_SRL_READONLY_MEMORY_LAYER.md",
                    "docs/architecture/F70_GRAPHITI_BRODY_MEMORY_DEEP_AUDIT.md"],
        "answer": ("Memory/Graphiti est une couche de projection et contexte "
                   "readonly/frozen (canonisee P66 SRL). Elle peut informer, contextualiser "
                   "ou exposer un etat memoire, mais ne decide pas, n'ecrit pas depuis le "
                   "terminal, et ne devient jamais souveraine. memory_write=false reste "
                   "la regle terminale.")},
    "thermo": {"keys": ("thermo",),
        "sources": ["docs/periphery/ENERGY_THERMO_GOVERNOR_V0.md"],
        "answer": ("Thermo designe ici ENERGY_THERMO_GOVERNOR_V0 : un bloc peripherique "
                   "non souverain qui produit ou structure des signaux de "
                   "friction/energie/stabilite exploitables par la peripherie (sortie : "
                   "PeripheralSignalPacket). Il ne decide pas, ne mute pas le Kernel/X108, "
                   "et ne remplace pas Sigma ni Brody. "
                   "[confiance: MEDIUM — doc source V0 minimale]")},
    "domains": {"keys": ("domaine", "domains", "bridge"),
        "sources": ["docs/architecture/OBSIDIA_F60_SIGMA_REGISTRY_CANONICAL_DOMAINS.md",
                    "docs/KERNEL_OVERVIEW.md", "scripts/obsidia_registry.yaml"],
        "answer": ("Les domaines Obsidia sont des couches bridge-only vers Bank, Trading, "
                   "Ecom, GPS/Defense/Aviation (surface canonique F60 : KX108_ONLY, "
                   "readonly, advisory_only). Ils traduisent le signal metier vers le "
                   "cadre admissible mais ne decident pas — KX108_ONLY. Les adapters live "
                   "sont POST-only, jamais appeles en GET par le doctor.")},
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


def _corpus_lookup(normalized: str):
    for topic, entry in LOCAL_CORPUS.items():
        if any(k in normalized for k in entry["keys"]):
            return topic, entry
    return None, None


def _contains(normalized: str, words) -> bool:
    return any(w in normalized for w in words)


def select_answer_mode(plan: dict, normalized: str, registry: dict) -> str:
    """Regles ordonnees : la policy passe toujours en premier."""
    if plan.get("deny_keyword"):
        return "ANSWER_POLICY_DENY"
    if _contains(normalized, _BLOCKER_WORDS) or _contains(normalized, _META_WORDS):
        return "ANSWER_PLAN"
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
    layers = "brody, obsidure, obsidienne, kernel, domains, audit, memory, live, sigma"
    return (f"Je ne peux pas repondre utilement : {reason}.\n"
            f"Precise la couche visee ({layers}) ou la source a consulter.")


def answer_router(raw: str, registry: dict) -> dict:
    """Moteur universel. Reutilise build_active_plan(); ne lance jamais rien
    hors HTTP GET readonly ; toute sortie passe par assert_output_allowed()."""
    plan = build_active_plan(raw, registry)
    normalized = plan["normalized"]
    mode = select_answer_mode(plan, normalized, registry)
    assert mode in ANSWER_MODES
    layer = plan["detected_layer"]
    corpus_used: list = []
    limites = ["reponse limitee au corpus/droits readonly du terminal — X108 decide"]
    reponse = ""
    next_h = plan["next_human_action"]

    if mode == "ANSWER_POLICY_DENY":
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
        else:
            reponse = build_unknown_answer(plan, raw, "IN trop vague ou sujet hors corpus local")
            if _contains(normalized, _KNOWLEDGE_WORDS):
                # Repli definitionnel declare (LOCAL_CORPUS_EXTENSION_V2) :
                # orientation vers le glossaire canonique, jamais de substance inventee.
                reponse += ("\nRepli definitionnel : docs/GLOSSAIRE.md — \"Dual Obsidia : "
                            "l'IA propose, le Juge dispose\". Terme non indexe en direct.")
            next_h = "reformuler ou fournir la source/scope"

    output = assert_output_allowed(_MODE_TO_OUTPUT[mode])
    return {
        "panel": "OBSIDIA_RESPONSE", "raw": raw, "reponse": reponse,
        "mode_reponse": mode, "detected_layer": layer, "confidence": plan["confidence"],
        "organes_mobilises": plan["organes_mobilises"],
        "organes_mobilisables": plan["organes_mobilisables"],
        "outils_utilises": plan["outils_utilises"],
        "corpus_utilise": corpus_used or ["aucun"],
        "limites": limites,
        "next_human_action": next_h,
        "output": output,
        "guidance": plan["guidance"], "guidance_authority": "NONE",
        "plan_status": plan["plan_status"],
    }


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


def main(argv: list[str]) -> int:
    if argv and argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    registry = load_registry(REGISTRY_PATH)
    verbose_mode = False
    if argv and argv[0] in ("-v", "--verbose"):
        verbose_mode = True
        argv = argv[1:]
    if not argv:
        return interactive_shell(registry)
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
    print(format_obsidia_response(resp) if verbose_mode
          else format_obsidia_response_compact(resp))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
