"""M8-C: complement commitment profiles + status derivation (non-runtime).

A ComplementCommitmentProfile describes, for one governor family AND one
construction, how the construction presents complement X (commitment) and how
that survives each scope operator. resolve_commitment applies it purely and
always returns a StatusDerivation. Unknown profiles, open doctrine cells and
unspecified operator compositions resolve to UNRESOLVED. Nothing here is an
occurrence, a truth value, evidence, verification or authority.
"""
from __future__ import annotations

import dataclasses
import json
from itertools import combinations, product

import pytest

from app.semantic.lattice import complement_commitment as CC
from app.semantic.lattice.complement_commitment import (
    SAFE_PROFILES,
    ComplementCommitment,
    ComplementCommitmentProfile,
    ConstructionType,
    DoctrineStatus,
    OperatorCell,
    ProjectionOperator,
    ProjectionRule,
    StatusDerivation,
    profile_for,
    resolve_commitment,
)
from app.semantic.lattice.event_extraction import OccurrenceStatus

C = ComplementCommitment
OP = ProjectionOperator
QUE = ConstructionType.QUE_PROPOSITION
DIRECT = ConstructionType.DIRECT_INFINITIVE_PERCEPTION


def _resolve(family, construction, *operators):
    return resolve_commitment(profile_for(family, construction), frozenset(operators), source_object_ref="u2")


@pytest.mark.parametrize("family", ["REPORT", "BELIEF"])
def test_attribution_families(family):
    base = _resolve(family, QUE)
    assert base.commitment is C.ATTRIBUTED
    assert base.derivation.rule == f"{family}/QUE_PROPOSITION:base"
    negated = _resolve(family, QUE, OP.NEGATION)
    assert negated.commitment is C.MENTIONED
    assert negated.derivation.rule == f"{family}/QUE_PROPOSITION:NEGATION:CHANGE"
    for op in (OP.QUESTION, OP.FUTURE, OP.MODAL, OP.CONDITION):
        assert _resolve(family, QUE, op).commitment is C.ATTRIBUTED
    assert _resolve(family, QUE, OP.COUNTERFACTUAL).commitment is C.UNRESOLVED


def test_believe_negation_is_not_belief_in_negation():
    negated = _resolve("BELIEF", QUE, OP.NEGATION)
    # "Marie ne croit pas que X" leaves X merely mentioned: not ATTRIBUTED(not-X).
    assert negated.commitment is C.MENTIONED
    assert negated.commitment is not C.ATTRIBUTED
    assert "complement_polarity" not in negated.to_dict()["derivation"]["provenance"]


def test_know_projects_through_negation_and_question_only():
    assert _resolve("KNOW", QUE).commitment is C.PRESUPPOSED
    for op in (OP.NEGATION, OP.QUESTION):
        res = _resolve("KNOW", QUE, op)
        assert res.commitment is C.PRESUPPOSED
        assert res.derivation.rule == f"KNOW/QUE_PROPOSITION:{op.value}:PROJECT"
    assert _resolve("KNOW", QUE, OP.NEGATION).derivation.provenance["cancellable"] is True
    for op in (OP.FUTURE, OP.MODAL, OP.CONDITION, OP.COUNTERFACTUAL):
        assert _resolve("KNOW", QUE, op).commitment is C.UNRESOLVED


@pytest.mark.parametrize("family", ["LEARN", "REMEMBER"])
def test_base_only_families(family):
    assert _resolve(family, QUE).commitment is C.PRESUPPOSED
    for op in OP:
        res = _resolve(family, QUE, op)
        assert res.commitment is C.UNRESOLVED
        assert res.derivation.provenance["doctrine_status"] in {"UNRESOLVED", "EXTERNAL_VALIDATION_NEEDED"}


def test_direct_and_propositional_perception_are_distinct_profiles():
    direct, propositional = profile_for("PERCEPTION", DIRECT), profile_for("PERCEPTION", QUE)
    assert direct is not None and propositional is not None and direct != propositional
    assert _resolve("PERCEPTION", DIRECT).commitment is C.ENTAILED
    assert _resolve("PERCEPTION", QUE).commitment is C.PRESUPPOSED
    # an entailment does not survive negation / question; it follows future / modal
    assert _resolve("PERCEPTION", DIRECT, OP.NEGATION).commitment is C.MENTIONED
    assert _resolve("PERCEPTION", DIRECT, OP.QUESTION).commitment is C.MENTIONED
    assert _resolve("PERCEPTION", DIRECT, OP.FUTURE).commitment is C.ENTAILED
    assert _resolve("PERCEPTION", DIRECT, OP.CONDITION).commitment is C.ENTERTAINED
    for op in OP:
        assert _resolve("PERCEPTION", QUE, op).commitment is C.UNRESOLVED


