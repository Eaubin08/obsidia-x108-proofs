"""RED MEMORY-INTERFACE tests of the pilot "force" (RED V0.2).

Requalified after the independent audit: these tests check what a faithful lesson store can
do (retrieval by sense / domain / provenance / context / revision, revision history, state
integrity). They are requirements of the student's memory INTERFACE, NOT evidence of
acquisition: a student that merely stores its lessons faithfully may pass them. They are
expected to FAIL against the empty reference student.
The B10 authenticity test is an INVARIANT (open decision: signature), not a student test.
"""
from __future__ import annotations

import hashlib
import sqlite3

from tests.education_pilot import _bench as B
from tests.education_pilot import _pilot_data as D
from tests.education_pilot.conftest import make_commit


def _taught(new_student, name="i"):
    student, teacher = new_student(name), B.Teacher(B.ShownLog())
    teacher.teach(student, D.E_LESSONS + D.E_EXERCISES)
    teacher.correct(student)
    return student


def _taught_ids():
    ids = {it[0]: it[3] for it in D.E_LESSONS + D.E_EXERCISES}
    exercises = {e[0]: e for e in D.E_EXERCISES}
    ids.update({c[0]: exercises[c[1]][3] for c in D.C_CORRECTIONS})
    return ids


def _consistent(hits, sense=None):
    taught = _taught_ids()
    return bool(hits) and all(h.get("provenance") and all(taught.get(p) == h.get("sense") for p in h["provenance"])
                              and (sense is None or h.get("sense") == sense) for h in hits)


def test_interface_retrieval_by_sense(new_student):
    student = _taught(new_student)
    for s in D.FORCE_SENSES:
        assert _consistent(student.retrieve(word="force", sense=s), s), s


def test_interface_retrieval_by_domain(new_student):
    hits = _taught(new_student).retrieve(word="force", domain="physique")
    assert _consistent(hits) and {h.get("sense") for h in hits} == {"F5"}


def test_interface_retrieval_by_provenance(new_student):
    hits = _taught(new_student).retrieve(word="force", provenance="C-2")
    assert _consistent(hits) and all("C-2" in h["provenance"] for h in hits)


def test_interface_retrieval_by_context(new_student):
    hits = _taught(new_student).retrieve(word="force", context="les forces de l'ordre")
    assert _consistent(hits) and hits[0].get("sense") == "F4"


def test_interface_retrieval_by_revision_keeps_the_past(new_student):
    student = _taught(new_student)
    before = student.retrieve(word="force", sense="F6", as_of_revision=1)
    student.apply_correction(D.CONTRADICTION, next(e for e in D.E_EXERCISES if e[0] == D.CONTRADICTION[1]))
    after = student.retrieve(word="force", sense="F6")
    assert _consistent(before, "F6") and after and before != after
    assert student.retrieve(word="force", sense="F6", as_of_revision=1) == before, "history rewritten"


def test_interface_contradiction_keeps_the_previous_version_in_history(new_student):
    student = _taught(new_student)
    old = student.retrieve(word="force", sense="F6")
    student.apply_correction(D.CONTRADICTION, next(e for e in D.E_EXERCISES if e[0] == D.CONTRADICTION[1]))
    history = student.history("force", "F6")
    assert len(history) >= 2 and all(isinstance(h, dict) and "revision" in h for h in history)
    assert any(h.get("content") == old for h in history), "previous version not recoverable"


def test_interface_tampered_student_state_is_detected_on_restart(new_student, tmp_path):
    student = _taught(new_student, name="tamper")
    probe_items = [(w, t) for _, w, t, *_ in D.E_EXERCISES]
    before = [student.answer(w, t) for w, t in probe_items]
    assert any(a.get("sense") not in (None, B.HOLD) for a in before), "nothing stored: integrity cannot be assessed"
    student.save()
    student.close()
    intact = new_student("tamper", load=True)                     # an intact state must reload identically
    assert [intact.answer(w, t) for w, t in probe_items] == before
    intact.close()
    files = sorted(p for p in (tmp_path / "state_tamper").rglob("*") if p.is_file())
    files[0].write_bytes(files[0].read_bytes() + b" ")
    try:
        new_student("tamper", load=True)
    except B.StudentError as exc:
        assert exc.error == "StateIntegrityError", exc.error
        return
    raise AssertionError("altered experimental memory was reloaded without StateIntegrityError")


def test_invariant_b10_forgery_with_recomputed_hash_is_detected(bench_b10, bench_authorization,
                                                              pilot_claim_and_record, tmp_path):
    """Authenticity, not only integrity. Expected RED while no signature exists (open decision)."""
    claim, record = pilot_claim_and_record
    bench_b10.execute_commit(make_commit(claim, record, bench_authorization))
    db = tmp_path / "pilot_b10.db"
    conn = sqlite3.connect(str(db))
    row = conn.execute("SELECT canonical_json FROM b10_artifacts WHERE artifact_id = ?", (claim.claim_id,)).fetchone()
    forged = row[0].replace("F4", "F3")
    conn.execute("UPDATE b10_artifacts SET canonical_json = ?, payload_hash = ? WHERE artifact_id = ?",
                 (forged, hashlib.sha256(forged.encode()).hexdigest(), claim.claim_id))
    conn.commit()
    conn.close()
    from app.knowledge.b10.persistence import B10PersistenceAdapter
    try:
        art = B10PersistenceAdapter(str(db)).get_artifact(claim.claim_id)
    except Exception:
        return
    assert '"F3"' not in art.canonical_json, "forged memory accepted (authenticity not guaranteed)"
