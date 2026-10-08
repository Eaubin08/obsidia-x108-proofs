"""V0.1 C4.2: OFFLINE, local cross-repository contract-composition probe.

Executes selected REAL code from pinned Trading and GPS checkouts, reads the
CSSA read-only status file, confronts the outputs with C4/C4.1 core contracts.
It is NOT a production multi-tenant action/runtime or real KX108 experiment.
No downloads, network transport, external sources, actions, tickets or secrets.
Requires three locally available Git checkouts. Missing/unpinned/dirty
checkouts fail closed. Does not write into any repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

EXPECTED_EXTERNAL = {
    "gps": ("Eaubin08/obsidia-gps-defense-",
            "d1221fce6914274f7b0c445a829739367b0c6abb"),
    "trading": ("Eaubin08/OBSIDIA_TRADING",
                "4c2438d97191ec780369b230e597c711471243ca"),
    "cssa": ("Eaubin08/cssa-v01--entreprise-universelle-domaien-obsidia-",
             "a3125ce211e0c55d6608b39396f1f7633dbab72c"),
}
EXPECTED_CORE_ANCESTOR = "f08623c28681151703a29c79e3452e45bd323ea0"
SCHEMA = "OBSIDIA_V01_C42_OFFLINE_INTERREPO_COMPOSITION_V0"
SUCCESS = "OFFLINE_CROSSREPO_CONTRACT_COMPOSITION_PASS_NO_LIVE_EXECUTION"

NETWORK_BLOCK = """
import socket
def _no_network(*_args, **_kwargs):
    raise RuntimeError("C42_NETWORK_TRANSPORT_FORBIDDEN")
socket.socket.connect = _no_network
socket.socket.connect_ex = _no_network
socket.create_connection = _no_network
"""

GPS_PROBE = r"""
import importlib.util
import json
from pathlib import Path

def import_path(filename, name):
    spec = importlib.util.spec_from_file_location(name, filename)
    mod = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

root = Path.cwd()
gate = import_path(root / 'evidence-pipeline/public_domain_bridge/gps_x108_gate.py',
                   'c42_gps_gate')
guard = import_path(root / 'evidence-pipeline/public_domain_bridge/gps_public_claim_guard_v0.py',
                    'c42_gps_claim_guard')
envelope = json.loads((root / 'evidence/hostile-rf-partial/window_C_observation_envelope.json').read_text(encoding='utf-8'))
classification = guard.classify_public_gps_evidence_claim_v0(envelope)
normalization = gate.normalize_kernel_response_v0({'x108_gate': 'HOLD', 'domain': gate.DOMAIN})
conflicted = gate.normalize_kernel_response_v0({'x108_gate': 'BLOCK', 'verdict': 'ACT', 'domain': gate.DOMAIN})
print('C42_PROBE=' + json.dumps({
    'domain': gate.DOMAIN,
    'observation_source_proof_level': envelope['proof_level'],
    'observation_input_hash': envelope['input_hash'],
    'claim_status': classification['claim_status'],
    'attack_causality_proven': classification['spoofing_causal_attribution_proven'],
    'normalization': list(normalization),
    'conflicted_authority': list(conflicted),
    'allowed_to_act': classification['allowed_to_act']
}, sort_keys=True))
"""

TRADING_PROBE = r"""
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

from execution.binder.proof_policy import ProofPolicy, ProofOutcome
from governance.bridge.kx108_client import RealKX108Client
from tests.unit.test_reference_runtime_proof_policy import _build_engine
from proof.receipts.receipt_store import ReceiptStore

def reply(url, json, timeout):  # noqa: A002
    if json.get('domain') != 'trading':
        raise AssertionError('C42_TRADING_DOMAIN_INCORRECT')
    return SimpleNamespace(
        raise_for_status=lambda: None,
        json=lambda: {'x108_gate': 'HOLD', 'domain': 'trading'},
    )

