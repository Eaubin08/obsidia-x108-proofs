from apps.obsidia_api.brody_contracts_packet import build_graphiti_contract


def test_f41_graphiti_contract_readonly():

    contract = build_graphiti_contract()

    assert contract["graphiti_read"] is True
    assert contract["graphiti_write"] is False
    assert contract["context_only"] is True
    assert contract["graphiti_decision_authority"] == "NONE"


def test_f41_graphiti_contract_has_no_write_authority():

    contract = build_graphiti_contract()

    assert contract.get("neo4j_write", False) is False
    assert contract.get("memory_write", False) is False
