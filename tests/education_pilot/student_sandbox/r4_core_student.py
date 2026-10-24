"""R4CoreStudent — isolated experimental student of the Oxygen polysemy pilot (R4-Core).

Contracts: R4.1 (locked design) + R4.2.2 (K1-K10, closure) with P_LEX=HOLD and P_ALIGN=HOLD:
no semantic evidence is taken from the lexicon. The lexical export (optional, read-only, mounted
at /extra) provides only lemmatisation, ambiguity of forms and the MOT_INCONNU check.
Configuration D = export present; configuration B = no export (folded surface forms).

The state is the SET of received events (labelled items, corrections); every derived structure
(statuses, contrasts, suspensions, voices) is recomputed from that set on the current label set,
so the derived state does not depend on the order of arrival. Standard library only; no sense
label, cue word or exam content is encoded. Local experimental memory only.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import unicodedata

from features import FUNCTION_WORDS, extract, stem
from students import HOLD, StateIntegrityError

TAU, DELTA, CONTRAST_MIN = 0.5, 0.15, 0.2
WINDOW = 3
STATE_FILE = "student_state.json"
DEFAULT_LEXICON = pathlib.Path("/extra")
CONSTRUCTION_CLASSES = ("POS", "NG", "DET", "SURF")
NEGATION_MARKERS = (("pas",), ("non",), ("plutot", "que"), ("au", "lieu", "de"))
DEVICE_PAIR = frozenset(("constructions", "exemplaires"))
P5L2_MISSING_CONDITIONS = ("P2_NC_TPC", "CONTRE_PREUVE", "P3_FREQUENCE", "RAPPEL")
PROVENANCE_FIELDS = ("lesson_id", "source_id", "author_id", "derived_from")


def fold(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(c) != "Mn")


def toks(text: str) -> list[str]:
    return re.findall(r"\w+", fold(text))


def jaccard(a, b) -> float:
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 0.0


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class Lexicon:
    """Read-only lemmatiser over the frozen export (Morphalou forms + thes_fr lemma list)."""

    def __init__(self, directory: pathlib.Path):
        morph = directory / "morphalou_fr.jsonl"
        self.sha256 = hashlib.sha256(morph.read_bytes()).hexdigest()
        self.forms: dict[str, object] = {}              # compact: str for one lemma, tuple for several
        with open(morph, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                k, v = fold(r["surface_form"]), fold(r["lemma"])
                old = self.forms.get(k)
                if old is None:
                    self.forms[k] = v
                elif isinstance(old, str):
                    if old != v:
                        self.forms[k] = (old, v)
                elif v not in old:
                    self.forms[k] = old + (v,)
        self.thes_lemmas = set()
        thes = directory / "thes_fr.jsonl"
        if thes.is_file():
            with open(thes, encoding="utf-8") as f:
                for line in f:
                    self.thes_lemmas.add(fold(json.loads(line)["lemma"]))

    def candidates(self, token: str) -> set[str]:
        v = self.forms.get(token)
        return set() if v is None else ({v} if isinstance(v, str) else set(v))

    def known(self, token: str) -> bool:
        return token in self.forms or token in self.thes_lemmas


class R4CoreStudent:
    def __init__(self, state: dict | None = None, lexicon_dir: str | None = None):
        self.state = state or {"revision": 0, "events": [], "resource_sha256": None}
        directory = pathlib.Path(lexicon_dir) if lexicon_dir else DEFAULT_LEXICON
        self.lexicon = Lexicon(directory) if (directory / "morphalou_fr.jsonl").is_file() else None
        current = self.lexicon.sha256 if self.lexicon else None
        if state is not None and state.get("resource_sha256") != current:
            raise StateIntegrityError("lexical resource differs from the one recorded in the state")
        self.state["resource_sha256"] = current
        self._cache = {}

    # --- events -------------------------------------------------------------------------------

    def _add(self, kind: str, payload, provenance=None) -> None:
        self.state["revision"] += 1
        event = {"revision": self.state["revision"], "kind": kind, "payload": payload}
        if provenance:
            event["provenance"] = provenance              # optional key: events without it keep the historical shape
        self.state["events"].append(event)
        self._cache = {}

    def learn(self, items, provenance=None):
        items = [list(i) for i in items]
        self._add("learn", items, self._checked_provenance(provenance, {it[0] for it in items}))

    def apply_correction(self, correction, exercise, provenance=None):
        self._add("correction", {"correction": list(correction), "exercise": list(exercise)},
                  self._checked_provenance(provenance, {correction[0], exercise[0]}))

    @staticmethod
    def _checked_provenance(provenance, ids) -> dict:
        """Optional teaching metadata keyed by item or correction id, validated at the boundary."""
        if provenance is not None and not isinstance(provenance, dict):
            raise ValueError("provenance must be a mapping of observation id to metadata")
        out = {}
        for oid, meta in (provenance or {}).items():
            if oid not in ids or not isinstance(meta, dict) or not set(meta) <= set(PROVENANCE_FIELDS):
                raise ValueError(f"invalid provenance entry for {oid!r}")
            entry = {}
            for k, v in meta.items():
                if v is None:
                    continue
                if k == "derived_from":
                    if not (isinstance(v, (list, tuple)) and v and all(isinstance(x, str) and x for x in v)):
                        raise ValueError(f"invalid derived_from for {oid!r}")
                    entry[k] = sorted(set(v))
                elif isinstance(v, str) and v:
                    entry[k] = v
                else:
                    raise ValueError(f"invalid {k} for {oid!r}")
            if entry:
                out[oid] = entry
        return out

    # --- derived state (function of the event SET up to a revision) -----------------------------

    def _derive(self, as_of=None):
        r = self.state["revision"] if as_of is None else as_of
        if r in self._cache:
            return self._cache[r]
        items, corrections, occurrences = {}, {}, {}

        def delivered(oid, revision):
            occ = occurrences.setdefault(oid, [])
            if revision not in occ:
                occ.append(revision)

        for ev in self.state["events"]:
            if ev["revision"] > r:
                continue
            if ev["kind"] == "learn":
                for it in ev["payload"]:
                    items.setdefault(it[0], {"item": it, "revision": ev["revision"]})
                    delivered(it[0], ev["revision"])
            else:
                c = ev["payload"]["correction"]
                corrections.setdefault(c[0], {"correction": c, "exercise": ev["payload"]["exercise"],
                                              "revision": ev["revision"]})
                ex = ev["payload"]["exercise"]
                items.setdefault(ex[0], {"item": ex, "revision": ev["revision"]})
                delivered(c[0], ev["revision"])
                delivered(ex[0], ev["revision"])
        labels = sorted({v["item"][3] for v in items.values()})
        parsed = {cid: self._parse(v["correction"][2], v["exercise"][3], labels)
                  for cid, v in sorted(corrections.items())}
        contested = {}
        for cid in sorted(parsed):
            if parsed[cid]["status"] == "CONTESTE":
                ex_id = corrections[cid]["exercise"][0]
                contested.setdefault(ex_id, set()).update(parsed[cid]["alternatives"] + [cid])
        contrasts = []
        for cid in sorted(parsed):
            p, ex = parsed[cid], corrections[cid]["exercise"]
            suspended = ex[0] in contested
            p["suspended"] = suspended and p["status"] == "OK"
            if p["status"] == "OK" and not suspended:
                for pos, neg in p["contrasts"]:
                    contrasts.append({"id": cid, "positive": pos, "negative": neg, "exercise": ex})
        derived = {"items": items, "corrections": corrections, "occurrences": occurrences, "parsed": parsed,
                   "labels": labels, "contested": {k: sorted(v) for k, v in contested.items()}, "contrasts": contrasts}
        self._cache[r] = derived
        return derived

    @staticmethod
    def _parse(text: str, ex_label: str, labels: list[str]) -> dict:
        body = re.sub(r"«[^»]*»", " ", text)
        t = toks(body)
        lab = {fold(x): x for x in labels}
        cut = len(t)
        # G1 (K2 R4.2.0): ne...pas and ne...plus -- cut at the "ne", not the marker
        for i, tok in enumerate(t):
            if tok == "ne" and any(x in ("pas", "plus") for x in t[i + 1:i + 5]):
                cut = min(cut, i)
        for i in range(len(t)):
            for m in NEGATION_MARKERS:
                if tuple(t[i:i + len(m)]) == m:
                    cut = min(cut, i)
        pos = sorted({lab[x] for x in t[:cut] if x in lab})
        neg = sorted({lab[x] for x in t[cut:] if x in lab})
        gloss = lambda seg: [x for x in seg if x not in lab]
        out = {"status": "NON_RECONNU", "contrasts": [], "glosses": {}, "alternatives": []}
        if not pos:
            return out
        if len(pos) > 1:
            return {**out, "status": "MALFORME"}
        p = pos[0]
        if p != ex_label:
            if cut < len(t):
                return {**out, "status": "MALFORME"}
            return {**out, "status": "CONTESTE", "alternatives": [p]}
        glosses = {ex_label: gloss(t[:cut])}
        contrasts = []
        for n in neg:
            if n != p:
                contrasts.append((p, n))
                glosses.setdefault(n, []).extend(gloss(t[cut:]))
        return {**out, "status": "OK", "contrasts": contrasts, "glosses": glosses}

    # --- representations ----------------------------------------------------------------------

    def _construction(self, word, sentence):
        return {f for f in extract(word, sentence) if f.split(":", 1)[0] in CONSTRUCTION_CLASSES}

    def _content(self, word, sentence):
        s = stem(word)
        # G2 (K5 / R4.2): content word = not a function word AND length >= 3 (contracted, not a tuning parameter)
        return [x for x in toks(sentence) if x not in FUNCTION_WORDS and len(x) > 2 and not x.startswith(s)]

    def _lemma_set(self, word, sentence):
        out = set()
        for x in self._content(word, sentence):
            out |= (self.lexicon.candidates(x) or {x}) if self.lexicon else {x}
        return out

    def _determinant_unknown(self, word, sentence) -> bool:
        if not self.lexicon:
            return False                                   # condition 4 not applicable in configuration B
        t = toks(sentence)
        s = stem(word)
        idx = next((i for i, x in enumerate(t) if x.startswith(s)), None)
        if idx is None:
            return False
        window = t[max(0, idx - WINDOW): idx + WINDOW + 1]
        return any(not self.lexicon.known(x) for x in window
                   if x not in FUNCTION_WORDS and len(x) > 2 and not x.startswith(s))

    # --- answering ------------------------------------------------------------------------------

    def _active(self, d, word):
        return [v["item"] for k, v in sorted(d["items"].items())
                if v["item"][1] == word and k not in d["contested"]]

    def _evidence(self, word, sentence):
        d = self._derive()
        active = self._active(d, word)
        labels = sorted({it[3] for it in active})
        n = {L: sum(it[3] == L for it in active) for L in labels}
        shrink = lambda L, v: v * n[L] / (n[L] + 2)
        qc, ql = self._construction(word, sentence), self._lemma_set(word, sentence)
        classes = {}
        event_classes = {}
        for name, sim in (("constructions", lambda it: jaccard(qc, self._construction(word, it[2]))),
                          ("exemplaires", lambda it: jaccard(ql, self._lemma_set(word, it[2])))):
            voices, prov, ev_cls = {}, {}, {}
            for L in labels:
                sims = [(sim(it), it[0]) for it in active if it[3] == L]
                best = max(v for v, _ in sims)
                tied = {i for v, i in sims if v == best}          # every ex aequo item, never an id-order pick
                voices[L], prov[L] = shrink(L, best), tied
                ev_cls[L] = frozenset(self._source_event(d, i) for i in tied)
            classes[name] = (voices, prov)
            event_classes[name] = ev_cls
        voices, prov = {L: 0.0 for L in labels}, {L: set() for L in labels}
        for c in d["contrasts"]:
            if c["exercise"][1] != word or c["positive"] not in voices:
                continue
            s = jaccard(qc, self._construction(word, c["exercise"][2]))
            if s >= CONTRAST_MIN and shrink(c["positive"], s) > voices[c["positive"]]:
                voices[c["positive"]] = shrink(c["positive"], s)
                prov[c["positive"]] = {c["id"], c["exercise"][0]}
        classes["contrastes"] = (voices, prov)
        filtered = {k: v for k, v in classes.items() if any(x > 0 for x in v[0].values())}
        return filtered, labels, active, event_classes

    @staticmethod
    def _concordant(classes):
        out = {}
        for name, (voices, prov) in classes.items():
            ranked = sorted(voices.items(), key=lambda kv: -kv[1])
            if ranked and ranked[0][1] >= TAU and (len(ranked) == 1 or ranked[0][1] > ranked[1][1]):
                out.setdefault(ranked[0][0], []).append((name, prov[ranked[0][0]]))
        return out

    @staticmethod
    def _source_event(d: dict, item_id: str):
        entry = d["items"].get(item_id)
        return entry["revision"] if entry else None

    @staticmethod
    def _independent_pair(entries, event_of: dict | None = None, dependent=frozenset()) -> bool:
        for i, (na, pa) in enumerate(entries):
            for nb, pb in entries[i + 1:]:
                if pa & pb or frozenset((na, nb)) in dependent:
                    continue
                if event_of is not None:
                    ea = event_of.get(na, frozenset())
                    eb = event_of.get(nb, frozenset())
                    if ea & eb:
                        continue
                return True
        return False

    def _provenance_record(self, d, oid) -> dict:
        """Teaching provenance of an observation as attested at its first occurrence; unknown fields stay None."""
        if oid in d["items"]:
            revision, item_id, derived_from = d["items"][oid]["revision"], oid, None
        else:
            c = d["corrections"][oid]
            revision, item_id, derived_from = c["revision"], c["exercise"][0], [c["exercise"][0]]
        event = next(ev for ev in self.state["events"] if ev["revision"] == revision)
        meta = event.get("provenance", {}).get(oid, {})
        if "derived_from" in meta:
            derived_from = sorted(set(derived_from or ()) | set(meta["derived_from"]))
        return {"observation_id": oid, "item_id": item_id, "teaching_event_id": revision,
                "teaching_event_kind": event["kind"], "occurrences": list(d["occurrences"][oid]),
                "lesson_id": meta.get("lesson_id"), "source_id": meta.get("source_id"),
                "author_id": meta.get("author_id"), "derived_from": derived_from}

    def _observation_provenance(self, d, oid) -> dict:
        """Compact V1.2 view of the provenance record (stable keys)."""
        r = self._provenance_record(d, oid)
        return {k: r[k] for k in ("observation_id", "teaching_event_id", "teaching_event_kind",
                                  "lesson_id", "source_id", "derived_from")}

    def _lineage(self, d, ids) -> set:
        """The observations plus every ancestor declared through derived_from."""
        seen, todo = set(), list(ids)
        while todo:
            i = todo.pop()
            if i not in seen:
                seen.add(i)
                if i in d["items"] or i in d["corrections"]:
                    todo.extend(self._provenance_record(d, i)["derived_from"] or ())
        return seen

    def _pair_relation(self, d, a, b) -> str:
        """Pedagogical dependency of two evidence sets; distinct source ids never establish independence."""
        la, lb = self._lineage(d, a), self._lineage(d, b)
        records = lambda ids: [self._provenance_record(d, i) for i in sorted(ids) if i in d["items"] or i in d["corrections"]]
        ra, rb = records(la), records(lb)
        lessons = lambda rs: {r["lesson_id"] for r in rs} - {None}
        # a shared delivery is a dependency unless both observations attest distinct lessons
        same_delivery = any(x["teaching_event_id"] == y["teaching_event_id"]
                            and not (x["lesson_id"] and y["lesson_id"] and x["lesson_id"] != y["lesson_id"])
                            for x in ra for y in rb)
        if la & lb or lessons(ra) & lessons(rb) or same_delivery:
            return "SAME_EVENT"
        if any(r["teaching_event_kind"] != "learn" and r["derived_from"] is None for r in ra + rb):
            return "UNKNOWN_DEPENDENCY"          # an exercise received with a correction, origin lesson undeclared
        # VERIFIED_INDEPENDENT_SOURCES would need an independence attestation that the contract does not define
        return "DISTINCT_PEDAGOGICAL_EVENTS"

    @staticmethod
    def _device_pair_is_independent(relation: str) -> bool:
        # active safety policy; accepting DISTINCT_PEDAGOGICAL_EVENTS (K3-compatible legacy reading) is on HOLD
        return relation == "VERIFIED_INDEPENDENT_SOURCES"

    def _device_dependency(self, d, L, pc, pe, event_classes) -> list[str]:
        """Why the constructions/exemplaires pair cannot count as independent (STOP_CORROBORATION, fail-closed)."""
        items = d["items"]
        kinds = {ev["revision"]: ev["kind"] for ev in self.state["events"]}
        meta = lambda ids, k: {items[i]["item"][k] if len(items[i]["item"]) > k else None for i in ids}
        causes = []
        if pc & pe:
            causes.append("ITEM_COMMUN")
        if event_classes["constructions"][L] & event_classes["exemplaires"][L]:
            causes.append("EVENEMENT_COMMUN")
        for k, cause in ((4, "MEME_DOMAINE"), (5, "MEME_REGISTRE")):
            a, b = meta(pc, k), meta(pe, k)
            if a & b or None in a | b:                      # unknown metadata counts as shared
                causes.append(cause)
        if any(kinds[items[i]["revision"]] != "learn" for i in pc | pe):
            causes.append("OBSERVATION_DERIVEE")
        attested = lambda ids, k: {self._provenance_record(d, i)[k] for i in ids}
        for k, cause in (("lesson_id", "MEME_LECON"), ("source_id", "MEME_SOURCE"), ("author_id", "MEME_AUTEUR")):
            if (attested(pc, k) & attested(pe, k)) - {None}:
                causes.append(cause)
        if None in attested(pc | pe, "source_id") | attested(pc | pe, "author_id"):
            causes.append("SOURCE_AUTEUR_INCONNUS")         # source or author not attested for every observation
        return causes

    def _p5l2_status(self, word, sentence) -> dict:
        """Provisional P5-L2 view (hypothesis, candidate, admissibility). Informational: never authorises an answer."""
        d = self._derive()
        classes, _, _, event_classes = self._evidence(word, sentence)
        out = {"hypothesis": None, "candidate": False, "argmax": {}, "dependency": [], "evidence_status": None,
               "shared_cue_tokens": [], "missing_conditions": list(P5L2_MISSING_CONDITIONS), "admissible": False,
               "response_authority": False}
        for L, entries in self._concordant(classes).items():
            prov = dict(entries)
            if not DEVICE_PAIR <= prov.keys():
                continue
            pc, pe = prov["constructions"], prov["exemplaires"]
            dep = self._device_dependency(d, L, pc, pe, event_classes)
            qc, ql = self._construction(word, sentence), self._lemma_set(word, sentence)
            c_tok = {t for i in pc for f in qc & self._construction(word, d["items"][i]["item"][2])
                     for t in re.split(r"[:=_]", f)}
            e_tok = {t for i in pe for t in ql & self._lemma_set(word, d["items"][i]["item"][2])}
            relation = self._pair_relation(d, pc, pe)
            out.update(hypothesis=L, argmax={"constructions": sorted(pc), "exemplaires": sorted(pe)}, dependency=dep,
                       candidate=relation in ("DISTINCT_PEDAGOGICAL_EVENTS", "VERIFIED_INDEPENDENT_SOURCES"),
                       evidence_status=relation, shared_cue_tokens=sorted(c_tok & e_tok))
            out["admissible"] = out["candidate"] and not dep and not out["missing_conditions"]
        return out

    def answer(self, word, sentence):
        hold = lambda reason: {"sense": HOLD, "provenance": [], "reason": reason, "origin": "INCERTAIN",
                               "corpus_hypotheses": []}
        d = self._derive()
        if not any(v["item"][1] == word for v in d["items"].values()):
            return hold("MOT_INCONNU")
        if self._determinant_unknown(word, sentence):
            return hold("MOT_INCONNU")
        classes, labels, active, event_classes = self._evidence(word, sentence)
        if not classes:
            return hold("PREUVE_INSUFFISANTE")
        score = {L: sum(c[0][L] for c in classes.values()) / len(classes) for L in labels}
        ranked = sorted(score.items(), key=lambda kv: (-kv[1], kv[0]))
        top, s1 = ranked[0]
        s2 = ranked[1][1] if len(ranked) > 1 else 0.0
        conc = self._concordant(classes)
        event_of_conc = {L: {n: event_classes.get(n, {}).get(L, frozenset()) for n, _ in e}
                         for L, e in conc.items()}
        indep = {}
        for L, e in conc.items():
            prov = dict(e)
            dependent = ({DEVICE_PAIR} if DEVICE_PAIR <= prov.keys() and not self._device_pair_is_independent(
                self._pair_relation(d, prov["constructions"], prov["exemplaires"])) else frozenset())
            if self._independent_pair(e, event_of_conc[L], dependent):
                indep[L] = e
        prov_of = {L: set().union(*[p for _, p in e]) for L, e in conc.items()}
        rivals = sorted(prov_of)
        disjoint_rivals = any(not (prov_of[a] & prov_of[b]) for i, a in enumerate(rivals) for b in rivals[i + 1:])
        if disjoint_rivals or (s1 >= TAU and s2 >= TAU and s1 - s2 < DELTA):
            return hold("CONFLIT")                                # K9 precedence 2
        if top not in indep or s1 < TAU or s1 - s2 < DELTA:
            return hold("PREUVE_INSUFFISANTE")
        provenance = sorted(set().union(*[p for _, p in indep[top]]))
        taught = set().union(*[set(self._lemma_set(word, it[2])) for it in active if it[3] == top])
        if not (set(self._lemma_set(word, sentence)) & taught):
            origin = "TRANSFERE"
        elif any(name == "contrastes" for name, _ in indep[top]):
            origin = "CORRIGE"
        else:
            origin = "ACQUIS_LECON"
        return {"sense": top, "provenance": provenance, "reason": None, "origin": origin, "corpus_hypotheses": []}

    # --- memory interface ------------------------------------------------------------------------

    @staticmethod
    def _eff_status(parsed: dict) -> str:
        """G3 (F-A §2): effective correction status, exposing SUSPENDU.""";
        s = parsed["status"]
        return "SUSPENDU" if s == "OK" and parsed.get("suspended", False) else s

    def _hits(self, d, word):
        hits = []
        for k, v in sorted(d["items"].items()):
            it = v["item"]
            if it[1] != word:
                continue
            ok = sorted(cid for cid, c in d["corrections"].items()
                        if c["exercise"][0] == k and d["parsed"][cid]["status"] == "OK" and not d["parsed"][cid]["suspended"])
            hits.append({"id": k, "sense": it[3], "domain": it[4], "provenance": ok + [k],
                         "status": "CONTESTE" if k in d["contested"] else "ACTIF",
                         "corrections": [{"id": cid, "status": R4CoreStudent._eff_status(d["parsed"][cid])}
                                          for cid in sorted(cid for cid, c in d["corrections"].items() if c["exercise"][0] == k)],
                         "revision": v["revision"], "content": it[2]})
        return hits

    def retrieve(self, word=None, sense=None, domain=None, provenance=None, context=None, as_of_revision=None):
        d = self._derive(as_of_revision)
        hits = [h for h in self._hits(d, word) if (sense is None or h["sense"] == sense)
                and (domain is None or h["domain"] == domain) and (provenance is None or provenance in h["provenance"])]
        if context is not None:
            qc, ql = self._construction(word, context), self._lemma_set(word, context)
            key = lambda h: -(jaccard(qc, self._construction(word, h["content"])) + jaccard(ql, self._lemma_set(word, h["content"]))) / 2
            hits.sort(key=lambda h: (key(h), h["id"]))
        return [{k: v for k, v in h.items() if k != "domain"} for h in hits]

    def history(self, word, sense):
        out, previous = [], None
        for ev in self.state["events"]:
            content = self.retrieve(word=word, sense=sense, as_of_revision=ev["revision"])
            if content != previous:
                out.append({"revision": ev["revision"], "op": ev["kind"], "content": content})
                previous = content
        return out

    def derived_snapshot(self, word):
        """Order-independent view used by the order tests (no revision numbers)."""
        d = self._derive()
        return {"statuses": {cid: (p["status"], p.get("suspended", False)) for cid, p in sorted(d["parsed"].items())},
                "contested": d["contested"], "contrasts": sorted((c["id"], c["positive"], c["negative"]) for c in d["contrasts"]),
                "hits": [{k: v for k, v in h.items() if k != "revision"} for h in self._hits(d, word)]}

    def reinterpretation_journal(self):
        """G4 (NB-F R4.2.2): append-only log of correction status changes across revisions."""
        journal, prev = [], {}
        for ev in self.state["events"]:
            r = ev["revision"]
            d = self._derive(r)
            curr = {cid: self._eff_status(p) for cid, p in d["parsed"].items()}
            changes, suspended, reactivated = [], [], []
            for cid in sorted(curr):
                old_s, new_s = prev.get(cid), curr[cid]
                if old_s != new_s:
                    changes.append({"correction": cid, "previous_status": old_s, "new_status": new_s})
                    if new_s == "SUSPENDU":
                        suspended.append(cid)
                    elif old_s == "SUSPENDU":
                        reactivated.append(cid)
            if changes:
                journal.append({"revision": r, "event": ev["kind"],
                                 "changes": changes, "suspended": suspended, "reactivated": reactivated})
            prev = curr
        return journal

    # --- persistence -----------------------------------------------------------------------------

    def save(self, directory):
        payload = {"sha256": hashlib.sha256(canonical(self.state)).hexdigest(), "state": self.state}
        (pathlib.Path(directory) / STATE_FILE).write_bytes(canonical(payload))

    @classmethod
    def load(cls, directory, lexicon_dir: str | None = None):
        raw = (pathlib.Path(directory) / STATE_FILE).read_bytes()
        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise StateIntegrityError(f"unreadable state: {type(exc).__name__}") from exc
        if not isinstance(payload, dict) or set(payload) != {"sha256", "state"} or raw != canonical(payload):
            raise StateIntegrityError("state file is not canonical")
        if payload["sha256"] != hashlib.sha256(canonical(payload["state"])).hexdigest():
            raise StateIntegrityError("state hash mismatch")
        return cls(payload["state"], lexicon_dir)
