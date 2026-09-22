const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const express = require('express');
const app = express();
app.use(express.json());

app.post('/kernel/ragnarok', (req, res) => {
    const domain = req.body.domain || 'bank_security_policy';
    const data = JSON.stringify(req.body.data ?? req.body.state ?? req.body);

    console.log(`\x1b[35m🛰️ [INCOMING]:\x1b[0m Request for domain: ${domain}`);

    // On lance Python avec les arguments domain et data
    const py = spawn('python', ['-u', 'sigma/run_pipeline.py', domain, data], {
        env: { ...process.env, PYTHONPATH: process.cwd() }
    });

    let result = '';

    py.stdout.on('data', (d) => {
        const str = d.toString();
        // Si c'est du JSON (notre preuve scellée), on le stocke pour la réponse
        if (str.trim().startsWith('{')) {
            result += str;
        } else {
            // Sinon c'est de l'info, on l'affiche en bleu
            console.log(`\x1b[36m🐍 [PYTHON_INFO]:\x1b[0m ${str.trim()}`);
        }
    });

    py.stderr.on('data', (d) => {
        // Les erreurs Python s'affichent en rouge
        console.error(`\x1b[31m📢 [PYTHON_ERROR]:\x1b[0m ${d.toString().trim()}`);
    });

    py.on('close', (code) => {
        try {
            if (!result) throw new Error("No JSON output from Python");
            const parsedResult = JSON.parse(result);

            // Runtime trace persistence — Obsidia X-108 audit proof
            const allDataDir = path.join(__dirname, 'MonProjet', 'allData');
            if (!fs.existsSync(allDataDir)) {
                fs.mkdirSync(allDataDir, { recursive: true });
            }

            const safeDomain = String(domain).replace(/[^a-zA-Z0-9_-]/g, '_');
            const filename = `decision_${safeDomain}_${Date.now()}.json`;
            fs.writeFileSync(
                path.join(allDataDir, filename),
                JSON.stringify(parsedResult, null, 2),
                'utf8'
            );

            res.json(parsedResult);
            console.log(`\x1b[32m✅ [SUCCESS]:\x1b[0m Proof sealed for ${domain} -> ${filename}`);
        } catch (e) {
            console.error(`\x1b[41m💥 [CRASH]:\x1b[0m Pipeline failed or no valid JSON.`);
            res.status(500).json({ error: "Pipeline crash", details: result });
        }
    });
});

app.listen(3001, () => {
    console.log("\x1b[44m\x1b[37m %s \x1b[0m", " TRINITY KERNEL : CONNECTÉ & OPÉRATIONNEL ");
    console.log("🚀 Listening on port 3001...");
});
