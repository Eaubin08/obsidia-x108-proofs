# OBSIDIA — Runbooks d'Incident

---

## 🚨 Incident : App Down

### Symptômes
- Endpoint `/api/health` retourne 500 ou timeout
- Alertes : `AppDown`, `HighErrorRate`
- Logs : Erreurs critiques, stack traces

### Diagnostic

```bash
# Vérifier le statut du conteneur
docker-compose ps

# Vérifier les logs
docker-compose logs -f obsidia | tail -100

# Vérifier la connectivité
curl http://localhost:3000/api/health

# Vérifier les ressources
docker stats obsidia-platform
```

### Résolution

#### Étape 1 : Redémarrage gracieux
```bash
docker-compose restart obsidia
sleep 5
curl http://localhost:3000/api/health
```

#### Étape 2 : Si redémarrage échoue
```bash
# Vérifier les erreurs de build
docker-compose logs obsidia | grep -i error

# Reconstruire l'image
docker-compose down
docker build -t obsidia:latest .
docker-compose up -d
```

#### Étape 3 : Si toujours down
```bash
# Vérifier les dépendances
docker-compose ps

# Redémarrer toutes les dépendances
docker-compose down
docker-compose up -d

# Attendre que tout soit prêt
sleep 30
curl http://localhost:3000/api/health
```

### Escalade
- Si toujours down après 5 minutes : escalader à l'équipe SRE
- Collecter les logs complets : `docker-compose logs > incident.log`
- Créer un ticket incident avec les logs

---

## 🚨 Incident : High Response Time

### Symptômes
- P95 response time > 1s
- Alertes : `HighResponseTime`
- Utilisateurs signalent lenteur

### Diagnostic

```bash
# Vérifier les métriques Prometheus
curl http://localhost:9090/api/v1/query?query=histogram_quantile\(0.95,rate\(http_request_duration_seconds_bucket\[5m\]\)\)

# Vérifier les logs lents
docker-compose logs obsidia | grep "duration"

# Vérifier les ressources
docker stats obsidia-platform

# Vérifier la base de données
docker-compose exec postgres psql -U obsidia -c "SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
```

### Résolution

#### Étape 1 : Identifier la cause
```bash
# Requêtes lentes
docker-compose logs obsidia | grep "duration.*ms" | sort -t: -k2 -rn | head -20

# Connexions DB bloquées
docker-compose exec postgres psql -U obsidia -c "SELECT * FROM pg_locks WHERE NOT granted;"

# Charge système
docker stats --no-stream
```

#### Étape 2 : Optimiser
```bash
# Augmenter les workers Node
docker-compose exec obsidia export NODE_WORKERS=8

# Augmenter la mémoire
docker-compose down
# Éditer docker-compose.yml : mem_limit: 2g
docker-compose up -d

# Optimiser les requêtes DB
docker-compose exec postgres ANALYZE;
```

#### Étape 3 : Monitorer
```bash
# Vérifier que la latence diminue
watch -n 5 'curl -s http://localhost:9090/api/v1/query?query=histogram_quantile\(0.95,rate\(http_request_duration_seconds_bucket\[5m\]\)\) | jq .'
```

### Escalade
- Si latence persiste > 2s : escalader à l'équipe Backend
- Collecter les métriques Prometheus : `curl http://localhost:9090/api/v1/query_range?query=... > metrics.json`

---

## 🚨 Incident : High Error Rate

### Symptômes
- Taux d'erreur 5xx > 5%
- Alertes : `HighErrorRate`
- Utilisateurs signalent des erreurs

### Diagnostic

```bash
# Vérifier le taux d'erreur
curl http://localhost:9090/api/v1/query?query=rate\(http_requests_total\{status=~\"5..\"\}\[5m\]\)

# Vérifier les erreurs dans les logs
docker-compose logs obsidia | grep -i error | tail -50

# Vérifier les types d'erreur
docker-compose logs obsidia | grep "500\|502\|503\|504"
```

### Résolution

#### Étape 1 : Identifier l'erreur
```bash
# Erreurs d'application
docker-compose logs obsidia | grep -A 5 "Error:"

# Erreurs de base de données
docker-compose logs obsidia | grep "database\|query\|connection"

# Erreurs de dépendances
docker-compose logs obsidia | grep "tsa-authority\|postgres"
```

#### Étape 2 : Corriger
```bash
# Si erreur DB : redémarrer PostgreSQL
docker-compose restart postgres

# Si erreur TSA : redémarrer TSA
docker-compose restart tsa-authority

# Si erreur app : vérifier les logs détaillés
docker-compose logs obsidia | grep -B 5 -A 5 "Error:"
```

#### Étape 3 : Monitorer
```bash
# Vérifier que le taux d'erreur diminue
watch -n 5 'curl -s http://localhost:9090/api/v1/query?query=rate\(http_requests_total\{status=~\"5..\"\}\[5m\]\) | jq .'
```

---

## 🚨 Incident : TSA Down

### Symptômes
- Alertes : `TSADown`
- RFC3161 verification échoue
- Endpoint `/api/trpc/truth.rfc3161` retourne erreur

