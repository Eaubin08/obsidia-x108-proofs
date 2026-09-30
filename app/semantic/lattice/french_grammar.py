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

from app.semantic.lattice.lexicon import fold, has_imperative_paradigm, lookup, predicate_of
from app.semantic.lattice.primitives import (
    Argument, CoordinationRef, LatticeRelation, OperatorScopeRef, PredicateUnit, RelationKind,
    UtteranceFrame,
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
_TEMPORAL_INTRODUCERS = {"lorsque", "lorsqu'"}
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
    unresolved_governor: int | None = None  # index of an unknown verb governing "que"
    governor_lost: bool = False  # "que" clause after a non-nominal word: not a relative
    coordinated_with: "_Clause | None" = None  # "V que P et que Q": Q's sibling complement P
    attachment_ambiguous: bool = False  # coordinated after a complement, several attachments open
    complement_structure_lost: bool = False  # "V que [le X que P] V2": verbless complement opener merged
    evidential: str | None = None  # detached source / evidential adverbial ("Selon Marie, P")
    boundary: str | None = None  # punctuation that opened the clause
    protasis_head: "_Clause | None" = None  # first "si" clause of a conjunctive protasis
    ni_head: "_Clause | None" = None  # clause holding "ne" of a verbal "ne ... ni V1 ni V2"
    compound: tuple | None = None  # (tense, auxiliary surface, draft) of its last AUX+PP predicate
    shared_aux_host: "_Clause | None" = None  # clause whose auxiliary a bare participle shares
    modal: object = None  # its last modal+infinitive draft (OBLIGATION), shared by bare infinitives
    shared_modal_host: "_Clause | None" = None  # clause whose modal a bare infinitive shares
    ni_modal: object = None  # obligation modal of "ne doit ni INF1 ni INF2" (token, then its draft)
    ni_scope_open: object = None  # "vouloir" token of a "ne ... ni INF" whose negated scope is not shared
    neg_scope_open: object = None  # negated operator chain draft whose scope over a bare coordinated INF is open
    know_how_open: object = None  # savoir (KNOW_HOW) chain draft: its scope over a bare coordinated INF is open
    wh_governor: object = None  # verb token right before the WH word of a "wh" complement ("sais quand P")
    subject_unresolved_chain: bool = False  # its bare finite verb disagreed with the host subject (NF4)
    subject_host: object = None  # its last draft with an explicit subject, shared by an agreeing bare verb
    shared_subject_host: "_Clause | None" = None  # clause whose subject a bare finite verb shares
    share_family: str | None = None  # "and" | "or": connective family of a sharing chain member
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


def _is_puis_je(t: "_Tok", nxt: "_Tok | None") -> bool:
    """"puis" inverted with a hyphenated "je" is the first person of pouvoir."""
    return t.low == "puis" and nxt is not None and nxt.low == "je" and nxt.hyphen_before


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

    for i, t in enumerate(cleaned):
        if not t.is_punct:
            t.analyses, t.accentless_ambiguous = lookup(t.low)
            if _is_puis_je(t, cleaned[i + 1] if i + 1 < len(cleaned) else None):
                # "puis-je": pouvoir, present, first person singular (never the connective)
                t.analyses = [("pouvoir", frozenset({"PRES", "P1S"}))]
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
UNRESOLVED_GOVERNOR = "UNKNOWN_COMPLEMENT_GOVERNOR"
UNRESOLVED_GOVERNOR_CLASS = "unresolved_complement_governor"
# Epistemic marker of a complement whose known governor has no embedding
# contract (confirmer, expliquer, savoir... + que): not asserted, not typed.
UNRESOLVED_GOVERNANCE = "UNRESOLVED_GOVERNANCE"

# Closed-class words that can precede "que" without being a verb
# (subordinators, comparison / degree adverbs, disjunctive pronouns).
_NON_GOVERNOR_WORDS = {
    "ainsi", "bien", "tant", "aussi", "autant", "plutôt", "plutot", "même", "meme",
    "lors", "dès", "des", "pour", "afin", "tandis", "moins", "plus", "mieux", "pire",
    "tel", "telle", "tels", "telles", "moi", "toi", "lui", "eux", "ça", "cela", "ceci",
}
_PARTICIPLE_ENDINGS = ("é", "ée", "és", "ées", "i", "ie", "is", "ies", "u", "ue", "us", "ues",
                       "it", "ite", "its", "ites",
                       # irregular participles: découvert, mort, peint / craint / joint, dû
                       "ert", "erte", "erts", "ertes", "ort", "orte", "orts", "ortes",
                       "int", "inte", "ints", "intes", "û", "ûe", "ûs", "ûes")
_ANTECEDENT_PRONOUNS = {"ce", "c'", "celui", "celle", "ceux", "celles", "cela", "ça", "ca", "tout", "rien"}
_DEGREE_WORDS = {"si", "tellement", "tant", "trop", "assez", "tel", "telle", "tels", "telles"}
# Nominal / pronominal complement heads between a governor and "que":
# "parler du fait que", "tenir à ce que", "parler de ce que".
_COMPLEMENT_HEADS = {("du", "fait"), ("le", "fait"), ("de", "ce"), ("à", "ce")}


def _unresolved_governor_index(toks: list[_Tok]) -> int | None:
    """Index of a lexicon-unknown verb in verb position right before "que".

    Structural only: the word before "que" (after a "ne ... NEG" frame) has no
    lexical analysis and follows a subject pronoun, a nominal subject opening
    the clause, or an avoir/être auxiliary with a participle ending. Relatives
    (det + noun + que), clefts, restrictions and comparatives are excluded.
    """
    lows = [t.low for t in toks]
    has_ne = any(x in {"ne", "n'"} for x in lows)
    if has_ne and not any(x in _FR_NEGATORS for x in lows):
        return None  # "ne V que": restriction, not a complement
    j = len(toks) - 1
    if j >= 2 and (lows[j - 1], lows[j]) in _COMPLEMENT_HEADS:
        j -= 2  # the governor precedes the complement head ("parle du fait que")
    while has_ne and j >= 0 and lows[j] in _FR_NEGATORS:
        j -= 1
    if j < 0:
        return None
    g = toks[j]
    if (g.analyses or g.is_punct or not g.low.isalpha() or g.low in _NON_GOVERNOR_WORDS
            or g.low in _DETERMINERS or g.low in _SUBJECT_PRONOUNS or g.low in _PREPOSITIONS
            or g.low in _CONNECTIVES or g.low in _WH_WORDS):
        return None
    k = j - 1
    # Skip "ne", a "ne ... NEG" negator and clitics (se souvient, me doute, te promet).
    while k >= 0 and (lows[k] in {"ne", "n'"} or lows[k] in _REFLEXIVE_CLITICS
                      or (has_ne and lows[k] in _FR_NEGATORS)):
        k -= 1
    if k < 0:
        return None
    before = toks[k]
    if before.low in _SUBJECT_PRONOUNS:
        return j
    if _is_verb(toks, k) and _pred(before) in {"HAVE", "BE"}:
        cleft = k > 0 and lows[k - 1] in {"c'", "ce"}
        return j if g.low.endswith(_PARTICIPLE_ENDINGS) and not cleft else None
    if _is_verb(toks, k) and _cls(before) in {"modal", "aspectual"}:
        # "pourrait découvrir que", "va découvrir que": unknown infinitive governor.
        return j if g.low.endswith(_INFINITIVE_ENDINGS) else None
    if before.analyses or before.low in _DETERMINERS or before.low in _NON_GOVERNOR_WORDS:
        return None
    if k == 0 or (k == 1 and lows[0] in _DETERMINERS):
        return j
    return None


def _clause_follows(toks: list[_Tok], que_at: int) -> bool:
    """True when a verb occurs after "que" before the next clause punctuation."""
    k = que_at + 1
    while k < len(toks) and not toks[k].is_punct:
        if _is_verb(toks, k):
            return True
        k += 1
    return False


def _known_complement_governor(ctoks: list[_Tok], toks: list[_Tok], que_at: int) -> bool:
    """A lexicon-known verb without embedding contract governing "que + clause".

    Structural only: the clause's last verb is known, is neither an embedding
    verb nor an auxiliary/copula/volitive, and is followed before "que" only by
    a "ne ... NEG" negator and/or an "à + NP" indirect object, and a finite
    clause follows "que". "ne V que" stays a restriction; for governed actions
    (world_action, preparatory) "ne V pas que" keeps its "not only" reading.
    """
    v = next((k for k in range(len(ctoks) - 1, -1, -1) if _is_verb(ctoks, k)), None)
    if v is None or not ctoks[v].analyses:
        return False
    cls, pred = _cls(ctoks[v]), _pred(ctoks[v])
    if cls.startswith("embedding") or pred in {"HAVE", "BE", "WANT", "NEED"}:
        return False
    lows = [t.low for t in ctoks]
    has_ne = any(x in {"ne", "n'"} for x in lows)
    if has_ne and not any(x in _FR_NEGATORS for x in lows):
        return False
    if has_ne and cls in {"world_action", "preparatory"}:
        return False
    k = v + 1
    while has_ne and k < len(ctoks) and lows[k] in _FR_NEGATORS:
        k += 1
    tail = lows[k:]
    if tail and not (tail[0] in {"à", "au", "aux"} and len(tail) <= 4
                     and not any(_is_verb(ctoks, m) for m in range(k, len(ctoks)))):
        return False
    return _clause_follows(toks, que_at)


def _unresolved_governor_draft(toks: list[_Tok], idx: int) -> "_Draft":
    k = idx - 1
    while k >= 0 and toks[k].low in _FR_NEGATORS | {"ne", "n'"}:
        k -= 1
    aux = k >= 0 and _is_verb(toks, k) and _pred(toks[k]) in {"HAVE", "BE"}
    modal = k >= 0 and not aux and _is_verb(toks, k) and _cls(toks[k]) in {"modal", "aspectual"}
    folded = modal and _pred(toks[k]) == "GO"  # "va découvrir": aller folds into the infinitive
    head = k if aux or folded else idx  # under a modal unit, negation scope stays on the infinitive
    subj, person = _subject_before(toks, k if modal else head)
    if modal:
        # A modal keeps its own unit and governs this infinitive (see
        # _mark_governed); "aller + inf" folds into the infinitive as for known
        # verbs ("va dire" -> NEAR_FUTURE), so the future is never lost.
        tense = "NEAR_FUTURE" if folded else "NONE"
        form = "INFINITIVE"
    elif aux:
        tense = {"PRESENT": "PAST", "PAST": "PLUPERFECT", "FUTURE": "FUTURE",
                 "CONDITIONAL": "CONDITIONAL"}.get(_tense_of(_feats(toks[k])), "PAST")
        form = "PARTICIPLE"
    else:
        tense, form = "NONE", "FINITE"
    return _Draft(toks[idx], idx, head, form, tense, subject=subj, subject_person=person,
                  unresolved_governor=True)


def _last_verb(toks: list[_Tok]) -> _Tok | None:
    for i in range(len(toks) - 1, -1, -1):
        if _is_verb(toks, i):
            return toks[i]
    return None


_ELIDED_SI_SUBJECTS = {"il", "ils", "elle", "elles"}


def _politeness_formula(toks: list[_Tok], i: int) -> bool:
    """ "s'il te plaît" / "s'il vous plaît" is a politeness formula, not a protasis."""
    return (i + 3 < len(toks) and toks[i + 1].low == "il" and toks[i + 2].low in {"te", "vous"}
            and toks[i + 3].low in {"plaît", "plait"})


def _si_nominal_subject(toks: list[_Tok], i: int) -> bool:
    """ "si" + bare nominal subject (proper noun, 1-2 words) + verb opens a protasis.

    Structural: the word(s) after "si" are unknown to the lexicon and are not
    function words, and a verb follows (optionally after "ne"). Adverbial "si"
    ("si content", "si bien fait") has no verb right after its complement.
    """
    blocked = (_NON_GOVERNOR_WORDS | _DETERMINERS | _PREPOSITIONS | _WH_WORDS | _FR_NEGATORS
               | _SUBJECT_PRONOUNS | {"que", "qu'", "qui", "ne", "n'"})
    j, names = i + 1, 0
    while j < len(toks) and names < 2:
        t = toks[j]
        if t.is_punct or t.analyses or not t.low.isalpha() or t.low in blocked or t.low in _CONNECTIVES:
            break
        names += 1
        j += 1
    if names == 0:
        return False
    if j < len(toks) and toks[j].low == "et":
        # "si Nadia et Luc exécutent Q": a coordinated subject, only with a plural verb
        k = j + 1
        if k < len(toks) and toks[k].low in _DETERMINERS:
            k += 1
        conj = 0
        while k < len(toks) and conj < 2 and (toks[k].low in _TONIC_PRONOUNS or not (
                toks[k].is_punct or toks[k].analyses or not toks[k].low.isalpha()
                or toks[k].low in blocked or toks[k].low in _CONNECTIVES)):
            conj += 1
            k += 1
        while k < len(toks) and toks[k].low in {"ne", "n'"}:
            k += 1
        return conj > 0 and k < len(toks) and _is_verb(toks, k) and _plural_verb(toks[k])
    while j < len(toks) and toks[j].low in {"ne", "n'"}:
        j += 1
    return j < len(toks) and _is_verb(toks, j)


def _si_unresolved_governor(toks: list[_Tok], i: int) -> bool:
    """Clause-initial "si" + nominal subject + unknown complement governor + "que".

    "Si Marie découvre que X, ..." / "Si Marie se souvient que X, ...": the
    governor is unknown to the lexicon, so no verb follows the subject; the
    protasis is recognised through the same structural governor test as a
    main clause. Mid-clause adverbial "si" ("est si peu fiable que") is excluded.
    """
    if not (i == 0 or toks[i - 1].is_punct or toks[i - 1].low in _CONNECTIVES):
        return False
    q = i + 1
    while q < len(toks) and not toks[q].is_punct and toks[q].low not in {"que", "qu'"}:
        q += 1
    if q >= len(toks) or toks[q].low not in {"que", "qu'"} or q - i < 3:
        return False
    return _unresolved_governor_index(toks[i + 1:q]) is not None


# ── unanalyzed predicative content (M8-0b) ───────────────────────────────
# A clause whose verb the lexicon does not know yields no PredicateUnit. It is
# not non-existent: it is reported in frame.missing with its span and link.
UNANALYZED_PREDICATIVE_CONTENT = "unanalyzed_predicative_content"
_INFINITIVE_ENDINGS = ("er", "ir", "re", "oir")
_PRE_VERB_SKIP = {"ne", "n'", "y", "en", "le", "la", "les", "l'", "lui", "leur"} | _REFLEXIVE_CLITICS
_AUX_ADVERBS = {"déjà", "deja", "bien", "vraiment", "encore", "toujours", "souvent", "enfin", "aussi"}
# Constructions already analysed without a PredicateUnit ("il paraît que" -> HEARSAY).
_ANALYSED_NON_UNIT_WORDS = {"paraît", "parait"}


def _content_word(t: _Tok) -> bool:
    """A word unknown to the lexicon that is not a closed-class function word."""
    return (not t.analyses and not t.is_punct and t.low.isalpha()
            and t.low not in _NON_GOVERNOR_WORDS | _DETERMINERS | _PREPOSITIONS | _WH_WORDS
            | _FR_NEGATORS | _SUBJECT_PRONOUNS | set(_CONNECTIVES) | _ANALYSED_NON_UNIT_WORDS
            | {"que", "qui", "si"})


def _lost_verb_evidence(clause: "_Clause") -> list[tuple[int, int]]:
    """(auxiliary/modal index, unknown participle/infinitive index) pairs of the clause."""
    toks, lows = clause.toks, [t.low for t in clause.toks]
    out = []
    for k in range(len(toks)):
        if not _is_verb(toks, k) or toks[k].hyphen_before:
            continue
        pred, cls = _pred(toks[k]), _cls(toks[k])
        if pred in {"HAVE", "BE"} or cls in {"modal", "aspectual"}:
            # After an auxiliary only negators / adverbs can intervene ("n'est
            # pas parti"); object clitics may follow a modal ("peut le faire").
            if pred in {"HAVE", "BE"}:
                skip = _FR_NEGATORS | _AUX_ADVERBS
            else:
                skip = _PRE_VERB_SKIP | _FR_NEGATORS | _AUX_ADVERBS
            j = k + 1
            while j < len(toks) and lows[j] in skip:
                j += 1
            endings = _PARTICIPLE_ENDINGS if pred in {"HAVE", "BE"} else _INFINITIVE_ENDINGS
            if j < len(toks) and _content_word(toks[j]) and lows[j].endswith(endings):
                out.append((k, j))
    return out


# connectives whose clause is always expected to carry a predication: a copula +
# attribute there is reported, never dropped ("Lance P si c'est prêt")
_COPULA_REPORTED_CONNS = {"si", "que", "apres_que", "avant_que", "a_moins_que"}


def _copula_evidence(clause: "_Clause") -> list[tuple[int, int]]:
    """(finite "être" index, attribute index) pairs: "c'est prêt", "le test est vert".

    Only a finite, non-inverted "être" directly followed (after negators /
    adverbs) by a non-verbal word; presence ("est là"), "est-ce", "n'est-ce" and
    auxiliaries of a participle are not copulas here. Nothing is inferred about
    the attribute: this is evidence of an unanalysed predication only.
    """
    toks, lows = clause.toks, [t.low for t in clause.toks]
    out = []
    for k in range(len(toks)):
        if not _is_verb(toks, k) or toks[k].hyphen_before or _pred(toks[k]) != "BE" \
                or "INF" in _feats(toks[k]) or "PP" in _feats(toks[k]):
            continue
        j, adverb = k + 1, None
        while j < len(toks) and lows[j] in _FR_NEGATORS | _AUX_ADVERBS:
            adverb = j if lows[j] in _AUX_ADVERBS else adverb
            j += 1
        if j < len(toks) and not toks[j].is_punct and not toks[j].hyphen_before and not _is_verb(toks, j) \
                and lows[j] not in {"là", "ici", "here", "en"}:
            out.append((k, j))
        elif (j >= len(toks) or toks[j].is_punct) and adverb is not None:
            out.append((k, adverb))  # the adverb is the attribute: "c'est bien", "il est aussi"
    return out


_SEQUENCE_CONNECTIVES = {"et", "ou", "mais", "puis", "donc", "car", "alors"}
# demonstrative subjects: a clause they open has the shape of a subject pronoun's ("ça parle de X")
_DEMONSTRATIVE_SUBJECTS = {"ça", "ca", "cela", "ceci"}


def _unanalyzed_predicative(clause: "_Clause", in_sequence: bool = False) -> bool:
    """Structural evidence of a predication whose verb is unknown (no meaning inferred).

    Either an auxiliary / modal / aspectual verb followed by an unknown
    participle or infinitive ("est parti", "va partir", "pourrait partir"), or
    a verbless clause shaped subject + unknown word: a subject pronoun ("elle
    appelle") or a demonstrative one ("ça parle de X"), or a nominal subject where a clause is expected ("que Paul
    part", "si Paul part", or a clause of a sequence: "Paul frobnique le test
    puis lance P", "Nadia exécute Q et Paul lança P"). A standalone verbless
    utterance ("Merci Paul.", "Le test rouge.") is not a predication.
    """
    toks, lows = clause.toks, [t.low for t in clause.toks]
    skip = _PRE_VERB_SKIP | _FR_NEGATORS
    if _lost_verb_evidence(clause):
        return True
    if any(_is_verb(toks, k) for k in range(len(toks))):
        return False
    i = 1 if lows[:1] == ["si"] else 0
    if i >= len(toks):
        return False
    expected = clause.conn in {"que", "si", "quand", "wh"} or i == 1
    if lows[i] in _SUBJECT_PRONOUNS | _DEMONSTRATIVE_SUBJECTS:
        j = i + 1
    elif (expected or (in_sequence and _source_marker(clause.toks) is None)) and lows[i] not in _INTERJECTIONS:
        if lows[i] in _DETERMINERS:
            i += 1
        if i >= len(toks) or not _content_word(toks[i]):
            return False
        j = i + 1
    else:
        return False
    while j < len(toks) and lows[j] in skip:
        j += 1
    if not (j < len(toks) and _content_word(toks[j])):
        return False
    if lows[i] in _SUBJECT_PRONOUNS | _DEMONSTRATIVE_SUBJECTS or expected:
        return True
    # a sequence clause with a nominal subject: the unknown verb must introduce an
    # argument ("Paul frobnique le test"), so "et la gouvernance Obsidia" stays an NP
    # ("de / du / des" mostly open a noun complement: "le contexte historique de ce projet")
    return j + 1 < len(toks) and lows[j + 1] in (_DETERMINERS - {"de", "d'", "du", "des"}) \
        | _OBJECT_CLITICS | {"que", "qu'"}


def _content_operators(clause: "_Clause") -> list[str]:
    """Scope operators detectable around unanalyzed content (never inferred meaning)."""
    lows = [t.low for t in clause.toks]
    ops = []
    if any(x in {"ne", "n'"} for x in lows) and any(x in _FR_NEGATORS for x in lows):
        ops.append("neg")
    verbs = [t for k, t in enumerate(clause.toks) if _is_verb(clause.toks, k)]
    tenses = {_tense_of(_feats(t)) for t in verbs}
    if "FUTURE" in tenses or any(_pred(t) == "GO" for t in verbs):
        ops.append("future")
    if "CONDITIONAL" in tenses:
        ops.append("conditional_mood")
    if any(_cls(t) == "modal" for t in verbs):
        ops.append("modal")
    return ops


_EVIDENCE_NOUNS = frozenset({"logs", "log", "traces", "journaux", "résultats", "resultats", "données", "donnees",
                             "métriques", "metriques", "mesures"})


def _source_marker(toks: list[_Tok]) -> str | None:
    """Detached source / evidential adverbial clause: "selon Marie", "d'après les logs",
    "selon moi", "apparemment". Only a bare name/pronoun (human), "moi" (speaker) or a
    known trace noun (evidence) is recognised; anything else ("selon la procédure")
    stays unmarked."""
    lows = [t.low for t in toks]
    if lows == ["apparemment"]:
        return "INFERRED"
    if lows[:1] == ["selon"]:
        rest = lows[1:]
    elif lows[:2] == ["d'", "après"] or lows[:2] == ["d'", "apres"]:
        rest = lows[2:]
    else:
        return None
    if rest == ["moi"]:
        return "SPEAKER_BELIEF"
    if len(rest) == 2 and rest[0] in _DETERMINERS and rest[1] in _EVIDENCE_NOUNS:
        return "EVIDENCE_SOURCE"
    if len(rest) == 1 and rest[0].isalpha() and rest[0] not in _DETERMINERS:
        return "HUMAN_SOURCE"
    return None


def _mark_verbal_ni(clauses: list[_Clause]) -> None:
    """"Paul n'a ni lancé P ni arrêté Q": the negation is shared by the verbal ni members.

    Only when "ne" precedes the first "ni", no lexical/modal verb precedes it
    (an auxiliary may: it is shared), a verb directly follows it, and at least
    two "ni" coordinate verbs (same clause or ", ni ..." clauses). Every "ni"
    must introduce a past participle sharing the auxiliary; nominal "ni"
    (objects/subjects), bare infinitives and modal "ne doit ni ... ni" are
    left unchanged.
    """
    for k, c in enumerate(clauses):
        lows = [t.low for t in c.toks]
        if "ni" not in lows:
            continue
        f = lows.index("ni")
        if not any(x in {"ne", "n'"} for x in lows[:f]) or f + 1 >= len(lows) or not _is_verb(c.toks, f + 1):
            continue
        verbs = [j for j in range(f) if _is_verb(c.toks, j)]
        # exactly one auxiliary (members are past participles) or one
        # obligation / ability-permission / desire modal (members are infinitives),
        # shared by every member (rebuilt on each member, see _share_auxiliary);
        # a conditional one stays out of scope (negation vs. conditional mood open)
        if len(verbs) != 1:
            continue
        shared = c.toks[verbs[0]]
        # a conditional or second-person desire ("ne voudrait ni", "Ne veux-tu ni ... ?")
        # is not shared either, but its ni infinitives are never injunctive: they stay
        # open under that exact "vouloir" (negated_scope_open)
        desire = _MODALITY.get(_pred(shared)) == "DESIRE" and "IMP" not in _feats(shared)
        desire_open = desire and ("COND" in _feats(shared) or any(x in _SECOND_PERSON for x in lows))
        # "ne sait ni INF ni INF": KNOW_HOW sharing is not decided, its ni infinitives stay open too
        know_how = _MODALITY.get(_pred(shared)) == "KNOW_HOW"
        desire_open = desire_open or know_how
        ability = _MODALITY.get(_pred(shared)) == "ABILITY_OR_PERMISSION"
        # "Ne peux-tu / pourrais-tu ni P ni Q ?": negated question / reproach / suggestion: not
        # shared either, its ni infinitives stay open under that exact "pouvoir" (never injunctive)
        ability_open = ability and any(x in _SECOND_PERSON for x in lows)
        desire_open = desire_open or ability_open
        if "COND" in _feats(shared) and not (desire or know_how or ability_open):
            continue
        modal = ability or desire or know_how or _MODALITY.get(_pred(shared)) == "OBLIGATION"
        if not modal and _pred(shared) not in {"HAVE", "BE"}:
            continue
        member_feat, other_feat = ("INF", "PP") if modal else ("PP", "INF")
        group, count = [c], lows.count("ni")
        for d in clauses[k + 1:]:
            if not (d.conn is None and d.boundary == "," and d.toks and d.toks[0].low == "ni"):
                break
            group.append(d)
            count += sum(1 for t in d.toks if t.low == "ni")
        after_ni = [(g.toks, j + 1) for g in group for j, t in enumerate(g.toks) if t.low == "ni"]
        if count >= 2 and all(j < len(ts) and _is_verb(ts, j) and member_feat in _feats(ts[j])
                              and other_feat not in _feats(ts[j]) for ts, j in after_ni):
            if desire_open:
                for g in group:
                    g.ni_scope_open = shared
                continue
            for g in group:
                g.ni_head = c
            c.ni_modal = shared if modal else None


_COMPOUND_TENSE = {"PRESENT": "PAST", "PAST": "PLUPERFECT", "FUTURE": "FUTURE", "CONDITIONAL": "CONDITIONAL"}

_PERSON_FEATS = {"je": {"P1S"}, "j'": {"P1S"}, "tu": {"P2S"}, "il": {"P3S"}, "elle": {"P3S"},
                 "on": {"P3S"}, "c'": {"P3S"}, "ça": {"P3S"}, "ca": {"P3S"}, "cela": {"P3S"},
                 "nous": {"P1P"}, "vous": {"P2P"}, "ils": {"P3P"}, "elles": {"P3P"}}
# connectives after which a bare verb's subject stays open ("R si Paul lance P et exécute Q")
_NO_SUBJECT_SHARE = {"que", "rel", "comparative", "si", "sans", "sans_que", "avant_que", "a_moins_que", "apres_que",
                     "quand", "wh"}
# subordinates that never lend their auxiliary / modal / periphrasis to a following clause
_NO_CHAIN_SHARE = {"que", "rel", "comparative", "apres_que", "quand", "wh"}


def _agrees_with_subject(tok: _Tok, host: "_Draft") -> bool:
    """A subject-less present verb takes the host's subject only when its person
    agrees ("Paul ... et exécute Q", "Les tests ... et exécutent Q"); a form of another
    person never does ("Paul ... et exécutez / exécutent Q"). For a form without an
    imperative reading, a nominal subject's number is read on the host's own finite
    verb when it carries one (NF4: agreement required, no proximity fallback, no
    automatic subject fusion); imperative-ambiguous forms keep the P1 contract."""
    feats = _feats(tok)
    if "EN" in feats or "PRES" not in feats:
        return False
    want = _PERSON_FEATS.get(host.subject)
    if want is None and host.subject_person == "3":
        own = _feats(host.lex) & {"P3S", "P3P"} if host.verb_form == "FINITE" and "IMP" not in feats else set()
        want = own or {"P3S", "P3P"}
    return bool((want or set()) & feats)


def _share_auxiliary(clauses: list[_Clause], ci: int, drafts: list) -> None:
    """One written auxiliary shared by coordinated past participles.

    "Paul a lancé et exécuté le test", "Paul a lancé, exécuté et arrêté le
    test": a bare participle clause (no subject, no auxiliary) coordinated by
    "et" / "," right after a main clause ending in AUX+PP takes that compound
    tense. "ne AUX ni PP1 ni PP2": every ni member takes the auxiliary's
    compound tense. Ambiguous attachments (after a complement or a relative)
    never share.
    """
    clause = clauses[ci]
    if clause.ni_head is not None and clause.ni_head.ni_modal is not None:
        # "ne doit ni INF1 ni INF2" / "ne peut ni INF1 ni INF2": the modal (its
        # modality, tense, subject) is shared by the infinitives; its own finite
        # draft is folded into them, exactly as in "ne doit pas INF".
        head = clause.ni_head
        if clause is head:
            finite = [d for d in drafts if d.lex is head.ni_modal and d.verb_form == "FINITE"]
            if not finite:
                return
            head.ni_modal = finite[0]
            drafts.remove(finite[0])
        m = head.ni_modal
        if isinstance(m, _Draft):
            for d in drafts:
                if d.head_index > 0 and clause.toks[d.head_index - 1].low == "ni" \
                        and d.verb_form == "INFINITIVE" and d.modality is None and d.subject is None:
                    d.modality, d.modal_tok, d.tense = _MODALITY.get(_pred(m.lex)), m.lex, m.tense
                    # same rule as the modal+infinitive chain: "falloir" is impersonal
                    d.subject = m.subject
                    d.subject_person = "impersonal" if _pred(m.lex) == "NEED" else m.subject_person
        return
    if clause.ni_head is not None:
        head = clause.ni_head
        lows = [t.low for t in head.toks]
        aux = [t for t in head.toks[:lows.index("ni")] if t.analyses and _pred(t) in {"HAVE", "BE"}]
        tense = _COMPOUND_TENSE.get(_tense_of(_feats(aux[0])), "PAST") if aux else None
        for d in drafts:
            if tense and d.head_index > 0 and clause.toks[d.head_index - 1].low == "ni" \
                    and d.verb_form == "PARTICIPLE" and d.tense == "NONE":
                d.tense = tense
    elif ci > 0 and drafts and not clause.attachment_ambiguous and clause.protasis_head is None:
        prev, d0 = clauses[ci - 1], drafts[0]
        conns = [x.low for x in clause.conn_toks]
        linked = conns == ["et"] or (clause.conn is None and clause.boundary == ",")
        # "puis" / "mais" coordinate the same way; under a negated host ("ne ... pas P
        # mais Q") a shared auxiliary / modal / periphrasis would decide the held
        # negative scope, so only the finite subject (own inflection) is shared there
        sequenced = clause.conn in {"puis", "mais"} and bool(conns) \
            and set(conns) <= {"et", "puis", "ensuite", "mais"}
        # "ou" shares the same structure over a disjunction (group kind OR); one chain
        # never mixes "et" and "ou" members (their precedence is not decided), a comma
        # member takes the chain's family
        disjoined = clause.conn == "ou" and conns == ["ou"]
        family = "or" if disjoined else prev.share_family if not conns else "and"
        same_family = prev.share_family in (None, family)
        negated_host = any(t.low in {"ne", "n'"} for t in prev.toks)
        chained = same_family and (linked or ((sequenced or disjoined) and not negated_host))
        if chained and prev.compound is not None and prev.conn not in _NO_CHAIN_SHARE \
                and d0.head_index == d0.lex_index == 0 and d0.verb_form == "PARTICIPLE" \
                and d0.tense == "NONE" and d0.subject is None:
            d0.tense = prev.compound[0]
            clause.compound = (prev.compound[0], prev.compound[1], d0)
            clause.shared_aux_host = prev.shared_aux_host or prev
            clause.share_family = family
            return
        # "Paul doit lancer P et exécuter Q": the obligation modal chain (the modal,
        # its tense, its subject) is shared by a bare coordinated infinitive;
        # "Veuillez lancer P et exécuter Q": so is the directive operator's scope;
        # "Peux-tu lancer P et exécuter Q ?": so is the ability-permission modal
        if chained and prev.modal is not None and prev.conn not in _NO_CHAIN_SHARE \
                and _bare_infinitive(clause, d0) \
                and d0.modality is None and d0.subject is None:
            m = prev.modal
            d0.modality, d0.modal_tok, d0.tense = m.modality, m.modal_tok, m.tense
            d0.subject, d0.subject_person, d0.politeness = m.subject, m.subject_person, m.politeness
            d0.directive, d0.compound_modal = m.directive, m.compound_modal
            clause.modal = m
            clause.shared_modal_host = prev.shared_modal_host or prev
            clause.share_family = family
            return
        # "Paul ne veut / peut / va pas lancer P et / puis / ou / mais / , exécuter Q": the
        # bare infinitive stays open under that exact negated operator unit, no polarity chosen
        open_host = prev.neg_scope_open
        if open_host is not None and same_family \
                and (linked or disjoined or sequenced) \
                and prev.conn not in _NO_CHAIN_SHARE \
                and _bare_infinitive(clause, d0) \
                and d0.modality is None and d0.subject is None:
            d0.governed = "negated_scope_open"
            d0.governor_span = (open_host.lex.start, open_host.lex.end)
            clause.neg_scope_open = open_host
            clause.share_family = family
            return
        # "Paul aime / vient lancer P et exécuter Q": after an infinitive governed by an
        # unrecognised word, the bare infinitive continues that content or is independent;
        # it is never an injunction: it takes the same open contract (named)
        gov_prev = prev.units[-1][1] if prev.units else None
        if gov_prev is not None and gov_prev.governed == "unknown_governor" and same_family \
                and (linked or disjoined or sequenced) and prev.conn not in _NO_CHAIN_SHARE \
                and _bare_infinitive(clause, d0) and d0.modality is None and d0.subject is None:
            d0.governed = "unknown_governor"
            clause.share_family = family
            return
        # "Paul sait lancer P et exécuter Q": KNOW_HOW sharing is not decided; the bare
        # infinitive stays open under that exact savoir unit (know_how_scope_open)
        open_host = prev.know_how_open
        if open_host is not None and same_family and (linked or disjoined or sequenced) \
                and prev.conn not in _NO_CHAIN_SHARE \
                and _bare_infinitive(clause, d0) \
                and d0.modality is None and d0.subject is None:
            d0.governed = "know_how_scope_open"
            d0.governor_span = (open_host.lex.start, open_host.lex.end)
            clause.know_how_open = open_host
            clause.share_family = family
            return
        # "Paul lance P et exécute Q": a bare present verb agreeing with the host's
        # explicit subject shares that subject; it is never an imperative
        host = prev.subject_host
        if same_family and (linked or sequenced or disjoined) and host is not None \
                and prev.conn not in _NO_SUBJECT_SHARE \
                and d0.head_index == d0.lex_index == 0 and d0.verb_form in {"IMPERATIVE", "FINITE"} \
                and d0.subject is None and d0.modality is None and _agrees_with_subject(d0.lex, host):
            d0.verb_form, d0.tense = "FINITE", _tense_of(_feats(d0.lex))
            d0.subject, d0.subject_person = host.subject, host.subject_person
            d0.governed = None
            clause.subject_host = host
            clause.shared_subject_host = prev.shared_subject_host or prev
            clause.share_family = family
            return
        # "Paul lance P et exécutent Q": no agreement, and the form has no imperative
        # reading: never shared, never an imperative; the subject stays unresolved (named)
        if same_family and (linked or sequenced or disjoined) \
                and (host is not None or prev.subject_unresolved_chain) \
                and prev.conn not in _NO_SUBJECT_SHARE \
                and d0.head_index == d0.lex_index == 0 and d0.verb_form in {"IMPERATIVE", "FINITE"} \
                and d0.subject is None and d0.modality is None \
                and {"PRES"} <= _feats(d0.lex) and not {"IMP", "EN"} & _feats(d0.lex):
            d0.verb_form, d0.tense = "FINITE", _tense_of(_feats(d0.lex))
            d0.governed = "subject_unresolved"
            clause.subject_unresolved_chain = True
            clause.share_family = family
            return
        # "Paul lance P et ne pas exécuter Q": no host operator licenses the negated bare
        # infinitive; it is never an independent prohibition (NO_EXECUTE), only named
        host = prev.subject_host
        if same_family and (linked or sequenced or disjoined) and host is not None \
                and host.modality is None and not host.directive and host.tense not in _PERIPHRASES \
                and prev.conn not in _NO_CHAIN_SHARE and _bare_infinitive(clause, d0) and d0.head_index > 0 \
                and d0.modality is None and d0.subject is None:
            d0.governed = "unknown_governor"
            clause.share_family = family
            return
    compound = [d for d in drafts if d.verb_form == "PARTICIPLE" and d.head_index != d.lex_index]
    if compound and compound[-1] is drafts[-1]:
        clause.compound = (compound[-1].tense, clause.toks[compound[-1].head_index].low, compound[-1])
    last = drafts[-1] if drafts else None
    if last is not None and last.subject is not None and not last.inverted \
            and last.subject_person in {"1", "2", "3"} and last.verb_form != "IMPERATIVE":
        clause.subject_host = last
    # a negated "pouvoir" / "vouloir" ("ne peut pas P et Q": ¬(P∧Q) or ¬P∧¬Q) or one
    # inside a protasis ("R si tu peux P et Q") has no safe scope over a coordination
    # "Paul va lancer P et exécuter Q": the near-future periphrasis (tense, subject) is
    # shared like a modal chain; a negated one stays open like a negated "pouvoir"
    # (so are "venir de" RECENT_PAST and "être en train de" PROGRESSIVE)
    near_future = last is not None and last.modality is None and not last.directive \
        and last.tense in {"NEAR_FUTURE", "RECENT_PAST", "PROGRESSIVE"} and last.subject is not None
    negated_head = last is not None and any(t.low in {"ne", "n'"} for t in clause.toks[:last.head_index])
    scope_open = last is not None and (last.modality in {"ABILITY_OR_PERMISSION", "DESIRE"} or near_future) \
        and (clause.conn == "si" or negated_head)
    # "Paul ne doit pas lancer P et exécuter Q": a negated obligation is never shared as a
    # positive one (nor its negation copied): its scope over Q stays open too (G2)
    scope_open = scope_open or (last is not None and last.modality == "OBLIGATION" and negated_head
                                and clause.conn != "si")
    # "Paul ne veut / peut / va pas lancer P et exécuter Q": ¬(P∧Q), ¬P∧¬Q or ¬P∧Q stays
    # held, but in every reading Q is that operator's content, never an injunction
    # (negated_scope_open)
    if scope_open and clause.conn != "si" and last.verb_form == "INFINITIVE" \
            and last.head_index != last.lex_index and last.modal_tok is not None:
        clause.neg_scope_open = last
    if last is not None and clause.conn != "si" and last.modality == "KNOW_HOW" and last.verb_form == "INFINITIVE" \
            and last.head_index != last.lex_index and last.modal_tok is not None:
        clause.know_how_open = last
    if last is not None and (last.modality in {"OBLIGATION", "ABILITY_OR_PERMISSION", "DESIRE"}
                             or last.directive or near_future) \
            and not scope_open and last.verb_form == "INFINITIVE" \
            and last.head_index != last.lex_index and last.modal_tok is not None:
        clause.modal = last


_PERIPHRASES = {"NEAR_FUTURE", "RECENT_PAST", "PROGRESSIVE"}
_MEMBER_NEGATORS = {"ne", "n'", "pas", "plus", "jamais"}


def _bare_infinitive(clause: _Clause, d0: "_Draft") -> bool:
    """A subject-less infinitive opening its clause, possibly after its own negation
    ("et exécuter Q", "et ne pas exécuter Q": the negation stays local to the member)."""
    return d0.verb_form == "INFINITIVE" and d0.head_index == d0.lex_index \
        and all(t.low in _MEMBER_NEGATORS for t in clause.toks[:d0.head_index])


def _share_kind(sharers: list[_Clause]) -> str:
    """Kind of a sharing group: OR when its members are joined by "ou" (never mixed with "et")."""
    return "OR" if any(c.conn == "ou" for c in sharers) else "AND"


def _is_complement(clause: _Clause) -> bool:
    return clause.conn == "que" or (clause.conn == "rel" and clause.governor_lost)


def _coordinated_complement(clauses: list[_Clause]) -> tuple[_Clause | None, bool]:
    """"V que P et que Q" / "V que P ou que Q": (the complement P that Q coordinates with, ambiguous).

    P is a "que" complement, or one whose governor was lost (Q then shares that
    unknown governance). Only for a unique syntactic governor: when P's governor
    is itself a "que" complement, Q could complement either governor, and the
    attachment stays ambiguous.
    """
    if len(clauses) < 2:
        return None, False
    c, prev = clauses[-1], clauses[-2]
    if c.toks or c.conn not in {"et", "ou"} or not _is_complement(prev):
        return None, False
    if prev.attachment_ambiguous:
        return None, True
    gov = prev.embedding_parent
    if gov is None or not 0 <= gov < len(clauses) - 2:
        return None, False
    if clauses[gov].conn == "que":
        return None, True
    return prev, False


_WH_COMPLEMENT_WORDS = {"quand", "comment", "pourquoi", "où", "combien"}
_HYPHEN_OBJECT_PRONOUNS = {"moi", "toi", "lui", "nous", "vous", "leur", "le", "la", "les"}
_TONIC_PRONOUNS = {"moi", "toi", "lui", "elle", "nous", "vous", "eux", "elles"}
_SUBJECT_INTRODUCERS = {"si", "que", "qu'", "comme", "dès", "pendant", "lorsque", "lorsqu'", "quand", "depuis"}
_PLURAL_AUX = {"ont", "sont", "vont", "avons", "sommes", "allons", "avez", "êtes", "allez", "font", "doivent",
               "peuvent", "veulent", "savent", "viennent"}


def _bare_noun_phrase(ts: list) -> bool:
    """An optional determiner and one or two unknown content words ("Nadia", "le test")."""
    words = [t for t in ts if t.low not in _DETERMINERS]
    return bool(words) and len(ts) - len(words) <= 1 and len(words) <= 2 \
        and all(_content_word(t) and not t.hyphen_before for t in words)


def _plural_verb(tok) -> bool:
    return bool(_feats(tok) & {"P1P", "P2P", "P3P"}) or tok.low in _PLURAL_AUX


def _wh_complement_governor(toks: list[_Tok], i: int) -> "_Tok | None":
    """The verb governing a WH complement ("Je sais quand P", "Dis-moi comment P"): only the
    verb right before the WH word (or before its hyphenated pronoun), and only when a finite
    clause follows ("Dis-moi comment lancer P" stays a WH infinitive)."""
    if toks[i].low not in _WH_COMPLEMENT_WORDS or i == 0 or i + 1 >= len(toks):
        return None
    nxt = toks[i + 1]
    if nxt.is_punct or nxt.low in {"même", "meme"} or _is_verb(toks, i + 1):
        return None
    g = i - 1
    if toks[g].hyphen_before and toks[g].low in _HYPHEN_OBJECT_PRONOUNS:
        g -= 1
    if g < 0 or not _is_verb(toks, g):
        return None
    for j in range(i + 2, len(toks)):
        if toks[j].low in {".", "!", "?", ";", ","}:
            return None
        if _is_verb(toks, j):
            return toks[g]
    return None


def _subordinating_quand(toks: list[_Tok], i: int) -> bool:
    """"quand" opening a subordinate clause, not an interrogative or idiomatic one.

    Not: "quand même", "quand" followed by a verb ("Quand lances-tu P ?",
    "Quand est-ce que ..."), after a preposition ("depuis quand", "n'importe
    quand") or right after a verb / hyphenated pronoun (indirect question:
    "Dis-moi quand P", "Je sais quand P"). A clause-initial "quand" is one only
    when a comma follows it in the sentence ("Quand Q, P"; "Quand Paul lance-t-il
    P ?" stays a question).
    """
    nxt = toks[i + 1] if i + 1 < len(toks) else None
    if nxt is None or nxt.is_punct or nxt.low in {"même", "meme"} or _is_verb(toks, i + 1):
        return False
    prev = toks[i - 1] if i > 0 else None
    if prev is None or prev.is_punct or prev.low in _CONNECTIVES:
        for t in toks[i + 1:]:
            if t.low == ",":
                return True
            if t.low in {".", "!", "?", ";", ":"}:
                return False
        return False
    if prev.low in _PREPOSITIONS | {"depuis", "importe", "jusqu'", "jusqu'à"} or prev.hyphen_before:
        return False
    return not _is_verb(toks, i - 1)


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
            cur().boundary = low
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
        # "après que Q": a temporal subordinate (Q before its host), never a relative
        if low in {"après", "apres"} and nxt is not None and nxt.low in {"que", "qu'"} \
                and not (cur().toks and cur().toks[-1].low == "d'"):
            open_clause("apres_que", [t, nxt])
            i += 2
            continue
        # "Je sais quand P", "Dis-moi comment P": a WH complement of the adjacent verb
        gov = _wh_complement_governor(toks, i)
        if gov is not None:
            open_clause("wh", [t])
            cur().wh_governor = gov
            i += 1
            continue
        # "quand" / "lorsque" Q: a temporal subordinate whose meaning stays held
        if low in _TEMPORAL_INTRODUCERS or (low == "quand" and _subordinating_quand(toks, i)):
            open_clause("quand", [t])
            i += 1
            continue
        # "d'après X" is a source adverbial, never the temporal connective.
        if low in {"après", "apres"} and cur().toks and cur().toks[-1].low != "d'":
            open_clause("apres", [t])
            i += 1
            continue

        # "puis-je" is pouvoir, not the connective.
        if _is_puis_je(t, nxt):
            cur().toks.append(t)
            i += 1
            continue

        # Elided conditional "si" before il/ils/elle/elles: "s'il", "s'ils".
        if low == "s'" and nxt is not None and nxt.low in _ELIDED_SI_SUBJECTS                 and not _politeness_formula(toks, i):
            open_clause("si", [t])
            i += 1
            continue

        if low in {"si", "if"}:
            if nxt is not None and (nxt.low in _SUBJECT_PRONOUNS | _DETERMINERS
                                    or nxt.low in {"c'", "ça", "ca", "it"}
                                    or _si_nominal_subject(toks, i)
                                    or _si_unresolved_governor(toks, i)):
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
            if not c.toks and c.conn == "et" and len(clauses) >= 2 and clauses[-2].conn == "si":
                # "si P et que Q": "que" takes up "si"; Q joins the protasis.
                c.conn, c.conn_toks = "si", c.conn_toks + [t]
                i += 1
                continue
            sibling, ambiguous = _coordinated_complement(clauses)
            if sibling is not None:
                c.conn, c.conn_toks, c.governor_lost = sibling.conn, c.conn_toks + [t], sibling.governor_lost
                c.embedding_parent, c.coordinated_with = sibling.embedding_parent, sibling
                i += 1
                continue
            if ambiguous:
                c.conn, c.conn_toks, c.attachment_ambiguous = "que", c.conn_toks + [t], True
                i += 1
                continue
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
            governor_at = None if embedding else _unresolved_governor_index(c.toks)
            if embedding:
                open_clause("que", [t], parent=len(clauses) - 1)
            elif governor_at is not None:
                c.unresolved_governor = governor_at
                open_clause("que", [t], parent=len(clauses) - 1)
            elif _known_complement_governor(c.toks, toks, i):
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
                # A relative "que" follows a nominal antecedent (det + noun, "ce").
                # Otherwise the governor of this complement could not be
                # recognised; it must stay subordinated (see pragmatics).
                # Clefts ("c'est Paul que") and degree consecutives ("si rapide
                # que") are not complements either.
                lows_c = [x.low for x in c.toks]
                nominal = prev is None or prev.low in _ANTECEDENT_PRONOUNS or (
                    len(c.toks) >= 2 and c.toks[-2].low in _DETERMINERS) or bool(
                    {"c'", "ce"} & set(lows_c) or _DEGREE_WORDS & set(lows_c[1:]))
                open_clause("rel", [t], parent=len(clauses) - 1)
                cur().governor_lost = not nominal
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
    lost_complement = False
    pending_source = None
    for c in clauses:
        has_verb = c.unresolved_governor is not None or any(
            _is_verb(c.toks, k) for k in range(len(c.toks)))
        # A clause opened by punctuation (conn None) holding only a source adverbial:
        # clause-initial ("Selon Marie, P") marks the next clause, clause-final
        # ("P, selon Marie") the previous one.
        marker = _source_marker(c.toks) if c.conn is None else None
        if marker is not None and merged and merged[-1].units == [] and any(
                _is_verb(merged[-1].toks, k) for k in range(len(merged[-1].toks))):
            merged[-1].evidential = merged[-1].evidential or marker
        elif marker is not None and not merged:
            pending_source = marker
        if marker is None and has_verb and c.conn is None and pending_source is not None:
            c.evidential, pending_source = pending_source, None
        # A verbless clause shaped like a predication with an unknown verb
        # ("elle appelle Luc") is kept as its own (unanalyzed) clause, and so is
        # a verbless "quand / lorsque" subordinate ("lorsque Nadia et Luc V").
        if not has_verb and merged and c.conn not in {"sans", "sans_que", "quand", "wh"} \
                and not _unanalyzed_predicative(c, in_sequence=c.conn in _SEQUENCE_CONNECTIVES
                                                or (c.conn is None and c.boundary == ",")):
            prev = merged[-1]
            prev.toks += c.conn_toks + c.toks
            # "V que le test que P V2": the complement opener only held its
            # subject NP; the relative that follows also carries V2.
            lost_complement = _is_complement(c)
            continue
        c.complement_structure_lost = lost_complement and c.conn == "rel"
        lost_complement = False
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
    governor_span: tuple | None = None   # exact governor token of a negated_scope_open infinitive
    unresolved_governor: bool = False    # unknown verb kept only as a "que" governor
    directive: bool = False              # under a written directive operator ("veuillez" + inf)
    compound_modal: bool = False         # "a pu / a dû / a voulu V": compound-tense modal chain


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
        # nominal subject ("maman", "le script"); it never extends across a WH word
        # or a temporal introducer ("P quand Nadia exécute Q": the subject is "nadia")
        j = k
        while j > 0 and not toks[j - 1].analyses and toks[j - 1].low not in (
                _PREPOSITIONS | _SUBJECT_PRONOUNS | _WH_WORDS | _TEMPORAL_INTRODUCERS | {"ne", "n'"}):
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
                                             subject=subj, subject_person=person, modal_tok=t))
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
                if _MODALITY.get(_pred(lex)) is not None:
                    # "a voulu / a pu / a dû / a su / a fallu" + infinitive: one modal chain in
                    # a compound tense (its occurrence is held, see modal_past_occurrence_open)
                    w = _next_verb(toks, v + 1, skip)
                    if w is not None and "INF" in _feats(toks[w]) and "PP" not in _feats(toks[w]):
                        drafts.append(_Draft(
                            toks[w], w, k, "INFINITIVE", _COMPOUND_TENSE.get(_tense_of(feats), "PAST"),
                            modality=_MODALITY[_pred(lex)], modal_tok=lex, subject=subj,
                            subject_person="impersonal" if _pred(lex) == "NEED" else person,
                            inverted=inverted, compound_modal=True))
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
                                     subject=subj, subject_person=person, modal_tok=t))
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
                                         subject=subj, subject_person=person, modal_tok=t))
                    consumed.update({k, v})
                    k = v + 1
                    continue
            v = _next_verb(toks, after, skip)
            if v is not None and person in {"1", "3"} and "INF" in _feats(toks[v]) and "PP" not in _feats(toks[v]):
                # "Paul (ne) vient (pas) lancer P": venir + infinitive has no construction here;
                # the infinitive is content of that unrecognised governor, never an injunction
                drafts.append(_Draft(toks[v], v, v, "INFINITIVE", governed="unknown_governor"))
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
                # "veuillez" + inf: polite directive operator, not a desire modality
                polite = pred == "WANT" and "IMP" in feats and subj is None
                d = _Draft(toks[v], v, k, form, _tense_of(feats),
                           modality=None if polite else _MODALITY.get(pred), modal_tok=t,
                           politeness=polite or "COND" in feats or t.low == "could",
                           subject=subj, subject_person=person, inverted=inverted,
                           directive=polite)
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

        form, unresolved_subject = "FINITE", False
        prev = toks[k - 1] if k > 0 else None
        if "INF" in feats and (not ({"PRES", "IMP", "PP"} & feats)
                               or (prev is not None and prev.low in {"de", "d'", "à", "to", "pas", "rien"})):
            form = "INFINITIVE"
        elif "PPR" in feats and not ({"PRES", "IMP", "INF"} & feats):
            form = "GERUND"
        elif subj is None and "PRES" in feats and not ({"IMP", "EN", "P1P", "P2P"} & feats) \
                and has_imperative_paradigm(_lemma(t)):
            # no subject is not a proof of imperative: "Exécutent Q.", "Font Q." have no
            # imperative reading in a known paradigm; the subject stays unresolved (a 1st /
            # 2nd plural present is always a possible imperative: "Disons Q.")
            form, unresolved_subject = "FINITE", True
        elif subj is None and ({"IMP", "PRES", "INF"} & feats):
            form = "IMPERATIVE"
        elif subj is None and "PP" in feats:
            form = "PARTICIPLE"
        drafts.append(_Draft(t, k, k, form, "NONE" if form in {"IMPERATIVE", "INFINITIVE"}
                             else _tense_of(feats), subject=subj, subject_person=person,
                             inverted=inverted,
                             governed="subject_unresolved" if unresolved_subject else None))
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

    # verbal "ne ... ni V1 ni V2": the member directly after "ni" is negated by
    # the shared ni coordination (see _mark_verbal_ni), not by another member.
    if clause.ni_head is not None and lo > 0 and lows[lo - 1] == "ni":
        out.update(polarity="negative", negator="ni", negation_confirmed=True)
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
    _mark_verbal_ni(clauses)
    # "Si P et Q, R" / "si P et que Q" / "si P et si Q": one conjunctive protasis.
    # A bare "et Q" joins only a sentence-initial protasis ("R si P et Q" stays open).
    for k in range(1, len(clauses)):
        prev, clause = clauses[k - 1], clauses[k]
        if prev.conn != "si" or clause.boundary is not None or not clause.conn_toks \
                or clause.conn_toks[0].low != "et":
            continue
        head = prev.protasis_head or prev
        hi = next(j for j, c in enumerate(clauses) if c is head)
        preposed = hi == 0 or head.boundary in {".", "!", "?", ";", ":"}
        if clause.conn == "si" or (clause.conn == "et" and preposed):
            clause.conn, clause.protasis_head, head.protasis_head = "si", head, head
    # "V que P et Q": Q coordinates inside the complement or with its host.
    # "V que P parce que Q" / "V que P donc Q": the cause / consequence may bear on P
    # (inside the complement) or on V; within one sentence it is never bound to the
    # nearest host. "P quand Q et R": R may continue Q or P (never the nearest either)
    for prev, clause in zip(clauses, clauses[1:]):
        causal = clause.conn in {"car", "donc"} and clause.boundary not in {".", "!", "?", ";"}
        if (clause.conn in {"et", "ou"} or causal) and (_is_complement(prev) or prev.evidential is not None
                                                        or prev.conn in {"quand", "wh"}):
            clause.attachment_ambiguous = True
    if any(t.hyphen_before and t.low in _SUBJECT_PRONOUNS for t in toks):
        interrogative = True

    units: list[PredicateUnit] = []
    relations: list[LatticeRelation] = []
    coordinations: list[CoordinationRef] = []
    ambiguities: list[str] = []
    deixis = [t.low for t in toks if t.low in _DEIXIS and not t.hyphen_before]
    counter = 0

    for ci, clause in enumerate(clauses):
        drafts = _build_drafts(clause.toks)
        if clause.unresolved_governor is not None:
            drafts.append(_unresolved_governor_draft(clause.toks, clause.unresolved_governor))
        _share_auxiliary(clauses, ci, drafts)
        for d in drafts:
            counter += 1
            if d.unresolved_governor:
                # Unknown to the lexicon: no lemma, no meaning, only structure.
                lemma, pred, pcls = d.lex.low, UNRESOLVED_GOVERNOR, UNRESOLVED_GOVERNOR_CLASS
            else:
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

    # clause -> (governor unit, host clause), reused by a coordinated sibling
    resolved: dict[int, tuple[PredicateUnit | None, _Clause | None]] = {}
    complement_alternatives: list[list[PredicateUnit]] = []
    for ci, clause in enumerate(clauses):
        parent_unit, host = None, clauses[ci - 1] if ci > 0 else None
        if clause.coordinated_with is not None and id(clause.coordinated_with) in resolved:
            parent_unit, host = resolved[id(clause.coordinated_with)]
        else:
            if clause.embedding_parent is not None and clause.embedding_parent < ci:
                parent_unit = last_of(clause.embedding_parent)
            # embedding parent may have been merged; fall back to previous clause
            if clause.conn in {"que", "rel", "comparative"} and parent_unit is None and ci > 0:
                parent_unit = last_of(ci - 1)
        resolved[id(clause)] = (parent_unit, host)
        new_units = []
        for n, (u, d) in enumerate(clause.units):
            prag, epi, realized = u.pragmatic, "NOT_APPLICABLE", None
            embedded_under = None
            if prag == "NOT_REQUIRED":
                new_units.append((u, d))
                continue
            if clause.conn in {"sans", "sans_que"} and n == 0:
                prag = "FORBIDDEN"
            elif clause.complement_structure_lost:
                # Relative and complement predicate share a clause whose complement
                # structure was lost: subordinated under the governor, unknown
                # governance, never an asserted relative of the governor.
                prag, epi = "EMBEDDED", UNRESOLVED_GOVERNANCE
                ambiguities.append(f"complement_structure_lost:{u.id}")
                if parent_unit is not None:
                    embedded_under = parent_unit.id
                    relations.append(LatticeRelation(RelationKind.EMBEDS.value, parent_unit.id, u.id,
                                                     evidence="que_governor_lost"))
            elif clause.attachment_ambiguous and n == 0:
                # Several attachments stay open: never the nearest governor,
                # never a root assertion.
                prag, epi = "EMBEDDED", UNRESOLVED_GOVERNANCE
                ambiguities.append(f"coordination_attachment_ambiguous:{u.id}")
            elif clause.conn == "que" and parent_unit is None and n == 0 and host is not None and any(
                    t.low in {"paraît", "parait"} for t in host.toks):
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
                elif pp == UNRESOLVED_GOVERNOR:
                    # Governor meaning unknown: the complement is neither asserted
                    # nor reported/believed/denied; it is only subordinated.
                    prag, epi, kind = "EMBEDDED", "NOT_APPLICABLE", RelationKind.EMBEDS
                    ambiguities.append(f"complement_under_unresolved_governor:{u.id}")
                elif pp in {"WANT", "NEED"}:
                    speaker_wants = pp == "NEED" or parent_unit.subject in _FIRST_PERSON
                    prag = "REQUESTED" if speaker_wants else "REPORTED"
                    if u.polarity == "negative" and speaker_wants:
                        prag = "FORBIDDEN"
                    kind = RelationKind.WANTS
                else:
                    # Known governor without an embedding contract: the complement
                    # is subordinated, never promoted to a root assertion.
                    prag, epi, kind = "EMBEDDED", UNRESOLVED_GOVERNANCE, RelationKind.EMBEDS
                    ambiguities.append(f"unresolved_complement_governance:{u.id}")
                relations.append(LatticeRelation(
                    kind.value, parent_unit.id, u.id,
                    evidence="que_unresolved_governance" if epi == UNRESOLVED_GOVERNANCE else "que"))
            elif clause.conn in {"avant_que", "a_moins_que"} and n == 0:
                prag, epi = "HYPOTHETICAL", "HYPOTHETICAL"
            elif clause.conn == "apres_que" and n == 0:
                # temporal context of its host, presupposed by the construction, not asserted
                # (the finite counterpart of "après avoir V")
                prag, epi = "EMBEDDED", "NOT_APPLICABLE"
                d.governed = "temporal"
            elif clause.conn == "wh":
                # WH complement: subordinated under its adjacent governor; its commitment
                # (presupposed, mentioned, asked) is not decided
                prag, epi = "EMBEDDED", UNRESOLVED_GOVERNANCE
                ambiguities.append(f"unresolved_complement_governance:{u.id}")
                wg = clause.wh_governor
                gov = next((x for c2 in clauses for (x, _) in (new_units if c2 is clause else c2.units)
                            if x.span == (wg.start, wg.end)), None)
                if gov is not None:
                    embedded_under = gov.id
                    relations.append(LatticeRelation(RelationKind.EMBEDS.value, gov.id, u.id,
                                                     evidence="wh_unresolved_governance"))
            elif clause.conn == "quand":
                # "quand / lorsque Q": order, simultaneity, habit or condition is a held
                # doctrine: Q is subordinated, never asserted, no relation and no host chosen
                prag, epi = "EMBEDDED", UNRESOLVED_GOVERNANCE
                ambiguities.append(f"temporal_subordinate_open:{u.id}")
            elif clause.conn == "si" and n == 0:
                prag, epi = "HYPOTHETICAL", "HYPOTHETICAL"
            elif clause.conn == "rel" and clause.governor_lost and n == 0:
                # "que" complement whose governor could not be built ("se rend
                # compte que", "pourrait se rendre compte que"): subordinated
                # content of unknown governance, never a root assertion nor a
                # relative asserted under whatever unit precedes it.
                prag, epi = "EMBEDDED", UNRESOLVED_GOVERNANCE
                ambiguities.append(f"complement_governor_lost:{u.id}")
                if parent_unit is not None:
                    embedded_under = parent_unit.id
                    relations.append(LatticeRelation(RelationKind.EMBEDS.value, parent_unit.id, u.id,
                                                     evidence="que_governor_lost"))
            elif clause.conn in {"rel", "comparative"}:
                prag, epi = "ASSERTED", "ASSERTED"
                if parent_unit is not None:
                    embedded_under = parent_unit.id
                    relations.append(LatticeRelation(RelationKind.EMBEDS.value, parent_unit.id,
                                                     u.id, evidence=clause.conn))
            elif d.governed == "subject_unresolved":
                # "Paul lance P et exécutent Q": the predicate is kept, its subject is not
                # the host's (no agreement) and is not known: never asserted, never requested
                prag, epi = "EMBEDDED", UNRESOLVED_GOVERNANCE
                ambiguities.append(f"subject_unresolved:{u.id}")
            elif d.governed == "unknown_governor":
                # content of an unrecognised finite governor: no subject taken from it, no request
                prag, epi = "EMBEDDED", "NOT_APPLICABLE"
                ambiguities.append(f"infinitive_under_unrecognized_governor:{u.id}")
                u, d.subject_person = replace(u, subject=None), None
            elif d.governed in {"negated_scope_open", "know_how_scope_open"}:
                # an infinitive under a negated operator (or a savoir chain) whose scope over
                # it is not established: its content, never an injunction, no polarity chosen
                prag, epi = "EMBEDDED", "NOT_APPLICABLE"
                ambiguities.append(f"{d.governed}:{u.id}")
                gov = next((x for c2 in clauses for (x, _) in (new_units if c2 is clause else c2.units)
                            if x.span == d.governor_span), None)
                if gov is not None:
                    embedded_under = gov.id
                    relations.append(LatticeRelation(RelationKind.EMBEDS.value, gov.id, u.id,
                                                     evidence=d.governed))
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
            elif d.governed == "modal_governor":
                prag, epi = "EMBEDDED", "NOT_APPLICABLE"
                gov = next((x for (x, _) in new_units + clause.units if x.id == d.governor_unit), None)
                if gov is not None:
                    embedded_under = gov.id
                    relations.append(LatticeRelation(RelationKind.EMBEDS.value, gov.id, u.id,
                                                     evidence="modal+inf"))
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
            if d.governed == "subject_unresolved" and f"subject_unresolved:{u.id}" not in ambiguities:
                # whatever branch set its pragmatics (protasis, ambiguous attachment...), a
                # finite verb whose subject is unknown is always named (R1)
                ambiguities.append(f"subject_unresolved:{u.id}")
            if d.compound_modal:
                # whether "a pu / a dû / a voulu V" happened is not decided: never realized
                ambiguities.append(f"modal_past_occurrence_open:{u.id}")
            elif u.tense_aspect in {"PAST", "PLUPERFECT", "RECENT_PAST"} and prag in {
                    "ASSERTED", "REPORTED", "BELIEVED", "ASKED"}:
                realized = True if prag != "ASKED" else None
            if u.tense_aspect == "AVERTED":
                realized, epi = False, "COUNTERFACTUAL"
            if interrogative and d.lex is clause.ni_scope_open and d.modality is None \
                    and _MODALITY.get(_pred(d.lex)) == "ABILITY_OR_PERMISSION":
                # "Ne peux-tu ni lancer P ni exécuter Q ?": the act of the negated ability
                # question over its open ni members is not decided either (named)
                ambiguities.append(f"negated_speech_act_open:{u.id}")
            if prag == "INDIRECT_REQUEST" and u.polarity == "negative" and _negates_operator(clause.toks, d):
                # "Ne peux-tu pas lancer P ?", "Tu ne lances pas P ?": the negation bears on
                # the question / ability operator, not on a requested content: never a
                # prohibition; which act it is stays open (named), no gate, no constraint
                ambiguities.append(f"negated_speech_act_open:{u.id}")
            elif prag in {"REQUESTED", "FORBIDDEN", "INDIRECT_REQUEST"} and u.polarity == "negative":
                prag = "FORBIDDEN"
            elif prag == "FORBIDDEN" and u.polarity == "positive" and clause.conn not in {"sans", "sans_que"}:
                prag = "REQUESTED"
            if clause.evidential is not None and n == 0 and prag == "ASSERTED" and epi == "ASSERTED":
                epi = clause.evidential
            tmp = replace(u, pragmatic=prag, epistemic=epi, realized=realized,
                          embedded_under=embedded_under)
            role = _role(tmp, d, prag, interrogative)
            agent = _action_agent(tmp, d, prag)
            target = _request_target(tmp, agent, prag, role)
            new_units.append((replace(tmp, action_agent=agent, request_target=target,
                                      role=role), d))
        clause.units = new_units
        sibling = clause.coordinated_with
        if sibling is not None and sibling.units and new_units:
            a, b = sibling.units[0][0], new_units[0][0]
            if clause.conn_toks and clause.conn_toks[0].low == "ou":
                # "V que P ou que Q": sibling complements in one disjunction
                relations.append(LatticeRelation(RelationKind.ALTERNATIVE.value, a.id, b.id, evidence="ou que"))
                group = next((g for g in complement_alternatives if g[-1] is a), None)
                if group is None:
                    complement_alternatives.append([a, b])
                else:
                    group.append(b)
            else:
                relations.append(LatticeRelation(RelationKind.COORDINATES.value, a.id, b.id, evidence="et que"))
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
        # host of a following "puis" / "mais": only main clauses do. A clause of
        # ambiguous attachment is not known to be one.
        if clause.conn not in {"que", "rel", "comparative", "sans", "sans_que", "si",
                               "avant_que", "a_moins_que", "apres_que", "quand", "wh", "car"} and clause.units                 and not clause.attachment_ambiguous:
            main_heads.append((ci, clause.units[0][0]))

    for group in complement_alternatives:
        coordinations.append(CoordinationRef(
            f"c{len(coordinations) + 1}", "OR", tuple(u.id for u in group), "disjunction",
            tuple("ou que" for _ in group[1:]), (group[0].span[0], group[-1].span[1])))

    def _replace_group_unit(unit: PredicateUnit) -> None:
        for c in clauses:
            for i, (old, d) in enumerate(c.units):
                if old.id == unit.id:
                    c.units[i] = (unit, d)
                    return

    def _share_group_arguments(members: list[PredicateUnit], *, subject: str | None = None) -> list[PredicateUnit]:
        updated = list(members)
        if subject is not None:
            updated = [replace(u, subject=subject) if u.subject is None else u for u in updated]
        object_sources = [u.objects for u in updated if u.objects]
        if len(object_sources) == 1:
            shared_objects = object_sources[0]
            last_predicate_end = max(u.span[1] for u in updated)
            shared_after_coordination = all(arg.span is not None and arg.span[0] >= last_predicate_end
                                            for arg in shared_objects)
            if shared_after_coordination:
                updated = [replace(u, objects=shared_objects) if not u.objects else u for u in updated]
        for before, after in zip(members, updated):
            if before is not after:
                _replace_group_unit(after)
        return updated
    # ── shared auxiliary: host AUX+PP predicate and the bare participles sharing it ──
    for host in [c for c in clauses if c.shared_aux_host is None and c.compound is not None]:
        sharers = [c for c in clauses if c.shared_aux_host is host]
        if not sharers:
            continue
        unit_of = {id(d): u for c in (host, *sharers) for (u, d) in c.units}
        members = [unit_of.get(id(c.compound[2])) for c in (host, *sharers)]
        if any(u is None for u in members):
            continue
        members = _share_group_arguments(members, subject=members[0].subject)
        for c, a, b in zip(sharers, members, members[1:]):
            if c.conn is None and _share_kind(sharers) == "AND":  # ", PP": no connective relation was built for it
                relations.append(LatticeRelation(RelationKind.COORDINATES.value, a.id, b.id, evidence=","))
        coordinations.append(CoordinationRef(
            f"c{len(coordinations) + 1}", _share_kind(sharers), tuple(u.id for u in members), "shared_auxiliary",
            (host.compound[1], *(" ".join(x.low for x in c.conn_toks) or "," for c in sharers)),
            (members[0].span[0], members[-1].span[1])))

    operator_scopes: list[OperatorScopeRef] = []

    def _scope_operator(m: _Draft, coord: CoordinationRef) -> None:
        # one "pouvoir" over the coordination: one speech act, derived from the modal itself
        tok = m.modal_tok or m.lex
        if _MODALITY.get(_pred(tok)) != "ABILITY_OR_PERMISSION":
            return
        act = _ability_speech_act(m, interrogative)
        operator_scopes.append(OperatorScopeRef(
            f"o{len(operator_scopes) + 1}", "ABILITY_OR_PERMISSION", tok.low, coord.id, act,
            "ADDRESSEE_OR_POSSIBLE_ADDRESSEE" if act == "INDIRECT_REQUEST" else "NONE",
            (tok.start, coord.span[1])))

    # ── shared modality: host modal+infinitive predicate and the bare infinitives sharing it ──
    for host in [c for c in clauses if c.shared_modal_host is None and c.modal is not None]:
        sharers = [c for c in clauses if c.shared_modal_host is host]
        if not sharers:
            continue
        unit_of = {id(d): u for c in (host, *sharers) for (u, d) in c.units}
        members = [unit_of.get(id(host.modal))] + [unit_of.get(id(c.units[0][1])) if c.units else None
                                                   for c in sharers]
        if any(u is None for u in members):
            continue
        members = _share_group_arguments(members)
        for c, a, b in zip(sharers, members, members[1:]):
            if c.conn is None and _share_kind(sharers) == "AND":  # ", INF": no connective relation was built for it
                relations.append(LatticeRelation(RelationKind.COORDINATES.value, a.id, b.id, evidence=","))
        coordinations.append(CoordinationRef(
            f"c{len(coordinations) + 1}", _share_kind(sharers), tuple(u.id for u in members),
            "shared_directive" if host.modal.directive
            else "shared_periphrasis" if host.modal.modality is None else "shared_modality",
            (host.modal.modal_tok.low, *(" ".join(x.low for x in c.conn_toks) or "," for c in sharers)),
            (members[0].span[0], members[-1].span[1])))
        _scope_operator(host.modal, coordinations[-1])

    # ── shared subject: host predicate with an explicit subject and the bare agreeing verbs ──
    for host in [c for c in clauses if c.shared_subject_host is None and c.subject_host is not None]:
        sharers = [c for c in clauses if c.shared_subject_host is host]
        if not sharers:
            continue
        unit_of = {id(d): u for c in (host, *sharers) for (u, d) in c.units}
        members = [unit_of.get(id(host.subject_host))] + [unit_of.get(id(c.units[0][1])) if c.units else None
                                                          for c in sharers]
        if any(u is None for u in members):
            continue
        for c, a, b in zip(sharers, members, members[1:]):
            if c.conn is None and _share_kind(sharers) == "AND":  # ", V": no connective relation was built for it
                relations.append(LatticeRelation(RelationKind.COORDINATES.value, a.id, b.id, evidence=","))
        coordinations.append(CoordinationRef(
            f"c{len(coordinations) + 1}", _share_kind(sharers), tuple(u.id for u in members), "shared_subject",
            (host.subject_host.subject, *(" ".join(x.low for x in c.conn_toks) or "," for c in sharers)),
            (members[0].span[0], members[-1].span[1])))

    # ── verbal ni coordination: one structural group per "ne ... ni ... ni" ──
    ni_heads = [c for c in clauses if c.ni_head is c]
    for head in ni_heads:
        members = [u for c in clauses if c.ni_head is head for (u, d) in c.units
                   if d.head_index > 0 and c.toks[d.head_index - 1].low == "ni" and u.negator == "ni"]
        if len(members) < 2:
            continue
        for a, b in zip(members, members[1:]):
            relations.append(LatticeRelation(RelationKind.COORDINATES.value, a.id, b.id, evidence="ni"))
        coordinations.append(CoordinationRef(
            f"c{len(coordinations) + 1}", "AND", tuple(u.id for u in members), "ni_negative_coordination",
            tuple("ni" for _ in members), (members[0].span[0], members[-1].span[1])))
        if isinstance(head.ni_modal, _Draft):
            _scope_operator(head.ni_modal, coordinations[-1])

    # ── inter-clause relations ──
    alternatives: list[list[PredicateUnit]] = []
    for ci, clause in enumerate(clauses):
        h = head_of(ci)
        # a protasis head without a unit ("Si Nadia et Luc exécutent Q"): its group still conditions
        if h is None and not (clause.conn == "si" and clause.protasis_head is clause):
            continue
        conn = clause.conn
        prev_main = next((u for (cj, u) in reversed(main_heads) if cj < ci), None)
        next_main = next((u for (cj, u) in main_heads if cj > ci), None)
        if conn in {"sans", "sans_que"}:
            host = prev_main or next_main
            if host is not None:
                relations.append(LatticeRelation(RelationKind.FORBIDS.value, host.id, h.id,
                                                 evidence=conn))
        elif conn == "si" and clause.protasis_head is not None and clause.protasis_head is not clause:
            pass  # member of a conjunctive protasis: related through its head's group
        elif conn == "si":
            host = next_main if next_main is not None else prev_main
            source = h.id if h is not None else None
            if clause.protasis_head is clause:
                group = [c for c in clauses if c.protasis_head is clause and c.units]
                heads = [c.units[0][0] for c in group]
                if source is None:
                    if not heads:
                        continue
                    source = heads[0].id
                links = tuple(" ".join(x.low for x in c.conn_toks) for c in group[1:])
                for a, (b, link) in zip(heads, zip(heads[1:], links)):
                    relations.append(LatticeRelation(RelationKind.COORDINATES.value, a.id, b.id, evidence=link))
                if len(heads) > 1:
                    source = f"c{len(coordinations) + 1}"
                    coordinations.append(CoordinationRef(
                        source, "AND", tuple(u.id for u in heads), "conditional_protasis", links,
                        (heads[0].span[0], heads[-1].span[1])))
            if host is not None:
                relations.append(LatticeRelation(RelationKind.CONDITIONS.value, source, host.id,
                                                 evidence="si"))
        elif conn == "apres_que" and (prev_main or next_main) is not None:
            host = prev_main if prev_main is not None else next_main
            relations.append(LatticeRelation(RelationKind.PRECEDES.value, h.id, host.id,
                                             evidence="après que"))
        elif conn == "avant_que" and prev_main is not None:
            relations.append(LatticeRelation(RelationKind.PRECEDES.value, prev_main.id, h.id,
                                             evidence="avant que"))
        elif conn == "a_moins_que" and prev_main is not None:
            relations.append(LatticeRelation(RelationKind.CONDITIONS.value, h.id, prev_main.id,
                                             confidence=0.8, evidence="à moins que"))
        elif prev_main is not None and not clause.attachment_ambiguous and conn in {
                "mais", "puis", "et", "ou", "donc", "car", "avant_de", "apres", "alors"}:
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
            if conn == "ou":
                # "P ou Q (ou R)": one disjunction over the branches, never an occurrence of one
                group = next((g for g in alternatives if g[-1] is prev_main), None)
                if group is None:
                    alternatives.append([prev_main, h])
                else:
                    group.append(h)
    for group in alternatives:
        coordinations.append(CoordinationRef(
            f"c{len(coordinations) + 1}", "OR", tuple(u.id for u in group), "disjunction",
            tuple("ou" for _ in group[1:]), (group[0].span[0], group[-1].span[1])))

    # ── unanalyzed predicative content: reported, never dropped (M8-0b) ──
    # "<marker>:<start>-<end>:<link>[:ops=...]" — the span of the clause, its
    # structural link when syntax gives it, and detectable scope operators.
    missing: list[str] = []
    protases = [cj for cj, c in enumerate(clauses)
                if c.conn == "si" or (c.toks and c.toks[0].low == "si")]
    for ci, clause in enumerate(clauses):
        if not clause.toks:
            continue
        governed_by = None
        if clause.units:
            # Partial loss: a known modal / auxiliary whose unknown infinitive or
            # participle produced no unit ("pourrait partir").
            covered = {u.span for (u, _) in clause.units}
            lost = [(k, j) for k, j in _lost_verb_evidence(clause)
                    if (clause.toks[j].start, clause.toks[j].end) not in covered]
            if not lost:
                continue
            k = lost[0][0]
            governed_by = next((u for (u, _) in clause.units
                                if u.span == (clause.toks[k].start, clause.toks[k].end)), None)
        elif clause.conn != "quand" and not _unanalyzed_predicative(
                clause, in_sequence=(in_seq := clause.conn in _SEQUENCE_CONNECTIVES
                                     or (clause.conn is None and any(c.units for c in clauses if c is not clause)))) \
                and not (_copula_evidence(clause) and (in_seq or clause.conn in _COPULA_REPORTED_CONNS)):
            # (a "quand / lorsque" subordinate without any unit is always reported; so is
            # a copula + attribute clause in a subordinate or a sequence: "si c'est prêt")
            continue
        content = clause.toks[1:] if clause.toks[0].low == "si" else clause.toks
        if clause.conn in {"que", "rel"}:
            parent = None
            if clause.embedding_parent is not None and clause.embedding_parent < ci:
                parent = last_of(clause.embedding_parent)
            if parent is None and ci > 0:
                parent = last_of(ci - 1)
            if parent is not None:
                link = f"embedded_under={parent.id}"
            elif clause.conn == "rel" and not clause.governor_lost:
                link = "unattached"  # e.g. main predicate absorbed after a relative
            else:
                link = "embedded_under_unresolved_governor"
        elif clause.conn == "quand":
            link = "temporal_subordinate"  # no host chosen
        elif clause.conn == "wh":
            link = "wh_complement"
        elif ci in protases:
            link = "conditional_protasis"
        else:
            cj = max((p for p in protases if p < ci), default=None)
            if cj is not None and not any(cj < mj < ci for mj, _ in main_heads):
                h = head_of(cj)
                link = f"conditional_consequent_of={h.id}" if h is not None else "conditional_consequent"
            elif clause.conn in {"mais", "puis", "et", "ou", "donc", "car", "alors", "apres", "avant_de", "apres_que"}:
                prev_main = next((u for (mj, u) in reversed(main_heads) if mj < ci), None)
                link = f"{clause.conn}_after={prev_main.id}" if prev_main is not None else clause.conn
            else:
                link = "root"
        ops = _content_operators(clause)
        missing.append(f"{UNANALYZED_PREDICATIVE_CONTENT}:{content[0].start}-{content[-1].end}:{link}"
                       + (f":governed_by={governed_by.id}" if governed_by is not None else "")
                       + (f":ops={','.join(ops)}" if ops else ""))

    # "Nadia et Luc exécutent Q": "et" split a coordinated subject; the first nominal
    # conjunct (a verbless clause) is never lost silently. The group-subject schema is not
    # decided: the conjunct is kept as a named missing entry, the unit carries a blocker.
    for ci in range(len(clauses) - 1):
        c0, c1 = clauses[ci], clauses[ci + 1]
        if c0.units or not c0.toks or c0.conn not in {None, "si", "que"} or not c1.units \
                or [x.low for x in c1.conn_toks] != ["et"]:
            continue
        np0 = list(c0.toks)
        while np0 and np0[0].low in _SUBJECT_INTRODUCERS:
            np0 = np0[1:]
        u1, d1 = c1.units[0]
        pre = [t for t in c1.toks[:d1.head_index] if t.low not in {"ne", "n'"}]
        head = c1.toks[d1.head_index]
        covered = any(m.split(":")[1] == f"{c0.toks[0].start}-{c0.toks[-1].end}" for m in missing)
        if not covered and _bare_noun_phrase(np0) \
                and (_bare_noun_phrase(pre) or [t.low for t in pre] in (["moi"], ["toi"])) \
                and d1.head_index > 0 and _plural_verb(head):
            missing.append(f"coordinated_subject_unrepresented:{np0[0].start}-{np0[-1].end}:subject_of={u1.id}")
            ambiguities.append(f"coordinated_subject_unrepresented:{u1.id}")

    final_units = [u for c in clauses for (u, _) in c.units]
    final_units, ref_relations, unresolved, presupposed, ambiguous_refs = _resolve_references(final_units)
    relations.extend(ref_relations)
    ambiguities.extend(ambiguous_refs)

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
        missing=tuple(missing),
        disfluencies=tuple(disfluencies),
        orthography_flags=tuple(dict.fromkeys(ortho)),
        coordinations=tuple(coordinations),
        operator_scopes=tuple(operator_scopes),
    )


