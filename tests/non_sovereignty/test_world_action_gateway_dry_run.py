from periphery.world_action_gateway import WorldActionReadiness

def test_readiness_model_not_action():
    r = WorldActionReadiness("a", True, True, False, "READY")
    assert r.world_action_allowed is False