### Diagnostic

```bash
# Vérifier le statut du conteneur
docker-compose ps tsa-authority

# Vérifier les logs
docker-compose logs tsa-authority

# Vérifier la connectivité
curl -v telnet://localhost:3161

# Vérifier le certificat
docker-compose exec tsa-authority openssl x509 -in /etc/tsa/tsa.crt -text -noout
```

### Résolution

#### Étape 1 : Redémarrer TSA
```bash
docker-compose restart tsa-authority
sleep 5
curl -v telnet://localhost:3161
```

#### Étape 2 : Régénérer le certificat
```bash
docker-compose exec tsa-authority rm -f /etc/tsa/tsa.crt /etc/tsa/tsa.key
docker-compose restart tsa-authority
sleep 5
curl -v telnet://localhost:3161
```

#### Étape 3 : Vérifier la connectivité réseau
```bash
# Vérifier que le réseau Docker fonctionne
docker network ls
docker network inspect obsidia-net

# Vérifier les routes
docker-compose exec obsidia route -n
```

---

## 🚨 Incident : PostgreSQL Down

### Symptômes
- Alertes : `PostgreSQLDown`
- Erreurs de connexion DB
- Endpoint `/api/trpc/truth.byDecision` retourne erreur

### Diagnostic

```bash
# Vérifier le statut du conteneur
docker-compose ps postgres

# Vérifier les logs
docker-compose logs postgres

# Vérifier la connectivité
docker-compose exec postgres psql -U obsidia -d obsidia -c "SELECT 1;"

# Vérifier l'espace disque
docker-compose exec postgres df -h
```

### Résolution

#### Étape 1 : Redémarrer PostgreSQL
```bash
docker-compose restart postgres
sleep 10
docker-compose exec postgres psql -U obsidia -d obsidia -c "SELECT 1;"
```

#### Étape 2 : Vérifier l'intégrité de la base
```bash
docker-compose exec postgres psql -U obsidia -d obsidia -c "REINDEX DATABASE obsidia;"
```

#### Étape 3 : Récupérer depuis backup
```bash
# Si la base est corrompue
docker-compose down
docker volume rm obsidia_postgres-data
docker-compose up -d postgres
sleep 10

# Restaurer depuis backup (si disponible)
docker-compose exec postgres psql -U obsidia -d obsidia < backup.sql
```

---

## 🚨 Incident : High Memory Usage

### Symptômes
- Alertes : `HighMemoryUsage`, `ContainerHighMemory`
- App lente ou crash
- OOMKilled dans les logs

### Diagnostic

```bash
# Vérifier l'utilisation mémoire
docker stats --no-stream

# Vérifier les processus gourmands
docker-compose exec obsidia ps aux --sort=-%mem | head -10

# Vérifier les fuites mémoire
docker-compose logs obsidia | grep -i "memory\|leak\|gc"
```

### Résolution

#### Étape 1 : Augmenter la limite mémoire
```bash
# Éditer docker-compose.yml
# Augmenter mem_limit: 1g → mem_limit: 2g

docker-compose down
docker-compose up -d
```

#### Étape 2 : Optimiser l'app
```bash
# Forcer le garbage collection
docker-compose exec obsidia kill -USR2 <pid>

# Redémarrer l'app
docker-compose restart obsidia
```

#### Étape 3 : Monitorer
```bash
# Vérifier que la mémoire diminue
watch -n 5 'docker stats --no-stream'
```

---

## 🚨 Incident : High Disk Usage

### Symptômes
- Alertes : `HighDiskUsage`, `DiskSpaceRunningOut`
- Erreurs d'écriture dans les logs
- App ralentit ou crash

### Diagnostic

```bash
# Vérifier l'espace disque
df -h

# Vérifier les volumes Docker
docker volume ls
docker volume inspect obsidia_postgres-data

# Vérifier les fichiers volumineux
docker-compose exec obsidia du -sh /app/* | sort -rh

# Vérifier les logs
docker-compose logs obsidia | wc -l
```

### Résolution

#### Étape 1 : Nettoyer les logs
```bash
# Archiver les logs anciens
docker-compose logs obsidia > logs-$(date +%Y%m%d).log
docker-compose logs --tail=1000 obsidia > logs-recent.log

# Nettoyer les logs Docker
docker system prune -a --volumes
```

#### Étape 2 : Nettoyer les traces
```bash
# Archiver les traces anciennes
tar -czf traces-$(date +%Y%m%d).tar.gz traces/
rm -rf traces/*

# Garder les traces récentes
find traces/ -mtime +30 -delete
```

#### Étape 3 : Augmenter l'espace disque
```bash
# Ajouter un volume supplémentaire
# Éditer docker-compose.yml
# Ajouter un nouveau volume

docker-compose down
docker-compose up -d
```

---

## 🚨 Incident : RFC3161 Verification Failures

### Symptômes
- Alertes : `RFC3161VerificationFailed`
- Endpoint `/api/trpc/truth.rfc3161` retourne `verified: false`
- Logs : Erreurs de vérification

