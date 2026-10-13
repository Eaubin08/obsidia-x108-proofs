from periphery.enterprise_ipc_reply_correlation_v0 import OfflineIPCReplyCorrelatorV0

A="c247-request-id-0000001"
B="c247-request-id-0000002"
GOOD="RESERVED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"

def test_out_of_order_replies_match_by_id():
    c=OfflineIPCReplyCorrelatorV0()
    assert c.register(A)=="C247_PENDING_NO_EXECUTION"
    assert c.register(B)=="C247_PENDING_NO_EXECUTION"
    assert c.accept(B,"BLOCK:C228_REPLAY_OR_DUPLICATE")=="C247_MATCHED_FIXTURE_ONLY_NO_EXECUTION"
    assert c.accept(A,GOOD)=="C247_MATCHED_FIXTURE_ONLY_NO_EXECUTION"
    assert not c.pending()

def test_duplicate_and_unknown_replies_block():
    c=OfflineIPCReplyCorrelatorV0()
    c.register(A)
    assert c.accept("unknown-request-id-001",GOOD)=="BLOCK:C247_UNMATCHED_RESPONSE"
    assert c.accept(A,GOOD)=="C247_MATCHED_FIXTURE_ONLY_NO_EXECUTION"
    assert c.accept(A,GOOD)=="BLOCK:C247_DUPLICATE_RESPONSE"
    assert c.register(A)=="BLOCK:C247_REQUEST_REPLAY_OR_INVALID"

def test_unrecognized_response_retains_pending_for_manual_recovery():
    c=OfflineIPCReplyCorrelatorV0()
    c.register(A)
    assert c.accept(A,"EXECUTED")=="BLOCK:C247_RESPONSE_VALUE_INVALID"
    assert A in c.pending()
