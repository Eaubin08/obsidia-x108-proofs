from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List


def load_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def write_json(path: str | Path, payload: Dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def normalize_lines(text: str) -> list[str]:
    """Normalize SOP text into ordered procedural lines.

    Handles numbered lists, bullets, Markdown checkboxes, semicolons used as
    compact SOP separators, and keeps order intact. It does not rewrite meaning.
    """
    normalized: list[str] = []
    expanded = text.replace(";", "\n")
    for raw in expanded.splitlines():
        line = raw.strip()
        line = re.sub(r"^[-*•]+\s*", "", line)
        line = re.sub(r"^\[[ xX]\]\s*", "", line)
        line = re.sub(r"^\d+[.)]\s*", "", line)
        line = line.strip(" \t")
        if line:
            normalized.append(line)
    return normalized


def infer_actor(text: str) -> str:
    lower = text.lower()
    if any(w in lower for w in ["client", "customer", "utilisateur", "user"]):
        return "external_user_or_client"
    if any(w in lower for w in ["manager", "lead", "reviewer", "responsable", "supervisor"]):
        return "human_reviewer"
    if any(w in lower for w in ["agent", "bot", "brody", "claude", "workflow"]):
        return "agentic_worker"
    if any(w in lower for w in ["x108", "gate", "kernel", "preuve", "evidence"]):
        return "governance_boundary"
    return "operator_or_agent"


def infer_tools(text: str) -> list[str]:
    lower = text.lower()
    tools = []
    hints = {
        "email_or_messaging": ["email", "mail", "slack", "teams", "message", "envoyer"],
        "banking_or_payment_tool": ["bank", "banque", "iban", "virement", "payment", "payer"],
        "repo_or_ci_cd": ["repo", "git", "github", "deploy", "ci", "pipeline", "production"],
        "document_system": ["contract", "contrat", "pdf", "doc", "invoice", "facture"],
        "identity_access_system": ["access", "accès", "permission", "password", "secret", "token"],
        "obsidia_x108_boundary": ["x108", "obsidia", "kernel", "packet", "context"],
    }
    for name, words in hints.items():
        if any(w in lower for w in words):
            tools.append(name)
    return sorted(set(tools))


def infer_conditions(text: str) -> list[str]:
    lower = text.lower()
    conditions = []
    for marker in ["if", "si ", "unless", "sauf", "when", "quand", "after", "après", "before", "avant"]:
        if marker in lower:
            conditions.append(f"condition_marker:{marker.strip()}")
    return conditions


def unique_keep_order(values: Iterable[str]) -> list[str]:
    seen = set()
    out = []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out
