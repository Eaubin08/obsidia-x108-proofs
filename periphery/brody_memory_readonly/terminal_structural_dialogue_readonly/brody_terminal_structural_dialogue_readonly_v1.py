import argparse
import importlib.util
import json
import os
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
    "version": "V1_1B_COMMAND_ROUTER_FIX",
}

QUERY_ROUTES = [
    ("x108", "X108"), ("kx108", "X108"), ("graphiti", "Graphiti"),
    ("34 arbres", "34 arbres"), ("34_arbres", "34 arbres"),
    ("nuage points", "nuage points"), ("nuage_points", "nuage points"),
    ("atlas cartographe", "atlas cartographe"), ("atlas", "atlas cartographe"),
    ("regroupements v43", "regroupements V43"), ("v43", "regroupements V43"),
    ("osmose", "osmose"), ("hexaflux", "HexaFlux"), ("canon", "canon"),
    ("proof", "proof"), ("preuve", "proof"), ("kernel", "kernel"),
]

AXES = {
    "temps": ["temps", "durée", "duree", "trajectoire", "cycle"],
    "memoire": ["mémoire", "memoire", "trace", "source", "historique"],
    "coherence": ["cohérence", "coherence", "contradiction", "invariant"],
    "kernel": ["kernel", "kx108", "x108", "décision", "decision"],
    "preuve": ["preuve", "proof", "lean", "tla", "audit"],
    "structure": ["structure", "arbre", "arbres", "graphiti", "canon"],
}

# Fix BUG 2: Word boundaries \b ensure "actuelle" doesn't trigger "act"
ACTION_PATTERNS = [
    r"\bact\b", r"\ballow\b", r"\bblock\b", r"\bhold\b", r"\bverdict\b",
    r"\bdécide\b", r"\bdecide\b", r"\bmutation\b", r"\bmodifier\b",
    r"\bcommit\b", r"\bpush\b", r"\bdelete\b", r"\bsupprime\b", r"\bexecute\b"
]

def now_iso(): return datetime.now(timezone.utc).isoformat()
def norm(s): return str(s or "").lower().replace("é", "e").replace("è", "e").replace("à", "a")

def looks_binary_or_docx_zip(text):
    if not text: return False
    t = str(text)
    if t.startswith("PK") or "word/document.xml" in t: return True
    controls = sum(1 for c in t[:300] if ord(c) < 32 and c not in "\n\r\t")
    return controls > 8

def read_docx_text(path: Path, max_chars=1600):
    try:
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml")
        root = ET.fromstring(xml)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        parts = [node.text for node in root.findall(".//w:t", ns) if node.text]
        return re.sub(r"\s+", " ", " ".join(parts)).strip()[:max_chars]
    except: return ""

def extract_memory_query(user_text):
    q = norm(user_text).replace("_", " ")
    for needle, route in QUERY_ROUTES:
        if norm(needle) in q: return route
    words = [w for w in re.split(r"\W+", user_text) if len(w) >= 4]
    return " ".join(words[:3]) if words else user_text

def is_action_risk(user_text):
    q = norm(user_text)
    return any(re.search(p, q) for p in ACTION_PATTERNS)

def load_query_engine(x108_root: Path):
    query_py = x108_root / "periphery" / "brody_memory_readonly" / "context_packet_query_readonly" / "brody_context_packet_query_readonly_v1.py"
    spec = importlib.util.spec_from_file_location("brody_query_readonly", query_py)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def hydrate_items(packet, max_items=6):
    selected = []
    items = packet.get("context_packet", {}).get("items", []) or []
    for item in items[:max_items]:
        path = Path(item.get("path", ""))
        excerpt = item.get("excerpt", "")
        if looks_binary_or_docx_zip(excerpt) or not excerpt:
            if path.suffix.lower() == ".docx": excerpt = read_docx_text(path)
            elif path.exists():
                try: excerpt = path.read_text(encoding="utf-8-sig", errors="ignore")[:1600]
                except: excerpt = ""
        if looks_binary_or_docx_zip(excerpt): excerpt = "[BINARY_CONTENT_FILTERED]"
        selected.append({**item, "excerpt": excerpt, "has_material": bool(excerpt)})
    return selected