@pytest.mark.parametrize("family, construction", [
    ("DISCOVER", QUE), ("REALIZE", QUE), ("NOTICE", QUE), ("REGRET", QUE), ("DENY", QUE),
    ("UNKNOWN_COMPLEMENT_GOVERNOR", QUE), ("KNOW", DIRECT), ("REPORT", DIRECT), ("", QUE), (None, None),
    ("report", QUE), ("KNOW", "que"),
])
def test_unknown_profile_fails_closed(family, construction):
    assert profile_for(family, construction) is None
    res = resolve_commitment(None, frozenset(), source_object_ref="u9")
    assert res.commitment is C.UNRESOLVED
    assert res.derivation.rule == "no_profile"
    assert res.derivation.source_object_ref == "u9"


def test_operator_composition_is_not_invented():
    res = _resolve("REPORT", QUE, OP.NEGATION, OP.FUTURE)
    assert res.commitment is C.UNRESOLVED
    assert res.derivation.rule == "REPORT/QUE_PROPOSITION:operator_composition_unspecified"
    assert res.derivation.provenance["operators"] == ["FUTURE", "NEGATION"]


def test_profile_model_has_no_forbidden_dimension():
    names = {f.name for f in dataclasses.fields(ComplementCommitmentProfile)}
    assert {"governor_family", "construction_type", "base_commitment", "perspective_kind", "stance",
            "negation_projection", "question_projection", "future_projection", "modal_projection",
            "conditional_projection", "counterfactual_projection"} <= names
    forbidden = ("occurrence", "truth", "evidence", "verif", "authority", "confidence", "memory", "factive")
    assert not [n for n in names if any(f in n for f in forbidden)]
    assert not any(isinstance(getattr(p, n), bool) for p in SAFE_PROFILES.values() for n in names)


def test_change_requires_explicit_target_and_values_are_not_truth():
    with pytest.raises(ValueError):
        OperatorCell(ProjectionRule.CHANGE, None, DoctrineStatus.CLOSED_V0)
    with pytest.raises(ValueError):
        OperatorCell(ProjectionRule.PROJECT, C.MENTIONED, DoctrineStatus.CLOSED_V0)
    assert {c.value for c in C} == {"ASSERTED", "PRESUPPOSED", "ENTAILED", "ATTRIBUTED", "MENTIONED",
                                    "ENTERTAINED", "QUESTIONED", "UNRESOLVED"}
    assert not {c.value for c in C} & {s.value for s in OccurrenceStatus} - {"UNKNOWN"}
    assert {r.value for r in ProjectionRule} == {"PROJECT", "BLOCK", "CHANGE", "UNRESOLVED"}


def test_profiles_and_derivations_are_immutable():
    profile = profile_for("KNOW", QUE)
    with pytest.raises(dataclasses.FrozenInstanceError):
        profile.base_commitment = C.ASSERTED
    res = _resolve("KNOW", QUE)
    with pytest.raises(TypeError):
        res.derivation.provenance["rule"] = "x"
    with pytest.raises(TypeError):
        SAFE_PROFILES[("X", "Y")] = profile
    assert isinstance(res.derivation, StatusDerivation) and res.derivation.dimension == "commitment"


def test_module_is_not_wired_into_runtime_layers():
    import pathlib
    root = pathlib.Path(CC.__file__).parent
    # Only the shadow-only occurrence modules (M8-D1) may consume the profiles.
    shadow_consumers = {"complement_commitment.py", "occurrence_derivation.py", "occurrence_shadow.py"}
    for path in root.glob("*.py"):
        if path.name not in shadow_consumers:
            assert "complement_commitment" not in path.read_text(encoding="utf-8"), path.name
    source = pathlib.Path(CC.__file__).read_text(encoding="utf-8").lower()
    imports = [line for line in source.splitlines() if line.startswith(("import ", "from "))]
    for module in ("french_grammar", "event_extraction", "event_index", "review_join", "meta_event_relations"):
        assert not any(module in line for line in imports), module


