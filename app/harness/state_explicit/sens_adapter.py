"""B6 SENS -> working state: one SENS_FRAME entry per utterance, open meaning kept open.

Uses the canonical SENS APIs only (parse_utterance, governable_summary, semantic_closure);
app/semantic/lattice is never modified. SENS CLOSED does not mean every utterance is closed:
missing content, ambiguities, unresolved references, contradictions and closure reasons
(including the frozen D1-D5 limits) are copied as uncertainty, never resolved. A requested
world action is described, never authorized.
"""
from __future__ import annotations

from app.harness.state_explicit.contracts import StateEntry, StateStatus, Visibility, error_entry
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary
from app.semantic.lattice.semantic_closure import semantic_closure


def sens_state_entries(text: str, state_id: str = "sens:frame") -> tuple[StateEntry, ...]:
    source_ref = "app.semantic.lattice.french_grammar.parse_utterance"
    try:
        frame = parse_utterance(text)
        summary = governable_summary(frame)
        closure = semantic_closure(frame)
    except Exception as exc:          # a failed parse stays visible, never silent
        return (error_entry(state_id, source_ref, exc, state_type="SENS_FRAME_ERROR"),)
    open_items = [*frame.missing, *frame.ambiguities, *frame.unresolved_references,
                  *frame.contradictions, *closure.reasons]
    is_open = not closure.closed or not frame.closure
    payload = {
        "raw": frame.raw,
        "units": summary["units"],
        "relations": summary["relations"],
        "coordinations": summary["coordinations"],
        "requested_world_actions": summary["requested_world_actions"],
        "requested_is_authorized": False,
        "missing": list(frame.missing),
        "ambiguities": list(frame.ambiguities),
        "unresolved_references": list(frame.unresolved_references),
        "contradictions": list(frame.contradictions),
        "frame_closure": frame.closure,
        "semantic_closure": {"closed": closure.closed, "reasons": list(closure.reasons)},
    }
    tags = {"sens", *(u.lemma for u in frame.units if u.lemma)}
    if is_open:
        tags.add("sens_open")
    if summary["requested_world_actions"]:
        tags.add("requested_action")
    return (StateEntry(state_id=state_id, state_type="SENS_FRAME", source_ref=source_ref, payload=payload,
                       provenance=(source_ref, "app.semantic.lattice.semantic_closure"),
                       uncertainty=tuple(dict.fromkeys(open_items)),
                       status=StateStatus.OPEN if is_open else StateStatus.KNOWN,
                       visibility=Visibility.LONG, tags=tuple(sorted(tags)),
                       summary=f"SENS frame: {len(frame.units)} unit(s), "
                               f"{'open' if is_open else 'closed'}"),)
