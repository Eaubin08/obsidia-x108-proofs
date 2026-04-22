# api_server/signing.py
from __future__ import annotations
import os, base64, pathlib

KEY_DIR = pathlib.Path(os.getenv("OBSIDIA_KEY_DIR", "deploy/keys"))
KEY_DIR.mkdir(parents=True, exist_ok=True)

PRIVATE_KEY_PATH = KEY_DIR / "private_key.pem"
PUBLIC_KEY_PATH = KEY_DIR / "public_key.pem"

def crypto_available() -> bool:
    try:
        import cryptography  # noqa: F401
        return True
    except Exception:
        return False

def ensure_keys() -> tuple[str, str]:
    """Returns (private_pem, public_pem). Generates Ed25519 keypair if missing."""
    if not crypto_available():
        raise RuntimeError("cryptography not installed; cannot generate asymmetric keys")

    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization

    if PRIVATE_KEY_PATH.exists() and PUBLIC_KEY_PATH.exists():
        return (
            PRIVATE_KEY_PATH.read_text(encoding="utf-8"),
            PUBLIC_KEY_PATH.read_text(encoding="utf-8"),
        )

    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()

    priv_pem = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    pub_pem = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

    PRIVATE_KEY_PATH.write_text(priv_pem, encoding="utf-8")
    PUBLIC_KEY_PATH.write_text(pub_pem, encoding="utf-8")
    return priv_pem, pub_pem

def sign_bytes(message: bytes) -> tuple[str, str]:
    """Returns (signature_b64, public_key_pem). Requires cryptography."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization

    priv_pem, pub_pem = ensure_keys()
    priv = serialization.load_pem_private_key(priv_pem.encode("utf-8"), password=None)
    assert isinstance(priv, Ed25519PrivateKey)
    sig = priv.sign(message)
    return base64.b64encode(sig).decode("utf-8"), pub_pem

def verify_bytes(message: bytes, signature_b64: str, public_key_pem: str) -> bool:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    sig = base64.b64decode(signature_b64.encode("utf-8"))
    pub = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
    assert isinstance(pub, Ed25519PublicKey)
    try:
        pub.verify(sig, message)
        return True
    except Exception:
        return False
