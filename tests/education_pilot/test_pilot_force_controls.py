"""Controls of the pilot bench "force" (RED V0.2). Expected to PASS.

They check the bench itself: physical exam isolation (Docker read restriction proven by a
probe that searches the whole container filesystem), data separation, authority and B10
boundaries, and that the repository holds no exam key. They do not test learning.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sqlite3
import subprocess
from itertools import combinations

import pytest

from tests.education_pilot import _bench as B
from tests.education_pilot import _criteria as C
from tests.education_pilot import _pilot_data as D
from tests.education_pilot.conftest import make_commit

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXAM_KEYS = ("V_VALIDATION", "X0", "X1", "X1_FAR", "X2", "X3", "X4")


def _exam_items(exams):
    return [it for k in EXAM_KEYS for it in exams[k]]


# --- Physical isolation of the exams -----------------------------------------------------------

PROBE_SOURCE = '''
import json, os, socket, sys
NEEDLES = {needles!r}

class Probe:
    def probe(self):
        found, scanned = [], 0
        for top in ("/",):
            for dirpath, dirnames, filenames in os.walk(top):
                if dirpath.startswith(("/proc", "/sys", "/dev")):
                    dirnames[:] = []
                    continue
                for name in filenames:
                    path = os.path.join(dirpath, name)
                    try:
                        if os.path.getsize(path) > 4_000_000:
                            continue
                        data = open(path, "rb").read().decode("utf-8", "ignore")
                    except Exception:
                        continue
                    scanned += 1
                    for n in NEEDLES:
                        if n in data and not path.startswith("/extra/"):
                            found.append([path, n[:40]])
        try:
            socket.create_connection(("1.1.1.1", 53), timeout=2).close()
            network = "OPEN"
        except Exception as exc:
            network = type(exc).__name__
        try:
            import tests.education_pilot  # noqa: F401
            repo_import = "IMPORTED"
        except Exception as exc:
            repo_import = type(exc).__name__
        try:
            open("/rootfs_write_test", "w").write("x")
            rootfs = "WRITABLE"
        except Exception as exc:
            rootfs = type(exc).__name__
        mounts = [l.split()[1] for l in open("/proc/mounts") if l.split()[1].startswith(("/student", "/state", "/extra", "/host", "/mnt", "/c", "/Users"))]
        return {{"found": found, "scanned": scanned, "network": network, "repo_import": repo_import,
                "rootfs": rootfs, "uid": os.getuid(), "mounts": mounts,
                "env_keys": sorted(k for k in os.environ if "EXAM" in k.upper() or "OXYGEN" in k.upper())}}
'''


def test_control_student_container_cannot_read_exam_keys_or_reach_the_host(new_student, exams, tmp_path):
    needles = [exams["_canary"], B.exams_path().name] + [it[2] for it in _exam_items(exams)]
    extra = tmp_path / "probe_extra"
    extra.mkdir()
    (extra / "probe_student.py").write_text(PROBE_SOURCE.format(needles=needles), encoding="utf-8")
    report = new_student("probe", spec="probe_student:Probe", extra=str(extra)).probe()
    assert report["scanned"] > 500, report["scanned"]               # the probe really read the filesystem
    assert report["found"] == [], report["found"]                    # no exam key, sentence or canary visible
    assert report["network"] != "OPEN"
    assert report["repo_import"] != "IMPORTED"
    assert report["rootfs"] != "WRITABLE"
    assert report["uid"] == 65534
    assert sorted(report["mounts"]) == ["/extra", "/state", "/student"], report["mounts"]
    assert report["env_keys"] == [], report["env_keys"]


def test_control_no_exam_fragment_in_tracked_untracked_or_ignored_files(exams):
    needles = [exams["_canary"]] + [it[2] for it in _exam_items(exams)]
    skip = {".git", "node_modules", ".venv", "venv"}
    hits, scanned = [], 0
    for path in ROOT.rglob("*"):
        if any(part in skip for part in path.relative_to(ROOT).parts) or not path.is_file():
            continue
        if path.stat().st_size > 5_000_000:
            continue
        data = path.read_bytes()
        scanned += 1
        for n in needles:
            if n.encode("utf-8") in data:
                hits.append((str(path.relative_to(ROOT)), n[:30]))
    assert scanned > 100 and hits == [], hits


def test_control_exam_file_lives_outside_the_repository():
    assert ROOT not in B.exams_path().resolve().parents


# --- Data separation ---------------------------------------------------------------------------

def _hashes(items):
    return {B.sentence_hash(it[2]) for it in items}


def test_control_teaching_and_exam_sets_are_pairwise_disjoint(exams):
    sets = {"E": D.E_LESSONS + D.E_EXERCISES, "CONC": D.CONCURRENT_LESSONS, **{k: exams[k] for k in EXAM_KEYS}}
    for (a, ia), (b, ib) in combinations(sets.items(), 2):
        assert not (_hashes(ia) & _hashes(ib)), f"shared sentence between {a} and {b}"


def test_control_no_exam_item_is_a_near_copy_of_a_teaching_item(exams):
    teaching = D.E_LESSONS + D.E_EXERCISES + D.CONCURRENT_LESSONS
    for it in _exam_items(exams):
        a = B.content_words(it[2], it[1])
        for e in teaching:
            b = B.content_words(e[2], it[1])
            assert len(a & b) / max(1, len(a | b)) <= 0.5, (it[0], e[0])


def test_control_far_exam_shares_no_content_word_with_teaching(exams):
    teaching = D.E_LESSONS + D.E_EXERCISES + D.CONCURRENT_LESSONS
    for it in exams["X1_FAR"]:
        for e in teaching:
            assert not (B.content_words(e[2], it[1]) & B.content_words(it[2], it[1])), (it[0], e[0])


def test_control_corrections_come_only_from_E_exercises():
    exercise_ids = {e[0] for e in D.E_EXERCISES}
    assert all(c[1] in exercise_ids for c in D.C_CORRECTIONS) and D.CONTRADICTION[1] in exercise_ids


def test_control_every_sense_taught_and_examined_and_hold_present(exams):
    for sense in D.FORCE_SENSES:
        assert any(it[3] == sense for it in D.E_LESSONS)
        for k in ("X1", "X2", "X3", "X4"):
            assert any(it[3] == sense for it in exams[k]), (sense, k)
    for k in ("X0", "X1", "X2", "X3", "X4"):
        assert any(it[3] == B.HOLD for it in exams[k]), k
    for word, senses in (("chemin", ("C1", "C2")), ("corriger", ("R1", "R2"))):
        assert {it[3] for it in exams["X3"] if it[1] == word} == set(senses)


def test_control_teacher_never_shows_exams_and_leak_detector_works(exams):
    log = B.ShownLog()

    class Sink:
        def learn(self, items): pass
        def apply_correction(self, c, e): pass

    teacher, examiner = B.Teacher(log), B.Examiner(log)
    teacher.teach(Sink(), D.E_LESSONS + D.E_EXERCISES + D.CONCURRENT_LESSONS)
    teacher.correct(Sink())
    for k in EXAM_KEYS:
        assert examiner.check_unseen(exams[k]) == [], k
    teacher.teach(Sink(), [exams["X1"][0]])                       # injected leak must be detected
    assert examiner.check_unseen(exams["X1"]) == [exams["X1"][0][0]]


def test_control_baselines_are_computed_from_teaching_only(exams):
    for kind in B.BASELINES:
        assert B.baseline_answer(kind, "inconnu", "phrase") == B.HOLD
        B.baseline_score(exams["X1"], kind)


# --- Feasibility and discrimination of the acquisition criteria (host only) ---------------------

def test_control_perfect_reference_satisfies_every_acquisition_criterion(exams):
    S = C.perfect_reference(exams)
    invalid = [n for n, f in C.CRITERIA.items() if not f(S, exams)]
    assert invalid == [], f"INVALID_TEST: {invalid}"


def test_control_every_baseline_ceiling_leaves_a_reachable_margin(exams):
    for k in ("X1", "X1_FAR", "X2", "X3", "X4"):
        assert B.best_baseline_accuracy(exams[k]) + B.PROVISIONAL["baseline_margin"] <= 1.0, k
    for w in ("chemin", "corriger"):
        assert B.best_baseline_accuracy(exams["X3"], word=w) + B.PROVISIONAL["baseline_margin"] <= 1.0, w


def _position_oracle():
    order = {}
    for it in D.E_LESSONS + D.E_EXERCISES + D.CONCURRENT_LESSONS:
        order.setdefault(it[1], [])
        if it[3] not in order[it[1]]:
            order[it[1]].append(it[3])
    seen = {}

    def answer(pos, w, t, e):
        if pos == 0:
            seen.clear()
        n = seen.get(w, 0)
        seen[w] = n + 1
        senses = order.get(w, [])
        return (senses[n] if n < len(senses) else B.HOLD), []
    return answer


def _trivial_strategies():
    out = {f"baseline_{k}": (lambda k: lambda pos, w, t, e: (B.baseline_answer(k, w, t), []))(k) for k in B.BASELINES}
    out["always_hold"] = lambda pos, w, t, e: (B.HOLD, [])
    for s in D.FORCE_SENSES:
        out[f"constant_{s}"] = (lambda s: lambda pos, w, t, e: (s if w == "force" else B.HOLD, []))(s)
    return out


def test_control_no_trivial_strategy_satisfies_any_acquisition_criterion(exams):
    for name, fn in _trivial_strategies().items():
        S = C.strategy_scores(exams, fn, B.Examiner(B.ShownLog(), seed=1))
        passed = [n for n, f in C.CRITERIA.items() if f(S, exams)]
        assert passed == [], f"INVALID_DISCRIMINATION: {name} passes {passed}"


def test_control_position_oracle_fails_under_many_independent_permutations(exams):
    hits = {}
    for seed in range(200):
        S = C.strategy_scores(exams, _position_oracle(), B.Examiner(B.ShownLog(), seed=seed))
        for n, f in C.CRITERIA.items():
            hits[n] = hits.get(n, 0) + bool(f(S, exams))
    assert all(v == 0 for v in hits.values()), f"INVALID_DISCRIMINATION: {hits}"


def test_control_position_oracle_would_win_without_shuffling(exams):
    """Positive control: the B1 leak is real in file order, so the shuffle is what blocks it."""
    S = {k: C.scored(exams[k], _position_oracle()) for k in ("X0", "X1", "X1_FAR", "X2", "X3", "X4")}
    assert S["X1"].accuracy() == 1.0


def test_control_examiner_order_is_shuffled_and_differs_between_examiners(exams):
    orders = {tuple(it[0] for it in B.Examiner(B.ShownLog()).order(exams["X3"])) for _ in range(20)}
    assert len(orders) > 10
    assert tuple(it[0] for it in exams["X3"]) not in orders or len(orders) > 10


def test_control_student_receives_only_word_and_sentence(exams):
    calls = []

    class Spy:
        def answer(self, *args, **kwargs):
            calls.append((args, kwargs))
            return {"sense": B.HOLD, "provenance": []}

    B.Examiner(B.ShownLog()).score(Spy(), exams["X1"])
    sent = {(it[1], it[2]) for it in exams["X1"]}
    assert all(kw == {} and len(a) == 2 and a in sent for a, kw in calls) and len(calls) == len(exams["X1"])
    payload = "".join(map(str, calls))
    assert not any(it[0] in payload for it in exams["X1"]), "item id exposed"


# --- Witness (refutable, independent of the student under test) ---------------------------------

def test_control_witness_detects_an_untaught_gain_and_accepts_stability(exams):
    stable = C.strategy_scores(exams, lambda pos, w, t, e: (B.HOLD, []), B.Examiner(B.ShownLog(), seed=3))
    assert C.witness_stable(stable["X0"], stable["X1"])
    leaky = dict(stable)
    leaky["X1"] = C.scored(exams["X1"], lambda pos, w, t, e: ("T1" if w == "table" else B.HOLD, []))
    assert not C.witness_stable(leaky["X0"], leaky["X1"])
    ref = C.perfect_reference(exams)
    ref["X1"] = C.scored(exams["X1"], lambda pos, w, t, e: (e if w != "table" else "T1", []))
    assert not C.t1_acquisition(ref, exams), "a gain on the untaught witness must invalidate T1"


# --- Authority and B10 boundaries ------------------------------------------------------------------

def test_control_bench_authorization_is_never_kx108(bench_authorization):
    assert B.BENCH_AUTHORIZATION_LABEL.endswith("NOT_KX108")
    assert bench_authorization.granted_by == B.BENCH_AUTHORIZATION_LABEL


def test_control_b10_rejects_a_commit_without_authorization(bench_b10, pilot_claim_and_record):
    claim, record = pilot_claim_and_record
    bench_b10.execute_commit(make_commit(claim, record, None))
    assert not bench_b10.artifact_exists(claim.claim_id)


def test_control_b10_detects_a_naive_tamper(bench_b10, bench_authorization, pilot_claim_and_record, tmp_path):
    claim, record = pilot_claim_and_record
    bench_b10.execute_commit(make_commit(claim, record, bench_authorization))
    conn = sqlite3.connect(str(tmp_path / "pilot_b10.db"))
    conn.execute("UPDATE b10_artifacts SET canonical_json = replace(canonical_json, 'F4', 'F3') WHERE artifact_id = ?",
                 (claim.claim_id,))
    conn.commit()
    conn.close()
    from app.knowledge.b10.persistence import B10PersistenceAdapter
    with pytest.raises(Exception):
        B10PersistenceAdapter(str(tmp_path / "pilot_b10.db")).get_artifact(claim.claim_id)


# --- Worktree ------------------------------------------------------------------------------------------

def _worktree_fingerprint():
    out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], capture_output=True,
                         text=True, check=True, cwd=str(ROOT)).stdout
    rows = []
    for line in out.splitlines():
        path = ROOT / line[3:].strip().strip('"')
        rows.append((line, hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "-"))
    return rows


def test_control_bench_leaves_the_worktree_unchanged(new_student):
    before = _worktree_fingerprint()
    student = new_student("wt")
    B.Teacher(B.ShownLog()).teach(student, D.E_LESSONS)
    student.save()
    assert before == _worktree_fingerprint()
