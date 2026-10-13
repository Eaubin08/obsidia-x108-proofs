"""Runtime-independent positive controls (PC1–PC6) and self-mutation checks (SM1–SM7).
These PASS before GREEN; they prove the oracles and detectors used by the RED suite are non-vacuous."""
from __future__ import annotations

import hashlib

from tests.m33 import _harness as H


# PC1 — reference canonicalizer / identity is deterministic and discriminating; RFC 8785 numbers.
def test_pc1_reference_identity():
    a = H.ref_item_id("arm.concept", H.datum("A"))
    assert a == H.ref_item_id("arm.concept", H.datum("A")) and H.M32H.HEX64.match(a)
    assert a != H.ref_item_id("arm.concept", H.datum("B"))
    assert a != H.ref_item_id("arm.other", H.datum("A"))
    for v, txt in [(1e-7, "1e-7"), (1e-6, "0.000001"), (1e21, "1e+21"), (123456789012345680000.0, "123456789012345680000"),
                   (-0.0, "0"), (1.5, "1.5")]:
        assert H.es_number(v) == txt
    pre = '{"content":{"datum_type":"arm.text","schema_version":"v1","value":"A"},"item_kind":"arm.concept","schema_version":"m33.item.v1"}'
    assert a == hashlib.sha256(pre.encode("utf-8")).hexdigest()


# PC2 — evidence vs inference oracle is distinct.
def test_pc2_evidence_inference_distinct():
    e = H.support_obj("EVIDENCE", [("MATERIAL", "mat-1")])
    i = H.support_obj("INFERENCE", [("MATERIAL", "mat-1")])
    assert H.canonical_json(e) != H.canonical_json(i)


# PC3 — mutation probe really mutates (and the reference sees it).
def test_pc3_mutation_probe():
    payload = {"k": ["a"]}
    before = H.ref_item_id("arm.concept", H.datum(payload))
    payload["k"].append("b")
    assert H.ref_item_id("arm.concept", H.datum(payload)) != before


# PC4 — protected-path detector flags a synthetic protected change.
def test_pc4_protected_path_detector():
    paths = H.M32H.protected_paths()
    def protected(f):
        return any(f == p or f.startswith(p.rstrip("/") + "/") for p in paths)
    assert protected("app/cognition/b7/router.py") and protected("app/knowledge/b8/core.py")
    assert not protected("app/reconstruction/m33/__init__.py")


# PC5 — Candidate / competing-name detectors fire on a synthetic bad surface.
def test_pc5_collision_detectors(tmp_path):
    (tmp_path / "bad.py").write_text("class ReconstructionCandidate:\n    pass\nclass CognitivePath:\n    pass\n"
                                     "import app.knowledge.b8.core\n", encoding="utf-8")
    names = H.defined_names(tmp_path)
    assert H.candidate_names(names) == {"ReconstructionCandidate"}
    assert "CognitivePath" in names & H.M32H.public_names("app/cognition/b9")
    assert "app.knowledge.b8.core" in H.forbidden_imports(tmp_path)
    (tmp_path / "bad.py").write_text("from app.primitives.m32 import TypedCognitiveDatum\n", encoding="utf-8")
    assert H.forbidden_imports(tmp_path) == set() and H.defined_names(tmp_path) == set()


# PC6 — status / merge reference oracles are non-vacuous on certified examples.
def test_pc6_status_and_merge_oracles():
    assert H.expected_merged_status(["EVOKED_NOT_LOCKED", "EVOKED_NOT_LOCKED"]) == ("EVOKED_NOT_LOCKED", False)
    assert H.expected_merged_status(["ABSENT_IN_SCOPE", "EVOKED_NOT_LOCKED"]) == ("UNDETERMINED", True)
    assert H.expected_top_status(True, 3, []) == "FAILED_RUNTIME"
    assert H.expected_top_status(False, 0, ["UNRESOLVED_REFERENCE"]) == "INSUFFICIENT_MATERIAL"
    assert H.expected_top_status(False, 2, ["UNRESOLVED_REFERENCE"]) == "PARTIAL"
    assert H.expected_top_status(False, 2, ["CONTRADICTORY_SUPPORT"]) == "RECONSTRUCTED"


