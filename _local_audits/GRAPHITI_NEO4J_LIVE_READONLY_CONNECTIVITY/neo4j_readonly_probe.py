import os
from pathlib import Path

print("=== NEO4J READONLY PROBE ===")
print("NEO4J_URI=", os.environ.get("NEO4J_URI"))
print("GRAPHITI_NEO4J_URI=", os.environ.get("GRAPHITI_NEO4J_URI"))
print("NEO4J_USER=", os.environ.get("NEO4J_USER") or os.environ.get("NEO4J_USERNAME"))
print("NEO4J_PASSWORD=", "SET" if os.environ.get("NEO4J_PASSWORD") else "MISSING")

try:
    from neo4j import GraphDatabase
except Exception as e:
    print("NEO4J_DRIVER_IMPORT_FAIL=", repr(e))
    raise SystemExit(1)

uri = os.environ.get("NEO4J_URI") or "bolt://127.0.0.1:7688"
user = os.environ.get("NEO4J_USER") or os.environ.get("NEO4J_USERNAME") or "neo4j"
pwd = os.environ.get("NEO4J_PASSWORD")

if not pwd:
    print("NEO4J_PASSWORD_MISSING")
    raise SystemExit(2)

driver = GraphDatabase.driver(uri, auth=(user, pwd))
driver.verify_connectivity()

with driver.session() as s:
    print("RETURN_1=", dict(s.run("RETURN 1 AS ok").single()))
    print("NODE_COUNT=", dict(s.run("MATCH (n) RETURN count(n) AS nodes").single()))

driver.close()
print("NEO4J_READONLY_CONNECTIVITY_PASS")