def _mark_governed(clause: _Clause, d: _Draft, pol: dict) -> None:
    """Classify infinitive roles that mention an action without requesting it."""
    lows = [t.low for t in clause.toks]
    if d.governed in {"negated_scope_open", "know_how_scope_open", "unknown_governor", "subject_unresolved"}:
        return
    if clause.ni_scope_open is not None and d.verb_form == "INFINITIVE" and d.head_index > 0 \
            and lows[d.head_index - 1] == "ni" and d.modality is None and d.subject is None:
        # "ne voudrait ni INF": bound to that exact "vouloir" token, never to a nearest unit
        d.governed = "negated_scope_open"
        d.governor_span = (clause.ni_scope_open.start, clause.ni_scope_open.end)
        return
    if d.unresolved_governor and d.verb_form == "INFINITIVE":
        # Unknown "que" governor under a modal / aspectual: MODAL(G(X)), the
        # modal unit governs G, never flattened into G(X) or X.
        prior = [u for (u, dd) in clause.units if dd.lex_index < d.lex_index]
        if prior and prior[-1].predicate_class in {"modal", "aspectual"}:
            d.governed = "modal_governor"
            d.governor_unit = prior[-1].id
        return
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
    if _unknown_finite_governor(clause, d):
        # "Paul n'aime pas lancer P": governed by an unrecognised word, never injunctive
        d.governed = "unknown_governor"
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