# PC7 — A23/A24 guards fire on synthetic bad surfaces and spare valid certified names.
def test_pc7_flux_and_report_label_guards(tmp_path):
    bad = ["Flux", "FluxSignal", "FluxAnalytique", "FluxVisionnaire", "FluxDirectionnel", "FluxSymbolique",
           "FluxEmotionnel", "FluxFractal", "FluxReciproque"]
    assert H.flux_names(bad) == set(bad)
    assert H.flux_names(["_historical_flux_note", "ReconstructionItem", "reflux_helper"]) == set()
    (tmp_path / "bad.py").write_text("# Flux Fractal is historical\nNOTE = 'Flux Visionnaire'\nclass FluxSignal:\n    pass\n",
                                     encoding="utf-8")
    assert H.flux_names(H.defined_names(tmp_path)) == {"FluxSignal"}
    assert H.report_label_violations(["LATENT", "REPORT_LABEL", "report_label", "ReportLabel", "Solid", "open_questions"]) == {
        "LATENT", "REPORT_LABEL", "report_label", "ReportLabel", "Solid", "open_questions"}
    assert H.report_label_violations(list(H.INTEGRATION_VALUES) + list(H.ISSUE_KINDS) + list(H.STATUS_VALUES)
                                     + ["latent_note", "item_kind", "evoked_count"]) == set()


# Self-mutation checks: each synthetic mistake is detected by the oracle the RED suite uses.
def test_sm1_evidence_inference_collapse_detected():
    collapsed = lambda kind, refs: H.support_obj("EVIDENCE", refs)  # noqa: E731
    assert H.canonical_json(collapsed("INFERENCE", [("ITEM", "a" * 64)])) != H.canonical_json(
        H.support_obj("INFERENCE", [("ITEM", "a" * 64)]))


def test_sm2_candidate_namespace_detected():
    assert H.candidate_names({"ReconstructionItem", "KnowledgeCandidate"}) == {"KnowledgeCandidate"}


def test_sm3_identity_ignoring_semantics_detected():
    def mutant_id(kind, d):
        return H.ref_item_id(kind, H.datum("constant"))
    assert mutant_id("arm.concept", H.datum("A")) == mutant_id("arm.concept", H.datum("B"))
    assert H.ref_item_id("arm.concept", H.datum("A")) != H.ref_item_id("arm.concept", H.datum("B"))


def test_sm4_merge_order_dependence_detected():
    def first_wins(statuses):
        return statuses[0]
    pair = ["ALREADY_INTEGRATED", "EVOKED_NOT_LOCKED"]
    assert first_wins(pair) != first_wins(list(reversed(pair)))
    assert H.expected_merged_status(pair) == H.expected_merged_status(list(reversed(pair)))


def test_sm5_validation_precedence_inversion_detected():
    def expected(any_failed, structural_defect):
        return "RAISE" if structural_defect else ("FAILED_RUNTIME" if any_failed else "RESULT")
    def mutant(any_failed, structural_defect):
        return "FAILED_RUNTIME" if any_failed else ("RAISE" if structural_defect else "RESULT")
    assert expected(True, True) == "RAISE" and mutant(True, True) != expected(True, True)


def test_sm6_absent_sanitized_by_merge_detected():
    def expected(scope_ref, statuses):
        return "INVALID_INTEGRATION_STATUS" if scope_ref is None and "ABSENT_IN_SCOPE" in statuses else \
            H.expected_merged_status(statuses)[0]
    def mutant(scope_ref, statuses):
        return H.expected_merged_status(statuses)[0]
    case = (None, ["ABSENT_IN_SCOPE", "EVOKED_NOT_LOCKED"])
    assert expected(*case) == "INVALID_INTEGRATION_STATUS" and mutant(*case) == "UNDETERMINED"


def test_sm7_true_effect_flag_detected():
    def violations(flags):
        return [f for f in H.EFFECT_FIELDS if flags.get(f) is not False]
    assert violations({f: False for f in H.EFFECT_FIELDS}) == []
    assert violations({**{f: False for f in H.EFFECT_FIELDS}, "emits_act": True}) == ["emits_act"]
