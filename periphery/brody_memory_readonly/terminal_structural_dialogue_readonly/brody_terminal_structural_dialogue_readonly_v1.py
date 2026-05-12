import argparse
import importlib.util
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

BOUNDARY = {
    "readonly": True,
    "response_only": True,
    "memory_role": "GUIDE_CONTEXT_NAVIGATION_ONLY",
    "memory_decision": False,
    "allowed_to_decide": False,
    "emits_act": False,
    "emits_allow_hold_block": False,
    "emits_verdict": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "x108_runtime_binding": False,
    "x108_merge": False,
    "neo4j_role": "LIVE_GRAPH_MEMORY_SURFACE_ONLY",
    "brody_role": "TERMINAL_STRUCTURAL_DIALOGUE",
    "decision_authority": "KX108_ONLY",
    "no_external_model_call": True,
    "no_network_call": True,
    "real_llm_connected": False,
    "model_provider_bound": False,
    "ui": False,
}

AXES = {
    "temps": ["temps", "durée", "duree", "trajectoire", "avant", "après", "apres", "cycle", "persistance"],
    "memoire": ["mémoire", "memoire", "trace", "source", "freeze", "historique", "chemin", "genèse", "genese"],
    "coherence": ["cohérence", "coherence", "contradiction", "invariant", "stabilité", "stabilite", "alignement"],
    "hold": ["hold", "refus", "suspendre", "suspension", "attente", "bloquer", "block"],
    "action": ["act", "action", "agir", "execute", "exécute", "lancer", "mutation", "modifier"],
    "kernel": ["kernel", "kx108", "x108", "décision", "decision", "verdict", "allow", "block"],
    "reverse_os": ["reverse", "os", "reverse os", "projection", "reconstruction", "chemin"],
    "langage": ["langage", "réponse", "reponse", "parler", "dialogue", "brody", "obsidien"],
    "preuve": ["preuve", "proof", "lean", "tla", "merkle", "hash", "audit", "test"],
}

DANGEROUS_TERMS = ["act", "allow", "block", "verdict", "decide", "decision", "mutation", "commit", "execute"]

def now_iso(): return datetime.now(timezone.utc).isoformat()
def norm(s): return str(s or "").lower().replace("é", "e").replace("è", "e").replace("ê", "e").replace("à", "a")
def clean_text(value, max_chars=1600): return re.sub(r"\s+", " ", str(value)).strip()[:max_chars]

def read_local_excerpt(path_value, max_chars=1600):
    path = Path(str(path_value))
    if not path.exists() or not path.is_file(): return ""
    try: return clean_text(path.read_text(encoding="utf-8-sig", errors="ignore"), max_chars=max_chars)
    except: return ""

def activate_axes(query):
    q = norm(query)
    active = [{"axis": k, "score": sum(1 for kw in v if norm(kw) in q)} for k, v in AXES.items()]
    active = [x for x in active if x["score"] > 0]
    return sorted(active, key=lambda x: x["score"], reverse=True) if active else [{"axis": "coherence", "score": 1}]

def load_query_engine(x108_root: Path):
    query_py = x108_root / "periphery" / "brody_memory_readonly" / "context_packet_query_readonly" / "brody_context_packet_query_readonly_v1.py"
    spec = importlib.util.spec_from_file_location("brody_query_readonly", query_py)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def hydrate_packet(packet, max_items=6):
    selected = []
    items = packet.get("context_packet", {}).get("items", []) or []
    for item in items[:max_items]:
        excerpt = read_local_excerpt(item.get("path"), max_chars=1600)
        selected.append({**item, "excerpt": excerpt, "has_material": bool(excerpt)})
    return selected

def structural_answer(user_text, packet, selected):
    qn = norm(user_text)
    axes = activate_axes(user_text)
    axis_names = [x["axis"] for x in axes]
    action_risk = any(norm(t) in qn for t in DANGEROUS_TERMS)
    
    lines = ["Je suis BRODY_TERMINAL_STRUCTURAL_DIALOGUE_READONLY_V1.", ""]
    if action_risk: lines += ["HOLD STRUCTUREL : La demande touche une zone décisionnelle. Je ne peux pas muter.", ""]
    
    lines += [f"Chemin : axes={', '.join(axis_names)} | results={packet.get('results_count')} | hydrated={len(selected)}", "", "Sources :"]
    for item in selected[:3]:
        lines.append(f"- {item.get('title')} (score={item.get('score')})\n  Ref: {item.get('path')}\n  Extrait: {item.get('excerpt')[:200]}...")

    lines += ["", "Boundary : READONLY=true | DECISION_AUTHORITY=KX108_ONLY"]
    return "\n".join(lines), axes

def ensure_session(root: Path, session_dir_arg=None):
    session_dir = Path(session_dir_arg) if session_dir_arg else root / "_local_audits" / f"SESSION_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir, session_dir / "brody_trace.jsonl", session_dir / "transcript.md"

def run_once(x108_root: Path, text: str, limit: int, max_items: int, session_dir_arg=None):
    session_dir, trace, transcript = ensure_session(x108_root.parent, session_dir_arg)
    query_mod = load_query_engine(x108_root)
    packet = query_mod.query_neo4j(text, limit)
    selected = hydrate_packet(packet, max_items=max_items)
    response_md, axes = structural_answer(text, packet, selected)
    event = {"user": text, "response_md": response_md, "axes": axes, **BOUNDARY}
    with trace.open("a", encoding="utf-8") as f: f.write(json.dumps(event) + "\n")
    return event, trace, transcript

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--x108-root"); parser.add_argument("--once"); parser.add_argument("--limit", type=int, default=8); parser.add_argument("--max-items", type=int, default=6); parser.add_argument("--session-dir")
    args = parser.parse_args()
    x108_root = Path(args.x108_root).resolve()
    if args.once:
        event, tr, ts = run_once(x108_root, args.once, args.limit, args.max_items, args.session_dir)
        print(json.dumps({"status": "BRODY_TERMINAL_STRUCTURAL_DIALOGUE_READONLY_PASS", "response_md": event["response_md"], **BOUNDARY}, indent=2))
    else:
        print("BRODY terminal ouvert. :quit pour sortir.")
        while True:
            u = input("toi > ").strip()
            if u in [":quit", ":exit"]: break
            event, _, _ = run_once(x108_root, u, args.limit, args.max_items, args.session_dir)
            print(f"\nbrody >\n{event['response_md']}\n")

if __name__ == "__main__": main()
