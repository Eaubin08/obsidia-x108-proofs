"""Closed deterministic lexicon for the built-in grammar.

Only verbs that carry governance or grammatical weight are listed; this is
NOT a phrase dictionary. Every inflected form is generated from a lemma and
its conjugation class, so that "lancer / lance / lancez / lancé / lançons"
all reach the same canonical predicate. Lookup is accent-sensitive first
(accents disambiguate participle vs present), then accent-folded (noisy
input) with the union of analyses.
"""
from __future__ import annotations

import unicodedata

# lemma -> (canonical predicate, predicate class)
LEMMAS: dict[str, tuple[str, str]] = {
    # world actions (governed)
    "exécuter": ("EXECUTE", "world_action"),
    "lancer": ("EXECUTE", "world_action"),
    "relancer": ("EXECUTE", "world_action"),
    "run": ("EXECUTE", "world_action"),
    "execute": ("EXECUTE", "world_action"),
    "launch": ("EXECUTE", "world_action"),
    "push": ("PUSH", "world_action"),
    "pusher": ("PUSH", "world_action"),
    "pousser": ("PUSH", "world_action"),
    "commit": ("COMMIT", "world_action"),
    "commiter": ("COMMIT", "world_action"),
    "déployer": ("DEPLOY", "world_action"),
    "deploy": ("DEPLOY", "world_action"),
    "supprimer": ("DELETE", "world_action"),
    "effacer": ("DELETE", "world_action"),
    "delete": ("DELETE", "world_action"),
    "installer": ("INSTALL", "world_action"),
    "install": ("INSTALL", "world_action"),
    # preparatory / production / inspection
    "préparer": ("PREPARE", "preparatory"),
    "prepare": ("PREPARE", "preparatory"),
    "écrire": ("WRITE", "text_production"),
    "write": ("WRITE", "text_production"),
    "rédiger": ("WRITE", "text_production"),
    "expliquer": ("EXPLAIN", "text_production"),
    "explain": ("EXPLAIN", "text_production"),
    # distinct operations, never collapsed into EXPLAIN / SAY (lexical distinction kept)
    "détailler": ("DETAIL", "text_production"),
    "comparer": ("COMPARE", "text_production"),
    "tester": ("VERIFY", "inspection"),
    "vérifier": ("VERIFY", "inspection"),
    "check": ("VERIFY", "inspection"),
    "confirmer": ("CONFIRM", "inspection"),
    "oublier": ("FORGET", "other"),
    "faire": ("DO", "generic_action"),
    "do": ("DO", "generic_action"),
    # embedding verbs
    "dire": ("SAY", "embedding_say"),
    # audited safe report subset (B2b); embedding still requires "que"
    "affirmer": ("SAY", "embedding_say"),
    "déclarer": ("SAY", "embedding_say"),
    "mentionner": ("SAY", "embedding_say"),
    "say": ("SAY", "embedding_say"),
    "tell": ("SAY", "embedding_say"),
    "craindre": ("FEAR", "embedding_fear"),
    "redouter": ("FEAR", "embedding_fear"),
    "fear": ("FEAR", "embedding_fear"),
    "éviter": ("PREVENT", "embedding_prevent"),
    "empêcher": ("PREVENT", "embedding_prevent"),
    "penser": ("BELIEVE", "embedding_believe"),
    "croire": ("BELIEVE", "embedding_believe"),
    # audited safe belief subset (B2b)
    "supposer": ("BELIEVE", "embedding_believe"),
    "apprendre": ("LEARN", "embedding_learn"),
    "voir": ("OBSERVE", "observation"),
    "observer": ("OBSERVE", "observation"),
    "détecter": ("OBSERVE", "observation"),
    "think": ("BELIEVE", "embedding_believe"),
    "believe": ("BELIEVE", "embedding_believe"),
    # modals
    "pouvoir": ("ABLE", "modal"),
    "devoir": ("MUST", "modal"),
    "vouloir": ("WANT", "modal"),
    "falloir": ("NEED", "modal"),
    "savoir": ("KNOW", "modal"),
    "can": ("ABLE", "modal"),
    "could": ("ABLE", "modal"),
    "must": ("MUST", "modal"),
    "should": ("MUST", "modal"),
    # auxiliaries / aspectuals
    "avoir": ("HAVE", "aux"),
    "être": ("BE", "copula"),
    "aller": ("GO", "aspectual"),
    "venir": ("COME", "aspectual"),
    "faillir": ("NEARLY", "aspectual"),
    # others
    "pleuvoir": ("WEATHER", "weather"),
    "neiger": ("WEATHER", "weather"),
    "attendre": ("WAIT", "other"),
    "hésiter": ("HESITATE", "other"),
    "inquiéter": ("WORRY", "other"),
    "passer": ("PASS", "other"),
    "changer": ("CHANGE", "other"),
    "arrêter": ("STOP", "other"),
    "stop": ("STOP", "other"),
}