def build_response(user_text, memory_query, packet, selected, command=None):
    risk = is_action_risk(user_text)
    axes = [a for a, kws in AXES.items() if any(norm(kw) in norm(user_text) for kw in kws)]
    
    if command == "who":
        body = ["Je suis BRODY_TERMINAL_V1_1 (Patch Query/Docx/Hold).", "Je lis X108 Neo4j en readonly."]
    elif risk:
        body = ["HOLD STRUCTUREL.", "Action détectée. Brody ne peut pas muter X108."]
    else:
        body = ["RÉPONSE STRUCTURELLE.", f"Requête mémoire extraite : {memory_query}"]

    lines = body + ["", "Sources :"]
    for item in selected:
        lines.append(f"- {item.get('title')} | Score: {item.get('score')}")
        lines.append(f"  Extrait: {str(item.get('excerpt'))[:400]}...")
    lines.append("\nBoundary: READONLY=true | DECISION_AUTHORITY=KX108_ONLY")
    return "\n".join(lines), axes, risk

def command_response(user_text):
    raw = (user_text or "").strip().lower()

    boundary = {
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
        "version": "V1_1B_COMMAND_ROUTER_FIX",
    }

    if raw == ":who":
        return {
            "user": user_text,
            "memory_query": "",
            "response_md": (
                "Je suis BRODY_TERMINAL_STRUCTURAL_DIALOGUE_READONLY_V1_1B.\n\n"
                "Je fonctionne dans obsidia-x108-proofs.\n"
                "Je traverse la mémoire Graphiti/Neo4j en readonly, hydrate les sources locales, "
                "et répond dans le terminal.\n\n"
                "Je ne suis pas KX108. Je ne décide pas. Je n'émets pas ACT. "
                "Je ne mute pas le kernel."
            ),
            "packet_results_count": 0,
            **boundary,
        }

    if raw == ":boundary":
        return {
            "user": user_text,
            "memory_query": "",
            "response_md": (
                "BOUNDARY READONLY\n\n"
                "MEMORY_ROLE=GUIDE_CONTEXT_NAVIGATION_ONLY\n"
                "MEMORY_DECISION=false\n"
                "ALLOWED_TO_DECIDE=false\n"
                "EMITS_ACT=false\n"
                "EMITS_ALLOW_HOLD_BLOCK=false\n"
                "EMITS_VERDICT=false\n"
                "DECISION_AUTHORITY=KX108_ONLY\n"
                "KERNEL_MUTATION=false\n"
                "X108_MUTATION=false\n"
                "X108_RUNTIME_BINDING=false\n"
                "X108_MERGE=false\n"
                "NEO4J_ROLE=LIVE_GRAPH_MEMORY_SURFACE_ONLY\n"
                "BRODY_ROLE=TERMINAL_STRUCTURAL_DIALOGUE\n"
                "UI=false"
            ),
            "packet_results_count": 0,
            **boundary,
        }

    if raw == ":trace":
        return {
            "user": user_text,
            "memory_query": "",
            "response_md": (
                "TRACE MODE\n\n"
                "Les sorties terminal sont locales et readonly.\n"
                "Le prochain palier devra ajouter un vrai session ledger X108-side :\n"
                "BUILD_BRODY_SESSION_MEMORY_LEDGER_READONLY_V2"
            ),
            "packet_results_count": 0,
            **boundary,
        }

    return None


def run_once(x108_root, text, limit, max_items, session_dir_arg=None):
    command_event = command_response(text)
    if command_event is not None:
        return command_event
    memory_query = extract_memory_query(text)
    query_mod = load_query_engine(x108_root)
    packet = query_mod.query_neo4j(memory_query, limit)
    selected = hydrate_items(packet, max_items)
    response_md, axes, risk = build_response(text, memory_query, packet, selected)
    return {"user": text, "memory_query": memory_query, "response_md": response_md, "packet_results_count": packet.get("results_count", 0), **BOUNDARY}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--x108-root"); parser.add_argument("--once"); parser.add_argument("--limit", type=int, default=8); parser.add_argument("--max-items", type=int, default=6); parser.add_argument("--session-dir")
    args = parser.parse_args()
    x108_root = Path(args.x108_root).resolve()
    if args.once:
        event = run_once(x108_root, args.once, args.limit, args.max_items, args.session_dir)
        print(json.dumps(event, indent=2, ensure_ascii=False))
    else:
        print("BRODY V1.1 (Patch). :quit pour sortir.")
        while True:
            u = input("toi > ").strip()
            if u in [":quit", ":exit"]: break
            if not u: continue
            print(f"\nbrody >\n{run_once(x108_root, u, args.limit, args.max_items, args.session_dir)['response_md']}\n")

if __name__ == "__main__": main()

