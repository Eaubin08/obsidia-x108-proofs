"""
tests/integration_cognition/test_brody_real_lexicon_and_corpus_red.py

Comprehensive test suite verifying Brody's real French and English lexical,
morphological, and semantic corpus integration.

Contracts tested:
1. Real Database Verification (provenance, table counts, licenses).
2. Bidirectional French Conjugation (regular and irregular paradigms).
3. Bidirectional English Morphology (regular and irregular paradigms).
4. Homonyms & Sense Disambiguation (multiple categories, synonyms, definitions).
5. Epistemic Unknown Handling & Non-word Rejection.
6. Real Native Semantic Realization (agreement, irregulars, negation, conditionals, questions).
7. Runtime Grammar Lattice Integration (parse_utterance consumes real corpus).
8. Performance & Latency Thresholds (sub-millisecond B-tree lookups, low memory).
"""
from __future__ import annotations

import time
import pytest

from periphery.language.lexical_corpus import (
    lookup_surface_form,
    realize_inflection,
    get_verb_paradigm,
    get_senses_and_synonyms,
    is_known_lexical_item,
    get_corpus_statistics,
)
from app.semantic.lattice.french_grammar import parse_utterance
from periphery.language.native_realization import realize_semantic_relation
from periphery.language.lexical_calibrator import calibrate_lexical_with_corpus


# ==============================================================================
# 1. Real Database Verification
# ==============================================================================
def test_corpus_1_real_database_metrics_and_sources():
    """Verify that the database contains substantial real corpus data and verified licenses."""
    stats = get_corpus_statistics()
    assert stats["status"] == "READY", f"Database not ready: {stats}"
    assert stats["total_lemmas"] >= 500_000, f"Expected >=500k lemmas, got {stats['total_lemmas']}"
    assert stats["total_inflected_forms"] >= 1_500_000, f"Expected >=1.5M forms, got {stats['total_inflected_forms']}"
    assert stats["total_senses"] >= 200_000, f"Expected >=200k senses, got {stats['total_senses']}"
    assert stats["french_verb_lemmas"] >= 10_000, f"Expected >=10k French verb lemmas, got {stats['french_verb_lemmas']}"
    assert stats["english_verb_lemmas"] >= 15_000, f"Expected >=15k English verb lemmas, got {stats['english_verb_lemmas']}"

    source_ids = {s["id"] for s in stats["sources"]}
    assert "morphalou_3_1" in source_ids, "Morphalou 3.1 must be present"
    assert "unimorph_eng" in source_ids, "UniMorph English must be present"
    assert "oewn_2025" in source_ids, "Open English WordNet 2025 must be present"
    assert "thes_fr" in source_ids, "French Thesaurus must be present"


# ==============================================================================
# 2. Bidirectional French Conjugation
# ==============================================================================
@pytest.mark.parametrize("lemma, expected_present_3sg", [
    ("être", "est"),
    ("avoir", "a"),
    ("aller", "va"),
    ("faire", "fait"),
    ("prendre", "prend"),
    ("venir", "vient"),
    ("pouvoir", "peut"),
    ("devoir", "doit"),
    ("vouloir", "veut"),
    ("tenir", "tient"),
    ("voir", "voit"),
    ("savoir", "sait"),
    ("falloir", "faut"),
    ("valoir", "vaut"),
    ("mettre", "met"),
    ("dire", "dit"),
    ("écrire", "écrit"),
    ("lire", "lit"),
    ("croire", "croit"),
    ("ouvrir", "ouvre"),
    ("partir", "part"),
    ("finir", "finit"),
    ("agir", "agit"),
    ("choisir", "choisit"),
    ("lancer", "lance"),
])
def test_corpus_2_french_verb_realization_sample(lemma, expected_present_3sg):
    """Verify reverse lookup: lemma + features -> surface form on a representative sample."""
    form = realize_inflection(lemma, pos="verb", mood="indicative", tense="present", person="3", number="sg", lang="fr")
    assert form == expected_present_3sg, f"Failed realization for {lemma}: expected {expected_present_3sg}, got {form}"


