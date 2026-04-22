# Public deploy (secured) — Obsidia API Gateway v2.5

## Recommended stack
- Uvicorn on localhost:8000
- Caddy in front (TLS auto + rate limit + optional basic auth)
- Optional API key (X-API-Key) enforced by the FastAPI app

## 1) Local
```bash
pip install fastapi uvicorn
export OBSIDIA_API_KEY=""     # empty disables key check
uvicorn api_server.main:app --host 127.0.0.1 --port 8000
```

## 2) LAN
```bash
export OBSIDIA_API_KEY="change-me"
uvicorn api_server.main:app --host 0.0.0.0 --port 8000
```

## 3) Public (Caddy)
Set env:
- `ACME_EMAIL`
- `OBSIDIA_DOMAIN` (ex: api.example.com)
- optional `BASIC_AUTH_USER` + `BASIC_AUTH_HASH` (use: `caddy hash-password --plaintext 'pass'`)
- optional `OBSIDIA_API_KEY` (clients must send `X-API-Key`)

Run (docker):
```bash
cd deploy
docker compose up -d
```

## Headers
- API key: `X-API-Key: <value>`
- Basic auth: optional (if enabled via env)

## Rate limiting
Default: 60 req/min per IP (Caddy config). Adjust in `deploy/Caddyfile`.

## Auth modes (maximum)
Set `OBSIDIA_AUTH_MODE`:

- `none`  : no auth (not recommended)
- `apikey`: require `X-API-Key`
- `jwt`   : require `Authorization: Bearer <token>`
- `both`  : accept either api key OR bearer token (recommended for transition)

### JWT (self-contained, no external dependency)
Env:
- `OBSIDIA_JWT_SECRET` (required for jwt/both)
- `OBSIDIA_USER` + `OBSIDIA_PASSWORD` (to mint tokens)
- optional: `OBSIDIA_JWT_TTL_SECONDS`, `OBSIDIA_JWT_ISSUER`, `OBSIDIA_JWT_AUDIENCE`

Mint token:
```bash
curl -X POST "https://$OBSIDIA_DOMAIN/auth/token" \
  -F "username=$OBSIDIA_USER" -F "password=$OBSIDIA_PASSWORD"
```

Call decision:
```bash
curl -X POST "https://$OBSIDIA_DOMAIN/v1/decision" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d @request.json
```

### Recommended production combo
- Caddy TLS + rate-limit
- `OBSIDIA_AUTH_MODE=both`
- API key for services
- JWT for humans / UI


## mTLS (Maximum Lockdown)
Client certificate required. Only clients signed by your CA can connect.
Generate CA and client cert, place CA as deploy/client_ca.crt.
Use docker-compose.mtls.yml instead of default.

## HMAC request signing (anti-tamper + anti-replay)
If `OBSIDIA_HMAC_SECRET` is set, every request to `/v1/*` and `/auth/*` must include:

- `X-Obsidia-Timestamp`: unix seconds
- `X-Obsidia-Nonce`: random unique string
- `X-Obsidia-Signature`: hex(HMAC_SHA256(secret, f"{ts}.{nonce}."+body))

Env:
- `OBSIDIA_HMAC_SECRET`
- optional: `OBSIDIA_HMAC_WINDOW_SECONDS` (default 60)

Example (Python):
```python
import time, os, hmac, hashlib, secrets, requests, json
secret = os.environ["OBSIDIA_HMAC_SECRET"].encode()
ts = str(int(time.time()))
nonce = secrets.token_hex(16)
body = json.dumps(payload).encode()
msg = (ts + "." + nonce).encode() + b"." + body
sig = hmac.new(secret, msg, hashlib.sha256).hexdigest()
headers = {"X-Obsidia-Timestamp": ts, "X-Obsidia-Nonce": nonce, "X-Obsidia-Signature": sig}
requests.post("https://<domain>/v1/decision", headers=headers, json=payload)
```

## Append-only signed audit log (hash chain)
The gateway writes:
- `api_store/audit.log` (JSONL events)
- `api_store/audit.chain` (hash chain entries)

Endpoint:
- `GET /v1/audit/chain` (protected by API key/JWT)


## WORM / Immutable audit storage (S3 Object Lock / MinIO)
Goal: store daily snapshots of audit.log and audit.chain in an immutable bucket.
Included:
- deploy/docker-compose.minio.yml (MinIO)
- api_server/worm_uploader.py (optional, uses boto3)
- deploy/obsidia-worm.service + obsidia-worm.timer

Run MinIO:
```bash
cd deploy
docker compose -f docker-compose.minio.yml up -d
```
Daily upload:
```bash
export OBSIDIA_WORM_ENABLED=1
export OBSIDIA_WORM_ENDPOINT=http://127.0.0.1:9000
export MINIO_ROOT_USER=minioadmin
export MINIO_ROOT_PASSWORD=minioadmin
pip install boto3
python api_server/worm_uploader.py
```


## Daily signed rotation + public attestation (existence proof)
Adds daily attestation files based on audit.log/audit.chain hashes.
Attestations are chained via prev_attestation_hash.

Generate:
```bash
python api_server/run_attestation.py
```
If `cryptography` is installed, Obsidia generates an Ed25519 keypair in `deploy/keys/` and signs each attestation.
Public attestation pattern: publish only `day + attestation_hash` externally as a timestamp witness.
