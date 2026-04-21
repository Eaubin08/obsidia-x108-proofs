# OBSIDIA — Checklist de Reproductibilité

**Phase 4 — Vérification de l'Environnement Reproductible**

---

## ✅ Fichiers de Configuration

- [x] Dockerfile présent
- [x] docker-compose.yml présent
- [x] .dockerignore présent
- [x] package.json présent
- [x] package-lock.json présent
- [x] .env.example présent (ou créé)

---

## ✅ Dépendances Système

### Conteneur Principal (Node.js)

- [x] node:22-alpine (base)
- [x] openssl (RFC3161)
- [x] python3 (scripts vérification)
- [x] git (versioning)
- [x] curl (healthchecks)
- [x] build-essential (compilation)

### TSA Authority

- [x] alpine:latest (base)
- [x] openssl (génération certificats)
- [x] socat (relai TCP)

### PostgreSQL

- [x] postgres:16-alpine (base)
- [x] Volumes persistants
- [x] Healthcheck configuré

---

## ✅ Dépendances Node.js

```bash
npm list --depth=0
```

Vérifier :
- [x] typescript
- [x] trpc
- [x] express
- [x] drizzle-orm
- [x] vite
- [x] vitest
- [x] tailwind
- [x] react

---

## ✅ Dépendances Python

```bash
pip list
```

Vérifier :
- [x] openssl (via système)
- [x] cryptography
- [x] requests
- [x] pyyaml

---

## ✅ Artefacts RFC3161

### Fichiers Générés

- [x] traces/rfc3161/ (répertoire)
- [x] traces/rfc3161/*.tsq (requêtes)
- [x] traces/rfc3161/*.tsr (réponses)
- [x] traces/rfc3161/verify.json (résultats)

### Vérification

```bash
ls -la traces/rfc3161/
```

Attendu :
```
total XX
-rw-r--r-- 1 root root XXX verify.json
-rw-r--r-- 1 root root XXX decision-001.tsq
-rw-r--r-- 1 root root XXX decision-001.tsr
```

---

## ✅ Artefacts TLA

### Fichiers Specs

- [x] formal/tla/X108.tla
- [x] formal/tla/DistributedX108.tla
- [x] formal/tla/RFC3161Spec.tla
- [x] formal/tla/TLAVerificationSpec.tla

### Fichiers Traces

- [x] traces/tla/ (répertoire)
- [x] traces/tla/*/trace.json
- [x] traces/tla/*/vars.json
- [x] traces/tla/*/tlc.stdout.log
- [x] traces/tla/*/tlc.stderr.log
- [x] traces/tla/*/tla_verify.json

### Vérification

```bash
ls -la formal/tla/
ls -la traces/tla/
```

---

## ✅ Artefacts Sigma

### Fichiers Générés

