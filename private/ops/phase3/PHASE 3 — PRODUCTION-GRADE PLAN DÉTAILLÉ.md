# PHASE 3 — PRODUCTION-GRADE PLAN DÉTAILLÉ

## Objectif
Valider que RFC3161, TLA, Sigma et tRPC peuvent fonctionner en production sous charge, avec défaillances, et avec monitoring.

**Durée estimée** : 3-5 jours
**Équipe** : 1-2 ingénieurs
**Infrastructure** : Kubernetes ou Docker Compose

---

## 1. LOAD TESTING (1-2 jours)

### 1.1 Objectif
Prouver que le système peut traiter 1000+ décisions/sec sans dégradation.

### 1.2 Setup

**Infrastructure** :
```bash
# Docker Compose pour load testing
docker-compose -f docker-compose.load-test.yml up -d

# Services requis :
- os4-platform (backend)
- PostgreSQL (database)
- Redis (cache)
- Prometheus (monitoring)
- Grafana (dashboards)
```

**Configuration** :
```yaml
load_test:
  ramp_up: 60s          # Montée en charge progressive
  steady_state: 300s    # 5 minutes à charge constante
  ramp_down: 60s        # Descente progressive
  target_rps: 1000      # 1000 requêtes/sec
  concurrent_users: 100 # 100 utilisateurs concurrents
```

### 1.3 Scénarios de test

#### Scénario 1 : Orchestration simple
```
POST /api/trpc/orchestration.real
{
  "decision_type": "bank_transfer",
  "amount": 1000,
  "from": "account_123",
  "to": "account_456"
}

Métriques :
- Latency p50, p95, p99
- Throughput (req/sec)
- Error rate
- Database connections
- Memory usage
```

#### Scénario 2 : Attestation RFC3161
```
POST /api/trpc/attestation.verify
{
  "decision_id": "dec_123",
  "merkle_root": "0x..."
}

Métriques :
- RFC3161 verification latency
- TSA response time
- openssl ts -verify latency
- Error rate
```

#### Scénario 3 : TLA Verification
```
POST /api/trpc/tla.verify
{
  "decision_id": "dec_123",
  "trace_path": "/traces/trace_123.json",
  "vars_path": "/traces/vars_123.json"
}

Métriques :
- TLC model checking latency
- Trace/vars parsing latency
- Spec verification latency
- Error rate
```

#### Scénario 4 : Audit retrieval
```
GET /api/trpc/audit.byDecision
{
  "decision_id": "dec_123"
}

Métriques :
- Database query latency
- Audit log retrieval latency
- Memory usage for large logs
- Error rate
```

### 1.4 Outils de load testing

**Apache JMeter** :
```bash
# Installer
apt-get install jmeter

# Créer test plan
jmeter -n -t load_test.jmx -l results.jtl -j jmeter.log

# Générer rapport
jmeter -g results.jtl -o report/
```

**Locust** (Python-based) :
```python
from locust import HttpUser, task, between

class OSPlatformUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def orchestrate(self):
        self.client.post("/api/trpc/orchestration.real", json={
            "decision_type": "bank_transfer",
            "amount": 1000
        })
    
    @task
    def verify_attestation(self):
        self.client.post("/api/trpc/attestation.verify", json={
            "decision_id": "dec_123"
        })
```

**k6** (Go-based) :
```javascript
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '1m', target: 100 },   // Ramp-up
    { duration: '5m', target: 1000 },  // Steady-state
    { duration: '1m', target: 0 },     // Ramp-down
  ],
};

export default function () {
  let res = http.post('http://localhost:3000/api/trpc/orchestration.real', {
    decision_type: 'bank_transfer',
    amount: 1000,
  });
  
  check(res, {
    'status is 200': (r) => r.status === 200,
    'latency < 500ms': (r) => r.timings.duration < 500,
  });
}
```

### 1.5 Métriques à collecter

