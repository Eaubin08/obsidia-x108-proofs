"""P-LEX measurement, design R3 formula, teaching data only. Read-only corpus access."""
import json, math, sqlite3, sys, itertools, collections
sys.stdout.reconfigure(encoding="utf-8")
from tests.education_pilot import _pilot_data as D
from tests.education_pilot._bench import content_words
DB = "file:data/linguistic_corpus/lexicon.db?mode=ro&immutable=1"
c = sqlite3.connect(DB, uri=True)
# neighbourhoods V(l) over ALL thes_fr fr entries (= future export rule)
V = collections.defaultdict(set)
for lemma, syn in c.execute("select lemma, synonyms from senses where source_id='thes_fr' and lang='fr'"):
    V[lemma].add(lemma)
    try: V[lemma].update(json.loads(syn or "[]"))
    except Exception: pass
N = len(V)
df = collections.Counter(p for s in V.values() for p in s)
idf = lambda p: math.log(N / df[p]) if df[p] else 0.0
def lemmas(form):
    rows = c.execute("select distinct lemma from inflections where lang='fr' and surface_form=?", (form,)).fetchall()
    return sorted({r[0] for r in rows})
def lemma_of(form):
    ls = [l for l in lemmas(form) if l in V]
    if form in V: return form          # form itself is a thes_fr lemma
    return ls[0] if len(ls) == 1 else (None if not ls else "AMBIG:" + "|".join(ls))
def prox(a, b):
    A, B = V[a], V[b]
    num = sum(idf(p) for p in A & B)
    den = math.sqrt(sum(idf(p) for p in A) * sum(idf(p) for p in B))
    return num / den if den else 0.0
items = D.E_LESSONS + D.E_EXERCISES
occ = []
for it in items:
    for w in sorted(content_words(it[2], it[1])):
        occ.append((it[0], it[3], w, lemma_of(w)))
tp = fp = fn = tn = 0; undec = 0; ambig = 0; same_lemma = collections.Counter()
for (i1, l1, w1, m1), (i2, l2, w2, m2) in itertools.combinations(occ, 2):
    if i1 == i2: continue
    if m1 is None or m2 is None: undec += 1; continue
    if m1.startswith("AMBIG") or m2.startswith("AMBIG"): ambig += 1; continue
    kept = prox(m1, m2) >= 0.2
    same = l1 == l2
    if m1 == m2: same_lemma[(kept, same)] += 1
    if kept and same: tp += 1
    elif kept: fp += 1
    elif same: fn += 1
    else: tn += 1
ret = tp + fp
prec = tp / ret if ret else float("nan")
rate_same = tp / (tp + fn) if tp + fn else 0; rate_diff = fp / (fp + tn) if fp + tn else 0
ratio = rate_same / rate_diff if rate_diff else float("inf")
print(json.dumps(dict(N=N, occurrences=len(occ), TP=tp, FP=fp, FN=fn, TN=tn, retained=ret, undecidable_no_lemma=undec,
      ambiguous_lemma=ambig, precision=round(prec, 3), recall=round(rate_same, 3), rate_diff=round(rate_diff, 4),
      discrimination_ratio=round(ratio, 2) if ratio != float("inf") else "inf",
      same_lemma_pairs={f"kept={k}/same_label={s}": v for (k, s), v in same_lemma.items()},
      PLEX_PASS=bool(ret >= 10 and prec >= 0.5 and (ratio >= 3 or (rate_diff == 0 and tp >= 10))))))
