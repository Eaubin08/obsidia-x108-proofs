"""ExemplarSenseStudent — isolated experimental GREEN V0 of the Oxygen polysemy pilot.

Implements design R3 (docs/education/OXYGEN_GREEN_DESIGN_V0.md, sha256 01df067f…).
Exemplar learning with generic contextual features, Naive Bayes + k-NN vote + cue bonus,
abstention by threshold, revisioned memory, canonical single-file state.

Standard library only. It knows no sense before `learn`; every sense label comes from the
teaching items it receives. Local experimental state only: no candidate memory, no promotion,
no B8/B9/B10, no KX108.

Implementation interpretations (not tuning, frozen before any exam run):
- an exemplar's id is the id of the taught sentence (lesson or exercise); the correction ids
  that produced or revised it are kept in its `provenance` for `retrieve` / `history`;
- `answer` cites teaching item ids only (exemplars and, for cues, the corrected exercise),
  never correction ids: a correction is a revision of an item, not a new piece of evidence.
"""
from __future__ import annotations

import hashlib
import json
import math
import pathlib
import re

from features import extract, is_non_trivial, tokenize, weight
from students import HOLD, StateIntegrityError

TAU = 0.5
DELTA = 0.15
K = 3
CORRECTION_WEIGHT = 2.0
CUE_BONUS = 2.0
LAPLACE = 1.0
STATE_FILE = "student_state.json"


def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _quoted_segments(text: str) -> list[str]:
    return [s.strip() for s in re.findall(r"«([^»]+)»", text) if s.strip()]


