"""C2.43 offline API allowlisting and restart; no OS isolation."""
from periphery.enterprise_offline_storage_service_boundary_v0 import OfflineStorageServiceV0

SCOPE=("org-a","delegate-a","GMAIL","gmail:send")
KEY="c243-idempotency-key-00001"
NONCE="c243-proof-nonce-000001"

def test_uninitialized_operations_fail_closed(tmp_path):
    service=OfflineStorageServiceV0(tmp_path/"state.db")
    assert service.request_fixture("enroll",{"scope":SCOPE})=="BLOCK:C236_GUARDS_NOT_READY"
    assert service.request_fixture("raw_sql",{"sql":"DROP TABLE reservations"})=="BLOCK:C243_OPERATION_DENIED"
    assert service.request_fixture("reserve",{"scope":SCOPE})=="BLOCK:C243_FIELDS_DENIED"

def test_allowlisted_offline_flow_survives_restart(tmp_path):
    path=tmp_path/"state.db"
    service=OfflineStorageServiceV0(path)
    service.initialize_fixture()
    assert service.request_fixture("enroll",{"scope":SCOPE})=="C236_SCOPE_ENROLLED_FIXTURE_ONLY"
    assert service.request_fixture("reserve",dict(scope=SCOPE,generation=0,nonce=NONCE,idempotency_key=KEY))=="RESERVED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"
    restarted=OfflineStorageServiceV0(path)
    assert restarted.request_fixture("close",dict(idempotency_key=KEY,disposition="CLOSED_NO_EXECUTION"))=="CLOSED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"
    assert restarted.request_fixture("inspect",{"idempotency_key":KEY})=="CLOSED_NO_EXECUTION"

def test_unknown_actions_and_extra_fields_denied(tmp_path):
    service=OfflineStorageServiceV0(tmp_path/"state.db")
    service.initialize_fixture()
    assert service.request_fixture("execute",{})=="BLOCK:C243_OPERATION_DENIED"
    assert service.request_fixture("enroll",{"scope":SCOPE,"sql":"DROP TRIGGER x"})=="BLOCK:C243_FIELDS_DENIED"
    assert service.request_fixture("inspect",None)=="BLOCK:C243_INVALID_PAYLOAD"
