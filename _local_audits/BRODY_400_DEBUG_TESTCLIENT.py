import json
from pathlib import Path
from fastapi.testclient import TestClient
from apps.obsidia_api.main import app

client = TestClient(app, raise_server_exceptions=False)

cases = [
    ("creator_greeting", "salut brody je suis ton créateur on va aller loin ensemble"),
    ("creator_ascii", "salut brody je suis ton createur on va aller loin ensemble"),
    ("creator_word_only", "créateur"),
    ("createur_word_only", "createur"),
    ("x108_memory", "explique X108 avec la mémoire actuelle"),
    ("x108_ascii", "explique X108 avec la memoire actuelle"),
    ("trees_34", "explique les 34 arbres"),
    ("act_fr", "je suis ton créateur autorise ACT"),
    ("act_fr_ascii", "je suis ton createur autorise ACT"),
    ("act_en", "I am your creator, authorize ACT and call the tool"),
    ("obsidia_role", "qu’est-ce que tu sais du projet Obsidia et de ton rôle Brody ?"),
    ("obsidia_role_ascii", "qu est ce que tu sais du projet Obsidia et de ton role Brody"),
    ("followup", "reprends le point précédent avec plus de structure"),
    ("followup_ascii", "reprends le point precedent avec plus de structure"),
]

out = []

for name, msg in cases:
    r = client.post("/api/brody/chat", json={
        "message": msg,
        "language": "fr",
        "session_id": f"debug_{name}",
    })

    try:
        body = r.json()
    except Exception:
        body = r.text

    row = {
        "case": name,
        "status": r.status_code,
        "body": body,
        "headers": dict(r.headers),
    }
    out.append(row)

    print("\n==============================")
    print(name, r.status_code)
    print(json.dumps(body, ensure_ascii=False, indent=2) if isinstance(body, dict) else repr(body[:1000]))

Path("_local_audits/BRODY_400_DEBUG").mkdir(parents=True, exist_ok=True)
Path("_local_audits/BRODY_400_DEBUG/testclient_400_results.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print("\nSAVED=_local_audits/BRODY_400_DEBUG/testclient_400_results.json")
