"""
tests/integration_cognition/test_native_public_wiring_red.py

RED contracts: the native realization layer must be reachable from the public
Brody entry point for structures the SENS frame fully captures, must NOT be
called when the structure is ambiguous or incomplete, and every admitted
auxiliary statement must declare who formulated it.
"""
from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from periphery.language.lexical_corpus import DB_PATH

pytestmark = pytest.mark.skipif(not DB_PATH.exists(), reason="linguistic corpus not built")


# Admissibility of a statement for native realization ---------------------------

@pytest.mark.parametrize("stmt,expected", [
    ("Les opérateurs ne vérifiaient pas la vanne principale.", "Les opérateurs ne vérifiaient pas la vanne principale"),
    ("L'opérateur vérifiera la vanne.", "L'opérateur vérifiera la vanne"),
    ("Le technicien a lancé le test.", "Le technicien a lancé le test"),
    ("Le technicien principal lance le test.", "Le technicien principal lance le test"),
])
def test_wiring_admissible_statements_are_realized_natively(stmt, expected):
    from apps.obsidia_api.brody_true_voice_adapter import _reconstruct_with_provenance

    text, provenance = _reconstruct_with_provenance(stmt, fr=True)
    assert provenance == "NATIVE_REALIZATION"
    assert text == expected


@pytest.mark.parametrize("stmt", [
    "Le technicien a lancé le test hier.",              # deixis would be lost
    "Le technicien lance le test dans le hangar.",      # oblique would be lost
    "L'opérateur ne vérifie jamais la vanne.",          # negator other than pas
    "L'opérateur doit vérifier la vanne.",              # modality
    "L'opérateur vérifie la vanne et la pompe.",        # coordination
    "L'opérateur avait vérifié la vanne.",              # pluperfect unsupported
    "Le technicien répare la pompe.",                   # verb outside the sealed lexicon: no unit
    "The operator checks the valve.",                   # no English SENS parser
])
def test_wiring_inadmissible_statements_are_not_realized(stmt):
    from apps.obsidia_api.brody_true_voice_adapter import _reconstruct_with_provenance

    _text, provenance = _reconstruct_with_provenance(stmt, fr=not stmt.startswith("The "))
    assert provenance != "NATIVE_REALIZATION"


# Public entry point ------------------------------------------------------------

def _chat(reply: str, message: str, language: str):
    from apps.obsidia_api.routes.brody import BrodyChatRequest, brody_chat
    from tests.integration_cognition.test_brody_qwen_cognitive_collaboration_red import (
        _is_model_endpoint_call,
        _mock_qwen_http_response,
    )

    with patch("urllib.request.urlopen") as mock_http:
        mock_http.side_effect = lambda req_obj, timeout=None: (
            _mock_qwen_http_response(reply)
            if _is_model_endpoint_call(req_obj)
            else MagicMock(read=lambda: b'{"status":"healthy"}', __enter__=lambda s: s, __exit__=lambda s, *a: False)
        )
        return asyncio.run(brody_chat(BrodyChatRequest(message=message, language=language, allow_local_model=True)))


def _spy_realizations(monkeypatch):
    import periphery.language.native_realization as nr

    calls = []
    original = nr.realize_semantic_relation

    def spy(*args, **kwargs):
        out = original(*args, **kwargs)
        calls.append(out)
        return out

    monkeypatch.setattr(nr, "realize_semantic_relation", spy)
    return calls


def test_wiring_public_brody_chat_reaches_native_realization(monkeypatch):
    calls = _spy_realizations(monkeypatch)
    res = _chat("Les opérateurs ne vérifiaient pas la vanne principale.",
                "Quel est l'état de la vanne Omega-9 ?", "fr")

    assert any(c["text"] == "Les opérateurs ne vérifiaient pas la vanne principale." for c in calls)
    assert "les opérateurs ne vérifiaient pas la vanne principale" in res["final_answer"].lower()
    snap = res["true_voice_snapshot"]
    assert "NATIVE_REALIZATION" in snap["formulation_provenance"]
    assert res["decision_authority"] == "KX108_ONLY"
    assert res["cognitive_runtime_receipt"]["neural_generation_snapshot"]["qwen_authority"] == "NONE"


def test_wiring_public_english_declares_auxiliary_wording_dependency(monkeypatch):
    calls = _spy_realizations(monkeypatch)
    res = _chat("The operator checks the valve.", "What is the status of the Omega-9 valve?", "en")

    assert calls == []
    snap = res["true_voice_snapshot"]
    assert snap["formulation_provenance"]
    assert "NATIVE_REALIZATION" not in snap["formulation_provenance"]
    assert snap["auxiliary_wording_dependency"] is True


def test_wiring_public_ambiguous_input_is_not_forced(monkeypatch):
    calls = _spy_realizations(monkeypatch)
    res = _chat("L'opérateur ne vérifie jamais la vanne.", "Quel est l'état de la vanne Omega-9 ?", "fr")

    assert calls == []
    assert res["true_voice_snapshot"]["auxiliary_wording_dependency"] is True
