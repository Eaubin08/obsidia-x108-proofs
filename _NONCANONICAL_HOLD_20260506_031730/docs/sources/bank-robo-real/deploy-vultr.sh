#!/bin/bash
# Script de déploiement automatique pour Vultr
# Ce script configure tout ce qui est nécessaire pour que Vultr fonctionne comme Manus

set -e

echo "🚀 Déploiement Bank Safety Lab sur Vultr"
echo "=========================================="
echo ""

# 1. Créer le fichier .env avec la clé Gemini
echo "📝 Configuration de l'environnement..."
cat > .env << 'EOF'
DATABASE_URL=file:./local.db
NODE_ENV=production
GEMINI_API_KEY=${GEMINI_API_KEY:-}
VITE_APP_TITLE=Bank Safety Lab
EOF

echo "✅ Fichier .env créé"

# 2. Modifier drizzle.config.ts pour supporter SQLite
echo "🔧 Configuration de la base de données SQLite..."
cat > drizzle.config.ts << 'EOF'
import { defineConfig } from "drizzle-kit";

const connectionString = process.env.DATABASE_URL;
if (!connectionString) {
  throw new Error("DATABASE_URL is required to run drizzle commands");
}

const isSQLite = connectionString.startsWith("file:");

export default defineConfig({
  schema: "./drizzle/schema.ts",
  out: "./drizzle",
  dialect: isSQLite ? "sqlite" : "mysql",
  dbCredentials: isSQLite 
    ? { url: connectionString.replace("file:", "") }
    : { url: connectionString },
});
EOF

echo "✅ Configuration base de données mise à jour"

# 3. Installer better-sqlite3 si nécessaire
echo "📦 Vérification des dépendances..."
if ! grep -q "better-sqlite3" package.json; then
    pnpm add better-sqlite3
fi

echo "✅ Dépendances installées"

# 4. Supprimer les anciennes migrations MySQL et créer la base SQLite
echo "🗄️  Création de la base de données..."
rm -rf drizzle/meta drizzle/*.sql
rm -f local.db
pnpm db:push

echo "✅ Base de données créée"

# 5. Compiler le frontend
echo "🔨 Compilation du frontend..."
pnpm run build

echo "✅ Frontend compilé"

# 6. Redémarrer l'application
echo "🔄 Redémarrage de l'application..."
pm2 restart bank-safety-lab || pm2 start ecosystem.config.cjs

echo ""
echo "=========================================="
echo "✅ DÉPLOIEMENT TERMINÉ !"
echo "=========================================="
echo ""
echo "🌐 Votre application est accessible sur:"
echo "   http://45.32.151.185/"
echo ""
echo "📊 Pour voir les logs:"
echo "   pm2 logs bank-safety-lab"
echo ""
