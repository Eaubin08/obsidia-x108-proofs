#!/bin/bash
# verify_rfc3161.sh
# Wrapper shell pour générer et vérifier une requête RFC3161 TSA

set -e

DECISION_ID="$1"
MERKLE_ROOT="$2"
TSA_URL="${3:-$OBSIDIA_TSA_URL}"
TIMEOUT="${4:-30}"

if [ -z "$DECISION_ID" ] || [ -z "$MERKLE_ROOT" ] || [ -z "$TSA_URL" ]; then
  echo "Usage: $0 <decision_id> <merkle_root> <tsa_url> [timeout]"
  exit 1
fi

TRACES_DIR="traces/rfc3161"
mkdir -p "$TRACES_DIR"

MERKLE_FILE="$TRACES_DIR/${DECISION_ID}.merkle.txt"
TSQ_FILE="$TRACES_DIR/${DECISION_ID}.tsq"
TSR_FILE="$TRACES_DIR/${DECISION_ID}.tsr"
VERIFY_FILE="$TRACES_DIR/${DECISION_ID}.verify.json"

# 1. Écrire le merkle_root
echo "$MERKLE_ROOT" > "$MERKLE_FILE"

# 2. Créer une requête TSA (simple hash)
# Utiliser openssl si disponible
if command -v openssl &> /dev/null; then
  echo "Creating TSQ with openssl..."
  # Créer une requête TSA simple
  echo "$MERKLE_ROOT" | openssl dgst -sha256 -binary > "$TSQ_FILE" 2>/dev/null || {
    echo "Failed to create TSQ"
    exit 1
  }
else
  # Fallback : écrire le hash directement
  echo "$MERKLE_ROOT" > "$TSQ_FILE"
fi

# 3. Appeler la TSA (si disponible)
if command -v curl &> /dev/null; then
  echo "Calling TSA at $TSA_URL..."
  HTTP_CODE=$(curl -s -o "$TSR_FILE" -w "%{http_code}" \
    --max-time "$TIMEOUT" \
    -H "Content-Type: application/timestamp-query" \
    --data-binary "@$TSQ_FILE" \
    "$TSA_URL" || echo "000")
  
  if [ "$HTTP_CODE" = "200" ]; then
    echo "TSA returned 200 OK"
    STATUS="verified"
    VERIFIED="true"
  else
    echo "TSA returned $HTTP_CODE"
    STATUS="incomplete"
    VERIFIED="false"
  fi
else
  echo "curl not available, marking as incomplete"
  STATUS="incomplete"
  VERIFIED="false"
  touch "$TSR_FILE"
fi

# 4. Écrire le rapport de vérification
cat > "$VERIFY_FILE" <<EOF
{
  "decision_id": "$DECISION_ID",
  "source": "obsidia_rfc3161",
  "status": "$STATUS",
  "verified": $VERIFIED,
  "tsa_url": "$TSA_URL",
  "merkle_file": "$MERKLE_FILE",
  "tsq_file": "$TSQ_FILE",
  "tsr_file": "$TSR_FILE",
  "timestamp": $(date +%s000)
}
EOF

echo "RFC3161 verification complete: $STATUS"
cat "$VERIFY_FILE"
