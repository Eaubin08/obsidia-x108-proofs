"""C2.47 offline IPC reply correlation; reject stale, duplicate and out-of-order replies.

No automatic retry, connector call or execution authority.
"""
class OfflineIPCReplyCorrelatorV0:
    def __init__(self):
        self._pending=set()
        self._completed=set()
    def register(self,request_id):
        if not isinstance(request_id,str) or len(request_id)<16 or request_id in self._pending or request_id in self._completed:
            return "BLOCK:C247_REQUEST_REPLAY_OR_INVALID"
        self._pending.add(request_id)
        return "C247_PENDING_NO_EXECUTION"
    def accept(self,request_id,result):
        if request_id in self._completed:
            return "BLOCK:C247_DUPLICATE_RESPONSE"
        if request_id not in self._pending:
            return "BLOCK:C247_UNMATCHED_RESPONSE"
        if not isinstance(result,str) or not (result.startswith("BLOCK:") or result in (
            "RESERVED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY",
            "CLOSED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY",
        )):
            return "BLOCK:C247_RESPONSE_VALUE_INVALID"
        self._pending.remove(request_id)
        self._completed.add(request_id)
        return "C247_MATCHED_FIXTURE_ONLY_NO_EXECUTION"
    def pending(self):
        return frozenset(self._pending)
