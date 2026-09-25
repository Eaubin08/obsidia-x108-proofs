"""Projection of an UtteranceFrame onto the governable UnifiedInputIR.

The IR stays the public, governable summary. This module only extracts the
few facts the IR is allowed to use, under explicit fail-closed rules:

  * a world action is REQUESTED if any unit requests it (imperative,
    injunctive infinitive, indirect request, embedded under an unrecognized
    governor);
  * an execution is CONFIRMED-NEGATED only for a written negation
    (ne ... NEG, ne NEG + infinitive, sans, do not) — oral / ASR negation
    without "ne" is understood but never relaxes anything;
  * relaxation of the execution HOLD is only eligible when a positive
    PREPARE request is accompanied by a confirmed NO_EXECUTE and no world
    action is requested anywhere and no directive contradiction exists.
"""
from __future__ import annotations

from app.semantic.lattice.primitives import BOUNDARY, UtteranceFrame

SCHEMA = "OBSIDIA_UTTERANCE_FRAME_SUMMARY_V0"
REQUEST_PRAGMATICS = frozenset({"REQUESTED", "INDIRECT_REQUEST", "EMBEDDED"})


def _compact(u) -> dict:
    return {
        "id": u.id, "predicate": u.predicate, "surface": u.surface,
        "polarity": u.polarity, "pragmatic": u.pragmatic, "negator": u.negator,
        "negation_confirmed": u.negation_confirmed, "restriction": u.restriction,
        "modality": u.modality, "tense_aspect": u.tense_aspect,
        "epistemic": u.epistemic, "object": u.object_head,
    }


def governable_summary(frame: UtteranceFrame) -> dict:
    requested = [u for u in frame.units
                 if u.predicate_class == "world_action" and u.polarity == "positive"
                 and u.pragmatic in REQUEST_PRAGMATICS]
    negated_execute = [u for u in frame.units
                       if u.predicate == "EXECUTE" and u.polarity == "negative"
                       and u.pragmatic == "FORBIDDEN" and u.negation_confirmed]
    prepare = [u for u in frame.units
               if u.predicate == "PREPARE" and u.polarity == "positive"
               and u.pragmatic in {"REQUESTED", "INDIRECT_REQUEST"}]
    prepare_referent_open = any(
        u.object is None or u.object.reference in {"UNRESOLVED", "PRESUPPOSED"}
        for u in prepare)
    no_execute = bool(negated_execute)
    relaxable = bool(prepare) and no_execute and not requested and not frame.contradictions
    return {
        "schema": SCHEMA,
        "units": [_compact(u) for u in frame.units],
        "relations": [[r.kind, r.source, r.target] for r in frame.relations],
        "constraints": list(frame.constraints),
        "requested_world_actions": sorted({u.predicate for u in requested}),
        "requested_action_surfaces": [u.surface for u in requested],
        "negated_execute_surfaces": sorted({u.surface for u in negated_execute}),
        "confirmed_no_execute": no_execute,
        "prepare_requested": bool(prepare),
        "prepare_referent_open": prepare_referent_open,
        "execution_hold_relaxable": relaxable,
        "unresolved_references": list(frame.unresolved_references),
        "presupposed_referents": list(frame.presupposed_referents),
        "contradictions": list(frame.contradictions),
        "evidence_needs": list(frame.evidence_needs),
        "closure": frame.closure,
        "closure_blockers": list(frame.closure_blockers),
        "boundary": dict(BOUNDARY),
    }


def fail_closed_summary(error: Exception) -> dict:
    """Used when the grammar raises: describe nothing, relax nothing."""
    return {
        "schema": SCHEMA,
        "error": type(error).__name__,
        "units": [], "relations": [], "constraints": [],
        "requested_world_actions": [], "requested_action_surfaces": [],
        "negated_execute_surfaces": [], "confirmed_no_execute": False,
        "prepare_requested": False, "prepare_referent_open": False,
        "execution_hold_relaxable": False, "unresolved_references": [],
        "presupposed_referents": [], "contradictions": [], "evidence_needs": [],
        "closure": False, "closure_blockers": ["parser_error"],
        "boundary": dict(BOUNDARY),
    }
