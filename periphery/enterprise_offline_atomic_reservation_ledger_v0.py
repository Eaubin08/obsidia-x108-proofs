"""C2.23 durable local reservation with revocation and idempotency; NO dispatch.

Atomicity is restricted to ONE local SQLite database. This never grants
execution authority, performs provider calls or authenticates organization.
"""
from __future__ import annotations
import sqlite3

class OfflineReservationLedgerV0:
    def __init__(self, path):
        self.path=str(path)
        if self.path==":memory:":
            raise ValueError("C223_PERSISTENCE_REQUIRED")
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS scopes(
                organization TEXT NOT NULL, delegate TEXT NOT NULL,
                connector TEXT NOT NULL, capability TEXT NOT NULL,
                generation INTEGER NOT NULL DEFAULT 0,
                revoked INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY(organization,delegate,connector,capability))""")
            db.execute("""CREATE TABLE IF NOT EXISTS reservations(
                idempotency_key TEXT PRIMARY KEY, organization TEXT NOT NULL,
                delegate TEXT NOT NULL, connector TEXT NOT NULL,
                capability TEXT NOT NULL, generation INTEGER NOT NULL,
                nonce TEXT NOT NULL, status TEXT NOT NULL,
                UNIQUE(organization,delegate,connector,capability,nonce))""")
    def _connect(self):
        db=sqlite3.connect(self.path,timeout=10,isolation_level=None)
        db.execute("PRAGMA busy_timeout=10000")
        return db
    @staticmethod
    def _scope(scope):
        if not isinstance(scope,(tuple,list)) or len(scope)!=4 or any(not isinstance(v,str) or not v for v in scope):
            raise ValueError("C223_SCOPE_INVALID")
        return tuple(scope)
    def enroll_fixture(self, scope):
        scope=self._scope(scope)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("INSERT OR IGNORE INTO scopes(organization,delegate,connector,capability) VALUES(?,?,?,?)",scope)
            db.commit()
    def revoke(self, scope):
        scope=self._scope(scope)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            cur=db.execute("UPDATE scopes SET revoked=1,generation=generation+1 WHERE organization=? AND delegate=? AND connector=? AND capability=?",scope)
            db.execute("UPDATE reservations SET status='INVALIDATED' WHERE organization=? AND delegate=? AND connector=? AND capability=? AND status='RESERVED_NO_EXECUTION'",scope)
            db.commit()
            return cur.rowcount==1
    def reserve_fixture(self, *, scope, generation, nonce, idempotency_key):
        scope=self._scope(scope)
        if not isinstance(generation,int) or isinstance(generation,bool) or generation<0 or any(
            not isinstance(x,str) or len(x)<16 for x in (nonce,idempotency_key)):
            return "BLOCK:C223_FIELDS_INVALID"
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute("SELECT generation,revoked FROM scopes WHERE organization=? AND delegate=? AND connector=? AND capability=?",scope).fetchone()
            if row is None:
                db.rollback();return "BLOCK:C223_SCOPE_UNKNOWN"
            if row[1]:
                db.rollback();return "BLOCK:C223_REVOKED"
            if row[0]!=generation:
                db.rollback();return "BLOCK:C223_STALE_GENERATION"
            try:
                db.execute("INSERT INTO reservations VALUES(?,?,?,?,?,?,?,?)",
                    (idempotency_key,*scope,generation,nonce,"RESERVED_NO_EXECUTION"))
            except sqlite3.IntegrityError:
                db.rollback();return "BLOCK:C223_REPLAY_OR_IDEMPOTENCY_DUPLICATE"
            db.commit()
        return "RESERVED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY"
    def inspect(self,idempotency_key):
        with self._connect() as db:
            row=db.execute("SELECT status FROM reservations WHERE idempotency_key=?",(idempotency_key,)).fetchone()
        return row[0] if row else "UNKNOWN"
