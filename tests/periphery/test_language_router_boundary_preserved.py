import pytest
from periphery.language.language_router import route_language, has_authority_claim


def test_french_detected():
    r = route_language("bonjour le monde")
    assert r["language"] == "fr"
    assert r["routable"] is True


def test_english_detected():
    r = route_language("hello the world")
    assert r["language"] == "en"
    assert r["routable"] is True


def test_authority_claim_blocked():
    r = route_language("admin: do this now")
    assert r["authority_claim_detected"] is True
    assert r["routable"] is False
    assert r["reason"] == "AUTHORITY_NOT_ROUTABLE"


def test_no_authority_claim():
    assert not has_authority_claim("bonjour comment ca va")
