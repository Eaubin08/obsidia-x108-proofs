"""Built-in deterministic grammar: raw utterance -> UtteranceFrame.

Pipeline (each step is scope-aware, none is a phrase dictionary):
  1. tokenize with character spans aligned on the RAW input;
  2. remove disfluencies / discourse markers (recorded, never lost);
  3. segment into clauses at punctuation and connectives (the clause is the
     scope boundary of negation, modality and pragmatic force);
  4. build predicate units from verb chains (aux + participle, modal +
     infinitive, aspectual periphrases);
  5. assign polarity (ne ... negator, oral negation, sans, EN not),
     restriction (ne ... que), ne explétif, modality, tense/aspect;
  6. assign pragmatic / epistemic status from clause role;
  7. resolve intra-utterance references, relate clauses, derive
     constraints, contradictions and evidence needs.

French coverage follows docs/semantic/FRENCH_LINGUISTIC_BASIS_V0.md; English
coverage is deliberately minimal. Deterministic, stdlib-only, no network,
no model. Describes; never decides.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, replace

from app.semantic.lattice.lexicon import fold, lookup, predicate_of
from app.semantic.lattice.primitives import (
    Argument, LatticeRelation, PredicateUnit, RelationKind, UtteranceFrame,
)

# ── closed word classes ──────────────────────────────────────────────────
_SUBJECT_PRONOUNS = {
    "je", "j'", "tu", "il", "elle", "on", "nous", "vous", "ils", "elles",
    "i", "you", "he", "she", "we", "they",
}
_SECOND_PERSON = {"tu", "vous", "you"}
_FIRST_PERSON = {"je", "j'", "nous", "i", "we"}
_OBJECT_CLITICS = {"le", "la", "les", "l'", "lui", "leur", "en", "y"}
_REFLEXIVE_CLITICS = {"me", "m'", "te", "t'", "se", "s'"}
_DETERMINERS = {
    "le", "la", "les", "l'", "un", "une", "des", "du", "de", "d'", "au", "aux",
    "ce", "cet", "cette", "ces", "mon", "ma", "mes", "ton", "ta", "tes",
    "son", "sa", "ses", "notre", "votre", "nos", "vos", "leur", "leurs",
    "aucun", "aucune", "the", "an", "this", "these", "those", "that", "my",
    "your", "some", "any",
}
_DEFINITE = {"le", "la", "les", "l'", "the", "au", "aux", "du"}
_DEMONSTRATIVE_DET = {"ce", "cet", "cette", "ces", "this", "these", "those", "that"}
_PRONOUN_OBJECTS_EN = {"it", "them"}
_DEMONSTRATIVE_PRONOUNS = {"ça", "ca", "cela", "ceci", "celui", "celle", "ceux", "celles"}
_FR_NEGATORS = {"pas", "plus", "jamais", "rien", "personne", "aucun", "aucune",
                "nul", "nulle", "guère", "guere", "point", "ni"}
_ORAL_NEGATORS = {"pas", "jamais", "rien"}
_EN_NEGATORS = {"not", "never", "don't", "doesn't", "didn't", "cannot", "can't",
                "won't", "shouldn't", "mustn't"}
_RESTRICTION_ADVERBS = {"only", "seulement", "uniquement"}
_ADVERBS_SKIPPABLE = {"pas", "jamais", "plus", "rien", "déjà", "deja", "bien",
                      "surtout", "vraiment", "encore", "toujours", "not", "never",
                      "please", "stp", "svp"}
_PREPOSITIONS = {"sur", "dans", "avec", "pour", "à", "a", "en", "par", "vers",
                 "chez", "on", "in", "with", "to", "for", "into", "at", "of",
                 "from"}
_DEIXIS = {"ici", "là", "maintenant", "aujourd'hui", "demain", "hier",
           "here", "now", "today", "tomorrow", "yesterday"}
_TIME_ADVERBS = _DEIXIS | {"dehors", "ensuite", "après", "apres", "avant", "tard", "tôt"}
# Manner adverbs that must never be read as a bare (determiner-less) object.
_MANNER_ADVERBS = {"tout", "seul", "seule", "seuls", "vite", "ensemble", "automatiquement",
                   "directement", "immédiatement", "immediatement", "maintenant"}
_INTERJECTIONS = {"please", "stp", "svp", "merci", "ok", "okay", "bon", "bonjour",
                  "salut", "hey", "hello", "hi", "oui", "non", "yes", "no"}
_WH_WORDS = {"comment", "pourquoi", "quand", "où", "quoi", "combien", "how", "what",
             "why", "when", "where", "whether", "which"}
_DISFLUENCIES = {"euh", "heu", "bah", "ben", "hum", "hmm", "uh", "um", "erm"}
_NO_COLLAPSE = {"nous", "vous"}
_ELIDED_LETTERS = {"l", "j", "n", "m", "t", "s", "d", "c", "qu"}

# Connectives -> normalized connective names.
_CONNECTIVES = {
    "mais": "mais", "but": "mais",
    "puis": "puis", "ensuite": "puis", "then": "puis",
    "et": "et", "and": "et",
    "ou": "ou", "or": "ou", "sinon": "ou",
    "donc": "donc", "so": "donc",
    "car": "car", "because": "car", "puisque": "car",
    "alors": "alors",
    "si": "si", "if": "si",
    "without": "sans",
    "before": "avant_de", "after": "apres",
}
_CLAUSE_PUNCT = {",", ";", ".", "!", "?", ":"}

_TOKEN_RE = re.compile(r"[^\W\d_]+n't|[^\W_]+'|[^\W_]+|[?!.,;:]", re.UNICODE)


@dataclass
class _Tok:
    low: str
    start: int
    end: int
    hyphen_before: bool = False
    analyses: list = field(default_factory=list)
    accentless_ambiguous: bool = False

    @property
    def is_punct(self) -> bool:
        return self.low in _CLAUSE_PUNCT


@dataclass
class _Clause:
    toks: list
    conn: str | None = None
    conn_toks: list = field(default_factory=list)
    restriction: str | None = None      # ONLY | NOT_ONLY
    restriction_at: int | None = None   # index of "que" in toks
    embedding_parent: int | None = None  # clause index hosting the embedding verb
    units: list = field(default_factory=list)


# ── 1-2. tokenization ────────────────────────────────────────────────────
def _lower_aligned(raw: str) -> str:
    out = []
    for ch in raw:
        if ch in "’‘ʼ`´":
            out.append("'")
            continue
        low = ch.lower()
        out.append(low if len(low) == 1 else ch)
    return "".join(out)


def _tokenize(raw: str) -> tuple[list[_Tok], list[str], list[str]]:
    text = _lower_aligned(raw)
    toks: list[_Tok] = []
    for m in _TOKEN_RE.finditer(text):
        hyphen = m.start() > 0 and text[m.start() - 1] == "-"
        toks.append(_Tok(m.group(), m.start(), m.end(), hyphen))

    ortho: list[str] = []
    merged: list[_Tok] = []
    for i, t in enumerate(toks):
        nxt = toks[i + 1] if i + 1 < len(toks) else None
        if t.low == "aujourd'" and nxt is not None and nxt.low == "hui":
            continue
        if t.low == "hui" and merged and merged[-1].low == "aujourd'":
            merged[-1] = _Tok("aujourd'hui", merged[-1].start, t.end)
            continue
        if (t.low in _ELIDED_LETTERS and nxt is not None and not nxt.is_punct
                and t.low != "a"):
            ortho.append(f"missing_apostrophe:{t.low}")
            t = _Tok(t.low + "'", t.start, t.end, t.hyphen_before)
        merged.append(t)
    if merged and merged[0].low == "aujourd'":  # defensive
        pass

    disfluencies: list[str] = []
    cleaned: list[_Tok] = []
    i = 0
    while i < len(merged):
        t = merged[i]
        nxt = merged[i + 1] if i + 1 < len(merged) else None
        if t.low in _DISFLUENCIES:
            disfluencies.append(t.low)
            i += 1
            continue
        # "vas-y", "vas y", "allez-y", "go ahead": discourse markers.
        if t.low in {"vas", "allez", "va"} and nxt is not None and nxt.low == "y":
            disfluencies.append(f"discourse:{t.low}-y")
            i += 2
            continue
        if t.low == "go" and nxt is not None and nxt.low == "ahead":
            disfluencies.append("discourse:go-ahead")
            i += 2
            continue
        if (cleaned and cleaned[-1].low == t.low and not t.is_punct
                and t.low not in _NO_COLLAPSE):
            disfluencies.append(f"repetition:{t.low}")
            i += 1
            continue
        cleaned.append(t)
        i += 1

    for t in cleaned:
        if not t.is_punct:
            t.analyses, t.accentless_ambiguous = lookup(t.low)
            if t.accentless_ambiguous and any(
                    "PP" in ft for _, ft in t.analyses) and any(
                    "PRES" in ft or "INF" in ft for _, ft in t.analyses):
                ortho.append(f"accentless:{t.low}")
    return cleaned, disfluencies, ortho


# ── helpers on analyses ──────────────────────────────────────────────────
def _feats(tok: _Tok) -> frozenset:
    out: set = set()
    for _, ft in tok.analyses:
        out |= ft
    return frozenset(out)


def _lemma(tok: _Tok) -> str:
    # Prefer a French lemma when both a French and an English one exist.
    fr = [lem for lem, ft in tok.analyses if "EN" not in ft]
    return (fr or [tok.analyses[0][0]])[0]


def _en_only(tok: _Tok) -> bool:
    return bool(tok.analyses) and all("EN" in ft for _, ft in tok.analyses)


def _cls(tok: _Tok) -> str:
    return predicate_of(_lemma(tok))[1] if tok.analyses else "none"


def _pred(tok: _Tok) -> str:
    return predicate_of(_lemma(tok))[0]


_EN_CONTEXT = {"then", "and", "but", "not", "don't", "doesn't", "didn't", "never",
               "you", "i", "we", "please", "to", "can", "could", "must", "should",
               "only", "do", "it", "they", "he", "she", "so", "or", "without"}


def _is_verb(toks: list[_Tok], i: int) -> bool:
    t = toks[i]
    if not t.analyses:
        return False
    prev = toks[i - 1] if i > 0 else None
    if _en_only(t):
        return prev is None or prev.low in _EN_CONTEXT
    if prev is not None and prev.low in _DETERMINERS:
        # "le lance" / "le lancer": clitic + verb; "le script": det + noun.
        if prev.low in {"le", "la", "les", "l'"}:
            return True
        # "de lancer" (vient de, en train de, besoin de): infinitive.
        if prev.low in {"de", "d'"} and "INF" in _feats(t):
            return True
        return False
    return True


# ── 3. clause segmentation ───────────────────────────────────────────────
def _last_verb(toks: list[_Tok]) -> _Tok | None:
    for i in range(len(toks) - 1, -1, -1):
        if _is_verb(toks, i):
            return toks[i]
    return None


def _segment(toks: list[_Tok]) -> tuple[list[_Clause], bool]:
    clauses: list[_Clause] = [_Clause([])]
    interrogative = False
    i = 0

    def cur() -> _Clause:
        return clauses[-1]

    def open_clause(conn: str | None, conn_toks: list, parent: int | None = None) -> None:
        if cur().toks:
            clauses.append(_Clause([], conn, conn_toks, embedding_parent=parent))
        else:
            if conn is not None:
                cur().conn = conn
            cur().conn_toks += conn_toks
            if parent is not None:
                cur().embedding_parent = parent

    while i < len(toks):
        t = toks[i]
        nxt = toks[i + 1] if i + 1 < len(toks) else None
        nxt2 = toks[i + 2] if i + 2 < len(toks) else None
        low = t.low

        if t.is_punct:
            if low == "?":
                interrogative = True
            open_clause(None, [])
            i += 1
            continue

        # "est-ce que" / "est-ce qu'" — interrogative marker, not a predicate.
        if low == "est" and nxt is not None and nxt.low == "ce" and nxt.hyphen_before \
                and nxt2 is not None and nxt2.low in {"que", "qu'"}:
            interrogative = True
            i += 3
            continue

        # Complex subordinators.
        if low in {"avant", "before"} and nxt is not None and nxt.low in {"de", "d'"}:
            open_clause("avant_de", [t, nxt])
            i += 2
            continue
        if low == "avant" and nxt is not None and nxt.low in {"que", "qu'"}:
            open_clause("avant_que", [t, nxt])
            i += 2
            continue
        if low in {"à", "a"} and nxt is not None and nxt.low == "moins" \
                and nxt2 is not None and nxt2.low in {"que", "qu'"}:
            open_clause("a_moins_que", [t, nxt, nxt2])
            i += 3
            continue
        if low == "parce" and nxt is not None and nxt.low in {"que", "qu'"}:
            open_clause("car", [t, nxt])
            i += 2
            continue
        if low == "sans":
            if nxt is not None and nxt.low in {"que", "qu'"}:
                open_clause("sans_que", [t, nxt])
                i += 2
            else:
                open_clause("sans", [t])
                i += 1
            continue
        if low in {"après", "apres"} and cur().toks:
            open_clause("apres", [t])
            i += 1
            continue

        # "puis-je" is pouvoir, not the connective.
        if low == "puis" and nxt is not None and nxt.hyphen_before:
            cur().toks.append(t)
            i += 1
            continue

        if low in {"si", "if"}:
            if nxt is not None and (nxt.low in _SUBJECT_PRONOUNS | _DETERMINERS
                                    or nxt.low in {"c'", "ça", "ca", "it"}):
                open_clause("si", [t])
                i += 1
                continue

        if low in _CONNECTIVES and low not in {"si", "if"}:
            conn = _CONNECTIVES[low]
            # "et puis" / ", puis": keep the most informative connective.
            if not cur().toks and cur().conn in {"et"} and conn == "puis":
                cur().conn = "puis"
                cur().conn_toks.append(t)
            elif conn == "alors" and not cur().toks:
                cur().conn_toks.append(t)
                if cur().conn is None:
                    cur().conn = "alors"
            else:
                open_clause(conn, [t])
            i += 1
            continue

        if low in {"que", "qu'"}:
            c = cur()
            verb = _last_verb(c.toks)
            vcls = _cls(verb) if verb is not None else "none"
            vpred = _pred(verb) if verb is not None else ""
            has_ne = any(x.low in {"ne", "n'"} for x in c.toks)
            prev = c.toks[-1] if c.toks else None
            embedding = (vcls.startswith("embedding") or vpred in {"WANT", "NEED"}
                         or any(x.low == "peur" for x in c.toks)
                         or any(x.low in {"paraît", "parait"} for x in c.toks))
            comparative = any(x.low in {"plus", "moins", "mieux", "autant", "pire"}
                              for x in c.toks) and not has_ne
            if embedding:
                open_clause("que", [t], parent=len(clauses) - 1)
            elif has_ne and verb is not None:
                negs = [x for x in c.toks if x.low in _FR_NEGATORS]
                c.restriction = "NOT_ONLY" if (prev is not None and prev.low == "pas") else (
                    None if negs else "ONLY")
                if c.restriction is None:
                    open_clause("que", [t], parent=len(clauses) - 1)
                else:
                    c.restriction_at = len(c.toks)
                    c.toks.append(t)
            elif comparative:
                open_clause("comparative", [t], parent=len(clauses) - 1)
            else:
                open_clause("rel", [t], parent=len(clauses) - 1)
            i += 1
            continue
        if low == "qui" and cur().toks:
            open_clause("rel", [t], parent=len(clauses) - 1)
            i += 1
            continue

        cur().toks.append(t)
        i += 1

    clauses = [c for c in clauses if c.toks or c.conn_toks]
    # A "clause" without any verb is NP material (coordination, apposition):
    # reattach it to the previous clause, connective included.
    merged: list[_Clause] = []
    for c in clauses:
        has_verb = any(_is_verb(c.toks, k) for k in range(len(c.toks)))
        if not has_verb and merged and c.conn not in {"sans", "sans_que"}:
            prev = merged[-1]
            prev.toks += c.conn_toks + c.toks
            continue
        merged.append(c)
    # Re-index embedding parents after merging.
    return merged, interrogative


# ── 4-6. predicate units ─────────────────────────────────────────────────
@dataclass
class _Draft:
    lex: _Tok
    lex_index: int
    head_index: int               # index of the finite/first verb of the chain
    verb_form: str
    tense: str = "NONE"
    modality: str | None = None
    politeness: bool = False
    modal_tok: _Tok | None = None
    subject: str | None = None
    subject_person: str | None = None
    inverted: bool = False
    governed: str | None = None          # wh | prep | purpose | temporal | permission
    governor_unit: str | None = None
    governor_negated: bool = False


_MODALITY = {"ABLE": "ABILITY_OR_PERMISSION", "MUST": "OBLIGATION",
             "NEED": "OBLIGATION", "WANT": "DESIRE", "KNOW": "KNOW_HOW"}


def _tense_of(feats: frozenset) -> str:
    for f, name in (("FUT", "FUTURE"), ("COND", "CONDITIONAL"), ("IMPF", "PAST"),
                    ("PAST_SIMPLE", "PAST"), ("PRES", "PRESENT"), ("SUBJ", "PRESENT")):
        if f in feats:
            return name
    return "NONE"


def _next_verb(toks: list[_Tok], start: int, allow: set) -> int | None:
    """Index of the next verb after start, skipping only tokens in allow."""
    k = start
    while k < len(toks):
        if _is_verb(toks, k):
            return k
        if toks[k].low not in allow:
            return None
        k += 1
    return None


def _subject_before(toks: list[_Tok], idx: int) -> tuple[str | None, str | None]:
    """Subject text and person for the verb chain starting at idx."""
    k = idx - 1
    while k >= 0 and toks[k].low in (_OBJECT_CLITICS | _REFLEXIVE_CLITICS
                                     | {"ne", "n'", "y", "en"} | _EN_NEGATORS | {"do", "does", "did"}):
        k -= 1
    if k < 0:
        return None, None
    t = toks[k]
    if t.low in _SUBJECT_PRONOUNS:
        person = "2" if t.low in _SECOND_PERSON else ("1" if t.low in _FIRST_PERSON else "3")
        return t.low, person
    if t.low in {"c'", "ça", "ca", "cela"}:
        return t.low, "3"
    if not t.analyses and t.low not in _DETERMINERS and t.low not in _PREPOSITIONS             and t.low not in _INTERJECTIONS and t.low not in _WH_WORDS \
            and t.low not in _FR_NEGATORS and t.low not in _CONNECTIVES \
            and t.low not in _TIME_ADVERBS and t.low not in {"que", "qu'", "qui"}:
        # nominal subject ("maman", "le script")
        j = k
        while j > 0 and not toks[j - 1].analyses and toks[j - 1].low not in (
                _PREPOSITIONS | _SUBJECT_PRONOUNS | {"ne", "n'"}):
            j -= 1
        words = [x.low for x in toks[j:k + 1] if x.low not in _DETERMINERS]
        return (" ".join(words) or t.low), "3"
    return None, None


def _build_drafts(toks: list[_Tok]) -> list[_Draft]:
    drafts: list[_Draft] = []
    consumed: set[int] = set()
    k = 0
    skip = {"ne", "n'", "pas", "plus", "jamais", "rien", "déjà", "deja", "bien", "not",
            "never", "surtout", "vraiment", "encore", "toujours", "le", "la", "les", "l'",
            "y", "en", "lui", "leur"} | _REFLEXIVE_CLITICS
    while k < len(toks):
        if k in consumed or not _is_verb(toks, k):
            k += 1
            continue
        t = toks[k]
        cls, pred, feats = _cls(t), _pred(t), _feats(t)
        subj, person = _subject_before(toks, k)
        inverted = False
        nxt = toks[k + 1] if k + 1 < len(toks) else None
        if nxt is not None and nxt.low in _SUBJECT_PRONOUNS and (
                nxt.hyphen_before or ("EN" in feats and cls == "modal")):
            subj, person, inverted = nxt.low, ("2" if nxt.low in _SECOND_PERSON else "1"
                                               if nxt.low in _FIRST_PERSON else "3"), True
        after = k + 2 if inverted else k + 1

        # aux avoir/être + participle ; "a failli" + infinitive ; "est en train de"
        if pred in {"HAVE", "BE"}:
            if pred == "BE":
                # être là / ici -> presence ; être en train de + inf -> progressive
                j = after
                if j < len(toks) and toks[j].low in {"là", "ici", "la", "here"} and (
                        j + 1 >= len(toks) or toks[j].low != "la" or not toks[j + 1].analyses):
                    drafts.append(_Draft(t, k, k, "FINITE", _tense_of(feats),
                                         subject=subj, subject_person=person, inverted=inverted))
                    consumed.add(k)
                    k += 1
                    continue
                if (j + 2 < len(toks) and toks[j].low == "en" and toks[j + 1].low == "train"
                        and toks[j + 2].low in {"de", "d'"}):
                    v = _next_verb(toks, j + 3, skip)
                    if v is not None:
                        drafts.append(_Draft(toks[v], v, k, "INFINITIVE", "PROGRESSIVE",
                                             subject=subj, subject_person=person))
                        consumed.update({k, v})
                        k = v + 1
                        continue
            v = _next_verb(toks, after, skip)
            if v is not None and "PP" in _feats(toks[v]):
                lex = toks[v]
                if _pred(lex) == "NEARLY":
                    w = _next_verb(toks, v + 1, skip)
                    if w is not None:
                        drafts.append(_Draft(toks[w], w, k, "INFINITIVE", "AVERTED",
                                             subject=subj, subject_person=person))
                        consumed.update({k, v, w})
                        k = w + 1
                        continue
                aux_t = _tense_of(feats)
                tense = {"PRESENT": "PAST", "PAST": "PLUPERFECT", "FUTURE": "FUTURE",
                         "CONDITIONAL": "CONDITIONAL"}.get(aux_t, "PAST")
                drafts.append(_Draft(lex, v, k, "PARTICIPLE", tense,
                                     subject=subj, subject_person=person, inverted=inverted))
                consumed.update({k, v})
                k = v + 1
                continue
            if pred == "HAVE" and nxt is not None and nxt.low == "peur":
                drafts.append(_Draft(t, k, k, "FINITE", _tense_of(feats), subject=subj,
                                     subject_person=person))
                consumed.add(k)
                k += 1
                continue
            consumed.add(k)
            k += 1
            continue

        # aller + inf (near future / imperative "va lancer"), venir de + inf
        if pred == "GO":
            v = _next_verb(toks, after, skip)
            if v is not None and "INF" in _feats(toks[v]):
                drafts.append(_Draft(toks[v], v, k, "INFINITIVE",
                                     "NEAR_FUTURE" if subj else "NONE",
                                     subject=subj, subject_person=person))
                consumed.update({k, v})
                k = v + 1
                continue
            consumed.add(k)
            k += 1
            continue
        if pred == "COME":
            if after < len(toks) and toks[after].low in {"de", "d'"}:
                v = _next_verb(toks, after + 1, skip)
                if v is not None:
                    drafts.append(_Draft(toks[v], v, k, "INFINITIVE", "RECENT_PAST",
                                         subject=subj, subject_person=person))
                    consumed.update({k, v})
                    k = v + 1
                    continue
            consumed.add(k)
            k += 1
            continue

        # modal + infinitive
        if cls == "modal":
            v = _next_verb(toks, after, skip)
            form = "INFINITIVE"
            if v is not None and _pred(toks[v]) == "BE":
                # passive under modal: "doit être lancé"
                w = _next_verb(toks, v + 1, skip)
                if w is not None and "PP" in _feats(toks[w]):
                    consumed.add(v)
                    v, form = w, "PARTICIPLE"
            if v is not None and ("INF" in _feats(toks[v]) or form == "PARTICIPLE"):
                d = _Draft(toks[v], v, k, form, _tense_of(feats),
                           modality=_MODALITY.get(pred), modal_tok=t,
                           politeness="COND" in feats or t.low == "could",
                           subject=subj, subject_person=person, inverted=inverted)
                if pred == "NEED":
                    d.subject_person = "impersonal"
                drafts.append(d)
                consumed.update({k, v})
                k = v + 1
                continue
            drafts.append(_Draft(t, k, k, "FINITE", _tense_of(feats), subject=subj,
                                 subject_person=person, politeness="COND" in feats,
                                 inverted=inverted))
            consumed.add(k)
            k += 1
            continue

        # EN "do" as auxiliary: do not run / don't run
        if pred == "DO" and "EN" in feats and nxt is not None and nxt.low in _EN_NEGATORS:
            consumed.add(k)
            k += 1
            continue

        form = "FINITE"
        prev = toks[k - 1] if k > 0 else None
        if "INF" in feats and (not ({"PRES", "IMP", "PP"} & feats)
                               or (prev is not None and prev.low in {"de", "d'", "à", "to", "pas", "rien"})):
            form = "INFINITIVE"
        elif "PPR" in feats and not ({"PRES", "IMP", "INF"} & feats):
            form = "GERUND"
        elif subj is None and ({"IMP", "PRES", "INF"} & feats):
            form = "IMPERATIVE"
        elif subj is None and "PP" in feats:
            form = "PARTICIPLE"
        drafts.append(_Draft(t, k, k, form, "NONE" if form in {"IMPERATIVE", "INFINITIVE"}
                             else _tense_of(feats), subject=subj, subject_person=person,
                             inverted=inverted))
        consumed.add(k)
        k += 1
    return drafts


# ── objects ──────────────────────────────────────────────────────────────
def _np_from(toks: list[_Tok], j: int) -> tuple[Argument | None, int]:
    """Parse one noun phrase starting at j. Returns (argument, next index)."""
    if j >= len(toks):
        return None, j
    t = toks[j]
    if t.low in _WH_WORDS or t.low in _REFLEXIVE_CLITICS or t.low in _MANNER_ADVERBS:
        return None, j
    if t.low in _DEMONSTRATIVE_PRONOUNS:
        end = j + 1
        text = t.low
        if end < len(toks) and toks[end].hyphen_before and toks[end].low in {"ci", "là", "la"}:
            text += "-" + toks[end].low
            end += 1
        return Argument(text, text, "DEMONSTRATIVE", "UNRESOLVED", span=(t.start, toks[end - 1].end)), end
    if t.low in _PRONOUN_OBJECTS_EN:
        return Argument(t.low, t.low, "PRONOUN", "UNRESOLVED", span=(t.start, t.end)), j + 1
    if t.low == "rien" or t.low == "personne":
        return Argument(t.low, "*", "NEGATIVE_QUANTIFIER", "LITERAL", span=(t.start, t.end)), j + 1
    det = None
    if t.low in _DETERMINERS:
        det = t.low
        j += 1
    words = []
    start = t.start
    end_tok = t
    while j < len(toks):
        w = toks[j]
        if (w.low in _PREPOSITIONS or w.low in _TIME_ADVERBS or w.low in _CONNECTIVES
                or w.low in {"que", "qu'", "qui", "ne", "n'"} or w.low in _WH_WORDS
                or (words and (w.low in _FR_NEGATORS or w.low in _EN_NEGATORS))
                or w.low in _DETERMINERS
                or w.low in _SUBJECT_PRONOUNS or w.low in _RESTRICTION_ADVERBS
                or _is_verb(toks, j)):
            break
        words.append(w.low)
        end_tok = w
        j += 1
    if det is None and not words:
        return None, j
    if not words:
        # bare "le" / "la" / "les" / "l'" with nothing nominal after: pronoun
        if det in {"le", "la", "les", "l'"}:
            return Argument(det, det, "PRONOUN", "UNRESOLVED", span=(t.start, t.end)), j
        return None, j
    head = " ".join(words)
    if det in _DEMONSTRATIVE_DET:
        ref, kind = "DEICTIC", "NP"
    elif det in {"aucun", "aucune"}:
        ref, kind = "LITERAL", "NEGATIVE_QUANTIFIER"
    elif det in _DEFINITE:
        ref, kind = "PRESUPPOSED", "NP"
    else:
        ref, kind = "LITERAL", "NP"
    text = " ".join(([det] if det else []) + words)
    return Argument(text, head, kind, ref, span=(start, end_tok.end)), j


def _objects_for(toks: list[_Tok], d: _Draft, clause: _Clause) -> list[Argument]:
    args: list[Argument] = []
    k = d.lex_index
    # clitic objects before the chain head ("ne l'exécute", "tu le lances")
    j = d.head_index - 1
    while j >= 0 and toks[j].low in (_OBJECT_CLITICS | _REFLEXIVE_CLITICS | {"ne", "n'", "rien"}):
        if toks[j].low in {"le", "la", "les", "l'"}:
            args.append(Argument(toks[j].low, toks[j].low, "PRONOUN", "UNRESOLVED",
                                 span=(toks[j].start, toks[j].end)))
        if toks[j].low == "rien":
            args.append(Argument("rien", "*", "NEGATIVE_QUANTIFIER", "LITERAL",
                                 span=(toks[j].start, toks[j].end)))
        j -= 1
    # clitic between modal and infinitive ("tu peux le lancer")
    for m in range(d.head_index + 1, k):
        if toks[m].low in {"le", "la", "les", "l'"}:
            args.append(Argument(toks[m].low, toks[m].low, "PRONOUN", "UNRESOLVED",
                                 span=(toks[m].start, toks[m].end)))
    j = k + 1
    if d.inverted and d.head_index == k:
        j += 1
    # hyphenated clitic: "exécute-le", "fais-le"
    if j < len(toks) and toks[j].hyphen_before and toks[j].low in {"le", "la", "les", "moi", "lui"}:
        if toks[j].low in {"le", "la", "les"}:
            args.append(Argument(toks[j].low, toks[j].low, "PRONOUN", "UNRESOLVED",
                                 span=(toks[j].start, toks[j].end)))
        j += 1
    # restriction "que" ("ne lance que les tests")
    if clause.restriction_at is not None and clause.restriction_at > k:
        j = clause.restriction_at + 1
    while j < len(toks) and toks[j].low in (_ADVERBS_SKIPPABLE | _RESTRICTION_ADVERBS
                                            | {"ni"}) - {"rien"}:
        j += 1
    # coordinated NPs: "le script et les tests", "ni le script ni les tests"
    while j < len(toks):
        arg, nj = _np_from(toks, j)
        if arg is None:
            break
        args.append(arg)
        j = nj
        if j < len(toks) and toks[j].low in {"et", "ni", "ou", "and", "or", ","}:
            j += 1
            continue
        break
    return args


# ── negation / restriction / expletive ne ────────────────────────────────
def _polarity(toks: list[_Tok], d: _Draft, clause: _Clause, all_drafts: list[_Draft]) -> dict:
    out = {"polarity": "positive", "negator": None, "negation_confirmed": False,
           "ne_omitted": False, "ne_expletive": False, "restriction": None,
           "confidence": 1.0}
    lo, hi = d.head_index, d.lex_index
    lows = [t.low for t in toks]

    if clause.conn in {"sans", "sans_que"} and d is all_drafts[0]:
        out.update(polarity="negative", negator="sans" if clause.conn == "sans" else "sans que",
                   negation_confirmed=True)
        return out

    # EN negation: do not / don't / never / not before the chain head.
    for j in range(max(0, lo - 3), lo):
        if lows[j] in _EN_NEGATORS:
            out.update(polarity="negative", negator=lows[j], negation_confirmed=True)
            return out

    # Scope (OQLF): "ne" precedes the finite verb (clitics in between) and the
    # negator follows it: ne [clitics] V_fin NEG. Before an infinitive both
    # elements precede it: ne NEG [clitics] V_inf. A "ne ... NEG" pair that
    # frames ANOTHER word (even a verb unknown to the lexicon, e.g.
    # "n'oublie pas de lancer") does not negate this chain.
    prev_hi = max([x.lex_index for x in all_drafts if x.lex_index < lo] or [-1])
    next_lo = min([x.head_index for x in all_drafts if x.head_index > hi] or [len(toks)])
    clitics = _OBJECT_CLITICS | _REFLEXIVE_CLITICS
    ne_idx = [j for j in range(prev_hi + 1, hi) if lows[j] in {"ne", "n'"}]
    if ne_idx:
        ne = ne_idx[-1]
        if clause.restriction == "NOT_ONLY":
            out["restriction"] = "NOT_ONLY"
            return out
        framed = ne < lo and all(lows[j] in clitics for j in range(ne + 1, lo))
        if framed:
            # ne [clitics] V_fin ... NEG  (negator after the chain head)
            neg = [j for j in range(lo + 1, next_lo) if lows[j] in _FR_NEGATORS]
            if neg:
                out.update(polarity="negative", negator=lows[neg[0]], negation_confirmed=True)
                return out
        # ne NEG [clitics] V_inf  (both precede the lexical infinitive)
        if ne + 1 < hi and lows[ne + 1] in _FR_NEGATORS and all(
                lows[j] in clitics | _FR_NEGATORS or j == lo for j in range(ne + 2, hi)):
            out.update(polarity="negative", negator=lows[ne + 1], negation_confirmed=True)
            return out
        if framed:
            if clause.restriction == "ONLY":
                out["restriction"] = "ONLY"
                return out
            if clause.conn in {"que", "avant_que", "a_moins_que", "comparative"}:
                out["ne_expletive"] = True
                return out
            out.update(polarity="negative", negator="ne", negation_confirmed=False, confidence=0.5)
            return out
        # The ne ... NEG pair frames another (possibly unknown) predicate.
        out["governor_negated"] = True
        return out
    # oral negation: negator right after the verb (or its hyphenated clitic)
    j = hi + 1
    while j < len(lows) and toks[j].hyphen_before and lows[j] in {"le", "la", "les", "moi", "lui"}:
        j += 1
    if j < len(lows) and lows[j] in _ORAL_NEGATORS and not (
            j + 1 < len(lows) and lows[j] == "pas" and lows[j + 1] in {"à", "a", "besoin"}):
        out.update(polarity="negative", negator=lows[j], ne_omitted=True,
                   negation_confirmed=False, confidence=0.7)
        return out
    if any(lows[j] in _RESTRICTION_ADVERBS for j in range(prev_hi + 1, min(next_lo, len(lows)))):
        out["restriction"] = "ONLY"
    return out


# ── main entry point ─────────────────────────────────────────────────────
def parse_utterance(raw: str) -> UtteranceFrame:
    raw = raw if isinstance(raw, str) else str(raw)
    toks, disfluencies, ortho = _tokenize(raw)
    normalized = " ".join(t.low for t in toks)
    clauses, interrogative = _segment(toks)
    if any(t.hyphen_before and t.low in _SUBJECT_PRONOUNS for t in toks):
        interrogative = True

    units: list[PredicateUnit] = []
    relations: list[LatticeRelation] = []
    ambiguities: list[str] = []
    deixis = [t.low for t in toks if t.low in _DEIXIS and not t.hyphen_before]
    counter = 0

    for ci, clause in enumerate(clauses):
        drafts = _build_drafts(clause.toks)
        for d in drafts:
            counter += 1
            lemma = _lemma(d.lex)
            pred, pcls = predicate_of(lemma)
            if pred == "BE":
                pred, pcls = "BE_PRESENT", "state"
            pol = _polarity(clause.toks, d, clause, drafts)
            objs = _objects_for(clause.toks, d, clause)
            if pol["negator"] in {"rien", "personne"} and not objs:
                objs = [Argument(pol["negator"], "*", "NEGATIVE_QUANTIFIER", "LITERAL")]
            if pol["negator"] == "aucun" or pol["negator"] == "aucune":
                pol["negator"] = "aucun"
            unit = PredicateUnit(
                id=f"u{counter}", predicate=pred, lemma=lemma, surface=d.lex.low,
                span=(d.lex.start, d.lex.end), clause=ci, predicate_class=pcls,
                verb_form=d.verb_form, polarity=pol["polarity"], negator=pol["negator"],
                negation_confirmed=pol["negation_confirmed"], ne_omitted=pol["ne_omitted"],
                ne_expletive=pol["ne_expletive"], restriction=pol["restriction"],
                modality=d.modality, politeness=d.politeness, tense_aspect=d.tense,
                subject=d.subject, objects=tuple(objs), confidence=pol["confidence"],
            )
            if d.lex.accentless_ambiguous:
                unit = replace(unit, confidence=min(unit.confidence, 0.9))
            if pol["negator"] == "ne":
                ambiguities.append(f"bare_ne:{unit.id}")
            _mark_governed(clause, d, pol)
            clause.units.append((unit, d))
            units.append(unit)

    # "pas besoin de" + infinitive
    for clause in clauses:
        lows = [t.low for t in clause.toks]
        for idx in range(len(lows) - 2):
            if lows[idx] == "pas" and lows[idx + 1] == "besoin" and lows[idx + 2] in {"de", "d'"}:
                for n, (u, d) in enumerate(clause.units):
                    if d.lex_index > idx + 2:
                        clause.units[n] = (replace(u, polarity="positive", negator=None,
                                                   ne_omitted=False, pragmatic="NOT_REQUIRED",
                                                   confidence=0.9), d)
                        break

    # ── pragmatic / epistemic by clause role ──
    main_heads: list[tuple[int, PredicateUnit]] = []

    def head_of(ci: int) -> PredicateUnit | None:
        return clauses[ci].units[0][0] if clauses[ci].units else None

    def last_of(ci: int) -> PredicateUnit | None:
        return clauses[ci].units[-1][0] if clauses[ci].units else None

    for ci, clause in enumerate(clauses):
        parent_unit = None
        if clause.embedding_parent is not None and clause.embedding_parent < ci:
            parent_unit = last_of(clause.embedding_parent)
        # embedding parent may have been merged; fall back to previous clause
        if clause.conn in {"que", "rel", "comparative"} and parent_unit is None and ci > 0:
            parent_unit = last_of(ci - 1)
        new_units = []
        for n, (u, d) in enumerate(clause.units):
            prag, epi, realized = u.pragmatic, "NOT_APPLICABLE", None
            embedded_under = None
            if prag == "NOT_REQUIRED":
                new_units.append((u, d))
                continue
            if clause.conn in {"sans", "sans_que"} and n == 0:
                prag = "FORBIDDEN"
            elif clause.conn == "que" and parent_unit is None and n == 0 and ci > 0 and any(
                    t.low in {"paraît", "parait"} for t in clauses[ci - 1].toks):
                prag, epi = "REPORTED", "HEARSAY"
            elif clause.conn == "que" and parent_unit is not None and n == 0:
                embedded_under = parent_unit.id
                pp = parent_unit.predicate
                if pp == "SAY":
                    prag = "REPORTED"
                    epi = "HEARSAY" if parent_unit.subject in {"on", "ils", "they"} else "REPORTED"
                    kind = RelationKind.REPORTS
                elif pp == "FEAR" or (pp in {"HAVE"}):
                    prag, epi, kind = "FEARED", "POSSIBLE", RelationKind.FEARS
                elif pp == "PREVENT":
                    prag, kind = "PREVENTED", RelationKind.PREVENTS
                elif pp == "BELIEVE":
                    prag, epi, kind = "BELIEVED", "BELIEF", RelationKind.BELIEVES
                elif pp == "LEARN":
                    prag, epi, kind = "ASSERTED", "ASSERTED", RelationKind.EMBEDS
                elif pp == "OBSERVE":
                    prag, epi, kind = "ASSERTED", "ASSERTED", RelationKind.EMBEDS
                elif pp in {"WANT", "NEED"}:
                    speaker_wants = pp == "NEED" or parent_unit.subject in _FIRST_PERSON
                    prag = "REQUESTED" if speaker_wants else "REPORTED"
                    if u.polarity == "negative" and speaker_wants:
                        prag = "FORBIDDEN"
                    kind = RelationKind.WANTS
                else:
                    prag, epi, kind = "ASSERTED", "ASSERTED", RelationKind.EMBEDS
                relations.append(LatticeRelation(kind.value, parent_unit.id, u.id,
                                                 evidence="que"))
            elif clause.conn in {"avant_que", "a_moins_que"} and n == 0:
                prag, epi = "HYPOTHETICAL", "HYPOTHETICAL"
            elif clause.conn == "si" and n == 0:
                prag, epi = "HYPOTHETICAL", "HYPOTHETICAL"
            elif clause.conn in {"rel", "comparative"}:
                prag, epi = "ASSERTED", "ASSERTED"
                if parent_unit is not None:
                    embedded_under = parent_unit.id
                    relations.append(LatticeRelation(RelationKind.EMBEDS.value, parent_unit.id,
                                                     u.id, evidence=clause.conn))
            elif d.governed == "wh":
                prag, epi = ("ASKED", "UNKNOWN") if interrogative else ("EMBEDDED", "NOT_APPLICABLE")
            elif d.governed in {"purpose", "temporal", "permission"}:
                prag, epi = "EMBEDDED", "NOT_APPLICABLE"
            elif d.governed == "observation_target":
                prag, epi = "EMBEDDED", "NOT_APPLICABLE"
                gov = next((x for (x, _) in new_units + clause.units if x.id == d.governor_unit), None)
                if gov is not None:
                    embedded_under = gov.id
                    relations.append(LatticeRelation(RelationKind.EMBEDS.value, gov.id, u.id,
                                                     evidence="observation+inf"))
            elif d.governed == "prep":
                gov = next((x for (x, _) in new_units + clause.units if x.id == d.governor_unit), None)
                if gov is not None and gov.predicate in {"FORGET", "HESITATE"} and d.governor_negated:
                    # "n'oublie pas de lancer", "n'hésite pas à lancer": reminder / invitation
                    prag, epi = "REQUESTED", "NOT_APPLICABLE"
                else:
                    prag, epi = "EMBEDDED", "NOT_APPLICABLE"
                    if gov is None:
                        d.governed = "unknown_prep"
                        ambiguities.append(f"infinitive_under_unrecognized_governor:{u.id}")
                if gov is not None:
                    embedded_under = gov.id
                    relations.append(LatticeRelation(RelationKind.EMBEDS.value, gov.id, u.id,
                                                     evidence="prep+inf"))
            else:
                prag, epi = _main_pragmatics(u, d, interrogative, ambiguities)
            if u.tense_aspect in {"PAST", "PLUPERFECT", "RECENT_PAST"} and prag in {
                    "ASSERTED", "REPORTED", "BELIEVED", "ASKED"}:
                realized = True if prag != "ASKED" else None
            if u.tense_aspect == "AVERTED":
                realized, epi = False, "COUNTERFACTUAL"
            if prag in {"REQUESTED", "FORBIDDEN", "INDIRECT_REQUEST"} and u.polarity == "negative":
                prag = "FORBIDDEN"
            elif prag == "FORBIDDEN" and u.polarity == "positive" and clause.conn not in {"sans", "sans_que"}:
                prag = "REQUESTED"
            tmp = replace(u, pragmatic=prag, epistemic=epi, realized=realized,
                          embedded_under=embedded_under)
            role = _role(tmp, d, prag, interrogative)
            agent = _action_agent(tmp, d, prag)
            target = _request_target(tmp, agent, prag, role)
            new_units.append((replace(tmp, action_agent=agent, request_target=target,
                                      role=role), d))
        clause.units = new_units
        # Temporal infinitives mention context; preserve legacy fail-closed
        # behavior when a PREPARE request is framed as before executing.
        if clause.conn in {"avant_de", "apres"} and clause.units and main_heads:
            prev = main_heads[-1][1]
            u, d = clause.units[0]
            if prev.predicate == "PREPARE" and u.predicate_class == "world_action":
                clause.units[0] = (replace(u, pragmatic="REQUESTED", epistemic="NOT_APPLICABLE",
                                           action_agent="ADDRESSEE", request_target="ADDRESSEE",
                                           role="REQUEST"), d)

        # Subordinate clauses (reason, condition, embedding...) never become the
        # host of a following "puis" / "mais": only main clauses do.
        if clause.conn not in {"que", "rel", "comparative", "sans", "sans_que", "si",
                               "avant_que", "a_moins_que", "car"} and clause.units:
            main_heads.append((ci, clause.units[0][0]))

    # ── inter-clause relations ──
    for ci, clause in enumerate(clauses):
        h = head_of(ci)
        if h is None:
            continue
        conn = clause.conn
        prev_main = next((u for (cj, u) in reversed(main_heads) if cj < ci), None)
        next_main = next((u for (cj, u) in main_heads if cj > ci), None)
        if conn in {"sans", "sans_que"}:
            host = prev_main or next_main
            if host is not None:
                relations.append(LatticeRelation(RelationKind.FORBIDS.value, host.id, h.id,
                                                 evidence=conn))
        elif conn == "si":
            host = next_main if next_main is not None else prev_main
            if host is not None:
                relations.append(LatticeRelation(RelationKind.CONDITIONS.value, h.id, host.id,
                                                 evidence="si"))
        elif conn == "avant_que" and prev_main is not None:
            relations.append(LatticeRelation(RelationKind.PRECEDES.value, prev_main.id, h.id,
                                             evidence="avant que"))
        elif conn == "a_moins_que" and prev_main is not None:
            relations.append(LatticeRelation(RelationKind.CONDITIONS.value, h.id, prev_main.id,
                                             confidence=0.8, evidence="à moins que"))
        elif prev_main is not None and conn in {"mais", "puis", "et", "ou", "donc", "car",
                                                "avant_de", "apres", "alors"}:
            kind, src, tgt = {
                "mais": (RelationKind.CONTRASTS, prev_main, h),
                "puis": (RelationKind.PRECEDES, prev_main, h),
                "avant_de": (RelationKind.PRECEDES, prev_main, h),
                "apres": (RelationKind.PRECEDES, h, prev_main),
                "et": (RelationKind.COORDINATES, prev_main, h),
                "ou": (RelationKind.ALTERNATIVE, prev_main, h),
                "donc": (RelationKind.CAUSES, prev_main, h),
                "alors": (RelationKind.CAUSES, prev_main, h),
                "car": (RelationKind.CAUSES, h, prev_main),
            }[conn]
            if conn == "avant_de" and prev_main.polarity == "negative":
                # "ne lance pas X avant de le préparer" => préparer precedes lancer
                src, tgt = h, prev_main
            # "si P, alors Q": CONDITIONS already links P -> Q.
            if not (conn == "alors" and any(c.conn == "si" for c in clauses[:ci])):
                relations.append(LatticeRelation(kind.value, src.id, tgt.id, evidence=conn))

    final_units = [u for c in clauses for (u, _) in c.units]
    final_units, ref_relations, unresolved, presupposed = _resolve_references(final_units)
    relations.extend(ref_relations)

    constraints = _constraints(final_units)
    contradictions = _contradictions(final_units)
    evidence = _evidence_needs(final_units)

    if interrogative:
        surface = "interrogative"
    elif any(u.verb_form == "IMPERATIVE" and u.embedded_under is None for u in final_units):
        surface = "imperative"
    elif final_units:
        surface = "declarative"
    else:
        surface = "none"

    return UtteranceFrame(
        raw=raw,
        normalized=normalized,
        units=tuple(final_units),
        relations=tuple(relations),
        constraints=tuple(constraints),
        surface_act=surface,
        unresolved_references=tuple(unresolved),
        presupposed_referents=tuple(presupposed),
        deixis=tuple(deixis),
        ambiguities=tuple(dict.fromkeys(ambiguities)),
        contradictions=tuple(contradictions),
        evidence_needs=tuple(evidence),
        disfluencies=tuple(disfluencies),
        orthography_flags=tuple(dict.fromkeys(ortho)),
    )


def _mark_governed(clause: _Clause, d: _Draft, pol: dict) -> None:
    """Classify infinitive roles that mention an action without requesting it."""
    lows = [t.low for t in clause.toks]
    if (clause.conn in {"avant_de", "apres"} or any(x in {"après", "apres", "before", "after"} for x in lows[:d.lex_index])) and d.verb_form in {"INFINITIVE", "PARTICIPLE"}:
        d.governed = "temporal"
        return
    if d.verb_form in {"INFINITIVE", "PARTICIPLE"}:
        prior = [u for (u, dd) in clause.units if dd.lex_index < d.head_index]
        if prior and prior[-1].predicate == "OBSERVE":
            d.governed = "observation_target"
            d.governor_unit = prior[-1].id
            return
    if d.verb_form != "INFINITIVE" or d.lex_index != d.head_index:
        return
    j = d.lex_index - 1
    skip = _OBJECT_CLITICS | _REFLEXIVE_CLITICS | {"ne", "n'", "pas", "rien", "jamais", "plus", "avoir"}
    while j >= 0 and lows[j] in skip:
        j -= 1
    if j < 0:
        return
    if lows[j] in _WH_WORDS or (lows[j] in {"de", "d'", "à", "to"} and j > 0
                                and lows[j - 1] in _WH_WORDS):
        d.governed = "wh"
        return
    if lows[j] in {"pour", "for"}:
        d.governed = "purpose"
        return
    if lows[j] in {"de", "d'", "à", "to"} and j > 0:
        if lows[j - 1] in {"droit", "permission"}:
            d.governed = "permission"
            speaker = next((x for x in lows[:j] if x in _FIRST_PERSON), None)
            if speaker is not None:
                d.subject = speaker
                d.subject_person = "1"
            return
        if lows[j - 1] == "besoin":
            return
        d.governed = "prep"
        prior = [u for (u, dd) in clause.units if dd.lex_index < j]
        d.governor_unit = prior[-1].id if prior else None
        d.governor_negated = bool(pol.get("governor_negated")) or bool(
            prior and prior[-1].polarity == "negative")


def _action_agent(u: PredicateUnit, d: _Draft, prag: str) -> str:
    if d.subject_person == "1":
        return "SPEAKER"
    if d.subject_person == "2":
        return "ADDRESSEE"
    if d.subject_person == "3":
        return "THIRD_PARTY"
    if d.subject_person == "impersonal":
        return "IMPERSONAL"
    if d.subject is None and prag in {"REQUESTED", "INDIRECT_REQUEST", "FORBIDDEN"}:
        return "ADDRESSEE"
    return "UNKNOWN"


def _role(u: PredicateUnit, d: _Draft, prag: str, interrogative: bool) -> str:
    if u.polarity == "negative":
        return "NEGATED"
    if prag == "REPORTED":
        return "REPORTED"
    if prag == "BELIEVED":
        return "BELIEVED"
    if prag == "HYPOTHETICAL":
        return "HYPOTHETICAL"
    if d.governed == "wh":
        return "EXPLANATION_CONTENT"
    if d.governed == "purpose":
        return "PURPOSE"
    if d.governed == "temporal":
        return "TEMPORAL_CONTEXT"
    if d.governed == "permission":
        return "PERMISSION_QUERY"
    if d.governed == "unknown_prep":
        return "REQUEST"
    if prag == "REQUESTED":
        return "REQUEST"
    if prag == "INDIRECT_REQUEST":
        return "AMBIGUOUS_REQUEST"
    if d.subject_person == "1" and u.modality == "DESIRE":
        return "DESIRE_ASSERTION"
    if d.subject_person == "1" and (interrogative or u.modality == "ABILITY_OR_PERMISSION"):
        return "PERMISSION_QUERY"
    if d.subject_person == "3" and u.predicate_class == "world_action":
        return "THIRD_PARTY_ACTION"
    if u.predicate_class == "world_action":
        return "MENTION"
    return "OTHER"


def _request_target(u: PredicateUnit, agent: str, prag: str, role: str) -> str:
    if u.polarity != "positive" or u.predicate_class != "world_action":
        return "NONE"
    if role == "REQUEST" and prag in {"REQUESTED", "EMBEDDED"} and agent in {"ADDRESSEE", "UNKNOWN", "IMPERSONAL"}:
        return "ADDRESSEE"
    if role == "AMBIGUOUS_REQUEST" and prag == "INDIRECT_REQUEST" and agent == "ADDRESSEE":
        return "ADDRESSEE_OR_POSSIBLE_ADDRESSEE"
    return "NONE"

def _main_pragmatics(u: PredicateUnit, d: _Draft, interrogative: bool,
                     ambiguities: list[str]) -> tuple[str, str]:
    person = d.subject_person
    if u.modality == "ABILITY_OR_PERMISSION":
        if person == "2" and (interrogative or d.politeness):
            ambiguities.append(f"ability_permission_or_request:{u.id}")
            return "INDIRECT_REQUEST", "NOT_APPLICABLE"
        return ("ASKED", "UNKNOWN") if interrogative else ("ASSERTED", "ASSERTED")
    if u.modality == "OBLIGATION":
        if person in {"2", "impersonal"} or d.subject is None:
            return "REQUESTED", "NOT_APPLICABLE"
        return ("ASKED", "UNKNOWN") if interrogative else ("ASSERTED", "ASSERTED")
    if u.modality == "DESIRE":
        if person == "1":
            ambiguities.append(f"desire_or_request:{u.id}")
        return ("ASKED", "UNKNOWN") if interrogative else ("ASSERTED", "ASSERTED")
    if u.modality == "KNOW_HOW":
        return ("ASKED", "UNKNOWN") if interrogative else ("ASSERTED", "ASSERTED")
    if (interrogative and person == "2" and u.tense_aspect == "PRESENT"
            and u.predicate_class == "world_action"):
        # "tu lances le script ?" — literal question or request: fail-closed.
        ambiguities.append(f"question_or_request:{u.id}")
        return "INDIRECT_REQUEST", "NOT_APPLICABLE"
    if u.verb_form == "IMPERATIVE":
        return "REQUESTED", "NOT_APPLICABLE"
    if u.verb_form == "INFINITIVE" and d.subject is None:
        # injunctive infinitive ("lancer le script") or "va lancer"
        return "REQUESTED", "NOT_APPLICABLE"
    if interrogative:
        return "ASKED", "UNKNOWN"
    return "ASSERTED", "ASSERTED"


def _resolve_references(units: list[PredicateUnit]):
    """Intra-utterance anaphora (then cataphora) for pronoun objects."""
    candidates: list[tuple[int, str, str]] = []  # (position, head, unit id)
    for u in units:
        for a in u.objects:
            if a.kind in {"NP", "NEGATIVE_QUANTIFIER"} and a.head != "*":
                candidates.append(((a.span or u.span)[0], a.head, u.id))
    relations: list[LatticeRelation] = []
    unresolved: list[str] = []
    presupposed: list[str] = []
    out: list[PredicateUnit] = []
    for u in units:
        new_args = []
        for a in u.objects:
            if a.reference == "UNRESOLVED" and a.kind == "PRONOUN":
                pos = (a.span or u.span)[0]
                before = [c for c in candidates if c[0] < pos]
                after = [c for c in candidates if c[0] > pos]
                ante = before[-1] if before else (after[0] if after else None)
                if ante is not None:
                    a = replace(a, reference="RESOLVED_INTRA", antecedent=ante[1],
                                antecedent_unit=ante[2])
                    if ante[2] != u.id:
                        relations.append(LatticeRelation(RelationKind.REFERS_TO.value, u.id,
                                                         ante[2], confidence=0.8,
                                                         evidence=f"{a.text}->{ante[1]}"))
            if a.reference == "UNRESOLVED":
                unresolved.append(f"{u.id}:{a.text}")
            if a.reference == "PRESUPPOSED":
                presupposed.append(a.head)
            new_args.append(a)
        out.append(replace(u, objects=tuple(new_args)))
    return out, relations, unresolved, list(dict.fromkeys(presupposed))


def _heads(u: PredicateUnit) -> list[str]:
    heads = []
    for a in u.objects:
        if a.reference == "RESOLVED_INTRA" and a.antecedent:
            heads.append(a.antecedent)
        elif a.reference != "UNRESOLVED":
            heads.append(a.head)
    return heads or ["*"]


def _constraints(units: list[PredicateUnit]) -> list[str]:
    out: list[str] = []
    for u in units:
        if u.pragmatic == "FORBIDDEN" and u.polarity == "negative":
            out += [f"NO_{u.predicate}({h})" for h in _heads(u)]
        if u.pragmatic == "PREVENTED":
            out += [f"PREVENT_{u.predicate}({h})" for h in _heads(u)]
        if u.restriction == "ONLY" and u.polarity == "positive":
            out += [f"ONLY_{u.predicate}({h})" for h in _heads(u)]
    return list(dict.fromkeys(out))


def _contradictions(units: list[PredicateUnit]) -> list[str]:
    out = []
    requested = [u for u in units if u.pragmatic in {"REQUESTED", "INDIRECT_REQUEST"}
                 and u.polarity == "positive"]
    forbidden = [u for u in units if u.pragmatic == "FORBIDDEN" and u.polarity == "negative"]
    for r in requested:
        for f in forbidden:
            if r.predicate != f.predicate:
                continue
            rh, fh = set(_heads(r)), set(_heads(f))
            if rh & fh or "*" in fh:
                out.append(f"{r.predicate}({sorted(rh & fh or rh)[0]}):requested_and_forbidden:"
                           f"{r.id}/{f.id}")
    return out


def _evidence_needs(units: list[PredicateUnit]) -> list[str]:
    out = []
    for u in units:
        if u.pragmatic != "ASKED" or u.tense_aspect not in {"PRESENT", "NONE"}:
            continue
        if u.predicate == "BE_PRESENT":
            out.append(f"current_world_observation:BE_PRESENT({u.subject or '?'})")
        elif u.predicate == "WEATHER":
            out.append("current_world_observation:WEATHER")
    return out