| Métrique | Target | Alert |
|----------|--------|-------|
| Latency p50 | < 100ms | > 200ms |
| Latency p95 | < 500ms | > 1000ms |
| Latency p99 | < 1000ms | > 2000ms |
| Throughput | 1000+ req/sec | < 800 req/sec |
| Error rate | < 0.1% | > 0.5% |
| CPU usage | < 80% | > 90% |
| Memory usage | < 4GB | > 6GB |
| Database connections | < 50 | > 100 |

### 1.6 Résultats attendus

```
Load Test Results
=================
Ramp-up phase:
  - Latency p50: 45ms
  - Latency p95: 120ms
  - Latency p99: 250ms
  - Throughput: 500 req/sec

Steady-state phase:
  - Latency p50: 50ms
  - Latency p95: 150ms
  - Latency p99: 300ms
  - Throughput: 1000 req/sec
  - Error rate: 0.05%

Ramp-down phase:
  - Graceful shutdown
  - No errors
  - Clean resource cleanup

✅ PASS : Système stable à 1000 req/sec
```

---

## 2. CHAOS ENGINEERING (1-2 jours)

### 2.1 Objectif
Prouver que le système se récupère correctement en cas de défaillances.

### 2.2 Scénarios de chaos

#### Scénario 1 : Défaillance réseau (latency)
```bash
# Ajouter 500ms de latency sur le port 3000
tc qdisc add dev eth0 root netem delay 500ms

# Mesurer l'impact
- Latency p99 : 500ms + 300ms = 800ms
- Error rate : < 0.1%
- Recovery : Immédiat après suppression du chaos

# Nettoyer
tc qdisc del dev eth0 root
```

#### Scénario 2 : Défaillance réseau (packet loss)
```bash
# Perdre 5% des paquets
tc qdisc add dev eth0 root netem loss 5%

# Mesurer l'impact
- Error rate : < 5%
- Retry logic : Fonctionne correctement
- Recovery : Immédiat

# Nettoyer
tc qdisc del dev eth0 root
```

#### Scénario 3 : Défaillance réseau (jitter)
```bash
# Ajouter jitter (variation de latency)
tc qdisc add dev eth0 root netem delay 100ms jitter 50ms

# Mesurer l'impact
- Latency variance : Augmente
- Error rate : < 0.1%
- Recovery : Immédiat
```

#### Scénario 4 : Défaillance TSA (RFC3161)
```bash
# Simuler TSA timeout
- Configurer timeout RFC3161 à 1s
- TSA ne répond pas
- Attendre timeout

# Mesurer l'impact
- RFC3161 status : "incomplete"
- Decision verdict : Inchangé (RFC3161 est optionnel)
- Error rate : 0%
- Recovery : Immédiat après TSA disponible
```

#### Scénario 5 : Défaillance TLC (TLA)
```bash
# Simuler TLC indisponible
- Renommer tlc binary
- Appeler verify_tla.py

# Mesurer l'impact
- TLA status : "incomplete"
- Decision verdict : Inchangé (TLA est optionnel)
- Error rate : 0%
- Recovery : Immédiat après TLC disponible
```

#### Scénario 6 : Défaillance Sigma
```bash
# Simuler Sigma timeout
- Configurer timeout Sigma à 1s
- Sigma ne répond pas
- Attendre timeout

# Mesurer l'impact
- Sigma result : "unknown"
- Decision verdict : Inchangé (Sigma est observation-only)
- Error rate : 0%
- Recovery : Immédiat après Sigma disponible
```

#### Scénario 7 : Défaillance Database
```bash
# Arrêter PostgreSQL
docker stop postgres

# Mesurer l'impact
- Database connections : 0
- Error rate : 100% (pour les opérations DB)
- Audit log : Pas écrit
- Recovery : Immédiat après restart

# Redémarrer
docker start postgres
```

#### Scénario 8 : Défaillance mémoire
```bash
# Limiter mémoire à 512MB
docker update --memory 512m os4-platform

# Mesurer l'impact
- Memory pressure : Augmente
- OOM killer : Peut être déclenché
- Error rate : Peut augmenter
- Recovery : Après augmentation de mémoire
```

