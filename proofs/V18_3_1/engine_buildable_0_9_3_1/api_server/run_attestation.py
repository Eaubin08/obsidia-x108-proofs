# api_server/run_attestation.py
from __future__ import annotations
import json
from api_server.attestation import build_attestation, write_attestation
from api_server.signing import crypto_available, sign_bytes

def main():
    att = build_attestation()
    # Sign only the base payload (without attestation_hash to avoid circularity)
    base = {k: att[k] for k in att if k != "attestation_hash"}
    raw = json.dumps(base, separators=(",", ":"), sort_keys=True).encode("utf-8")

    sig_b64 = None
    pub_pem = None
    if crypto_available():
        sig_b64, pub_pem = sign_bytes(raw)

    path = write_attestation(att, sig_b64, pub_pem)
    print(str(path))
    print("attestation_hash:", att["attestation_hash"])
    if sig_b64:
        print("signature: present")
    else:
        print("signature: absent (install cryptography to enable Ed25519 signing)")

if __name__ == "__main__":
    main()
