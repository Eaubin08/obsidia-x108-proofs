"""Action-agent and request-target projection tests.

These tests separate mentioning an action from requesting the governed
addressee/system to perform it. Gates remain fail-closed separately.
"""

import pytest

from app.ir.unified_ir import build_ir
from app.semantic.lattice.french_grammar import parse_utterance


def _unit(raw: str, predicate: str = "EXECUTE"):
    frame = parse_utterance(raw)
    for unit in frame.units:
        if unit.predicate == predicate:
            return frame, unit
    raise AssertionError(f"{predicate} not found in {raw!r}: {frame.units!r}")


def _summary(raw: str):
    return build_ir(raw)["semantics"]


@pytest.mark.parametrize(
    "raw, target",
    [
        ("lance le test", "ADDRESSEE"),
        ("peux-tu lancer le test ?", "ADDRESSEE_OR_POSSIBLE_ADDRESSEE"),
        ("tu peux lancer le test ?", "ADDRESSEE_OR_POSSIBLE_ADDRESSEE"),
        ("pourrais-tu lancer le test ?", "ADDRESSEE_OR_POSSIBLE_ADDRESSEE"),
    ],
)
def test_addressee_execution_requests_project_as_requested(raw, target):
    frame, unit = _unit(raw)

    assert unit.action_agent == "ADDRESSEE"
    assert unit.request_target == target
    assert unit.role in {"REQUEST", "AMBIGUOUS_REQUEST"}
    assert unit.pragmatic in {"REQUESTED", "INDIRECT_REQUEST"}
    if "peux" in raw or "pourrais" in raw:
        assert unit.modality == "ABILITY_OR_PERMISSION"
        assert any("ability_permission_or_request" in a for a in frame.ambiguities)

    summary = _summary(raw)
    assert "EXECUTE" in summary["requested_world_actions"]


@pytest.mark.parametrize(
    "raw",
    [
        "est-ce que je peux lancer le test ?",
        "puis-je lancer le test ?",
        "est-ce que j'ai le droit de lancer le test ?",
        "je veux lancer le test",
    ],
)
def test_speaker_actions_are_not_system_execution_requests(raw):
    _, unit = _unit(raw)

    assert unit.action_agent == "SPEAKER"
    assert unit.request_target == "NONE"
    assert unit.role in {"PERMISSION_QUERY", "DESIRE_ASSERTION", "MENTION"}
    assert "EXECUTE" not in _summary(raw)["requested_world_actions"]


@pytest.mark.parametrize(
    "raw",
    [
        "Paul peut lancer le test ?",
        "il doit lancer le test",
        "est-ce qu'ils peuvent lancer le test ?",
    ],
)
def test_third_party_actions_are_not_system_execution_requests(raw):
    _, unit = _unit(raw)

    assert unit.action_agent == "THIRD_PARTY"
    assert unit.request_target == "NONE"
    assert unit.role in {"THIRD_PARTY_ACTION", "MENTION"}
    assert "EXECUTE" not in _summary(raw)["requested_world_actions"]


@pytest.mark.parametrize(
    "raw",
    [
        "dis-moi comment lancer le test",
        "explique comment exécuter le script",
        "tu peux m'expliquer comment lancer le test ?",
        "comment lancer le test ?",
    ],
)
def test_explanation_content_is_not_requested_execution(raw):
    _, unit = _unit(raw)

    assert unit.role == "EXPLANATION_CONTENT"
    assert unit.request_target == "NONE"
    assert "EXECUTE" not in _summary(raw)["requested_world_actions"]


@pytest.mark.parametrize(
    "raw, role",
    [
        ("pour lancer le test, ouvre le terminal", "PURPOSE"),
        ("avant de lancer le test, vérifie le build", "TEMPORAL_CONTEXT"),
        ("après avoir lancé le test, vérifie les logs", "TEMPORAL_CONTEXT"),
    ],
)
def test_purpose_and_temporal_context_are_not_requested_execution(raw, role):
    _, unit = _unit(raw)

    assert unit.role == role
    assert unit.request_target == "NONE"
    assert "EXECUTE" not in _summary(raw)["requested_world_actions"]


@pytest.mark.parametrize(
    "raw, role",
    [
        ("on m'a dit que tu pouvais lancer le test", "REPORTED"),
        ("je pense que tu peux lancer le test", "BELIEVED"),
        ("il paraît qu'il peut lancer le test", "REPORTED"),
    ],
)
def test_reported_and_believed_actions_are_not_requested_execution(raw, role):
    _, unit = _unit(raw)

    assert unit.role == role
    assert unit.request_target == "NONE"
    assert "EXECUTE" not in _summary(raw)["requested_world_actions"]


@pytest.mark.parametrize(
    "raw",
    [
        "ne lance pas le test",
        "n'oublie pas de ne pas lancer le test",
    ],
)
def test_negated_execution_is_not_positive_requested_execution(raw):
    _, unit = _unit(raw)

    assert unit.polarity == "negative"
    assert unit.role == "NEGATED"
    assert unit.request_target == "NONE"
    assert "EXECUTE" not in _summary(raw)["requested_world_actions"]
