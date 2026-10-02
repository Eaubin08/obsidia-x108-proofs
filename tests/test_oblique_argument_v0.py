"""ObliqueArgumentRef V0 (approved O2): oblique arguments are structured, roles only where licensed.

Every post-object prepositional argument of a unit is one ObliqueArgumentRef (unit,
role, marker, argument, span, group) on UtteranceFrame.oblique_arguments, replacing the
provisional S11 marker (never both). Roles come from the construction, never the noun:
INSTRUMENT for "en utilisant / à l'aide de / au moyen de X", SOURCE for "à partir de X"
when X is not a temporal cue; every other oblique ("avec", "sur", "à", "en", "par",
"depuis", "via", "vers", "chez", "à partir de demain") is UNRESOLVED. A structured but
UNRESOLVED oblique keeps the frame open; SOURCE / INSTRUMENT do not block closure.
Several obliques reuse the argument CoordinationRef (AND / OR). Functional SOURCE is not
the epistemic source (SourceClass); INSTRUMENT(memory) selects or authorizes nothing.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _s11(f):
    return [m for m in f.missing if ":unattached_prepositional_of=" in m or ":unattached_nominal_of=" in m]


def _obl(f):
    return [(o.role, o.marker, o.argument.text, f.raw[o.span[0]:o.span[1]].lower()) for o in f.oblique_arguments]


def _gov(f):
    s = governable_summary(f)
    return (s["requested_world_actions"], s["confirmed_no_execute"], f.constraints,
            [(u.predicate, u.pragmatic, u.polarity, u.subject, tuple(a.text for a in u.objects)) for u in f.units],
            [e.occurrence_claim for e in build_frame_event_index(f).events()])


@pytest.mark.parametrize("text,ref,role,marker,arg,closed", [
    ("Explique Obsidia en utilisant ta mémoire.", "Explique Obsidia.", "INSTRUMENT", "en utilisant", "ta mémoire", True),
    ("Explique Obsidia à l'aide du document X.", "Explique Obsidia.", "INSTRUMENT", "à l'aide de", "du document x", True),
    ("Explique Obsidia au moyen de ta mémoire.", "Explique Obsidia.", "INSTRUMENT", "au moyen de", "ta mémoire", True),
    ("Explique Obsidia à partir de ta mémoire.", "Explique Obsidia.", "SOURCE", "à partir de", "ta mémoire", True),
    ("Explique Obsidia à partir du document X.", "Explique Obsidia.", "SOURCE", "à partir de", "du document x", True),
    ("Explique Obsidia avec ta mémoire.", "Explique Obsidia.", "UNRESOLVED", "avec", "ta mémoire", False),
    ("Explique Obsidia avec Python.", "Explique Obsidia.", "UNRESOLVED", "avec", "python", False),
    ("Lance P sur le serveur.", "Lance P.", "UNRESOLVED", "sur", "le serveur", False),
    ("Dis bonjour à maman.", "Dis bonjour.", "UNRESOLVED", "à", "maman", False),
    ("Lance P via SSH.", "Lance P.", "UNRESOLVED", "via", "ssh", False),
    ("Explique Obsidia à partir de demain.", "Explique Obsidia.", "UNRESOLVED", "à partir de", "demain", False),
])
def test_oblique_ref_role_licensed_by_construction(text, ref, role, marker, arg, closed):
    f, r = parse_utterance(text), parse_utterance(ref)
    ((o_role, o_marker, o_arg, o_span),) = _obl(f)
    assert (o_role, o_marker, o_arg) == (role, marker, arg) and o_span.endswith(arg.split()[-1])
    o = f.oblique_arguments[0]
    assert o.unit == f.units[0].id and o.group is None
    assert not _s11(f)  # one meaning, one representation: the S11 marker is migrated
    assert f.closure is closed
    assert _gov(f) == _gov(r)  # no force, request, constraint, occurrence or object change


def test_temporal_source_is_not_guessed():
    f = parse_utterance("Explique Obsidia à partir de demain.")
    assert f.oblique_arguments[0].role == "UNRESOLVED" and f.deixis == ("demain",)
    assert not any(r.kind in {"TEMPORAL_ANCHOR", "PRECEDES"} for r in f.relations)


@pytest.mark.parametrize("text,kind", [("Explique Obsidia à partir de ta mémoire et du document X.", "AND"),
                                       ("Explique Obsidia à partir de ta mémoire ou du document X.", "OR")])
def test_several_obliques_reuse_argument_coordination(text, kind):
    f = parse_utterance(text)
    assert [(o.role, o.argument.text) for o in f.oblique_arguments] == \
        [("SOURCE", "ta mémoire"), ("SOURCE", "du document x")]
    (c,) = [c for c in f.coordinations if c.construction == "coordinated_oblique"]
    assert (c.kind, c.member_kind, c.host, c.member_texts) == (kind, "argument", "u1", ("ta mémoire", "du document x"))
    assert {o.group for o in f.oblique_arguments} == {c.id} and not _s11(f) and f.closure


def test_epistemic_and_functional_sources_coexist():
    f = parse_utterance("Selon Paul, explique Obsidia en utilisant ta mémoire.")
    assert _obl(f)[0][:3] == ("INSTRUMENT", "en utilisant", "ta mémoire")
    assert any(m.endswith(":detached_source_of=u1") for m in f.missing) and not f.closure  # S12 unchanged


@pytest.mark.parametrize("text", ["Lance P immédiatement.", "Lance P pour tester Q.", "Si Paul lance P, exécute Q.",
                                  "Ils lancent P ensemble.", "Paul lance chacun des tests.", "Lance P."])
def test_consumed_material_creates_no_oblique(text):
    f = parse_utterance(text)
    assert f.oblique_arguments == () and f.closure


def test_unparseable_remainder_keeps_the_s11_fallback():
    f = parse_utterance("Lance P sur le serveur de Paul demain matin vite.")
    assert f.closure is False and (f.oblique_arguments or _s11(f))
