import json
import inspect
import sys
from pathlib import Path
from fastapi.testclient import TestClient

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))

import apps.obsidia_api.routes.brody as brody_route
from apps.obsidia_api.main import app
from apps.obsidia_api.brody_text_encoding import (
    repair_mojibake_via_latin1_roundtrip,
    is_mojibake,
    normalize_brody_text,
)

print("=== MODULE FILES ===")
print("brody_route_file=", brody_route.__file__)
print("has_last_mile=", hasattr(brody_route, "_last_mile_brody_utf8_repair"))
print("has_repair_func=", callable(repair_mojibake_via_latin1_roundtrip))

print("\n=== ROUTE SOURCE MARKERS ===")
src = inspect.getsource(brody_route)
for marker in [
    "_last_mile_brody_utf8_repair",
    "repair_mojibake_via_latin1_roundtrip",
    "return",
]:
    print(marker, "=", marker in src)

print("\n=== DIRECT REPAIR TEST ===")
bad = "_Brody â rÃ©ponse structurÃ©e readonly. KX108_ONLY. Pas de dÃ©cision, pas d'Ã©criture mÃ©moire._"
print("bad=", bad)
print("bad_is_mojibake=", is_mojibake(bad))
fixed = repair_mojibake_via_latin1_roundtrip(bad)
print("fixed=", fixed)
print("fixed_is_mojibake=", is_mojibake(fixed))
print("fixed_has_reponse=", "réponse" in fixed)
print("fixed_has_decision=", "décision" in fixed)
print("fixed_has_memoire=", "mémoire" in fixed)

print("\n=== TESTCLIENT /api/brody/chat ===")
client = TestClient(app, raise_server_exceptions=False)
resp = client.post("/api/brody/chat", json={
    "message": "explique X108 avec la mémoire actuelle",
    "language": "fr",
    "session_id": "diagnostic_testclient_last_mile",
})
print("status_code=", resp.status_code)
body = resp.json()
fa = body.get("final_answer", "")
print("topic=", body.get("topic"))
print("final_answer_source=", body.get("final_answer_source"))
print("neo4j_write=", body.get("neo4j_write"))
print("final_answer=", fa)
print("final_contains_mojibake=", bool(("Ã" in fa) or ("â" in fa)))
print("final_contains_reponse=", "réponse" in fa)
print("final_contains_decision=", "décision" in fa)
print("final_contains_memoire=", "mémoire" in fa)

out = ROOT / "_local_audits/BRODY_LAST_MILE_LIVE_MISMATCH/diagnostic_testclient.json"
out.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
print("SAVED=", out)
