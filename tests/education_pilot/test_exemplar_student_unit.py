"""Host-side unit tests of ExemplarSenseStudent (GREEN V0, design R3). No exam is used.

The student modules are imported from `student_sandbox/` exactly as the container does; the
tests use teaching data only.
"""
from __future__ import annotations

import ast
import pathlib
import re
import sys

import pytest

from tests.education_pilot import _bench as B
from tests.education_pilot import _pilot_data as D

SANDBOX = pathlib.Path(__file__).resolve().parent / "student_sandbox"
SOURCES = [SANDBOX / "exemplar_student.py", SANDBOX / "features.py"]


@pytest.fixture(scope="module")
def mod():
    sys.path.insert(0, str(SANDBOX))
    try:
        import exemplar_student
        import students
        yield exemplar_student, students
    finally:
        sys.path.remove(str(SANDBOX))


def _taught(es):
    s = es.ExemplarSenseStudent()
    s.learn(D.E_LESSONS + D.E_EXERCISES)
    exercises = {e[0]: e for e in D.E_EXERCISES}
    for c in D.C_CORRECTIONS:
        s.apply_correction(c, exercises[c[1]])
    return s


# --- N8 / M2: no sense, no cue word, no bench import in the student's source ---------------------

def test_source_contains_no_sense_identifier_as_token():
    for path in SOURCES:
        hits = re.findall(r"\b(F[1-7]|C[12]|R[12]|T1)\b", path.read_text(encoding="utf-8"))
        assert hits == [], (path.name, hits)


def test_source_imports_only_stdlib_and_sandbox_modules():
    allowed = {"__future__", "hashlib", "json", "math", "pathlib", "re", "unicodedata", "features", "students"}
    for path in SOURCES:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        names = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        names |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
        assert names <= allowed, (path.name, names - allowed)


def test_source_string_literals_contain_no_teaching_content_word():
    teaching = set()
    for it in D.E_LESSONS + D.E_EXERCISES + D.CONCURRENT_LESSONS:
        teaching |= B.content_words(it[2]) | {it[1]}
    for c in D.C_CORRECTIONS + [D.CONTRADICTION]:
        teaching |= B.content_words(c[2])
    sys.path.insert(0, str(SANDBOX))
    try:
        import features                      # closed grammatical classes are not content words
    finally:
        sys.path.remove(str(SANDBOX))
    teaching -= features.FUNCTION_WORDS
    for path in SOURCES:
        literals = " ".join(n.value for n in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
                            if isinstance(n, ast.Constant) and isinstance(n.value, str)).lower()
        words = set(re.findall(r"\w+", literals))
        assert not (words & teaching), (path.name, sorted(words & teaching))


# --- learning really changes the state ---------------------------------------------------------------

def test_empty_student_knows_nothing_and_holds(mod):
    es, st = mod
    s = es.ExemplarSenseStudent()
    assert s.state["revision"] == 0 and s.state["senses"] == {}
    assert all(s.answer(it[1], it[2])["sense"] == st.HOLD for it in D.E_LESSONS)


def test_learn_builds_the_state_and_one_call_is_one_revision(mod):
    es, _ = mod
    s = es.ExemplarSenseStudent()
    s.learn(D.E_LESSONS)
    assert s.state["revision"] == 1 and len(s.state["exemplars"]) == len(D.E_LESSONS)
    assert set(s.state["senses"]["force"]) == {it[3] for it in D.E_LESSONS}
    s.learn(D.E_EXERCISES)
    assert s.state["revision"] == 2


def test_untaught_word_gives_hold(mod):
    es, st = mod
    s = _taught(es)
    assert s.answer("table", "Ils mangent autour de la table.") == {"sense": st.HOLD, "provenance": []}


def test_leave_one_out_on_teaching_is_reported_not_tuned(mod, capsys):
    """Verification only (design R3 §1.3): accuracy is printed, never used to set parameters."""
    es, st = mod
    items = D.E_LESSONS + D.E_EXERCISES
    correct = held = 0
    for k, it in enumerate(items):
        s = es.ExemplarSenseStudent()
        s.learn(items[:k] + items[k + 1:])
        ans = s.answer(it[1], it[2])["sense"]
        correct += ans == it[3]
        held += ans == st.HOLD
    print(f"LOO teaching: {correct}/{len(items)} correct, {held} HOLD")
    assert correct + held <= len(items)