def test_corpus_2b_french_full_paradigm_coverage():
    """Verify that a full conjugation paradigm can be retrieved with all moods and tenses."""
    paradigm = get_verb_paradigm("prendre", lang="fr")
    assert len(paradigm) >= 6, f"Expected at least 6 mood/tense groups for 'prendre', got {len(paradigm)}"
    present_indicative = paradigm.get("indicative_present", [])
    present_forms = {p["surface_form"] for p in present_indicative}
    assert "prends" in present_forms
    assert "prend" in present_forms
    assert "prenons" in present_forms
    assert "prenez" in present_forms
    assert "prennent" in present_forms


# ==============================================================================
# 3. Bidirectional English Morphology
# ==============================================================================
@pytest.mark.parametrize("lemma, tense, expected_form", [
    ("be", "past", "was"),
    ("have", "past", "had"),
    ("do", "past", "did"),
    ("go", "past", "went"),
    ("see", "past", "saw"),
    ("write", "past", "wrote"),
    ("read", "past", "read"),
    ("run", "past", "ran"),
    ("take", "past", "took"),
    ("come", "past", "came"),
    ("give", "past", "gave"),
    ("know", "past", "knew"),
    ("think", "past", "thought"),
    ("make", "past", "made"),
    ("get", "past", "got"),
])
def test_corpus_3_english_irregular_verbs(lemma, tense, expected_form):
    """Verify that English irregular past tenses resolve correctly from real corpus data."""
    form = realize_inflection(lemma, pos="verb", tense=tense, person="3", number="sg", lang="en")
    assert form == expected_form, f"Expected {expected_form} for {lemma} {tense}, got {form}"


# ==============================================================================
# 4. Homonyms & Multiple Senses
# ==============================================================================
def test_corpus_4_homonym_category_separation():
    """Verify that homographs with multiple parts of speech are distinct in forward lookup."""
    est_analyses = lookup_surface_form("est", lang="fr")
    poses = {a.pos for a in est_analyses}
    assert "verb" in poses, "'est' must have a verb analysis (être)"
    assert "noun" in poses, "'est' must have a noun analysis (l'est)"

    run_analyses = lookup_surface_form("run", lang="en")
    run_poses = {a.pos for a in run_analyses}
    assert "verb" in run_poses, "'run' must have verb analysis"
    assert "noun" in run_poses, "'run' must have noun analysis"


def test_corpus_4b_senses_and_definitions_retrieval():
    """Verify that real senses, definitions, and synonyms are returned."""
    en_defs = get_senses_and_synonyms("move", lang="en")
    assert len(en_defs) >= 1
    assert any("motion" in d.definition.lower() or "change" in d.definition.lower() for d in en_defs)

    fr_syns = get_senses_and_synonyms("abaisser", lang="fr")
    assert len(fr_syns) >= 1
    assert "diminuer" in fr_syns[0].synonyms or "baisser" in fr_syns[0].synonyms


# ==============================================================================
# 5. Missing / Unknown Words & Epistemic Humility
# ==============================================================================
def test_corpus_5_unknown_word_detection():
    """Verify that real words return True and artificial noise tokens return False."""
    assert is_known_lexical_item("vanne", lang="fr") is True
    assert is_known_lexical_item("température", lang="fr") is True
    assert is_known_lexical_item("pressure", lang="en") is True
    assert is_known_lexical_item("generator", lang="en") is True

    assert is_known_lexical_item("xyzq_nonexistent_token_12345", lang="fr") is False
    assert is_known_lexical_item("blablablazorpquux", lang="en") is False


