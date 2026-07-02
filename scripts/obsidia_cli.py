#!/usr/bin/env python3
"""OBSIDIA TERMINAL CLI V0 — entree unique NON SOUVERAINE.

Usage:
    python scripts/obsidia_cli.py doctor
    python scripts/obsidia_cli.py "statut du kernel"
    python scripts/obsidia_cli.py "audit merkle"

Garanties V0 (par construction, pas par option) :
  - AUCUN subprocess : le CLI ne lance jamais de commande shell.
  - Seul EXECUTE possible : doctor/status/sigma via HTTP GET readonly.
  - Aucune ecriture hors de son receipt JSONL local non souverain.
  - Pas de --apply, --commit, --deploy, --act : ces flags n'existent pas.
  - stdlib uniquement, zero import de apps/, sigma/, periphery/.
  - decision_authority = KX108_ONLY. Le terminal ne decide rien.
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
import urllib.request
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
# Volontaire : aucune dependance externe, demarrage a froid < 1s.
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
        # Les commandes contenant '#' sont entre guillemets -> garder la ligne brute.
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
# Doctor : EXECUTE readonly du terminal V0 (HTTP GET, jamais de shell)
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
# Pipeline IN
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


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    raw = " ".join(argv)
    registry = load_registry(REGISTRY_PATH)
    result = handle(raw, registry)
    receipt_path = write_receipt(registry, result)
    result["receipt"] = str(receipt_path.relative_to(REPO_ROOT))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