# --- corrections, revisions, history -----------------------------------------------------------------

def test_correction_sense_is_the_exercise_sense_and_previous_exemplar_is_retired(mod):
    es, _ = mod
    s = _taught(es)
    ex = next(e for e in D.E_EXERCISES if e[0] == D.CONTRADICTION[1])
    before = [e for e in s.state["exemplars"] if e["sentence"] == ex[2]]
    s.apply_correction(D.CONTRADICTION, ex)
    after = [e for e in s.state["exemplars"] if e["sentence"] == ex[2]]
    assert len(after) == len(before) + 1
    assert after[-1]["sense"] == ex[3] and after[-1]["rev_retired"] is None
    assert all(e["rev_retired"] is not None for e in after[:-1])
    assert D.CONTRADICTION[0] in after[-1]["provenance"]


def test_cue_is_the_quoted_segment(mod):
    es, _ = mod
    s = _taught(es)
    assert {c["cue_ngram"] for c in s.state["cues"]} == {seg for c in D.C_CORRECTIONS
                                                       for seg in re.findall(r"«\s*([^»]+?)\s*»", c[2])}


def test_history_content_equals_retrieve_as_of_revision(mod):
    es, _ = mod
    s = _taught(es)
    sense = D.E_EXERCISES[-1][3]
    s.apply_correction(D.CONTRADICTION, D.E_EXERCISES[-1])
    hist = s.history("force", sense)
    assert len(hist) >= 2
    for h in hist:
        assert h["content"] == s.retrieve(word="force", sense=sense, as_of_revision=h["revision"])


def test_retrieve_as_of_revision_is_stable_after_later_revisions(mod):
    es, _ = mod
    s = _taught(es)
    sense = D.E_EXERCISES[-1][3]
    r1 = s.retrieve(word="force", sense=sense, as_of_revision=1)
    s.apply_correction(D.CONTRADICTION, D.E_EXERCISES[-1])
    assert s.retrieve(word="force", sense=sense, as_of_revision=1) == r1


def test_answer_provenance_cites_teaching_items_of_the_answered_sense_only(mod):
    es, st = mod
    s = _taught(es)
    s.apply_correction(D.CONTRADICTION, D.E_EXERCISES[-1])
    taught = {it[0]: it[3] for it in D.E_LESSONS + D.E_EXERCISES}
    correction_ids = {c[0] for c in D.C_CORRECTIONS} | {D.CONTRADICTION[0]}
    for it in D.E_LESSONS + D.E_EXERCISES:
        a = s.answer(it[1], it[2])
        if a["sense"] != st.HOLD:
            assert a["provenance"] and not (set(a["provenance"]) & correction_ids)
            assert all(taught[p] == a["sense"] for p in a["provenance"])


# --- persistence and integrity -----------------------------------------------------------------------

def test_canonical_save_reload_gives_identical_answers(mod, tmp_path):
    es, _ = mod
    s = _taught(es)
    s.save(tmp_path)
    r = es.ExemplarSenseStudent.load(tmp_path)
    assert r.state == s.state
    probes = [(it[1], it[2]) for it in D.E_LESSONS + D.CONCURRENT_LESSONS] + [("force", "Une phrase neutre.")]
    assert [r.answer(w, t) for w, t in probes] == [s.answer(w, t) for w, t in probes]


@pytest.mark.parametrize("tamper", ["append_space", "flip_sense", "recomputed_free_edit"])
def test_any_byte_change_raises_state_integrity_error(mod, tmp_path, tamper):
    es, st = mod
    s = _taught(es)
    s.save(tmp_path)
    f = tmp_path / es.STATE_FILE
    raw = f.read_bytes()
    if tamper == "append_space":
        raw += b" "
    elif tamper == "flip_sense":
        raw = raw.replace(b'"weight":2.0', b'"weight":3.0', 1)
    else:
        raw = raw.replace(b'"revision":5', b'"revision":6', 1)
    f.write_bytes(raw)
    with pytest.raises(st.StateIntegrityError):
        es.ExemplarSenseStudent.load(tmp_path)