def _unknown_finite_governor(clause: _Clause, d: _Draft) -> bool:
    """A bare infinitive whose left context is subject + unknown content word (+ ne /
    pas / ni): "Paul aime lancer P", "Paul n'aime ni lancer P ni exécuter Q".

    The second "ni" member takes the same (exact) governor as the first; an
    interjection or a hyphenated word is never taken as a governor or a subject.
    """
    toks, lows = clause.toks, [t.low for t in clause.toks]
    g = d.lex_index - 1
    if g >= 0 and lows[g] == "ni" and any(dd.governed == "unknown_governor" for (_, dd) in clause.units):
        return True
    while g >= 0 and lows[g] in _OBJECT_CLITICS | _REFLEXIVE_CLITICS | {"ne", "n'", "pas", "plus", "jamais", "ni"}:
        g -= 1
    if g < 1 or not _content_word(toks[g]) or toks[g].hyphen_before or lows[g] in _INTERJECTIONS:
        return False
    s = g - 1
    while s >= 0 and lows[s] in {"ne", "n'"}:
        s -= 1
    return s >= 0 and lows[s] not in _INTERJECTIONS and not toks[s].hyphen_before and (
        lows[s] in _SUBJECT_PRONOUNS | _DEMONSTRATIVE_SUBJECTS or _content_word(toks[s]))


