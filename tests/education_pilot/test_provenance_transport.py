"""Transport of declared teaching provenance: curriculum -> bench -> runner -> student (R4.4 V1.4).
Synthetic development fixture only; its metadata is declared by this test, never verified or attested."""
from __future__ import annotations

import contextlib
import importlib.util
import itertools
import sys

import pytest

from tests.education_pilot import _bench as B
from tests.education_pilot import _pilot_data as D

SANDBOX = B.SANDBOX_DIR
NOLEX = str(SANDBOX / "__no_lexicon__")
R4 = "r4_core_student:R4CoreStudent"
HISTORICAL = ("students:EmptyStudent", "exemplar_student:ExemplarSenseStudent")
needs_docker = pytest.mark.skipif(not B.docker_ready(), reason="HOLD_SECURITY_BOUNDARY: Docker isolation unavailable")

# two lessons in one call (TP-A1, TP-B1, two declared but unattested sources), a second delivery of
# lesson SYN-LEC-A, items without provenance, and a correction whose exercise declares its source item
TA1 = ("TP-A1", "mot", "Le mot vole souvent dans les nuages lointains.", "L1", "d", "x")
TA2 = ("TP-A2", "mot", "Un mot bondit depuis la branche haute.", "L1", "d", "x")
TA3 = ("TP-A3", "mot", "Ce mot plonge sous la surface froide.", "L1", "d", "x")
TB1 = ("TP-B1", "mot", "Ce mot vole souvent sur des arbres immenses aussi.", "L1", "d", "x")
TE1 = ("TP-E1", "mot", "La route du mot longe toute la colline.", "L2", "e", "x")
TE2 = ("TP-E2", "mot", "Quelle colline prend ce mot fragile.", "L2", "e", "x")
TA1_BIS = ("TP-A1-BIS", "mot", "Le mot vole souvent au-dessus des nuages.", "L1", "d", "x")
TEX = ("TP-EX", "mot", "Le mot vole souvent dans les arbres immenses.", "L1", "d", "x")
TK1 = ("TP-K1", "TP-EX", "« vole » marque ce sens (L1), pas l’autre (L2).")
DELIVERY_1 = [TA1, TA2, TA3, TB1, TE1, TE2]
PROV_1 = {"TP-A1": {"lesson_id": "SYN-LEC-A", "source_id": "SYN-SRC-1", "author_id": "SYN-AUT-1"},
          "TP-B1": {"lesson_id": "SYN-LEC-B", "source_id": "SYN-SRC-2", "author_id": "SYN-AUT-2"}}
DELIVERY_2 = [TA1, TA1_BIS]
PROV_2 = {"TP-A1": {"lesson_id": "SYN-LEC-A"}, "TP-A1-BIS": {"lesson_id": "SYN-LEC-A"}}
PROV_C = {"TP-EX": {"derived_from": ["TP-A2"]}, "TP-K1": {"author_id": "SYN-AUT-3"}}
QUERIES = ("Le mot vole souvent sur les arbres immenses.", "Le mot vole souvent.", "La route du mot longe la colline.")


@pytest.fixture(scope="module")
def sandbox_modules():
    sys.path.insert(0, str(SANDBOX))
    try:
        import exemplar_student
        import r4_core_student
        import students
        yield r4_core_student, students, exemplar_student
    finally:
        sys.path.remove(str(SANDBOX))


