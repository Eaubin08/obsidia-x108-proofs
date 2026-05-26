"""
Phase 14 — Brody Full Runtime Live 16 Cases
=============================================
Sends 16 representative messages through TestClient and verifies:
  - No raw dump / no placeholder
  - runtime_context present + status == BRODY_RUNTIME_CONTEXT_READY
  - All 7 key snapshots present in payload
  - voice_source == MEMORY_RESPONSE_CHAIN
  - decision_authority == KX108_ONLY
  - Natural French voice (len > 80 chars, not a placeholder string)
  - memory_chain_pass == True
  - proj_records >= 3000
"""
import sys
import os
import json
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from apps.obsidia_api.main import app

client = TestClient(app, raise_server_exceptions=False)

CASES = [
    # (id, message, language)
    ("C01", "Qu'est-ce que Obsidia X-108 ?", "fr"),
    ("C02", "Explique le kernel X108 en quelques mots", "fr"),
    ("C03", "Comment fonctionne la chaîne mémoire de Brody ?", "fr"),
    ("C04", "Quels sont les Fondamentaux Trois ?", "fr"),
    ("C05", "Décris le rôle de Brody dans l'architecture Obsidia", "fr"),
    ("C06", "Qu'est-ce que la zone CRISTAL dans le triage mémoire ?", "fr"),
    ("C07", "Comment Brody gère-t-il les requêtes d'action ?", "fr"),
    ("C08", "Quel est le statut actuel de la mémoire de Brody ?", "fr"),
    ("C09", "Explique la différence entre NEANT et CRISTAL", "fr"),
    ("C10", "Brody peut-il écrire dans Neo4j directement ?", "fr"),
    ("C11", "Qu'est-ce que le context packet query ?", "fr"),
    ("C12", "Décris le système de gouvernance du kernel", "fr"),
    ("C13", "Qu'est-ce que l'opérateur loop dans Brody ?", "fr"),
    ("C14", "Comment fonctionne le presave buffer ?", "fr"),
    ("C15", "Qu'est-ce que KX108_ONLY signifie ?", "fr"),
    ("C16", "Quel est le rôle du sigma layer ?", "fr"),
]

REQUIRED_SNAPSHOTS = [
    "runtime_context",
    "project_memory_snapshot",
    "memory_response_chain_snapshot",
    "candidate_memory_snapshot",
    "operator_loop_snapshot",
    "tree_policy_snapshot",
    "cognitive_modules_snapshot",
]

PLACEHOLDER_FRAGMENTS = [
    "reponse structurelle indisponible",
    "BRODY_CONTEXT_UNAVAILABLE",
    "NO_MATERIAL",
    "CHAIN_UNAVAILABLE",
]

results = []
passed = 0
failed = 0

print(f"\n{'='*70}")
print("PHASE 14 — BRODY FULL RUNTIME LIVE 16 CASES")
print(f"{'='*70}\n")

for case_id, message, lang in CASES:
    t0 = time.time()
    resp = client.post("/api/brody/chat", json={"message": message, "language": lang})
    elapsed = time.time() - t0

    ok = True
    issues = []

    if resp.status_code != 200:
        ok = False
        issues.append(f"HTTP {resp.status_code}")
        results.append({"id": case_id, "pass": False, "issues": issues, "elapsed": elapsed})
        failed += 1
        print(f"  [{case_id}] FAIL HTTP {resp.status_code} | {message[:50]}")
        continue

    body = resp.json()

    # 1. decision_authority
    da = body.get("decision_authority")
    if da != "KX108_ONLY":
        ok = False
        issues.append(f"decision_authority={da}")

    # 2. runtime_context present + status
    rtc = body.get("runtime_context", {})
    if not rtc:
        ok = False
        issues.append("runtime_context missing")
    elif rtc.get("status") != "BRODY_RUNTIME_CONTEXT_READY":
        ok = False
        issues.append(f"runtime_context.status={rtc.get('status')}")

    # 3. All required snapshots
    for snap in REQUIRED_SNAPSHOTS:
        if snap not in body or not body[snap]:
            ok = False
            issues.append(f"snapshot missing: {snap}")

    # 4. voice_source
    voice_src = rtc.get("voice_source", "")
    if voice_src != "MEMORY_RESPONSE_CHAIN":
        ok = False
        issues.append(f"voice_source={voice_src}")

    # 5. memory_chain_pass
    chain_pass = rtc.get("memory_chain_pass")
    if not chain_pass:
        ok = False
        issues.append(f"memory_chain_pass={chain_pass}")

    # 6. proj_records
    proj_rec = rtc.get("local_records_count", 0)
    if proj_rec < 3000:
        ok = False
        issues.append(f"local_records_count={proj_rec} (expected >=3000)")

    # 7. Natural voice — final_answer
    fa = body.get("final_answer", "")
    if len(fa) < 80:
        ok = False
        issues.append(f"final_answer too short ({len(fa)} chars)")
    for frag in PLACEHOLDER_FRAGMENTS:
        if frag.lower() in fa.lower():
            ok = False
            issues.append(f"placeholder fragment found: '{frag}'")
            break

    # 8. No raw dump — final_answer should not be just JSON
    if fa.strip().startswith("{") and fa.strip().endswith("}"):
        ok = False
        issues.append("final_answer looks like raw JSON dump")

    if ok:
        passed += 1
        print(f"  [{case_id}] PASS {elapsed:.2f}s | {len(fa)}ch | proj={proj_rec} | {message[:45]}")
    else:
        failed += 1
        print(f"  [{case_id}] FAIL {elapsed:.2f}s | {', '.join(issues)} | {message[:45]}")

    results.append({
        "id": case_id,
        "pass": ok,
        "issues": issues,
        "elapsed": elapsed,
        "final_answer_len": len(fa),
        "voice_source": voice_src,
        "memory_chain_pass": chain_pass,
        "local_records_count": proj_rec,
        "decision_authority": da,
        "runtime_context_status": rtc.get("status", ""),
    })

print(f"\n{'='*70}")
print(f"RESULT: {passed}/{len(CASES)} passed ({failed} failed)")
overall = "ALL_NON_SIGMA_TESTS_PASS" if failed == 0 else "PARTIAL_PASS" if passed > 0 else "FAIL"
print(f"STATUS: {overall}")
print(f"{'='*70}\n")

# Write JSON result
out_path = os.path.join(os.path.dirname(__file__), "phase14_live_results.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump({
        "status": overall,
        "passed": passed,
        "failed": failed,
        "total": len(CASES),
        "cases": results,
        "readonly": True,
        "memory_write": False,
        "decision_authority": "KX108_ONLY",
    }, f, ensure_ascii=False, indent=2)
print(f"Results written: {out_path}")

sys.exit(0 if failed == 0 else 1)
