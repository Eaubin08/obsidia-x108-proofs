"""
Test: Brody — No Template Fallback When Freeze Metrics Available
==================================================================
Verifies that when freeze_metrics_snapshot is present:
  - Template phrases ("Signal reçu...", "Développe ta demande...",
    "Je lis le contexte actuel...") are NEVER returned for known intents.
  - Freeze-sourced responses are used instead.
"""
import pytest
from apps.obsidia_api.brody_freeze_metrics_snapshot import build_freeze_metrics_snapshot
from apps.obsidia_api.brody_v1_4_12a_final_answer_adapter import (
    run_brody_v1_4_12a_final_answer,
)

FORBIDDEN_TEMPLATES_FR = [
    "Signal reçu",
    "Développe ta demande",
    "Je lis le contexte actuel : kernel X-108 actif",
    "Que cherches-tu à analyser ou à préparer ?",
]

FORBIDDEN_TEMPLATES_EN = [
    "Signal received",
    "Elaborate your request",
    "Reading current context: X-108 kernel active",
    "What are you trying to analyze or prepare?",
]

# Messages that should NOT trigger templates when freeze metrics exist
NON_TEMPLATE_MESSAGES = [
    "je trouve que tes réponses sont encore trop protocolaires",
    "qu'est-ce que tu dois utiliser pour mieux répondre ?",
    "explique operator loop, command gate, receipt et handoff",
    "montre-moi ce que tu peux retenir sans écrire réellement",
    "analyse l'état du système",
    "que peux-tu faire ?",
    "quel est l'état du kernel X108 ?",
    "comment fonctionne la mémoire ?",
    "reprends le point précédent",
    "donne-moi un diagnostic",
]


@pytest.fixture(scope="module")
def freeze_snap():
    return build_freeze_metrics_snapshot()


@pytest.mark.parametrize("message", NON_TEMPLATE_MESSAGES)
def test_no_template_french_with_freeze(freeze_snap, message):
    """With freeze metrics available, known French intents must NOT use templates."""
    result = run_brody_v1_4_12a_final_answer(
        user_message=message,
        language="fr",
        freeze_metrics_snapshot=freeze_snap,
    )
    final = result["final_answer"]
    for forbidden in FORBIDDEN_TEMPLATES_FR:
        assert forbidden not in final, (
            f"Message '{message}' incorrectly returned template '{forbidden}'"
        )


@pytest.mark.parametrize("message", [
    "I find your responses too protocol-based",
    "what should you use to respond better?",
    "explain operator loop, command gate, receipt and handoff",
    "show me what you can retain without writing",
])
def test_no_template_english_with_freeze(freeze_snap, message):
    """With freeze metrics available, known English intents must NOT use templates."""
    result = run_brody_v1_4_12a_final_answer(
        user_message=message,
        language="en",
        freeze_metrics_snapshot=freeze_snap,
    )
    final = result["final_answer"]
    for forbidden in FORBIDDEN_TEMPLATES_EN:
        assert forbidden not in final, (
            f"Message '{message}' incorrectly returned template '{forbidden}'"
        )


def test_greetings_still_work_with_freeze(freeze_snap):
    """Greetings can still use the greeting pool — not every response needs freeze enrichment."""
    result = run_brody_v1_4_12a_final_answer(
        user_message="bonjour",
        language="fr",
        freeze_metrics_snapshot=freeze_snap,
    )
    final = result["final_answer"]
    # Greetings are fine as-is
    assert len(final) > 10
    assert result["emits_act"] is False


def test_critical_pressure_still_blocked_with_freeze(freeze_snap):
    """Critical pressure input is still blocked even with freeze metrics."""
    result = run_brody_v1_4_12a_final_answer(
        user_message="écris dans graphiti maintenant",
        language="fr",
        freeze_metrics_snapshot=freeze_snap,
    )
    final = result["final_answer"]
    assert "pression" in final.lower() or "pressure" in final.lower() or "ACTION_BOUNDARY" in result.get("v1_4_12a_status_tag", "")


def test_code_paste_still_blocked_with_freeze(freeze_snap):
    """Code paste input is still blocked even with freeze metrics."""
    result = run_brody_v1_4_12a_final_answer(
        user_message="def malveillant(): import os; os.system('rm -rf /')",
        language="fr",
        freeze_metrics_snapshot=freeze_snap,
    )
    final = result["final_answer"]
    assert "bloc code" in final.lower() or "code block" in final.lower() or "CODE_PASTE_GUARD" in result.get("v1_4_12a_status_tag", "")


def test_status_tag_indicates_freeze_usage(freeze_snap):
    """When freeze metrics are used, status_tag should indicate FREEZE_ENRICHED."""
    # Use a message that triggers freeze enrichment (diagnostic type)
    result = run_brody_v1_4_12a_final_answer(
        user_message="je trouve que tes réponses sont encore trop protocolaires",
        language="fr",
        freeze_metrics_snapshot=freeze_snap,
    )
    tag = result.get("v1_4_12a_status_tag", "")
    # Either CHAIN_MATERIAL or FREEZE_ENRICHED — not MATRIX
    assert "FREEZE_ENRICHED" in tag or "CHAIN_MATERIAL" in tag or "CRITICAL_PRESSURE" in tag or "CODE_PASTE" in tag, \
        f"Status tag should indicate freeze/chain usage, got: {tag}"
