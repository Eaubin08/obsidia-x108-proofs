#!/usr/bin/env python3
"""
Brody Terminal Chat Client V1
================================
Interactive CLI client for /api/brody/chat.
Connects to a local Obsidia API at http://127.0.0.1:8000.

Commands:
  /help       Show available commands
  /exit, /quit  Exit cleanly
  /debug on   Enable debug mode (full payload)
  /debug off  Disable debug mode (compact)
  /compact on Enable compact mode
  /compact off Disable compact mode
  /session <name>  Change session ID
  /status     Show current client state
  /save       Force save transcript
  /last       Re-display last Brody response
  /raw        Show last raw JSON

Usage:
  python scripts/brody_terminal_chat.py
  python scripts/brody_terminal_chat.py --endpoint http://127.0.0.1:8000
"""
from __future__ import annotations

import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ── Config ──────────────────────────────────────────────────────────────────

DEFAULT_ENDPOINT = "http://127.0.0.1:8000"
DEFAULT_LANGUAGE = "fr"
DEFAULT_SESSION = "brody-terminal"
REQUEST_TIMEOUT = 30  # seconds
TRANSCRIPT_DIR = Path("_local_audits/BRODY_TERMINAL_CHAT_CLIENT_V1/sessions")
MEMORY_DIR = Path("_local_audits/BRODY_TERMINAL_CHAT_CLIENT_V1/personal_memory")
CONTEXT_CHAR_BUDGET = 3000  # max chars for injected context

# ── Memory signal keywords ──────────────────────────────────────────────────

_MEMORY_SIGNALS = [
    "garde", "retient", "à retenir", "important", "validé", "freeze",
    "canon", "barrière", "prochain palier", "on a stabilisé",
    "à faire après", "pas maintenant", "plus tard", "mémoire personnelle",
    "souviens", "note", "rappelle", "stabilisé",
]


# ── Personal Memory Sidecar ─────────────────────────────────────────────────

