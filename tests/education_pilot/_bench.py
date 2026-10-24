"""Host-side bench for the Oxygen textual pilot "force" (RED V0.2). Test-side only.

Physical separation:
  - the STUDENT runs in a Docker container: no network, read-only root filesystem,
    unprivileged user, all capabilities dropped. Only `student_sandbox/` (read-only), its own
    state directory and, for probes, an extra read-only directory are mounted. The repository,
    this bench and the private exam keys are NOT visible to it.
  - the TEACHER (host) sends only teaching items and corrections, with the provenance the
    curriculum declares for them when it declares one (declared, never verified or inferred).
  - the EXAMINER (host) loads exam items and answer keys from a PRIVATE file outside the
    repository (OXYGEN_PILOT_EXAMS) and sends the student only (word, sentence).
No production module is modified. No canonical memory is touched.
The bench authorization artefact is a TEST artefact. It is never KX108.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import random
import secrets
import shutil
import subprocess
import unicodedata
from dataclasses import dataclass, field
from typing import Any

from tests.education_pilot import _pilot_data as D

PROVISIONAL = {  # pre-registration candidates, NOT validated by the founder (spec §6)
    "acquisition_gain_min": 0.5,
    "acquisition_min_senses": 5,
    "retention_tolerance": 0.10,
    "forgetting_tolerance": 0.10,
    "transfer_fraction_min": 0.5,
    "transfer_min_senses": 4,
    "baseline_margin": 0.25,
    "abstention_appropriate_min": 0.5,
    "abstention_unjustified_max": 0.2,
}
BENCH_AUTHORIZATION_LABEL = "PILOT_BENCH_TEST_AUTHORIZATION_NOT_KX108"
HOLD = "HOLD"

IMAGE = "python@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f"  # python:3.13-slim
SANDBOX_DIR = pathlib.Path(__file__).resolve().parent / "student_sandbox"
DEFAULT_EXAMS = pathlib.Path.home() / "Documents" / "OBSIDIA_PRIVATE" / "education_pilot_force" / "exams_v0.json"
CONTAINER_LABEL = "oxygen_pilot_student=1"
STUDENT_SPEC = os.environ.get("OXYGEN_PILOT_STUDENT", "students:EmptyStudent")
STUDENT_EXTRA = os.environ.get("OXYGEN_PILOT_STUDENT_PATH", "")

STOP = set("le la les l de d du des un une a à au aux il elle ils on en et sa son ses sur par pour ne n pas plus "
           "se s qu que qui ce c est été avec dans je j me m tu te t nous vous leur leurs mon ma mes ton ta tes "
           "vers ont sont être avoir fait très".split())


def sentence_hash(sentence: str) -> str:
    return hashlib.sha256(" ".join(sentence.lower().split()).encode("utf-8")).hexdigest()


def teaching_fingerprint(sentence: str) -> str:
    """RAPPEL identity (§3.8): lower case, folded accents, normalised spaces, final . ! ? removed."""
    folded = "".join(c for c in unicodedata.normalize("NFD", sentence.lower()) if unicodedata.category(c) != "Mn")
    return " ".join(folded.split()).rstrip(" .!?")


def content_words(sentence: str, target: str = "") -> set[str]:
    words = {w for w in re.findall(r"\w+", sentence.lower()) if w not in STOP and len(w) > 2}
    return {w for w in words if not w.startswith(target[:4])} if target else words


# --- Docker isolation ----------------------------------------------------------------

def docker_ready() -> bool:
    if not shutil.which("docker"):
        return False
    return subprocess.run(["docker", "image", "inspect", IMAGE], capture_output=True).returncode == 0


def docker_command(state_dir: pathlib.Path, spec: str, extra: str = "", load: bool = False) -> list[str]:
    cmd = ["docker", "run", "--rm", "-i", "--label", CONTAINER_LABEL, "--network", "none", "--read-only", "--tmpfs", "/tmp:rw,size=16m",
           "--user", "65534:65534", "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
           "--pids-limit", "64", "--memory", "256m",
           "-v", f"{SANDBOX_DIR}:/student:ro", "-v", f"{state_dir}:/state:rw",
           "-e", f"STUDENT={spec}", "-e", "STUDENT_PATHS=/student:/extra", "-e", f"LOAD={'1' if load else '0'}"]
    if extra:
        cmd += ["-v", f"{extra}:/extra:ro"]
    return cmd + [IMAGE, "python", "-I", "-B", "/student/runner.py"]


class StudentError(Exception):
    def __init__(self, error: str, message: str = ""):
        super().__init__(f"{error}: {message}")
        self.error = error


class SandboxStudent:
    """Host-side proxy of a student living in its own container. One container = one process
    lifetime; a new SandboxStudent on the same state_dir with load=True is a restart."""

    def __init__(self, state_dir: pathlib.Path, spec: str | None = None, extra: str | None = None,
                 load: bool = False):
        state_dir.mkdir(parents=True, exist_ok=True)
        self.provenance_delivered = None            # last reply: True/False when provenance was sent, else None
        self.proc = subprocess.Popen(docker_command(state_dir, spec or STUDENT_SPEC,
                                                    STUDENT_EXTRA if extra is None else extra, load),
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     text=True, encoding="utf-8")
        ready = self._read()
        if not ready.get("ok"):
            self.close()
            raise StudentError(ready.get("error", "Unknown"), ready.get("message", ""))

    def _read(self) -> dict:
        line = self.proc.stdout.readline()
        if not line:
            raise StudentError("NoResponse", self.proc.stderr.read()[-500:])
        return json.loads(line)

    def _call(self, payload: dict) -> Any:
        self.proc.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
        self.proc.stdin.flush()
        resp = self._read()
        if not resp.get("ok"):
            raise StudentError(resp.get("error", "Unknown"), resp.get("message", ""))
        self.provenance_delivered = resp.get("provenance_delivered")
        return resp.get("result")

    def learn(self, items, provenance=None):
        payload = {"op": "learn", "items": [list(i) for i in items]}
        if provenance:
            payload["provenance"] = provenance
        return self._call(payload)

    def apply_correction(self, correction, exercise, provenance=None):
        payload = {"op": "apply_correction", "correction": list(correction), "exercise": list(exercise)}
        if provenance:
            payload["provenance"] = provenance
        return self._call(payload)

    def answer(self, word, sentence):
        return self._call({"op": "answer", "word": word, "sentence": sentence}) or {}

    def retrieve(self, **query):
        return self._call({"op": "retrieve", "query": query}) or []

    def history(self, word, sense):
        return self._call({"op": "history", "word": word, "sense": sense}) or []

    def save(self):
        return self._call({"op": "save"})

    def probe(self):
        return self._call({"op": "probe"})

    def close(self):
        try:
            if self.proc.poll() is None:
                self.proc.stdin.write(json.dumps({"op": "close"}) + "\n")
                self.proc.stdin.flush()
                self.proc.wait(timeout=30)
        except Exception:
            self.proc.kill()


# --- Private exams (host only) -----------------------------------------------------------

def exams_path() -> pathlib.Path:
    return pathlib.Path(os.environ.get("OXYGEN_PILOT_EXAMS", str(DEFAULT_EXAMS)))


def load_private_exams() -> dict[str, Any]:
    data = json.loads(exams_path().read_text(encoding="utf-8"))
    return {k: [tuple(i) for i in v] if isinstance(v, list) else v for k, v in data.items()}


# --- Teacher / Examiner / Score --------------------------------------------------------------

@dataclass
class ShownLog:
    hashes: set[str] = field(default_factory=set)
    fingerprints: set[str] = field(default_factory=set)

    def record(self, sentence: str) -> None:
        self.hashes.add(sentence_hash(sentence))
        self.fingerprints.add(teaching_fingerprint(sentence))


class Teacher:
    def __init__(self, log: ShownLog):
        self.log = log

    def teach(self, student, items, provenance=None) -> None:
        for it in items:
            self.log.record(it[2])
        if provenance:
            student.learn(list(items), provenance=provenance)
        else:
            student.learn(list(items))

    def correct(self, student, provenance=None) -> None:
        exercises = {e[0]: e for e in D.E_EXERCISES}
        for corr in D.C_CORRECTIONS:
            ex = exercises[corr[1]]
            self.log.record(ex[2])
            declared = {k: v for k, v in (provenance or {}).items() if k in (corr[0], ex[0])}
            if declared:
                student.apply_correction(corr, ex, provenance=declared)
            else:
                student.apply_correction(corr, ex)


@dataclass
class Score:
    per_item: list[dict[str, Any]]

    def _subset(self, word=None, sense=None, expect_hold=None):
        out = self.per_item
        if word is not None:
            out = [r for r in out if r["word"] == word]
        if sense is not None:
            out = [r for r in out if r["expected"] == sense]
        if expect_hold is not None:
            out = [r for r in out if (r["expected"] == HOLD) == expect_hold]
        return out

    def accuracy(self, word="force", sense=None) -> float:
        rows = self._subset(word, sense, expect_hold=False)
        return sum(r["answer"] == r["expected"] for r in rows) / len(rows) if rows else 0.0

    def abstention_appropriate(self, word="force") -> float:
        rows = self._subset(word, expect_hold=True)
        return sum(r["answer"] == HOLD for r in rows) / len(rows) if rows else 0.0

    def abstention_unjustified(self, word="force") -> float:
        rows = self._subset(word, expect_hold=False)
        return sum(r["answer"] == HOLD for r in rows) / len(rows) if rows else 0.0


class Examiner:
    """Holds the private exams. Sends the student only (word, sentence), in an order shuffled
    with a private seed that never leaves the examiner. Answers are re-associated with the
    internal item id on the host side."""

    def __init__(self, log: ShownLog, seed: int | None = None):
        self.log = log
        self._rng = random.Random(secrets.randbits(64) if seed is None else seed)

    def order(self, exam) -> list:
        return self._rng.sample(list(exam), len(exam))

    def check_unseen(self, exam) -> list[str]:
        """Exam items already shown, by exact hash or by the RAPPEL fingerprint: a recall is never unseen."""
        return [it[0] for it in exam if sentence_hash(it[2]) in self.log.hashes
                or teaching_fingerprint(it[2]) in self.log.fingerprints]

    def score(self, student, exam) -> Score:
        rows = []
        for item_id, word, sentence, expected, domain, register in self.order(exam):
            ans = student.answer(word, sentence)
            rows.append({"id": item_id, "word": word, "expected": expected, "answer": ans.get("sense"),
                         "provenance": ans.get("provenance") or [], "domain": domain, "register": register})
        return Score(rows)


# --- Trivial baselines (host, teaching data only) ---------------------------------------------

def _trigrams(s: str) -> set[str]:
    s = f"  {' '.join(s.lower().split())}  "
    return {s[i:i + 3] for i in range(len(s) - 2)}


def baseline_answer(kind: str, word: str, sentence: str) -> str:
    lessons = [l for l in D.E_LESSONS + D.E_EXERCISES + D.CONCURRENT_LESSONS if l[1] == word]
    if not lessons:
        return HOLD
    if kind == "first_lesson":
        return lessons[0][3]
    if kind == "majority":
        senses = [l[3] for l in lessons]
        return max(dict.fromkeys(senses), key=senses.count)
    if kind == "memorizer":
        same = [l for l in lessons if sentence_hash(l[2]) == sentence_hash(sentence)]
        return same[0][3] if same else HOLD
    if kind == "keyword":
        best = max(lessons, key=lambda l: len(content_words(l[2], word) & content_words(sentence, word)))
        return best[3] if content_words(best[2], word) & content_words(sentence, word) else HOLD
    if kind == "trigram":
        return max(lessons, key=lambda l: len(_trigrams(l[2]) & _trigrams(sentence))
                   / max(1, len(_trigrams(l[2]) | _trigrams(sentence))))[3]
    raise ValueError(kind)


BASELINES = ("first_lesson", "majority", "memorizer", "keyword", "trigram")


def baseline_score(exam, kind: str) -> Score:
    return Score([{"id": i, "word": w, "expected": e, "answer": baseline_answer(kind, w, t), "provenance": [],
                   "domain": d, "register": r} for i, w, t, e, d, r in exam])


def best_baseline_accuracy(exam, word="force", sense=None) -> float:
    return max(baseline_score(exam, k).accuracy(word=word, sense=sense) for k in BASELINES)


def senses_beating_baselines(score: Score, exam, margin: float = 0.0) -> list[str]:
    return [s for s in D.FORCE_SENSES
            if any(r["expected"] == s for r in score.per_item)
            and score.accuracy(sense=s) > best_baseline_accuracy(exam, sense=s) + margin]


def kill_leftover_containers() -> None:
    if shutil.which("docker"):
        ids = subprocess.run(["docker", "ps", "-q", "--filter", f"label={CONTAINER_LABEL}"],
                             capture_output=True, text=True).stdout.split()
        if ids:
            subprocess.run(["docker", "kill", *ids], capture_output=True)
