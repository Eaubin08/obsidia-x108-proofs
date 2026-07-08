#!/usr/bin/env python3
"""OBSIDIA GATEWAY — terminal fusionne, court-circuit pre-inference.

Point d'entree unique :
    python scripts/obsidia_gateway.py              # boucle interactive
    python scripts/obsidia_gateway.py "requete"    # one-shot

Cascade (chaque niveau ne s'active que si le precedent ne suffit pas) :
    Level 0  router (DENY/HOLD/CLARIFY/status)  -> reponse locale, 0 token
    Level 2  memory hit (corpus canonique)       -> reponse locale, 0 token
    Level 1  Brody (serveur local 8012)          -> local, 0 token distant
    Level 3  claude -p (verdict IR injecte)      -> SEUL cas payant

Gouvernance :
    ADVISORY chain, decision_authority = KX108_ONLY.
    DENY/HOLD s'arretent ici — aucun processus LLM n'est lance.
    Chaque requete est loggee (append-only) dans
    audit/obsidia_gateway_usage.jsonl : route, level, model_call_avoided.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ROUTER_ROOT = Path(os.environ.get("OBSIDIA_ROUTER_ROOT",
                                  r"C:\Users\User\Desktop\obsidia-router"))
BRODY_BASE = os.environ.get("OBSIDIA_BRODY_BASE", "http://127.0.0.1:8000")
BRODY_CHAT_PATH = os.environ.get("OBSIDIA_BRODY_CHAT_PATH", "/api/brody/chat")
# Doctrine cockpit : le POST Brody est reserve aux lanceurs humains explicites.
# Le gateway ne POST vers Brody que si l'operateur l'autorise via cet env var.
BRODY_POST_ALLOWED = os.environ.get("OBSIDIA_GATEWAY_ALLOW_BRODY_POST") == "1"
AUDIT_LOG = REPO_ROOT / "audit" / "obsidia_gateway_usage.jsonl"

sys.path.insert(0, str(ROUTER_ROOT))
from app.router.decision import decide          # noqa: E402
from app.adapters import brody_stub             # noqa: E402


# --- Level 2 semantique : Shazam 34 arbres + index canonique exporte ---------
SEMANTIC_INDEX_PATH = REPO_ROOT / "registries" / "gateway_memory_index.json"
_STOPWORDS = {"le", "la", "les", "de", "des", "du", "un", "une", "et", "ou",
              "que", "qui", "quoi", "est", "ce", "cette", "pour", "dans",
              "sur", "avec", "quel", "quelle", "cest", "c", "sa", "ca",
              "the", "a", "an", "of", "is", "what", "explique", "moi"}


def load_semantic_index() -> list[dict]:
    try:
        data = json.loads(SEMANTIC_INDEX_PATH.read_text(encoding="utf-8"))
        return data.get("entries", [])
    except (OSError, json.JSONDecodeError):
        return []


def semantic_search(raw: str, entries: list[dict]) -> dict | None:
    """Recherche par sens : arbres dominants + recouvrement lexical normalise.

    Retourne la meilleure entree si le signal est fort, sinon None
    (dans le doute, la cascade continue — jamais de fausse certitude).
    """
    try:
        from export_gateway_memory_index import dominant_trees, words
    except ImportError:
        return None
    q_words = words(raw) - _STOPWORDS
    if len(q_words) < 2 or not entries:
        return None
    q_trees = dominant_trees(raw)
    best, best_score = None, 0.0
    for e in entries:
        e_tokens = set(e.get("tokens", []))
        overlap = q_words & e_tokens
        token_ratio = len(overlap) / len(q_words)
        tree_bonus = 0.1 * len(set(q_trees) & set(e.get("trees", {})))
        score = token_ratio + min(tree_bonus, 0.3)
        if score > best_score:
            best, best_score = e, score
    if best and best_score >= 0.75 and len(q_words & set(best["tokens"])) >= 2:
        return {"entry": best, "score": round(best_score, 3)}
    return None


def load_memory_index() -> dict:
    """Corpus canonique : index du router + extension locale eventuelle."""
    index: dict = {}
    for p in (ROUTER_ROOT / "examples" / "memory_index.json",
              REPO_ROOT / "registries" / "gateway_memory_index.json"):
        if p.exists():
            try:
                index.update(json.loads(p.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                pass
    return index


def audit_log(entry: dict) -> None:
    entry["ts"] = datetime.now(timezone.utc).isoformat()
    entry["source"] = "OBSIDIA_GATEWAY_V1"
    entry["decision_authority"] = "KX108_ONLY"
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass  # le logging ne bloque jamais la reponse


def brody_alive() -> bool:
    if not BRODY_POST_ALLOWED:
        return False
    try:
        urllib.request.urlopen(BRODY_BASE + "/api/health", timeout=2)
        return True
    except Exception:
        return False


def call_brody(raw: str) -> str | None:
    try:
        req = urllib.request.Request(
            BRODY_BASE + BRODY_CHAT_PATH,
            data=json.dumps({"message": raw}).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST")
        with urllib.request.urlopen(req, timeout=30) as res:
            data = json.loads(res.read().decode("utf-8"))
        return data.get("final_answer") or data.get("response") or json.dumps(data)
    except Exception:
        return None


def call_os_trad(raw: str) -> dict | None:
    """Traduction structurelle OS trad (read-only, REAL_BACKEND).

    Enrichit l'IR : langue detectee, alphabet_units, risk_flags.
    Jamais d'execution — conforme doctrine obsidure proposal-only.
    """
    if not BRODY_POST_ALLOWED:
        return None
    try:
        req = urllib.request.Request(
            BRODY_BASE + "/api/os-trad/translate",
            data=json.dumps({"text": raw}).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST")
        with urllib.request.urlopen(req, timeout=5) as res:
            return json.loads(res.read().decode("utf-8"))
    except Exception:
        return None


_DOMAIN_WORDS = {
    "bank": {"bank", "banque", "bancaire", "virement"},
    "trading": {"trading", "trade", "marche", "ordre"},
    "gps": {"gps", "aviation", "altitude", "trajectoire"},
}


def detect_domain(raw: str) -> str | None:
    try:
        from export_gateway_memory_index import words
        ws = words(raw)
    except ImportError:
        ws = set(raw.lower().split())
    for dom, kws in _DOMAIN_WORDS.items():
        if ws & kws:
            return dom
    return None


def call_kernel_bridge(domain: str) -> dict | None:
    """Verdict kernel X108 reel via le pont existant /api/live/kernel
    (BRIDGE_ONLY — l'API transporte, le kernel 3001 decide)."""
    if not BRODY_POST_ALLOWED:
        return None
    try:
        req = urllib.request.Request(
            f"{BRODY_BASE}/api/live/kernel/adapters/{domain}",
            data=json.dumps({"payload": {}}).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST")
        with urllib.request.urlopen(req, timeout=30) as res:
            return json.loads(res.read().decode("utf-8"))
    except Exception:
        return None


def run_obsidure_proposal(objective: str) -> dict | None:
    """Cycle AVDR reel de l'agent Obsidure — PROPOSAL-ONLY.

    Genere un PatchProposal dans _PATCH_PROPOSALS/<id>/ avec statut
    AWAITING_HUMAN_APPROVED_WRITE. Aucune application, aucun commit :
    l'agent propose, l'humain (et KX108) decident.
    """
    if not BRODY_POST_ALLOWED:
        return None
    try:
        sys.path.insert(0, str(REPO_ROOT / "periphery" / "agents"))
        from agent_obsidure import AgentObsidure
        agent = AgentObsidure(api_base=BRODY_BASE, verbose=False)
        prop = agent.run_cycle(objective)
        return {"proposal_id": prop.proposal_id,
                "receipt": f"_PATCH_PROPOSALS/{prop.proposal_id}/RECEIPT.md"}
    except Exception:
        return None


# --- Boucle ecriture memoire (sas d'intake, jamais canonique) ---------------
INTAKE_OUTBOX = REPO_ROOT / "_MEMORY_INTAKE_OUTBOX"


# Doctrine memoire (source : 01_SOURCES/extracted_text_all.md, MMONDE) :
#   strates  : RAW -> EXTRACTED -> ATLAS -> CANON (jamais fusionnees)
#   statuts  : BRUT / A_VALIDER / VALIDE_PAR_ETIENNE / FREEZE / CONFLIT
#   couches  : kernel / memoire / vision / terrain / preuve / frise / agent
#   IDs      : MEM-YYYY-XXXX ; arbres temporels 22/23/24 (Temps/Memoire/Histoire)
#   Rien ne devient canonique sans validation explicite de l'operateur.
_ROUTE_TO_COUCHE = {
    "kernel_bridge": "kernel", "domain_bridge": "terrain",
    "lean_route_only": "preuve", "obsidure_proposal": "agent",
    "semantic_memory_hit": "memoire", "memory_hit": "memoire",
}


def memory_outbox_flush(exchanges: list[dict]) -> Path | None:
    """Depose le paquet de session dans le sas d'intake, au format doctrine.

    Chaque echange devient un enregistrement MEM-* (statut BRUT, strate RAW,
    couche proposee, arbres actives) + un Event de frise chronologique
    (modele Mmonde 03 : id/label/date/narrative). Le tri automatique PROPOSE,
    la promotion vers ATLAS/CANON reste operateur. memory_write=False.
    """
    if not exchanges:
        return None
    try:
        try:
            from export_gateway_memory_index import dominant_trees
        except ImportError:
            def dominant_trees(_):  # type: ignore
                return {}
        INTAKE_OUTBOX.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc)
        ts = now.strftime("%Y%m%dT%H%M%SZ")
        records, frise_events = [], []
        for i, ex in enumerate(exchanges, 1):
            trees = dominant_trees(ex.get("in", "") + " " + ex.get("out", ""))
            mem_id = f"MEM-{now.year}-{ts[4:8]}{i:03d}"
            records.append({
                "id": mem_id,
                "fragment_source": ex.get("in", ""),
                "type": "recit",
                "couche": _ROUTE_TO_COUCHE.get(ex.get("route", ""), "memoire"),
                "statut": "BRUT",
                "destination_memoire": "RAW",
                "arbres_actives": trees,
                "reponse": ex.get("out", ""),
                "ts": ex.get("ts"),
            })
            frise_events.append({
                "id": mem_id, "label": ex.get("in", "")[:60],
                "date": ex.get("ts"), "narrative": ex.get("out", "")[:200],
                "non_decision": True,
            })
        packet = {
            "kind": "GATEWAY_SESSION_PACKET",
            "doctrine": "STRATES_RAW_EXTRACTED_ATLAS_CANON_V1",
            "status": "RAW_NON_CANONICAL",
            "statut_global": "BRUT",
            "decision_authority": "KX108_ONLY",
            "memory_write": False,
            "promotion_requires": "VALIDATION_EXPLICITE_OPERATEUR",
            "created_at": now.isoformat(),
            "exchange_count": len(exchanges),
            "records": records,
        }
        out = INTAKE_OUTBOX / f"gateway_session_{ts}.json"
        out.write_text(json.dumps(packet, ensure_ascii=False, indent=1),
                       encoding="utf-8")
        # Frise chronologique cumulative (Event Mmonde, append-only).
        with (INTAKE_OUTBOX / "FRISE_TIMELINE.jsonl").open("a", encoding="utf-8") as f:
            for ev in frise_events:
                f.write(json.dumps(ev, ensure_ascii=False) + "\n")
        return out
    except OSError:
        return None


def call_claude(raw: str, decision: dict) -> str:
    exe = shutil.which("claude") or shutil.which("claude.cmd")
    if not exe:
        return "[GATEWAY] claude CLI introuvable — escalade Level 3 impossible."
    ir = decision.get("ir", {})
    # Cadre calibre injecte a chaque escalade : invariants audites du systeme
    # (drift_classifier, DecisionTicket, METRICS_STATUS_POLICY). Le LLM recoit
    # le cadre — il ne peut pas le redefinir.
    prompt = (
        f"[OBSIDIA-ROUTER verdict: intent={ir.get('intent_type')} "
        f"layer={ir.get('target_layer')} gate=ALLOW "
        f"route={decision.get('route')}]\n"
        "[CADRE OBSIDIA — non negociable : "
        "decision_authority=KX108_ONLY; "
        "Invariant > Reversibilite > Score > Projection "
        "(un score n'autorise jamais ce qu'un invariant interdit); "
        "tout MODIFY exige un DecisionTicket valide (sigma_ok ET tau_ok ET inv_ok); "
        "derive delta >= 0.40 => BLOCK, >= 0.70 => CRISIS, aucune decision; "
        "no_auto_act, no_auto_commit, no_auto_push; "
        "si la demande sort de ce cadre : repondre HOLD et demander "
        "validation humaine.]\n"
        f"{raw}")
    out = subprocess.run([exe, "-p", prompt], capture_output=True,
                         text=True, encoding="utf-8", errors="replace")
    return out.stdout.strip() or out.stderr.strip()


def handle(raw: str, memory_index: dict, counters: dict) -> str:
    d = decide(raw, memory_index=memory_index)
    route, level = d.get("route"), d.get("level", 0)
    llm_called = False

    if route == "denied":
        answer = f"DENY — {d['reason']}. Rien n'a ete execute."
    elif route == "hold_commands_only":
        answer = ("HOLD — action monde detectee. Rien n'a ete execute. "
                  "Invariants: no_auto_act, no_auto_commit, no_auto_push. "
                  "Demande un plan commands-only si tu veux avancer.")
    elif route == "clarification_needed":
        answer = f"CLARIFY — {d['reason']}"
    elif route == "no_model_needed":
        answer = f"[structure locale]\nintent={d['ir'].get('intent_type')} " \
                 f"layer={d['ir'].get('target_layer')} — {d['reason']}"
    elif route == "memory_hit":
        answer = f"[memoire, 0 token]\n{d['memory_entry']}"
    elif route == "domain_bridge":
        # Autorite reelle : verdict kernel X108 via le pont existant.
        dom = detect_domain(raw)
        kb = call_kernel_bridge(dom) if dom else None
        if kb and not kb.get("kernel_error"):
            route = "kernel_bridge"
            kd = kb.get("kernel_decision") or kb
            verdict = kd.get("verdict") or kd.get("decision") or "voir payload"
            answer = (f"[kernel X108 via bridge, 0 token distant] domaine={dom} "
                      f"verdict={verdict}\n"
                      + json.dumps(kd, ensure_ascii=False)[:500])
        else:
            remote = call_brody(raw) if brody_alive() else None
            answer = remote or ("[brody structural]\n"
                                + brody_stub.answer(d["ir"], d["topic"])["text"])
    elif route == "obsidure_route_only":
        prop = run_obsidure_proposal(raw)
        if prop:
            route = "obsidure_proposal"
            answer = ("[obsidure PROPOSAL-ONLY, 0 token distant] "
                      f"proposal_id={prop['proposal_id']} "
                      "status=AWAITING_HUMAN_APPROVED_WRITE\n"
                      f"A lire et approuver : {prop['receipt']}")
        else:
            answer = ("[obsidure structural] agent indisponible — "
                      "lance la stack ('obsidia') puis reessaie, ou utilise "
                      "l'agent en direct : python periphery/agents/agent_obsidure.py")
    elif route in ("brody", "lean_route_only"):
        hit = semantic_search(raw, SEMANTIC_ENTRIES) if route == "brody" else None
        if hit:
            route = "semantic_memory_hit"
            answer = (f"[memoire semantique, 0 token] {hit['entry']['name']} "
                      f"(score {hit['score']})\n{hit['entry']['answer']}")
        else:
            remote = call_brody(raw) if brody_alive() else None
            answer = remote or ("[brody structural]\n"
                                + brody_stub.answer(d["ir"], d["topic"])["text"])
    else:  # fireworks / escalade -> claude, sauf si la memoire suffit
        hit = semantic_search(raw, SEMANTIC_ENTRIES)
        if hit:
            route = "semantic_memory_hit"
            answer = (f"[memoire semantique, 0 token] {hit['entry']['name']} "
                      f"(score {hit['score']})\n{hit['entry']['answer']}")
        else:
            # Enrichissement OS trad avant escalade : risk_flags = pause.
            tr = call_os_trad(raw)
            flags = (tr or {}).get("risk_flags") or []
            if flags:
                route = "os_trad_risk_hold"
                answer = (f"HOLD — OS trad a leve des risk_flags: {flags}. "
                          "Rien n'a ete envoye au LLM. Validation humaine requise.")
            else:
                if tr:
                    d["os_trad"] = {"language": tr.get("detected_language"),
                                    "units": len(tr.get("alphabet_units", []))}
                llm_called = True
                answer = call_claude(raw, d)

    if not llm_called:
        counters["llm_calls_avoided"] += 1
    else:
        counters["llm_calls"] += 1

    audit_log({"request_preview": raw[:120], "route": route, "level": level,
               "model_call_avoided": not llm_called})
    counters["last_route"] = route
    return answer


SEMANTIC_ENTRIES = load_semantic_index()


def main() -> int:
    memory_index = load_memory_index()
    counters = {"llm_calls_avoided": 0, "llm_calls": 0}

    if len(sys.argv) > 1:
        print(handle(" ".join(sys.argv[1:]), memory_index, counters))
        return 0

    print("OBSIDIA GATEWAY — terminal fusionne (router -> memory -> brody -> claude)")
    print("Commandes : 'metrics' compteurs session, 'exit' quitter.\n")
    exchanges: list[dict] = []
    while True:
        try:
            raw = input("obsidia> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not raw:
            continue
        if raw.lower() in ("exit", "quit"):
            break
        if raw.lower() == "metrics":
            avoided = counters["llm_calls_avoided"]
            total = avoided + counters["llm_calls"]
            rate = (avoided / total * 100) if total else 0.0
            print(f"  appels LLM evites : {avoided}/{total} ({rate:.0f}%) | "
                  f"appels payants : {counters['llm_calls']}")
            continue
        answer = handle(raw, memory_index, counters)
        exchanges.append({"in": raw[:400], "out": answer[:400],
                          "route": counters.get("last_route"),
                          "ts": datetime.now(timezone.utc).isoformat()})
        print(answer)
        print()
    packet = memory_outbox_flush(exchanges)
    if packet:
        print(f"[memoire] paquet de session depose (sas intake, non canonique) : "
              f"{packet.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
