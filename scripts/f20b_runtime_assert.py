import json
import urllib.request

message = (
    "F20 runtime assert: expose gencoin_cognitive_ledger_packet depuis le vrai "
    "gencoin_shadow_packet, sans mint, sans wallet, sans blockchain, sans ACT."
)

for port in (8000, 8012):
    data = json.dumps({
        "message": message,
        "language": "fr",
        "session_id": f"f20b_runtime_assert_{port}",
    }).encode("utf-8")

    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/api/brody/chat",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(req, timeout=60) as r:
        p = json.loads(r.read().decode("utf-8"))

    with open(f"docs/runtime/F20B_{port}_GENCOIN_COGNITIVE_LEDGER_PAYLOAD.json", "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=2)

    g = p.get("gencoin_shadow_packet") or {}
    gl = p.get("gencoin_cognitive_ledger_packet") or {}
    entries = gl.get("entries") or []
    entry = entries[0] if entries else {}
    scores = entry.get("shadow_scores") or {}

    print("PORT=", port)
    print("source=", p.get("source"))
    print("graphiti_status=", p.get("graphiti_status"))
    print("gencoin_version=", g.get("version"))
    print("usable_shadow_value=", g.get("usable_shadow_value"))
    print("cognitive_ledger_status=", gl.get("status"))
    print("cognitive_ledger_source=", gl.get("source"))
    print("ledger_status=", gl.get("ledger_status"))
    print("entry_count=", gl.get("entry_count"))
    print("projected_only=", gl.get("projected_only"))
    print("persisted=", gl.get("persisted"))
    print("cognitive_ledger_score=", entry.get("cognitive_ledger_score"))
    print("score_status=", entry.get("score_status"))
    print("shadow_scores_keys=", sorted(scores.keys()))
    print("mint_allowed=", gl.get("mint_allowed"))
    print("wallet_enabled=", gl.get("wallet_enabled"))
    print("blockchain_enabled=", gl.get("blockchain_enabled"))
    print("is_real_token=", gl.get("is_real_token"))

    assert p.get("decision_authority") == "KX108_ONLY"
    assert p.get("readonly") is True
    assert p.get("emits_act") is False
    assert p.get("memory_write") is False
    assert p.get("graphiti_write") is False
    assert p.get("kernel_mutation") is False
    assert p.get("x108_mutation") is False

    assert g.get("version") == "GENCOIN_SHADOW_VALUE_PACKET_V1"
    assert g.get("usable_shadow_value") is True
    assert isinstance(g.get("shadow_scores"), dict)
    assert len([v for v in g.get("shadow_scores", {}).values() if isinstance(v, (int, float))]) >= 7

    assert gl.get("version") == "GENCOIN_COGNITIVE_LEDGER_PACKET_V1"
    assert gl.get("status") == "GENCOIN_COGNITIVE_LEDGER_READONLY_PASS"
    assert gl.get("source") == "BRODY_F20B_GENCOIN_COGNITIVE_LEDGER"
    assert gl.get("mode") == "READONLY_PROJECTED_LEDGER"
    assert gl.get("ledger_status") == "LIVE_EMPTY_REGISTRY"
    assert gl.get("entry_count") == 1
    assert gl.get("projected_only") is True
    assert gl.get("persisted") is False

    assert gl.get("decision_authority") == "KX108_ONLY"
    assert gl.get("readonly") is True
    assert gl.get("emits_act") is False
    assert gl.get("emits_verdict") is False
    assert gl.get("memory_write") is False
    assert gl.get("graphiti_write") is False
    assert gl.get("kernel_mutation") is False
    assert gl.get("x108_mutation") is False
    assert gl.get("final_scoring_enabled") is False
    assert gl.get("economic_scoring_enabled") is False
    assert gl.get("blockchain_enabled") is False
    assert gl.get("mint_allowed") is False
    assert gl.get("wallet_enabled") is False
    assert gl.get("is_real_token") is False

    assert entry.get("ledger_projection", {}).get("projected_entry_only") is True
    assert entry.get("ledger_projection", {}).get("persisted") is False
    assert entry.get("ledger_projection", {}).get("minted") is False
    assert entry.get("ledger_projection", {}).get("wallet_touched") is False
    assert entry.get("ledger_projection", {}).get("blockchain_touched") is False
    assert isinstance(entry.get("cognitive_ledger_score"), (int, float))
    assert entry.get("shadow_scores", {}).get("economic_projection") is None

print("F20B_RUNTIME_ASSERT_PASS")
