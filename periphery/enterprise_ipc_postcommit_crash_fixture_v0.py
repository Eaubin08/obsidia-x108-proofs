"""C2.46 offline deterministic post-commit worker crash fixture.

Only for local integration tests: terminate worker *after* durable reservation
commit and *before* emitting the IPC response. No provider execution.
"""
import multiprocessing as mp
import os
import queue
from periphery.enterprise_offline_storage_service_boundary_v0 import OfflineStorageServiceV0

def _crash_worker(path,requests,responses):
    service=OfflineStorageServiceV0(path)
    while True:
        task=requests.get()
        if task is None: return
        request_id,op,payload=task
        if op=="reserve_then_crash":
            outcome=service.request_fixture("reserve",payload)
            if outcome=="RESERVED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY":
                os._exit(87)  # Process dies after SQLite commit, before response.
            responses.put((request_id,outcome))
        elif op=="initialize_fixture":
            responses.put((request_id,service.initialize_fixture()))
        else:
            responses.put((request_id,service.request_fixture(op,payload)))

class CrashInjectedStorageWorkerV0:
    def __init__(self,path):
        self.path=str(path)
        self.requests=mp.Queue()
        self.responses=mp.Queue()
        self.process=None
        self.request_id=0

    def start(self):
        self.process=mp.Process(target=_crash_worker,
            args=(self.path,self.requests,self.responses))
        self.process.start()

    def request(self,operation,payload=None,timeout=2):
        if self.process is None or not self.process.is_alive():
            return "BLOCK:C246_WORKER_UNAVAILABLE"
        if operation not in ("initialize_fixture","enroll","reserve_then_crash","inspect"):
            return "BLOCK:C246_OPERATION_DENIED"
        self.request_id+=1
        self.requests.put((self.request_id,operation,payload))
        try:
            response_id,result=self.responses.get(timeout=timeout)
        except queue.Empty:
            return "BLOCK:C246_AMBIGUOUS_IPC_RESPONSE"
        if response_id!=self.request_id:
            return "BLOCK:C246_RESPONSE_MISMATCH"
        return result

    def stop(self):
        if self.process is not None and self.process.is_alive():
            self.requests.put(None)
            self.process.join(3)
            if self.process.is_alive():
                self.process.terminate()
                self.process.join(3)
        self.process=None
