"""C2.3 SQLite durable revoke/replay simulation; NEVER an execution permit.

Transactions serialize through SQLite BEGIN IMMEDIATE for processes sharing
one local DB. No shared remote store, connector dispatch or KX108 authority.
"""
from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

SCHEMA = "OBSIDIA_C23_DURABLE_REVOCATION_SIMULATION_V0"


class DurableDelegationLedgerV0:
    def __init__(self, path: str | Path):
        self.path = str(path)
        if self.path == ":memory:":
            raise ValueError("C23_DISALLOW_EPHEMERAL_DATABASE")
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS delegation (
                organization TEXT NOT NULL, delegate TEXT NOT NULL,
                connector TEXT NOT NULL, capability TEXT NOT NULL,
                generation INTEGER NOT NULL DEFAULT 0,
                revoked INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY(organization, delegate, connector, capability))""")
            db.execute("""CREATE TABLE IF NOT EXISTS used_nonce (
                organization TEXT NOT NULL, delegate TEXT NOT NULL,
                connector TEXT NOT NULL, capability TEXT NOT NULL,
                nonce TEXT NOT NULL,
                PRIMARY KEY(organization, delegate, connector, capability, nonce))""")

    def _connect(self):
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        db.execute("PRAGMA busy_timeout=10000")
        return db

    @staticmethod
    def _scope(scope):
        if len(scope) != 4 or any(not isinstance(v, str) or not v for v in scope):
            raise ValueError("C23_SCOPE_INVALID")
        return scope

    def register_fixture(self, scope):
        """Fixture bootstrap only; never authenticates an issuer or delegate."""
        scope = self._scope(scope)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("INSERT OR IGNORE INTO delegation(organization, delegate, connector, capability) VALUES(?,?,?,?)", scope)
            db.commit()

    def revoke(self, scope):
        scope = self._scope(scope)
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            cursor = db.execute(
                "UPDATE delegation SET revoked=1, generation=generation+1 WHERE organization=? AND delegate=? AND connector=? AND capability=?", scope)
            db.commit()
            return cursor.rowcount == 1

    def check_and_consume_fixture(self, scope, *, generation, nonce, evidence_verified=False):
        """Atomic ledger-only replay/revocation check. Always denies execution.

        Caller-supplied evidence_verified is not proof: return CHECKED_ONLY
        solely for fixture inspection. Real dispatch must never use it as ALLOW.
        """
        scope = self._scope(scope)
        if not isinstance(nonce, str) or len(nonce) < 16 or not isinstance(generation, int) or generation < 0:
            return "BLOCK:C23_PROOF_FIELDS_INVALID"
        if evidence_verified is not True:
            return "BLOCK:C23_EVIDENCE_NOT_INDEPENDENTLY_VERIFIED"
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT generation,revoked FROM delegation WHERE organization=? AND delegate=? AND connector=? AND capability=?", scope
            ).fetchone()
            if row is None:
                db.rollback()
                return "BLOCK:C23_DELEGATION_UNKNOWN"
            if row[1]:
                db.rollback()
                return "BLOCK:C23_REVOKED"
            if row[0] != generation:
                db.rollback()
                return "BLOCK:C23_GENERATION_STALE"
            try:
                db.execute("INSERT INTO used_nonce VALUES(?,?,?,?,?)", (*scope, nonce))
            except sqlite3.IntegrityError:
                db.rollback()
                return "BLOCK:C23_NONCE_REPLAY"
            db.commit()
            return "CHECKED_FIXTURE_ONLY_NO_EXECUTION_AUTHORITY"
