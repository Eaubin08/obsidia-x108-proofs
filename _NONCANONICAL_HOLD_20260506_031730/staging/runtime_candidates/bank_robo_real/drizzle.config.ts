import { defineConfig } from "drizzle-kit";

const connectionString = process.env.DATABASE_URL;
if (!connectionString) {
  throw new Error("DATABASE_URL is required to run drizzle commands");
}

// Détecter automatiquement SQLite vs MySQL
const isSQLite = connectionString.startsWith("file:");

export default defineConfig({
  schema: "./drizzle/schema.ts",
  out: "./drizzle",
  dialect: isSQLite ? "sqlite" : "mysql",
  dbCredentials: isSQLite 
    ? { url: connectionString.replace("file:", "") }
    : { url: connectionString },
});
