from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional

# Format versioning
TICKET_VERSION_V1 = "obsidia.kx108.ticket.v1"

# Default Key ID and In-Memory Registry for Key Rotation
_DEFAULT_KEY_ID = "kx108-k1"
_KEY_REGISTRY: Dict[str, bytes] = {}


def get_kernel_key(key_id: str = _DEFAULT_KEY_ID) -> bytes:
    """
    Récupère la clé secrète associée à un key_id.
    - En production (OBSIDIA_ENV=production|prod) : la clé est STRICTEMENT OBLIGATOIRE via variable
      d'environnement et doit mesurer au minimum 32 octets (256 bits). Aucune génération silencieuse.
    - En environnement de test/dev local : génération sécurisée 256 bits en RAM sans fuite Git.
    """
    if key_id not in _KEY_REGISTRY:
        env_var = f"OBSIDIA_KEY_{key_id.upper().replace('-', '_')}"
        env_key = os.environ.get(env_var) or os.environ.get("OBSIDIA_KX108_SECRET_KEY")
        is_production = os.environ.get("OBSIDIA_ENV", "").strip().lower() in ("production", "prod")

        if env_key:
            key_bytes = env_key.encode("utf-8") if isinstance(env_key, str) else env_key
            if is_production and len(key_bytes) < 32:
                raise ValueError(
                    f"OBSIDIA_KEY_SAFETY_ERROR: Secret key for '{key_id}' in production must have "
                    f"at least 32 bytes (256 bits) of entropy, got {len(key_bytes)}."
                )
            _KEY_REGISTRY[key_id] = key_bytes
        else:
            if is_production:
                raise RuntimeError(
                    f"OBSIDIA_PRODUCTION_FAIL_CLOSED: Secret key for '{key_id}' is mandatory in production. "
                    f"Set {env_var} or OBSIDIA_KX108_SECRET_KEY."
                )
            # Environnement de test/dev local : clé cryptographique 256 bits en mémoire
            _KEY_REGISTRY[key_id] = secrets.token_bytes(32)
    return _KEY_REGISTRY[key_id]


def reset_kernel_keys() -> None:
    """Réinitialise le registre de clés pour tests hermétiques."""
    global _KEY_REGISTRY
    _KEY_REGISTRY.clear()


def register_kernel_key(key_id: str, key_bytes: bytes) -> None:
    """Enregistre ou fait pivoter une clé d'autorité pour tests ou rotation officielle."""
    _KEY_REGISTRY[key_id] = key_bytes


