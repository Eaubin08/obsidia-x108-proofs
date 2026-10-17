"""
tests/integration_cognition/test_provenance_honesty_red.py

RED contracts: the public provenance of each admitted auxiliary statement must
state exactly what was done to it. Reusing the auxiliary wording after a
morphology regeneration that reproduced it is NOT a grammatical, semantic or
factual verification, and the auxiliary wording dependency must be declared.
"""
from __future__ import annotations

import asyncio
import json
from unittest.mock import MagicMock, patch

import pytest

from periphery.language.lexical_corpus import DB_PATH

pytestmark = pytest.mark.skipif(not DB_PATH.exists(), reason="linguistic corpus not built")

NOT_EVALUATED = {"GRAMMAR_GENERAL", "VALENCY", "SEMANTIC_FIDELITY", "CROSS_STATEMENT_CONSISTENCY", "FACTUAL_TRUTH"}


def _record(stmt: str, fr: bool = True) -> dict:
    from apps.obsidia_api.brody_true_voice_adapter import _reconstruct_with_record

    return _reconstruct_with_record(stmt, fr=fr)


# Internal records ----------------------------------------------------------------

def test_honesty_reused_wording_record():
    rec = _record("Les opérateurs ne vérifiaient pas la vanne principale.")
    assert rec["provenance"] == "AUXILIARY_WORDING_REUSED"
    assert rec["origin"] == "AUXILIARY_MODEL"
    assert rec["realizer_called"] is True
    assert rec["realizer_regeneration_matched"] is True
    assert rec["applied"] == "AUXILIARY_TEXT"
    assert set(rec["checks_performed"]) >= {"VERB_MORPHOLOGY_REGENERATED", "NOUN_PHRASE_AGREEMENT"}
    assert set(rec["not_evaluated"]) >= NOT_EVALUATED


def test_honesty_realizer_called_without_match_is_not_reuse_by_regeneration():
    rec = _record("Le technicien vérifient la vanne.")
    assert rec["realizer_called"] is True
    assert rec["realizer_regeneration_matched"] is False
    assert rec["provenance"] == "AUXILIARY_WORDING_PRESERVED"
    assert rec["applied"] == "AUXILIARY_TEXT"


def test_honesty_no_realizer_for_english():
    rec = _record("The operator checks the valve.", fr=False)
    assert rec["realizer_called"] is False
    assert rec["provenance"] == "AUXILIARY_WORDING_PRESERVED"


def test_honesty_no_provenance_value_claims_verification():
    from apps.obsidia_api import brody_true_voice_adapter as adapter

    src = open(adapter.__file__, encoding="utf-8").read()
    assert "NATIVE_VERIFIED_ECHO" not in src


# Public brody_chat ------------------------------------------------------------------

def _chat(reply: str, monkeypatch, language: str = "fr"):
    import periphery.language.native_realization as nr
    from apps.obsidia_api.routes.brody import BrodyChatRequest, brody_chat
    from tests.integration_cognition.test_brody_qwen_cognitive_collaboration_red import (
        _is_model_endpoint_call,
        _mock_qwen_http_response,
    )

    calls = []
    original = nr.realize_semantic_relation

    def spy(*args, **kwargs):
        out = original(*args, **kwargs)
        calls.append(out)
        return out

    monkeypatch.setattr(nr, "realize_semantic_relation", spy)
    with patch("urllib.request.urlopen") as mock_http:
        mock_http.side_effect = lambda req_obj, timeout=None: (
            _mock_qwen_http_response(reply)
            if _is_model_endpoint_call(req_obj)
            else MagicMock(read=lambda: b'{"status":"healthy"}', __enter__=lambda s: s, __exit__=lambda s, *a: False)
        )
        message = "Quel est l'état de la vanne Omega-9 ?" if language == "fr" else "What is the status of the Omega-9 valve?"
        res = asyncio.run(brody_chat(BrodyChatRequest(message=message, language=language, allow_local_model=True)))
    return res, calls


def _assert_honest(snap: dict):
    assert snap["auxiliary_wording_dependency"] is True
    for rec in snap["formulation_records"]:
        assert set(rec["not_evaluated"]) >= NOT_EVALUATED
        assert rec["origin"] == "AUXILIARY_MODEL"
    assert "VERIFIED" not in snap["native_linguistic_level"]
    assert "NATIVE" not in snap["native_linguistic_level"] or snap["native_linguistic_level"] == "NOT_APPLIED"


@pytest.mark.parametrize("reply", [
    "Les opérateurs ne vérifiaient pas la vanne principale.",   # reused wording
    "J'vérifie la vanne.",                                       # ungrammatical
    "La vanne vérifie le technicien.",                           # semantically absurd
    "Le technicien vérifie la vanne. Le technicien ne vérifie pas la vanne.",  # contradiction
    "Le technicien vérifie la vanne !",                          # punctuation
    "The operator checks the valve.",                            # no native realization
    "Le technicien vérifient la vanne.",                         # realizer called, no effective match
])
def test_honesty_public_metadata(reply, monkeypatch):
    language = "en" if reply.startswith("The ") else "fr"
    res, _calls = _chat(reply, monkeypatch, language)
    snap = res["true_voice_snapshot"]
    _assert_honest(snap)
    assert "NATIVE_VERIFIED_ECHO" not in json.dumps(res, ensure_ascii=False, default=str)
    assert res["decision_authority"] == "KX108_ONLY"


def test_honesty_public_text_identity_is_not_overclaimed(monkeypatch):
    res, _ = _chat("Le technicien vérifie la vanne !", monkeypatch)
    recs = res["true_voice_snapshot"]["formulation_records"]
    assert recs and all(r["text_identity"] != "EXACT" for r in recs)


def test_honesty_public_reuse_records_realizer_call(monkeypatch):
    res, calls = _chat("Les opérateurs ne vérifiaient pas la vanne principale.", monkeypatch)
    recs = res["true_voice_snapshot"]["formulation_records"]
    assert calls and recs[0]["realizer_called"] is True and recs[0]["realizer_regeneration_matched"] is True
    assert res["true_voice_snapshot"]["formulation_provenance"] == ["AUXILIARY_WORDING_REUSED"]
