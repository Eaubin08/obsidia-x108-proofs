"""Independent implementation of rule C (R4.3.2) over R4-Core primitives. Read-only."""
import sys, pathlib
REPO = pathlib.Path(r"C:\Users\User\Desktop\obsidia-claude-linguistique")
sys.path[:0] = [str(REPO / "tests/education_pilot/student_sandbox"), str(REPO / "tests/education_pilot")]
from r4_core_student import R4CoreStudent, jaccard, fold, toks
LEX = r"C:\Users\User\Documents\OBSIDIA_HANDOFF\oxygen_r4_lexicon_export\v1"
TAU, DELTA, SMIN, TAU1 = 0.5, 0.15, 0.2, 0.75
CLASSES = ("constructions", "lemmes")


class Engine:
    def __init__(self, lex=True):
        self.st = R4CoreStudent(lexicon_dir=LEX if lex else r"C:\nonexistent_dir")
        self._fc, self._lc = {}, {}

    def load(self, items, corrections):
        st = self.st
        st.state = {"revision": 0, "events": [], "resource_sha256": st.state["resource_sha256"]}
        st._cache = {}
        if items:
            st.learn(items)
        for c, ex in corrections:
            st.apply_correction(c, ex)
        self.d = st._derive()

    def cons(self, w, s):
        k = (w, s)
        if k not in self._fc:
            self._fc[k] = frozenset(self.st._construction(w, s))
        return self._fc[k]

    def lem(self, w, s):
        k = (w, s)
        if k not in self._lc:
            self._lc[k] = frozenset(self.st._lemma_set(w, s))
        return self._lc[k]

    def active(self, w):
        return self.st._active(self.d, w)

    def feats(self, cls, w, s):
        return self.cons(w, s) if cls == "constructions" else self.lem(w, s)

    # C1: construction trait non-informative iff present in >=1 exemplar of EACH label (on given exemplars)
    def noninfo(self, cls, w, ex):
        if cls != "constructions":
            return frozenset()
        labels = sorted({it[3] for it in ex})
        if not labels:
            return frozenset()
        sets = [frozenset().union(*[self.feats(cls, w, it[2]) for it in ex if it[3] == L]) for L in labels]
        return frozenset.intersection(*sets)

    def classify(self, cls, w, s, ex):
        """-> (label, prov_id) or None (mute)."""
        if not ex:
            return None
        ni = self.noninfo(cls, w, ex)
        q = self.feats(cls, w, s) - ni
        best = {}
        for it in ex:
            v = jaccard(q, self.feats(cls, w, it[2]) - ni)
            L = it[3]
            if L not in best or v > best[L][0] or (v == best[L][0] and it[0] < best[L][1]):
                best[L] = (v, it[0])
        ranked = sorted(best.items(), key=lambda kv: -kv[1][0])
        top, (s1, pid) = ranked[0]
        if s1 < SMIN:
            return None
        if len(ranked) > 1:
            s2 = ranked[1][1][0]
            if s2 == s1 or s1 - s2 < DELTA - 1e-12:
                return None
        return top, pid

    def reliability(self, cls, w, ex):
        N = TP = 0
        for j, it in enumerate(ex):
            r = self.classify(cls, w, it[2], ex[:j] + ex[j + 1:])
            if r is not None:
                N += 1
                TP += (r[0] == it[3])
        return (TP + 1) / (N + 2), TP, N

    def exclusive(self, cls, w, ex):
        out = {}
        for L in sorted({it[3] for it in ex}):
            mine = frozenset().union(*[self.feats(cls, w, it[2]) for it in ex if it[3] == L])
            others = frozenset().union(*[self.feats(cls, w, it[2]) for it in ex if it[3] != L])
            out[L] = mine - others
        return out

    def answer(self, w, s):
        d = self.d
        allitems = [v["item"] for v in d["items"].values() if v["item"][1] == w]
        if not allitems:
            return ("HOLD", "MOT_INCONNU", {})
        fs = " ".join(toks(s))
        for it in allitems:
            if " ".join(toks(it[2])) == fs:
                if it[0] in d["contested"]:
                    return ("HOLD", "RAPPEL_CONTESTE", {})
                return (it[3], "RAPPEL", {})
        if self.st._determinant_unknown(w, s):
            return ("HOLD", "MOT_INCONNU", {})
        ex = self.active(w)
        info, votes = {}, {}
        for cls in CLASSES:
            c = self.classify(cls, w, s, ex)
            r = self.reliability(cls, w, ex)
            info[cls] = (c, r)
            if c:
                votes[cls] = (c[0], c[1], r[0])
        labs = {v[0] for v in votes.values()}
        if len(labs) > 1:
            return ("HOLD", "CONFLIT", info)
        if not labs:
            return ("HOLD", "PREUVE_INSUFFISANTE", info)
        L = labs.pop()
        for cls in CLASSES:  # C2
            q = self.feats(cls, w, s)
            for L2, exc in self.exclusive(cls, w, ex).items():
                if L2 != L and q & exc:
                    info["C2"] = (cls, L2, sorted(q & exc)[:4])
                    return ("HOLD", "CONFLIT", info)
        qc, ni = self.cons(w, s), self.noninfo("constructions", w, ex)  # C4
        bestc = None
        for c in d["contrasts"]:
            if c["exercise"][1] != w:
                continue
            v = jaccard(qc - ni, self.cons(w, c["exercise"][2]) - ni)
            if v >= SMIN and (bestc is None or v > bestc[0]):
                bestc = (v, c["positive"])
        if bestc and bestc[1] != L:
            info["C4"] = bestc
            return ("HOLD", "CONFLIT", info)
        vs = list(votes.values())
        if len(vs) == 2:
            if vs[0][1] != vs[1][1]:
                p = 1 - (1 - vs[0][2]) * (1 - vs[1][2])
                return (L, "voie_a", info) if p >= TAU else ("HOLD", "PREUVE_INSUFFISANTE", info)
            r = max(vs[0][2], vs[1][2])
            return (L, "voie_b_C3", info) if r >= TAU1 else ("HOLD", "PREUVE_INSUFFISANTE", info)
        return (L, "voie_b", info) if vs[0][2] >= TAU1 else ("HOLD", "PREUVE_INSUFFISANTE", info)
