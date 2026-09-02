from scripts.providers.obsidure_runtime_contract_v1 import (
    ObsidureRuntimeRequest,
)

from scripts.providers.obsidure_runtime_engine_v1 import (
    ObsidureRuntimeEngine,
)


def request():
    return ObsidureRuntimeRequest(
        mission_id="mission-001",
        capability="proof",
        proof_target="theorem",
        payload={}
    )


def test_execution():

    engine = ObsidureRuntimeEngine()

    result = engine.execute(request())

    assert result.provider_id == "obsidure"
    assert result.verified is True


def test_proof_created():

    engine = ObsidureRuntimeEngine()

    result = engine.execute(request())

    assert result.proof["status"] == "verified"


def test_invariants():

    status = ObsidureRuntimeEngine().status()

    assert status["decision_authority"] is False
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False


def test_runtime_name():

    assert ObsidureRuntimeEngine().runtime_name == "obsidure-runtime-v1"


def test_no_decision():

    result = ObsidureRuntimeEngine().execute(request())

    assert "decision" not in result.to_dict()
