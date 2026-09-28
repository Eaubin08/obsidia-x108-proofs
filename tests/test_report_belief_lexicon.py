"""B2b: safe report/belief lexicon replaces the unresolved-governor fallback.

affirmer / déclarer / mentionner -> SAY (REPORTS), supposer -> BELIEVE
(BELIEVES), plus the missing croire forms. Embedding still requires a "que"
complement; excluded verbs keep failing closed.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_extraction import OccurrenceStatus, extract_event_candidates
from app.semantic.lattice.events import EventKind
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary
from app.semantic.lattice.knowledge_event_extraction import extract_knowledge_event_targets
from app.semantic.lattice.language_flow_projection import project_ordered_flows
from app.semantic.lattice.lexicon import lookup
from app.semantic.lattice.observation_event_extraction import extract_observation_event_targets

GOVERNOR = "UNKNOWN_COMPLEMENT_GOVERNOR"
A = OccurrenceStatus.ASSERTED_OCCURRED
R = OccurrenceStatus.REPORTED
U = OccurrenceStatus.UNKNOWN
N = OccurrenceStatus.NEGATED
F = OccurrenceStatus.FUTURE
C = OccurrenceStatus.UNCERTAIN


def _analyse(text: str):
    frame = parse_utterance(text)
    base = extract_event_candidates(frame)
    observation = extract_observation_event_targets(frame, base)
    knowledge = extract_knowledge_event_targets(frame, base)
    events = tuple(base) + tuple(observation.observation_events) + tuple(knowledge.knowledge_events)
    targets = tuple(observation.targets) + tuple(knowledge.targets)
    return frame, {event.predicate_ref: event for event in events}, targets


def _statuses(text: str):
    frame, events, _ = _analyse(text)
    return [
        (unit.predicate, events[unit.id].occurrence_status)
        for unit in sorted(frame.units, key=lambda unit: unit.span[0])
        if unit.id in events
    ]


def _relations(frame):
    return {(r.kind, r.source, r.target) for r in frame.relations}


# Report subset.

@pytest.mark.parametrize("text, lemma", [
    ("Paul affirme que Marie a lancé le test.", "affirmer"),
    ("Paul déclare que Marie a lancé le test.", "déclarer"),
    ("Paul mentionne que Marie a lancé le test.", "mentionner"),
    ("Paul affirmait que Marie avait lancé le test.", "affirmer"),
    ("Paul a déclaré que Marie a lancé le test.", "déclarer"),
])
def test_safe_report_verbs_replace_fallback_with_say(text, lemma):
    frame, events, _ = _analyse(text)
    say = next(unit for unit in frame.units if unit.predicate == "SAY")
    run = next(unit for unit in frame.units if unit.predicate == "EXECUTE")

    assert not [unit for unit in frame.units if unit.predicate == GOVERNOR]
    assert say.lemma == lemma and say.predicate_class == "embedding_say"
    assert ("REPORTS", say.id, run.id) in _relations(frame)
    assert events[say.id].event_ref.event_kind is EventKind.REPORT
    assert events[say.id].occurrence_status is A
    assert events[run.id].occurrence_status is R


# Belief subset.

@pytest.mark.parametrize("text", [
    "Paul suppose que Marie a lancé le test.",
    "Paul supposait que Marie avait lancé le test.",
])
def test_supposer_maps_to_believe(text):
    frame, events, _ = _analyse(text)
    believe = next(unit for unit in frame.units if unit.predicate == "BELIEVE")
    run = next(unit for unit in frame.units if unit.predicate == "EXECUTE")

    assert believe.lemma == "supposer"
    assert ("BELIEVES", believe.id, run.id) in _relations(frame)
    assert events[believe.id].event_ref.event_kind is EventKind.BELIEF
    assert events[believe.id].occurrence_status is A
    assert events[run.id].occurrence_status is U


@pytest.mark.parametrize("text, expected", [
    ("Paul suppose que Marie n'a pas lancé le test.", N),
    ("Paul suppose que Marie lancera le test.", F),
    ("Paul suppose que Marie pourrait lancer le test.", C),
    ("Paul affirme que Marie n'a pas lancé le test.", N),
    ("Paul déclare que Marie lancera le test.", F),
])
def test_strong_local_signals_survive_new_governors(text, expected):
    assert _statuses(text)[-1] == ("EXECUTE", expected)


# Croire / penser inflections.

_CROIRE_FORMS = ("croyais", "croyait", "croyions", "croyiez", "croyaient", "croira", "croirait")


def test_missing_croire_forms_are_now_known():
    for form in _CROIRE_FORMS:
        assert [lemma for lemma, _ in lookup(form)[0]] == ["croire"], form


@pytest.mark.parametrize("text", [
    "Paul croyait que Marie avait lancé le test.",
    "Je croyais que Marie avait lancé le test.",
    "Paul pensait que Marie avait lancé le test.",
    "Nous croyions que Marie avait lancé le test.",
    "Ils croyaient que Marie avait lancé le test.",
    "Paul croira que Marie a lancé le test.",
    "Paul croirait que Marie a lancé le test.",
    "Paul a cru que Marie avait lancé le test.",
    "Paul a pensé que Marie avait lancé le test.",
])
def test_croire_penser_inflections_embed_belief(text):
    frame, events, _ = _analyse(text)
    believe = [unit for unit in frame.units if unit.predicate == "BELIEVE"]
    run = next(unit for unit in frame.units if unit.predicate == "EXECUTE")

    assert len(believe) == 1 and not [unit for unit in frame.units if unit.predicate == GOVERNOR]
    assert ("BELIEVES", believe[0].id, run.id) in _relations(frame)
    assert events[run.id].occurrence_status is U


# Nesting: the nearest epistemic ancestor governs.

def test_report_around_belief_with_new_lexicon():
    assert _statuses("Paul affirme que Marie croit que Jean a lancé le test.") == [
        ("SAY", A), ("BELIEVE", R), ("EXECUTE", U),
    ]


def test_belief_around_report_with_new_lexicon():
    assert _statuses("Paul suppose que Marie a dit que Jean a lancé le test.") == [
        ("BELIEVE", A), ("SAY", U), ("EXECUTE", R),
    ]


# Structural guard: no complement, no embedding.

@pytest.mark.parametrize("text", [
    "Paul déclare ses revenus.",
    "Paul mentionne Marie.",
    "Paul affirme sa position.",
    "Paul pense à Marie.",
    "Paul suppose une erreur.",
])
def test_new_verbs_without_complement_do_not_embed(text):
    frame, _, targets = _analyse(text)

    assert not {r.kind for r in frame.relations} & {"REPORTS", "BELIEVES", "EMBEDS"}
    assert all(unit.embedded_under is None for unit in frame.units)
    assert targets == ()


# Excluded verbs still fail closed.

@pytest.mark.parametrize("text", [
    "Paul prétend que Marie a lancé le test.",
    "Paul nie que Marie a lancé le test.",
    "Les logs indiquent que Marie a lancé le test.",
    "Paul soupçonne que Marie a lancé le test.",
    "Paul imagine que Marie a lancé le test.",
    "Paul considère que Marie a lancé le test.",
])
def test_excluded_verbs_keep_unresolved_governor_fallback(text):
    frame, events, _ = _analyse(text)
    run = next(unit for unit in frame.units if unit.predicate == "EXECUTE")

    assert [unit for unit in frame.units if unit.predicate == GOVERNOR]
    assert events[run.id].occurrence_status is U


# Closed by B2c (known non-embedding governor + que fails closed).
@pytest.mark.parametrize("text", [
    "Paul confirme que Marie a lancé le test.",
    "Paul explique que Marie a lancé le test.",
])
def test_known_non_embedding_verbs_with_complement_do_not_assert(text):
    frame, events, _ = _analyse(text)
    run = next(unit for unit in frame.units if unit.predicate == "EXECUTE")
    assert events[run.id].occurrence_status is not A


# Adversarial matrix.

_NEW_REPORT = (("affirme", "affirmait", "affirmé"), ("déclare", "déclarait", "déclaré"),
               ("mentionne", "mentionnait", "mentionné"))
_NEW_BELIEF = (("suppose", "supposait", "supposé"),)
_INFLECTIONS = (
    ("Je", "crois"), ("Tu", "crois"), ("Paul", "croit"), ("Nous", "croyons"), ("Vous", "croyez"),
    ("Ils", "croient"), ("Je", "croyais"), ("Paul", "croyait"), ("Nous", "croyions"),
    ("Vous", "croyiez"), ("Ils", "croyaient"), ("Paul", "croira"), ("Paul", "croirait"),
    ("Paul", "a cru"), ("Je", "pense"), ("Tu", "penses"), ("Nous", "pensons"), ("Vous", "pensez"),
    ("Ils", "pensent"), ("Je", "pensais"), ("Paul", "pensait"), ("Nous", "pensions"),
    ("Vous", "pensiez"), ("Ils", "pensaient"), ("Paul", "pensera"), ("Paul", "penserait"),
    ("Paul", "a pensé"),
)
_EXCLUDED = ("prétend", "nie", "indique", "soupçonne", "imagine", "considère")
_SUBJECTS = ("Paul", "Anne", "Il", "Elle", "Le chef")
_COMPLEMENTS = (
    ("a lancé le test {i}", U, R),
    ("n'a pas lancé le test {i}", N, N),
    ("lancera le test {i}", F, F),
    ("pourrait lancer le test {i}", C, C),
)
_DIRECT = ("{s} déclare ses revenus {i}.", "{s} mentionne {o} {i}.", "{s} affirme sa position {i}.",
           "{s} pense à {o} {i}.", "{s} suppose une erreur {i}.")


def test_report_belief_lexicon_adversarial_matrix():
    metrics = dict.fromkeys((
        "CASES", "REPORT_RECOGNIZED", "BELIEF_RECOGNIZED", "UNKNOWN_SAFE_FALLBACKS", "FALSE_REPORTS",
        "FALSE_BELIEFS", "ASSERTED_REPORT_CONTENT", "ASSERTED_BELIEF_CONTENT", "STRONG_STATUS_LOST",
        "REQUEST_FABRICATED", "VERIFIED_CREATED", "SUPPORTED_CREATED", "AUTHORIZED_FLOW_CREATED",
        "EXECUTED_FLOW_CREATED", "UNKNOWN_GOVERNOR_REGRESSION", "UNEXPECTED_STATUS",
    ), 0)

    def run(text, family, expected=None):
        frame, events, _ = _analyse(text)
        metrics["CASES"] += 1
        kinds = {r.kind for r in frame.relations}
        runs = [unit for unit in frame.units if unit.predicate == "EXECUTE"]
        statuses = [events[unit.id].occurrence_status for unit in runs]
        if governable_summary(frame)["requested_world_actions"]:
            metrics["REQUEST_FABRICATED"] += 1
        for flow in project_ordered_flows(frame):
            if flow.state in {"VERIFIED", "SUPPORTED", "AUTHORIZED", "EXECUTED"}:
                metrics[{"VERIFIED": "VERIFIED_CREATED", "SUPPORTED": "SUPPORTED_CREATED",
                         "AUTHORIZED": "AUTHORIZED_FLOW_CREATED",
                         "EXECUTED": "EXECUTED_FLOW_CREATED"}[flow.state]] += 1
        if family == "report":
            metrics["REPORT_RECOGNIZED"] += "REPORTS" in kinds
            metrics["FALSE_BELIEFS"] += "BELIEVES" in kinds
            metrics["ASSERTED_REPORT_CONTENT"] += statuses.count(A)
        elif family == "belief":
            metrics["BELIEF_RECOGNIZED"] += "BELIEVES" in kinds
            metrics["FALSE_REPORTS"] += "REPORTS" in kinds
            metrics["ASSERTED_BELIEF_CONTENT"] += statuses.count(A)
        elif family == "excluded":
            has_governor = any(unit.predicate == GOVERNOR for unit in frame.units)
            metrics["UNKNOWN_SAFE_FALLBACKS"] += has_governor
            metrics["UNKNOWN_GOVERNOR_REGRESSION"] += (not has_governor) + statuses.count(A)
            metrics["FALSE_REPORTS"] += "REPORTS" in kinds
            metrics["FALSE_BELIEFS"] += "BELIEVES" in kinds
        elif family == "direct":
            metrics["FALSE_REPORTS"] += "REPORTS" in kinds
            metrics["FALSE_BELIEFS"] += "BELIEVES" in kinds
            metrics["UNEXPECTED_STATUS"] += any(unit.embedded_under for unit in frame.units)
        if expected is not None and statuses[-1:] != [expected]:
            metrics["STRONG_STATUS_LOST" if expected in {N, F, C} else "UNEXPECTED_STATUS"] += 1

    for i in range(6):
        for s in _SUBJECTS:
            for o in ("Marie", "Claire"):
                for complement, belief_status, report_status in _COMPLEMENTS:
                    c = complement.format(i=i)
                    for present, imperfect, participle in _NEW_REPORT:
                        for verb in (present, imperfect, f"a {participle}"):
                            run(f"{s} {verb} que {o} {c}.", "report", report_status)
                    for present, imperfect, participle in _NEW_BELIEF:
                        for verb in (present, imperfect, f"a {participle}"):
                            run(f"{s} {verb} que {o} {c}.", "belief", belief_status)
                    run(f"{s} dit que {o} {c}.", "report", report_status)
                    run(f"{s} croit que {o} {c}.", "belief", belief_status)
                    for verb in _EXCLUDED:
                        run(f"{s} {verb} que {o} {c}.", "excluded")
                run(f"{s} affirme que {o} croit que Jean a lancé le test {i}.", "nested", U)
                run(f"{s} suppose que {o} a dit que Jean a lancé le test {i}.", "nested", R)
                run(f"{o} a lancé le test {i}.", "root", A)
                for template in _DIRECT:
                    run(template.format(s=s, o=o, i=i), "direct")
        for subject, form in _INFLECTIONS:
            for complement, belief_status, _ in _COMPLEMENTS:
                run(f"{subject} {form} que Marie {complement.format(i=i)}.", "belief", belief_status)

    assert metrics["CASES"] >= 3000
    for key in ("REPORT_RECOGNIZED", "BELIEF_RECOGNIZED", "UNKNOWN_SAFE_FALLBACKS"):
        assert metrics[key] > 0, (key, metrics)
    for key, value in metrics.items():
        if key not in {"CASES", "REPORT_RECOGNIZED", "BELIEF_RECOGNIZED", "UNKNOWN_SAFE_FALLBACKS"}:
            assert value == 0, (key, metrics)