def _negates_operator(toks: list[_Tok], d: _Draft) -> bool:
    """The negation of this chain frames its finite head (the question / modal operator),
    not its lexical infinitive: "ne peux-tu pas lancer" vs "peux-tu ne pas lancer". A member
    sharing an operator from another clause ("peux-tu arrêter P et ne pas lancer Q ?")
    carries its own negation."""
    if d.modal_tok is not None and not any(t is d.modal_tok for t in toks):
        return False
    return not any(t.low in {"ne", "n'"} for t in toks[d.head_index + 1:d.lex_index])


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

def _ability_speech_act(d: _Draft, interrogative: bool) -> str:
    """Speech act carried by an ability-permission modal, from its own context."""
    if d.subject_person == "2" and (interrogative or d.politeness) and not d.compound_modal:
        return "INDIRECT_REQUEST"
    return "QUESTION" if interrogative else "NONE"


def _main_pragmatics(u: PredicateUnit, d: _Draft, interrogative: bool,
                     ambiguities: list[str]) -> tuple[str, str]:
    person = d.subject_person
    if d.compound_modal:
        # a past modal ("tu as dû lancer P", "il a fallu lancer P") is never a directive
        return ("ASKED", "UNKNOWN") if interrogative else ("ASSERTED", "ASSERTED")
    if d.directive:
        # one written directive operator scopes over its (coordinated) infinitives
        return "REQUESTED", "NOT_APPLICABLE"
    if u.modality == "ABILITY_OR_PERMISSION":
        act = _ability_speech_act(d, interrogative)
        if act == "INDIRECT_REQUEST":
            ambiguities.append(f"ability_permission_or_request:{u.id}")
            return "INDIRECT_REQUEST", "NOT_APPLICABLE"
        return ("ASKED", "UNKNOWN") if act == "QUESTION" else ("ASSERTED", "ASSERTED")
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


