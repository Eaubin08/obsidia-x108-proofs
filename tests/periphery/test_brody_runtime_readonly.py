import pytest
from periphery.brody.brody_runtime_readonly import brody_respond


def test_brody_responds():
    r = brody_respond("What is X-108?", "en")
    assert r.readonly is True
    assert r.response_text != ""


def test_brody_emits_no_act():
    r = brody_respond("Should I deploy?", "en")
    assert r.emits_act is False


def test_brody_no_memory_write():
    r = brody_respond("Remember this fact", "en")
    assert r.memory_write is False


def test_brody_decision_authority_kx108():
    r = brody_respond("Authorize the action", "en")
    assert r.contract["decision_authority"] == "KX108_ONLY"


def test_brody_dict_fields():
    r = brody_respond("context query", "fr")
    d = r.to_dict()
    assert "readonly" in d
    assert "emits_act" in d
    assert d["emits_act"] is False
