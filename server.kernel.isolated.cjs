const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const express = require('express');
const app = express();
app.use(express.json({ limit: '10mb' }));

app.post('/kernel/ragnarok', (req, res) => {
    const domain = req.body.domain || 'bank_security_policy';
    const data = JSON.stringify(req.body.data || req.body);
    const reqId = crypto.randomUUID();

    // Calcul de l'empreinte cryptographique de l'entrée (input_hash)
    const inputHash = crypto.createHash('sha256').update(data).digest('hex');

    console.log(`\x1b[35m🛰️ [INCOMING [${reqId.substring(0, 8)}]]:\x1b[0m Domain: ${domain} | Input SHA256: ${inputHash.substring(0, 16)}...`);

    // Lancement de Python avec isolation stricte : transmission du JSON via stdin ('-')
    // Élimine toute race condition de fichier temporaire (input_temp.json) et contourne la limite argv de l'OS
    const py = spawn('python', ['-u', 'sigma/run_pipeline.py', domain, '-'], {
        env: { ...process.env, PYTHONPATH: process.cwd() }
    });

    let result = '';
    let stderrOutput = '';

    py.stdout.on('data', (d) => {
        const str = d.toString();
        if (str.trim().startsWith('{')) {
            result += str;
        } else {
            console.log(`\x1b[36m🐍 [PYTHON_INFO [${reqId.substring(0, 8)}]]:\x1b[0m ${str.trim()}`);
        }
    });

    py.stderr.on('data', (d) => {
        const errStr = d.toString().trim();
        stderrOutput += errStr + '\n';
        console.error(`\x1b[31m📢 [PYTHON_ERROR [${reqId.substring(0, 8)}]]:\x1b[0m ${errStr}`);
    });

    // Transmission isolée en mémoire
    py.stdin.write(data, 'utf-8');
    py.stdin.end();

    py.on('close', (code) => {
        try {
            if (!result) {
                throw new Error(`No JSON output from Python (exit code ${code}). Stderr: ${stderrOutput}`);
            }
            const parsedResult = JSON.parse(result);

            // Calcul de l'empreinte de sortie (output_hash)
            const outputHash = crypto.createHash('sha256').update(result).digest('hex');

            // Intégration non-invasive des hash d'audit dans la réponse
            if (parsedResult.raw_engine) {
                parsedResult.raw_engine.req_id = reqId;
                parsedResult.raw_engine.input_hash = inputHash;
                parsedResult.raw_engine.output_hash = outputHash;
            }

            // Persistance de la trace d'audit scellée dans MonProjet/allData
            // L'adjonction d'entropie aléatoire garantit qu'aucune requête simultanée n'écrase la preuve d'une autre
            const allDataDir = path.join(__dirname, 'MonProjet', 'allData');
            if (!fs.existsSync(allDataDir)) {
                fs.mkdirSync(allDataDir, { recursive: true });
            }

            const safeDomain = String(domain).replace(/[^a-zA-Z0-9_-]/g, '_');
            const entropy = crypto.randomBytes(4).toString('hex');
            const filename = `decision_${safeDomain}_${Date.now()}_${entropy}.json`;
            const filePath = path.join(allDataDir, filename);

            fs.writeFileSync(
                filePath,
                JSON.stringify(parsedResult, null, 2),
                'utf8'
            );

            res.json(parsedResult);
            console.log(`\x1b[32m✅ [SUCCESS [${reqId.substring(0, 8)}]]:\x1b[0m Proof sealed for ${domain} -> ${filename}`);
        } catch (e) {
            console.error(`\x1b[41m💥 [CRASH [${reqId.substring(0, 8)}]]:\x1b[0m Pipeline failed: ${e.message}`);
            res.status(500).json({ error: "Pipeline crash", details: result, stderr: stderrOutput, req_id: reqId });
        }
    });
});

const PORT = process.env.PORT || 3001;
const server = app.listen(PORT, () => {
    console.log("\x1b[44m\x1b[37m %s \x1b[0m", " TRINITY KERNEL (ISOLATED ADAPTER) : CONNECTÉ & OPÉRATIONNEL ");
    console.log(`🚀 Listening on port ${PORT}...`);
});

module.exports = { app, server };