# -er verbs: lemma -> (stem, stem used before a mute e, or None)
_ER_VERBS: dict[str, tuple[str, str | None]] = {
    "exécuter": ("exécut", None),
    "lancer": ("lanc", None),
    "relancer": ("relanc", None),
    "pusher": ("push", None),
    "pousser": ("pouss", None),
    "commiter": ("commit", None),
    "supprimer": ("supprim", None),
    "effacer": ("effac", None),
    "installer": ("install", None),
    "préparer": ("prépar", None),
    "rédiger": ("rédig", None),
    "expliquer": ("expliqu", None),
    "détailler": ("détaill", None),
    "comparer": ("compar", None),
    "tester": ("test", None),
    "vérifier": ("vérifi", None),
    "confirmer": ("confirm", None),
    "oublier": ("oubli", None),
    "redouter": ("redout", None),
    "éviter": ("évit", None),
    "empêcher": ("empêch", None),
    "penser": ("pens", None),
    "affirmer": ("affirm", None),
    "déclarer": ("déclar", None),
    "mentionner": ("mentionn", None),
    "supposer": ("suppos", None),
    "apprendre": ("appr", None),
    "observer": ("observ", None),
    "détecter": ("détect", None),
    "neiger": ("neig", None),
    "hésiter": ("hésit", None),
    "inquiéter": ("inquiét", "inquièt"),
    "passer": ("pass", None),
    "changer": ("chang", None),
    "arrêter": ("arrêt", None),
}