def test_complement_commitment_property_matrix():
    metrics = dict.fromkeys((
        "CASES", "UNKNOWN_TO_ASSERTED", "UNKNOWN_TO_PRESUPPOSED", "UNKNOWN_TO_ENTAILED", "COMMITMENT_WITHOUT_DERIVATION",
        "OCCURRENCE_MUTATION", "CRASH", "PROFILE_TO_OCCURRENCE", "PROFILE_TO_VERIFICATION", "PROFILE_TO_AUTHORITY",
        "PROFILE_TO_MEMORY", "NON_DETERMINISTIC", "RESOLVED_SAFE_CELLS", "UNRESOLVED_CELLS", "MULTI_OPERATOR_CASES",
    ), 0)
    families = ["REPORT", "BELIEF", "KNOW", "LEARN", "REMEMBER", "PERCEPTION", "DISCOVER", "REALIZE", "NOTICE",
                "REGRET", "DENY", "SAY", "UNKNOWN_COMPLEMENT_GOVERNOR", "report", "", "X" * 3]
    constructions = [*ConstructionType, "QUE", "que_proposition", "NOMINAL", "PSEUDO_RELATIVE"]
    contexts = [frozenset()] + [frozenset({o}) for o in OP] + [frozenset(p) for p in combinations(OP, 2)] + [
        frozenset(p) for p in combinations(OP, 3)]
    for family, construction, context, ref in product(families, constructions, contexts, ("u1", None)):
        metrics["CASES"] += 1
        metrics["MULTI_OPERATOR_CASES"] += len(context) > 1
        try:
            profile = profile_for(family, construction)
            res = resolve_commitment(profile, context, source_object_ref=ref)
            again = resolve_commitment(profile, frozenset(context), source_object_ref=ref)
        except Exception:
            metrics["CRASH"] += 1
            continue
        if res.to_dict() != again.to_dict():
            metrics["NON_DETERMINISTIC"] += 1
        if res.derivation is None or res.derivation.value != res.commitment.value or not res.derivation.rule:
            metrics["COMMITMENT_WITHOUT_DERIVATION"] += 1
        if profile is None:
            metrics["UNKNOWN_TO_ASSERTED"] += res.commitment is C.ASSERTED
            metrics["UNKNOWN_TO_PRESUPPOSED"] += res.commitment is C.PRESUPPOSED
            metrics["UNKNOWN_TO_ENTAILED"] += res.commitment is C.ENTAILED
        if res.commitment is C.UNRESOLVED:
            metrics["UNRESOLVED_CELLS"] += 1
        elif profile is not None:
            metrics["RESOLVED_SAFE_CELLS"] += 1
        dumped = json.dumps(res.to_dict()).lower()
        metrics["PROFILE_TO_OCCURRENCE"] += "occurr" in dumped or res.commitment.value in {
            s.value for s in OccurrenceStatus} - {"UNKNOWN"}
        metrics["PROFILE_TO_VERIFICATION"] += any(w in dumped for w in ("verified", "proof", "truth"))
        metrics["PROFILE_TO_AUTHORITY"] += any(w in dumped for w in ("authority", "authorized", "kx108"))
        metrics["PROFILE_TO_MEMORY"] += "memory" in dumped
        metrics["OCCURRENCE_MUTATION"] += isinstance(res.commitment, OccurrenceStatus)

    assert metrics["CASES"] >= 5000, metrics
    for key in ("RESOLVED_SAFE_CELLS", "UNRESOLVED_CELLS", "MULTI_OPERATOR_CASES"):
        assert metrics[key] > 0, (key, metrics)
    for key in ("UNKNOWN_TO_ASSERTED", "UNKNOWN_TO_PRESUPPOSED", "UNKNOWN_TO_ENTAILED", "COMMITMENT_WITHOUT_DERIVATION",
                "OCCURRENCE_MUTATION", "CRASH", "PROFILE_TO_OCCURRENCE", "PROFILE_TO_VERIFICATION",
                "PROFILE_TO_AUTHORITY", "PROFILE_TO_MEMORY", "NON_DETERMINISTIC"):
        assert metrics[key] == 0, (key, metrics)
