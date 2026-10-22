"""Independent re-implementation of rule C (R4.3.1). Reviewer script, read-only on repo."""
import sys, pathlib, hashlib, json
REPO = pathlib.Path(r"C:\Users\User\Desktop\obsidia-claude-linguistique")
sys.path[:0] = [str(REPO / "tests/education_pilot/student_sandbox"), str(REPO)]
from r4_core_student import R4CoreStudent, jaccard, fold, toks
LEX = r"C:\Users\User\Documents\OBSIDIA_HANDOFF\oxygen_r4_lexicon_export\v1"
S_MIN, DELTA, TAU, TAU1, REL = 0.2, 0.15, 0.5, 0.75, 0.5
_LEXOBJ = None

def new_student():
    global _LEXOBJ
    st = R4CoreStudent(lexicon_dir=LEX) if _LEXOBJ is None else None
    if _LEXOBJ is None:
        _LEXOBJ = st.lexicon
    else:
        st = R4CoreStudent.__new__(R4CoreStudent)
        st.state = {"revision": 0, "events": [], "resource_sha256": _LEXOBJ.sha256}
        st.lexicon = _LEXOBJ; st._cache = {}
    return st

def rel_filter(st, word, exemplars):
    feats = [st._construction(word, it[2]) for it in exemplars]
    if not feats: return set()
    from collections import Counter
    c = Counter(f for fs in feats for f in fs)
    return {f for f, k in c.items() if k / len(feats) >= REL}

def class_vote(st, word, sentence, exemplars):
    """returns {class: (label|None, prov|None, detail)}"""
    drop = rel_filter(st, word, exemplars)
    qc = st._construction(word, sentence) - drop
    ql = st._lemma_set(word, sentence)
    out = {}
    for name, rep in (("constructions", lambda s: st._construction(word, s) - drop),
                      ("lemmes", lambda s: st._lemma_set(word, s))):
        q = qc if name == "constructions" else ql
        best = {}
        for it in exemplars:
            s = jaccard(q, rep(it[2]))
            L = it[3]
            if L not in best or s > best[L][0] or (s == best[L][0] and it[0] < best[L][1]):
                best[L] = (s, it[0])
        ranked = sorted(best.items(), key=lambda kv: -kv[1][0])
        if not ranked or ranked[0][1][0] < S_MIN:
            out[name] = (None, None, "below_smin"); continue
        s1 = ranked[0][1][0]; s2 = ranked[1][1][0] if len(ranked) > 1 else 0.0
        if s1 == s2:
            out[name] = (None, None, "tie"); continue
        if s1 - s2 < DELTA:
            out[name] = (None, None, f"margin {s1-s2:.3f}"); continue
        out[name] = (ranked[0][0], {ranked[0][1][1]}, f"s1={s1:.3f} s2={s2:.3f}")
    return out

def reliability(st, word, active):
    N = {"constructions": 0, "lemmes": 0}; TP = dict(N)
    for j in active:
        rest = [it for it in active if it[0] != j[0]]
        v = class_vote(st, word, j[2], rest)
        for c, (L, _, _) in v.items():
            if L is not None:
                N[c] += 1; TP[c] += (L == j[3])
    return {c: (TP[c] + 1) / (N[c] + 2) for c in N}, N, TP

def contrast_vote(st, word, sentence, d, exemplars):
    drop = rel_filter(st, word, exemplars)
    qc = st._construction(word, sentence) - drop
    best = None
    for c in d["contrasts"]:
        if c["exercise"][1] != word: continue
        s = jaccard(qc, st._construction(word, c["exercise"][2]) - drop)
        if s >= S_MIN and (best is None or s > best[0]):
            best = (s, c["positive"])
    return best

def answer(st, word, sentence):
    d = st._derive()
    if not any(v["item"][1] == word for v in d["items"].values()):
        return ("HOLD", "MOT_INCONNU", None)
    for k, v in d["items"].items():   # RAPPEL (exact folded fingerprint)
        if v["item"][1] == word and fold(v["item"][2]).strip() == fold(sentence).strip():
            if k in d["contested"]:
                return ("HOLD", "CONTESTE", None)
            return (v["item"][3], "RAPPEL", None)
    if st._determinant_unknown(word, sentence):
        return ("HOLD", "MOT_INCONNU", None)
    active = st._active(d, word)
    votes = class_vote(st, word, sentence, active)
    r, N, TP = reliability(st, word, active)
    info = {"votes": votes, "r": r, "N": N, "TP": TP}
    cv = contrast_vote(st, word, sentence, d, active)
    info["contrast"] = cv
    voiced = {c: v for c, v in votes.items() if v[0] is not None}
    labs = {v[0] for v in voiced.values()}
    if len(labs) > 1: return ("HOLD", "CONFLIT", info)
    if not labs: return ("HOLD", "PREUVE_INSUFFISANTE", info)
    L = labs.pop()
    if cv and cv[1] != L: return ("HOLD", "CONFLIT", info)
    if len(voiced) == 2:
        a, b = voiced.values()
        p = 1 - (1 - r["constructions"]) * (1 - r["lemmes"])
        if not (a[1] & b[1]) and p >= TAU: return (L, "ACQUIS(a)", info)
        return ("HOLD", "PREUVE_INSUFFISANTE", info)
    (c, v), = voiced.items()
    if r[c] >= TAU1: return (L, f"ACQUIS(b:{c})", info)
    return ("HOLD", "PREUVE_INSUFFISANTE", info)