_IRREGULAR: dict[str, dict[str, tuple[str, ...]]] = {
    "faire": {
        "PRES": ("fais", "fait", "faisons", "faites", "font"),
        "IMP": ("fais", "faisons", "faites"),
        "INF": ("faire",), "PP": ("fait", "faite", "faits"),
        "IMPF": ("faisais", "faisait", "faisions", "faisiez", "faisaient"),
        "FUT": ("ferai", "feras", "fera", "ferons", "ferez", "feront"),
        "COND": ("ferais", "ferait", "ferions", "feriez", "feraient"),
        "SUBJ": ("fasse", "fasses", "fassions", "fassiez", "fassent"),
    },
    "pouvoir": {
        "PRES": ("peux", "peut", "pouvons", "pouvez", "peuvent"),
        "INF": ("pouvoir",), "PP": ("pu",),
        "IMPF": ("pouvais", "pouvait", "pouvions", "pouviez", "pouvaient"),
        "FUT": ("pourrai", "pourras", "pourra", "pourrons", "pourrez", "pourront"),
        "COND": ("pourrais", "pourrait", "pourrions", "pourriez", "pourraient"),
        "SUBJ": ("puisse", "puisses", "puissions", "puissiez", "puissent"),
    },
    "devoir": {
        "PRES": ("dois", "doit", "devons", "devez", "doivent"),
        "INF": ("devoir",), "PP": ("dû",),
        "IMPF": ("devais", "devait", "devions", "deviez", "devaient"),
        "FUT": ("devrai", "devras", "devra", "devrons", "devrez", "devront"),
        "COND": ("devrais", "devrait", "devrions", "devriez", "devraient"),
    },
    "vouloir": {
        "PRES": ("veux", "veut", "voulons", "voulez", "veulent"),
        "INF": ("vouloir",), "PP": ("voulu",), "IMP": ("veuillez",),
        "IMPF": ("voulais", "voulait", "voulions", "vouliez", "voulaient"),
        "FUT": ("voudrai", "voudras", "voudra", "voudrons", "voudrez", "voudront"),
        "COND": ("voudrais", "voudrait", "voudrions", "voudriez", "voudraient"),
    },
    "falloir": {
        "PRES": ("faut",), "INF": ("falloir",), "PP": ("fallu",),
        "IMPF": ("fallait",), "FUT": ("faudra",), "COND": ("faudrait",),
        "SUBJ": ("faille",),
    },
    "savoir": {
        "PRES": ("sais", "sait", "savons", "savez", "savent"),
        "INF": ("savoir",), "PP": ("su",),
        "IMPF": ("savais", "savait", "savions", "saviez", "savaient"),
        "FUT": ("saurai", "sauras", "saura", "saurons", "saurez", "sauront"),
        "COND": ("saurais", "saurait", "saurions", "sauriez", "sauraient"),
    },
    "avoir": {
        "PRES": ("ai", "as", "a", "avons", "avez", "ont"),
        "INF": ("avoir",), "PP": ("eu",),
        "IMPF": ("avais", "avait", "avions", "aviez", "avaient"),
        "FUT": ("aurai", "auras", "aura", "aurons", "aurez", "auront"),
        "COND": ("aurais", "aurait", "aurions", "auriez", "auraient"),
    },
    "être": {
        "PRES": ("suis", "es", "est", "sommes", "êtes", "sont"),
        "INF": ("être",), "PP": ("été",),
        "IMPF": ("étais", "était", "étions", "étiez", "étaient"),
        "FUT": ("serai", "seras", "sera", "serons", "serez", "seront"),
        "COND": ("serais", "serait", "serions", "seriez", "seraient"),
        "SUBJ": ("sois", "soit", "soyons", "soyez", "soient"),
    },
    "aller": {
        "PRES": ("vais", "vas", "va", "allons", "allez", "vont"),
        "IMP": ("va", "allons", "allez"),
        "INF": ("aller",), "PP": ("allé",),
        "IMPF": ("allais", "allait", "allions", "alliez", "allaient"),
        "FUT": ("irai", "iras", "ira", "irons", "irez", "iront"),
    },
    "venir": {
        "PRES": ("viens", "vient", "venons", "venez", "viennent"),
        "INF": ("venir",), "PP": ("venu",),
        "IMPF": ("venais", "venait", "venions", "veniez", "venaient"),
    },
    "faillir": {"INF": ("faillir",), "PP": ("failli",)},
    "dire": {
        "PRES": ("dis", "dit", "disons", "dites", "disent"),
        "IMP": ("dis", "dites"),
        "INF": ("dire",), "PP": ("dit", "dite"),
        "IMPF": ("disais", "disait", "disaient"),
        "FUT": ("dira", "dirai"), "COND": ("dirait", "dirais"),
    },
    "craindre": {
        "PRES": ("crains", "craint", "craignons", "craignez", "craignent"),
        "INF": ("craindre",), "PP": ("craint",),
        "IMPF": ("craignais", "craignait"),
    },
    "croire": {
        "PRES": ("crois", "croit", "croyons", "croyez", "croient"),
        "INF": ("croire",), "PP": ("cru",),
        "IMPF": ("croyais", "croyait", "croyions", "croyiez", "croyaient"),
        "FUT": ("croirai", "croiras", "croira", "croirons", "croirez", "croiront"),
        "COND": ("croirais", "croirait", "croirions", "croiriez", "croiraient"),
    },
    "apprendre": {
        "PRES": ("apprends", "apprend", "apprenons", "apprenez", "apprennent"),
        "INF": ("apprendre",), "PP": ("appris", "apprise"),
        "IMPF": ("apprenais", "apprenait", "apprenaient"),
        "FUT": ("apprendrai", "apprendra", "apprendrez"),
        "COND": ("apprendrais", "apprendrait"),
    },
    "voir": {
        "PRES": ("vois", "voit", "voyons", "voyez", "voient"),
        "INF": ("voir",), "PP": ("vu", "vue", "vus", "vues"),
        "IMPF": ("voyais", "voyait", "voyaient"),
        "FUT": ("verrai", "verra", "verrez"),
        "COND": ("verrais", "verrait"),
    },
    "écrire": {
        "PRES": ("écris", "écrit", "écrivons", "écrivez", "écrivent"),
        "IMP": ("écris", "écrivons", "écrivez"),
        "INF": ("écrire",), "PP": ("écrit", "écrite"),
    },
    "attendre": {
        "PRES": ("attends", "attend", "attendons", "attendez", "attendent"),
        "IMP": ("attends", "attendons", "attendez"),
        "INF": ("attendre",), "PP": ("attendu",),
    },
    "pleuvoir": {
        "PRES": ("pleut",), "INF": ("pleuvoir",), "PP": ("plu",),
        "IMPF": ("pleuvait",), "FUT": ("pleuvra",), "COND": ("pleuvrait",),
    },
    "lancer": {"PRES": ("lançons",), "IMP": ("lançons",), "IMPF": ("lançais", "lançait", "lançaient"),
               "PPR": ("lançant",)},
    "relancer": {"PRES": ("relançons",), "IMP": ("relançons",)},
    "effacer": {"PRES": ("effaçons",), "IMP": ("effaçons",)},
    "changer": {"PRES": ("changeons",), "IMPF": ("changeait",)},
    "neiger": {"IMPF": ("neigeait",)},
    "rédiger": {"PRES": ("rédigeons",)},
    "déployer": {
        "PRES": ("déploie", "déploies", "déployons", "déployez", "déploient"),
        "IMP": ("déploie", "déployons", "déployez"),
        "INF": ("déployer",), "PP": ("déployé", "déployée", "déployés"),
        "FUT": ("déploiera",), "SUBJ": ("déploie", "déploies"),
    },
}

