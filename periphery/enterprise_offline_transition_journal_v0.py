"""C2.27 locally hash-linked fixture transition journal: no authority or egress.

Hash links detect selective changes when an independently known root remains.
A writer who rewrites the entire SQLite journal can rebuild all hashes.
"""
from __future__ import annotations
import hashlib
import json
import sqlite3

GENESIS="0"*64

def digest(payload):
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

class OfflineTransitionJournalV0:
    def __init__(self,path):
        self.path=str(path)
        if self.path==":memory:": raise ValueError("C227_PERSISTENCE_REQUIRED")
        with self._db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS transition_events(
                sequence INTEGER PRIMARY KEY, idempotency_key TEXT NOT NULL,
                event_kind TEXT NOT NULL, previous_hash TEXT NOT NULL,
                event_hash TEXT NOT NULL)""")
    def _db(self):
        db=sqlite3.connect(self.path,timeout=10,isolation_level=None)
        db.execute("PRAGMA busy_timeout=10000")
        return db
    def append_fixture(self,*,idempotency_key,event_kind):
        if not isinstance(idempotency_key,str) or not idempotency_key or event_kind not in (
            "RESERVED_NO_EXECUTION","CLOSED_NO_EXECUTION",
            "ABANDONED_NO_EXECUTION","INVALIDATED"):
            return "BLOCK:C227_EVENT_INVALID"
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute("SELECT sequence,event_hash FROM transition_events ORDER BY sequence DESC LIMIT 1").fetchone()
            sequence=row[0]+1 if row else 1
            previous=row[1] if row else GENESIS
            event_hash=digest({"sequence":sequence,"idempotency_key":idempotency_key,
                               "event_kind":event_kind,"previous_hash":previous})
            db.execute("INSERT INTO transition_events VALUES(?,?,?,?,?)",
                       (sequence,idempotency_key,event_kind,previous,event_hash))
            db.commit()
        return "APPENDED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY"
    def verify_local(self):
        with self._db() as db:
            rows=db.execute("SELECT sequence,idempotency_key,event_kind,previous_hash,event_hash FROM transition_events ORDER BY sequence").fetchall()
        previous=GENESIS
        for index,(seq,key,kind,prev,current) in enumerate(rows,1):
            if seq!=index or prev!=previous or current!=digest(
                {"sequence":seq,"idempotency_key":key,"event_kind":kind,"previous_hash":prev}):
                return {"status":"BLOCK","reason":"C227_HASH_CHAIN_INVALID",
                        "egress_allowed":False}
            previous=current
        return {"status":"BLOCK","reason":"C227_LOCAL_CHAIN_CONSISTENT_NOT_ATTESTED",
                "event_count":len(rows),"head_hash":previous,"egress_allowed":False}