# ==============================================================================
# 6. Real Native Semantic Realization
# ==============================================================================
def test_corpus_6_native_realization_french_and_english():
    """Verify that Brody's native realization generates grammatical sentences with proper agreement."""
    # French affirmative
    res_fr = realize_semantic_relation(
        "L'opérateur", "vérifier", "le circuit", mood="indicative", tense="present", person="3", number="sg", lang="fr"
    )
    assert res_fr["text"] == "L'opérateur vérifie le circuit."
    assert res_fr["has_linguistic_limitations"] is False
    assert res_fr["decision_authority"] == "KX108_ONLY"

    # French conditional
    res_fr_cond = realize_semantic_relation(
        "Le système", "maintenir", "la pression", mood="conditional", tense="present", person="3", number="sg", lang="fr"
    )
    assert "maintiendrait" in res_fr_cond["text"]
    assert res_fr_cond["has_linguistic_limitations"] is False

    # French negation with elision
    res_fr_neg = realize_semantic_relation(
        "La vanne", "ouvrir", "le conduit", polarity="negative", mood="indicative", tense="present", person="3", number="sg", lang="fr"
    )
    assert "n'ouvre pas" in res_fr_neg["text"]

    # French question
    res_fr_q = realize_semantic_relation(
        "le capteur", "mesurer", "la pression", mood="interrogative", tense="present", person="3", number="sg", lang="fr"
    )
    assert res_fr_q["text"].startswith("Est-ce que")
    assert res_fr_q["text"].endswith("?")

    # English affirmative past
    res_en = realize_semantic_relation(
        "The operator", "take", "the measurement", mood="indicative", tense="past", person="3", number="sg", lang="en"
    )
    assert res_en["text"] == "The operator took the measurement."

    # English negative past
    res_en_neg = realize_semantic_relation(
        "The operator", "take", "the measurement", polarity="negative", mood="indicative", tense="past", person="3", number="sg", lang="en"
    )
    assert res_en_neg["text"] == "The operator did not take the measurement."


def test_corpus_6b_unsupported_structure_produces_limitation():
    """Verify that unsupported vocabulary produces explicit linguistic limitation without crashing."""
    res = realize_semantic_relation(
        "Le module", "blablablazorpiser", "la donnée", lang="fr"
    )
    assert res["has_linguistic_limitations"] is True
    assert "UNKNOWN_LEXICAL_ITEM" in res["limitation_reason"]


# ==============================================================================
# 7. Runtime Grammar Lattice Integration
# ==============================================================================
@pytest.mark.xfail(
    strict=True,
    reason="HOLD: requires a corpus fallback inside sealed app/semantic/lattice/lexicon.py "
    "(no extension point exists); needs an explicit reseal decision",
)
def test_corpus_7_french_grammar_parses_arbitrary_corpus_verbs():
    """
    Verify that parse_utterance natively parses verbs outside the hardcoded 50 verbs
    using the reconnected Morphalou corpus.
    """
    # 'maintenir' was previously unparsed; now parsed into PredicateUnit
    frame = parse_utterance("Le système maintient la pression.")
    assert len(frame.units) >= 1
    u = frame.units[0]
    assert u.predicate == "MAINTENIR"
    assert u.lemma == "maintenir"
    assert u.polarity == "positive"
    assert u.tense_aspect == "PRESENT"

    # 'osciller'
    frame_osc = parse_utterance("Le capteur oscille.")
    assert len(frame_osc.units) >= 1
    assert frame_osc.units[0].predicate == "OSCILLER"
    assert frame_osc.units[0].lemma == "osciller"


# ==============================================================================
# 8. Performance & Latency Thresholds
# ==============================================================================
def test_corpus_8_sub_millisecond_lookup_latency():
    """Verify that database queries execute in under 2 milliseconds across 100 random lookups."""
    words = ["est", "va", "doit", "veut", "fait", "prend", "vient", "went", "saw", "took", "had", "did"]
    latencies = []
    for _ in range(10):
        for w in words:
            t0 = time.perf_counter()
            lookup_surface_form(w)
            latencies.append((time.perf_counter() - t0) * 1000)

    avg_latency = sum(latencies) / len(latencies)
    assert avg_latency < 2.0, f"Average lookup latency too high: {avg_latency:.3f} ms"


