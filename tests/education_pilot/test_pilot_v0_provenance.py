"""Real V0 provenance (R4.4 V1.5): the manifest of the historical teaching curriculum and its transport.
Teaching data only, no exam; every value is read from the curriculum artefact or left UNKNOWN."""
from __future__ import annotations

import contextlib
import hashlib
import shutil
import sys

import pytest

from tests.education_pilot import _bench as B
from tests.education_pilot import _pilot_data as D
from tests.education_pilot import _pilot_provenance as P

SANDBOX = B.SANDBOX_DIR
NOLEX = str(SANDBOX / "__no_lexicon__")
TAUGHT = D.E_LESSONS + D.E_EXERCISES
PROBES = [(it[1], it[2]) for it in TAUGHT + D.CONCURRENT_LESSONS]
needs_docker = pytest.mark.skipif(not B.docker_ready(), reason="HOLD_SECURITY_BOUNDARY: Docker isolation unavailable")


@pytest.fixture(scope="module")
def r4():
    sys.path.insert(0, str(SANDBOX))
    try:
        import r4_core_student
        yield r4_core_student
    finally:
        sys.path.remove(str(SANDBOX))


@contextlib.contextmanager
def sandbox(state_dir, load=False):
    student = B.SandboxStudent(state_dir, spec="r4_core_student:R4CoreStudent", extra="", load=load)
    try:
        yield student
    finally:
        student.close()


def teach_v0(student, manifest=None):
    teacher = B.Teacher(B.ShownLog())
    declared = (lambda ids: P.declared_provenance(manifest, ids)) if manifest else (lambda ids: None)
    teacher.teach(student, TAUGHT, provenance=declared([it[0] for it in TAUGHT]))
    teacher.correct(student, provenance=declared([c[0] for c in D.C_CORRECTIONS]))


def test_manifest_describes_exactly_the_v0_curriculum_artifact():
    m = P.load_manifest()
    raw = (P.REPO / m["curriculum"]["path"]).read_bytes()
    assert m["curriculum"]["sha256"] == hashlib.sha256(raw).hexdigest() and m["curriculum"]["bytes"] == len(raw)
    corrections = D.C_CORRECTIONS + [D.CONTRADICTION]
    assert list(m["observations"]) == [it[0] for it in TAUGHT + D.CONCURRENT_LESSONS] + [c[0] for c in corrections]
    g = m["groupings"]
    assert g["E_LESSONS"]["items"] == [it[0] for it in D.E_LESSONS] and g["E_EXERCISES"]["items"] == [it[0] for it in D.E_EXERCISES]
    assert g["TEACHING_SETS"]["E"] == [it[0] for it in D.TEACHING_SETS["E"]]
    assert m["pedagogical_source"] == {"source_id": None, "author_id": None, "status": "UNKNOWN"}
    assert m["source_independence"] == "NOT_ATTESTED"
    assert all((o["lesson_id"], o["source_id"], o["author_id"]) == (None, None, None) for o in m["observations"].values())
    assert {k: o["derived_from"] for k, o in m["observations"].items() if o["derived_from"]} == {c[0]: [c[1]] for c in corrections}


def test_manifest_is_refused_when_the_curriculum_artifact_differs(tmp_path):
    rel = P.load_manifest()["curriculum"]["path"]
    copy = tmp_path / rel
    copy.parent.mkdir(parents=True)
    shutil.copyfile(P.REPO / rel, copy)
    assert P.load_manifest(repo=tmp_path)["curriculum"]["path"] == rel          # an identical copy is accepted
    copy.write_bytes(copy.read_bytes().replace(b"vieil homme", b"homme"))
    with pytest.raises(ValueError):
        P.load_manifest(repo=tmp_path)


def test_only_attested_fields_are_transported():
    m = P.load_manifest()
    assert P.declared_provenance(m, [it[0] for it in TAUGHT + D.CONCURRENT_LESSONS]) == {}
    assert P.declared_provenance(m, [c[0] for c in D.C_CORRECTIONS]) == {c[0]: {"derived_from": [c[1]]} for c in D.C_CORRECTIONS}


def test_v0_answers_and_records_are_identical_with_or_without_the_manifest(r4):
    plain, tagged = r4.R4CoreStudent(lexicon_dir=NOLEX), r4.R4CoreStudent(lexicon_dir=NOLEX)
    teach_v0(plain)
    teach_v0(tagged, P.load_manifest())
    assert [plain.answer(w, q) for w, q in PROBES] == [tagged.answer(w, q) for w, q in PROBES]
    dp, dt = plain._derive(), tagged._derive()
    assert all(plain._provenance_record(dp, i) == tagged._provenance_record(dt, i) for i in [*dp["items"], *dp["corrections"]])
    assert [ev["revision"] for ev in tagged.state["events"] if "provenance" in ev] == [2, 3, 4, 5]
    assert not any("provenance" in ev for ev in plain.state["events"])


@needs_docker
def test_e2e_v0_manifest_crosses_the_real_bench_without_changing_any_answer(r4, tmp_path):
    manifest, runs = P.load_manifest(), {}
    for tag, m in (("plain", None), ("tagged", manifest)):
        with sandbox(tmp_path / tag) as student:
            teach_v0(student, m)
            ack = student.provenance_delivered                                # reply to the last correction
            runs[tag] = (ack, [student.answer(w, q) for w, q in PROBES])
            student.save()
    assert runs["plain"][0] is None and runs["tagged"][0] is True
    assert runs["plain"][1] == runs["tagged"][1]
    with sandbox(tmp_path / "tagged", load=True) as restarted:
        assert [restarted.answer(w, q) for w, q in PROBES] == runs["tagged"][1]
    s = r4.R4CoreStudent.load(tmp_path / "tagged", lexicon_dir=NOLEX)
    d = s._derive()
    assert len(d["items"]) == len(TAUGHT) and s._provenance_record(d, "EX-F1")["occurrences"] == [1, 2]
    assert {s._provenance_record(d, i)["teaching_event_id"] for i in d["items"]} == {1}
    assert all(s._provenance_record(d, i)[k] is None for i in d["items"] for k in ("lesson_id", "source_id", "author_id"))
    assert {c: s._provenance_record(d, c)["derived_from"] for c in d["corrections"]} == {c[0]: [c[1]] for c in D.C_CORRECTIONS}
    assert s._pair_relation(d, {"E-F1-1"}, {"E-F1-2"}) == "SAME_EVENT"          # one delivery, lessons unknown
    st = s._p5l2_status("force", D.E_EXERCISES[0][2])
    assert st["admissible"] is False and st["response_authority"] is False
