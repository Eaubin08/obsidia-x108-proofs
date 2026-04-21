FROM node:22-alpine

# Installer dépendances système
RUN apk add --no-cache \
    openssl \
    openssl-dev \
    python3 \
    python3-dev \
    pip \
    git \
    curl \
    wget \
    build-essential \
    ca-certificates

# Installer TLC (TLA+ model checker)
# Note: TLC est complexe à installer, on utilise une version pré-compilée
RUN mkdir -p /opt/tla && \
    cd /opt/tla && \
    wget -q https://github.com/tlaplus/tlaplus/releases/download/v1.7.9/tla2tools.jar -O tlc.jar || \
    echo "TLC download failed, will use fallback" && \
    chmod +x tlc.jar 2>/dev/null || true

# Créer répertoire de travail
WORKDIR /app

# Copier package.json et installer dépendances Node
COPY package.json package-lock.json ./
RUN npm install --legacy-peer-deps

# Copier code source
COPY . .

# Créer répertoires pour artefacts
RUN mkdir -p traces/rfc3161 traces/tla traces/sigma traces/audit

# Build
RUN npm run build

# Exposer port
EXPOSE 3000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1

# Démarrer serveur
CMD ["npm", "run", "dev"]
