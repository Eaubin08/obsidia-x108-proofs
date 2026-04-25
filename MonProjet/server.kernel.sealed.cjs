const express = require("express");
const { Client } = require("pg");
const { spawnSync } = require("child_process");
const crypto = require("crypto");
const path = require("path");
const app = express();
const port = 3001;

app.use(express.json());

const DATABASE_URL = process.env.DATABASE_URL;
const KERNEL_ROOT = "C:\\Users\\User\\Desktop\\obsidia-engine-proof-core\\obsidia-x108-proofs";
const RUN_PIPELINE = path.join(KERNEL_ROOT, "sigma", "run_pipeline.py");

const client = new Client({ 
    connectionString: DATABASE_URL,
    ssl: { rejectUnauthorized: false } 
});

client.on('error', err => {
    console.error('❌ [DATABASE ERROR]:', err.message);
    process.exit(1);
});

function sha256(value) {
    return crypto.createHash("sha256").update(value, "utf8").digest("hex");
}

async function processSovereignRequest(domain, payload, res) {
    try {
        console.log(`\n🧠 [${domain.toUpperCase()}] Consultation du Kernel X-108...`);
        const result = spawnSync("python", [RUN_PIPELINE, domain, JSON.stringify(payload)], {
            cwd: KERNEL_ROOT,
            encoding: "utf8",
            env: { ...process.env, PYTHONPATH: KERNEL_ROOT }
        });

        if (result.stderr) console.error("🐍 [PYTHON LOG]:", result.stderr);
        if (!result.stdout) throw new Error("Le Kernel n'a renvoyé aucune donnée.");

        const kernel = JSON.parse(result.stdout);
        const decision = kernel.x108_gate || "HOLD";
        const pHash = sha256(JSON.stringify(payload));
        const rHash = sha256(pHash + decision + (kernel.attestation_ref || ""));

        await client.query(
            `INSERT INTO obsidia_kernel_logs (domain, payload, payload_hash, kernel_result, decision, record_hash)
             VALUES ($1, $2, $3, $4, $5, $6)`,
            [domain, JSON.stringify(payload), pHash, JSON.stringify(kernel), decision, rHash]
        );

        console.log(`⚖️  [VERDICT] ${decision} | Proof Sealed: ${rHash.substring(0,10)}...`);
        res.json({ status: decision, record_hash: rHash, kernel });
    } catch (err) {
        res.status(500).json({ error: "Erreur de scellage", details: err.message });
    }
}

async function init() {
    try {
        await client.connect();
        console.log("✅ [SYSTEM] Liaison Neon Cloud active.");
        
        // --- ROUTES ---
        app.post("/kernel/gps_defense_aviation", (req, res) => processSovereignRequest("gps_defense_aviation", req.body, res));
        app.post("/kernel/bank", (req, res) => processSovereignRequest("bank", req.body, res));
        
        // La route manquante est de retour !
        app.get("/allData", async (req, res) => {
            try {
                const r = await client.query("SELECT id, domain, decision, record_hash, created_at FROM obsidia_kernel_logs ORDER BY id DESC LIMIT 10");
                res.json(r.rows);
            } catch (err) {
                res.status(500).json({ error: err.message });
            }
        });

        app.listen(port, () => console.log(`🚀 [READY] OBSIDIA SEALED BRIDGE ONLINE : PORT ${port}`));
    } catch (err) {
        console.error("❌ [BOOT FAILED]:", err.message);
    }
}

init();
