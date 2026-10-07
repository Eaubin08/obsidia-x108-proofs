"""RED tranche 2 — order independence of T5 / T6 / T9 outcomes and the hard-zero authority boundary
(spec §1, §9.1 multi-cause ordering, §9.3 bundle digest, §11)."""
from __future__ import annotations

import ast
import itertools
import pathlib

from tests.b8.red2_support import (
    FRAME_A, FRAME_B, evaluate, evidence, ids, latest, make_claim, make_record, request, snapshot, verification,
)

HERE = pathlib.Path(__file__).resolve().parent
RED2_FILES = sorted(HERE.glob("test_b8_*_red.py")) + [HERE / "red2_support.py"]


def _fingerprint(result):
    body = result.bundle.bundle_id if getattr(result, "bundle", None) is not None else None
    return (result.verdict, tuple(r.value for r in result.receipt.reasons), result.receipt.canonical_json(),
            result.receipt.receipt_id, body)


def test_t5_outcome_is_independent_of_artifact_order(b8):
    claim = make_claim(b8, "det-t5")
    snap = snapshot(b8, [(claim, make_record(b8, claim, "SUPPORTED"))], slot_id=claim.slot_id)
    arts = [verification(b8, claim, claim_version=2), verification(b8, claim, family="FORMAL_PROOF_VERIFIER"),
            evidence(b8, claim)]
    refs = ids(*arts)
    prints = {_fingerprint(evaluate(b8, snap, request(b8, claim, latest(snap, claim), "VERIFIED", refs=refs), perm))
              for perm in itertools.permutations(arts)}
    assert len(prints) == 1
    (fp,) = prints
    assert list(fp[1]) == ["ref_binding_mismatch", "verifier_inadmissible"]


def _t6_entries(b8):
    cand = make_claim(b8, "det-t6")
    occ_a = make_claim(b8, "occ-a", start=50, end=60, fid=FRAME_A)
    occ_b = make_claim(b8, "occ-b", start=0, end=10, fid=FRAME_B)
    con = make_claim(b8, "contra", start=20, end=30, fid=FRAME_A)
    return cand, [(cand, make_record(b8, cand, "VERIFIED")), (occ_a, make_record(b8, occ_a, "PROMOTED")),
                  (occ_b, make_record(b8, occ_b, "PROMOTED")), (con, make_record(b8, con, "CONTESTED"))]


def test_t6_reasons_and_receipt_are_independent_of_snapshot_order(b8):
    cand, entries = _t6_entries(b8)
    prints = set()
    for perm in itertools.permutations(entries):
        snap = snapshot(b8, list(perm), slot_id=cand.slot_id)
        prints.add(_fingerprint(evaluate(b8, snap, request(b8, cand, latest(snap, cand), "PROMOTED", revision=4))))
    assert len(prints) == 1
    (fp,) = prints
    assert list(fp[1]) == ["open_contradiction", "slot_occupied", "stale_request", "temporal_relation_indeterminate"]


def test_t9_bundle_is_independent_of_snapshot_order(b8):
    new = make_claim(b8, "det-new")
    pred = make_claim(b8, "det-pred", start=10, end=20)
    bystander = make_claim(b8, "det-bystander", start=100, end=200)
    entries = [(new, make_record(b8, new, "VERIFIED")), (pred, make_record(b8, pred, "PROMOTED")),
               (bystander, make_record(b8, bystander, "PROMOTED"))]
    prints = set()
    for perm in itertools.permutations(entries):
        snap = snapshot(b8, list(perm), slot_id=new.slot_id)
        req = request(b8, new, latest(snap, new), "PROMOTED", supersedes_claim_id=pred.claim_id,
                      supersedes_record_id=latest(snap, pred).record_id)
        result = evaluate(b8, snap, req)
        assert result.verdict is b8.TransitionVerdict.APPLIED
        prints.add((_fingerprint(result), result.bundle.bundle_digest))
    assert len(prints) == 1


def test_boundary_stays_hard_false_after_tranche2_transitions(b8):
    claim = make_claim(b8, "authority")
    snap = snapshot(b8, [(claim, make_record(b8, claim, "PROMOTED"))], slot_id=claim.slot_id)
    ev = evidence(b8, claim, kind="WITHDRAWAL")
    evaluate(b8, snap, request(b8, claim, latest(snap, claim), "INVALIDATED", refs=ids(ev)), [ev])
    assert b8.BOUNDARY["memory_write"] is False
    assert b8.BOUNDARY["emits_act"] is False
    assert b8.BOUNDARY["kernel_mutation"] is False
    assert b8.BOUNDARY["kx108_knowledge_promotion_role"] == "NONE"


def test_red2_tests_need_no_runtime_authority_memory_or_network():
    forbidden = ("app.cognition", "app.harness", "apps", "periphery", "graphiti", "neo4j", "requests", "httpx",
                 "urllib", "socket", "http", "aiohttp", "subprocess")
    red1 = {"test_b8_identity_red.py"}  # RED-1 imports B6 canonical_json as test-only conformance evidence
    for path in RED2_FILES:
        if path.name in red1 or path.name.startswith(("test_b8_authority_boundary", "test_b8_cas", "test_b8_receipts",
                                                      "test_b8_types")):
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            mods = ([a.name for a in node.names] if isinstance(node, ast.Import)
                    else [node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
            for m in mods:
                assert not any(m == p or m.startswith(p + ".") for p in forbidden), (path.name, m)