_EN_FORMS: dict[str, dict[str, tuple[str, ...]]] = {
    "run": {"BASE": ("run",), "PRES3": ("runs",), "PAST": ("ran",), "PP": ("run",), "GER": ("running",)},
    "execute": {"BASE": ("execute",), "PRES3": ("executes",), "PAST": ("executed",), "PP": ("executed",),
                "GER": ("executing",)},
    "launch": {"BASE": ("launch",), "PRES3": ("launches",), "PAST": ("launched",), "PP": ("launched",),
               "GER": ("launching",)},
    "push": {"BASE": ("push",), "PRES3": ("pushes",), "PAST": ("pushed",), "PP": ("pushed",),
             "GER": ("pushing",)},
    "commit": {"BASE": ("commit",), "PRES3": ("commits",), "PAST": ("committed",), "PP": ("committed",),
               "GER": ("committing",)},
    "deploy": {"BASE": ("deploy",), "PRES3": ("deploys",), "PAST": ("deployed",), "PP": ("deployed",),
               "GER": ("deploying",)},
    "delete": {"BASE": ("delete",), "PRES3": ("deletes",), "PAST": ("deleted",), "PP": ("deleted",),
               "GER": ("deleting",)},
    "install": {"BASE": ("install",), "PRES3": ("installs",), "PAST": ("installed",), "PP": ("installed",),
                "GER": ("installing",)},
    "prepare": {"BASE": ("prepare",), "PRES3": ("prepares",), "PAST": ("prepared",), "PP": ("prepared",),
                "GER": ("preparing",)},
    "write": {"BASE": ("write",), "PRES3": ("writes",), "PAST": ("wrote",), "PP": ("written",),
              "GER": ("writing",)},
    "explain": {"BASE": ("explain",), "PRES3": ("explains",), "PAST": ("explained",), "GER": ("explaining",)},
    "check": {"BASE": ("check",), "PRES3": ("checks",), "PAST": ("checked",)},
    "do": {"BASE": ("do",), "PRES3": ("does",), "PAST": ("did",), "PP": ("done",)},
    "say": {"BASE": ("say",), "PRES3": ("says",), "PAST": ("said",), "PP": ("said",)},
    "tell": {"BASE": ("tell",), "PRES3": ("tells",), "PAST": ("told",), "PP": ("told",)},
    "fear": {"BASE": ("fear",), "PRES3": ("fears",), "PAST": ("feared",)},
    "think": {"BASE": ("think",), "PRES3": ("thinks",), "PAST": ("thought",)},
    "believe": {"BASE": ("believe",), "PRES3": ("believes",), "PAST": ("believed",)},
    "can": {"MODAL": ("can",)},
    "could": {"MODAL": ("could",)},
    "must": {"MODAL": ("must",)},
    "should": {"MODAL": ("should",)},
    "stop": {"BASE": ("stop",), "PRES3": ("stops",), "PAST": ("stopped",)},
}

# EN analyses map onto the French feature names used by the grammar.
_EN_FEATS = {
    "BASE": {"INF", "IMP", "PRES"}, "PRES3": {"PRES"}, "PAST": {"PAST_SIMPLE"},
    "PP": {"PP"}, "GER": {"PPR"}, "MODAL": {"PRES"},
}


def fold(text: str) -> str:
    out = []
    for ch in text:
        base = unicodedata.normalize("NFKD", ch)
        base = "".join(c for c in base if not unicodedata.combining(c))
        out.append(base if len(base) == 1 else ch)
    return "".join(out)


def _er_forms(stem: str, mute: str | None) -> dict[str, tuple[str, ...]]:
    m = mute or stem
    return {
        "PRES": (m + "e", m + "es", stem + "ons", stem + "ez", m + "ent"),
        "IMP": (m + "e", stem + "ons", stem + "ez"),
        "SUBJ": (m + "e", m + "es", stem + "ions", stem + "iez", m + "ent"),
        "INF": (stem + "er",),
        "PP": (stem + "é", stem + "ée", stem + "és", stem + "ées"),
        "IMPF": (stem + "ais", stem + "ait", stem + "ions", stem + "iez", stem + "aient"),
        "FUT": tuple(m + "er" + e for e in ("ai", "as", "a", "ons", "ez", "ont")),
        "COND": tuple(m + "er" + e for e in ("ais", "ait", "ions", "iez", "aient")),
        "PPR": (stem + "ant",),
    }