_PLURAL_DETS = {"les", "des", "ces", "mes", "tes", "ses", "nos", "vos", "leurs", "aux"}
_FEMININE_DETS = {"la", "une", "cette", "ma", "ta", "sa"}
_MASCULINE_DETS = {"le", "un", "ce", "cet", "mon", "ton", "son", "du", "au"}


def _agrees_with_antecedent(pronoun: str, det: str | None) -> bool:
    """Number / gender agreement of an object pronoun with an NP determiner (unknown: compatible)."""
    if det is None or pronoun not in {"le", "la", "l'", "les"}:
        return True
    if pronoun == "les":
        return det in _PLURAL_DETS
    if det in _PLURAL_DETS:
        return False
    return not ((pronoun == "le" and det in _FEMININE_DETS) or (pronoun == "la" and det in _MASCULINE_DETS))


def _resolve_references(units: list[PredicateUnit]):
    """Intra-utterance anaphora (then cataphora) for pronoun objects.

    Only antecedents agreeing with the pronoun count; a unique one resolves it,
    several distinct ones leave it open (never the nearest), none leaves it open.
    """
    candidates: list[tuple[int, str, str, str | None]] = []  # (position, head, unit id, determiner)
    for u in units:
        for a in u.objects:
            if a.kind in {"NP", "NEGATIVE_QUANTIFIER"} and a.head != "*":
                first = a.text.split()[0] if a.text.split() else ""
                det = first if first in _DETERMINERS else ("l'" if a.text.startswith("l'") else None)
                candidates.append(((a.span or u.span)[0], a.head, u.id, det))
    relations: list[LatticeRelation] = []
    unresolved: list[str] = []
    presupposed: list[str] = []
    ambiguous: list[str] = []
    out: list[PredicateUnit] = []
    for u in units:
        new_args = []
        for a in u.objects:
            if a.reference == "UNRESOLVED" and a.kind == "PRONOUN":
                pos = (a.span or u.span)[0]
                agree = [c for c in candidates if _agrees_with_antecedent(a.text, c[3])]
                before = [c for c in agree if c[0] < pos]
                after = [c for c in agree if c[0] > pos]
                pool = before or after
                ante = pool[-1] if before else (pool[0] if pool else None)
                # several distinct agreeing antecedents ("le test ... le build ... le"):
                # never the nearest; the reference stays open (no nearest match)
                rivals = {(c[0], c[1]) for c in pool}
                if not pool and a.text == "les":
                    # "le test et le build ... les": only a collective reading of the
                    # coordinated singulars would agree; it stays open (named, not chosen)
                    raw = [c for c in candidates if c[0] < pos] or [c for c in candidates if c[0] > pos]
                    host = raw[-1][2] if raw and raw[0][0] < pos else (raw[0][2] if raw else None)
                    rivals = {(c[0], c[1]) for c in raw if c[2] == host}
                if len(rivals) > 1:
                    ambiguous.append(f"ambiguous_antecedent:{u.id}:{a.text}:"
                                     + ",".join(h for _, h in sorted(rivals)))
                    ante = None
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
    return out, relations, unresolved, list(dict.fromkeys(presupposed)), ambiguous


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
