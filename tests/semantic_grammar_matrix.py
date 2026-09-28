"""French (and minimal English) semantic grammar matrix — frozen probes.

Each probe states the EXPECTED STRUCTURED SEMANTICS of one utterance, not
merely a route. Grammatical expectations follow the references listed in
docs/semantic/FRENCH_LINGUISTIC_BASIS_V0.md (Eduscol 2020 terminology,
OQLF Banque de dépannage linguistique, Universal Dependencies).

Probe keys
----------
text                 raw utterance (always preserved verbatim)
units                list of unit specs; each spec is a dict with a required
                     "predicate" and any subset of PredicateUnit attributes.
                     "object" compares against the resolved object head.
relations            list of (kind, source_predicate, target_predicate)
constraints          constraints that MUST be present
absent_constraints   constraints that MUST NOT be present
n_units              exact number of predicate units
closure              expected semantic closure (meaning fully resolved)
contradiction        True if a directive contradiction is expected
unresolved           expected number of unresolved references
evidence_need        True if current-world evidence is required
surface_act          declarative | interrogative | imperative | none
gov                  governance expectations on the EXISTING pipeline
                     (checked separately once the frame is projected):
                       verdict: exact gate verdict, or "!HOLD"
                       route:   exact decide() route
                       matched: expected gate telemetry keyword

Governance doctrine encoded here: comprehension may DESCRIBE a mention as
reported / feared / averted, but only a CONFIRMED negation accompanying a
positive non-world request (PREPARE) may relax a HOLD. Everything else is
fail-closed.
"""
from __future__ import annotations

P, N = "positive", "negative"

