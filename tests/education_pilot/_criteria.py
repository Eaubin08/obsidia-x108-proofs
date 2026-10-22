"""Acquisition criteria of the pilot "force" (RED V0.3), as pure functions of host-side scores.

Every criterion takes `S`, a dict of Score objects keyed by exam name (X0 = before teaching,
X1, X1_FAR, X3 after concurrent lessons, X2 after restart, X4 transfer), and `exams`, the
private exams. They are evaluated identically for the student under test, for the perfect
reference (feasibility) and for trivial strategies (discrimination).

Baseline comparisons are made on the AGGREGATE accuracy of an exam, never per sense: with one
item per sense a correct baseline already reaches 1.0 on that sense and cannot be beaten
(V0.2 audit, blocker B2). Thresholds are PROVISIONAL (spec §6).
"""
from __future__ import annotations

from tests.education_pilot import _bench as B
from tests.education_pilot import _pilot_data as D

P = B.PROVISIONAL
CLOSE_SENSES = ("F1", "F2", "F3", "F5", "F6")


def taught_senses() -> dict[str, str]:
    ids = {it[0]: it[3] for it in D.E_LESSONS + D.E_EXERCISES}
    exercises = {e[0]: e for e in D.E_EXERCISES}
    ids.update({c[0]: exercises[c[1]][3] for c in D.C_CORRECTIONS})
    return ids


def beats_baselines(score, exam, word="force") -> bool:
    return score.accuracy(word=word) >= B.best_baseline_accuracy(exam, word=word) + P["baseline_margin"]


def witness_stable(t0, t1) -> bool:
    """The untaught witness word 'table' must not change between T0 and T1."""
    a = {r["id"]: r["answer"] for r in t0.per_item if r["word"] == "table"}
    b = {r["id"]: r["answer"] for r in t1.per_item if r["word"] == "table"}
    return set(a.values()) <= {B.HOLD} and set(b.values()) <= {B.HOLD}


def t1_acquisition(S, exams) -> bool:
    gained = [s for s in D.FORCE_SENSES
              if S["X1"].accuracy(sense=s) - S["X0"].accuracy(sense=s) >= P["acquisition_gain_min"]]
    return (len(gained) >= P["acquisition_min_senses"] and beats_baselines(S["X1"], exams["X1"])
            and witness_stable(S["X0"], S["X1"]))


def far_sentences(S, exams) -> bool:
    return beats_baselines(S["X1_FAR"], exams["X1_FAR"])


def close_senses(S, exams) -> bool:
    return all(S["X1"].accuracy(sense=s) == 1.0 for s in CLOSE_SENSES) and beats_baselines(S["X1"], exams["X1"])


def t2_retention(S, exams) -> bool:
    return (t1_acquisition(S, exams) and S["X2"].accuracy() >= S["X1"].accuracy() - P["retention_tolerance"]
            and beats_baselines(S["X2"], exams["X2"]))


def t3_no_forgetting(S, exams) -> bool:
    acquired = [s for s in D.FORCE_SENSES if S["X1"].accuracy(sense=s) == 1.0]
    return (t1_acquisition(S, exams) and beats_baselines(S["X3"], exams["X3"])
            and all(S["X3"].accuracy(sense=s) >= S["X1"].accuracy(sense=s) - P["forgetting_tolerance"]
                    for s in acquired))


def t3_concurrent(S, exams) -> bool:
    return all(S["X3"].accuracy(word=w, sense=s) == 1.0 and beats_baselines(S["X3"], exams["X3"], word=w)
               for w, senses in (("chemin", ("C1", "C2")), ("corriger", ("R1", "R2"))) for s in senses)


def t3_abstention(S, exams) -> bool:
    return (S["X3"].abstention_appropriate() >= P["abstention_appropriate_min"]
            and S["X3"].abstention_unjustified() <= P["abstention_unjustified_max"]
            and beats_baselines(S["X3"], exams["X3"]))


def t4_transfer(S, exams) -> bool:
    return (beats_baselines(S["X4"], exams["X4"])
            and S["X4"].accuracy() >= P["transfer_fraction_min"] * S["X1"].accuracy() > 0)


def t1_abstention(S, exams) -> bool:
    return (S["X1"].abstention_appropriate() >= P["abstention_appropriate_min"]
            and S["X1"].abstention_unjustified() <= P["abstention_unjustified_max"]
            and beats_baselines(S["X1"], exams["X1"]))


def provenance(S, exams) -> bool:
    taught = taught_senses()
    correct = [r for r in S["X1"].per_item if r["answer"] == r["expected"] and r["expected"] != B.HOLD]
    return t1_acquisition(S, exams) and all(
        r["provenance"] and all(taught.get(p) == r["answer"] for p in r["provenance"]) for r in correct)


CRITERIA = {f.__name__: f for f in (t1_acquisition, far_sentences, close_senses, t2_retention, t3_no_forgetting,
                                     t3_concurrent, t3_abstention, t4_transfer, t1_abstention, provenance)}


# --- Host-only references (never given to the student) ------------------------------------------

def scored(exam, answer_fn, order=None) -> "B.Score":
    rows = []
    for pos, (i, w, t, e, d, r) in enumerate(order if order is not None else exam):
        sense, prov = answer_fn(pos, w, t, e)
        rows.append({"id": i, "word": w, "expected": e, "answer": sense, "provenance": prov, "domain": d,
                     "register": r})
    return B.Score(rows)


def perfect_reference(exams) -> dict:
    """Exact key on taught words after teaching, HOLD before teaching and on untaught words."""
    by_sense = {}
    for item_id, sense in taught_senses().items():
        by_sense.setdefault(sense, item_id)
    taught_words = {it[1] for it in D.E_LESSONS + D.E_EXERCISES + D.CONCURRENT_LESSONS}

    def key(pos, w, t, e):
        if w not in taught_words or e == B.HOLD:
            return B.HOLD, []
        return e, [by_sense[e]] if e in by_sense else [next(it[0] for it in D.CONCURRENT_LESSONS if it[3] == e)]

    S = {k: scored(exams[k], key) for k in ("X1", "X1_FAR", "X2", "X3", "X4")}
    S["X0"] = scored(exams["X0"], lambda *a: (B.HOLD, []))
    return S


def strategy_scores(exams, answer_fn, examiner) -> dict:
    """Scores of a stateless trivial strategy, asked in the examiner's (shuffled) order."""
    return {k: scored(exams[k], answer_fn, examiner.order(exams[k])) for k in ("X0", "X1", "X1_FAR", "X2", "X3", "X4")}