class PersonalMemorySidecar:
    """
    Local-only personal memory sidecar.
    NEVER writes to Graphiti, Neo4j, or BrodyMemoryDoc.
    All entries are LOCAL_PERSONAL_MEMORY_ONLY or LOCAL_CANDIDATE_REVIEW_REQUIRED.
    """

    def __init__(self) -> None:
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        self._memory_path = MEMORY_DIR / "personal_memory.jsonl"
        self._index_path = MEMORY_DIR / "personal_memory_index.json"
        self._candidates_path = MEMORY_DIR / "pending_candidates.jsonl"
        self._links_path = MEMORY_DIR / "readonly_links.json"
        self._context_cache_path = MEMORY_DIR / "memory_context_cache.json"

    # ── Memory entries ──────────────────────────────────────────────────

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _make_id(self) -> str:
        return f"pm-{int(time.time() * 1000)}-{os.urandom(4).hex()}"

    def add_memory_entry(
        self, topic: str, content: str, tags: list[str] | None = None, confidence: float = 0.5,
    ) -> dict[str, Any]:
        entry: dict[str, Any] = {
            "id": self._make_id(),
            "timestamp": self._now(),
            "source": "brody_terminal_personal_sidecar",
            "status": "LOCAL_PERSONAL_MEMORY_ONLY",
            "scope": "terminal_conversation",
            "topic": topic,
            "content": content,
            "tags": tags or [],
            "confidence": confidence,
            "promotion_allowed": False,
            "requires_review": True,
            "memory_write": False,
            "graphiti_write": False,
            "neo4j_write": False,
            "kernel_mutation": False,
        }
        with open(self._memory_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def read_memory_entries(self, limit: int = 50) -> list[dict[str, Any]]:
        if not self._memory_path.exists():
            return []
        entries = []
        with open(self._memory_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        return entries[-limit:]

    def search_memory(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        q = query.lower()
        results = []
        for entry in reversed(self.read_memory_entries()):
            if q in json.dumps(entry).lower():
                results.append(entry)
                if len(results) >= limit:
                    break
        return results

    def memory_count(self) -> int:
        return len(self.read_memory_entries(limit=10000))

    # ── Candidates ──────────────────────────────────────────────────────

    def add_candidate(
        self, candidate_type: str, content: str, user_msg: str, brody_answer: str,
    ) -> dict[str, Any]:
        entry: dict[str, Any] = {
            "id": self._make_id(),
            "timestamp": self._now(),
            "source": "terminal_conversation",
            "status": "LOCAL_CANDIDATE_REVIEW_REQUIRED",
            "candidate_type": candidate_type,
            "content": content,
            "evidence_user_message": user_msg[:500],
            "evidence_brody_answer": brody_answer[:500],
            "promotion_allowed": False,
            "requires_review": True,
            "memory_write": False,
            "graphiti_write": False,
            "neo4j_write": False,
            "kernel_mutation": False,
        }
        with open(self._candidates_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def read_candidates(self, limit: int = 50) -> list[dict[str, Any]]:
        if not self._candidates_path.exists():
            return []
        entries = []
        with open(self._candidates_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        e = json.loads(line)
                        if e.get("status") == "LOCAL_CANDIDATE_REVIEW_REQUIRED":
                            entries.append(e)
                    except json.JSONDecodeError:
                        pass
        return entries[-limit:]

    def candidate_count(self) -> int:
        return len(self.read_candidates(limit=10000))

    def promote_candidate(self, candidate_id: str) -> dict[str, Any] | None:
        """Promote a candidate to personal memory (LOCAL ONLY, never Graphiti/Neo4j)."""
        candidates = self._read_all_candidates_raw()
        target = None
        new_lines = []
        for line in candidates:
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                new_lines.append(line)
                continue
            if e.get("id") == candidate_id and e.get("status") == "LOCAL_CANDIDATE_REVIEW_REQUIRED":
                # Promote to personal memory
                entry = self.add_memory_entry(
                    topic=e.get("candidate_type", "general"),
                    content=e.get("content", ""),
                    confidence=0.7,
                )
                target = entry
                # Mark candidate as promoted
                e["status"] = "LOCAL_PROMOTED_TO_PERSONAL_MEMORY"
                new_lines.append(json.dumps(e, ensure_ascii=False))
            else:
                new_lines.append(json.dumps(e, ensure_ascii=False) if isinstance(e, dict) else line)
        self._candidates_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        return target

    def reject_candidate(self, candidate_id: str) -> bool:
        """Mark a candidate as locally rejected."""
        candidates = self._read_all_candidates_raw()
        found = False
        new_lines = []
        for line in candidates:
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                new_lines.append(line)
                continue
            if e.get("id") == candidate_id and e.get("status") == "LOCAL_CANDIDATE_REVIEW_REQUIRED":
                e["status"] = "LOCAL_REJECTED"
                found = True
                new_lines.append(json.dumps(e, ensure_ascii=False))
            else:
                new_lines.append(json.dumps(e, ensure_ascii=False) if isinstance(e, dict) else line)
        self._candidates_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        return found

    def _read_all_candidates_raw(self) -> list[str]:
        if not self._candidates_path.exists():
            return []
        return self._candidates_path.read_text(encoding="utf-8").split("\n")

    # ── Readonly links ──────────────────────────────────────────────────

    def get_readonly_links(self) -> dict[str, Any]:
        if not self._links_path.exists():
            return {"links": [], "readonly": True}
        try:
            return json.loads(self._links_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"links": [], "readonly": True}

    # ── Search (unified) ────────────────────────────────────────────────

    def search_unified(self, query: str, limit: int = 10) -> dict[str, Any]:
        mem = self.search_memory(query, limit)
        cand = [
            c for c in self.read_candidates()
            if query.lower() in json.dumps(c).lower()
        ][:limit]
        return {"personal_memory": mem, "pending_candidates": cand}


# ── Memory signal detection ─────────────────────────────────────────────────

def detect_memory_signal(text: str) -> bool:
    """Detect if the user message contains a memory-signal keyword."""
    low = text.lower()
    return any(sig in low for sig in _MEMORY_SIGNALS)


# ── Context builder ─────────────────────────────────────────────────────────

def build_memory_context_packet(
    state: dict[str, Any],
    user_message: str,
    turns: list[dict[str, Any]],
    memory: PersonalMemorySidecar,
) -> str:
    """
    Build a lightweight context suffix to append after the user message.
    User message comes FIRST (priority), context is a short suffix.
    Respects CONTEXT_CHAR_BUDGET for the context portion only.
    """
    parts = []

    # Session turns (last 2, compact)
    if turns:
        recent = turns[-2:]
        parts.append("[Session:")
        for t in recent:
            parts.append(f" You: {t['user_message'][:80]}")
            parts.append(f" Brody: {t['final_answer'][:120]}")
        parts.append("]")

    # Personal memory hits (compact)
    memory_hits = memory.search_memory(user_message, limit=3)
    if memory_hits:
        parts.append("[Memory:")
        for m in memory_hits[:3]:
            parts.append(f" [{m['topic']}] {m['content'][:100]}")
        parts.append("]")

    # Pending candidates (compact)
    candidates = memory.read_candidates(limit=3)
    if candidates:
        parts.append("[Candidates review-only:")
        for c in candidates[:3]:
            parts.append(f" [{c['candidate_type']}] {c['content'][:80]}")
        parts.append("]")

    parts.append("[Flags: readonly advisory_only memory_write=false graphiti_write=false neo4j_write=false kernel_mutation=false]")

    ctx = " ".join(parts)
    if len(ctx) > CONTEXT_CHAR_BUDGET:
        ctx = ctx[:CONTEXT_CHAR_BUDGET] + "..."
    return ctx


def build_true_runtime_payload(
    user_message: str,
    *,
    state: dict[str, Any],
    turns: list[dict[str, Any]],
    memory: PersonalMemorySidecar | None = None,
) -> str:
    """
    Build the message field for /api/brody/chat.
    User message ALWAYS comes first and is the primary content.
    Context (if enabled) is appended as a lightweight suffix after a separator.
    This ensures Brody's intent detection works on the user's actual message.
    """
    runtime_mode = state.get("runtime_mode", "true_runtime")
    message = user_message

    if runtime_mode == "raw_api":
        # Send only the raw user message, no context
        return message

    if runtime_mode == "compact_debug":
        # Legacy: full context wrapper
        if state.get("auto_context", True) and memory:
            ctx = build_memory_context_packet(state, user_message, turns, memory)
            if ctx:
                message = f"{user_message}\n\n[CTX: {ctx}]"
        return message

    # true_runtime (default): user message first, lightweight context suffix
    if state.get("auto_context", True) and memory:
        ctx = build_memory_context_packet(state, user_message, turns, memory)
        if ctx:
            message = f"{user_message}\n[local_ctx: {ctx}]"

    return message


# ── UTF-8 safe print ────────────────────────────────────────────────────────

def safe_print(text: str, **kwargs) -> None:
    """Print text safely, avoiding UnicodeEncodeError on Windows consoles."""
    try:
        print(text, **kwargs)
    except UnicodeEncodeError:
        encoded = text.encode(sys.stdout.encoding or "utf-8", errors="replace")
        sys.stdout.buffer.write(encoded + b"\n")


# ── Payload builder ─────────────────────────────────────────────────────────

def build_payload(
    message: str,
    *,
    language: str = DEFAULT_LANGUAGE,
    session_id: str = DEFAULT_SESSION,
    compact: bool = True,
    debug: bool = False,
) -> dict[str, Any]:
    """Build the JSON payload for /api/brody/chat."""
    return {
        "message": message,
        "language": language,
        "session_id": session_id,
        "compact": compact,
        "debug": debug,
    }


# ── Response extractors ─────────────────────────────────────────────────────

def extract_answer(data: dict[str, Any]) -> str:
    """Extract the best text answer from a Brody response dict."""
    # Priority: final_answer > response_md > response > raw repr
    fa = data.get("final_answer", "")
    if fa and isinstance(fa, str) and len(fa.strip()) > 5:
        return fa.strip()
    rmd = data.get("response_md", "")
    if rmd and isinstance(rmd, str) and len(rmd.strip()) > 5:
        return rmd.strip()
    resp = data.get("response", "")
    if resp and isinstance(resp, str) and len(resp.strip()) > 5:
        return resp.strip()
    # Fallback: compact JSON of the whole response
    return json.dumps(data, ensure_ascii=False, indent=2)


def extract_boundary(data: dict[str, Any]) -> dict[str, Any]:
    """Extract boundary flags from a Brody response dict."""
    keys = [
        "decision_authority", "emits_act", "emits_verdict",
        "memory_write", "graphiti_write", "neo4j_write",
        "kernel_mutation", "readonly", "compact", "debug",
    ]
    result: dict[str, Any] = {}
    for k in keys:
        result[k] = data.get(k, "UNKNOWN")
    return result


def format_boundary_line(boundary: dict[str, Any]) -> str:
    """Format boundary flags as a single line."""
    parts = []
    for k in [
        "decision_authority", "emits_act", "memory_write",
        "graphiti_write", "neo4j_write", "kernel_mutation",
    ]:
        parts.append(f"{k}={boundary.get(k, 'UNKNOWN')}")
    return "  ".join(parts)


# ── HTTP call ───────────────────────────────────────────────────────────────

def call_brody_api(endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
    """
    POST to /api/brody/chat and return parsed JSON.
    Raises ConnectionError, TimeoutError, ValueError on failure.
    """
    import urllib.request
    import urllib.error

    url = f"{endpoint.rstrip('/')}/api/brody/chat"
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            raw = resp.read()
            return json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        raise ConnectionError(f"HTTP {e.code}: {body}")
    except urllib.error.URLError as e:
        raise ConnectionError(f"Cannot reach {url}: {e.reason}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from server: {e}")


# ── Transcript ───────────────────────────────────────────────────────────────

def ensure_transcript_dir() -> Path:
    """Create and return the transcript directory."""
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    return TRANSCRIPT_DIR


def write_transcript_jsonl(session_id: str, entry: dict[str, Any]) -> None:
    """Append a turn to the session JSONL transcript."""
    d = ensure_transcript_dir()
    path = d / f"{session_id}.jsonl"
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def write_transcript_md(session_id: str, turns: list[dict[str, Any]]) -> None:
    """Write the full session as a markdown transcript."""
    d = ensure_transcript_dir()
    path = d / f"{session_id}.md"
    lines = [
        f"# Brody Terminal Chat — Session: {session_id}",
        f"# Started: {datetime.now(timezone.utc).isoformat()}",
        "",
    ]
    for i, turn in enumerate(turns, 1):
        lines.append(f"## Turn {i}")
        lines.append(f"**You**: {turn.get('user_message', '')}")
        lines.append("")
        lines.append(f"**Brody**: {turn.get('final_answer', '')}")
        lines.append("")
        b = turn.get("boundary", {})
        lines.append(f"*Boundary: {format_boundary_line(b)}*")
        lines.append("")
        lines.append("---")
        lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ── Command handlers ────────────────────────────────────────────────────────

def handle_command(
    cmd: str,
    state: dict[str, Any],
    last_response: Optional[dict[str, Any]],
    turns: list[dict[str, Any]],
    memory: "PersonalMemorySidecar | None" = None,
) -> tuple[bool, bool]:
    """
    Handle a slash command. Returns (should_continue, save_needed).
    """
    parts = cmd.strip().split(maxsplit=1)
    action = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    if action in ("/exit", "/quit", "/q"):
        safe_print("\nBrody: Au revoir. Session sauvegardée.")
        return False, True

    elif action == "/help":
        safe_print("""
Commandes disponibles:
  /help           Ce message
  /exit, /quit    Quitter
  /debug on/off   Activer/désactiver debug
  /compact on/off Activer/désactiver compact
  /session <id>   Changer session_id
  /status         Afficher l'état du client
  /save           Sauvegarder le transcript
  /last           Réafficher la dernière réponse
  /raw            Afficher le JSON brut
  /memory status  Afficher l'état de la mémoire personnelle
  /memory show    Afficher les entrées récentes
  /memory candidates  Afficher les candidats en attente
  /memory promote-local <id>  Promouvoir un candidat (local only)
  /memory reject <id>  Rejeter un candidat
  /memory search <q>  Rechercher dans la mémoire
  /memory links   Afficher les liens readonly
  /context on/off Activer/désactiver le contexte mémoire auto
  /context show   Afficher le dernier contexte injecté
""")

    elif action == "/debug":
        if arg.lower() == "on":
            state["debug"] = True
            state["compact"] = False
            safe_print("debug=ON  compact=OFF")
        else:
            state["debug"] = False
            state["compact"] = True
            safe_print("debug=OFF  compact=ON")

    elif action == "/compact":
        if arg.lower() == "on":
            state["compact"] = True
            state["debug"] = False
            safe_print("compact=ON  debug=OFF")
        else:
            state["compact"] = False
            safe_print("compact=OFF")

    elif action == "/session":
        if arg:
            state["session_id"] = arg.strip()
            safe_print(f"session_id = {state['session_id']}")

    elif action == "/save":
        return True, True

    elif action == "/last":
        if last_response:
            safe_print("\n--- Dernière réponse Brody ---")
            safe_print(extract_answer(last_response))
            safe_print("---")
        else:
            safe_print("Aucune réponse précédente.")

    elif action == "/raw":
        if last_response:
            safe_print(json.dumps(last_response, ensure_ascii=False, indent=2))
        else:
            safe_print("Aucune réponse précédente.")

    # ── Memory commands ─────────────────────────────────────────────────

    elif action == "/memory" and memory:
        sub = arg.split(maxsplit=1)
        sub_cmd = sub[0].lower() if sub else ""
        sub_arg = sub[1] if len(sub) > 1 else ""

        if sub_cmd == "status":
            mem_count = memory.memory_count()
            cand_count = memory.candidate_count()
            links = memory.get_readonly_links()
            safe_print(f"""
Mémoire personnelle (LOCAL ONLY):
  Entrées:            {mem_count}
  Candidats:          {cand_count}
  Liens readonly:     {len(links.get('links', []))}
  Promotion autorisée: False
  Graphiti write:     False
  Neo4j write:        False
""")

        elif sub_cmd == "show":
            entries = memory.read_memory_entries(limit=10)
            if entries:
                for e in reversed(entries):
                    safe_print(f"[{e['topic']}] {e['content'][:120]}  ({e['timestamp'][:19]})")
            else:
                safe_print("Aucune entrée mémoire personnelle.")

        elif sub_cmd == "candidates":
            candidates = memory.read_candidates(limit=10)
            if candidates:
                for c in reversed(candidates):
                    safe_print(f"[{c['id'][:16]}][{c['candidate_type']}] {c['content'][:120]}")
            else:
                safe_print("Aucun candidat en attente.")

        elif sub_cmd == "promote-local":
            if sub_arg:
                result = memory.promote_candidate(sub_arg.strip())
                if result:
                    safe_print(f"Promu: {result['id'][:16]} → personal_memory (LOCAL_PERSONAL_MEMORY_ONLY)")
                    safe_print("memory_write=False  graphiti_write=False  neo4j_write=False")
                else:
                    safe_print(f"Candidat {sub_arg[:16]} non trouvé ou déjà traité.")
            else:
                safe_print("Usage: /memory promote-local <id>")

        elif sub_cmd == "reject":
            if sub_arg:
                ok = memory.reject_candidate(sub_arg.strip())
                safe_print("Candidat rejeté (local)." if ok else "Candidat non trouvé.")
            else:
                safe_print("Usage: /memory reject <id>")

        elif sub_cmd == "search":
            if sub_arg:
                results = memory.search_unified(sub_arg.strip(), limit=8)
                mem = results["personal_memory"]
                cand = results["pending_candidates"]
                safe_print(f"\nMémoire ({len(mem)} hits):")
                for m in mem[:4]:
                    safe_print(f"  [{m['topic']}] {m['content'][:100]}")
                safe_print(f"\nCandidats ({len(cand)} hits):")
                for c in cand[:4]:
                    safe_print(f"  [{c['candidate_type']}] {c['content'][:100]}")
            else:
                safe_print("Usage: /memory search <query>")

        elif sub_cmd == "links":
            links = memory.get_readonly_links()
            safe_print(f"Liens readonly: {len(links.get('links', []))}")
            for lk in links.get("links", []):
                safe_print(f"  - {lk.get('label', '?')}: {lk.get('status', '?')}")

        elif sub_cmd == "gate":
            gate_sub = sub_arg.split(maxsplit=1)
            gate_cmd = gate_sub[0].lower() if gate_sub else "status"
            gate_arg = gate_sub[1] if len(gate_sub) > 1 else ""

            if gate_cmd == "status":
                from scripts.brody_memory_intake_gate import load_candidates
                candidates = load_candidates()
                safe_print(f"""
Intake Gate Status:
  Mode:              dry-run par défaut
  Pending candidates: {len(candidates)}
  Write autorisé:    False (nécessite 3 env vars)
  Neo4j configuré:   {'Oui' if os.environ.get('NEO4J_URI') else 'Non'}
  Sortie:            _local_audits/BRODY_PERSONAL_SIDECAR_TO_REAL_INTAKE_GATE_V1/
""")

            elif gate_cmd == "locate":
                safe_print("Lancement du pipeline locator...")
                from scripts.brody_memory_pipeline_locator import locate_pipeline
                report = locate_pipeline()
                safe_print(f"Pipeline trouvé: {report['pipeline_found']}")
                safe_print(f"Import count historique: {report['expected_import_count']}")
                safe_print(f"Rollback plan: {'Oui' if report['rollback_plan'] else 'Non'}")

            elif gate_cmd == "dry-run":
                safe_print("Dry-run intake gate...")
                from scripts.brody_memory_intake_gate import run_authorized_dry_run
                report = run_authorized_dry_run()
                safe_print(f"Convertis: {report['converted_count']}  Rejetés: {report['rejected_count']}")
                safe_print(f"Plan: {report['plan_path']}")
                env = report.get("envelope", {})
                if env:
                    safe_print(f"Sovereign: step_count={env.get('sequence_step_count_after')} accepted={env.get('sequence_accepted')}")
                safe_print("neo4j_write=False  graphiti_write=False  memory_write=False")

            elif gate_cmd == "prepare-write":
                safe_print("Prepare-write (aucun write)...")
                from scripts.brody_memory_intake_gate import run_authorized_prepare_write
                report = run_authorized_prepare_write()
                safe_print(f"Convertis: {report['converted_count']}  Rejetés: {report['rejected_count']}")
                env = report.get("envelope", {})
                if env:
                    safe_print(f"Sovereign: step_count={env.get('sequence_step_count_after')} accepted={env.get('sequence_accepted')}")
                safe_print(f"Snapshot: {report['snapshot_path']}")
                safe_print(f"Rollback: {report['rollback_path']}")
                safe_print(f"Read link: {report['read_link_path']}")
                safe_print("neo4j_write=False  graphiti_write=False")

            elif gate_cmd == "envelope":
                from scripts.brody_memory_intake_gate import load_last_sovereign_envelope, get_sequence_state
                env = load_last_sovereign_envelope()
                seq = get_sequence_state()
                if env:
                    safe_print(f"""
Sovereign Envelope:
  action:          {env.get('sequence_action')}
  step before:     {env.get('sequence_step_count_before')}
  step after:      {env.get('sequence_step_count_after')}
  accepted:        {env.get('sequence_accepted')}
  graphiti_write:  {env.get('graphiti_write_requested')}
  neo4j_write:     {env.get('neo4j_write_requested')}
  decision_auth:   {env.get('decision_authority')}
  kernel_mutation: {env.get('kernel_mutation')}
""")
                else:
                    safe_print("Aucune envelope générée.")
                if seq:
                    safe_print(f"Sequence: step_count={seq['sequence_step_count']} status={seq['last_status']}")

            elif gate_cmd == "sequence":
                from scripts.brody_memory_intake_gate import get_sequence_state
                seq = get_sequence_state()
                safe_print(f"""
Sequence Governor:
  step_count:      {seq['sequence_step_count']}
  last_action:     {seq['last_action']}
  last_status:     {seq['last_status']}
  decision_auth:   {seq['decision_authority']}
  kernel_mutation: {seq['kernel_mutation']}
""")

            elif gate_cmd == "write-confirm":
                safe_print("""
WRITE RÉEL — Commandes manuelles requises:

1. Définir les variables d'approbation :
   $env:BRODY_MEMORY_GATE_MODE = "WRITE"
   $env:BRODY_MEMORY_WRITE_APPROVED = "I_UNDERSTAND_LOCAL_NEO4J_WRITE"
   $env:BRODY_MEMORY_TARGET = "LOCAL_NEO4J_7688_ONLY"

2. Définir les credentials Neo4j :
   $env:NEO4J_URI = "bolt://127.0.0.1:7688"
   $env:NEO4J_USER = "neo4j"
   $env:NEO4J_PASSWORD = "votre_mot_de_passe"

3. Lancer le write :
   python scripts/brody_memory_intake_gate.py write

4. Vérifier le ROLLBACK_PLAN avant exécution.
   Aucun write n'est déclenché depuis ce terminal.
""")
            else:
                safe_print(f"Gate sub-command inconnue: {gate_cmd}")

    elif action == "/context":
        if arg.lower() == "on":
            state["auto_context"] = True
            safe_print("Contexte mémoire auto: ON")
        elif arg.lower() == "off":
            state["auto_context"] = False
            safe_print("Contexte mémoire auto: OFF")
        elif arg.lower() == "show":
            ctx = state.get("_last_context", "")
            if ctx:
                safe_print(f"\n--- Dernier contexte injecté ({len(ctx)} chars) ---")
                safe_print(ctx[:2000])
                safe_print("---")
            else:
                safe_print("Aucun contexte injecté.")

    elif action == "/runtime":
        if arg.lower() in ("status", ""):
            safe_print(f"runtime_mode = {state.get('runtime_mode', 'true_runtime')}")
        elif arg.lower() == "true":
            state["runtime_mode"] = "true_runtime"
            safe_print("runtime_mode = true_runtime (message utilisateur prioritaire)")
        elif arg.lower() == "raw":
            state["runtime_mode"] = "raw_api"
            safe_print("runtime_mode = raw_api (message brut, sans contexte)")
        elif arg.lower() == "compact":
            state["runtime_mode"] = "compact_debug"
            safe_print("runtime_mode = compact_debug (contexte complet)")

    elif action == "/status":
        mem_info = ""
        if memory:
            mem_info = f"""
  personal_memory: {memory.memory_count()} entrées
  candidates:      {memory.candidate_count()}
  auto_context:    {state.get('auto_context', True)}
  runtime_mode:    {state.get('runtime_mode', 'true_runtime')}
  last_ctx_size:   {len(state.get('_last_context', ''))} chars"""
        safe_print(f"""
État client:
  endpoint:    {state['endpoint']}
  session_id:  {state['session_id']}
  language:    {state['language']}
  compact:     {state['compact']}
  debug:       {state['debug']}
  turns:       {len(turns)}{mem_info}
""")

    else:
        safe_print(f"Commande inconnue: {cmd}. Tapez /help.")

    return True, False


# ── Main loop ───────────────────────────────────────────────────────────────

def main(endpoint: str = DEFAULT_ENDPOINT) -> None:
    """Run the interactive Brody terminal chat loop."""
    # ── UTF-8 setup ─────────────────────────────────────────────────────
    if sys.stdout.encoding and sys.stdout.encoding.upper() != "UTF-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if sys.stderr.encoding and sys.stderr.encoding.upper() != "UTF-8":
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    # ── State ───────────────────────────────────────────────────────────
    state: dict[str, Any] = {
        "endpoint": endpoint,
        "session_id": DEFAULT_SESSION,
        "language": DEFAULT_LANGUAGE,
        "compact": True,
        "debug": False,
        "auto_context": True,
        "runtime_mode": "true_runtime",
        "_last_context": "",
    }
    memory = PersonalMemorySidecar()
    last_response: Optional[dict[str, Any]] = None
    turns: list[dict[str, Any]] = []

    safe_print(f"Brody Terminal Chat Client V1")
    safe_print(f"Endpoint: {endpoint}")
    safe_print(f"Session:  {state['session_id']}")
    safe_print(f"Mode:     compact=True  debug=False")
    safe_print(f"Tapez /help pour les commandes, /exit pour quitter.\n")

    running = True
    while running:
        try:
            user_input = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            safe_print("\nBrody: Session interrompue. Au revoir.")
            break

        if not user_input:
            continue

        # Commands
        if user_input.startswith("/"):
            running, save_needed = handle_command(
                user_input, state, last_response, turns, memory
            )
            if save_needed:
                if turns:
                    write_transcript_md(state["session_id"], turns)
                    safe_print(f"Transcript saved: {TRANSCRIPT_DIR / state['session_id']}.md")
                if not running:
                    break
            continue

        # ── Send to Brody (with optional context injection) ─────────────
        message = build_true_runtime_payload(
            user_input, state=state, turns=turns, memory=memory
        )

        payload = build_payload(
            message,
            language=state["language"],
            session_id=state["session_id"],
            compact=state["compact"],
            debug=state["debug"],
        )

        try:
            data = call_brody_api(state["endpoint"], payload)
        except ConnectionError as e:
            safe_print(f"\n[ERREUR] API injoignable: {e}")
            safe_print("Vérifiez que l'API est lancée sur http://127.0.0.1:8000")
            safe_print("Tapez /status pour l'état, /exit pour quitter.\n")
            continue
        except TimeoutError:
            safe_print("\n[ERREUR] Timeout - l'API n'a pas répondu dans le délai.")
            continue
        except ValueError as e:
            safe_print(f"\n[ERREUR] Réponse invalide: {e}")
            continue

        last_response = data

        # ── Display answer ──────────────────────────────────────────────
        answer = extract_answer(data)
        safe_print(f"\nBrody > {answer}\n")

        # ── Display boundary ────────────────────────────────────────────
        boundary = extract_boundary(data)
        safe_print(f"Boundary: {format_boundary_line(boundary)}")

        # ── Auto-capture memory signal ──────────────────────────────────
        candidate_captured = False
        if detect_memory_signal(user_input):
            memory.add_candidate(
                candidate_type="auto_detected_signal",
                content=user_input[:300],
                user_msg=user_input,
                brody_answer=answer,
            )
            candidate_captured = True
            safe_print(f"Memory: candidate captured locally  review_required=True  graphiti_write=False  neo4j_write=False")

        # ── Context info line ───────────────────────────────────────────
        mem_hits = len(memory.search_memory(user_input, limit=10))
        cand_count = memory.candidate_count()
        links = memory.get_readonly_links()
        safe_print(f"Context: session_turns={len(turns)}  personal_memory_hits={mem_hits}  candidates={cand_count}  readonly_links={'active' if links.get('links') else 'none'}")
        safe_print(f"Memory: local_candidate_captured={candidate_captured}  promotion_allowed=False\n")

        # ── Source check ────────────────────────────────────────────────
        source = data.get("final_answer_source", data.get("voice_source", ""))
        topic = data.get("topic", "")
        safe_print(f"Source: final_answer_source={source}  topic={topic}")

        _fallback_sources = {
            "SEMANTIC_ADVISORY_NO_MEMORY", "FALLBACK", "PLACEHOLDER",
            "FREEZE_METRICS_AND_MATRIX",
        }
        if source in _fallback_sources:
            safe_print("Warning: terminal may be using fallback path, not true Brody runtime.")
            safe_print("  Try /runtime true or /context off for cleaner interaction.\n")

        # ── Record turn ─────────────────────────────────────────────────
        turn_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": state["session_id"],
            "user_message": user_input,
            "final_answer": answer,
            "decision_authority": boundary.get("decision_authority", "UNKNOWN"),
            "emits_act": boundary.get("emits_act", "UNKNOWN"),
            "memory_write": boundary.get("memory_write", "UNKNOWN"),
            "graphiti_write": boundary.get("graphiti_write", "UNKNOWN"),
            "neo4j_write": boundary.get("neo4j_write", "UNKNOWN"),
            "kernel_mutation": boundary.get("kernel_mutation", "UNKNOWN"),
            "compact": state["compact"],
            "debug": state["debug"],
            "boundary": boundary,
        }
        turns.append(turn_entry)
        write_transcript_jsonl(state["session_id"], turn_entry)

    # ── Final save ──────────────────────────────────────────────────────
    if turns:
        write_transcript_md(state["session_id"], turns)
        safe_print(f"\nTranscript saved: {TRANSCRIPT_DIR / state['session_id']}.md")


if __name__ == "__main__":
    endpoint = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ENDPOINT
    main(endpoint)
