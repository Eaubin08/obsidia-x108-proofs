"""check_unseen and RAPPEL (R4.4 V1.7): a taught sentence changed only by case, accents, spaces or final
punctuation is a recall, never an unseen exam item. Synthetic sentences only, no exam."""
from __future__ import annotations

import sys

from tests.education_pilot import _bench as B
from tests.education_pilot import _pilot_data as D

TAUGHT = "Le mot vole très haut au-dessus du lac."
VARIANTS = ("le mot vole très haut au-dessus du lac.", "Le mot vole tres haut au-dessus du lac.",
            "Le  mot vole très haut   au-dessus du lac.", "Le mot vole très haut au-dessus du lac !",
            "Le mot vole très haut au-dessus du lac")
OTHERS = ("Le mot vole très haut au-dessus de la mer.", "Le mot vole, très haut au-dessus du lac.")


def examiner_after_teaching(sentence):
    log = B.ShownLog()
    log.record(sentence)
    return B.Examiner(log, seed=0)


def test_check_unseen_flags_every_recall_variant_of_a_taught_sentence():
    exam = [("V%d" % i, "mot", s, "L1", "a", "x") for i, s in enumerate(VARIANTS)]
    assert examiner_after_teaching(TAUGHT).check_unseen(exam) == [it[0] for it in exam]


def test_check_unseen_keeps_genuinely_new_sentences_unseen():
    exam = [("N%d" % i, "mot", s, "L1", "a", "x") for i, s in enumerate(OTHERS)]
    assert examiner_after_teaching(TAUGHT).check_unseen(exam) == []


def test_bench_fingerprint_is_the_student_rappel_fingerprint():
    sys.path.insert(0, str(B.SANDBOX_DIR))
    try:
        import r4_core_student
    finally:
        sys.path.remove(str(B.SANDBOX_DIR))
    for s in (TAUGHT,) + VARIANTS + OTHERS:
        assert B.teaching_fingerprint(s) == r4_core_student.recall_key(s), s


def test_exact_hash_and_memorizer_baseline_are_unchanged():
    lesson = D.E_LESSONS[1]
    variant = lesson[2].rstrip(".")
    assert B.sentence_hash(lesson[2]) != B.sentence_hash(variant)
    assert B.baseline_answer("memorizer", lesson[1], lesson[2]) == lesson[3]
    assert B.baseline_answer("memorizer", lesson[1], variant) == B.HOLD