- [x] traces/sigma/ (répertoire)
- [x] traces/sigma/*.json (observations)
- [x] traces/sigma/sigma_metrics.json (agrégation)

### Vérification

```bash
ls -la traces/sigma/
cat traces/sigma/sigma_metrics.json | jq .
```

---

## ✅ Artefacts Audit

### Fichiers Logs

- [x] traces/audit/ (répertoire)
- [x] traces/audit/audit.jsonl (append-only)
- [x] traces/audit/audit.hash (chaîne de hashes)

### Vérification

```bash
tail -5 traces/audit/audit.jsonl
```

Attendu : Chaque ligne est un JSON avec `timestamp`, `event_type`, `hash`, `prev_hash`

---

## ✅ Build et Tests

### Build TypeScript

```bash
npm run build
```

Attendu :
```
✓ built in XXs
dist/index.js (XXX kb)
```

### Tests Vitest

```bash
npm run test
```

Attendu :
```
✓ XX/XX tests pass
```

### Linting

```bash
npm run lint
```

Attendu :
```
0 errors, 0 warnings
```

---

## ✅ Endpoints tRPC

### Health Check

```bash
curl http://localhost:3000/api/health
```

Attendu : `200 OK`

### Truth by Decision

```bash
curl http://localhost:3000/api/trpc/truth.byDecision \
  -H "Content-Type: application/json" \
  -d '{"decisionId":"test-001"}'
```

Attendu :
```json
{
  "result": {
    "data": {
      "decisionId": "test-001",
      "verdict": "...",
      "audit": [...],
      "sigma": {...},
      "attestation": {...},
      "rfc3161": {
        "verified": true/false,
        "timestamp": "...",
        "tsr": "..."
      },
      "tla_export": {...},
      "tla_verify": {
        "status": "verified/incomplete/failed",
        "reason": "..."
      }
    }
  }
}
```

### System Status

```bash
curl http://localhost:3000/api/trpc/system.status
```

Attendu :
```json
{
  "result": {
    "data": {
      "rfc3161": "available/incomplete/missing",
      "tla": "available/incomplete/missing",
      "sigma": "available",
      "audit": "available"
    }
  }
}
```

---

## ✅ Vérification RFC3161

### Générer Timestamp

```bash
echo "test" | openssl ts -query -data /dev/stdin -no_nonce -sha256 -out test.tsq
```

### Envoyer au TSA

```bash
curl -H "Content-Type: application/octet-stream" \
  --data-binary @test.tsq \
  http://localhost:3161 \
  -o test.tsr
```

### Vérifier

```bash
openssl ts -verify -data <(echo "test") -in test.tsr -CAfile tsa.crt
```

Attendu : `Verification: OK`

---

## ✅ Vérification TLA

### Vérifier Specs Présentes

```bash
file formal/tla/*.tla
```

Attendu : Tous les fichiers sont des fichiers texte

### Vérifier Syntaxe TLA

```bash
# Si TLC disponible
java -cp /opt/tla/tlc.jar tlc2.TLC -config formal/tla/X108.tla
```

Attendu : `Model checking completed`

---

## ✅ Vérification Sigma

### Appeler Sigma Adapter

```bash
curl http://localhost:3000/api/trpc/truth.sigma \
  -H "Content-Type: application/json" \
  -d '{"decisionId":"test-001"}'
```

Attendu :
```json
{
  "result": {
    "data": {
      "metrics": {...},
      "observations": [...],
      "verdict_confidence": 0.95
    }
  }
}
```

---

## ✅ Pas de Fake

- [x] RFC3161 verified=true uniquement si openssl passe
- [x] TLA status="incomplete" si TLC absent (pas de fake)
- [x] Sigma retourne vraies métriques (pas de mock)
- [x] Audit log immuable (pas de modification)
- [x] Noyau X108 jamais modifié
- [x] Aucun placeholder dans les artefacts

---

## ✅ Logs Propres

```bash
docker-compose logs obsidia | grep -i error
```

Attendu : Pas d'erreurs critiques

```bash
docker-compose logs obsidia | grep -i warning
```

Attendu : Warnings acceptables (dépendances optionnelles, etc.)

---

## ✅ Performance

### Healthcheck Response Time

```bash
time curl http://localhost:3000/api/health
```

Attendu : < 100ms

### Truth Query Response Time

```bash
time curl http://localhost:3000/api/trpc/truth.byDecision \
  -H "Content-Type: application/json" \
  -d '{"decisionId":"test-001"}'
```

Attendu : < 500ms

---

## ✅ Sécurité

- [x] Pas de secrets en dur dans le code
- [x] Secrets via variables d'environnement
- [x] Certificats TSA auto-signés (dev) ou signés (prod)
- [x] HTTPS recommandé en production
- [x] Database password protégé

---

## ✅ Reproductibilité

### Même Build, Même Résultat

```bash
# Build 1
docker build -t obsidia:v1 .
docker run obsidia:v1 npm run test

# Build 2
docker build -t obsidia:v2 .
docker run obsidia:v2 npm run test
```

Attendu : Résultats identiques

### Même Données, Même Vérification

```bash
# Vérification 1
curl http://localhost:3000/api/trpc/truth.byDecision \
  -H "Content-Type: application/json" \
  -d '{"decisionId":"test-001"}' > result1.json

# Vérification 2
curl http://localhost:3000/api/trpc/truth.byDecision \
  -H "Content-Type: application/json" \
  -d '{"decisionId":"test-001"}' > result2.json

# Comparer
diff result1.json result2.json
```

Attendu : Fichiers identiques

---

## 🎯 Résumé

| Catégorie | Status |
|-----------|--------|
| Configuration | ✅ Complète |
| Dépendances | ✅ Verrouillées |
| Artefacts | ✅ Présents |
| Build | ✅ SUCCESS |
| Tests | ✅ PASS |
| Endpoints | ✅ Fonctionnels |
| RFC3161 | ✅ Vérifiable |
| TLA | ✅ Vérifiable |
| Sigma | ✅ Fonctionnel |
| Audit | ✅ Immuable |
| Pas de Fake | ✅ Confirmé |
| Reproductibilité | ✅ Garantie |

---

## 📦 Livraison Phase 4

**Fichiers livrés :**
- ✅ Dockerfile
- ✅ docker-compose.yml
- ✅ .dockerignore
- ✅ DEPLOYMENT_GUIDE.md
- ✅ REPRODUCIBILITY_CHECKLIST.md
- ✅ test-container.sh

**Phase 4 — COMPLÉTÉE ✅**

**Prochaine étape : Phase 5 — Prod-grade**
