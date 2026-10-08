"""C2.28 atomic fixture reservation/journal transitions, no execution."""
from __future__ import annotations
from periphery.enterprise_offline_reservation_lifecycle_v0 import OfflineReservationLifecycleV0
from periphery.enterprise_offline_transition_journal_v0 import GENESIS, digest

class AtomicOfflineReservationJournalV0(OfflineReservationLifecycleV0):
    def __init__(self,path):
        super().__init__(path)
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS transition_events(
                sequence INTEGER PRIMARY KEY, idempotency_key TEXT NOT NULL,
                event_kind TEXT NOT NULL, previous_hash TEXT NOT NULL,
                event_hash TEXT NOT NULL)""")

    @staticmethod
    def _append(db,key,kind):
        last=db.execute("SELECT sequence,event_hash FROM transition_events ORDER BY sequence DESC LIMIT 1").fetchone()
        seq=last[0]+1 if last else 1
        prev=last[1] if last else GENESIS
        current=digest({"sequence":seq,"idempotency_key":key,"event_kind":kind,"previous_hash":prev})
        db.execute("INSERT INTO transition_events VALUES(?,?,?,?,?)",(seq,key,kind,prev,current))

    def reserve_logged_fixture(self,*,scope,generation,nonce,idempotency_key):
        scope=self._scope(scope)
        if not isinstance(generation,int) or isinstance(generation,bool) or generation<0 or any(
            not isinstance(x,str) or len(x)<16 for x in (nonce,idempotency_key)):
            return "BLOCK:C228_FIELDS_INVALID"
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute("SELECT generation,revoked FROM scopes WHERE organization=? AND delegate=? AND connector=? AND capability=?",scope).fetchone()
            if not row or row[1] or row[0]!=generation:
                db.rollback();return "BLOCK:C228_SCOPE_REVOKED_OR_STALE"
            try:
                db.execute("INSERT INTO reservations VALUES(?,?,?,?,?,?,?,?)",
                    (idempotency_key,*scope,generation,nonce,"RESERVED_NO_EXECUTION"))
                self._append(db,idempotency_key,"RESERVED_NO_EXECUTION")
            except Exception:
                db.rollback();raise
            db.commit()
        return "RESERVED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"

    def close_logged_fixture(self,*,idempotency_key,disposition):
        if disposition not in ("CLOSED_NO_EXECUTION","ABANDONED_NO_EXECUTION"):
            return "BLOCK:C228_DISPOSITION_INVALID"
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute("SELECT status FROM reservations WHERE idempotency_key=?",(idempotency_key,)).fetchone()
            if row is None or row[0]!="RESERVED_NO_EXECUTION":
                db.rollback();return "BLOCK:C228_RESERVATION_NOT_ACTIVE"
            import hashlib,json
            receipt_hash=hashlib.sha256(json.dumps({"idempotency_key":idempotency_key,
                "final_status":disposition},sort_keys=True,separators=(",",":")).encode()).hexdigest()
            db.execute("UPDATE reservations SET status=? WHERE idempotency_key=?",(disposition,idempotency_key))
            db.execute("INSERT INTO lifecycle_receipts VALUES(?,?,?)",(idempotency_key,disposition,receipt_hash))
            self._append(db,idempotency_key,disposition)
            db.commit()
        return "CLOSED_LOGGED_FIXTURE_NO_EXECUTION_AUTHORITY"

    def revoke(self,scope):
        scope=self._scope(scope)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            cur=db.execute("UPDATE scopes SET revoked=1,generation=generation+1 WHERE organization=? AND delegate=? AND connector=? AND capability=?",scope)
            if not cur.rowcount:
                db.rollback();return False
            active=db.execute("SELECT idempotency_key FROM reservations WHERE organization=? AND delegate=? AND connector=? AND capability=? AND status='RESERVED_NO_EXECUTION' ORDER BY idempotency_key",scope).fetchall()
            for (key,) in active:
                db.execute("UPDATE reservations SET status='INVALIDATED' WHERE idempotency_key=?",(key,))
                self._append(db,key,"INVALIDATED")
            db.commit()
            return True

    def verify_logged_fixture(self):
        with self._connect() as db:
            rows=db.execute("SELECT sequence,idempotency_key,event_kind,previous_hash,event_hash FROM transition_events ORDER BY sequence").fetchall()
            states=dict(db.execute("SELECT idempotency_key,status FROM reservations").fetchall())
        previous=GENESIS
        latest={}
        for index,(seq,key,kind,prev,current) in enumerate(rows,1):
            if seq!=index or prev!=previous or current!=digest(
                {"sequence":seq,"idempotency_key":key,"event_kind":kind,"previous_hash":prev}):
                return "BLOCK:C228_CHAIN_INVALID"
            latest[key]=kind
            previous=current
        if not states or latest!=states:
            return "BLOCK:C228_STATE_JOURNAL_MISMATCH"
        return "BLOCK:C228_LOCAL_JOURNAL_CONSISTENT_NOT_ATTESTED"
