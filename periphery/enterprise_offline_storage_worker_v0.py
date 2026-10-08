"""C2.44 separate local worker process with request/response IPC, fixture only.

Not an OS security boundary: parent still knows the database path and runs
under the same OS identity. No network, SQL commands, or external dispatch.
"""
import multiprocessing as mp
import queue
import threading
import time
from periphery.enterprise_offline_storage_service_boundary_v0 import OfflineStorageServiceV0

def _worker(path, requests, responses):
    service=OfflineStorageServiceV0(path)
    while True:
        item=requests.get()
        if item is None: return
        sequence, operation, payload=item
        try:
            if operation=="initialize_fixture":
                answer=service.initialize_fixture()
            else:
                answer=service.request_fixture(operation,payload)
        except Exception:
            answer="BLOCK:C244_WORKER_ERROR"
        responses.put((sequence,answer))

class OfflineStorageWorkerV0:
    def __init__(self,path):
        self._path=str(path)
        self._requests=mp.Queue()
        self._responses=mp.Queue()
        self._process=None
        self._sequence=0
        self._request_lock=threading.Lock()

    def start(self):
        if self._process is not None and self._process.is_alive():
            return "C244_ALREADY_STARTED"
        self._process=mp.Process(target=_worker,args=(self._path,self._requests,self._responses),daemon=True)
        self._process.start()
        return "C244_WORKER_STARTED_FIXTURE_ONLY"

    def request_fixture(self,operation,payload=None,timeout=3):
        # Serialize use of this client queue across threads. Unmatched late
        # replies are discarded, never attached to another request.
        with self._request_lock:
            if self._process is None or not self._process.is_alive():
                return "BLOCK:C244_WORKER_UNAVAILABLE"
            if operation not in ("initialize_fixture","enroll","reserve","close","revoke","inspect"):
                return "BLOCK:C244_OPERATION_DENIED"
            self._sequence+=1
            sequence=self._sequence
            try:
                self._requests.put((sequence,operation,payload))
                deadline=time.monotonic()+max(0,timeout)
                while True:
                    remaining=deadline-time.monotonic()
                    if remaining<=0:
                        return "BLOCK:C244_WORKER_TIMEOUT"
                    try:
                        returned,answer=self._responses.get(timeout=remaining)
                    except queue.Empty:
                        return "BLOCK:C244_WORKER_TIMEOUT"
                    if returned!=sequence:
                        # Old/foreign responses are discarded; no replay.
                        continue
                    return answer
            except (TypeError,ValueError,EOFError,OSError):
                return "BLOCK:C248_IPC_UNAVAILABLE"

    def stop(self):
        if self._process is not None and self._process.is_alive():
            self._requests.put(None)
            self._process.join(3)
            if self._process.is_alive():
                self._process.terminate()
                self._process.join(3)
        self._process=None