class ExemplarSenseStudent:
    def __init__(self, state: dict | None = None):
        self.state = state or {"revision": 0, "exemplars": [], "cues": [], "senses": {}, "log": []}

    # --- teaching -----------------------------------------------------------------------------

    def _add_exemplar(self, item, source: str, w: float, provenance: list[str]) -> None:
        item_id, word, sentence, sense, domain, register = item
        rev = self.state["revision"]
        for ex in self._active(word):
            if ex["sentence"] == sentence:                  # same sentence: revise, never erase
                ex["rev_retired"] = rev
        self.state["exemplars"].append({
            "id": item_id, "word": word, "sentence": sentence, "sense": sense, "domain": domain,
            "register": register, "source": source, "features": extract(word, sentence), "weight": w,
            "provenance": provenance, "rev_added": rev, "rev_retired": None})
        info = self.state["senses"].setdefault(word, {}).setdefault(sense, {"count": 0, "domains": []})
        info["count"] += 1
        if domain not in info["domains"]:
            info["domains"].append(domain)

    def learn(self, items):
        self.state["revision"] += 1
        ids = []
        for item in items:
            source = "exercise" if str(item[0]).startswith("EX") else "lesson"
            self._add_exemplar(tuple(item), source, 1.0, [item[0]])
            ids.append(item[0])
        self.state["log"].append({"revision": self.state["revision"], "op": "learn", "ids": ids})

    def apply_correction(self, correction, exercise):
        corr_id, ex_id, text = correction[0], correction[1], correction[2]
        self.state["revision"] += 1
        rev = self.state["revision"]
        exercise = tuple(exercise)
        sense = exercise[3]                                # B3: sense is always ex[3]
        self._add_exemplar(exercise, "correction", CORRECTION_WEIGHT, [corr_id, ex_id])
        for seg in _quoted_segments(text):
            self.state["cues"].append({"id": f"{corr_id}:{seg}", "word": exercise[1], "cue_ngram": seg,
                                       "sense": sense, "source_id": corr_id, "exercise_id": ex_id,
                                       "rev_added": rev, "rev_retired": None})
        self.state["log"].append({"revision": rev, "op": "apply_correction", "ids": [corr_id, ex_id]})

    # --- memory views ---------------------------------------------------------------------------

    def _active(self, word, as_of=None):
        r = self.state["revision"] if as_of is None else as_of
        return [e for e in self.state["exemplars"] if e["word"] == word and e["rev_added"] <= r
                and (e["rev_retired"] is None or e["rev_retired"] > r)]

    def _active_cues(self, word):
        return [c for c in self.state["cues"] if c["word"] == word and c["rev_retired"] is None]

    @staticmethod
    def _view(e) -> dict:
        return {"id": e["id"], "sense": e["sense"], "provenance": list(e["provenance"]),
                "revision": e["rev_added"], "content": e["sentence"]}

    @staticmethod
    def _similarity(a: list[str], b: list[str]) -> float:
        sa, sb = set(a), set(b)
        union = sum(weight(f) for f in sa | sb)
        return sum(weight(f) for f in sa & sb) / union if union else 0.0

    def retrieve(self, word=None, sense=None, domain=None, provenance=None, context=None, as_of_revision=None):
        hits = [e for e in self._active(word, as_of_revision)
                if (sense is None or e["sense"] == sense) and (domain is None or e["domain"] == domain)
                and (provenance is None or provenance in e["provenance"])]
        if context is not None:
            q = extract(word, context)
            hits.sort(key=lambda e: (-self._similarity(q, e["features"]), e["id"], e["rev_added"]))
        else:
            hits.sort(key=lambda e: (e["id"], e["rev_added"]))
        return [self._view(e) for e in hits]

    def history(self, word, sense):
        out, previous = [], None
        for entry in self.state["log"]:
            content = self.retrieve(word=word, sense=sense, as_of_revision=entry["revision"])
            if content != previous:
                out.append({"revision": entry["revision"], "op": entry["op"], "content": content})
                previous = content
        return out

    # --- answering -------------------------------------------------------------------------------

    def _scores(self, word, sentence):
        exemplars = self._active(word)
        q = extract(word, sentence)
        senses = sorted({e["sense"] for e in exemplars})
        counts = {s: {} for s in senses}
        totals = {s: 0.0 for s in senses}
        mass = {s: 0.0 for s in senses}
        vocab = set()
        for e in exemplars:
            mass[e["sense"]] += e["weight"]
            for f in e["features"]:
                counts[e["sense"]][f] = counts[e["sense"]].get(f, 0.0) + e["weight"]
                totals[e["sense"]] += e["weight"]
                vocab.add(f)
        all_mass = sum(mass.values())
        score = {}
        for s in senses:
            ll = math.log(mass[s] / all_mass)
            for f in q:
                ll += weight(f) * math.log((counts[s].get(f, 0.0) + LAPLACE) / (totals[s] + LAPLACE * len(vocab)))
            score[s] = ll
        folded = " ".join(tokenize(sentence))
        cue_hits = []
        for c in self._active_cues(word):
            if " ".join(tokenize(c["cue_ngram"])) in folded and c["sense"] in score:
                score[c["sense"]] += CUE_BONUS
                cue_hits.append(c)
        neighbours = sorted(exemplars, key=lambda e: (-self._similarity(q, e["features"]), e["id"], e["rev_added"]))
        for e in neighbours[:K]:
            score[e["sense"]] += self._similarity(q, e["features"])
        seen = any(is_non_trivial(f) and f in vocab for f in q)
        return score, neighbours, cue_hits, q, seen

    def answer(self, word, sentence):
        if not self._active(word):
            return {"sense": HOLD, "provenance": []}
        score, neighbours, cue_hits, q, seen = self._scores(word, sentence)
        top = max(score.values())
        exp = {s: math.exp(v - top) for s, v in score.items()}
        z = sum(exp.values())
        ranked = sorted(((p / z, s) for s, p in exp.items()), key=lambda t: (-t[0], t[1]))
        p1, best = ranked[0]
        p2 = ranked[1][0] if len(ranked) > 1 else 0.0
        if not seen or p1 <= TAU or p1 - p2 <= DELTA:
            return {"sense": HOLD, "provenance": []}
        prov = [e["id"] for e in neighbours if e["sense"] == best][:K]
        prov += [c["exercise_id"] for c in cue_hits if c["sense"] == best and c["exercise_id"] not in prov]
        return {"sense": best, "provenance": prov}

    # --- persistence -----------------------------------------------------------------------------

    def save(self, directory):
        payload = {"sha256": hashlib.sha256(_canonical(self.state)).hexdigest(), "state": self.state}
        (pathlib.Path(directory) / STATE_FILE).write_bytes(_canonical(payload))

    @classmethod
    def load(cls, directory):
        path = pathlib.Path(directory) / STATE_FILE
        try:
            raw = path.read_bytes()
            payload = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise StateIntegrityError(f"unreadable state: {type(exc).__name__}") from exc
        if not isinstance(payload, dict) or set(payload) != {"sha256", "state"}:
            raise StateIntegrityError("unexpected state layout")
        if raw != _canonical(payload):
            raise StateIntegrityError("state file is not canonical")
        if payload["sha256"] != hashlib.sha256(_canonical(payload["state"])).hexdigest():
            raise StateIntegrityError("state hash mismatch")
        return cls(payload["state"])
