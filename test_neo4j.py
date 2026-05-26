from neo4j import GraphDatabase

URI = "bolt://127.0.0.1:7688"
USER = "neo4j"
PASS = "obsidia_neo4j_2026"

try:
    print("Tentative de connexion à " + URI + "...")
    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
    driver.verify_connectivity()
    print("SUCCESS: Connexion Neo4j établie avec succès !")
    driver.close()
except Exception as e:
    print(f"FAIL: Impossible de se connecter. Erreur : {e}")
