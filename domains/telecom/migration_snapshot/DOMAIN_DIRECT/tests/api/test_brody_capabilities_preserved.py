import json
from fastapi.testclient import TestClient
from apps.obsidia_api.main import app


client = TestClient(app)


def _post(message: str, session_id: str):
    response = client.post(
        "/api/brody/chat",
        json={
            "message": message,
            "session_id": session_id,
            "compact": False,
            "debug": True,
        },
    )
    assert response.status_code == 200, response.text
    raw = response.content.decode("utf-8", errors="replace")
    json.loads(raw)
    return raw, response.json()


def test_french_utf8_capability_preserved():
    raw, _ = _post(
        "Brody, réponds en français naturel. Test accents : é è à ç œ.",
        "pytest_cap_fr_utf8",
    )
    bad_patterns = ["Ã©", "Ã¨", "Ã§", "Ã ", "â€™", "�", "RequÃ", "franÃ", "RÃ"]
    found = [p for p in bad_patterns if p in raw]
    assert not found, f"Mojibake detected: {found}\nRAW={raw[:1000]}"


def test_english_understanding_capability_preserved():
    raw, _ = _post(
        "Brody, answer in English. Explain what you are in two short sentences. Do not take action.",
        "pytest_cap_en",
    )
    assert raw.strip()


def test_code_answering_capability_preserved():
    raw, _ = _post(
        "Brody, explain this Python bug briefly: print(undefined_variable). Safe diagnostic only.",
        "pytest_cap_code",
    )
    assert raw.strip()
    assert "undefined" in raw.lower() or "variable" in raw.lower() or "python" in raw.lower()


def test_true_voice_runtime_metadata_present_or_response_nonempty():
    raw, data = _post(
        "Qui es-tu Brody ? Réponds en français naturel, readonly.",
        "pytest_cap_voice",
    )
    serialized = str(data)
    assert raw.strip()
    assert (
        "BRODY" in serialized.upper()
        or "V1_4_12A" in serialized
        or "voice" in serialized.lower()
        or "runtime" in serialized.lower()
    )
