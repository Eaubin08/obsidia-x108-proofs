const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const express = require('express');
const app = express();
app.use(express.json());

app.post('/kernel/ragnarok', (req, res) => {
    const sigmaDir = path.join(__dirname, '..', 'sigma');
    const scriptPath = path.join(sigmaDir, 'run_pipeline.py');
    const tempFilePath = path.join(__dirname, 'input_temp.json');
    
    // --- CHIRURGIE DYNAMIQUE ---
    // On extrait le domaine (par défaut aviation) et les données réelles (state)
    const domain = req.body.domain || "gps_defense_aviation";
    const dataToProcess = req.body.state || req.body; 

    // 1. On écrit les données dans un fichier physique pour éviter les bugs de quotes
    try {
        fs.writeFileSync(tempFilePath, JSON.stringify(dataToProcess, null, 2));
    } catch (err) {
        return res.status(500).json({ error: "Failed to write temp file", details: err.message });
    }
    
    console.log(`\x1b[35m[BRIDGE]\x1b[0m 🚀 Routing -> Domain: ${domain}`);

    // 2. On lance Python en pointant vers le fichier
    const py = spawn('python', ['-u', scriptPath, domain, tempFilePath], {
        env: { ...process.env, PYTHONPATH: path.join(__dirname, '..') }
    });

    let result = '';

    py.stdout.on('data', (data) => {
        const str = data.toString();
        // On ne capture que le JSON final pour la réponse
        if (str.trim().startsWith('{')) {
            result += str;
        } else {
            console.log(`\x1b[36m🐍 [PYTHON_INFO]:\x1b[0m ${str.trim()}`);
        }
    });

    py.stderr.on('data', (data) => {
        // Les logs de contracts.py (obsidia_log) passent par ici
        console.error(`\x1b[33m📢 [KERNEL_TRACE]:\x1b[0m ${data.toString().trim()}`);
    });

    py.on('close', (code) => {
        // 3. Nettoyage immédiat
        if (fs.existsSync(tempFilePath)) {
            try { fs.unlinkSync(tempFilePath); } catch(e) {}
        }

        if (code !== 0 && !result) {
            console.error(`\x1b[31m[ERROR]\x1b[0m Python a quitté avec le code ${code}`);
            return res.status(500).json({ error: "Python Crash Code " + code });
        }

        try {
            const parsedResult = JSON.parse(result);
            
            // --- AJOUT SÉCURISÉ : PERSISTENCE ---
            const allDataDir = path.join(__dirname, 'allData');
            if (!fs.existsSync(allDataDir)) fs.mkdirSync(allDataDir);
            
            const filename = `decision_${domain}_${Date.now()}.json`;
            fs.writeFileSync(path.join(allDataDir, filename), JSON.stringify(parsedResult, null, 2));
            console.log(`\x1b[32m💾 [SAVE]\x1b[0m ${filename}`);
            // ------------------------------------

            res.json(parsedResult);
        } catch (e) {
            console.error("\x1b[31m[PARSE ERROR]\x1b[0m", result);
            res.status(500).json({ error: "Parsing error", raw: result });
        }
    });
});

app.listen(3001, () => {
    console.log("\x1b[45m\x1b[37m %s \x1b[0m", " ⚡ BRIDGE UNIVERSEL : MODE FICHIER TAMPON ⚡ ");
    console.log("🚀 Prêt pour Ragnarok sur http://localhost:3001");
});