_ER_PRES_PERSONS = (("P1S", "P3S"), ("P2S",), ("P1P",), ("P2P",), ("P3P",))
# five-slot present table of a non -er irregular verb ("fais, fait, faisons, faites, font")
_IRR_PRES_PERSONS = (("P1S", "P2S"), ("P3S",), ("P1P",), ("P2P",), ("P3P",))


def _er_present_persons(form: str) -> tuple[str, ...]:
    """Person/number of an -er present form from its ending (same paradigm as _ER_PRES_PERSONS)."""
    for ending, persons in (("ent", ("P3P",)), ("ons", ("P1P",)), ("ez", ("P2P",)), ("es", ("P2S",)),
                            ("e", ("P1S", "P3S"))):
        if form.endswith(ending):
            return persons
    return ()

Analysis = tuple[str, frozenset]  # (lemma, features)


def _build() -> tuple[dict[str, list[Analysis]], dict[str, list[Analysis]]]:
    exact: dict[str, dict[str, set]] = {}

    def add(form: str, lemma: str, feats: set) -> None:
        exact.setdefault(form, {}).setdefault(lemma, set()).update(feats)

    for lemma, (stem, mute) in _ER_VERBS.items():
        for feat, forms in _er_forms(stem, mute).items():
            for i, f in enumerate(forms):
                # present person/number, known by position (agreement with a shared subject)
                add(f, lemma, {feat} | (set(_ER_PRES_PERSONS[i]) if feat == "PRES" else set()))
    for lemma, table in _IRREGULAR.items():
        for feat, forms in table.items():
            for i, f in enumerate(forms):
                # an -er verb's present person follows its ending ("déploie", "lançons");
                # another verb's follows its position in a full five-slot table
                if feat == "PRES" and lemma.endswith("er"):
                    persons = _er_present_persons(f) if lemma != "aller" else ()
                elif feat == "PRES" and len(forms) == 5:
                    persons = _IRR_PRES_PERSONS[i]
                else:
                    persons = ()
                add(f, lemma, {feat, *persons})
    for lemma, table in _EN_FORMS.items():
        for key, forms in table.items():
            for f in forms:
                add(f, lemma, _EN_FEATS[key] | {"EN"})

    exact_out = {f: [(lem, frozenset(ft)) for lem, ft in d.items()] for f, d in exact.items()}
    folded: dict[str, dict[str, set]] = {}
    for form, analyses in exact_out.items():
        for lem, ft in analyses:
            folded.setdefault(fold(form), {}).setdefault(lem, set()).update(ft)
    folded_out = {f: [(lem, frozenset(ft)) for lem, ft in d.items()] for f, d in folded.items()}
    return exact_out, folded_out


_EXACT, _FOLDED = _build()

# Accent-free spellings that are overwhelmingly function words: an accent-
# folded verb form must never capture them ("du" is not "dû").
_FOLD_STOPLIST = {"du"}


def lookup(low: str) -> tuple[list[Analysis], bool]:
    """Return (analyses, accent_ambiguous) for a lowercase token.

    An accented spelling is authoritative ("à" is never "a"). An accent-free
    spelling may be an accent-stripped verb form, so every reading of the
    folded form is kept and the token is flagged as ambiguous.
    """
    folded_form = fold(low)
    typed_without_accents = low == folded_form
    if low in _EXACT:
        exact = _EXACT[low]
        folded = _FOLDED.get(folded_form, exact)
        if typed_without_accents and folded != exact:
            return folded, True
        return exact, False
    if typed_without_accents and low not in _FOLD_STOPLIST and low in _FOLDED:
        return _FOLDED[low], True
    return [], False


def predicate_of(lemma: str) -> tuple[str, str]:
    return LEMMAS.get(lemma, (lemma.upper(), "other"))


def has_imperative_paradigm(lemma: str) -> bool:
    """Whether the lexicon knows this lemma's imperative forms (every -er verb, and the
    irregular tables with an IMP row); False means the lexicon is silent, not that no
    imperative exists ("voir")."""
    return lemma in _ER_VERBS or "IMP" in _IRREGULAR.get(lemma, {})