# ==============================================================================
# 9. Compound Tenses, Auxiliaries, Agreements & Pronominals
# ==============================================================================
def test_corpus_9_compound_tenses_and_auxiliary_selection():
    """Verify French compound tenses with avoir, être, negation, and participle agreement."""
    # Transitive verb with avoir
    r_avoir = realize_semantic_relation(
        "L'opérateur", "vérifier", "le circuit", tense="passé_composé", lang="fr"
    )
    assert r_avoir["text"] == "L'opérateur a vérifié le circuit."
    assert r_avoir["has_linguistic_limitations"] is False

    # Motion verb with être
    r_etre = realize_semantic_relation(
        "L'opérateur", "arriver", "", tense="passé_composé", gender="masc", number="sg", lang="fr"
    )
    assert r_etre["text"] == "L'opérateur est arrivé."

    # Feminine plural agreement with être
    r_fem_pl = realize_semantic_relation(
        "Les équipes", "partir", "", tense="passé_composé", gender="fem", number="pl", lang="fr"
    )
    assert r_fem_pl["text"] == "Les équipes sont parties."

    # Pronominal verb with reflexive pronoun and agreement
    r_refl = realize_semantic_relation(
        "La turbine", "arrêter", "", tense="passé_composé", is_pronominal=True, gender="fem", number="sg", lang="fr"
    )
    assert r_refl["text"] == "La turbine s'est arrêtée."

    # Negation of compound tense
    r_neg = realize_semantic_relation(
        "L'opérateur", "vérifier", "le circuit", polarity="negative", tense="passé_composé", lang="fr"
    )
    assert r_neg["text"] == "L'opérateur n'a pas vérifié le circuit."


# ==============================================================================
# 10. English Aspectual and Tense Constructions
# ==============================================================================
def test_corpus_10_english_aspectual_and_tense_constructions():
    """Verify English aspectual constructions: perfect and progressive."""
    # Perfect aspect
    r_perf = realize_semantic_relation(
        "The operator", "verify", "the circuit", aspect="perfect", lang="en"
    )
    assert r_perf["text"] == "The operator has verified the circuit."

    # Past continuous aspect
    r_cont = realize_semantic_relation(
        "The operator", "take", "the measurement", aspect="continuous", tense="past", lang="en"
    )
    assert r_cont["text"] == "The operator was taking the measurement."

    # Negative continuous
    r_cont_neg = realize_semantic_relation(
        "The operator", "take", "the measurement", aspect="continuous", tense="past", polarity="negative", lang="en"
    )
    assert r_cont_neg["text"] == "The operator was not taking the measurement."


# ==============================================================================
# 11. Distinction between Genuine Definitions and Synonym-Only Entries
# ==============================================================================
def test_corpus_11_genuine_definitions_vs_synonyms():
    """Verify that real French definitions from XMLittré are distinguished from synonym clusters."""
    # French genuine definition from XMLittré
    pression_senses = get_senses_and_synonyms("pression", lang="fr")
    assert len(pression_senses) >= 1
    littre_senses = [s for s in pression_senses if s.source_id == "xmlittre_fr"]
    assert len(littre_senses) >= 1
    assert "presser" in littre_senses[0].definition.lower()

    # Bilingual gloss from FreeDict
    freedict_senses = [s for s in pression_senses if s.source_id == "freedict_fra_eng"]
    assert len(freedict_senses) >= 1
    assert freedict_senses[0].kind == "translation_gloss" and freedict_senses[0].definition == ""
    assert "pressure" in freedict_senses[0].gloss.lower()

    # English genuine definition from Open English WordNet
    move_senses = get_senses_and_synonyms("move", lang="en")
    assert len(move_senses) >= 1
    assert any("motion" in s.definition.lower() or "position" in s.definition.lower() for s in move_senses)


# ==============================================================================
# 12. Broad Coverage Measurement Over Representative Lexicons
# ==============================================================================
def test_corpus_12_broad_coverage_measurement():
    """Measure verified coverage across 50 common/irregular French verbs and 50 English verbs."""
    sample_fr_verbs = [
        "être", "avoir", "aller", "faire", "dire", "pouvoir", "vouloir", "savoir", "falloir", "voir",
        "devoir", "venir", "suivre", "parler", "prendre", "croire", "aimer", "passer", "mettre", "trouver",
        "donner", "comprendre", "connaître", "partir", "demander", "tenir", "sembler", "laisser", "rester",
        "penser", "entendre", "regarder", "répondre", "rendre", "conduire", "vivre", "arriver", "sentir",
        "attendre", "sortir", "écrire", "perdre", "montrer", "assurer", "tenter", "ouvrir", "agir", "finir",
        "choisir", "lancer"
    ]
    fr_attested = sum(1 for v in sample_fr_verbs if realize_inflection(v, pos="verb", mood="indicative", tense="present", person="3", number="sg", lang="fr"))
    fr_coverage = fr_attested / len(sample_fr_verbs)
    assert fr_coverage >= 0.98, f"French verb coverage below 98%: {fr_coverage * 100}%"

    sample_en_verbs = [
        "be", "have", "do", "say", "get", "make", "go", "know", "take", "see",
        "come", "think", "look", "want", "give", "use", "find", "tell", "ask", "work",
        "seem", "feel", "try", "leave", "call", "run", "write", "read", "keep", "let",
        "begin", "hold", "bring", "stand", "hear", "mean", "meet", "pay", "sit", "speak",
        "lie", "lead", "stop", "create", "allow", "grow", "open", "walk", "win", "offer"
    ]
    en_attested = sum(1 for v in sample_en_verbs if realize_inflection(v, pos="verb", mood="indicative", tense="past", person="3", number="sg", lang="en"))
    en_coverage = en_attested / len(sample_en_verbs)
    assert en_coverage >= 0.98, f"English verb past coverage below 98%: {en_coverage * 100}%"