### Diagnostic

```bash
# Vérifier les logs de vérification
docker-compose logs obsidia | grep -i "rfc3161\|verification"

# Vérifier les artefacts
ls -la traces/rfc3161/

# Vérifier le certificat TSA
docker-compose exec tsa-authority openssl x509 -in /etc/tsa/tsa.crt -text -noout

# Tester manuellement
echo "test" | openssl ts -query -data /dev/stdin -no_nonce -sha256 -out test.tsq
curl -H "Content-Type: application/octet-stream" --data-binary @test.tsq http://localhost:3161 -o test.tsr
openssl ts -verify -data <(echo "test") -in test.tsr -CAfile tsa.crt
```

### Résolution

#### Étape 1 : Vérifier le certificat TSA
```bash
# Régénérer le certificat
docker-compose exec tsa-authority rm -f /etc/tsa/tsa.crt /etc/tsa/tsa.key
docker-compose restart tsa-authority
sleep 5
```

#### Étape 2 : Tester la vérification
```bash
# Générer une nouvelle requête
echo "test" | openssl ts -query -data /dev/stdin -no_nonce -sha256 -out test.tsq

# Envoyer au TSA
curl -H "Content-Type: application/octet-stream" --data-binary @test.tsq http://localhost:3161 -o test.tsr

# Vérifier
openssl ts -verify -data <(echo "test") -in test.tsr -CAfile <(docker-compose exec -T tsa-authority cat /etc/tsa/tsa.crt)
```

---

## 🚨 Incident : TLA Verification Incomplete

### Symptômes
- Alertes : `TLAVerificationIncomplete`
- Endpoint `/api/trpc/truth.tla` retourne `status: incomplete`
- TLC non disponible

### Diagnostic

```bash
# Vérifier les specs TLA
docker-compose exec obsidia ls -la formal/tla/

# Vérifier TLC
docker-compose exec obsidia which java
docker-compose exec obsidia ls -la /opt/tla/

# Vérifier les logs
docker-compose logs obsidia | grep -i "tla\|tlc"
```

### Résolution

#### Étape 1 : Installer TLC
```bash
# Télécharger TLC
docker-compose exec obsidia wget -q https://github.com/tlaplus/tlaplus/releases/download/v1.7.9/tla2tools.jar -O /opt/tla/tlc.jar

# Vérifier l'installation
docker-compose exec obsidia java -cp /opt/tla/tlc.jar tlc2.TLC -version
```

#### Étape 2 : Exécuter TLC
```bash
# Exécuter TLC sur X108.tla
docker-compose exec obsidia java -cp /opt/tla/tlc.jar tlc2.TLC \
  -config formal/tla/X108.tla \
  -workers 4
```

#### Étape 3 : Monitorer
```bash
# Vérifier que TLA status passe à "verified"
curl http://localhost:3000/api/trpc/truth.tla
```

---

## 📞 Escalade

### Niveau 1 : Incident Mineur
- Response time > 1s
- Error rate > 5%
- Disk usage > 85%

**Action :** Appliquer les runbooks ci-dessus

### Niveau 2 : Incident Majeur
- App down
- Database down
- TSA down
- Error rate > 20%

**Action :** 
1. Appliquer les runbooks
2. Notifier l'équipe SRE
3. Créer un ticket incident

### Niveau 3 : Incident Critique
- Data loss
- Security breach
- Multiple services down
- Audit log corruption

**Action :**
1. Isoler les services affectés
2. Notifier immédiatement l'équipe SRE
3. Créer un ticket incident P1
4. Activer le plan de continuité

---

## 📊 Métriques à Monitorer

| Métrique | Seuil Warning | Seuil Critical |
|----------|---------------|----------------|
| Response Time P95 | > 500ms | > 1s |
| Error Rate | > 1% | > 5% |
| CPU Usage | > 70% | > 90% |
| Memory Usage | > 75% | > 85% |
| Disk Usage | > 80% | > 90% |
| DB Connections | > 50 | > 80 |
| TSA Response Time | > 1s | > 2s |
| RFC3161 Failures | > 0.1% | > 1% |
| TLA Status | incomplete | failed |
| Audit Log Writes | > 0 errors | > 1 error |

---

## 🔄 Post-Incident

### Après chaque incident :

1. **Documenter** : Créer un post-mortem
2. **Analyser** : Identifier la cause racine
3. **Corriger** : Appliquer un fix
4. **Prévenir** : Ajouter une alerte ou un test
5. **Communiquer** : Notifier l'équipe

### Template Post-Mortem

```markdown
# Post-Mortem — [Incident Name]

## Timeline
- T+0 : Incident détecté
- T+X : Action prise
- T+Y : Incident résolu

## Cause Racine
[Description]

## Impact
- Utilisateurs affectés : X
- Durée : Y minutes
- Données perdues : Z

## Actions Correctives
- [ ] Fix implémenté
- [ ] Alerte ajoutée
- [ ] Test ajouté
- [ ] Documentation mise à jour

## Prévention
- [Mesure 1]
- [Mesure 2]
- [Mesure 3]
```
