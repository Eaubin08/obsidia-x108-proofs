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

const client = new Client({ connectionString: DATABASE_URL });

function sha256(value) {
    return crypto.createHash("sha256").update(value, "utf8").digest("hex");
}

async function start() {
    try {
        console.log("\n--- 🏁 OBSIDIA MULTI-DOMAIN KERNEL STARTING ---");
        await client.connect();
        console.log("✅ [DATABASE] Neon Cloud Link Active.");

        app.use((req, res, next) => {
            console.log(`\n📡 [${new Date().toLocaleTimeString()}] INCOMING: ${req.method} ${req.url}`);
            next();
        });

        // FONCTION GENERIQUE DE TRAITEMENT (Le processus de scellage reste identique)
        async function processKernelRequest(domain, payload, res) {
            try {
                console.log(`🧠 [${domain.toUpperCase()}] Running deterministic logic...`);
                const result = spawnSync("python", [RUN_PIPELINE, domain, JSON.stringify(payload)], { cwd: KERNEL_ROOT, encoding: "utf8" });
                
                if (result.stderr) console.warn("🐍 [KERNEL WARNING]", result.stderr);
                
                const kernel = JSON.parse(result.stdout);
                const decision = kernel.x108_gate || kernel.decision;
                console.log(`⚖️  [VERDICT] ${decision} | Code: ${kernel.reason_code}`);

                const pHash = sha256(JSON.stringify(payload));
                const rHash = sha256(pHash + decision + (kernel.attestation_ref || ""));

                await client.query(
                    `INSERT INTO obsidia_kernel_logs (domain, payload, payload_hash, kernel_result, decision, record_hash) 
                     VALUES ($1, $2, $3, $4, $5, $6)`,
                    [domain, JSON.stringify(payload), pHash, JSON.stringify(kernel), decision, rHash]
                );
                
                console.log(`💾 [SEALED] Proof recorded. ID: ${kernel.decision_id || 'N/A'}`);
                res.json({ status: decision, record_hash: rHash, details: kernel });
            } catch (err) {
                console.error("❌ [ERROR]", err.message);
                res.status(500).json({ error: err.message });
            }
        }

        // ROUTES
        app.post("/kernel/bank", (req, res) => processKernelRequest("bank", req.body, res));
        app.post("/kernel/aviation", (req, res) => processKernelRequest("aviation", req.body, res));
        
        app.get("/allData", async (req, res) => {
            const r = await client.query("SELECT id, domain, decision, record_hash, created_at FROM obsidia_kernel_logs ORDER BY id DESC LIMIT 50");
            res.json(r.rows);
        });

        app.listen(port, () => console.log(`🚀 [OBSIDIA READY] Multi-domain bridge on port ${port}\n`));
    } catch (e) {
        console.error("❌ [CRITICAL]", e.message);
    }
}
start();
