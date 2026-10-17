"""
tests/integration_cognition/test_brody_native_grammar_reconnection_red.py

RED Contract Suite for Brody Native Grammar Reconnection:
1. 'La température serait de 300 K.' must not establish a verified value.
2. 'La température est-elle de 300 K ?' must not resolve a knowledge gap.
3. 'La température reste inconnue.' must preserve the unknown.
4. 'La température est de 300 K.' may yield an answer candidate, not automatically verified truth.
5. Negation embedded in a subordinate clause must not negate unrelated claims.
6. Brody final wording must come from admitted structured relations, not merely regex substitution.
7. Unsupported grammatical structures must produce an explicit limitation, not fabricated semantic certainty.
"""

from __future__ import annotations

import pytest

from apps.obsidia_api.brody_neural_generation_adapter import (
    reassess_cognitive_evidence_delta,
)
from apps.obsidia_api.brody_true_voice_adapter import (
    extract_candidate_claims,
    synthesize_brody_native_claims,
)


# ==============================================================================
# 1. 'La température serait de 300 K.' must not establish a verified value
# ==============================================================================
def test_red_1_conditional_mood_does_not_establish_verified_value():
    """
    Conditional mood ('serait') expresses hypothesis, not established fact.
    reassess_cognitive_evidence_delta must NOT mark the unknown as addressed.
    """
    b6 = {"unknowns": ["temperature"]}
    res = reassess_cognitive_evidence_delta(
        round1_content="La température serait de 300 K.",
        b6_context_packet=b6,
        world_hypothesis_snapshot={},
        user_message="Quelle est la température ?",
    )
    assert res["has_residual"] is True, "1: Conditional mood must keep has_residual=True"
    assert "temperature" in res["residual_unknowns"], "1: Unknown must remain in residual_unknowns"
    assert "temperature" not in res["addressed_unknowns"], "1: Conditional statement must not address unknown as fact"

    claims = extract_candidate_claims("La température serait de 300 K.")
    assert len(claims) >= 1
    assert claims[0]["modality"] in ("HYPOTHETICAL", "CONDITIONAL", "ADVISORY"), (
        f"1: Claim modality must be non-factual, got: {claims[0]['modality']}"
    )


# ==============================================================================
# 2. 'La température est-elle de 300 K ?' must not resolve a knowledge gap
# ==============================================================================
def test_red_2_interrogative_does_not_resolve_knowledge_gap():
    """
    An interrogative sentence asking about a value must NEVER resolve the unknown.
    """
    b6 = {"unknowns": ["temperature"]}
    res = reassess_cognitive_evidence_delta(
        round1_content="La température est-elle de 300 K ?",
        b6_context_packet=b6,
        world_hypothesis_snapshot={},
        user_message="Quelle est la température ?",
    )
    assert res["has_residual"] is True, "2: Interrogative sentence must keep has_residual=True"
    assert "temperature" in res["residual_unknowns"], "2: Unknown must remain in residual_unknowns"
    assert "temperature" not in res["addressed_unknowns"], "2: Question cannot resolve an unknown"


# ==============================================================================
# 3. 'La température reste inconnue.' must preserve the unknown
# ==============================================================================
def test_red_3_unresolved_preserves_unknown():
    """
    Explicit negative assertion of ignorance must preserve the unknown.
    """
    b6 = {"unknowns": ["temperature"]}
    res = reassess_cognitive_evidence_delta(
        round1_content="La température reste inconnue et non mesurée.",
        b6_context_packet=b6,
        world_hypothesis_snapshot={},
        user_message="Quelle est la température ?",
    )
    assert res["has_residual"] is True, "3: 'reste inconnue' must keep has_residual=True"
    assert "temperature" in res["residual_unknowns"]
    assert "temperature" not in res["addressed_unknowns"]