with tempfile.TemporaryDirectory(prefix='c42-trading-') as work:
    engine, broker = _build_engine(
        kx108_client=RealKX108Client(base_url='http://127.0.0.1:1/mock'),
        proof_policy=ProofPolicy.REQUIRED,
        proof=ReceiptStore(Path(work) / 'receipt.jsonl'),
    )
    with patch('requests.post', side_effect=reply):
        outcome = engine.run_cycle()
    result = {
        'domain': 'trading',
        'proof_policy': engine.proof_policy.value,
        'mode': engine.mode.value,
        'authority': outcome.authority.value if outcome.authority else None,
        'fake_broker_submit_count': len(broker.submit_calls),
        'proof_outcome': outcome.proof_outcome.value,
        'external_effect': bool(outcome.touched_the_market),
        'kernel_http_mocked': True,
    }

with patch('requests.post', return_value=SimpleNamespace(
        raise_for_status=lambda: None,
        json=lambda: {'verdict': 'ACT', 'x108_gate': 'BLOCK'})):
    conflicted = RealKX108Client(base_url='http://127.0.0.1:1/mock').evaluate_trading(
        {'domain': 'trading', 'data': {}, 'meta': {}}
    )
result['conflict_no_verdict'] = 'verdict' not in conflicted
result['transport_source'] = conflicted.get('source')
print('C42_PROBE=' + json.dumps(result, sort_keys=True))
"""

CSSA_PROBE = r"""
import json
from pathlib import Path
p = Path.cwd() / 'organizations/cssa/intake/f3h_h_real_readonly_pilot_preflight_progress_v0.json'
status = json.loads(p.read_text(encoding='utf-8'))
print('C42_PROBE=' + json.dumps({
    'schema': status['schema'],
    'status': status['status'],
    'connected_club_mailbox': status['connected_club_mailbox'],
    'connected_club_internal_documents': status['connected_club_internal_documents'],
    'operational_source_authorized': status['operational_source_authorized'],
    'pilot_started': status['pilot_started'],
    'real_native_promotions': status['real_native_promotions'],
    'external_mutation_allowed': status['external_mutation_allowed'],
}, sort_keys=True))
"""


def sha256_obj(data: Any) -> str:
    return hashlib.sha256(json.dumps(
        data, ensure_ascii=False, sort_keys=True, separators=(',', ':')
    ).encode('utf-8')).hexdigest()


def git_stdout(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args], shell=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        timeout=15, check=False,
    )
    if result.returncode:
        raise ValueError("C42_GIT_LOCAL_CHECK_FAILED")
    return result.stdout.strip()


def check_local_checkout(root: Path, *, expected_sha: str, allow_descendant: bool) -> str:
    if not root.is_dir() or not (root / ".git").exists():
        # Linked worktrees use a .git text pointer; .git exists for both.
        raise ValueError("C42_LOCAL_REPOSITORY_NOT_PRESENT")
    sha = git_stdout(root, "rev-parse", "HEAD")
    if len(sha) != 40:
        raise ValueError("C42_GIT_COMMIT_INVALID")
    if allow_descendant:
        git_stdout(root, "merge-base", "--is-ancestor", expected_sha, "HEAD")
    elif sha != expected_sha:
        raise ValueError("C42_SOURCE_NOT_AT_PINNED_COMMIT")
    if git_stdout(root, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("C42_TRACKED_WORKTREE_DIRTY")
    return sha


def run_probe(root: Path, program: str) -> dict[str, Any]:
    safe_env = {
        key: value for key, value in os.environ.items()
        if key.upper() in {
            "PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "HOME",
            "USERPROFILE", "TMP", "TEMP", "TMPDIR", "LOCALAPPDATA",
            "PROGRAMFILES", "PROGRAMFILES(X86)",
        }
    }
    safe_env["PYTHONDONTWRITEBYTECODE"] = "1"
    safe_env["PYTHONNOUSERSITE"] = "1"
    safe_env["OBSIDIA_KERNEL_URL"] = ""  # explicitly disallow live kernel
    # Socket denial is installed before importing business packages.
    result = subprocess.run(
        [sys.executable, "-B", "-c", NETWORK_BLOCK + program],
        cwd=str(root), env=safe_env, shell=False,
        capture_output=True, text=True, timeout=50, check=False,
    )
    if result.returncode:
        # No raw stderr: error outputs can accidentally contain local paths.
        raise ValueError("C42_PROBE_FAILED_OFFLINE_OR_MISSING_DEPENDENCY")
    markers = [line[10:] for line in result.stdout.splitlines()
               if line.startswith("C42_PROBE=")]
    if len(markers) != 1:
        raise ValueError("C42_PROBE_OUTPUT_NOT_EXACTLY_ONE")
    try:
        value = json.loads(markers[0])
    except json.JSONDecodeError as exc:
        raise ValueError("C42_PROBE_OUTPUT_INVALID") from exc
    if not isinstance(value, dict):
        raise ValueError("C42_PROBE_OUTPUT_NOT_OBJECT")
    return value


def verify_handoffs(
    *, gps: dict[str, Any], trading: dict[str, Any], cssa: dict[str, Any],
    registry: dict[str, Any], c41: dict[str, Any],
) -> dict[str, Any]:
    """Pure composition validator; never treats a mocked HOLD as real KX proof."""
    from periphery.enterprise_sector_claims_v0 import (
        verify_c4_evidence_registry_v0, assess_sector_claim_v0,
        STATUS_REFUSE, STATUS_CONFLICT,
    )

    verify_c4_evidence_registry_v0(registry)
    if c41.get("schema") != "OBSIDIA_V01_C41_CROSSREPO_CONTRACT_FREEZE_V0":
        raise ValueError("C42_FREEZE_CONTRACT_INVALID")
    updates = {x["sector_id"]: x for x in c41.get("domain_updates", [])}
    for sector in ("TRADING_REFERENCE", "GPS_DEFENSE_PUBLIC_EXPORT"):
        if sector not in updates or updates[sector]["tests"]["conclusion"] != "success":
            raise ValueError("C42_PINNED_DOMAIN_TESTS_UNCONFIRMED")
    if (
        gps.get("domain") != "gps_defense_aviation"
        or gps.get("observation_source_proof_level") != "RECORDED_RF_ATTACK"
        or gps.get("claim_status") != "SOURCE_LEVEL_CONFLICT_REVIEW_REQUIRED"
        or gps.get("attack_causality_proven") is not False
        or gps.get("allowed_to_act") is not False
        or gps.get("normalization") != ["HOLD", "X108_GATE_CANONICAL"]
        or gps.get("conflicted_authority") != ["HOLD", "CONTRADICTORY_KERNEL_GATE_FIELDS"]
    ):
        raise ValueError("C42_GPS_CONTRACT_OR_TRUTH_ESCALATION")
    rf = assess_sector_claim_v0(
        registry, sector_id="GPS_DEFENSE_PUBLIC_EXPORT",
        domain_id="gps_defense_aviation",
        claim_id="FGI_RF_TRAJECTORY_ANOMALY_CANDIDATE",
        source_proof_level=gps["observation_source_proof_level"],
    )
    if rf["status"] != STATUS_CONFLICT:
        raise ValueError("C42_GPS_CLAIM_QUARANTINE_BYPASSED")
    if (
        trading.get("domain") != "trading"
        or trading.get("mode") != "PAPER"
        or trading.get("proof_policy") != "REQUIRED"
        or trading.get("authority") not in ("HOLD", "BLOCK")
        or trading.get("fake_broker_submit_count") != 0
        or trading.get("external_effect") is not False
        or trading.get("kernel_http_mocked") is not True
        or trading.get("conflict_no_verdict") is not True
        or trading.get("transport_source") != "KX108_REAL"
        or trading.get("proof_outcome") != "PROVEN"
    ):
        raise ValueError("C42_TRADING_PROOF_OR_KERNEL_BOUNDARY_VIOLATION")
    forbidden_trade = assess_sector_claim_v0(
        registry, sector_id="TRADING_REFERENCE",
        domain_id="trading", claim_id="LIVE_TRADING_READY",
    )
    if forbidden_trade["status"] != STATUS_REFUSE:
        raise ValueError("C42_TRADING_LIVE_CLAIM_LEAK")
    if (
        cssa.get("schema") != "CSSA_REAL_READONLY_PILOT_PREFLIGHT_V0"
        or cssa.get("connected_club_mailbox") is not False
        or cssa.get("connected_club_internal_documents") is not False
        or cssa.get("operational_source_authorized") is not False
        or cssa.get("pilot_started") is not False
        or cssa.get("external_mutation_allowed") is not False
        or cssa.get("real_native_promotions") != 0
    ):
        raise ValueError("C42_CSSA_REAL_AUTHORITY_UNPROVEN")
    forbidden_club = assess_sector_claim_v0(
        registry, sector_id="CSSA_ADMIN_SHADOW",
        domain_id="administration", claim_id="CLUB_INTERNAL_MAILBOX_CONNECTED",
    )
    if forbidden_club["status"] != STATUS_REFUSE:
        raise ValueError("C42_CSSA_CLAIM_PROMOTION")
    return {
        "status": SUCCESS,
        "scope": "LOCAL_PINNED_SOURCE_CODE_CONTRACT_COMPOSITION",
        "gps": "RF_ATTACK_LABEL_QUARANTINED_KX_HOLD_MOCK",
        "trading": "PAPER_FAKE_BROKER_KX_HOLD_MOCK_PROOF_STORED",
        "cssa": "INTERNAL_SOURCE_ABSENT_SHADOW_ONLY",
        "actual_remote_kernel_tested": False,
        "actual_broker_used": False,
        "actual_club_mailbox_used": False,
        "multi_tenant_runtime_permission_proven": False,
        "real_external_effect": False,
        "allowed_to_act": False,
        "decision_authority": "KX108_ONLY",
    }


def run_local_composition(
    *, core_root: Path, trading_root: Path, gps_root: Path, cssa_root: Path,
) -> dict[str, Any]:
    roots = {
        "core": core_root.resolve(),
        "trading": trading_root.resolve(),
        "gps": gps_root.resolve(),
        "cssa": cssa_root.resolve(),
    }
    if len(set(roots.values())) != 4:
        raise ValueError("C42_REPOSITORY_ROOTS_MUST_BE_DISTINCT")
    # Check the three external checkouts FIRST, so missing prerequisites
    # produce the exact fail-closed dependency result even under shallow CI.
    observed = {}
    for key, (_, pinned) in EXPECTED_EXTERNAL.items():
        observed[key] = check_local_checkout(
            roots[key], expected_sha=pinned, allow_descendant=False,
        )
    observed["core"] = check_local_checkout(
        roots["core"], expected_sha=EXPECTED_CORE_ANCESTOR,
        allow_descendant=True,
    )
    c4_path = roots["core"] / "docs/runtime/V01_ENTERPRISE_C4_SECTOR_EVIDENCE_PROFILES_V0.json"
    c41_path = roots["core"] / "docs/runtime/V01_ENTERPRISE_C41_CROSSREPO_CONTRACT_FREEZE_V0.json"
    registry = json.loads(c4_path.read_text(encoding="utf8"))
    c41 = json.loads(c41_path.read_text(encoding="utf8"))
    for update in c41["domain_updates"]:
        key = "gps" if update["sector_id"] == "GPS_DEFENSE_PUBLIC_EXPORT" else "trading"
        if update["feature_sha"] != observed[key]:
            raise ValueError("C42_FEATURE_PIN_DIFFERS_FROM_FREEZE")
    if c41["blocked_domain"]["sha"] != observed["cssa"]:
        raise ValueError("C42_CSSA_PIN_DIFFERS_FROM_FREEZE")
    results = {
        "gps": run_probe(roots["gps"], GPS_PROBE),
        "trading": run_probe(roots["trading"], TRADING_PROBE),
        "cssa": run_probe(roots["cssa"], CSSA_PROBE),
    }
    verified = verify_handoffs(**results, registry=registry, c41=c41)
    report = {
        "schema": SCHEMA,
        "results": verified,
        "source_commits": observed,
        "evidence_model": "LOCAL_EXECUTED_CODE_AND_EXPORTED_OFFLINE_FIXTURES",
        "cross_repository_contract_composed": True,
        "actual_multi_repository_live_runtime_integrated": False,
        "network_access_permitted": False,
        "kernel_mutation": False,
        "monde_mutation": False,
        "main_merge": False,
    }
    report["report_sha256"] = sha256_obj(report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--trading-root", type=Path, required=True)
    parser.add_argument("--gps-root", type=Path, required=True)
    parser.add_argument("--cssa-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        report = run_local_composition(
            core_root=args.core_root, trading_root=args.trading_root,
            gps_root=args.gps_root, cssa_root=args.cssa_root,
        )
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        # Deliberately do not expose raw paths or tool traceback to stdout.
        print(json.dumps({"schema": SCHEMA, "status": "BLOCKED_FAIL_CLOSED",
                          "reason": str(exc).split(":")[0]}))
        return 2
    output = json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