#### Scénario 9 : Défaillance CPU
```bash
# Limiter CPU à 1 core
docker update --cpus 1 os4-platform

# Mesurer l'impact
- CPU usage : 100%
- Latency : Augmente
- Throughput : Diminue
- Error rate : Peut augmenter
- Recovery : Après augmentation de CPU
```

#### Scénario 10 : Défaillance disque
```bash
# Remplir le disque
dd if=/dev/zero of=/tmp/fillup bs=1M count=10000

# Mesurer l'impact
- Disk space : 0%
- Audit log write : Échoue
- Error rate : Augmente
- Recovery : Après libération d'espace

# Nettoyer
rm /tmp/fillup
```

### 2.3 Outils de chaos engineering

**Chaos Toolkit** :
```bash
# Installer
pip install chaostoolkit

# Créer experiment.json
{
  "title": "RFC3161 Resilience",
  "description": "Test resilience to TSA failures",
  "steady-state-hypothesis": {
    "title": "System is healthy",
    "probes": [
      {
        "type": "probe",
        "name": "check-endpoint",
        "provider": {
          "type": "http",
          "url": "http://localhost:3000/api/trpc/system.health"
        }
      }
    ]
  },
  "method": [
    {
      "type": "action",
      "name": "stop-tsa",
      "provider": {
        "type": "process",
        "path": "/usr/bin/killall",
        "arguments": "tsa-server"
      }
    }
  ],
  "rollbacks": [
    {
      "type": "action",
      "name": "start-tsa",
      "provider": {
        "type": "process",
        "path": "/usr/bin/systemctl",
        "arguments": "start tsa-server"
      }
    }
  ]
}

# Exécuter
chaos run experiment.json
```

**Gremlin** (SaaS) :
```bash
# Installer Gremlin agent
curl -s https://app.gremlin.com/downloads/gremlin-install.sh | sudo bash

# Créer chaos experiment via UI
- Target : os4-platform container
- Blast radius : 1 container
- Duration : 60s
- Type : Network latency (500ms)
```

**Pumba** (Docker chaos) :
```bash
# Arrêter container aléatoirement
docker run -d \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gaiaadm/pumba \
  pumba --interval 60s kill --signal SIGSTOP os4-platform

# Résultats
- Container arrêté pendant 60s
- Mesurer impact
- Container redémarré automatiquement
```

### 2.4 Métriques de résilience

| Scénario | Impact | Recovery | Status |
|----------|--------|----------|--------|
| Network latency (500ms) | Latency +500ms | Immédiat | ✅ |
| Packet loss (5%) | Error rate +5% | Immédiat | ✅ |
| Network jitter | Latency variance | Immédiat | ✅ |
| TSA failure | RFC3161 incomplete | Immédiat | ✅ |
| TLC failure | TLA incomplete | Immédiat | ✅ |
| Sigma failure | Sigma unknown | Immédiat | ✅ |
| Database failure | Error rate 100% | Après restart | ✅ |
| Memory pressure | Latency +50% | Après cleanup | ✅ |
| CPU limit | Throughput -50% | Après increase | ✅ |
| Disk full | Write failure | Après cleanup | ✅ |

### 2.5 Résultats attendus

```
Chaos Engineering Results
=========================

Network Latency (500ms):
  - Latency p99: 500ms + 300ms = 800ms ✅
  - Error rate: 0.05% ✅
  - Recovery: Immédiat ✅

Packet Loss (5%):
  - Error rate: 4.8% ✅
  - Retry logic: Fonctionne ✅
  - Recovery: Immédiat ✅

TSA Failure:
  - RFC3161 status: "incomplete" ✅
  - Decision verdict: Inchangé ✅
  - Error rate: 0% ✅

Database Failure:
  - Error rate: 100% (expected) ✅
  - Audit log: Pas écrit (expected) ✅
  - Recovery: Immédiat après restart ✅

✅ PASS : Système résilient à toutes les défaillances
```

---

## 3. MONITORING & ALERTING (1 jour)

### 3.1 Objectif
Mettre en place monitoring et alerting pour production.

### 3.2 Métriques à monitorer