# ==============================================================================
# 4. 'La température est de 300 K.' yields candidate, not verified truth
# ==============================================================================
def test_red_4_factual_assertion_yields_candidate_not_established_truth():
    """
    An affirmative statement provides a candidate answer, but KX108_ONLY remains
    sole decision authority, and established_facts remains empty.
    """
    b6 = {"unknowns": ["temperature"]}
    res = reassess_cognitive_evidence_delta(
        round1_content="La température est de 300 K.",
        b6_context_packet=b6,
        world_hypothesis_snapshot={},
        user_message="Quelle est la température ?",
    )
    assert "temperature" in res["addressed_unknowns"], "4: Factual assertion addresses unknown as candidate"

    claims = extract_candidate_claims("La température est de 300 K.")
    synth = synthesize_brody_native_claims(claims, user_message="Quelle est la température ?")
    assert synth["established_facts"] == [], "4: Auxiliary claim must not become established world fact"
    assert synth["decision_authority"] == "KX108_ONLY"
    assert "consultative" in synth["text"].lower() or "advisory" in synth["text"].lower()


# ==============================================================================
# 5. Negation in subordinate clause must not negate unrelated claims
# ==============================================================================
def test_red_5_subordinate_negation_does_not_negate_main_clause():
    """
    In 'Le système maintient la pression, bien que la vanne ne régule pas la température':
    1. 'pression' (main clause) is affirmed and must be in addressed_unknowns.
    2. 'temperature' (negated subordinate clause) is negated and must NOT be in addressed_unknowns.
    """
    b6 = {"unknowns": ["pression", "temperature"]}
    res = reassess_cognitive_evidence_delta(
        round1_content="Le système maintient la pression, bien que la vanne ne régule pas la température.",
        b6_context_packet=b6,
        world_hypothesis_snapshot={},
        user_message="Quels sont les états de la pression et de la température ?",
    )
    assert "pression" in res["addressed_unknowns"], "5: Main clause affirmation ('pression') must be addressed"
    assert "temperature" not in res["addressed_unknowns"], (
        f"5: Negated subordinate clause ('temperature') must NOT be addressed as a resolved fact. Got: {res}"
    )
    assert "temperature" in res["residual_unknowns"]


# ==============================================================================
# 6. Brody final wording must come from structured grammar relations
# ==============================================================================
def test_red_6_brody_final_wording_uses_grammar_engine_relations():
    """
    Brody native synthesis must connect to the deterministic grammar lattice
    (parse_utterance) to produce structured relations rather than pure regex substitution.
    """
    claims = extract_candidate_claims("L'opérateur vérifie la température du circuit.")
    synth = synthesize_brody_native_claims(
        claims,
        user_message="Que fait l'opérateur ?",
        language="fr",
    )
    assert synth.get("native_linguistic_level") == "GRAMMAR_LATTICE_ADAPTER", (
        f"6: Expected GRAMMAR_LATTICE_ADAPTER linguistic level, got {synth.get('native_linguistic_level')}"
    )
    assert "parsed_structures" in synth, "6: Synthesis must preserve parsed grammatical structures"


# ==============================================================================
# 7. Unsupported grammatical structures produce explicit limitation
# ==============================================================================
def test_red_7_unsupported_structures_produce_explicit_limitation():
    """
    Arbitrary opaque verbless fragments must not be fabricated into resolved factual certainty.
    They must be flagged with an explicit linguistic limitation.
    """
    b6 = {"unknowns": ["parametre_inconnu"]}
    res = reassess_cognitive_evidence_delta(
        round1_content="Blah qux baz quux random noise token sequence.",
        b6_context_packet=b6,
        world_hypothesis_snapshot={},
        user_message="Quel est le parametre inconnu ?",
    )
    assert res["has_residual"] is True, "7: Unparseable noise must not resolve unknown"
    assert "parametre_inconnu" not in res["addressed_unknowns"], "7: Noise tokens must not address unknown"

    claims = extract_candidate_claims("Blah qux baz quux random noise token sequence.")
    synth = synthesize_brody_native_claims(
        claims,
        user_message="Quel est ce statut ?",
        language="fr",
    )
    assert synth.get("has_linguistic_limitations") is True, (
        "7: Unsupported grammatical structures must set has_linguistic_limitations=True"
    )
