import json
import urllib.request

message = (
    "F19 runtime assert: expose thermo_unified_packet, coherence, energy_thermo, "
    "time shadow, sans écrire mémoire, sans ACT, sans mutation X108."
)

for port in (8000, 8012):
    data = json.dumps({
        "message": message,
        "language": "fr",
        "session_id": f"f19b_runtime_assert_{port}",
    }).encode("utf-8")

    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/api/brody/chat",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(req, timeout=60) as r:
        p = json.loads(r.read().decode("utf-8"))

    with open(f"docs/runtime/F19B_{port}_THERMO_COHERENCE_TIME_UNIFIED_PAYLOAD.json", "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=2)

    tu = p.get("thermo_unified_packet") or {}
    scores = tu.get("scores") or {}
    energy = tu.get("energy_thermo_packet") or {}
    coh = tu.get("coherence_shadow_packet") or {}
    time = tu.get("time_shadow_packet") or {}

    print("PORT=", port)
    print("source=", p.get("source"))
    print("graphiti_status=", p.get("graphiti_status"))
    print("thermo_unified_status=", tu.get("status"))
    print("thermo_unified_source=", tu.get("source"))
    print("stability_state=", tu.get("stability_state"))
    print("composite_temperature=", tu.get("composite_temperature"))
    print("scores_keys=", sorted(scores.keys()))
    print("energy_source=", energy.get("source"))
    print("coherence_status=", coh.get("status"))
    print("time_status=", time.get("status"))
    print("usable_for_gencoin=", tu.get("usable_for_gencoin"))
    print("usable_for_value_layer=", tu.get("usable_for_value_layer"))

    assert p.get("decision_authority") == "KX108_ONLY"
    assert p.get("readonly") is True
    assert p.get("emits_act") is False
    assert p.get("memory_write") is False
    assert p.get("graphiti_write") is False
    assert p.get("kernel_mutation") is False
    assert p.get("x108_mutation") is False

    assert tu.get("version") == "THERMO_COHERENCE_TIME_UNIFIED_PACKET_V1"
    assert tu.get("status") == "THERMO_COHERENCE_TIME_UNIFIED_READONLY_PASS"
    assert tu.get("source") == "BRODY_F19B_UNIFIED_THERMO_COHERENCE_TIME"
    assert tu.get("decision_authority") == "KX108_ONLY"
    assert tu.get("readonly") is True
    assert tu.get("emits_act") is False
    assert tu.get("memory_write") is False
    assert tu.get("graphiti_write") is False
    assert tu.get("kernel_mutation") is False
    assert tu.get("x108_mutation") is False

    assert "thermo_coherence_temperature" in scores
    assert "energy_efficiency" in scores
    assert "replay_coherence_score" in scores
    assert "time_pressure" in scores
    assert isinstance(tu.get("composite_temperature"), (int, float))
    assert energy.get("source") == "periphery.energy_thermo.run_energy_thermo"
    assert coh.get("status") == "COHERENCE_SHADOW_COMPUTED_READONLY"
    assert time.get("source") == "BRODY_F19B_TIME_SHADOW"

print("F19B_RUNTIME_ASSERT_PASS")
