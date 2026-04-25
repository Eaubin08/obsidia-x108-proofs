# api_server/security.py
from __future__ import annotations
import os, time, json, base64, hmac, hashlib
from typing import Any, Dict, Optional, Tuple
from fastapi import Header, HTTPException

# Auth modes: "none" | "apikey" | "jwt" | "both"
AUTH_MODE = os.getenv("OBSIDIA_AUTH_MODE", "apikey").strip().lower()

# API key (simple)
API_KEY = os.getenv("OBSIDIA_API_KEY", "").strip()

# JWT (self-contained)
JWT_SECRET = os.getenv("OBSIDIA_JWT_SECRET", "").encode("utf-8")
JWT_ISSUER = os.getenv("OBSIDIA_JWT_ISSUER", "obsidia").strip()
JWT_AUDIENCE = os.getenv("OBSIDIA_JWT_AUDIENCE", "obsidia-api").strip()
JWT_TTL_SECONDS = int(os.getenv("OBSIDIA_JWT_TTL_SECONDS", "3600"))

# Simple user/password for token minting (OAuth2 password-style)
OBSIDIA_USER = os.getenv("OBSIDIA_USER", "").strip()
OBSIDIA_PASSWORD = os.getenv("OBSIDIA_PASSWORD", "").strip()

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

def _b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)

def _sign_hs256(msg: bytes, secret: bytes) -> bytes:
    return hmac.new(secret, msg, hashlib.sha256).digest()

def mint_jwt(sub: str) -> str:
    if not JWT_SECRET:
        raise RuntimeError("OBSIDIA_JWT_SECRET is required for jwt auth mode")
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "sub": sub,
        "iat": now,
        "exp": now + JWT_TTL_SECONDS,
    }
    h = _b64url_encode(json.dumps(header, separators=(",",":")).encode("utf-8"))
    p = _b64url_encode(json.dumps(payload, separators=(",",":")).encode("utf-8"))
    signing_input = f"{h}.{p}".encode("utf-8")
    sig = _b64url_encode(_sign_hs256(signing_input, JWT_SECRET))
    return f"{h}.{p}.{sig}"

def verify_jwt(token: str) -> Dict[str, Any]:
    if not JWT_SECRET:
        raise HTTPException(status_code=500, detail="JWT not configured")
    try:
        h_b64, p_b64, s_b64 = token.split(".")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token format")
    signing_input = f"{h_b64}.{p_b64}".encode("utf-8")
    expected = _b64url_encode(_sign_hs256(signing_input, JWT_SECRET))
    if not hmac.compare_digest(expected, s_b64):
        raise HTTPException(status_code=401, detail="Invalid token signature")
    payload = json.loads(_b64url_decode(p_b64).decode("utf-8"))
    now = int(time.time())
    if payload.get("iss") != JWT_ISSUER:
        raise HTTPException(status_code=401, detail="Invalid issuer")
    if payload.get("aud") != JWT_AUDIENCE:
        raise HTTPException(status_code=401, detail="Invalid audience")
    if int(payload.get("exp", 0)) < now:
        raise HTTPException(status_code=401, detail="Token expired")
    return payload

def _require_api_key(x_api_key: Optional[str]):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API key auth enabled but OBSIDIA_API_KEY is empty")
    if not x_api_key or x_api_key.strip() != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized (api key)")

def _require_jwt(authorization: Optional[str]):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized (bearer token)")
    token = authorization.split(" ", 1)[1].strip()
    verify_jwt(token)

def enforce_auth(x_api_key: Optional[str], authorization: Optional[str]):
    if AUTH_MODE == "none":
        return
    if AUTH_MODE == "apikey":
        _require_api_key(x_api_key)
        return
    if AUTH_MODE == "jwt":
        _require_jwt(authorization)
        return
    if AUTH_MODE == "both":
        # Accept either API key or JWT
        if x_api_key and API_KEY and x_api_key.strip() == API_KEY:
            return
        if authorization and authorization.lower().startswith("bearer "):
            _require_jwt(authorization)
            return
        raise HTTPException(status_code=401, detail="Unauthorized (api key or bearer token required)")
    raise HTTPException(status_code=500, detail=f"Invalid OBSIDIA_AUTH_MODE: {AUTH_MODE}")

def check_login(username: str, password: str) -> bool:
    # Very simple: compare env credentials
    return bool(OBSIDIA_USER) and bool(OBSIDIA_PASSWORD) and username == OBSIDIA_USER and password == OBSIDIA_PASSWORD


# ---------------------------
# HMAC signing (institutional)
# ---------------------------
import time
from typing import Set, Tuple

HMAC_SECRET = os.getenv("OBSIDIA_HMAC_SECRET", "").encode("utf-8")
HMAC_WINDOW_SECONDS = int(os.getenv("OBSIDIA_HMAC_WINDOW_SECONDS", "60"))
_SEEN_NONCES: Set[str] = set()
_SEEN_NONCES_TS: Dict[str, int] = {}

def _now() -> int:
    return int(time.time())

def _cleanup_nonces(now: int):
    # drop expired nonces
    expired = [n for n,t in _SEEN_NONCES_TS.items() if now - t > HMAC_WINDOW_SECONDS]
    for n in expired:
        _SEEN_NONCES_TS.pop(n, None)
        _SEEN_NONCES.discard(n)

def verify_hmac_signature(body: bytes, timestamp: str | None, signature: str | None, nonce: str | None):
    if not HMAC_SECRET:
        return  # disabled
    if not timestamp or not signature or not nonce:
        raise HTTPException(status_code=401, detail="Missing HMAC headers")
    try:
        ts = int(timestamp)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid timestamp")
    now = _now()
    if abs(now - ts) > HMAC_WINDOW_SECONDS:
        raise HTTPException(status_code=401, detail="HMAC timestamp outside window")

    _cleanup_nonces(now)
    if nonce in _SEEN_NONCES:
        raise HTTPException(status_code=401, detail="Replay detected (nonce reused)")
    _SEEN_NONCES.add(nonce)
    _SEEN_NONCES_TS[nonce] = now

    import hmac as _hmac, hashlib as _hashlib
    msg = (str(ts) + "." + nonce).encode("utf-8") + b"." + body
    expected = _hmac.new(HMAC_SECRET, msg, _hashlib.sha256).hexdigest()
    if not _hmac.compare_digest(expected, signature.strip().lower()):
        raise HTTPException(status_code=401, detail="Invalid HMAC signature")