def canonical_ticket_bytes(
    version: str,
    ticket_id: str,
    decision_id: str,
    action_id: str,
    os3_ticket_id: str,
    scope: str,
    x108_gate: str,
    autonomy_level: int,
    world_call_class: str,
    dry_run_only: bool,
    input_hash: str,
    action_hash: str,
    issued_at: str,
    expires_at: str,
    nonce: str,
    key_id: str,
) -> bytes:
    """Sérialisation canonique, versionnée et déterministe pour authentification HMAC."""
    canonical_dict = {
        "action_hash": str(action_hash),
        "action_id": str(action_id),
        "autonomy_level": int(autonomy_level),
        "decision_id": str(decision_id),
        "dry_run_only": bool(dry_run_only),
        "expires_at": str(expires_at),
        "input_hash": str(input_hash),
        "issued_at": str(issued_at),
        "key_id": str(key_id),
        "nonce": str(nonce),
        "os3_ticket_id": str(os3_ticket_id),
        "scope": str(scope),
        "ticket_id": str(ticket_id),
        "version": str(version),
        "world_call_class": str(world_call_class),
        "x108_gate": str(x108_gate),
    }
    return json.dumps(canonical_dict, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def compute_authenticator(raw_bytes: bytes, key_id: str = _DEFAULT_KEY_ID) -> str:
    """Calcule le HMAC-SHA256 de la sérialisation canonique."""
    key = get_kernel_key(key_id)
    return hmac.new(key, raw_bytes, hashlib.sha256).hexdigest()


@dataclass
class SovereignTicket:
    ticket_id: str
    action_id: str
    os3_ticket_id: str
    scope: str
    issued_at: str
    expires_at: str
    x108_gate: str
    autonomy_level: int
    dry_run_only: bool = True
    world_call_class: str = "NO_WORLD_CALL"
    hash: str = ""
    # Nouveaux champs d'autorité Phase 2G :
    decision_id: str = ""
    input_hash: str = ""
    action_hash: str = ""
    nonce: str = ""
    key_id: str = _DEFAULT_KEY_ID
    authenticator: str = ""
    version: str = TICKET_VERSION_V1

    @property
    def kernel_signature(self) -> str:
        """Alias documentaire pour conformité de contrat."""
        return self.authenticator

    def is_expired(self) -> bool:
        if not self.expires_at:
            return True
        now = datetime.now(timezone.utc).isoformat()
        return now > self.expires_at

    def is_valid_scope(self, required_scope: str) -> bool:
        return self.scope == required_scope or self.scope == "*"

    def assert_not_expired(self) -> None:
        if self.is_expired():
            raise AssertionError(f"SOVEREIGN_TICKET_EXPIRED:{self.ticket_id}")

    def assert_scope(self, required_scope: str) -> None:
        if not self.is_valid_scope(required_scope):
            raise AssertionError(f"SOVEREIGN_TICKET_INVALID_SCOPE:{self.scope}!={required_scope}")

    def assert_dry_run(self) -> None:
        if not self.dry_run_only:
            raise AssertionError("SOVEREIGN_TICKET_NOT_DRY_RUN")

    def to_dict(self) -> dict[str, Any]:
        return {
            "ticket_id": self.ticket_id,
            "action_id": self.action_id,
            "os3_ticket_id": self.os3_ticket_id,
            "scope": self.scope,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "x108_gate": self.x108_gate,
            "autonomy_level": self.autonomy_level,
            "dry_run_only": self.dry_run_only,
            "world_call_class": self.world_call_class,
            "hash": self.hash,
            "decision_id": self.decision_id,
            "input_hash": self.input_hash,
            "action_hash": self.action_hash,
            "nonce": self.nonce,
            "key_id": self.key_id,
            "authenticator": self.authenticator,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SovereignTicket:
        return cls(
            ticket_id=str(data.get("ticket_id", "")),
            action_id=str(data.get("action_id", "")),
            os3_ticket_id=str(data.get("os3_ticket_id", "")),
            scope=str(data.get("scope", "")),
            issued_at=str(data.get("issued_at", "")),
            expires_at=str(data.get("expires_at", "")),
            x108_gate=str(data.get("x108_gate", "UNKNOWN")),
            autonomy_level=int(data.get("autonomy_level", 0)),
            dry_run_only=bool(data.get("dry_run_only", True)),
            world_call_class=str(data.get("world_call_class", "NO_WORLD_CALL")),
            hash=str(data.get("hash", "")),
            decision_id=str(data.get("decision_id", "")),
            input_hash=str(data.get("input_hash", "")),
            action_hash=str(data.get("action_hash", "")),
            nonce=str(data.get("nonce", "")),
            key_id=str(data.get("key_id", _DEFAULT_KEY_ID)),
            authenticator=str(data.get("authenticator", "")),
            version=str(data.get("version", "")),
        )


def verify_authenticator(ticket: SovereignTicket) -> bool:
    """Vérification en temps constant du HMAC d'autorité."""
    if not ticket.authenticator or not ticket.nonce or not ticket.expires_at:
        return False
    try:
        key = get_kernel_key(ticket.key_id)
    except KeyError:
        return False

    raw_bytes = canonical_ticket_bytes(
        version=ticket.version or TICKET_VERSION_V1,
        ticket_id=ticket.ticket_id,
        decision_id=ticket.decision_id,
        action_id=ticket.action_id,
        os3_ticket_id=ticket.os3_ticket_id,
        scope=ticket.scope,
        x108_gate=ticket.x108_gate,
        autonomy_level=ticket.autonomy_level,
        world_call_class=ticket.world_call_class,
        dry_run_only=ticket.dry_run_only,
        input_hash=ticket.input_hash,
        action_hash=ticket.action_hash,
        issued_at=ticket.issued_at,
        expires_at=ticket.expires_at,
        nonce=ticket.nonce,
        key_id=ticket.key_id,
    )
    expected = hmac.new(key, raw_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(ticket.authenticator, expected)


def issue_sovereign_ticket(
    action_id: str,
    os3_ticket_id: str,
    x108_gate: str,
    scope: str,
    autonomy_level: int,
    world_call_class: str,
    input_hash: str = "",
    action_hash: str = "",
    decision_id: str = "",
    key_id: str = _DEFAULT_KEY_ID,
    nonce: str = "",
    ttl_seconds: int = 300,
) -> SovereignTicket:
    """
    Émet un ticket souverain authentifié cryptographiquement par le kernel KX108.
    """
    now = datetime.now(timezone.utc)
    issued_at = now.isoformat()
    expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat() if ttl_seconds > 0 else (now + timedelta(seconds=ttl_seconds)).isoformat()
    ticket_id = uuid.uuid4().hex
    
    if not decision_id:
        decision_id = f"dec-{uuid.uuid4().hex[:12]}"
    if not nonce:
        nonce = secrets.token_hex(16)
    if not action_hash:
        action_hash = hashlib.sha256(action_id.encode("utf-8")).hexdigest()

    raw_bytes = canonical_ticket_bytes(
        version=TICKET_VERSION_V1,
        ticket_id=ticket_id,
        decision_id=decision_id,
        action_id=action_id,
        os3_ticket_id=os3_ticket_id,
        scope=scope,
        x108_gate=x108_gate,
        autonomy_level=autonomy_level,
        world_call_class=world_call_class,
        dry_run_only=True,
        input_hash=input_hash,
        action_hash=action_hash,
        issued_at=issued_at,
        expires_at=expires_at,
        nonce=nonce,
        key_id=key_id,
    )
    authenticator = compute_authenticator(raw_bytes, key_id=key_id)

    # Condensat SHA-256 historique préservé pour compatibilité
    legacy_payload = {
        "ticket_id": ticket_id,
        "action_id": action_id,
        "os3_ticket_id": os3_ticket_id,
        "scope": scope,
        "issued_at": issued_at,
        "x108_gate": x108_gate,
    }
    legacy_hash = hashlib.sha256(
        json.dumps(legacy_payload, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()

    return SovereignTicket(
        ticket_id=ticket_id,
        action_id=action_id,
        os3_ticket_id=os3_ticket_id,
        scope=scope,
        issued_at=issued_at,
        expires_at=expires_at,
        x108_gate=x108_gate,
        autonomy_level=autonomy_level,
        dry_run_only=True,
        world_call_class=world_call_class,
        hash=legacy_hash,
        decision_id=decision_id,
        input_hash=input_hash,
        action_hash=action_hash,
        nonce=nonce,
        key_id=key_id,
        authenticator=authenticator,
        version=TICKET_VERSION_V1,
    )


def require_ticket_or_block(ticket: SovereignTicket | None) -> None:
    if ticket is None:
        raise AssertionError("NO_SOVEREIGN_TICKET_NO_WORLD_CALL")
    ticket.assert_not_expired()
    ticket.assert_dry_run()
    if not verify_authenticator(ticket):
        raise AssertionError(f"SOVEREIGN_TICKET_AUTHENTICATOR_INVALID:{ticket.ticket_id}")
