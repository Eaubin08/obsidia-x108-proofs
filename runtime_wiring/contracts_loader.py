# runtime_wiring/contracts_loader.py
# Read-only contract loader — stdlib pathlib only
# No network, no writes, no import from apps/ periphery/ connectors/
# Raises FileNotFoundError if any contract file is missing (fail_closed)

from __future__ import annotations
import pathlib
from typing import Any, Dict

_CONTRACT_FILES = [
    "runtime_contracts/contracts/ContextPacket.contract.md",
    "runtime_contracts/contracts/IntentEnvelope.contract.md",
    "runtime_contracts/contracts/DecisionTicket.contract.md",
    "runtime_contracts/contracts/OS3EvidenceTicket.contract.md",
    "runtime_contracts/boundaries/COGNITIVE_REINTEGRATION_ADVISORY_ONLY.md",
    "runtime_contracts/boundaries/RSSI_EVIDENCE_ONLY.md",
    "runtime_contracts/boundaries/RGPD_COMPLIANCE_SCOPE_GUARD.md",
    "runtime_contracts/boundaries/ATLAS_READONLY_ADVISORY_ONLY.md",
]


def _find_repo_root() -> pathlib.Path:
    current = pathlib.Path(__file__).resolve().parent
    for candidate in [current, current.parent, current.parent.parent]:
        if (candidate / "runtime_contracts").is_dir():
            return candidate
    raise FileNotFoundError(
        "Cannot locate repo root: runtime_contracts/ directory not found. "
        "Run from within the obsidia-x108-proofs repo."
    )


def load_all_contracts() -> Dict[str, Any]:
    """
    Verify existence and read all 8 required contract files.

    Returns:
        {
            "status": "ALL_PRESENT" | "MISSING",
            "repo_root": str,
            "contracts": {
                "<relative_path>": {
                    "status": "PRESENT",
                    "size_bytes": int,
                    "first_200_chars": str,
                    "readonly": True,
                    "advisory_only": True,
                    "dry_run_loader": True,
                }
            },
            "missing": [<path>, ...]
        }

    Raises:
        FileNotFoundError: if any contract file is absent (fail_closed)
    """
    repo_root = _find_repo_root()
    results: Dict[str, Any] = {
        "status": "ALL_PRESENT",
        "repo_root": str(repo_root),
        "contracts": {},
        "missing": [],
    }

    for relative_path in _CONTRACT_FILES:
        full_path = repo_root / relative_path
        if not full_path.is_file():
            results["missing"].append(relative_path)
            results["status"] = "MISSING"
        else:
            content = full_path.read_text(encoding="utf-8")
            results["contracts"][relative_path] = {
                "status": "PRESENT",
                "size_bytes": len(content.encode("utf-8")),
                "first_200_chars": content[:200].replace("\n", " "),
                "readonly": True,
                "advisory_only": True,
                "dry_run_loader": True,
            }

    if results["missing"]:
        missing_list = "\n  ".join(results["missing"])
        raise FileNotFoundError(
            f"FAIL_CLOSED: {len(results['missing'])} contract file(s) missing:\n  {missing_list}"
        )

    return results
