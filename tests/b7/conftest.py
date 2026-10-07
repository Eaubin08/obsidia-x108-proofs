"""B7 runtime RED contract — shared fixtures.

Sources: docs/architecture/B7_COGNITIVE_ROLE_SPEC_V1.md, B7_COGNITIVE_ROLE_SPEC_CLOSURE_20261007.md,
B7_RUNTIME_DETERMINISM_CONTRACT_V1.md. Future runtime target: ``app.cognition.b7``.
The ``b7`` fixture is a lazy handle: the module is imported on first attribute access inside the test
body, so until the runtime exists every test FAILS with a clean ModuleNotFoundError (no collection or
fixture-setup error).
"""
from __future__ import annotations

import importlib

import pytest

from app.harness.state_explicit.contracts import StateEntry, StateStatus, Visibility


class _LazyB7:
    def __getattr__(self, name):
        return getattr(importlib.import_module("app.cognition.b7"), name)


@pytest.fixture
def b7():
    return _LazyB7()


def make_entry(raw: str = "x", *, status: StateStatus = StateStatus.OPEN, state_id: str = "sens:frame",
               state_type: str = "SENS_FRAME", missing=(), ambiguities=(), unresolved_references=(),
               contradictions=(), reasons=(), units=("u1",), uncertainty=None, extra=None,
               unit_objects=None) -> StateEntry:
    """A synthetic B6 SENS_FRAME entry carrying exactly the given explicit markers.

    ``unit_objects`` ({unit_id: [object texts]}) gives SENS-shaped structured referents; under the
    STRUCTURED_REFERENT_ONLY amendment (2026-10-07) only such referents are admissible in B7."""
    payload = {
        "raw": raw,
        "missing": list(missing), "ambiguities": list(ambiguities),
        "unresolved_references": list(unresolved_references), "contradictions": list(contradictions),
        "semantic_closure": {"closed": not (missing or ambiguities or unresolved_references or contradictions
                                            or reasons), "reasons": list(reasons)},
        "semantic_frame": {"raw": raw, "units": [{"id": u, "objects": [{"text": t} for t in (unit_objects or {}).get(u, ())]}
                                     for u in units], "oblique_arguments": [],
                           "deixis": [], "constraints": [], "evidence_needs": [], "presupposed_referents": []},
        "requested_world_actions": [], "requested_is_authorized": False,
    }
    payload.update(extra or {})
    if uncertainty is None:
        uncertainty = (*unresolved_references, *contradictions, *ambiguities, *missing, *reasons)
    return StateEntry(state_id=state_id, state_type=state_type,
                      source_ref="app.semantic.lattice.french_grammar.parse_utterance", payload=payload,
                      provenance=("app.semantic.lattice.french_grammar.parse_utterance",
                                  "app.semantic.lattice.semantic_closure"),
                      uncertainty=tuple(uncertainty), status=status, visibility=Visibility.LONG,
                      tags=("sens",), summary="synthetic SENS frame")


@pytest.fixture
def entry_factory():
    return make_entry


@pytest.fixture
def coref_entry():
    """'Le script est prêt. Lance-le.' with one explicit unresolved reference, one other open item and
    the structured referent "le script" (requalified 2026-10-07: structured-referent-only doctrine)."""
    return make_entry("Le script est prêt. Lance-le.", unresolved_references=("u2:le",), units=("u1", "u2"),
                      uncertainty=("unresolved_reference:u2:le", "other_open_item"),
                      unit_objects={"u1": ["le script"]})


def raw_candidate(request, **overrides) -> dict:
    """A raw provider mapping that satisfies every gate check for a COREFERENCE request."""
    raw = {
        "request_id": request.request_id,
        "origin_state_id": request.origin_state_id,
        "original_state_digest": request.original_state_digest,
        "candidate_kind": "REFERENCE_BINDING",
        "proposer_role": "RESOLVER",
        "provider_ref": "provider:test",
        "resolves": list(request.problem_refs),
        "proposed_resolution": {"mention": "u2:le", "antecedent": "le script"},
        "evidence_refs": ["sens:frame#raw"],
        "context_refs": [],
        "provenance_refs": list(request.provenance_refs),
        "confidence_class": "MEDIUM",
        "remaining_unknowns": ["other_open_item"],
        "contradictions": [],
        "assumptions": [],
    }
    raw.update(overrides)
    return raw


@pytest.fixture
def raw_candidate_factory():
    return raw_candidate


PROVIDERS = {"provider:test": frozenset({"RESOLVER", "UNDERSTANDER", "CRITIC", "INVESTIGATOR"}),
             "provider:other": frozenset({"RESOLVER"})}


@pytest.fixture
def providers():
    return PROVIDERS
