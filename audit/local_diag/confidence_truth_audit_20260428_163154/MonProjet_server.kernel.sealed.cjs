const { spawn, exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const express = require('express');
const app = express();
app.use(express.json());

app.post('/kernel/ragnarok', (req, res) => {
    const sigmaDir = path.join(__dirname, '..', 'sigma');
    const scriptPath = path.join(sigmaDir, 'run_pipeline.py');
    let tempFilePath = null;

    // --- CHIRURGIE DYNAMIQUE ---
    const domain = req.body.domain || "gps_defense_aviation";
    const safeDomain = String(domain).replace(/[^a-zA-Z0-9_-]/g, "_");
    tempFilePath = path.join(
        __dirname,
        `input_${safeDomain}_${Date.now()}_${process.pid}_${Math.random().toString(16).slice(2)}.json`
    );
    const dataToProcess = req.body.state || req.body.data || req.body.payload || req.body;

    try {
        fs.writeFileSync(tempFilePath, JSON.stringify(dataToProcess, null, 2));
    } catch (err) {
        return res.status(500).json({ error: "Failed to write temp file", details: err.message });
    }

    console.log(`\x1b[35m[BRIDGE]\x1b[0m ðŸš€ Routing -> Domain: ${domain}`);

    const py = spawn('python', ['-u', scriptPath, domain, tempFilePath], {
        env: { ...process.env, PYTHONPATH: path.join(__dirname, '..') }
    });

    let result = '';

    py.stdout.on('data', (data) => {
        const str = data.toString();
        if (str.trim().startsWith('{')) {
            result += str;
        } else {
            console.log(`\x1b[36mðŸ [PYTHON_INFO]:\x1b[0m ${str.trim()}`);
        }
    });

    py.stderr.on('data', (data) => {
        console.error(`\x1b[33mðŸ“¢ [KERNEL_TRACE]:\x1b[0m ${data.toString().trim()}`);
    });

    py.on('close', (code) => {
        if (fs.existsSync(tempFilePath)) {
            try { fs.unlinkSync(tempFilePath); } catch(e) {}
        }

        if (code !== 0 && !result) {
            console.error(`\x1b[31m[ERROR]\x1b[0m Python a quittÃ© avec le code ${code}`);
            return res.status(500).json({ error: "Python Crash Code " + code });
        }

        try {
            const parsedResult = JSON.parse(result);

            const allDataDir = path.join(__dirname, 'allData');
            if (!fs.existsSync(allDataDir)) fs.mkdirSync(allDataDir);

            const filename = `decision_${domain}_${Date.now()}.json`;
            fs.writeFileSync(path.join(allDataDir, filename), JSON.stringify(parsedResult, null, 2));
            console.log(`\x1b[32mðŸ’¾ [SAVE]\x1b[0m ${filename}`);

            res.json(parsedResult);
        } catch (e) {
            console.error("\x1b[31m[PARSE ERROR]\x1b[0m", result);
            res.status(500).json({ error: "Parsing error", raw: result });
        }
    });
});

setInterval(() => {
    console.log("ðŸ” [AUTO-SEAL] Pulsation Merkle en cours...");

    exec('python C:\\Users\\User\\Desktop\\obsidia-engine-proof-core\\obsidia-x108-proofs\\audit_merkle.py', (error, stdout, stderr) => {
        if (error) {
            console.error(`âŒ [AUTO-SEAL] Ã‰chec : ${error.message}`);
            return;
        }

        const rootHash = stdout.match(/ROOT HASH : (.*)/);
        if (rootHash) {
            console.log(`ðŸ›¡ï¸ [AUTO-SEAL] SystÃ¨me ScellÃ©. Root: ${rootHash[1].substring(0, 12)}...`);
        } else {
            console.log("ðŸ” [AUTO-SEAL] Cycle complÃ©tÃ© (Pas de nouveau Root Hash dÃ©tectÃ©)");
        }
    });
}, 60000);

app.listen(3001, () => {
    console.log("\x1b[45m\x1b[37m %s \x1b[0m", " âš¡ BRIDGE UNIVERSEL : MODE FICHIER TAMPON âš¡ ");
    console.log("ðŸš€ PrÃªt pour Ragnarok sur http://localhost:3001");
});