"""C2.10 test-only issuer registry: immutable org/issuer enrollment and revocation.

NOT an identity provider. Enrollment is fixture-controlled, not legal proof.
Never authorizes KX108, tickets, connector egress, or execution.
"""
from __future__ import annotations
import sqlite3
from pathlib import Path

class FixtureIssuerTrustRegistryV0:
    def __init__(self, path):
        self.path = str(path)
        if self.path == ":memory:":
            raise ValueError("C210_EPHEMERAL_REGISTRY_FORBIDDEN")
        with self._connection() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS fixture_issuers (
                organization TEXT NOT NULL, issuer TEXT NOT NULL, key_digest TEXT NOT NULL,
                revoked INTEGER NOT NULL DEFAULT 0, generation INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY(organization, issuer))""")

    def _connection(self):
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        db.execute("PRAGMA busy_timeout=10000")
        return db

    def register_fixture(self, *, organization, issuer, key_digest):
        if not all(isinstance(x,str) and x for x in (organization,issuer,key_digest)) or len(key_digest)!=64:
            raise ValueError("C210_FIXTURE_IDENTITY_INVALID")
        with self._connection() as db:
            db.execute("BEGIN IMMEDIATE")
            existing=db.execute(
                "SELECT key_digest,revoked FROM fixture_issuers WHERE organization=? AND issuer=?",
                (organization,issuer)).fetchone()
            if existing is not None:
                db.rollback()
                if existing[0] != key_digest or existing[1]:
                    raise ValueError("C210_ISSUER_IMMUTABLE_OR_REVOKED")
                return
            db.execute("INSERT INTO fixture_issuers(organization,issuer,key_digest) VALUES (?,?,?)",
                       (organization,issuer,key_digest))
            db.commit()

    def revoke(self, *, organization, issuer):
        with self._connection() as db:
            db.execute("BEGIN IMMEDIATE")
            cur=db.execute(
                "UPDATE fixture_issuers SET revoked=1,generation=generation+1 WHERE organization=? AND issuer=?",
                (organization,issuer))
            db.commit()
            return cur.rowcount==1

    def check_fixture(self, *, organization, issuer, key_digest):
        with self._connection() as db:
            row=db.execute(
                "SELECT key_digest,revoked FROM fixture_issuers WHERE organization=? AND issuer=?",
                (organization,issuer)).fetchone()
        if row is None: return "BLOCK:C210_ISSUER_UNKNOWN"
        if row[1]: return "BLOCK:C210_ISSUER_REVOKED"
        if row[0] != key_digest: return "BLOCK:C210_ISSUER_KEY_MISMATCH"
        return "FIXTURE_ISSUER_MATCH_NO_ORGANIZATION_AUTHORITY"
