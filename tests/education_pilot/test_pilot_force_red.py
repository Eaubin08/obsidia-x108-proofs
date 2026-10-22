"""RED ACQUISITION tests of the pilot "force" (RED V0.3).

Expected to FAIL against the empty reference student. Each test asserts one pure criterion
of `_criteria.py`; the controls prove that the PERFECT reference satisfies every criterion
(feasibility) and that trivial strategies, including a position oracle under shuffled order,
satisfy none (discrimination). A criterion that the perfect reference fails would be an
INVALID_TEST, not a missing capability.

One campaign per module, sequential, at most one student container alive at a time:
X0 -> teach E + corrections -> X1, X1_FAR, X4 -> save, new container from state -> X2
-> concurrent lessons -> X3. Exam order is shuffled with a private examiner seed.
Thresholds are PROVISIONAL; samples are technical (see the report §6).
"""
from __future__ import annotations

import pytest

from tests.education_pilot import _bench as B
from tests.education_pilot import _criteria as C
from tests.education_pilot import _pilot_data as D


@pytest.fixture(scope="module")
def campaign(sandbox_ready, exams, tmp_path_factory):
    state = tmp_path_factory.mktemp("campaign") / "state"
    log = B.ShownLog()
    teacher, examiner = B.Teacher(log), B.Examiner(log)
    S = {}
    student = B.SandboxStudent(state)
    try:
        S["X0"] = examiner.score(student, exams["X0"])
        teacher.teach(student, D.E_LESSONS + D.E_EXERCISES)
        teacher.correct(student)
        for k in ("X1", "X1_FAR", "X4"):
            S[k] = examiner.score(student, exams[k])
        student.save()
    finally:
        student.close()
    restarted = B.SandboxStudent(state, load=True)       # new container, saved state only
    try:
        S["X2"] = examiner.score(restarted, exams["X2"])
        teacher.teach(restarted, D.CONCURRENT_LESSONS)
        S["X3"] = examiner.score(restarted, exams["X3"])
    finally:
        restarted.close()
    for k in ("X1", "X1_FAR", "X2", "X3", "X4"):
        assert examiner.check_unseen(exams[k]) == [], f"protocol leak on {k}"
    return S


@pytest.mark.parametrize("name", list(C.CRITERIA))
def test_red_acquisition(campaign, exams, name):
    assert C.CRITERIA[name](campaign, exams), f"criterion {name} not met"
