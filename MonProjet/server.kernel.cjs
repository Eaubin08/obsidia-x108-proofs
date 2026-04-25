const express = require("express");
const { Client } = require("pg");
const { spawnSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const app = express();
const port = 3001; // Port différent pour ne pas gêner l'autre serveur

app.use(express.json());

// On récupère le lien Neon automatiquement depuis ton autre fichier
function getDbUrl() {
    const serverFile = path.join(process.cwd(), "server.cjs");
    if (fs.existsSync(serverFile)) {
        const content = fs.readFileSync(serverFile, "utf8");
        const match = content.match(/connectionString\s*=\s*['"]([^'"]+)['"]/);
        return match ? match[1] : null;
    }
    return null;
}

const KERNEL_ROOT = "C:\\Users\\User\\Desktop\\obsidia-engine-proof-core\\obsidia-x108-proofs";
const RUN_PIPELINE = path.join(KERNEL_ROOT, "sigma", "run_pipeline.py");
const dbUrl = getDbUrl();

if (!dbUrl) {
    console.error("❌ Impossible de trouver le lien PostgreSQL dans server.cjs");
    process.exit(1);
}

const client = new Client({ connectionString: dbUrl });

// Fonction qui appelle ton VRAI Kernel Python
function callObsidiaKernel(domain, data) {
    const result = spawnSync("python", [RUN_PIPELINE, domain, JSON.stringify(data)], {
        cwd: KERNEL_ROOT,
        encoding: "utf8"
    });

    if (result.error) throw result.error;
    return JSON.parse(result.stdout);
}

async function init() {
    await client.connect();
    // Création de la table de logs du Kernel
    await client.query(`
        CREATE TABLE IF NOT EXISTS obsidia_kernel_logs (
            id SERIAL PRIMARY KEY,
            decision TEXT,
            payload JSONB,
            kernel_output JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    `);
    console.log("✅ Base de données connectée et prête.");
}

app.post("/kernel/bank", async (req, res) => {
    try {
        console.log("🧠 Consultation du Kernel X-108...");
        const kernelResult = callObsidiaKernel("bank", req.body);
        
        const decision = kernelResult.decision || kernelResult.x108_gate || "UNKNOWN";

        // Enregistrement de la décision réelle du noyau
        await client.query(
            "INSERT INTO obsidia_kernel_logs(decision, payload, kernel_output) VALUES($1, $2, $3)",
            [decision, JSON.stringify(req.body), JSON.stringify(kernelResult)]
        );

        res.json({ status: decision, kernel: kernelResult });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: "Erreur Kernel", message: err.message });
    }
});

app.get("/allData", async (req, res) => {
    const result = await client.query("SELECT * FROM obsidia_kernel_logs ORDER BY created_at DESC");
    res.json(result.rows);
});

init().then(() => {
    app.listen(port, () => console.log(`🚀 KERNEL BRIDGE ONLINE : http://localhost:${port}`));
});
