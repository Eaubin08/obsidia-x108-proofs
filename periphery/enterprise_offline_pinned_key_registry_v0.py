"""C2.16 offline pinned key registry. Test-only enrollment, deny-only result.

SHA256 fingerprints pin exact DER public-key bytes. Enrollment is a fixture
operation, not proof of organizational control or an authenticated IdP.
"""
from __future__ import annotations
import hashlib
import sqlite3
from pathlib import Path
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, load_pem_public_key

class OfflinePinnedKeyRegistryV0:
    def __init__(self, path):
        self.path = str(path)
        if self.path == ":memory:":
            raise ValueError("C216_PERSISTENCE_REQUIRED")
        with self._db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS keys (
                organization TEXT NOT NULL, issuer TEXT NOT NULL, audience TEXT NOT NULL,
                fingerprint TEXT NOT NULL, revoked INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY(organization,issuer,audience,fingerprint))""")
    def _db(self):
        db=sqlite3.connect(self.path,timeout=10,isolation_level=None)
        db.execute("PRAGMA busy_timeout=10000")
        return db
    @staticmethod
    def fingerprint(pem):
        key=load_pem_public_key(pem)
        der=key.public_bytes(Encoding.DER,PublicFormat.SubjectPublicKeyInfo)
        return hashlib.sha256(der).hexdigest()
    def enroll_fixture(self, *, organization, issuer, audience, public_key_pem):
        if not all(isinstance(x,str) and x for x in (organization,issuer,audience)):
            raise ValueError("C216_SCOPE_INCOMPLETE")
        fp=self.fingerprint(public_key_pem)
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            old=db.execute("SELECT revoked FROM keys WHERE organization=? AND issuer=? AND audience=? AND fingerprint=?",
                           (organization,issuer,audience,fp)).fetchone()
            if old is not None:
                db.rollback()
                if old[0]: raise ValueError("C216_REVOKED_KEY_CANNOT_REENROLL")
                return fp
            db.execute("INSERT INTO keys (organization,issuer,audience,fingerprint) VALUES (?,?,?,?)",
                       (organization,issuer,audience,fp))
            db.commit()
        return fp
    def revoke(self, *, organization, issuer, audience, fingerprint):
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            cur=db.execute("UPDATE keys SET revoked=1 WHERE organization=? AND issuer=? AND audience=? AND fingerprint=?",
                           (organization,issuer,audience,fingerprint))
            db.commit()
            return cur.rowcount==1
    def inspect_fixture(self, *, organization, issuer, audience, public_key_pem):
        try: fp=self.fingerprint(public_key_pem)
        except (ValueError,TypeError): return "BLOCK:C216_PUBLIC_KEY_INVALID"
        with self._db() as db:
            row=db.execute("SELECT revoked FROM keys WHERE organization=? AND issuer=? AND audience=? AND fingerprint=?",
                           (organization,issuer,audience,fp)).fetchone()
        if row is None: return "BLOCK:C216_KEY_NOT_ENROLLED"
        if row[0]: return "BLOCK:C216_KEY_REVOKED"
        return "PINNED_FIXTURE_ONLY_NO_ORGANIZATION_AUTHORITY"