@pytest.fixture
def runner(monkeypatch):
    monkeypatch.setenv("STUDENT_PATHS", "")          # the module puts STUDENT_PATHS on sys.path at import
    spec = importlib.util.spec_from_file_location("runner_under_test", SANDBOX / "runner.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextlib.contextmanager
def sandbox(state_dir, spec=R4, load=False):
    student = B.SandboxStudent(state_dir, spec=spec, extra="", load=load)
    try:
        yield student
    finally:
        student.close()


# --- host side, no container ------------------------------------------------------------------------

def test_runner_passes_provenance_only_to_a_method_that_declares_it(runner, sandbox_modules):
    r4, students, exemplar = sandbox_modules
    items = [tuple(i) for i in DELIVERY_1]
    for student in (students.EmptyStudent(), exemplar.ExemplarSenseStudent()):
        reply = {}
        runner._deliver(student.learn, {"op": "learn", "items": DELIVERY_1}, reply, items)
        assert reply == {}
        runner._deliver(student.learn, {"op": "learn", "items": DELIVERY_1, "provenance": PROV_1}, reply, items)
        assert reply == {"provenance_delivered": False}
    student, reply = r4.R4CoreStudent(lexicon_dir=NOLEX), {}
    runner._deliver(student.learn, {"op": "learn", "items": DELIVERY_1, "provenance": PROV_1}, reply, items)
    assert reply == {"provenance_delivered": True} and student.state["events"][0]["provenance"] == PROV_1


def test_runner_does_not_mask_a_defect_of_the_student(runner):
    class Faulty:
        def learn(self, items, provenance=None):
            raise TypeError("internal defect")
    with pytest.raises(TypeError, match="internal defect"):
        runner._deliver(Faulty().learn, {"provenance": {}}, {}, [])


def test_bench_sends_provenance_only_when_the_curriculum_declares_it():
    proxy, sent = object.__new__(B.SandboxStudent), []
    proxy._call = sent.append
    teacher = B.Teacher(B.ShownLog())
    teacher.teach(proxy, DELIVERY_1)
    teacher.teach(proxy, DELIVERY_1, provenance=PROV_1)
    proxy.apply_correction(TK1, TEX)
    proxy.apply_correction(TK1, TEX, provenance=PROV_C)
    assert [set(p) for p in sent] == [{"op", "items"}, {"op", "items", "provenance"},
                                      {"op", "correction", "exercise"}, {"op", "correction", "exercise", "provenance"}]
    assert sent[1]["provenance"] == PROV_1 and sent[3]["provenance"] == PROV_C


def test_teacher_correct_forwards_only_the_provenance_of_each_correction():
    proxy, sent = object.__new__(B.SandboxStudent), []
    proxy._call = sent.append
    B.Teacher(B.ShownLog()).correct(proxy)
    B.Teacher(B.ShownLog()).correct(proxy, provenance={"C-2": {"author_id": "SYN-AUT-9"}})
    assert len(sent) == 2 * len(D.C_CORRECTIONS) and all("provenance" not in p for p in sent[:len(D.C_CORRECTIONS)])
    tagged = [p for p in sent if "provenance" in p]
    assert len(tagged) == 1 and tagged[0]["correction"][0] == "C-2" and tagged[0]["provenance"] == {"C-2": {"author_id": "SYN-AUT-9"}}


# --- real bench path: Teacher -> SandboxStudent -> container runner -> student ------------------------

@needs_docker
def test_e2e_declared_provenance_crosses_the_real_bench_path(sandbox_modules, tmp_path):
    r4 = sandbox_modules[0]
    teacher = B.Teacher(B.ShownLog())
    with sandbox(tmp_path / "tagged") as student:
        teacher.teach(student, DELIVERY_1, provenance=PROV_1)
        assert student.provenance_delivered is True
        teacher.teach(student, DELIVERY_2, provenance=PROV_2)
        student.apply_correction(TK1, TEX, provenance=PROV_C)
        assert student.provenance_delivered is True
        answers = [student.answer("mot", q) for q in QUERIES]
        student.save()
    with sandbox(tmp_path / "tagged", load=True) as restarted:                 # replay in a new container
        assert [restarted.answer("mot", q) for q in QUERIES] == answers
    with sandbox(tmp_path / "plain") as plain:                                 # same curriculum, no metadata
        teacher.teach(plain, DELIVERY_1); teacher.teach(plain, DELIVERY_2); plain.apply_correction(TK1, TEX)
        assert plain.provenance_delivered is None
        assert [plain.answer("mot", q) for q in QUERIES] == answers
    s = r4.R4CoreStudent.load(tmp_path / "tagged", lexicon_dir=NOLEX)
    d = s._derive()
    rec = lambda i: s._provenance_record(d, i)
    assert len(d["items"]) == 8 and rec("TP-A1")["occurrences"] == [1, 2]
    assert (rec("TP-A1")["lesson_id"], rec("TP-A1")["source_id"], rec("TP-A1")["author_id"]) == ("SYN-LEC-A", "SYN-SRC-1", "SYN-AUT-1")
    assert all(rec(i)[k] is None for i in ("TP-A2", "TP-A3", "TP-E1", "TP-E2") for k in ("lesson_id", "source_id", "author_id"))
    assert rec("TP-EX")["derived_from"] == ["TP-A2"] and rec("TP-K1")["author_id"] == "SYN-AUT-3"
    assert s._lineage(d, {"TP-K1"}) == {"TP-K1", "TP-EX", "TP-A2"}
    relation = lambda a, b: s._pair_relation(d, {a}, {b})
    assert relation("TP-A1", "TP-B1") == "DISTINCT_PEDAGOGICAL_EVENTS"      # two lessons, one call, two declared sources
    assert relation("TP-A1", "TP-A1-BIS") == "SAME_EVENT"                    # one lesson, two deliveries
    assert relation("TP-A3", "TP-B1") == "SAME_EVENT"                        # undeclared lesson: never promoted
    assert relation("TP-EX", "TP-A2") == "SAME_EVENT"                        # filiation of the corrected exercise
    ids = sorted(d["items"]) + ["TP-K1"]
    assert all(relation(a, b) != "VERIFIED_INDEPENDENT_SOURCES" for a, b in itertools.combinations(ids, 2))
    assert not s._device_pair_is_independent(relation("TP-A1", "TP-B1"))
    st = s._p5l2_status("mot", QUERIES[0])
    assert st["admissible"] is False and st["response_authority"] is False


@needs_docker
def test_e2e_historical_students_receive_no_provenance_and_behave_identically(tmp_path):
    for n, spec in enumerate(HISTORICAL):
        runs = []
        for tag, declared in (("plain", None), ("tagged", PROV_1)):
            state = tmp_path / f"{n}_{tag}"
            with sandbox(state, spec=spec) as student:
                student.learn(DELIVERY_1, provenance=declared)
                ack = student.provenance_delivered
                answers = [student.answer("mot", q) for q in QUERIES]
                student.save()
            runs.append((ack, answers, sorted((p.name, p.read_bytes()) for p in state.iterdir())))
        assert runs[0][0] is None and runs[1][0] is False, spec
        assert runs[0][1:] == runs[1][1:], spec


@needs_docker
def test_e2e_curriculum_without_metadata_leaves_every_observation_unknown(sandbox_modules, tmp_path):
    r4 = sandbox_modules[0]
    teacher = B.Teacher(B.ShownLog())
    with sandbox(tmp_path / "pilot") as student:
        teacher.teach(student, D.E_LESSONS + D.E_EXERCISES)
        teacher.correct(student)
        assert student.provenance_delivered is None
        student.save()
    s = r4.R4CoreStudent.load(tmp_path / "pilot", lexicon_dir=NOLEX)
    d = s._derive()
    assert all(set(ev) == {"revision", "kind", "payload"} for ev in s.state["events"])
    assert all(s._provenance_record(d, i)[k] is None for i in d["items"] for k in ("lesson_id", "source_id", "author_id"))
    ids = [it[0] for it in D.E_LESSONS + D.E_EXERCISES]
    assert all(s._pair_relation(d, {a}, {b}) == "SAME_EVENT" for a, b in itertools.combinations(ids, 2))


@needs_docker
def test_e2e_s_policy_keeps_a_corrige_answer_with_or_without_metadata(tmp_path):
    pt = ("TP-T", "mot", "Le mot vole souvent sur les toits gris.", "L1", "d", "x")
    exc = ("TP-C", "mot", "Le mot vole souvent dans les arbres immenses.", "L1", "d", "x")
    ok = ("TP-KC", "TP-C", "« vole » marque ce sens (L1), pas l’autre (L2).")
    declared = {"TP-T": {"lesson_id": "SYN-LEC-T", "source_id": "SYN-SRC-T"},
                "TP-C": {"lesson_id": "SYN-LEC-C", "source_id": "SYN-SRC-C"}}
    answers = []
    for tag, meta in (("plain", None), ("tagged", declared)):
        with sandbox(tmp_path / tag) as student:
            student.learn([pt, exc, TA2, TA3, TE1, TE2], provenance=meta)
            student.apply_correction(ok, exc)
            answers.append(student.answer("mot", QUERIES[0]))
    assert answers[0] == answers[1] and (answers[0]["sense"], answers[0]["origin"]) == ("L1", "CORRIGE")
