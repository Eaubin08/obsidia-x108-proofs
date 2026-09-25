"""Adapter boundary: external linguistic parser evidence -> UtteranceFrame.

No parser is imported here. Any Universal Dependencies producer (Stanza,
spaCy, UDPipe, a treebank) can hand CoNLL-U-like tokens to frame_from_ud().
The built-in deterministic grammar stays the always-available fallback.

Fusion is FAIL-CLOSED: a world action counts as negated only if every
source says so, and counts as requested if any source says so. External
evidence can therefore add caution, never remove it.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.semantic.lattice.lexicon import predicate_of
from app.semantic.lattice.primitives import (
    Argument, LatticeRelation, PredicateUnit, RelationKind, UtteranceFrame,
)

_NEGATOR_LEMMAS = {"pas", "plus", "jamais", "rien", "personne", "aucun", "nul",
                   "guère", "point", "ni", "not", "never"}
_MODALITY = {"pouvoir": "ABILITY_OR_PERMISSION", "devoir": "OBLIGATION",
             "falloir": "OBLIGATION", "vouloir": "DESIRE", "savoir": "KNOW_HOW",
             "can": "ABILITY_OR_PERMISSION", "must": "OBLIGATION"}
_REQUEST_PRAGMATICS = {"REQUESTED", "INDIRECT_REQUEST", "EMBEDDED"}


@dataclass(frozen=True)
class UDToken:
    id: int
    form: str
    lemma: str
    upos: str
    head: int
    deprel: str
    feats: dict = field(default_factory=dict)
    start: int = 0
    end: int = 0


def frame_from_ud(raw: str, tokens: list[UDToken], parser: str = "external_ud") -> UtteranceFrame:
    by_head: dict[int, list[UDToken]] = {}
    for t in tokens:
        by_head.setdefault(t.head, []).append(t)
    units: list[PredicateUnit] = []
    relations: list[LatticeRelation] = []
    unit_of: dict[int, str] = {}

    for t in tokens:
        if t.upos != "VERB":
            continue
        head_tok = next((h for h in tokens if h.id == t.head), None)
        if t.lemma in _MODALITY and any(d.deprel == "xcomp" for d in by_head.get(t.id, [])):
            continue  # modal: its xcomp infinitive carries the unit
        deps = by_head.get(t.id, [])
        negs = [d for d in deps if d.feats.get("Polarity") == "Neg" or d.lemma in _NEGATOR_LEMMAS]
        real_negs = [d for d in negs if d.lemma not in {"ne"}]
        marks = {d.lemma for d in deps if d.deprel == "mark"}
        pred, pcls = predicate_of(t.lemma)
        modality = None
        if head_tok is not None and t.deprel == "xcomp" and head_tok.lemma in _MODALITY:
            modality = _MODALITY[head_tok.lemma]
            real_negs += [d for d in by_head.get(head_tok.id, [])
                          if d.feats.get("Polarity") == "Neg" and d.lemma != "ne"]
        polarity, negator = "positive", None
        if "sans" in marks or "without" in marks:
            polarity, negator = "negative", "sans"
        elif real_negs:
            polarity, negator = "negative", real_negs[0].lemma
        if t.feats.get("Mood") == "Imp":
            form, prag = "IMPERATIVE", "REQUESTED"
        elif t.feats.get("VerbForm") == "Inf":
            form, prag = "INFINITIVE", "REQUESTED" if t.deprel in {"root", "conj"} else "EMBEDDED"
        else:
            form, prag = "FINITE", "ASSERTED"
        if negator == "sans":
            prag = "FORBIDDEN"
        elif head_tok is not None and t.deprel == "ccomp":
            prag = {"dire": "REPORTED", "craindre": "FEARED", "penser": "BELIEVED",
                    "croire": "BELIEVED"}.get(head_tok.lemma, "EMBEDDED")
        if polarity == "negative" and prag in _REQUEST_PRAGMATICS:
            prag = "FORBIDDEN"
        objs = []
        for d in deps:
            if d.deprel == "obj":
                pron = d.upos == "PRON"
                objs.append(Argument(d.form.lower(), d.lemma, "PRONOUN" if pron else "NP",
                                     "UNRESOLVED" if pron else "PRESUPPOSED",
                                     span=(d.start, d.end)))
        uid = f"x{len(units) + 1}"
        unit_of[t.id] = uid
        units.append(PredicateUnit(
            id=uid, predicate=pred, lemma=t.lemma, surface=t.form.lower(),
            span=(t.start, t.end), clause=0, predicate_class=pcls, verb_form=form,
            polarity=polarity, negator=negator, negation_confirmed=polarity == "negative",
            modality=modality, pragmatic=prag, objects=tuple(objs), provenance=parser,
        ))
    for t in tokens:
        if t.id in unit_of and t.head in unit_of and t.deprel in {"conj", "ccomp", "advcl", "xcomp"}:
            kind = RelationKind.EMBEDS if t.deprel in {"ccomp", "xcomp"} else RelationKind.COORDINATES
            relations.append(LatticeRelation(kind.value, unit_of[t.head], unit_of[t.id],
                                             evidence=f"ud:{t.deprel}"))
    return UtteranceFrame(raw=raw, normalized=raw.lower(), units=tuple(units),
                          relations=tuple(relations))


def requested_world_actions(frame: UtteranceFrame) -> set[str]:
    return {u.predicate for u in frame.units
            if u.predicate_class == "world_action" and u.polarity == "positive"
            and u.pragmatic in _REQUEST_PRAGMATICS}


def fail_closed_requested_world_actions(*frames: UtteranceFrame) -> set[str]:
    """Union over sources: one source seeing a request is enough to gate it."""
    out: set[str] = set()
    for f in frames:
        out |= requested_world_actions(f)
    return out


def disagreements(builtin: UtteranceFrame, external: UtteranceFrame) -> list[str]:
    """Per-predicate polarity/pragmatic disagreements (audit only)."""
    out = []
    ext = {}
    for u in external.units:
        ext.setdefault(u.predicate, []).append(u)
    for u in builtin.units:
        for x in ext.get(u.predicate, []):
            if (u.polarity, u.pragmatic) != (x.polarity, x.pragmatic):
                out.append(f"{u.predicate}: builtin={u.polarity}/{u.pragmatic} "
                           f"external={x.polarity}/{x.pragmatic}")
    return out
