# OBSIDIA — Guide de Déploiement Conteneurisé

**Phase 4 — Conteneurisation**

---

## 📋 Prérequis

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB espace disque

---

## 🚀 Démarrage Rapide

### 1. Construire l'image

```bash
docker build -t obsidia:latest .
```

**Sortie attendue :**
```
Step 1/XX : FROM node:22-alpine
...
Successfully tagged obsidia:latest
```

### 2. Lancer le stack complet

```bash
docker-compose up -d
```

**Services démarrés :**
- `obsidia` (port 3000)
- `tsa-authority` (port 3161)
- `postgres` (port 5432)

### 3. Vérifier la santé

```bash
docker-compose ps
```

**Sortie attendue :**
```
NAME                  STATUS
obsidia-platform      Up 2 minutes (healthy)
obsidia-tsa           Up 2 minutes
obsidia-db            Up 2 minutes (healthy)
```

### 4. Consulter les logs

```bash
docker-compose logs -f obsidia
```

---

## 🔐 RFC3161 — Vérification TSA

### Générer une demande de timestamp

```bash
# Créer un fichier à horodater
echo "test data" > test.txt

# Générer une requête TSQ
openssl ts -query -data test.txt -no_nonce -sha256 -out test.tsq

# Envoyer au TSA du conteneur
curl -H "Content-Type: application/octet-stream" \
  --data-binary @test.tsq \
  http://localhost:3161 \
  -o test.tsr

# Vérifier la signature
openssl ts -verify -data test.txt -in test.tsr -CAfile <(docker-compose exec -T tsa-authority cat /etc/tsa/tsa.crt)
```

**Résultat attendu :**
```
Verification: OK
```

---

## 🧮 TLA — Vérification TLC

### Vérifier que les specs sont présentes

```bash
docker-compose exec obsidia ls -la formal/tla/
```

**Fichiers attendus :**
- `X108.tla` (spec principale)
- `DistributedX108.tla` (spec distribuée)
- `RFC3161Spec.tla` (addon RFC)
- `TLAVerificationSpec.tla` (addon vérification)

### Exécuter TLC

```bash
docker-compose exec obsidia java -cp /opt/tla/tlc.jar tlc2.TLC \
  -config formal/tla/X108.tla \
  -workers 4
```

**Résultat attendu :**
```
Model checking completed. No error found.
```

---

## 📊 Vérifier la Vérité Backend

### Appeler l'endpoint truth

```bash
curl http://localhost:3000/api/trpc/truth.byDecision \
  -H "Content-Type: application/json" \
  -d '{"decisionId":"test-001"}'
```

**Réponse attendue :**
```json
{
  "result": {
    "data": {
      "decisionId": "test-001",
      "verdict": "ALLOW",
      "audit": [...],
      "sigma": {...},
      "attestation": {...},
      "rfc3161": {
        "verified": true,
        "timestamp": "2026-04-10T...",
        "tsr": "..."
      },
      "tla_export": {...},
      "tla_verify": {
        "status": "incomplete",
        "reason": "TLC not available in sandbox"
      }
    }
  }
}
```

---

## 🛑 Arrêter le Stack

```bash
docker-compose down
```

### Supprimer les volumes (données persistantes)

```bash
docker-compose down -v
```

---

## 🔧 Configuration Avancée

### Variables d'environnement

Créer un fichier `.env` :

```env
NODE_ENV=production
DATABASE_URL=postgresql://obsidia:password@postgres:5432/obsidia
JWT_SECRET=your-secret-key
RFC3161_TSA_URL=http://tsa-authority:3161
TLA_SPECS_PATH=/app/formal/tla
TLC_PATH=/opt/tla/tlc.jar
```

### Utiliser PostgreSQL réelle

```bash
docker-compose up -d postgres
# Attendre que postgres soit prêt
sleep 5
docker-compose up -d obsidia
```

### Logs persistants

```bash
docker-compose logs --tail=100 obsidia > logs.txt
```

---

## 🧪 Tests de Charge

### Installer Apache Bench

```bash
apt-get install apache2-utils
```

### Lancer 1000 requêtes

```bash
ab -n 1000 -c 10 http://localhost:3000/api/health
```

**Résultat attendu :**
```
Requests per second: 500+
Failed requests: 0
```

---

## 📈 Monitoring

### Vérifier l'utilisation des ressources

```bash
docker stats obsidia-platform
```

### Logs du TSA

```bash
docker-compose logs tsa-authority
```

### Logs de PostgreSQL

```bash
docker-compose logs postgres
```

---

## 🚨 Dépannage

### Le conteneur ne démarre pas

```bash
docker-compose logs obsidia
```

Vérifier les erreurs de build ou de configuration.

### TSA ne répond pas

```bash
docker-compose restart tsa-authority
```

### PostgreSQL connexion refusée

```bash
docker-compose exec postgres psql -U obsidia -d obsidia
```

---

## ✅ Checklist de Vérification

- [ ] Docker et Docker Compose installés
- [ ] Dockerfile construit sans erreur
- [ ] docker-compose.yml valide
- [ ] Services démarrent et sont healthy
- [ ] RFC3161 TSA répond sur port 3161
- [ ] TLC specs présentes dans `/app/formal/tla`
- [ ] Endpoint truth.byDecision retourne données réelles
- [ ] RFC3161 verified=true pour requête valide
- [ ] TLA status="incomplete" documenté honnêtement
- [ ] Pas de fake, pas de placeholder
- [ ] Logs propres, pas d'erreurs critiques

---

## 📦 Livraison

Une fois tous les tests passés :

```bash
# Exporter l'image
docker save obsidia:latest -o obsidia-latest.tar.gz

# Compresser le projet
tar -czf obsidia-containerized.tar.gz .

# Livrer les deux fichiers
```

---

## 🎯 Résumé Phase 4

**Objectif :** Environnement reproductible et verrouillé

**Livré :**
- ✅ Dockerfile production-ready
- ✅ docker-compose.yml avec TSA + TLC + PostgreSQL
- ✅ Script de validation
- ✅ Guide de déploiement complet
- ✅ Checklist de vérification
- ✅ Stratégie de monitoring

**Prochaine étape :** Phase 5 — Prod-grade (load tests, chaos, healthchecks)
