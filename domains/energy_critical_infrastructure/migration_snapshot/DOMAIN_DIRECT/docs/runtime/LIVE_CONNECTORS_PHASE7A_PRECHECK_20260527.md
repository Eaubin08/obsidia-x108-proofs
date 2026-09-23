# LIVE_CONNECTORS_PHASE7A_PRECHECK_20260527

Status: DIAGNOSTIC_ONLY

## Port map
- port 8011: LISTEN pid=23324 process=python
- port 8012: LISTEN pid=4168 process=python
- port 5173: DOWN pid= process=
- port 7688: LISTEN pid=17116 process=wslrelay
- port 7688: LISTEN pid=17252 process=com.docker.backend
- port 7475: LISTEN pid=17116 process=wslrelay
- port 7475: LISTEN pid=17252 process=com.docker.backend
- port 8000: DOWN pid= process=
- port 8001: LISTEN pid=17116 process=wslrelay
- port 8001: LISTEN pid=17252 process=com.docker.backend
- port 3002: DOWN pid= process=

## HTTP checks
- Shell Graphiti 8011 health: FAIL http://127.0.0.1:8011/health code= length=
- Shell Graphiti 8011 status: OK http://127.0.0.1:8011/graph/v20/frozen/status code=200 length=390
- Target Brody 8012 health/openapi: OK http://127.0.0.1:8012/openapi.json code=200 length=87701
- Target Brody 8012 graphiti: OK http://127.0.0.1:8012/api/graphiti/status code=200 length=1391
- Workbench 5173: FAIL http://127.0.0.1:5173 code= length=
- Neo4j browser 7475: OK http://127.0.0.1:7475 code=200 length=251
- Possible bus 8001: FAIL http://127.0.0.1:8001/bus/health code= length=
- Possible service 3002: FAIL http://127.0.0.1:3002/health code= length=

## Next

PHASE 7B will decide what to start/reconnect:
- Neo4j live
- Workbench 5173
- bus/gateway 8000/8001/3002 if still useful
- flow metrics
- authorization/policy gateway

Boundary remains KX108_ONLY. No connector may decide.
