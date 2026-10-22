"""P-ALIGN feasibility gate (R4.2.2, contract K1 + B1-B5 + F-A + closure), teaching data only.

Leave-one-out over the 18 labelled "force" teaching items (lessons + exercises). For a held-out
item i, the learner state is rebuilt WITHOUT: item i, every correction whose exercise is i (its
glosses and contrasts), and the contradiction if it targets i. No exam data, no thresholds tuned.
Inputs: tests/education_pilot/_pilot_data.py, frozen lexicon export V1 (read-only JSONL).
Thresholds (fixed in R4.2): support >= 6 non-mute items, precision >= 0.50.
Usage: python -B tests/education_pilot/r4_p_align_measure.py <export_v1_dir>
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tests.education_pilot import _pilot_data as D  # noqa: E402

EXPECTED = {"thes_fr.jsonl": "378e4809508a1ac6cc4e6bfb7ea840125606410b16c69adf72bc22ff531188de",
            "morphalou_fr.jsonl": "9e6e60da4b771bb8726838a877a227e5d2ebd7778f6e3ec6fe10d0adc31fdee6"}
MIN_SUPPORT, MIN_PRECISION = 6, 0.50
# Closed function-word class, identical to the frozen V0 extractor (features.FUNCTION_WORDS).
sys.path.insert(0, str(ROOT / "tests" / "education_pilot" / "student_sandbox"))
from features import FUNCTION_WORDS, stem  # noqa: E402
NEGATION_MARKERS = [("pas",), ("non",), ("plutot", "que"), ("au", "lieu", "de")]


def fold(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(c) != "Mn")


def tokens(text: str) -> list[str]:
    return re.findall(r"\w+", fold(text))          # apostrophe splits elisions (B1/NB2)


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


class Lexicon:
    def __init__(self, export: pathlib.Path):
        for name, h in EXPECTED.items():
            if sha(export / name) != h:
                raise SystemExit(f"HOLD: {name} fingerprint mismatch")
        self.groups = {}          # target lemma -> list of (group_id, single-token set, multiword token tuples)
        self.lemmas = {}          # folded surface form -> set of folded lemmas
        with open(export / "morphalou_fr.jsonl", encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                self.lemmas.setdefault(fold(r["surface_form"]), set()).add(fold(r["lemma"]))
        with open(export / "thes_fr.jsonl", encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                single = {fold(s) for s in r["synonyms"] if " " not in s.strip()}
                multi = [tuple(tokens(s)) for s in r["synonyms"] if " " in s.strip()]
                self.groups.setdefault(fold(r["lemma"]), []).append((r["sense_id"], single, multi))

    def evoked(self, target: str, toks: list[str]) -> dict[str, float]:
        """group_id -> weight w = max 1/k over evoking words (B1); direct membership only."""
        tstem = stem(target)
        content = [t for t in toks if t not in FUNCTION_WORDS and len(t) > 2 and not t.startswith(tstem)]
        out = {}
        for gid, single, multi in self.groups.get(fold(target), []):
            w = 0.0
            for t in content:
                cands = self.lemmas.get(t, set())
                if cands and cands & single:
                    w = max(w, 1.0 / len(cands))
            for m in multi:                          # consecutive surface match, k = 1
                if any(tuple(toks[i:i + len(m)]) == m for i in range(len(toks) - len(m) + 1)):
                    w = max(w, 1.0)
            if w > 0:
                out[gid] = w
        return out


def parse_correction(text: str, ex_label: str, labels: set[str]):
    """K2 + B3 + R4.2.2: returns (status, contrasts, glosses{label: tokens})."""
    quoted = re.findall(r"«([^»]+)»", text)
    body = text
    for q in quoted:
        body = body.replace(q, " ")
    toks = tokens(body)
    lab = {fold(l): l for l in labels}
    cut = len(toks)
    for i in range(len(toks)):
        for m in NEGATION_MARKERS:
            if tuple(toks[i:i + len(m)]) == m:
                cut = min(cut, i)
    pos, neg = toks[:cut], toks[cut:]
    pos_labels = sorted({lab[t] for t in pos if t in lab})
    neg_labels = sorted({lab[t] for t in neg if t in lab})
    clean = lambda seg: [t for t in seg if t not in lab]
    if not pos_labels:
        return "NON_RECONNU", [], {}
    if len(pos_labels) > 1:
        return "MALFORME", [], {}
    p = pos_labels[0]
    if p != ex_label:
        return ("MALFORME" if cut < len(toks) else "CONTESTE"), [], {}
    glosses = {ex_label: clean(pos)}
    contrasts = []
    for n in neg_labels:
        if n != p:
            contrasts.append((p, n))
            glosses.setdefault(n, []).extend(clean(neg))
    return "OK", contrasts, glosses


def build_links(lex: Lexicon, target: str, items, corrections):
    """Learner state as a function of the SET of items and corrections (recomputed on current L)."""
    labels = {it[3] for it in items}                                   # L = labels of labelled items received
    exercises = {it[0]: it for it in items}
    parsed = [(c, parse_correction(c[2], exercises[c[1]][3], labels)) for c in corrections if c[1] in exercises]
    contested = {c[1]: s for c, (s, _, _) in parsed if s == "CONTESTE"}
    contesting_label = {}
    for c, (s, _, _) in parsed:
        if s == "CONTESTE":
            toks = tokens(c[2])
            contesting_label.setdefault(c[1], set()).update(l for l in labels if fold(l) in toks and l != exercises[c[1]][3])
    liaison, exclusivity = {}, {}
    for it in items:
        ev = lex.evoked(target, tokens(it[2]))
        if it[0] in contested:                                          # D23: veto only
            for lab in {it[3]} | contesting_label.get(it[0], set()):
                for g in ev:
                    exclusivity.setdefault(g, set()).add(lab)
            continue
        for g in ev:
            liaison.setdefault(g, set()).add(it[3])
            exclusivity.setdefault(g, set()).add(it[3])
    for c, (status, _, glosses) in parsed:
        if status != "OK" or c[1] in contested:                         # F-A: suspended
            continue
        for lab, toks in glosses.items():
            for g in lex.evoked(target, toks):
                liaison.setdefault(g, set()).add(lab)
                exclusivity.setdefault(g, set()).add(lab)
    links = {}
    ambiguous = set()
    for g, labs in liaison.items():
        if len(exclusivity.get(g, set())) >= 2:
            ambiguous.add(g)
        else:
            links[g] = next(iter(labs))
    return links, ambiguous


def voice(lex: Lexicon, target: str, sentence: str, links):
    ev = lex.evoked(target, tokens(sentence))
    total = sum(ev.values())
    linked = {g: w for g, w in ev.items() if g in links}
    if not linked:
        return None, ev
    v = {}
    for g, w in linked.items():
        v[links[g]] = v.get(links[g], 0.0) + w / total
    best = sorted(v.items(), key=lambda kv: -kv[1])
    if len(best) > 1 and best[0][1] == best[1][1]:
        return None, ev                                                # tie -> mute (B2)
    return best[0][0], ev


def loo(lex: Lexicon, target: str, items, corrections):
    rows = []
    for it in items:
        rest = [x for x in items if x[0] != it[0]]
        corr = [c for c in corrections if c[1] != it[0]]               # drops its corrections and the contradiction
        links, ambiguous = build_links(lex, target, rest, corr)
        pred, ev = voice(lex, target, it[2], links)
        ambiguous_forms = sum(1 for t in tokens(it[2]) if len(lex.lemmas.get(t, ())) > 1)
        rows.append({"item": it[0], "label": it[3], "evoked_groups": len(ev), "linked_groups": sum(g in links for g in ev),
                     "ambiguous_groups": sum(g in ambiguous for g in ev), "prediction": pred,
                     "ambiguous_forms_in_item": ambiguous_forms,
                     "outcome": "MUTE" if pred is None else ("TP" if pred == it[3] else "FP")})
    return rows


def summary(rows):
    n = len(rows)
    tp = sum(r["outcome"] == "TP" for r in rows)
    fp = sum(r["outcome"] == "FP" for r in rows)
    mute = sum(r["outcome"] == "MUTE" for r in rows)
    nonmute = tp + fp
    return {"items": n, "non_mute_support": nonmute, "TP": tp, "FP": fp, "FN_mute": mute, "TN": "undefined",
            "precision": round(tp / nonmute, 3) if nonmute else None, "recall": round(tp / n, 3) if n else None,
            "coverage": round(nonmute / n, 3) if n else None}


def main(export_dir: str):
    lex = Lexicon(pathlib.Path(export_dir))
    force_items = list(D.E_LESSONS + D.E_EXERCISES)
    corrections = list(D.C_CORRECTIONS) + [D.CONTRADICTION]
    rows = loo(lex, "force", force_items, corrections)
    s = summary(rows)
    gate = s["non_mute_support"] >= MIN_SUPPORT and (s["precision"] or 0) >= MIN_PRECISION
    by_lemma = {"force": s}
    for word in ("chemin", "corriger"):
        conc = [it for it in D.CONCURRENT_LESSONS if it[1] == word]
        by_lemma[word] = {**summary(loo(lex, word, conc, [])), "groups_in_export": len(lex.groups.get(word, [])),
                          "note": "descriptive only, not part of the gate"}
    out = {"thresholds": {"min_support": MIN_SUPPORT, "min_precision": MIN_PRECISION},
           "gate_population": "18 labelled force teaching items (E_LESSONS + E_EXERCISES)",
           "force_rows": rows, "by_lemma": by_lemma,
           "P_ALIGN": "PASS_FEASIBILITY" if gate else "HOLD",
           "script_sha256": sha(pathlib.Path(__file__))}
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