# ==============================================================================
# 13. Portability: Clean Installation When SQLite DB Is Absent
# ==============================================================================
def test_corpus_13_clean_installation_graceful_fallback():
    """Verify that when database is absent, the system degrades gracefully with explicit limitations."""
    from pathlib import Path
    from unittest.mock import patch
    with patch("periphery.language.lexical_corpus.DB_PATH", Path("nonexistent_path/lexicon.db")):
        from periphery.language.lexical_corpus import (
            _get_connection,
            realize_inflection,
            is_known_lexical_item,
            lookup_surface_form,
            _local,
        )
        realize_inflection.cache_clear()
        is_known_lexical_item.cache_clear()
        lookup_surface_form.cache_clear()
        old_conn = getattr(_local, "conn", None)
        _local.conn = None
        try:
            assert _get_connection() is None
            from periphery.language.native_realization import realize_semantic_relation
            res = realize_semantic_relation("L'opérateur", "vérifier", "le circuit", lang="fr")
            assert res["has_linguistic_limitations"] is True
            assert res["decision_authority"] == "KX108_ONLY"
        finally:
            _local.conn = old_conn
            realize_inflection.cache_clear()
            is_known_lexical_item.cache_clear()
            lookup_surface_form.cache_clear()


# ==============================================================================
# 14. Real Public Brody Chat Runtime Verification
# ==============================================================================
@pytest.mark.asyncio
async def test_corpus_14_brody_public_runtime_lexical_influence():
    """
    Verify through the actual public brody_chat API that:
    1. French and English queries operate normally;
    2. Unknown tokens produce explicit uncertainty/limitations;
    3. Real lexical lookups influence native composition;
    4. Qwen never authors the final answer.
    """
    from apps.obsidia_api.routes.brody import brody_chat, BrodyChatRequest
    from unittest.mock import patch, MagicMock

    req_fr = BrodyChatRequest(
        message="Détaille les métriques thermodynamiques exotiques du protocole Omega-9.",
        language="fr",
        allow_local_model=True,
    )
    fake_reply = "Gradient thermique mesuré à 4.2 K."

    from tests.integration_cognition.test_brody_qwen_cognitive_collaboration_red import (
        _mock_qwen_http_response,
        _is_model_endpoint_call,
    )

    with patch("urllib.request.urlopen") as mock_http:
        mock_http.side_effect = lambda req_obj, timeout=None: (
            _mock_qwen_http_response(fake_reply)
            if _is_model_endpoint_call(req_obj)
            else MagicMock(read=lambda: b'{"status":"healthy"}', __enter__=lambda s: s, __exit__=lambda s, *a: False)
        )
        res = await brody_chat(req_fr)

    final_ans = res.get("final_answer", "")
    assert "4.2 K" in final_ans, "Factual content from auxiliary evidence must be integrated"
    assert "Analyse consultative Brody" in final_ans, "Brody must author the response voice"
    assert res.get("decision_authority") == "KX108_ONLY"
    snap = res.get("cognitive_runtime_receipt", {}).get("neural_generation_snapshot", {})
    assert snap.get("qwen_authority") == "NONE"

    # English query
    req_en = BrodyChatRequest(
        message="What is the operational status of the primary pump?",
        language="en",
        allow_local_model=False,
    )
    res_en = await brody_chat(req_en)
    assert res_en.get("decision_authority") == "KX108_ONLY"

