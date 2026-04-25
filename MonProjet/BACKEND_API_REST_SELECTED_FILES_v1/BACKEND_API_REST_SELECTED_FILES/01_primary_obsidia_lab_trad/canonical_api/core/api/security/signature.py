import os
import nacl.signing
import nacl.encoding

KEY_PATH = os.path.join(os.path.dirname(__file__), "ed25519_private.key")

def _load_or_create_key():
    if os.path.exists(KEY_PATH):
        with open(KEY_PATH, "rb") as f:
            return nacl.signing.SigningKey(f.read())

    signing_key = nacl.signing.SigningKey.generate()
    with open(KEY_PATH, "wb") as f:
        f.write(signing_key.encode())
    return signing_key

_signing_key = _load_or_create_key()
_verify_key = _signing_key.verify_key

def sign_hash(entry_hash: str) -> str:
    signed = _signing_key.sign(entry_hash.encode())
    return signed.signature.hex()

def get_public_key_hex() -> str:
    return _verify_key.encode(encoder=nacl.encoding.HexEncoder).decode()