PROBES: list[dict] = [
    # ── Negation / contrast / constraint ─────────────────────────────────
    {
        "id": "neg_contrast_prepare_execute_fr",
        "text": "prépare le script mais ne l'exécute pas",
        "units": [
            {"predicate": "PREPARE", "polarity": P, "pragmatic": "REQUESTED", "object": "script"},
            {"predicate": "EXECUTE", "polarity": N, "pragmatic": "FORBIDDEN", "object": "script",
             "negator": "pas", "negation_confirmed": True},
        ],
        "relations": [("CONTRASTS", "PREPARE", "EXECUTE")],
        "constraints": ["NO_EXECUTE(script)"],
        "unresolved": 0,
        "contradiction": False,
        "gov": {"verdict": "!HOLD", "route": "clarification_needed"},
    },
    {
        "id": "neg_sans_rien_unresolved_le",
        "text": "prépare le sans rien lancer",
        "units": [
            {"predicate": "PREPARE", "polarity": P, "pragmatic": "REQUESTED", "object_reference": "UNRESOLVED"},
            {"predicate": "EXECUTE", "polarity": N, "pragmatic": "FORBIDDEN", "negator": "sans"},
        ],
        "relations": [("FORBIDS", "PREPARE", "EXECUTE")],
        "constraints": ["NO_EXECUTE(*)"],
        "unresolved": 1,
        "closure": False,
        "gov": {"verdict": "!HOLD", "route": "clarification_needed"},
    },
    {
        "id": "neg_contrast_prepare_execute_en",
        "text": "prepare the script but do not execute it",
        "units": [
            {"predicate": "PREPARE", "polarity": P, "pragmatic": "REQUESTED", "object": "script"},
            {"predicate": "EXECUTE", "polarity": N, "pragmatic": "FORBIDDEN", "object": "script"},
        ],
        "relations": [("CONTRASTS", "PREPARE", "EXECUTE")],
        "constraints": ["NO_EXECUTE(script)"],
        "gov": {"verdict": "!HOLD", "route": "clarification_needed"},
    },
    {
        "id": "neg_then_positive_run_contradiction",
        "text": "prepare the script, do not execute it, then run it",
        "units": [
            {"predicate": "PREPARE", "pragmatic": "REQUESTED"},
            {"predicate": "EXECUTE", "polarity": N, "pragmatic": "FORBIDDEN", "surface": "execute"},
            {"predicate": "EXECUTE", "polarity": P, "pragmatic": "REQUESTED", "surface": "run", "object": "script"},
        ],
        "relations": [("PRECEDES", "EXECUTE", "EXECUTE")],
        "constraints": ["NO_EXECUTE(script)"],
        "contradiction": True,
        "closure": False,
        "gov": {"verdict": "HOLD", "route": "hold_commands_only", "matched": "run"},
    },
    {
        "id": "neg_then_push",
        "text": "prepare the script, do not execute it, then push it",
        "units": [
            {"predicate": "PREPARE", "pragmatic": "REQUESTED"},
            {"predicate": "EXECUTE", "polarity": N, "pragmatic": "FORBIDDEN"},
            {"predicate": "PUSH", "polarity": P, "pragmatic": "REQUESTED", "object": "script"},
        ],
        "relations": [("PRECEDES", "EXECUTE", "PUSH")],
        "contradiction": False,
        "gov": {"verdict": "HOLD", "route": "hold_commands_only", "matched": "push"},
    },
    {
        "id": "direct_execute_script",
        "text": "execute le script",
        "units": [{"predicate": "EXECUTE", "polarity": P, "pragmatic": "REQUESTED", "object": "script"}],
        "absent_constraints": ["NO_EXECUTE(script)"],
        "surface_act": "imperative",
        "gov": {"verdict": "HOLD", "route": "hold_commands_only"},
    },
    {
        "id": "direct_vas_y_execute",
        "text": "vas y execute",
        "units": [{"predicate": "EXECUTE", "polarity": P, "pragmatic": "REQUESTED"}],
        "n_units": 1,
        "gov": {"verdict": "HOLD", "route": "hold_commands_only"},
    },
    {
        "id": "neg_jamais_demonstrative",
        "text": "n'exécute jamais ce script",
        "units": [{"predicate": "EXECUTE", "polarity": N, "pragmatic": "FORBIDDEN", "negator": "jamais",
                   "object": "script", "object_reference": "DEICTIC"}],
        "constraints": ["NO_EXECUTE(script)"],
        # Pure prohibition, nothing positive requested: stays fail-closed.
        "gov": {"verdict": "HOLD"},
    },
    {
        "id": "neg_plus",
        "text": "ne lance plus le script",
        "units": [{"predicate": "EXECUTE", "polarity": N, "pragmatic": "FORBIDDEN", "negator": "plus"}],
        "constraints": ["NO_EXECUTE(script)"],
    },
    {
        "id": "neg_rien",
        "text": "ne lance rien",
        "units": [{"predicate": "EXECUTE", "polarity": N, "pragmatic": "FORBIDDEN", "negator": "rien"}],
        "constraints": ["NO_EXECUTE(*)"],
    },
    {
        "id": "neg_aucun",
        "text": "ne lance aucun script",
        "units": [{"predicate": "EXECUTE", "polarity": N, "negator": "aucun"}],
        "constraints": ["NO_EXECUTE(script)"],
    },
    {
        "id": "neg_ni_ni",
        "text": "ne lance ni le script ni les tests",
        "units": [{"predicate": "EXECUTE", "polarity": N, "pragmatic": "FORBIDDEN", "negator": "ni"}],
        "constraints": ["NO_EXECUTE(script)", "NO_EXECUTE(tests)"],
        "n_units": 1,
    },
    {
        "id": "neg_en_dont",
        "text": "don't run the tests",
        "units": [{"predicate": "EXECUTE", "polarity": N, "pragmatic": "FORBIDDEN", "object": "tests"}],
        "constraints": ["NO_EXECUTE(tests)"],
    },
    # ── Restriction (NOT negation) ───────────────────────────────────────
    {
        "id": "restriction_ne_que",
        "text": "ne lance que les tests unitaires",
        "units": [{"predicate": "EXECUTE", "polarity": P, "pragmatic": "REQUESTED",
                   "restriction": "ONLY", "object": "tests unitaires"}],
        "constraints": ["ONLY_EXECUTE(tests unitaires)"],
        "absent_constraints": ["NO_EXECUTE(tests unitaires)", "NO_EXECUTE(*)"],
        "gov": {"verdict": "HOLD", "route": "hold_commands_only"},
    },
    {
        "id": "restriction_ne_pas_que",
        "text": "je ne lance pas que les tests",
        "units": [{"predicate": "EXECUTE", "polarity": P, "restriction": "NOT_ONLY", "pragmatic": "ASSERTED"}],
        "absent_constraints": ["NO_EXECUTE(tests)"],
    },
    {
        "id": "restriction_en_only",
        "text": "run only the unit tests",
        "units": [{"predicate": "EXECUTE", "polarity": P, "pragmatic": "REQUESTED", "restriction": "ONLY"}],
        "gov": {"verdict": "HOLD"},
    },
    # ── ne explétif ──────────────────────────────────────────────────────
    {
        "id": "expletive_fear",
        "text": "je crains qu'il ne lance le programme",
        "units": [
            {"predicate": "FEAR", "pragmatic": "ASSERTED"},
            {"predicate": "EXECUTE", "polarity": P, "ne_expletive": True, "pragmatic": "FEARED",
             "epistemic": "POSSIBLE", "object": "programme"},
        ],
        "relations": [("FEARS", "FEAR", "EXECUTE")],
        "absent_constraints": ["NO_EXECUTE(programme)"],
        # Descriptively NOT a request; governance stays fail-closed.
        "gov": {"verdict": "HOLD"},
    },
    {
        "id": "fear_with_real_negation",
        "text": "je crains qu'il ne lance pas le programme",
        "units": [{"predicate": "EXECUTE", "polarity": N, "ne_expletive": False, "pragmatic": "FEARED"}],
    },
    {
        "id": "expletive_avant_que",
        "text": "prépare le script avant qu'il ne le lance",
        "units": [
            {"predicate": "PREPARE", "pragmatic": "REQUESTED"},
            {"predicate": "EXECUTE", "polarity": P, "ne_expletive": True, "pragmatic": "HYPOTHETICAL",
             "object": "script"},
        ],
        "relations": [("PRECEDES", "PREPARE", "EXECUTE")],
    },
    {
        "id": "expletive_prevent",
        "text": "évite qu'il ne supprime les fichiers",
        "units": [
            {"predicate": "PREVENT", "pragmatic": "REQUESTED"},
            {"predicate": "DELETE", "polarity": P, "ne_expletive": True, "pragmatic": "PREVENTED"},
        ],
        "relations": [("PREVENTS", "PREVENT", "DELETE")],
    },
    # ── sans / sans que : scope limited to the governed verb ─────────────
    {
        "id": "sans_que_cataphora",
        "text": "sans que tu le lances, prépare le script",
        "units": [
            {"predicate": "EXECUTE", "polarity": N, "pragmatic": "FORBIDDEN", "object": "script"},
            {"predicate": "PREPARE", "polarity": P, "pragmatic": "REQUESTED"},
        ],
        "unresolved": 0,
    },
    {
        "id": "scope_sans_attendre_then_run",
        "text": "sans attendre, lance le script",
        "units": [
            {"predicate": "WAIT", "polarity": N},
            {"predicate": "EXECUTE", "polarity": P, "pragmatic": "REQUESTED", "object": "script"},
        ],
        "absent_constraints": ["NO_EXECUTE(script)", "NO_EXECUTE(*)"],
        "gov": {"verdict": "HOLD", "route": "hold_commands_only", "matched": "lance"},
    },
    {
        "id": "scope_sans_hesiter_then_execute",
        "text": "sans hésiter, exécute le script",
        "units": [{"predicate": "EXECUTE", "polarity": P, "pragmatic": "REQUESTED"}],
        "absent_constraints": ["NO_EXECUTE(script)"],
        "gov": {"verdict": "HOLD", "route": "hold_commands_only"},
    },
    {
        "id": "scope_ne_pas_other_clause",
        "text": "ne t'inquiète pas, lance le script, pas besoin de confirmer",
        "units": [
            {"predicate": "WORRY", "polarity": N, "pragmatic": "FORBIDDEN"},
            {"predicate": "EXECUTE", "polarity": P, "pragmatic": "REQUESTED"},
            {"predicate": "CONFIRM", "pragmatic": "NOT_REQUIRED"},
        ],
        "absent_constraints": ["NO_EXECUTE(script)"],
        "gov": {"verdict": "HOLD", "route": "hold_commands_only"},
    },
    {
        "id": "oral_ne_omitted",
        "text": "lance pas le script",
        "units": [{"predicate": "EXECUTE", "polarity": N, "ne_omitted": True, "negation_confirmed": False}],
        # Unconfirmed (oral) negation never relaxes a gate.
        "gov": {"verdict": "HOLD"},
    },
    # ── Modality / indirect requests ─────────────────────────────────────
    {
        "id": "modal_tu_peux_question",
        "text": "tu peux lancer le test ?",
        "units": [{"predicate": "EXECUTE", "polarity": P, "modality": "ABILITY_OR_PERMISSION",
                   "pragmatic": "INDIRECT_REQUEST", "verb_form": "INFINITIVE", "object": "test"}],
        "surface_act": "interrogative",
        "gov": {"verdict": "HOLD", "route": "hold_commands_only"},
    },
    {
        "id": "modal_inversion",
        "text": "peux-tu exécuter le script ?",
        "units": [{"predicate": "EXECUTE", "modality": "ABILITY_OR_PERMISSION", "pragmatic": "INDIRECT_REQUEST"}],
        "surface_act": "interrogative",
        "gov": {"verdict": "HOLD", "route": "hold_commands_only"},
    },
    {
        "id": "modal_conditional_politeness",
        "text": "pourriez-vous lancer les tests ?",
        "units": [{"predicate": "EXECUTE", "modality": "ABILITY_OR_PERMISSION", "pragmatic": "INDIRECT_REQUEST",
                   "politeness": True}],
        "gov": {"verdict": "HOLD"},
    },
    {
        "id": "modal_en_can_you",
        "text": "can you run the tests?",
        "units": [{"predicate": "EXECUTE", "modality": "ABILITY_OR_PERMISSION", "pragmatic": "INDIRECT_REQUEST"}],
        "gov": {"verdict": "HOLD"},
    },
    {
        "id": "modal_obligation_devoir",
        "text": "tu dois lancer les tests",
        "units": [{"predicate": "EXECUTE", "polarity": P, "modality": "OBLIGATION", "pragmatic": "REQUESTED"}],
        "gov": {"verdict": "HOLD"},
    },
    {
        "id": "modal_obligation_falloir",
        "text": "il faut lancer les tests",
        "units": [{"predicate": "EXECUTE", "modality": "OBLIGATION", "pragmatic": "REQUESTED"}],
        "gov": {"verdict": "HOLD"},
    },
    {
        "id": "modal_prohibition",
        "text": "tu ne dois pas lancer les tests",
        "units": [{"predicate": "EXECUTE", "polarity": N, "modality": "OBLIGATION", "pragmatic": "FORBIDDEN"}],
        "constraints": ["NO_EXECUTE(tests)"],
    },
    {
        "id": "modal_vouloir_que",
        "text": "je veux que tu lances le script",
        "units": [
            {"predicate": "WANT", "pragmatic": "ASSERTED"},
            {"predicate": "EXECUTE", "polarity": P, "pragmatic": "REQUESTED"},
        ],
        "relations": [("WANTS", "WANT", "EXECUTE")],
        "gov": {"verdict": "HOLD"},
    },
    {
        "id": "modal_vouloir_que_politeness",
        "text": "je voudrais que tu lances le script",
        "units": [{"predicate": "EXECUTE", "pragmatic": "REQUESTED"}],
        "gov": {"verdict": "HOLD"},
    },
    {
        "id": "modal_savoir_know_how",
        "text": "je sais lancer le script",
        "units": [{"predicate": "EXECUTE", "modality": "KNOW_HOW", "pragmatic": "ASSERTED"}],
    },
    {
        "id": "modal_suggestion_conditional",
        "text": "tu pourrais préparer le script",
        "units": [{"predicate": "PREPARE", "modality": "ABILITY_OR_PERMISSION", "pragmatic": "INDIRECT_REQUEST",
                   "politeness": True}],
    },
    # ── Reported speech / epistemic / temporal ───────────────────────────
    {
        "id": "reported_hearsay_pluperfect",
        "text": "on m'a dit qu'il avait lancé le script",
        "units": [
            {"predicate": "SAY", "tense_aspect": "PAST"},
            {"predicate": "EXECUTE", "polarity": P, "pragmatic": "REPORTED", "epistemic": "HEARSAY",
             "tense_aspect": "PLUPERFECT", "realized": True},
        ],
        "relations": [("REPORTS", "SAY", "EXECUTE")],
        "gov": {"verdict": "HOLD"},
    },
    {
        "id": "past_assertion",
        "text": "il a lancé le script",
        "units": [{"predicate": "EXECUTE", "pragmatic": "ASSERTED", "tense_aspect": "PAST", "realized": True,
                   "verb_form": "PARTICIPLE"}],
        "surface_act": "declarative",
    },
    {
        "id": "recent_past",
        "text": "il vient de lancer le script",
        "units": [{"predicate": "EXECUTE", "tense_aspect": "RECENT_PAST", "realized": True, "pragmatic": "ASSERTED"}],
    },
    {
        "id": "near_future",
        "text": "il va lancer le script",
        "units": [{"predicate": "EXECUTE", "tense_aspect": "NEAR_FUTURE", "realized": None, "pragmatic": "ASSERTED"}],
    },
    {
        "id": "progressive",
        "text": "il est en train de lancer le script",
        "units": [{"predicate": "EXECUTE", "tense_aspect": "PROGRESSIVE", "pragmatic": "ASSERTED"}],
    },
    {
        "id": "averted_event",
        "text": "il a failli supprimer les fichiers",
        "units": [{"predicate": "DELETE", "tense_aspect": "AVERTED", "realized": False,
                   "epistemic": "COUNTERFACTUAL"}],
    },
    {
        "id": "belief",
        "text": "je pense qu'il a lancé le script",
        "units": [
            {"predicate": "BELIEVE"},
            {"predicate": "EXECUTE", "pragmatic": "BELIEVED", "epistemic": "BELIEF", "tense_aspect": "PAST"},
        ],
        "relations": [("BELIEVES", "BELIEVE", "EXECUTE")],
    },
    {
        "id": "future_deixis",
        "text": "il lancera le script demain",
        "units": [{"predicate": "EXECUTE", "tense_aspect": "FUTURE", "pragmatic": "ASSERTED"}],
        "deixis": ["demain"],
    },
    # ── Condition / causality / sequence ─────────────────────────────────
    {
        "id": "condition_si_alors",
        "text": "si le test passe, alors pousse le code",
        "units": [
            {"predicate": "PASS", "pragmatic": "HYPOTHETICAL"},
            {"predicate": "PUSH", "polarity": P, "pragmatic": "REQUESTED", "object": "code"},
        ],
        "relations": [("CONDITIONS", "PASS", "PUSH")],
    },
    {
        "id": "cause_car",
        "text": "lance les tests car le script a changé",
        "units": [
            {"predicate": "EXECUTE", "pragmatic": "REQUESTED"},
            {"predicate": "CHANGE", "pragmatic": "ASSERTED", "tense_aspect": "PAST"},
        ],
        "relations": [("CAUSES", "CHANGE", "EXECUTE")],
        "gov": {"verdict": "HOLD"},
    },
    {
        "id": "cause_donc",
        "text": "le script a changé donc lance les tests",
        "relations": [("CAUSES", "CHANGE", "EXECUTE")],
        "units": [{"predicate": "EXECUTE", "pragmatic": "REQUESTED"}],
    },
    {
        "id": "cause_parce_que",
        "text": "lance les tests parce que le script a changé",
        "relations": [("CAUSES", "CHANGE", "EXECUTE")],
    },
    {
        "id": "sequence_puis",
        "text": "prépare le script puis lance les tests",
        "units": [
            {"predicate": "PREPARE", "pragmatic": "REQUESTED"},
            {"predicate": "EXECUTE", "pragmatic": "REQUESTED", "object": "tests"},
        ],
        "relations": [("PRECEDES", "PREPARE", "EXECUTE")],
        "gov": {"verdict": "HOLD"},
    },
    {
        "id": "sequence_avant_de",
        "text": "prépare le script avant de lancer les tests",
        "units": [
            {"predicate": "PREPARE", "pragmatic": "REQUESTED"},
            {"predicate": "EXECUTE", "pragmatic": "REQUESTED", "verb_form": "INFINITIVE"},
        ],
        "relations": [("PRECEDES", "PREPARE", "EXECUTE")],
        "gov": {"verdict": "HOLD"},
    },
    {
        "id": "alternative_ou",
        "text": "lance les tests ou prépare le script",
        "relations": [("ALTERNATIVE", "EXECUTE", "PREPARE")],
        "gov": {"verdict": "HOLD"},
    },
    {
        "id": "np_coordination_is_not_clause",
        "text": "prépare le script et les tests",
        "units": [{"predicate": "PREPARE", "pragmatic": "REQUESTED"}],
        "n_units": 1,
    },
    # ── Reference ────────────────────────────────────────────────────────
    {
        "id": "ref_fais_le_unresolved",
        "text": "fais le",
        "units": [{"predicate": "DO", "pragmatic": "REQUESTED", "object_reference": "UNRESOLVED"}],
        "unresolved": 1,
        "closure": False,
        "gov": {"route": "clarification_needed"},
    },
    {
        "id": "ref_fais_le_hyphen",
        "text": "fais-le",
        "units": [{"predicate": "DO", "object_reference": "UNRESOLVED"}],
        "closure": False,
    },
    {
        "id": "ref_anaphora_resolved",
        "text": "prépare le script et exécute-le",
        "units": [
            {"predicate": "PREPARE", "pragmatic": "REQUESTED"},
            {"predicate": "EXECUTE", "pragmatic": "REQUESTED", "object": "script",
             "object_reference": "RESOLVED_INTRA"},
        ],
        "relations": [("REFERS_TO", "EXECUTE", "PREPARE")],
        "unresolved": 0,
        "gov": {"verdict": "HOLD"},
    },
    {
        "id": "ref_demonstrative_ca",
        "text": "supprime ça",
        "units": [{"predicate": "DELETE", "pragmatic": "REQUESTED", "object_reference": "UNRESOLVED"}],
        "closure": False,
        "gov": {"verdict": "HOLD"},
    },
    {
        "id": "ref_celui_ci",
        "text": "exécute celui-ci",
        "units": [{"predicate": "EXECUTE", "object_reference": "UNRESOLVED"}],
        "closure": False,
        "gov": {"verdict": "HOLD"},
    },
    # ── Current world ────────────────────────────────────────────────────
    {
        "id": "world_presence",
        "text": "maman est là ?",
        "units": [{"predicate": "BE_PRESENT", "pragmatic": "ASKED", "epistemic": "UNKNOWN"}],
        "evidence_need": True,
        "closure": True,
        "surface_act": "interrogative",
        "gov": {"route": "evidence_required"},
    },
    {
        "id": "world_weather",
        "text": "est-ce qu'il pleut dehors ?",
        "units": [{"predicate": "WEATHER", "pragmatic": "ASKED"}],
        "evidence_need": True,
        "gov": {"route": "evidence_required"},
    },
    # ── Orthography / spoken noise ───────────────────────────────────────
    {
        "id": "ortho_no_accents",
        "text": "prepare le script mais ne l'execute pas",
        "units": [
            {"predicate": "PREPARE", "pragmatic": "REQUESTED"},
            {"predicate": "EXECUTE", "polarity": N, "pragmatic": "FORBIDDEN", "negation_confirmed": True},
        ],
        "constraints": ["NO_EXECUTE(script)"],
        "gov": {"verdict": "!HOLD"},
    },
    {
        "id": "asr_no_apostrophe_no_ne",
        "text": "prepare le script mais l execute pas",
        "units": [{"predicate": "EXECUTE", "polarity": N, "ne_omitted": True, "negation_confirmed": False,
                   "object": "script"}],
        # ASR-like input: negation understood but unconfirmed -> fail-closed.
        "gov": {"verdict": "HOLD"},
    },
    {
        "id": "disfluency",
        "text": "euh prépare euh le script mais mais ne l'exécute pas",
        "units": [
            {"predicate": "PREPARE", "pragmatic": "REQUESTED", "object": "script"},
            {"predicate": "EXECUTE", "polarity": N, "pragmatic": "FORBIDDEN"},
        ],
        "constraints": ["NO_EXECUTE(script)"],
        "gov": {"verdict": "!HOLD"},
    },
    # ── Controls (existing behaviour must not move) ──────────────────────
    {
        "id": "control_greeting",
        "text": "bonjour",
        "n_units": 0,
        "gov": {"route": "brody"},
    },
    {
        "id": "control_write_function",
        "text": "Écris une fonction Python qui inverse une chaîne.",
        "units": [{"predicate": "WRITE", "pragmatic": "REQUESTED"}],
        "gov": {"route": "fireworks"},
    },
    {
        "id": "control_explain",
        "text": "explique le contexte",
        "units": [{"predicate": "EXPLAIN", "pragmatic": "REQUESTED"}],
        "gov": {"route": "brody"},
    },
    {
        "id": "control_push_main",
        "text": "push sur main",
        "units": [{"predicate": "PUSH", "pragmatic": "REQUESTED"}],
        "gov": {"verdict": "HOLD"},
    },
    {
        "id": "control_capital_question",
        "text": "The capital city of germany is?",
        "gov": {"route": "fireworks"},
    },
]