**Application** :
- Latency (p50, p95, p99)
- Throughput (req/sec)
- Error rate
- Request count by endpoint
- Request count by status code

**RFC3161** :
- Verification latency
- TSA response time
- Verification success rate
- Verification failure reasons

**TLA** :
- Model checking latency
- Spec verification success rate
- Spec verification failure reasons
- TLC version

**Sigma** :
- Observation latency
- Anomaly detection rate
- Sigma timeout rate

**Audit** :
- Audit log write latency
- Audit log size
- Audit log read latency
- Audit log integrity checks

**Infrastructure** :
- CPU usage
- Memory usage
- Disk usage
- Network I/O
- Database connections
- Database query latency

### 3.3 Setup Prometheus + Grafana

**Prometheus** :
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'os4-platform'
    static_configs:
      - targets: ['localhost:3000']
  
  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:5432']
  
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
```

**Grafana Dashboard** :
```json
{
  "dashboard": {
    "title": "OS4 Platform Production",
    "panels": [
      {
        "title": "Latency p99",
        "targets": [
          {
            "expr": "histogram_quantile(0.99, http_request_duration_seconds_bucket)"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~'5..'}[5m])"
          }
        ]
      },
      {
        "title": "RFC3161 Success Rate",
        "targets": [
          {
            "expr": "rate(rfc3161_verification_success_total[5m])"
          }
        ]
      },
      {
        "title": "TLA Verification Success Rate",
        "targets": [
          {
            "expr": "rate(tla_verification_success_total[5m])"
          }
        ]
      }
    ]
  }
}
```

### 3.4 Alerting Rules

**Prometheus Alerts** :
```yaml
groups:
  - name: os4-platform
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.99, http_request_duration_seconds_bucket) > 1
        for: 5m
        annotations:
          summary: "High latency detected"
      
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~'5..'}[5m]) > 0.01
        for: 5m
        annotations:
          summary: "High error rate detected"
      
      - alert: RFC3161FailureRate
        expr: rate(rfc3161_verification_failure_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "RFC3161 failure rate high"
      
      - alert: TLAFailureRate
        expr: rate(tla_verification_failure_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "TLA failure rate high"
      
      - alert: DatabaseDown
        expr: pg_up == 0
        for: 1m
        annotations:
          summary: "Database is down"
      
      - alert: DiskFull
        expr: node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.1
        for: 5m
        annotations:
          summary: "Disk usage > 90%"
```

### 3.5 Résultats attendus

```
Monitoring & Alerting Setup
============================

Prometheus:
  - Scraping 4 targets
  - 500+ metrics collected
  - Retention: 15 days

Grafana:
  - 5 dashboards created
  - 20+ panels
  - Auto-refresh: 30s

Alerts:
  - 6 alert rules
  - Slack integration
  - PagerDuty integration

✅ PASS : Monitoring et alerting en place
```

---

## 4. RUNBOOK D'INCIDENT & RECOVERY (1 jour)

### 4.1 Objectif
Documenter procédures de recovery pour incidents courants.

### 4.2 Runbooks

#### Runbook 1 : RFC3161 TSA Down

**Symptômes** :
- RFC3161 verification latency > 10s
- RFC3161 failure rate > 50%
- Alert: RFC3161FailureRate

**Diagnostic** :
```bash
# Vérifier TSA endpoint
curl -v http://timestamp.digicert.com

# Vérifier logs
tail -f server/python_agents/verify_rfc3161.log

# Vérifier status
GET /api/trpc/system.health
```

**Recovery** :
```bash
# Option 1 : Attendre TSA recovery (automatique)
# Status passera de "failed" à "verified" automatiquement

# Option 2 : Basculer vers TSA secondaire
# Modifier server/config/rfc3161.ts
# Changer tsa_url de digicert.com à sectigo.com

# Option 3 : Désactiver RFC3161 temporairement
# Modifier server/adapters/rfc3161RealAdapter.ts
# Retourner status "incomplete" au lieu de "failed"

# Vérifier recovery
GET /api/trpc/system.health
# Attendre RFC3161 status = "verified"
```

#### Runbook 2 : TLA Verification Timeout

**Symptômes** :
- TLA verification latency > 30s
- TLA failure rate > 50%
- Alert: TLAFailureRate

**Diagnostic** :
```bash
# Vérifier TLC disponibilité
which tlc
tlc -version

# Vérifier logs
tail -f server/python_agents/verify_tla.log

# Vérifier status
GET /api/trpc/system.health
```

**Recovery** :
```bash
# Option 1 : Augmenter timeout TLA
# Modifier server/config/tla.ts
# tlc_timeout: 60000 (60s)

# Option 2 : Installer TLC
apt-get install tla-tools

# Option 3 : Désactiver TLA temporairement
# Modifier server/adapters/tlaVerifyAdapter.ts
# Retourner status "incomplete" au lieu de "failed"

# Vérifier recovery
GET /api/trpc/system.health
# Attendre TLA status = "verified"
```

#### Runbook 3 : Database Connection Pool Exhausted

**Symptômes** :
- Database connection count = 100 (max)
- Error rate > 50%
- Alert: DatabaseConnectionPoolExhausted

**Diagnostic** :
```bash
# Vérifier connexions actives
psql -c "SELECT count(*) FROM pg_stat_activity;"

# Vérifier requêtes longues
psql -c "SELECT pid, query, query_start FROM pg_stat_activity WHERE state = 'active';"

# Vérifier logs
tail -f /var/log/postgresql/postgresql.log
```

**Recovery** :
```bash
# Option 1 : Tuer requêtes longues
psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE query_start < now() - interval '5 minutes';"

# Option 2 : Augmenter pool size
# Modifier server/config/database.ts
# max_connections: 200

# Option 3 : Redémarrer service
systemctl restart os4-platform

# Vérifier recovery
psql -c "SELECT count(*) FROM pg_stat_activity;"
# Attendre < 50 connexions
```

#### Runbook 4 : Memory Leak

**Symptômes** :
- Memory usage augmente continuellement
- Memory usage > 6GB
- Alert: HighMemoryUsage

**Diagnostic** :
```bash
# Vérifier memory usage
free -h

# Vérifier process memory
ps aux | grep os4-platform

# Vérifier heap dump
node --inspect=0.0.0.0:9229 server/index.js

# Vérifier logs
tail -f server/logs/memory.log
```

**Recovery** :
```bash
# Option 1 : Redémarrer service (court terme)
systemctl restart os4-platform

# Option 2 : Identifier leak (long terme)
# Générer heap dump
curl http://localhost:9229/json/list
# Analyser avec Chrome DevTools

# Option 3 : Augmenter mémoire (court terme)
# Modifier docker-compose.yml
# mem_limit: 8g

# Vérifier recovery
free -h
# Attendre memory usage stable
```

#### Runbook 5 : Audit Log Corruption

**Symptômes** :
- Audit log integrity check échoue
- Hash mismatch détecté
- Alert: AuditLogCorruption

**Diagnostic** :
```bash
# Vérifier intégrité
GET /api/trpc/audit.verify
{
  "decision_id": "dec_123"
}

# Vérifier logs
tail -f server/logs/audit.log

# Vérifier database
psql -c "SELECT * FROM audit_log WHERE decision_id = 'dec_123';"
```

**Recovery** :
```bash
# Option 1 : Restaurer depuis backup
# Identifier backup le plus récent
ls -la /backups/audit_log_*.sql

# Restaurer
psql < /backups/audit_log_2026-04-09.sql

# Option 2 : Réécrire entry
# Recalculer hash
# Réécrire dans database

# Vérifier recovery
GET /api/trpc/audit.verify
# Attendre integrity check = "passed"
```

### 4.3 Résultats attendus

```
Runbook & Recovery
==================

Runbooks créés:
  - RFC3161 TSA Down
  - TLA Verification Timeout
  - Database Connection Pool Exhausted
  - Memory Leak
  - Audit Log Corruption

Chaque runbook contient:
  - Symptômes
  - Diagnostic
  - Recovery steps
  - Verification

✅ PASS : Runbooks en place pour tous les incidents courants
```

---

## 5. VALIDATION FINALE

### 5.1 Checklist

- [ ] Load testing : 1000+ req/sec, p99 < 1000ms
- [ ] Chaos engineering : Tous les scénarios résilients
- [ ] Monitoring : Prometheus + Grafana en place
- [ ] Alerting : 6+ alert rules configurées
- [ ] Runbooks : 5+ runbooks documentés
- [ ] Recovery : Tous les incidents testés
- [ ] Documentation : Complète et à jour
- [ ] Team training : Tous les ingénieurs formés

### 5.2 Résultats attendus

```
PHASE 3 — Production-grade Validation
======================================

Load Testing:
  ✅ 1000+ req/sec sustained
  ✅ Latency p99 < 1000ms
  ✅ Error rate < 0.1%

Chaos Engineering:
  ✅ Network failures resilient
  ✅ Service failures resilient
  ✅ Infrastructure failures resilient

Monitoring & Alerting:
  ✅ Prometheus collecting metrics
  ✅ Grafana dashboards live
  ✅ Alerts firing correctly

Runbook & Recovery:
  ✅ All incidents documented
  ✅ Recovery procedures tested
  ✅ Team trained

PHASE 3 VERDICT: ✅ PRODUCTION-READY
```

---

## 6. TIMELINE

| Phase | Task | Duration | Status |
|-------|------|----------|--------|
| 3.1 | Load testing setup | 4h | ⏳ |
| 3.1 | Load testing execution | 4h | ⏳ |
| 3.2 | Chaos engineering setup | 4h | ⏳ |
| 3.2 | Chaos engineering execution | 8h | ⏳ |
| 3.3 | Monitoring setup | 4h | ⏳ |
| 3.3 | Alerting setup | 4h | ⏳ |
| 3.4 | Runbook creation | 8h | ⏳ |
| 3.4 | Runbook testing | 4h | ⏳ |
| 3.5 | Documentation | 4h | ⏳ |
| 3.5 | Team training | 4h | ⏳ |

**Total** : 48 hours (3-5 jours avec 1-2 ingénieurs)

---

## 7. RESSOURCES REQUISES

**Infrastructure** :
- 1x Load testing machine (8 CPU, 16GB RAM)
- 1x Monitoring machine (4 CPU, 8GB RAM)
- 1x Production machine (8 CPU, 32GB RAM)
- 1x Backup machine (4 CPU, 8GB RAM)

**Outils** :
- Apache JMeter ou k6 (load testing)
- Chaos Toolkit ou Gremlin (chaos engineering)
- Prometheus (monitoring)
- Grafana (dashboards)
- PagerDuty (alerting)
- Slack (notifications)

**Équipe** :
- 1-2 performance engineers
- 1-2 SRE engineers
- 1 DevOps engineer
- 1 documentation writer

---

## 8. RISQUES & MITIGATION

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|-----------|
| Load test crashes system | Medium | High | Start with 100 req/sec, ramp gradually |
| Chaos test causes data loss | Low | Critical | Use staging environment, backup data |
| Monitoring overhead impacts performance | Medium | Medium | Use sampling, aggregate metrics |
| Runbook procedures incorrect | Medium | Medium | Test each runbook before production |
| Team not trained | High | High | Conduct training sessions, create videos |

---

## 9. SUCCÈS CRITERIA

✅ **PHASE 3 est complète si** :
1. Load test : 1000+ req/sec, p99 < 1000ms, error rate < 0.1%
2. Chaos test : Tous les scénarios résilients, recovery automatique
3. Monitoring : Prometheus + Grafana en place, 500+ métriques
4. Alerting : 6+ alert rules, Slack/PagerDuty intégré
5. Runbooks : 5+ runbooks documentés et testés
6. Documentation : Complète, à jour, accessible
7. Team : Formée et capable de supporter production

---

## 10. PROCHAINES ÉTAPES

**Après PHASE 3** :
- Déployer en production
- Activer monitoring et alerting
- Mettre en place on-call rotation
- Commencer incident post-mortems
- Itérer sur runbooks basé sur incidents réels
